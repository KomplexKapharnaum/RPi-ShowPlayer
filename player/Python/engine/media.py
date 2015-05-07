# -*- coding: utf-8 -*-
#
#
# This file provide class and function to manage media on the Raspebrry Pi
#

import os
import shutil
import datetime
import tarfile
import threading
import time
import subprocess
import shlex
import cPickle

import pyudev

from modules._classes import ExternalProcess
from libs import pyhashxx
from engine.setting import settings
from engine import tools
from engine.threads import network_scheduler

from engine.log import init_log

log = init_log("media")


def get_mtime(path):
    """
    Get the mtime of a file, if you change think to change osc repr in Media class
    :param path: absolute path
    :return:
    """
    if os.path.exists(path):
        return float(os.path.getmtime(path))
    else:
        return float(0)


def get_all_media_list():
    """
    This function return a MediaList for all media in scenario
    :return:
    """
    all_media = MediaList()
    media_path = settings.get_path("media")
    for path, dirs, files in os.walk(media_path):  # Retreived file list to check
        for f in files:
            abs_path = os.path.join(path, f)
            rel_path = os.path.relpath(abs_path, media_path)
            all_media.append(Media.from_fs(rel_path, abs_path, Media.get_size(abs_path)))
    return all_media


def get_unwanted_media_list(needed_media_list):
    """
    This function return the list of media present on the filesystem but which are not required by scenario
    :param needed_media_list: NeededMediaList obj, which contains all of the needed media
    :return:
    """
    unwanted_media_list = MediaList()
    media_path = settings.get_path("media")
    for path, dirs, files in os.walk(media_path):  # Retreived file list to check
        for f in files:
            abs_path = os.path.join(path, f)
            rel_path = os.path.relpath(abs_path, media_path)
            if rel_path in needed_media_list:
                continue
            unwanted_media_list.append(Media.from_fs(rel_path, abs_path, Media.get_size(abs_path)))
    return unwanted_media_list


class MediaList(list):
    """
    This class is a list of media
    """

    def __contains__(self, rel_path):
        """
        This function test if the media rel_path given is in the wanted list
        """
        for elem in self:
            if elem.rel_path == rel_path:
                return True
        return False

    def need(self, media_obj):
        """
        This function test if media_obj is wanted (present and newer) based on the NeededMediaList
        """
        log.log("raw", "Do this list need {0}".format(media_obj))
        if media_obj.source == "osc" and not settings.get("sync", "video") and Media.get_root_dir(
                media_obj.rel_path) == settings.get("path", "relative", "video"):
            log.log("raw", "Ignore because it's a video and we ask to do not scp copy them")
            log.log("raw", "Media : {0}, settings sync {1} settings video {2}".format(
                media_obj, settings.get("sync", "video"), settings.get("path", "relative", "video")
            ))
            return False  # It's a video and we ask to do not scp copy them
        for elem in self:
            log.log("raw", "Test with : {0}".format(elem))
            if media_obj.rel_path == elem.rel_path and media_obj.mtime > elem.mtime:
                log.log("raw", "NEED MEDIA Found !! our : {0}, update {1}  ".format(elem.mtime, media_obj.mtime))
                return True
        return False

    def update(self):
        """
        This function update mtime information for all media from fs
        """
        # log.log("error", "Update {0}".format(self))
        for elem in self:
            if elem.source != "osc":
                elem.mtime = get_mtime(elem.source_path)


    def get_smaller_media(self):  # , ignore=()):
        """
        This function return the smaller media to delete in the MediaList
        # :param ignore: list of elem to ignore
        """
        smaller = self[0]
        for elem in self:
            if elem.filesize < smaller.filesize:  # and elem not in ignore:
                smaller = elem
        return smaller

    def total_space(self):
        """
        This function return the total space of media content in the media list
        """
        total_size = 0
        for elem in self:
            if elem.filesize is not None:
                total_size += elem.filesize
        return total_size

    def __repr__(self):
        r = "Media list : \n"
        for elem in self:
            r += str(elem) + "\n"
        return r

    def __str__(self):
        return self.__repr__()

        # def get_media_to_delete(self, needspace):
        # """
        # This function return a list of smaller media
        # """
        # freespace = 0
        #     while freespace < needspace:


class Media:
    """
    This class represent a media in order to have a common representation between osc, scenario and usb
    """

    def __init__(self, rel_path, mtime, source, source_path, filesize=None):
        """
        :param rel_path: reltive path in media directory
        :param mtime: mtime of the file
        :param source: Source of the file (scenario, usb or osc) if osc it's a target
        :param source_path: Real source path of the file
        :param filesize: File size
        """
        self.rel_path = rel_path
        self.mtime = mtime
        self.source = source
        self.source_path = source_path
        self.filesize = filesize
        # log.log("raw", "Init {0}".format(self))

    @staticmethod
    def from_scenario(rel_path):
        """
        Create a Media from a rel path in scenario
        :param rel_path: rel_path of the media
        """
        path = os.path.join(settings.get_path("media"), rel_path)
        if not os.path.exists(path):
            log.log("raw", "Scenario media {0} not present in fs {1}".format(rel_path, path))
            # return False
            mtime = 0
        else:
            mtime = get_mtime(path)
        return Media(rel_path=rel_path, mtime=mtime, source="scenario", source_path=path)

    @staticmethod
    def from_usb(rel_path, abs_path):
        """
        Createa Media from a usb media
        :param rel_path: relative path of the media
        :param abs_path: absolute path of the media
        """
        if not os.path.exists(abs_path):
            log.error("Usb media {0} not present in fs {1}".format(rel_path, abs_path))
            return False
        mtime = get_mtime(abs_path)
        filesize = Media.get_size(abs_path)  # In Ko
        return Media(rel_path=rel_path, mtime=mtime, source="usb", source_path=abs_path, filesize=filesize)

    @staticmethod
    def from_osc(rel_path, mtime, filesize, user_ip, src_path):
        """
        Create Media from a osc message
        :param rel_path: rel_path of the media
        :param mtime: mtime of the media get by osc
        :param filesize: File size (in Ko) recv by osc
        :param user_ip: user@ip of the source owner
        :param src_path: source path of the owner
        """
        scp_path = user_ip + ":" + os.path.join(src_path, rel_path)
        return Media(rel_path=rel_path, mtime=mtime, source="osc", source_path=scp_path, filesize=filesize)

    @staticmethod
    def from_fs(rel_path, abs_path, filesize):
        """
        Create Media from fs (seem to be used to delte them after)
        :param rel_path: rel_path of the media
        :param abs_path: absolute path of the file on fs
        :param filesize: filesize in Ko of the media
        :return:
        """
        return Media(rel_path=rel_path, mtime=get_mtime(abs_path), source="fs", source_path=abs_path,
                     filesize=filesize)

    @staticmethod
    def get_size(abs_path):
        """
        This function return the size of a file in always the same format !
        :param abs_path: Absolute path of the file
        :return:
        """
        return int(os.path.getsize(abs_path) / 1000)

    @staticmethod
    def get_root_dir(path):
        """
        Return the first directory of a path
        :param path: Absolute or relative path
        :return:
        """
        path = os.path.split(path)
        while path[0] != "":
            path = os.path.split(path[0])
        return path[1]

    def get_osc_repr(self):
        """
        This function return an OSC reprentation of the Media
        :return: path, mtime, filesize
        """
        # log.log("raw", "get_osc_rep for : {0}".format(self))
        # return ('s', str(self.rel_path)), ('f', float(self.mtime)), ('i', int(self.filesize))
        return ('s', str(self.rel_path)), ('f', get_mtime(os.path.join(settings.get_path("media"), self.rel_path))), (
            'i', int(self.filesize))
        # return ('s', str(self.rel_path)), ('b', cPickle.dumps((self.mtime, self.filesize), 2))

    def check_on_fs(self):
        """
        This function test if the media is present on the fs
        :return:
        """
        if os.path.exists(os.path.join(settings.get_path("media"), self.rel_path)):
            return True
        else:
            return False

    def put_on_fs(self):  # , error_fnct=None
        """
            This methof put the Media to the file system with the correct way to preserve mtime
            ASUME THERE IS ENOUGHT SPACE ON FILESYSTEM
            # :param error_fnct: If the copy fail for one reason or another, the function is called
            #                     This function must take at least 2 param, the Media object and the Exception object
        """
        if self.source == "scenario":
            log.warning("Ask to get a file from the scenario... do nothing")
            return False
        tools.log_teleco((os.path.basename(self.rel_path), "copy from {0}".format(self.source.upper())), "sync")
        if self.source == "usb":
            dest_path = os.path.join(settings.get_path("media"), self.rel_path)
            dir_path = os.path.dirname(dest_path)
            if not os.path.exists(dir_path):
                log.log("raw", "Create directory to get file {0}".format(dest_path))
                os.makedirs(dir_path)
            cp = ExternalProcess("cp")
            cp.command += " --preserve=timestamp '{0}' '{1}'".format(self.source_path, dest_path)
            log.log("raw", "Start CP copy with {0}".format(cp.command))
            cp.start()
            try:
                cp.join(timeout=self.filesize / settings.get("sync", "usb_speed_min") + 5)  # Minimum 5 seconds
            except RuntimeError as e:
                log.exception(log.show_exception(e))
                # if error_fnct is not None:
                # error_fnct(self, e)
                cp.stop()
                tools.log_teleco((os.path.basename(self.rel_path), "fail copy {0}".format(self.source.upper())),
                                 "error")
                return self, e
            tools.log_teleco((os.path.basename(self.rel_path), "copy {0} : OK".format(self.source.upper())), "usb")
            cp.stop()
            return True
        elif self.source == "osc":
            log.info("Media to scp copy : {0}".format(self))
            dest_path = os.path.join(settings.get_path("media"), self.rel_path)
            dir_path = os.path.dirname(dest_path)
            if not os.path.exists(dir_path):
                log.log("raw", "Create directory to get file {0}".format(dest_path))
                os.makedirs(dir_path)
            # if os.path.exists(dest_path):
            # os.remove(dest_path)        # Need to remove in order to get the correct date to avoid scp loop
            scp = ExternalProcess("scp")
            scp.command += " {options} {scp_path} {path}".format(scp_path=self.source_path, path=dest_path,
                                                                 options=settings.get("sync", "scp_options"))
            log.log("raw", "SCP : Try to get distant media {0} with {1}".format(self, scp.command))
            scp.start()
            try:
                scp.join(timeout=self.filesize / settings.get("sync", "scp_speed_min") + 10)
            except RuntimeError as e:
                log.exception(log.show_exception(e))
                scp.stop()
                tools.log_teleco((os.path.basename(self.rel_path), "fail copy {0}".format(self.source.upper())),
                                 "error")
                return self, e
            log.log("raw", "Force mtime to {0}".format(self.mtime))
            os.utime(dest_path, (-1, self.mtime))  # Force setting new time on file to avoid scp loop (-p dosen't work)
            tools.log_teleco((os.path.basename(self.rel_path), "copy {0} : OK".format(self.source.upper())), "sync")
            scp.stop()
            return True
        else:
            log.warning("What the ..? ask to copy from {0} ".format(self.source))

    def remove_from_fs(self):
        """
        This function remove the media from the file system, only if the source is scenario or fs
        """
        if self.source not in ("scenario", "fs"):
            log.warning("Ask to delete a {0} but it isn't on our filesystem".format(self))
            return False
        try:
            os.remove(self.source_path)
        except OSError as e:
            log.exception(log.show_exception(e))
            log.error("Need to delete {0} but OSError".format(self.source_path))
            return False
        return True

    def __repr__(self):
        return "Media {0}:{4}, {1}Ko, from {2} at {3}".format(self.rel_path, self.filesize, self.source,
                                                              self.source_path, self.mtime)


def mount_partition(block_path, mount_path):
    """
    This function mount a partition in usb directory
    :param block_path: Path to the block device to mount
    :param mount_path: Path to the mount point
    :return:
    """
    log.debug("Mount {0} on {1} ".format(block_path, mount_path))
    mount_cmd = ExternalProcess(name="mount")
    if not os.path.exists(mount_path):
        try:
            os.makedirs(mount_path)
        except OSError as e:
            log.warning("Should create mounbt point {0} but failed ".format(mount_path))
            log.exception(log.show_exception(e))
    else:
        log.warning("Warning, we mount a device {0} on an existing mount point {1}".format(block_path, mount_path))
    mount_cmd.command += " {0} {1}".format(block_path, mount_path)
    mount_cmd.start()
    try:
        mount_cmd.join(timeout=settings.get("sync", "usb_mount_timeout"))
    except RuntimeError as e:
        log.exception(log.show_exception(e))
        log.warning("Unable to mount  {0} on {1} ".format(block_path, mount_path))
        tools.log_teleco(("!USB! : error", "mount fail"), "error")
        mount_cmd.stop()
        return False
    tools.log_teleco(("USB : stick", "mount ok"), "usb")
    mount_cmd.stop()
    return True


def umount_partitions():
    """
    This function unmount all partition in usb directory
    :return:
    """
    log.log("raw", "Start to umount partitions")
    sucess = True
    for f in os.listdir(settings.get_path("usb")):
        path = os.path.join(settings.get_path("usb"), f)
        log.log("raw", "found on usb dir : {0}".format(path))
        if os.path.ismount(path):
            log.log("raw", "Found directory to umount {0}".format(f))
            umount_cmd = ExternalProcess(name="umount")
            umount_cmd.command += " " + path
            umount_cmd.start()
            try:
                umount_cmd.join(timeout=settings.get("sync", "usb_mount_timeout"))
                log.log("debug", "Correctly umount {0}".format(path))
                time.sleep(settings.get("sync", "timeout_rm_mountpoint"))
                os.rmdir(path)
                log.log("raw", "Correctly remove after umount {0}".format(path))
                tools.log_teleco(("USB : unmount", "succes"), "usb")
            except RuntimeError as e:
                log.exception(log.show_exception(e))
                log.warning("Unable to umount {0}".format(path))
                umount_cmd.stop()
                tools.log_teleco(("!USB! : error", "unmount fail"), "error")
                sucess = False
                continue
            umount_cmd.stop()
    return sucess


class UdevThreadMonitor(threading.Thread):
    """
    This class is a thread wich wait on new block plug event and try to mount it
    """

    def __init__(self, monitor, machine, flag):
        """
        :param monitor: pyudev.Monitor object to watch
        :param machine: FSM to prevent on mounted partition
        :param flag: Flag to trig on mount
        """
        threading.Thread.__init__(self)
        self.monitor = monitor
        self.machine = machine
        self.flag = flag
        self._stop = threading.Event()
        tools.register_thread(self)

    def run(self):
        self.monitor.start()
        while not self._stop.is_set():
            device = self.monitor.poll(timeout=1)
            if device is None:  # Timeout
                continue
            log.log("raw", "Block device : {0}".format(device.__dict__))
            if device.action == "remove":
                log.log("debug", "Remove block device {0}".format(device.device_node))
                umount_partitions()
                if settings.get("sys", "raspi") and settings.get("sync", "netctl_autorestart"):
                    log.log("info",
                            "We will restart netctl in {0} sec ".format(settings.get("sync", "timeout_restart_netctl")))
                    network_scheduler.enter(settings.get("sync", "timeout_restart_netctl"), tools.restart_netctl)
                    tools.log_teleco(
                        ("network restart", "in {0} sec".format(settings.get("sync", "timeout_restart_netctl"))), "usb")
                    time.sleep(settings.get("log", "teleco", "error_delay"))  # Not an error but..
                continue
            elif device.action not in ("add", "change"):
                log.log("raw", "Block device event {1} (not add) : {0}".format(device.device_node, device.action))
                continue
            devdir = os.path.dirname(device.device_node)
            devname = os.path.basename(device.device_node)
            mounted = 0
            for block in os.listdir(devdir):
                if devname in block and devname != block:  # Found a partition
                    mounted += mount_partition(os.path.join(devdir, block), os.path.join(settings.get_path("usb"),
                                                                                         "usb{0}".format(devname[:-1])))
            if mounted > 0:  # A partition has been mounted
                log.debug("Correctly mount {0} usb device".format(mounted))
                self.machine.append_flag(self.flag.get())

    def stop(self):
        self._stop.set()


def save_scenario_on_fs(group, date_timestamp):
    """
    This function tar scenario files and copy the archive on the right location
    :param group: Group of the scenario to saved
    :param date_timestamp: Scenario date to save
    :return:
    """
    edit_date = datetime.datetime.fromtimestamp(float(date_timestamp)).strftime(settings.get("scenario", "date_format"))
    path = os.path.join(settings.get_path("scenario"), group)
    if not os.path.exists(path):
        os.makedirs(path)
    with tarfile.open(os.path.join(path, group + "@" + edit_date + ".tar"), "w") as tar:
        tar.add(settings.get_path("scenario", "activescenario"),
                arcname=os.path.basename(settings.get_path("scenario", "activescenario")))
    tar.close()


def load_scenario_from_fs(group, date_timestamp=None):
    """
    This function load a scenario from tar and extract on fs
    :param group: Group of the scenario
    :param date_timestamp: Date of the scenario, if None, the newest is taken
    :return: True if succed, False if not
    """
    groups = get_scenario_by_group_in_fs()
    if group not in groups.keys():
        log.warning("There is no group {0} on file system => aborting load scenario".format(group))
        return False
    if len(groups[group]) < 1:
        log.warning("There is no file in group {0} on file system => aborting load scenario".format(group))
        return False
    if date_timestamp is None:
        newer = get_newer_scenario(groups[group])
    else:
        edit_date = datetime.datetime.fromtimestamp(float(date_timestamp)).strftime(
            settings.get("scenario", "date_format"))
        newer = None
        for scenario in groups[group]:
            if scenario.date == edit_date:
                newer = scenario
                break
        if newer is None:  # Can't find scenario in fs
            log.error("Can't find scenario ({0}@{1}) in fs".format(group, edit_date))
            return False
    path = os.path.join(settings.get_path("scenario"), group)
    tar_path = os.path.join(path, group + "@" + newer.date + ".tar")
    log.log("raw", "Ask to load {0} from fs to update scenario ".format(tar_path))
    with tarfile.open(tar_path, "r") as tar:
        # RM current scenario active directory ! #
        if os.path.exists(settings.get_path("scenario", "activescenario")):
            shutil.rmtree(settings.get_path("scenario", "activescenario"))
        ##
        tar.extractall(path=settings.get_path("scenario"))  # path=settings.get("path", "scenario"))
        return True
    # if here it's because we ca not open tar file
    log.warning("Error when opening scnario at {0}".format(os.path.join(path, group + "@" + newer.date + ".tar")))
    return False


class ScenarioFile:
    """
        This class represent a scenario file in the fs
    """

    def __init__(self, path, group, edit_date, dateobj, user_ip="", distant_path=""):
        """
            :param path: Absolute path of the scenario file
            :param group: Work group of the scenario
            :param edit_date: Edite date of the file
            :param dateobj: Datetime object which represent edit date
            :param distant_path: Distant path if received from OSC
            :param user_ip: user@ip if received from OSC
        """
        self.path = path
        self.group = group
        self.date = edit_date
        self.dateobj = dateobj
        self.distant_path = distant_path
        self.user_ip = user_ip

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.group == other.group and self.date == other.date

    def __ne__(self, other):
        return not self.__eq__(other)

    def get_from_distant(self):
        """
            This function use scp to copy a distant scenario to the local filesystem
            :return:
        """
        # if settings.get("sys", "raspi"):
        # scp = ExternalProcess("scp")
        # scp.command += " {options} {ip}:{path} {path}".format(
        # ip=ip, path=self.path, options=settings.get("sync", "scp_options"))
        # log.log("raw", "SCP : Try to get distant scenario {0} with {1}".format(self, scp.command))
        #     scp.start()
        #     scp.join(timeout=settings.get("sync", "scenario_sync_timeout"))
        # else:
        #     log.warning("!! NOT IMPLEMENTED !!")
        #     log.warning("Should copy distant scenario {0} with scp but we are not on a raspi")
        log.log("raw", "path : {0}, distant_path {1}".format(self.path, self.distant_path))
        scp = ExternalProcess("scp")
        scp.command += " {options} {ip}:{distant_path} {path}".format(
            ip=self.user_ip,
            distant_path=os.path.join(self.distant_path, os.path.relpath(self.path, settings.get_path("scenario"))),
            path=self.path, options=settings.get("sync", "scp_options"))
        log.log("raw", "SCP : Try to get distant scenario {0} with {1}".format(self, scp.command))
        scp.start()
        try:
            scp.join(timeout=settings.get("sync", "scenario_sync_timeout"))
            log.error("END of scp : {0} with {1}".format(self, scp.command))
            if not os.path.exists(self.path):       # Test if the file really exist after scp
                log.error("SCP ERROR MAYBE CORRUPTED (reboot ?)")
                raise RuntimeError()
        except RuntimeError:
            log.warning("Can't get scenario {0} with {1}".format(self, scp.command))
            return False
        return True

    @staticmethod
    def create_by_path(path):
        """
            This function create a ScenarioFile by path
            :param path: Absolute path of the scenario file
        """
        filename = os.path.basename(path)
        group = filename[:-settings.get("scenario", "date_len")]
        edit_date = filename[-settings.get("scenario", "date_len") + 1:-4]
        dateobj = datetime.datetime.strptime(edit_date, settings.get("scenario", "date_format"))
        return ScenarioFile(path, group, edit_date, dateobj)

    @staticmethod
    def create_by_OSC(group, edit_date, user_ip="", distant_path=""):
        """
            This function create a ScenarioFile by OSC
            :param user_ip: user@ip of the sender
            :param distant_path: Distant path of the scenario dir from the sender
            :param group: group recv by OSC
            :param edit_date: edit_date recv by OSC
        """
        filename = group + "@" + edit_date + ".tar"
        path = os.path.join(settings.get_path("scenario"), group, filename)
        dateobj = datetime.datetime.strptime(edit_date, settings.get("scenario", "date_format"))
        return ScenarioFile(path, group, edit_date, dateobj, user_ip=user_ip, distant_path=distant_path)

    def __str__(self):
        return "ScenarioFile : {0}@{1}".format(self.group, self.date)

    def __repr__(self):
        return self.__str__()


def get_scenario_by_group_in_fs():
    """
    This function return a dictionary with groups in keys and foreach a list of version
    :return: dictionary with groups in keys and foreach a list of version
    """
    scenario_by_group = dict()
    for path, dirs, files in os.walk(settings.get_path("scenario")):
        if os.path.split(path)[1][:len(settings.get("sync",
                                                    "escape_scenario_dir"))] == settings.get("sync",
                                                                                             "escape_scenario_dir"):
            continue  # Ignore this directory
        group = os.path.basename(path)
        if group not in scenario_by_group.keys():
            scenario_by_group[group] = list()
        for sfile in files:
            try:
                scenario = ScenarioFile.create_by_path(os.path.join(path, sfile))
                scenario_by_group[group].append(scenario)
            except Exception as e:
                log.warning("Error during parsing a archive scenario file at {0}".format(sfile))
                log.exception(log.show_exception(e))
    return scenario_by_group


def get_scenario_by_group_in_osc(osc_args, ip):
    """
    This function return a dictionary with groups in keys and foreach a list of version
    :param osc_args: OSC args
    :param  ip: ip of the sender
    :return: dictionary with groups in keys and foreach a list of version
    """
    log.log("raw", "Recv osc_args : {0}".format(osc_args))
    user_ip = osc_args.pop(0) + "@" + ip
    distant_path = osc_args.pop(0)
    scenario_by_group = dict()
    if len(osc_args) % 2 != 0:
        log.critical("We must have n*2 arguments (one for group the other for date)")
        return []
    for i in range(len(osc_args) / 2):
        scenario = ScenarioFile.create_by_OSC(osc_args[2 * i], osc_args[2 * i + 1], user_ip=user_ip,
                                              distant_path=distant_path)
        # log.log("raw", "[i={0}]Create scenario : {1}".format(i, scenario))
        if scenario.group not in scenario_by_group.keys():
            # log.log("raw", "New group : {0}".format(scenario.group))
            scenario_by_group[scenario.group] = list()
        scenario_by_group[scenario.group].append(scenario)
    log.log("raw", "Return : {0}".format(scenario_by_group))
    return scenario_by_group


def get_newer_scenario(group):
    """
    This function return the newer scenario version of a scenario group
    :param group: list of scneario versions
    :return: The newer version (ScenarioFile)
    """
    if len(group) > 0:
        newer = group[0]
    else:
        return None  # There is no file in group
    for version in group:
        if version.dateobj > newer.dateobj:
            newer = version
    return newer

#
# class MediaMoved:
# """
# This class just represent the fact that the file as change his place
# """
#
# def __init__(self, old_path, new_path):
#         self.old_path = old_path
#         self.new_path = new_path
#
#
# class MediaChanged:
#     """
#     This class just represent the fact that the file as change his place
#     """
#
#     def __init__(self, path, current_checksum, new_checksum):
#         self.path = path
#         self.current_checksum = current_checksum
#         self.new_checksum = new_checksum
#
#
# class MediaUnknown:
#     """
#     This class just represent the fact that the file isn't in the filesystem at all
#     """
#
#     def __init__(self, path, checksum):
#         self.path = path
#         self.current = checksum
#
#
# def get_fs_checksum(path):
#     """
#     This function return the checksum of a file on the filesystem
#     :param path: Path to the file
#     :return:
#     """
#     with open(path, "rb") as ofile:
#         return pyhashxx.hashxx(ofile.read())
#
#
# def parse_media_dir():
#     """
#     This function parse the media directory to check current existing files
#     :return:
#     """
#     tree = dict()
#     for root, dirs, files in os.walk(settings.get("path", "media")):
#         for f in files:
#             tree[os.path.join(root, f)] = get_fs_checksum(os.path.join(root, f))
#     return tree
#
#
# def is_onfs(path, checksum, fs_tree):
#     """
#     This function search in the media directory if the media is in there
#     :param path: Media path
#     :param checksum: Checksum of the media
#     :param fs_tree: filesystem tree return by parse_media_dir
#     :return:
#     """
#     if path in fs_tree.keys():  # A file have the same name in the fs
#         if fs_tree[path] == checksum:  # The file is the same
#             return True
#         else:  # The file have changed
#             return MediaChanged(path, fs_tree[path], checksum)
#     elif checksum in fs_tree.values():
#         for old_path, cs in fs_tree.items():
#             if cs == checksum:
#                 return MediaMoved(old_path, path)  # Old path of the file
#     else:
#         return MediaUnknown(path, checksum)  # The file is not present at all
#
#
# def do_move_file(old_path, new_path, retry=False):
#     """
#     This function move a file from a path to another
#     :param old_path:
#     :param new_path:
#     :param retry: If True, an erro will be fatal
#     :return:
#     """
#     try:
#         shutil.move(old_path, new_path)
#         return True
#     except Exception:
#         if retry is not True:
#             os.remove(new_path)
#             return do_move_file(old_path, new_path)
#         else:
#             return False




