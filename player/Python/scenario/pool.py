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

    load_declared()


def load_declared():
    import functions
    import modules
    import intercom
    from scenario import DECLARED_ETAPES, DECLARED_FUNCTIONS, DECLARED_SIGNALS, DECLARED_PATCHER, DECLARED_TRANSITION, DECLARED_OSCROUTES, DECLARED_PUBLICBOXES
    from scenario.classes import Patch, Etape
    from engine.fsm import Flag
    global Etapes_and_Functions, Signals, Scenes, Frames, Devices, Cartes, Patchs, Medias, cross_ref
    global MANAGER, CURRENT_FRAME, CURRENT_SCENE, FSM, DEVICE_FSM, GLOBALS

    # ..
    # Import declared elements to Poll
    Etapes_and_Functions.update(DECLARED_FUNCTIONS)

    #..
    # Import declared OSC routes in one common patcher
    if len(DECLARED_OSCROUTES.keys()) > 0:
        fn_sgn_patcher = Etapes_and_Functions["MSG_SIGNAL_PATCHER"]
        oscroutes_patch = dict()
        for path, route in DECLARED_OSCROUTES.items():
            oscroutes_patch[path] = route
        DECLARED_PATCHER["DECLARED_OSCROUTES"] = Patch("DECLARED_OSCROUTES", "RECV_MSG", (fn_sgn_patcher, oscroutes_patch))
        #..
        # Create Etape Senders for OSCROUTES
        fn_sgn_sender = Etapes_and_Functions["ADD_SIGNAL"]
        fn_auto_transit = Etapes_and_Functions["TRANSIT_AUTO"]
        fn_auto_transit_clean = Etapes_and_Functions["TRANSIT_CLEAN"]
        for path, route in DECLARED_OSCROUTES.items():
            etape_sender = Etape('SEND_'+route['signal'], actions=[(fn_sgn_sender, {'signal':route['signal']}),
                                                                   (fn_auto_transit, {})],
                                                          out_actions= ((fn_auto_transit_clean, {}),)
                                                        )
            DECLARED_ETAPES[etape_sender.uid] = etape_sender

    # ..
    # Import Public Boxes as Etapes
    for name, box in DECLARED_PUBLICBOXES.items():
        etape_public = Etape(name, actions=[ (box['function'], {}) ] )
        DECLARED_ETAPES[etape_public.uid] = etape_public

    #..
    # Import declared Patches
    Patchs.update(DECLARED_PATCHER)


    # ..
    # Attach declared Transition to declared Etapes and create corresponding signals
    for etape_uid, transition in DECLARED_TRANSITION.items():
        for signal_uid, goto_uid in transition.items():
            # If origine Etape exist
            if etape_uid in DECLARED_ETAPES:
                # Prevent Etape looping on himself with non blocking transition
                if (signal_uid is None or signal_uid is True) and etape_uid == goto_uid:
                    log.warning("Circular non blocking transition forbidden !")
                else:
                    # If valid signal, add it to the declared stack
                    if signal_uid is not None:
                        DECLARED_SIGNALS[signal_uid] = Flag(signal_uid, JTL=None)
                    # If goto is a valid Etape
                    if goto_uid in DECLARED_ETAPES:
                        DECLARED_ETAPES[etape_uid].transitions[signal_uid] = DECLARED_ETAPES[goto_uid]
                    # Or If goto is a valid Function
                    elif goto_uid in DECLARED_FUNCTIONS:
                        DECLARED_ETAPES[etape_uid].transitions[signal_uid] = DECLARED_FUNCTIONS[goto_uid]
                    else:
                        log.warning("Etape {0}: No destination {1} for declared transition".format(etape_uid, goto_uid))
            else:
                log.warning("Can't find Etape {0} to attach a declared transition".format(etape_uid))


    # ..
    # Import declared Etapes to Poll
    Etapes_and_Functions.update(DECLARED_ETAPES)
    #
    # Import declared Signals
    Signals.update(DECLARED_SIGNALS)


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
