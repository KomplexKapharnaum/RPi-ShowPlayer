# -*- coding: utf-8 -*-
#
#
# This file provide some Etapes which are accessible from the scenario scope
#
#
import threading
from engine import fsm
from engine.threads import patcher
import scenario
import libs.oscack
from modules import link, DECLARED_PATCHER
from _classes import module
from engine.log import init_log
from engine.setting import settings
log = init_log("scenecontrol")

already_init = threading.Event()
already_init.clear()

def patch_msg(path, args, types, src,):
    # log.log("debug", "OSC WILD CARD get {0}".format(path))
    patcher.patch(libs.oscack.network.get_flag_from_msg(path, args, types, src))


@module('SceneControl')
@link({None: "scene_control"})
def scene_init(flag, **kwargs):
    global already_init
    log.debug("Init manager")
    scenario.CURRENT_FRAME = 0
    # Register Device Patchs
    # pool.Cartes[settings["uName"]].device.register_patchs()
    if settings["uName"] in scenario.pool.Cartes:
        for patch in scenario.pool.Cartes[settings["uName"]].device.patchs:
            patcher.add_patch(patch.signal, patch.treatment[0], patch.treatment[1])

        # Register Global Patchs
        for patch in DECLARED_PATCHER.values():
            patcher.add_patch(patch.signal, patch.treatment[0], patch.treatment[1])
            # patcher.add_patch(patch)
        # libs.oscack.DNCserver.del_method(None, None)                # Remove WILD CARD
        # libs.oscack.DNCserver.del_method(None, None)                # Remove WILD CARD (SEKU)
        if already_init.is_set():
            log.log("debug", "First init manager : set wildcard")
            libs.oscack.DNCserver.add_method(None, None, patch_msg)
            already_init.set()
        else:
            log.log("debug", "Omit wildcard because manager already been inited")
    else:
        log.log("important", "no device found in pool.Cartes")


@link({ "/scene/init": "scene_init",
        "/scene/start": "scene_start",
        "/scene/restart": "scene_restart",
        "/scene/previous": "scene_prev",
        "/scene/next": "scene_next",
        "/scene/stop": "scene_stop",
        })
def scene_control(flag, **kwargs):
    pass


@link({None: "scene_control"})
def scene_restart(flag, **kwargs):
    log.error("flag : {0}, kwargs : {1}".format(flag, kwargs))
    flag = fsm.Flag("SCENE_START")
    dest = "Self"
    if flag.args[0] == "GROUP":
        dest = "Group"
    patcher.patch(flag.get({"dest": dest}))


@link({None: "scene_control"})
def scene_start(flag, **kwargs):
    if scenario.CURRENT_FRAME > len(scenario.pool.Frames):
        scenario.CURRENT_FRAME = 0
    scenario.start_scene()
    log.log("debug", "Start SCENE {0}: {1}".format(scenario.CURRENT_FRAME, scenario.pool.Frames[scenario.CURRENT_FRAME]))

@link({None: "scene_control"})
def scene_prev(flag, **kwargs):
    if scenario.CURRENT_FRAME > 0:
        scenario.CURRENT_FRAME -= 1
        scenario.start_scene()

@link({None: "scene_control"})
def scene_next(flag, **kwargs):
    if scenario.CURRENT_FRAME < (len(scenario.pool.Frames)-1):
        scenario.CURRENT_FRAME += 1
        scenario.start_scene()

@link({None: "scene_control"})
def scene_stop(flag, **kwargs):
    scenario.stop_scene()






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
