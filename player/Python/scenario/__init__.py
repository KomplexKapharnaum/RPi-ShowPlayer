# -*- coding: utf-8 -*-
import pool
import classes
import parsing
from engine import log, fsm
from engine.setting import settings
log = log.init_log("scenario")

CURRENT_FRAME = None
CURRENT_SCENE = None

DEVICE_FSM = list()
SCENARIO_FSM = None
FSM = list()


def init():
    """
    This function init pool variable before parsing a new scenario file
    :return:
    """
    # STOP ALREADY RUNNING POOL MACHINES
    stop()
    # CLEAR SCENARIO FSMs
    global SCENARIO_FSM, CURRENT_FRAME, CURRENT_SCENE, FSM, DEVICE_FSM, CARTE
    SCENARIO_FSM = None
    CURRENT_FRAME = None
    CURRENT_SCENE = None
    FSM = list()
    DEVICE_FSM = list()
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
    global SCENARIO_FSM, DEVICE_FSM
    log.log('raw', 'Cards available: {0}'.format(pool.Cartes))

    if settings["uName"] in pool.Cartes.keys():

        # START MODULES
        log.log("raw", "Start device modules")
        for name, etape in pool.Cartes[settings["uName"]].device.modules.items():
            dfsm = classes.ScenarioFSM(name)
            dfsm.start(etape)
            DEVICE_FSM.append(dfsm)
            log.info("= MODULE (Scenario) :: "+name)

        import manager
        SCENARIO_FSM = fsm.FiniteStateMachine("Manager")
        SCENARIO_FSM.start(manager.step_init)
        SCENARIO_FSM.append_flag(manager.start_flag.get())
    else:
        SCENARIO_FSM = None
        log.warning("== NO SCENARIO FOR: {0}".format(settings["uName"]))


def stop():
    # STOP MODULES
    for dfsm in DEVICE_FSM:
        dfsm.stop()
        dfsm.join()
    # if settings["uName"] in pool.Cartes.keys():
    #     pool.Cartes[settings["uName"]].stop_modules()

    global SCENARIO_FSM
    if SCENARIO_FSM is not None:
        SCENARIO_FSM.stop()
        SCENARIO_FSM.join()

    for sfsm in FSM:
        sfsm.stop()
        sfsm.join()


def restart():
    stop()
    init()
    start()
