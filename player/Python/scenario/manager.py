# -*- coding: utf-8 -*-
#
# This file provide a FSM which manage a scenario by witch between scenes
#

import threading

import libs.oscack

from engine.threads import patcher
from engine import fsm
from engine.setting import settings
import scenario
#from scenario import pool, CURRENT_FRAME, CURRENT_SCENE, FSM
from modules import DECLARED_PATCHER

from engine.log import init_log
log = init_log("manager")


already_init = threading.Event()
already_init.clear()


def patch_msg(path, args, types, src,):
    log.log("debug", "OSC WILD CARD get {0}".format(path))
    patcher.patch(libs.oscack.network.get_flag_from_msg(path, args, types, src))


def init(flag):
    global already_init
    log.debug("Init manager")
    scenario.CURRENT_FRAME = 0
    # Register Device Patchs
    # pool.Cartes[settings["uName"]].device.register_patchs()
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


def start_scene(flag):
    log.log("raw", "Start scene. Current Frame : {0}".format(scenario.CURRENT_FRAME))
    for sfsm in scenario.FSM:
        sfsm.stop()
        scenario.FSM.remove(sfsm)
    scenario.CURRENT_SCENE = scenario.pool.Frames[scenario.CURRENT_FRAME]
    scenario.CURRENT_SCENE.start()


def _pass(flag):
    pass


def next_scene(flag):
    scenario.CURRENT_FRAME = scenario.pool.Scenes[scenario.CURRENT_SCENE.uid]["until"]


def change_frame(flag):
    pass


def trans_change_frame(flag):
    pass


start_flag = fsm.Flag("START", TTL=None)
next_flag = fsm.Flag("NEXT_SCENE", TTL=None, JTL=None)

step_init = fsm.State("INIT_STATE", function=init)
step_start_scene = fsm.State("START_SCENE_STATE", function=start_scene)
step_wait = fsm.State("WAIT_STATE", function=_pass)
step_change = fsm.State("CHANGE_FRAME_STATE", function=change_frame)
step_next_scene = fsm.State("NEXT_SCENE_STATE", function=next_scene)

step_init.transitions = {
    "START": step_start_scene
}
# step_readcurrent.transitions = {
#     None: step_start_scene
# }
step_start_scene.transitions = {
    None: step_wait
}
step_wait.transitions = {
    next_flag.uid: step_next_scene
}
step_change.transitions = {
    None: step_start_scene
}
step_next_scene.transitions = {
    None: step_start_scene
}
