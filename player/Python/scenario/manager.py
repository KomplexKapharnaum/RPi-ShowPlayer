# -*- coding: utf-8 -*-
#
# This file provide a FSM which manage a scenario by witch between scenes
#

import libs.oscack

from engine.threads import patcher
from engine import fsm
from engine.setting import settings
from scenario import pool, DECLARED_PATCHER

from engine.log import init_log
log = init_log("manager")


def patch_msg(path, args, types, src,):
    patcher.patch(libs.oscack.network.get_flag_from_msg(path, args, types, src))


def init(flag):
    log.debug("Init manager")
    pool.CURRENT_FRAME = 0

    # Register Device Patchs
    # pool.Cartes[settings["uName"]].device.register_patchs()
    for patch in pool.Cartes[settings["uName"]].device.patchs:
        patcher.add_patch(patch.signal, patch.treatment[0], patch.treatment[1])

    # Register Global Patchs
    for patch in DECLARED_PATCHER.values():
        patcher.add_patch(patch.signal, patch.treatment[0], patch.treatment[1])
        # patcher.add_patch(patch)

    libs.oscack.DNCserver.add_method(None, None, patch_msg)       # TODO WE DO NOT NEED OSC FOR SCENARIO SYSTEM, deplace !


def start_scene(flag):
    log.log("raw", "Start scene. Current Frame : {0}".format(pool.CURRENT_FRAME))
    for sfsm in pool.FSM:
        sfsm.stop()
        pool.FSM.remove(sfsm)
    pool.CURRENT_SCENE = pool.Frames[pool.CURRENT_FRAME]
    pool.CURRENT_SCENE.start()


def _pass(flag):
    pass


def next_scene(flag):
    pool.CURRENT_FRAME = pool.Scenes[pool.CURRENT_SCENE.uid]["until"]


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