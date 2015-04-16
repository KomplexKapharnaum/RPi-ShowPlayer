# -*- coding: utf-8 -*-
#
#
# This module provide a complexe sync protocol
# It only sync media
#

import os

import pyudev

from libs.oscack import message, network, DNCserver, BroadcastAddress
from engine.threads import network_scheduler, patcher

from engine import media
from engine import fsm
from libs.oscack import network
from engine.setting import settings
from engine.log import init_log

log = init_log("msync")

machine = fsm.FiniteStateMachine("MediaSyncProtocol")

flag_usb_plugged = fsm.Flag("USB_PLUGGED", TTL=None, JTL=None)
flag_usb_copy_error = fsm.Flag("USB_MEDIA_COPY_ERROR", TTL=2, JTL=10)
flag_update_media_list = fsm.Flag("UPDATE_MEDIA_LIST", TTL=2, JTL=None)
flag_timeout_send_list = fsm.Flag("TIMEOUT_SEND_MEDIA_LIST", TTL=1, JTL=None)
flag_timeout = fsm.Flag("TIMEOUT", TTL=None, JTL=None)
flag_scp_copy_error = fsm.Flag("SCP_COPY_MEDIA_ERROR", TTL=None, JTL=None)
flag_update_sync_flag = fsm.Flag("UPDATE_SYNC_FLAG", TTL=None, JTL=None)
flag_init_end = fsm.Flag("INIT_END", TTL=None, JTL=None)

msg_media_version = network.UnifiedMessageInterpretation("/sync/media/version", values=None, ACK=False,
                                                         JTL=3, TTL=1, flag_name="RECV_MEDIA_LIST")
msg_sync_flag = network.UnifiedMessageInterpretation("/sync/flag", values=(
    ('f', "timestamp"),
    ('i', "syncglobal"),
    ('i', "video")), ACK=False, JTL=3, TTL=1, flag_name="RECV_SYNC_FLAG")
msg_error_diskfull = network.UnifiedMessageInterpretation("/error/diskfull", values=(
    ('s', "path"),
    ('i', "size"),  # in Ko
    ('i', 'free')  # in Ko
), ACK=False, auto_add=False)

context_udev = pyudev.Context()
monitor_udev = None  # future Udev monitor
async_monitor_udev = None  # future observer for udev monitor

needed_media_list = None
unwanted_media_list = None


def init(flag):
    """
    This function init the scynmedia protocol
    :param flag:
    :return:
    """
    flag = fsm.Flag("INIT")
    global monitor_udev
    global async_monitor_udev
    global needed_media_list
    global unwanted_media_list
    monitor_udev = pyudev.Monitor.from_netlink(context_udev)
    monitor_udev.filter_by('block')  # get only block information
    monitor_udev.start()
    async_monitor_udev = media.UdevThreadMonitor(monitor_udev, machine, flag_usb_plugged)
    # TODO get the needed media list from scenario
    needed_media_list = media.MediaList()  # here come the media list
    unwanted_media_list = media.get_unwanted_media_list(needed_media_list)
    flag = flag_init_end.get()
    flag.args["timeout"] = settings.get("sync", "timeout_wait_syncflag")
    machine.append_flag(flag)


def _pass(flag):
    pass


def append_timeout_flag():
    """
    This function just add the timeout flag in the machine
    :return:
    """
    machine.append_flag(flag_timeout.get())


def send_sync_flag(flag):
    """
    Send our sync flag to target content in flag (fsm flag)
    :param flag: FSM flag wich content target to the flag
    :return:
    """
    if "timeout" in flag.args.keys():
        network_scheduler.enter(flag.args["timeout"], append_timeout_flag)
    if "target" not in flag.args.keys():
        target = message.Address("255.255.255.255")
    else:
        target = flag.args["target"]
    message.send(target, msg_sync_flag.get(timestamp=settings.get("sync", "flag_timestamp"),
                                           syncglobal=settings.get("sync", "enable"),
                                           video=settings.get("sync", "video")))
    log.log("raw", "Finish to send sync flag")


def trans_does_flag_newer(flag):
    """
    This function test if recv flag timestamp is newer than us
    :param flag:
    :return:
    """
    if flag.args["args"]["timestamp"] > settings.get("sync", "flag_timestamp"):
        return step_update_sync_flag
    else:
        flag.args["target"] = flag.args["src"]
        return step_send_sync_flag


def sync_media_on():
    """
    This function is not in a fsm, check if we must sync media or not
    :return:
    """
    return settings.get("sync", "enable") and settings.get("sync", "media")


def trans_usb_have_dnc_media(flag):
    """
    This function check if there is a dnc/media path in each mounted usb parition
    :param flag:
    :return:
    """
    path = settings.get("path", "usb")
    flag.args["trans_enough_place"] = trans_enought_place
    flag.args["trans_end"] = step_usb_end_copy
    flag.args["trans_free"] = step_put_media_on_fs
    flag.args["trans_full"] = trans_can_free
    for f in path:
        if os.path.isdir(f):
            if os.path.exists(os.path.join(path, f, "dnc", "media")):
                flag.args["usb_path"] = os.path.join(path, f, "dnc", "media")
                flag.args["files_to_test"] = list()
                for usb_path, dirs, files in os.walk(flag.args["usb_path"]):  # Retreived file list to check
                    for usb_f in files:
                        abs_path = os.path.join(usb_path, usb_f)
                        rel_path = os.path.relpath(abs_path, path)
                        log.log("raw", "Add to test list {0} with path : {1}".format(rel_path, abs_path))
                        flag.args["files_to_test"].append(media.Media.from_usb(rel_path, abs_path))
                log.info("There is a dnc/media path, start copy")
                return trans_need_media_in
            else:
                log.info("There is no dnc/media path, abort copy")
                return step_main_wait


def does_want_media(media, needed_list):
    """
    This function check if the media is needed and newer based on the wanted_list
    :param media: Media object of the media to check
    :param needed_list: List of media needed in scenario
    :return: True if need, False instead
    """


def trans_need_media_in(flag):
    """
    This function check if there a media needed in the files_to_test passed by the flag
    :param flag: need args : files_to_test, trans_need, trans_end
    :return:
    """
    global needed_media_list
    while len(flag.args["files_to_test"]) > 0:
        f = flag.args["files_to_test"].pop()
        if needed_media_list.need(f):
            flag.args["get_media"] = f
            return flag.args["trans_enough_place"]
    return flag.args["trans_end"]


def get_fs_media_free_space():
    """
    This function only return the free space (in Ko) of the project filesystem for media
    This his the free space available for the user (- protected space)
    :return:
    """
    s = os.statvfs(settings.get("path", "media"))
    return s.f_frsize * s.f_bavail / 1024  # in Ko


def trans_enought_place(flag):
    """
    This function test if there is enought place left on the file system
    :param flag: args need : get_media, trans_free, trans_full
    :return:
    """
    flag.args["free_space"] = get_fs_media_free_space() - settings.get("sync", "protected_space")
    if flag.args["get_media"].filesize > flag.args["free_space"]:
        return flag.args["trans_free"]
    else:
        return flag.args["trans_full"]


def trans_can_free(flag):
    """
    This function check if it's possible to free enough space to get the media
    :param flag: args need : get_media,
    :return:
    """
    global unwanted_media_list
    if len(unwanted_media_list) < 1:
        flag.args["error"] = "Not enough space, there no left media to remove, need {0}, only have {1}".format(
            flag.args["get_media"].filesize,
            flag.args["free_space"])
        return step_error
    elif unwanted_media_list.total_space() + flag.args["free_space"] < flag.args["get_media"].filesize:
        flag.args["error"] = "Not enough space, need {0}, only have {1}".format(flag.args["get_media"].filesize,
                                                                                flag.args["free_space"])
        return step_error
    else:
        return step_remove_media


def remove_media(flag):
    """
    This function remove an unwanted media in the file system
    :param flag:
    :return:
    """
    global unwanted_media_list
    if len(unwanted_media_list) < 1:
        log.error("There is no left media to remove")
        return None
    media_to_remove = unwanted_media_list.get_smaller_media()
    unwanted_media_list.remove(media_to_remove)   # Assume delete or undeletable
    if not media_to_remove.remove_from_fs():
        log.error("Unable to remove {0}".format(media_to_remove))


def get_media(flag):
    """
    This function get a media from a distant source (usb or osc)
    :param flag: need : get_media
    :return:
    """
    if not flag.args["get_media"].put_on_fs():
        log.error("Unabled to put {0} on fs".format(flag.args["get_media"]))


def monitor_usb_end_copy(flag):
    """
    This function will prompt a message to warn the uset that the copy is end    # SOULD GO TO SYNC BY NETWORK
    :param flag:
    :return:
    """
    log.info("USB copy end, wait a little for unplug your device")
    media.umount_partitions()
    log.info("USB umount end, you can unplug safely your device")


def error_function(flag):
    """
    This function manage erros during copy
    :param flag: need : error
    :return:
    """
    log.error(flag.args["error"])
    # TODO implement prompt on monitor


step_main_wait = fsm.State("STEP_MAIN_WAIT", function=_pass, transitions={
    flag_usb_plugged.uid: trans_usb_have_dnc_media
    # TODO implement the other transitions
})

step_send_sync_flag = fsm.State("STEP_SEND_SYNC_FLAG", function=send_sync_flag, transitions={
    flag_timeout.uid: step_main_wait,              # TODO : Go to first sync instead of main wait
    # msg_sync_flag.flag_name: "ERROR"        # TODO : Implement newer sync flag ?
})

step_init = fsm.State("INIT_SYNC_MEDIA", function=init, transitions={
    flag_init_end.uid: step_send_sync_flag
})

step_put_media_on_fs = fsm.State("STEP_PUT_MEDIA_ON_FS", function=get_media, transitions={
    True: trans_need_media_in
})

step_usb_end_copy = fsm.State("STEP_END_COPY", function=monitor_usb_end_copy, transitions={
    None: step_main_wait        # TODO : Go to direct send media list via network
})

step_remove_media = fsm.State("STEP_REMOVE_MEDIA", function=remove_media, transitions={
    True: trans_enought_place
})

step_error = fsm.State("STEP_ERROR", function=error_function, transitions={
    flag_timeout.uid: step_main_wait
})










