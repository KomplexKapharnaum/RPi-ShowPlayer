# -*- coding: utf-8 -*-
#
# This file is a file with all objects define in the scenario
#

from src import fsm

Etapes_and_Functions = dict()
Signals = dict()
Scenes = dict()
Frames = list()
Devices = dict()
Cartes = dict()
Patchs = dict()
Medias = dict()
cross_ref = list()

MANAGER = fsm.FiniteStateMachine
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


def do_cross_ref():
    """
    This function write reference for each element in cross ref
    :return:
    """
    global Etapes_and_Functions
    for elem in cross_ref:
        elem[0][elem[1]] = Etapes_and_Functions[elem[2]]