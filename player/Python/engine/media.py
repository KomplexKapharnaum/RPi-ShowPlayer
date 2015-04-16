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

import pyudev

from modules._classes import ExternalProcess
from libs import pyhashxx
from engine.setting import settings
from engine import tools

from engine.log import init_log

log = init_log("media", log_lvl="raw")


def get_unwanted_media_list(needed_media_list):
    """
    This function return the list of media present on the filesystem but which are not required by scenario
    :param needed_media_list: NeededMediaList obj, which contains all of the needed media
    :return:
    """
    unwanted_media_list = MediaList()
    media_path = settings.get("path", "media")
    for path, dirs, files in os.walk(media_path):  # Retreived file list to check
        for f in files:
            abs_path = os.path.join(path, f)
            rel_path = os.path.relpath(abs_path, media_path)
            if rel_path in needed_media_list:
                continue
            unwanted_media_list.append(Media.from_fs(rel_path, abs_path, os.path.getsize(abs_path)))
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
        for elem in self:
            if media_obj.rel_path == elem.rel_path and media_obj.mtime > elem.mtime:
                return True
        return False

    def get_smaller_media(self):    #, ignore=()):
        """
        This function return the smaller media to delete in the MediaList
        # :param ignore: list of elem to ignore
        """
        smaller = self[0]
        for elem in self:
            if elem.filesize < smaller.filesize: # and elem not in ignore:
                smaller = elem
        return smaller

    def __repr__(self):
        r = "Media list : \n"
        for elem in self:
            r += elem + "\n"

    def __str__(self):
        return self.__repr__()

    # def get_media_to_delete(self, needspace):
    #     """
    #     This function return a list of smaller media
    #     """
    #     freespace = 0
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
        log.log("raw", "Init {0}".format(self))

    @staticmethod
    def from_scenario(rel_path):
        """
        Create a Media from a rel path in scenario
        :param rel_path: rel_path of the media
        """
        path = os.path.join(settings.get("path", "media"), rel_path)
        if not os.path.exists(path):
            log.log("raw", "Scenario media {0} not present in fs {1}".format(rel_path, path))
            # return False
            mtime = 0
        else:
            mtime = time.ctime(os.path.getmtime(path))
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
        mtime = time.ctime(os.path.getmtime(abs_path))
        filesize = int(os.path.getsize(abs_path) / 1000)  # In Ko
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
        return Media(rel_path=rel_path, mtime=None, source="fs", source_path=abs_path, filesize=filesize)

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
        if self.source == "usb":
            dest_path = os.path.join(settings.get("path", "media"), self.rel_path)
            dir_path = os.path.dirname(dest_path)
            if not os.path.exists(dir_path):
                log.log("raw", "Create directory to get file {0}".format(dest_path))
                os.makedirs(dir_path)
            cp = ExternalProcess("cp")
            cp.command += " --preserve=timestamp {0} {1}".format(self.source_path, dest_path)
            log.log("raw", "Start CP copy with {0}".format(cp.command))
            cp.start()
            try:
                cp.join(timeout=self.filesize / settings.get("sync", "usb_speed_min") + 5)  # Minimum 5 seconds
            except RuntimeError as e:
                log.exception(log.show_exception(e))
                # if error_fnct is not None:
                # error_fnct(self, e)
                cp.stop()
                return self, e
            cp.stop()
            return True
        elif self.source == "scp":
            log.warning("!! NOT IMPLEMENTED !! ")
        else:
            log.warning("What the ..? ")

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
        os.mkdir(mount_path)
    else:
        log.warning("Warning, we mount a device {0} on an existing mount point {1}".format(block_path, mount_path))
    mount_cmd.command += " {0} {1}".format(block_path, mount_path)
    mount_cmd.start()
    try:
        mount_cmd.join(timeout=settings.get("sync", "usb_mount_timeout"))
    except RuntimeError as e:
        log.exception(log.show_exception(e))
        log.warning("Unable to mount  {0} on {1} ".format(block_path, mount_path))
        mount_cmd.stop()
        return False
    mount_cmd.stop()
    return True


def umount_partitions():
    """
    This function unmount all partition in usb directory
    :return:
    """
    log.log("raw", "Start to umount partitions")
    sucess = True
    for f in os.listdir(settings.get("path", "usb")):
        path = os.path.join(settings.get("path", "usb"), f)
        log.log("raw", "found on usb dir : {0}".format(path))
        if os.path.ismount(path):
            log.log("raw", "Found directory to umount {0}".format(f))
            umount_cmd = ExternalProcess(name="umount")
            umount_cmd.command += " " + path
            umount_cmd.start()
            try:
                umount_cmd.join(timeout=settings.get("sync", "usb_mount_timeout"))
                log.log("debug", "Correctly umount {0}".format(path))
                os.rmdir(path)
                log.log("raw", "Correctly remove after umount {0}".format(path))
            except RuntimeError as e:
                log.exception(log.show_exception(e))
                log.warning("Unable to umount {0}".format(path))
                umount_cmd.stop()
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
                continue
            elif device.action not in ("add", "change"):
                log.log("raw", "Block device event {1} (not add) : {0}".format(device.device_node, device.action))
                continue
            devdir = os.path.dirname(device.device_node)
            devname = os.path.basename(device.device_node)
            mounted = 0
            for block in os.listdir(devdir):
                if devname in block and devname != block:  # Found a partition
                    mounted += mount_partition(os.path.join(devdir, block), os.path.join(settings.get("path", "usb"),
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
    path = os.path.join(settings.get("path", "scenario"), group)
    if not os.path.exists(path):
        os.mkdir(path)
    with tarfile.open(os.path.join(path, group + "@" + edit_date + ".tar"), "w") as tar:
        tar.add(settings.get("path", "activescenario"),
                arcname=os.path.basename(settings.get("path", "activescenario")))
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
    path = os.path.join(settings.get("path", "scenario"), group)
    tar_path = os.path.join(path, group + "@" + newer.date + ".tar")
    log.log("raw", "Ask to load {0} from fs to update scenario ".format(tar_path))
    with tarfile.open(tar_path, "r") as tar:
        # RM current scenario active directory ! #
        if os.path.exists(settings.get("path", "activescenario")):
            shutil.rmtree(settings.get("path", "activescenario"))
        ##
        tar.extractall(path=settings.get("path", "scenario"))  # path=settings.get("path", "scenario"))
        return True
    # if here it's because we ca not open tar file
    log.warning("Error when opening scnario at {0}".format(os.path.join(path, group + "@" + newer.date + ".tar")))
    return False


class ScenarioFile:
    """
        This class represent a scenario file in the fs
    """

    def __init__(self, path, group, edit_date, dateobj):
        """
            :param path: Absolute path of the scenario file
        """
        self.path = path
        self.group = group
        self.date = edit_date
        self.dateobj = dateobj

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.group == other.group and self.date == other.date

    def __ne__(self, other):
        return not self.__eq__(other)

    def get_from_distant(self, ip):
        """
            This function use scp to copy a distant scenario to the local filesystem
            :param ip: Target ip of the distant client
            :return:
        """
        scp = ExternalProcess("scp")
        scp.command += " -p -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no {ip}:{path} {path}".format(
            ip=ip, path=self.path)
        log.log("raw", "SCP : Try to get distant scenario {0} with {1}".format(self, scp.command))
        scp.start()
        scp.join(timeout=settings.get("sync", "scenario_sync_timeout"))


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
    def create_by_OSC(group, edit_date):
        """
            This function create a ScenarioFile by OSC
            :param group: group recv by OSC
            :param edit_date: edit_date recv by OSC
        """
        filename = group + "@" + edit_date + ".tar"
        path = os.path.join(settings.get("path", "scenario"), group, filename)
        dateobj = datetime.datetime.strptime(edit_date, settings.get("scenario", "date_format"))
        return ScenarioFile(path, group, edit_date, dateobj)

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
    for path, dirs, files in os.walk(settings.get("path", "scenario")):
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


def get_scenario_by_group_in_osc(osc_args):
    """
    This function return a dictionary with groups in keys and foreach a list of version
    :param osc_args: OSC args
    :return: dictionary with groups in keys and foreach a list of version
    """
    log.log("raw", "Recv osc_args : {0}".format(osc_args))
    scenario_by_group = dict()
    if len(osc_args) % 2 != 0:
        log.critical("We must have n*2 arguments (one for group the other for date)")
        return []
    for i in range(len(osc_args) / 2):
        scenario = ScenarioFile.create_by_OSC(osc_args[2 * i], osc_args[2 * i + 1])
        log.log("raw", "[i={0}]Create scenario : {1}".format(i, scenario))
        if scenario.group not in scenario_by_group.keys():
            log.log("raw", "New group : {0}".format(scenario.group))
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
    newer = group[0]
    for version in group:
        if version.dateobj > newer.dateobj:
            newer = version
    return newer


class MediaMoved:
    """
    This class just represent the fact that the file as change his place
    """

    def __init__(self, old_path, new_path):
        self.old_path = old_path
        self.new_path = new_path


class MediaChanged:
    """
    This class just represent the fact that the file as change his place
    """

    def __init__(self, path, current_checksum, new_checksum):
        self.path = path
        self.current_checksum = current_checksum
        self.new_checksum = new_checksum


class MediaUnknown:
    """
    This class just represent the fact that the file isn't in the filesystem at all
    """

    def __init__(self, path, checksum):
        self.path = path
        self.current = checksum


def get_fs_checksum(path):
    """
    This function return the checksum of a file on the filesystem
    :param path: Path to the file
    :return:
    """
    with open(path, "rb") as ofile:
        return pyhashxx.hashxx(ofile.read())


def parse_media_dir():
    """
    This function parse the media directory to check current existing files
    :return:
    """
    tree = dict()
    for root, dirs, files in os.walk(settings.get("path", "media")):
        for f in files:
            tree[os.path.join(root, f)] = get_fs_checksum(os.path.join(root, f))
    return tree


def is_onfs(path, checksum, fs_tree):
    """
    This function search in the media directory if the media is in there
    :param path: Media path
    :param checksum: Checksum of the media
    :param fs_tree: filesystem tree return by parse_media_dir
    :return:
    """
    if path in fs_tree.keys():  # A file have the same name in the fs
        if fs_tree[path] == checksum:  # The file is the same
            return True
        else:  # The file have changed
            return MediaChanged(path, fs_tree[path], checksum)
    elif checksum in fs_tree.values():
        for old_path, cs in fs_tree.items():
            if cs == checksum:
                return MediaMoved(old_path, path)  # Old path of the file
    else:
        return MediaUnknown(path, checksum)  # The file is not present at all


def do_move_file(old_path, new_path, retry=False):
    """
    This function move a file from a path to another
    :param old_path:
    :param new_path:
    :param retry: If True, an erro will be fatal
    :return:
    """
    try:
        shutil.move(old_path, new_path)
        return True
    except Exception:
        if retry is not True:
            os.remove(new_path)
            return do_move_file(old_path, new_path)
        else:
            return False




