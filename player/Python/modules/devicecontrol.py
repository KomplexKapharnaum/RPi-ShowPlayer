# -*- coding: utf-8 -*-
#
#
# This file provide some Etapes which are accessible from the scenario scope
#
#

import scenario
from scenario import globaletape, link
from scenario import functions, pool, parsing
from engine.log import init_log
from engine.setting import settings
from engine.media import load_scenario_from_fs

log = init_log("etapes")


@link({"FS_TIMELINE_UPDATED": "DEVICE_UPDATE_TIMELINE",
        "/scenario/restart": "DEVICE_SCENARIO_RESTART",
        "TELECO_MESSAGE": "DEVICE_TELECO_CMD"})
def device_control(flag, **kwargs):
    pass

@link({None: "DEVICE_SCENARIO_RESTART"})
def device_update_timeline(flag, **kwargs):
    load_scenario_from_fs(settings["current_timeline"])

@link({None: "DEVICE_CONTROL"})
def device_scenario_restart(flag, **kwargs):
    pool.stop()
    scenario.init()
    parsing.load()
    pool.start()
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
