# -*- coding: utf-8 -*-
#
#
# This file provide some Etapes which are accessible from the scenario scope
#
#

from scenario import globaletape, link
from scenario import functions
from engine.log import init_log

log = init_log("etapes")


@link({"FS_TIMELINE_UPDATED": "DEVICE_UPDATE_TIMELINE"})
def device_control(flag, **kwargs):
    pass

@link({None: "DEVICE_CONTROL"})
def device_update_timeline(flag, **kwargs):
    # TODO GET THE TAR // UPDATE ACTIVE SCENARIO // RELOAD SCENARIO
    pass

@link({None: "DEVICE_CONTROL"})
def device_update_timeline(flag, **kwargs):
    # TODO GET THE TAR // UPDATE ACTIVE SCENARIO // RELOAD SCENARIO
    pass


# @globaletape("DEVICE_MANAGER_CONTROL", {
#                 None: "DEVICE_MANAGER"})
# def main_device_control(flag, **kwargs):
#     """
#     This function provide main control on the device
#     :param flag:
#     :param kwargs:
#     :return:
#     """
#     log.debug("=> Device control : {0}".format(flag.args["args"][0]))
#     if flag.args["args"][0] == "reboot_manager":
#         log.log("raw", "call reboot_manager")
#         functions.reboot_manager()
