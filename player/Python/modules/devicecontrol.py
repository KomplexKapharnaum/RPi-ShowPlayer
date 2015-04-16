# -*- coding: utf-8 -*-
#
#
# This file provide some Etapes which are accessible from the scenario scope
#
#

import application
from scenario import link
from _classes import module
from engine.log import init_log
from engine.setting import settings
from engine.media import load_scenario_from_fs
log = init_log("devicecontrol")


@module('DeviceControl')
@link({"/device/reload": "device_reload",
        "/device/poweroff": "device_poweroff",
        "/device/reboot": "device_reboot",
        "/scene/previous": "device_scene_prev",
        "/scene/next": "device_scene_next",
        "/scene/restart": "device_scene_restart",
        "FS_TIMELINE_UPDATED": "device_update_timeline"})
def device_control(flag, **kwargs):
    pass


@link({None: "device_control"})
def device_reload(flag, **kwargs):
    application.reload()


@link({None: "device_control"})
def device_poweroff(flag, **kwargs):
    application.POWEROFF = 2


@link({None: "device_control"})
def device_reboot(flag, **kwargs):
    log.warning('PW: '+str(application.POWEROFF))
    application.POWEROFF = 3
    log.warning('PW: '+str(application.POWEROFF))

@link({None: "device_reload"})
def device_update_timeline(flag, **kwargs):
    load_scenario_from_fs(settings["current_timeline"])


@link({None: "device_control"})
def device_scene_prev(flag, **kwargs):
    pass


@link({None: "device_control"})
def device_scene_next(flag, **kwargs):
    pass


@link({None: "device_control"})
def device_scene_restart(flag, **kwargs):
    pass



# 'TELECO_MESSAGE_BLINKGROUP': [],
# 'TELECO_MESSAGE_TESTROUTINE': ['testRoutine']


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
