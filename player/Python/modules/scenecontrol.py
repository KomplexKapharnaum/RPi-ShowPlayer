# -*- coding: utf-8 -*-
#
#
# This file provide some Etapes which are accessible from the scenario scope
#
#
import threading
from engine import fsm, rtpsync
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


def patch_msg(path, args, types, src, ):
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


@link({"/scene/init": "scene_init",
       "/scene/start": "scene_start",
       "/scene/restart [dispo]": "scene_restart",
       "/scene/previous [dispo]": "scene_prev",
       "/scene/next [dispo]": "scene_next",
       "/scene/go [dispo] [frame]": "scene_go",
       "/scene/stop": "scene_stop",
})
def scene_control(flag, **kwargs):
    pass


@link({None: "scene_control"})
def scene_restart(flag, **kwargs):
    log.error("flag : {0}, kwargs : {1}".format(flag, kwargs))
    new_flag = fsm.Flag("SCENE_START")
    already_dest = False
    dest = list()
    if 'args' in flag.args.keys():
        dest += flag.args['args']
        already_dest = True
    if 'dest' in flag.args.keys():
        dest += flag.args['dest']
        already_dest = True
    if not already_dest:
        dest = ["Self", ]
        if len(flag.args['args']) > 0 and flag.args['args'][0] in ("Self", "Group", "All"):
            dest = [flag.args['args'][0], ]
    log.log("debug", "new frame {0}, flag {1}, dest {2}".format(scenario.CURRENT_FRAME, flag, dest))
    patcher.patch(new_flag.get({"dest": dest, "keyframe": scenario.CURRENT_FRAME}))


@link({None: "scene_control"})
def scene_start(flag, **kwargs):
    log.debug("Scene_start at {1} with {0} kwargs {2}".format(scenario.CURRENT_FRAME, flag, kwargs))
    if "keyframe" in flag.args.keys():
        scenario.CURRENT_FRAME = flag.args['keyframe']
    if scenario.CURRENT_FRAME > len(scenario.pool.Frames):
        scenario.CURRENT_FRAME = 0
    rtpsync.flag_wait_sync(flag)
    scenario.start_scene()
    log.log("debug",
            "Start SCENE {0}: {1}".format(scenario.CURRENT_FRAME, scenario.pool.Frames[scenario.CURRENT_FRAME]))


@link({None: "scene_control"})
def scene_prev(flag, **kwargs):
    log.debug("Scene_prev at {1} with {0} kwargs {2}".format(scenario.CURRENT_FRAME, flag, kwargs))
    if "keyframe" in flag.args.keys():
        scenario.CURRENT_FRAME = flag.args['keyframe']
        scenario.start_scene()
    else:
        if scenario.CURRENT_FRAME > 0:
            scenario.CURRENT_FRAME -= 1
        already_dest = False
        dest = list()
        if 'args' in flag.args.keys():
            dest += flag.args['args']
            already_dest = True
        if 'dest' in flag.args.keys():
            dest += flag.args['dest']
            already_dest = True
        if not already_dest:
            dest = ["Self", ]
            if len(flag.args['args']) > 0 and flag.args['args'][0] in ("Self", "Group", "All"):
                dest = [flag.args['args'][0], ]
        log.log("debug", "new frame {0}, flag {1}, dest {2}".format(scenario.CURRENT_FRAME, flag, dest))
        patcher.patch(flag.get({"dest": dest, "keyframe": scenario.CURRENT_FRAME}))


@link({None: "scene_control"})
def scene_next(flag, **kwargs):
    log.debug("Scene_next at {1} with {0} kwargs {2}".format(scenario.CURRENT_FRAME, flag, kwargs))
    if "keyframe" in flag.args.keys():
        scenario.CURRENT_FRAME = flag.args['keyframe']
        scenario.start_scene()
    else:
        if scenario.CURRENT_FRAME < (len(scenario.pool.Frames) - 1):
            scenario.CURRENT_FRAME += 1
        already_dest = False
        dest = list()
        if 'args' in flag.args.keys():
            dest += flag.args['args']
            already_dest = True
        if 'dest' in flag.args.keys():
            dest += flag.args['dest']
            already_dest = True
        if not already_dest:
            dest = ["Self", ]
            if len(flag.args['args']) > 0 and flag.args['args'][0] in ("Self", "Group", "All"):
                dest = [flag.args['args'][0], ]
        log.log("debug", "new frame {0}, flag {1}, dest {2}".format(scenario.CURRENT_FRAME, flag, dest))
        patcher.patch(flag.get({"dest": dest, "keyframe": scenario.CURRENT_FRAME}))

@link({None: "scene_control"})
def scene_go(flag, **kwargs):
    log.debug("Scene_go at {1} with {0} kwargs {2}".format(scenario.CURRENT_FRAME, flag, kwargs))
    if "frame" in flag.args.keys():
        if scenario.CURRENT_FRAME == int(flag.args['frame']):
            log.debug("ignore frame {0} because we are already inside".format(flag.args['frame']))
            return
        if scenario.CURRENT_FRAME > int(flag.args['frame']):
            log.debug("ignore frame {0} because we are in frame after that one".format(flag.args['frame']))
            return
        scenario.CURRENT_FRAME = int(flag.args['frame'])
        scenario.start_scene()
    else:
        if 'frame' in flag.args.keys() and 0 <= flag.args['frame'] <= len(scenario.pool.Frames):
            log.debug("found scene {0} from init scene {1}".format(flag.args['frame'],scenario.CURRENT_FRAME))
            scenario.CURRENT_FRAME = flag.args['frame']
        already_dest = False
        dest = list()
        if 'args' in flag.args.keys():
            dest += flag.args['args']
            already_dest = True
        if 'dest' in flag.args.keys():
            dest += flag.args['dest']
            already_dest = True
        if not already_dest:
            dest = ["Self", ]
            if len(flag.args['args']) > 0 and flag.args['args'][0] in ("Self", "Group", "All"):
                dest = [flag.args['args'][0], ]
        log.log("debug", "new frame {0}, flag {1}, dest {2}".format(scenario.CURRENT_FRAME, flag, dest))
        patcher.patch(flag.get({"dest": dest, "frame": scenario.CURRENT_FRAME}))

@link({None: "scene_control"})
def scene_stop(flag, **kwargs):
    scenario.stop_scene()


# 'TELECO_MESSAGE_BLINKGROUP': [],
# 'TELECO_MESSAGE_TESTROUTINE': ['testRoutine']


# @globaletape("DEVICE_MANAGER_CONTROL", {
# None: "DEVICE_MANAGER"})
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
