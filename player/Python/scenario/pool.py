# -*- coding: utf-8 -*-
#
# This file is a file with all objects define in the scenario
#

from engine.setting import settings
from engine import log, fsm
log = log.init_log("pool")

# from engine import fsm

Etapes_and_Functions = dict()
Signals = dict()
Scenes = dict()
Frames = list()
Devices = dict()
Cartes = dict()
Patchs = dict()
Medias = dict()
cross_ref = list()

# MANAGER = fsm.FiniteStateMachine
MANAGER = None
CURRENT_FRAME = None
CURRENT_SCENE = None
FSM = list()
DEVICE_FSM = list()
GLOBALS = dict()
MANAGERMODULE = None

def init():
    """
    This function init pool variable before parsing a new scenario file
    :return:
    """
    # STOP ALREADY RUNNING POOL MACHINES
    stop()
    # CLEAR POOL
    global Etapes_and_Functions, Signals, Scenes, Frames, Devices, Cartes, Patchs, Medias, cross_ref
    global MANAGER, CURRENT_FRAME, CURRENT_SCENE, FSM, DEVICE_FSM, GLOBALS
    Etapes_and_Functions = dict()
    Signals = dict()
    Scenes = dict()
    Frames = list()
    Devices = dict()
    Cartes = dict()
    Patchs = dict()
    Medias = dict()
    cross_ref = list()
    MANAGER = None
    CURRENT_FRAME = None
    CURRENT_SCENE = None
    FSM = list()
    DEVICE_FSM = list()
    GLOBALS = dict()


def start():
    global MANAGER
    log.debug('{0}'.format(Cartes))
    if settings["uName"] in Cartes.keys():
        import manager
        Cartes[settings["uName"]].device.launch_manager()
        MANAGER = fsm.FiniteStateMachine("Manager")
        MANAGER.start(manager.step_init)
        MANAGER.append_flag(manager.start_flag.get())
    else:
        MANAGER = None
        log.info("== NO SCENARIO FOR: {0}".format(settings["uName"]))


def stop():
    global MANAGER
    if MANAGER is not None:
        MANAGER.stop()
        MANAGER.join()
    for sfsm in FSM:
        sfsm.stop()
        sfsm.join()
    for sfsm in DEVICE_FSM:
        sfsm.stop()
        sfsm.join()


def restart():
    stop()
    init()
    start()


def do_cross_ref():
    """
    This function write reference for each element in cross ref
    :return:
    """
    global Etapes_and_Functions
    for elem in cross_ref:
        elem[0][elem[1]] = Etapes_and_Functions[elem[2]]
