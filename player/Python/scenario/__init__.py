# -*- coding: utf-8 -*-
import pool
import parsing
from engine import log, fsm
from engine.setting import settings
log = log.init_log("scenario")

CURRENT_FRAME = None
CURRENT_SCENE = None

SCENARIO_FSM = None
FSM = list()
DEVICE_FSM = list()

GLOBALS = dict()

def init():
    """
    This function init pool variable before parsing a new scenario file
    :return:
    """
    # STOP ALREADY RUNNING POOL MACHINES
    stop()
    # CLEAR SCENARIO FSMs
    global SCENARIO_FSM, CURRENT_FRAME, CURRENT_SCENE, FSM, DEVICE_FSM, GLOBALS
    SCENARIO_FSM = None
    CURRENT_FRAME = None
    CURRENT_SCENE = None
    FSM = list()
    DEVICE_FSM = list()
    GLOBALS = dict()
    # INIT POOL
    pool.clear()
    pool.load()

def load(use_archive=True):
    parsing.load(use_archive)


def reload():
    stop()
    init()
    load(False)
    start()


def start():
    global SCENARIO_FSM
    log.debug('Cards available: {0}'.format(pool.Cartes))
    if settings["uName"] in pool.Cartes.keys():
        import manager
        pool.Cartes[settings["uName"]].device.launch_manager()
        SCENARIO_FSM = fsm.FiniteStateMachine("Manager")
        SCENARIO_FSM.start(manager.step_init)
        SCENARIO_FSM.append_flag(manager.start_flag.get())
    else:
        SCENARIO_FSM = None
        log.info("== NO SCENARIO FOR: {0}".format(settings["uName"]))


def stop():
    global SCENARIO_FSM
    if SCENARIO_FSM is not None:
        SCENARIO_FSM.stop()
        SCENARIO_FSM.join()
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
