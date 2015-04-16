# -*- coding: utf-8 -*-
#
#
# This file provide class and function to manage media on the Raspebrry Pi
#

import os
import shutil
import datetime
import tarfile

from modules._classes import ExternalProcess
from libs import pyhashxx
from engine.setting import settings

from engine.log import init_log

log = init_log("media")


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
        tar.add(settings.get("path", "activescenario"), arcname=os.path.basename(settings.get("path", "activescenario")))
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
        edit_date = datetime.datetime.fromtimestamp(float(date_timestamp)).strftime(settings.get("scenario", "date_format"))
        newer = None
        for scenario in groups[group]:
            if scenario.date == edit_date:
                newer = scenario
                break
        if newer is None:          # Can't find scenario in fs
            log.error("Can't find scenario ({0}@{1}) in fs".format(group, edit_date))
            return False
    path = os.path.join(settings.get("path", "scenario"), group)
    with tarfile.open(os.path.join(path, group + "@" + newer.date + ".tar"), "r") as tar:
        # RM current scenario active directory ! #
        if os.path.exists(settings.get("path", "activescenario")):
            shutil.rmtree(settings.get("path", "activescenario"))
        ##
        tar.extractall(path=settings.get("path", "scenario"))        # path=settings.get("path", "scenario"))
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
        edit_date = filename[-settings.get("scenario", "date_len") +1:-4]
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
            continue            # Ignore this directory
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
    for i in range(len(osc_args)/2):
        scenario = ScenarioFile.create_by_OSC(osc_args[2*i], osc_args[2*i+1])
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




