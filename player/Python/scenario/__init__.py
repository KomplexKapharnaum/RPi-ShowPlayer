# -*- coding: utf-8 -*-
import pool
import classes
import parsing
from engine import log,tools
from engine.setting import settings
log = log.init_log("scenario")

CURRENT_FRAME = 0
CURRENT_SCENE = None

MODULES_FSM = list()
SCENE_FSM = list()


def init():
    """
    This function init pool variable before parsing a new scenario file
    :return:
    """
    # STOP ALREADY RUNNING POOL MACHINES
    stop()
    # CLEAR SCENARIO FSMs
    global SCENE_FSM, MODULES_FSM, CARTE
    SCENE_FSM = list()
    MODULES_FSM = list()
    # INIT POOL WITH DECLARED COMPONENTS
    pool.clear()
    pool.load()


def load(use_archive=True):
    # PARSE SCENARIO FILES
    parsing.load(use_archive)
    # REAJUST KEYFRAME (keep last position unless it does not exist anymore..)
    global CURRENT_FRAME
    if CURRENT_FRAME > len(pool.Frames):
        CURRENT_FRAME = 0

def reload():
    stop()
    init()
    load(False)
    start()


def start():
    global MODULES_FSM
    log.log('raw', 'Cards available: {0}'.format(pool.Cartes))

    if settings["uName"] in pool.Cartes.keys():
        start_modules()
        start_scene()
    else:
        log.warning("== NO SCENARIO FOR: {0}".format(settings["uName"]))


def stop():
    stop_scene()
    stop_modules()


def start_scene():
    if CURRENT_FRAME < len(pool.Frames):
        name = pool.Frames[CURRENT_FRAME]
        if name in pool.Scenes.keys():
            scene = pool.Scenes[name]
            log.log('important', '= SCENE '+name)
            tools.log_teleco(("start scene",name),"scenario")
            if settings["uName"] in scene.cartes.keys():
                stop_scene()
                for etape in scene.cartes[settings["uName"]]:
                    fsm = classes.ScenarioFSM(etape.uid)
                    fsm.start(etape)
                    SCENE_FSM.append(fsm)
            else:
                log.debug('Nothing to do on Scene {0} for card {1}'.format(name, settings["uName"]))
        else:
            log.warning('No Scene found for KeyFrame {0} with name {1}'.format(CURRENT_FRAME, name))
    else:
        log.warning('KeyFrame {0} request doesn\'t exist'.format(CURRENT_FRAME))


def stop_scene():
    for sfsm in SCENE_FSM:
        sfsm.stop()
        SCENE_FSM.remove(sfsm)


def start_modules():
    log.log("raw", "Start device modules")
    for name, etape in pool.Cartes[settings["uName"]].device.modules.items():
        dfsm = classes.ScenarioFSM(name)
        dfsm.start(etape)
        MODULES_FSM.append(dfsm)
        log.info("= MODULE (Scenario) :: "+name)


def stop_modules():
    for dfsm in MODULES_FSM:
        dfsm.stop()
        dfsm.join()