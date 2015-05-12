# -*- coding: utf-8 -*-
import pool
import classes
import parsing
from engine import log, tools
from engine.setting import settings

log = log.init_log("scenario")

CURRENT_FRAME = 0
CURRENT_SCENE_FRAME = 0  # Represent the current scene frame (could be different from keyframe)

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
    # global MODULES_FSM
    if parsing.IS_THERE_SCENARIO_ERROR:
        log.error("There is an error in the scenario => do not start scenes")
        return
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
    log.debug("Look to a new scene ...")
    if CURRENT_FRAME < len(pool.Frames):
        scene = pool.Frames[CURRENT_FRAME]
        if pool.Cartes[settings.get("uName")] in scene.cartes.keys():
            log.log('important', '= SCENE ' + scene.name)
            tools.log_teleco(("start scene", scene.name), "scenario")
            if settings["uName"] in scene.cartes.keys():  # Fond scene !
                log.debug("Found scene to launch : {0}".format(scene))
                stop_scene()
                global CURRENT_SCENE_FRAME
                CURRENT_SCENE_FRAME = CURRENT_FRAME  # Real scene change
                for etape in scene.start_etapes[settings["uName"]]:
                    for action in etape.actions:
                        if len(action) > 1 and isinstance(action[1], dict) and "args" in action[1].keys() and "dest" in \
                                action[1]["args"].keys() and (
                                    "Self" in action[1]["args"]["dest"] or settings.get("uName") in action[1]["args"]["dest"]):
                            fsm = classes.ScenarioFSM(etape.uid, source=scene.name)
                            fsm.start(etape)
                            SCENE_FSM.append(fsm)
                            break
                        else:
                            log.debug("Ignore etape {0} because it's not for us".format(etape))
            else:
                log.debug('Nothing to do on Scene {0} for card {1}'.format(scene.name, settings["uName"]))
        else:
            log.log("info", "Ignore {0} because there is no scenario active for {1}".format(scene.uid, settings.get("uName")))
            log.log("info", "Current frame {0}, current_frame_scene {1}".format(CURRENT_FRAME, CURRENT_SCENE_FRAME))
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
        log.info("= MODULE (Scenario) :: " + name)


def stop_modules():
    for dfsm in MODULES_FSM:
        dfsm.stop()
        dfsm.join()


def get_group_members():
    """
    This function return all members of the current group
    Two cards are in the same group when :
     * They are in the same SCENE (not frame)
     * They have the same group color
    :return: list of card
    """
    members = list()
    for group in pool.Frames[CURRENT_SCENE_FRAME].groups.values():
        if pool.Cartes[settings.get("uName")] in group:
            for member in group:
                if member not in members:   # Avoid duplication
                    members.append(member)
    return members
