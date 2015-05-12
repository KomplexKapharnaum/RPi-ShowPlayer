# -*- coding: utf-8 -*-
#
# This file provides tools for parsing JSON objects to real python object
#
#

import os
import copy
import string
from os import listdir
from os.path import isfile, join

import engine
from engine import fsm
from scenario import classes, pool
from modules import DECLARED_PUBLICBOXES, MODULES
from scenario.userscope import *
from engine.setting import settings
from operator import itemgetter
import libs.simplejson as json

from engine.log import init_log

log = init_log("parse")

IS_THERE_SCENARIO_ERROR = False

SCENARIO = dict()
TIMELINE = dict()
LIBRARY = dict()


def load(use_archived_scenario=False):
    # UNPACK LAST ARCHIVE OF SCENARIO
    if use_archived_scenario:
        engine.media.load_scenario_from_fs(
            settings["current_timeline"])  # Reload newer tar file of group into active dir
    # LOAD ACTIVE FILES
    load_files()
    for name, timeline in TIMELINE.items():
        parse_devices(timeline)
    for name, library in LIBRARY.items():
        parse_library(library)
    for name, scenario in SCENARIO.items():
        parse_scenario(scenario, name)
    for name, timeline in TIMELINE.items():
        parse_timeline(timeline)


def load_files():
    path = settings.get_path("scenario", "activescenario")
    if not os.path.exists(path):
        log.warning("There is no {0} path for load scenario.. aborting".format(path))
        return False
    try:
        files = [f for f in listdir(path) if isfile(join(path, f))]
        for f in files:
            if f.startswith('scenario_'):
                name = f.replace('scenario_', '').replace('.json', '')
                SCENARIO[name] = parse_file(join(path, f))
                log.log('raw', "Load {0}".format(join(path, f)))
            elif f.startswith('library_'):
                name = f.replace('library_', '').replace('.json', '')
                LIBRARY[name] = parse_file(join(path, f))
                log.log('raw', "Load {0}".format(join(path, f)))
            elif f.startswith('timeline_'):
                name = f.replace('timeline_', '').replace('.json', '')
                TIMELINE[name] = parse_file(join(path, f))
                log.log('raw', "Load {0}".format(join(path, f)))
    except Exception as e:
        log.exception("Error while loading scenario file : ")
        log.exception(log.show_exception(e))
        return


def parse_file(path):
    with open(path, 'r') as fp:
        return json.load(fp, encoding="utf-8")


def parse_arg_function(jfunction):
    fnct = jfunction["function"]
    del jfunction["function"]
    return pool.Etapes_and_Functions[fnct], jfunction


def parse_function(jobj):
    fnct = None
    exec jobj["CODE"]
    pool.Etapes_and_Functions[jobj["ID"]] = fnct  # fnct define in the exec CODE
    return fnct


def etapename(box):
    return box['category'] + '_' + box['name']


def boxname(scenarioname, box):
    return (scenarioname + '_' + box['name'] + '_' + box['boxname']).upper()


# 1: DEVICES
def parse_devices(timeline):
    # DEVICES // CARTES
    for device in timeline['pool']:
        patchs = list()
        # for patch in importDevice["OTHER_PATCH"]:
        # patchs.append(pool.Patchs[patch])
        modules = dict()
        for m in device['modules']:
            if m in MODULES.keys():
                #log.debug('pool list: {0}'.format(pool.Etapes_and_Functions.keys()))
                modules[m] = MODULES[m]
            else:
                log.warning('Unknown device module: {0}'.format(m))
        pool.Devices[device['name']] = classes.Device(device['name'], patchs, modules)
        pool.Cartes[device['name']] = classes.Carte(device['name'], pool.Devices[device['name']])
        log.log('raw', "ADD CARTE {0}".format(pool.Cartes[device['name']]))


# 2: LIBRARY
# PROCESS LIBRARY OF USERS FUNCTION
def parse_library(libs):
    for fn in libs:
        importFn = {
            "ID": fn['category'] + '_' + fn['name'] + '_USERFUNC',
            "CODE": "def fnct(flag, **kwargs):\n  log.debug('CUSTOM CODE EXECUTED')\n"
        }
        code = string.split(fn['code'], '\n')
        code = [(2 * ' ') + line for line in code]
        code = string.join(code, '\n')
        code = code.replace('\t', '  ')
        importFn["CODE"] += code
        log.log('raw', importFn["CODE"])
        parse_function(importFn)


# 3: SCENARIOS
def parse_scenario(parsepool, name):
    pool._JSONScenario.append(parsepool)
    # GET PARSED SCENARIO FILE
    importEtapes = {}
    if 'boxes' not in parsepool:
        return

    # PROCESS BOXES
    for box in parsepool['boxes']:
        # USE PREBUILD ETAPE "SEND SIGNAL"
        # TODO :: SENDERS ARE PUBLICBOX !!! MERGE WITH PUBLIC BOX
        if 'SEND_' + etapename(box) in pool.Etapes_and_Functions.keys():
            etape = pool.Etapes_and_Functions['SEND_' + etapename(box)].get()
            etape.uid = boxname(name, box)
            if 'allArgs' in box:
                etape.actions[0][1]["args"] = box['allArgs']
            importEtapes[etape.uid] = etape
            log.log('raw', 'ADD PREBUILD SENDER ' + etape.uid)

        # CUSTOM FUNCTION (Declared in Library)
        elif etapename(box) + '_USERFUNC' in pool.Etapes_and_Functions.keys():
            fn = pool.Etapes_and_Functions[etapename(box) + '_USERFUNC']
            etape = classes.Etape(boxname(name, box), actions=((fn, {'args': box['allArgs']}),))
            importEtapes[etape.uid] = etape
            log.log('raw', 'ADD USER FUNC ' + etape.uid)


        # PUBLIC FUNCTION (Declared in Library)
        elif box['name'] + '_PUBLICBOX' in pool.Etapes_and_Functions.keys():
            etape = pool.Etapes_and_Functions[box['name'] + '_PUBLICBOX'].get()
            etape.uid = boxname(name, box)
            if 'allArgs' in box:
                etape.actions[0][1]["args"] = box['allArgs']
            importEtapes[etape.uid] = etape
            log.log('raw', 'ADD PREBUILD BOX ' + etape.uid)

        # NO MATCHING ETAPE..
        else:
            log.log('warning', 'Can\'t create ' + etapename(box))

    for etape in importEtapes.values():
        log.log('raw', 'WITH ARGS {0}'.format(etape.actions[0][1]["args"]))

    # PROCESS CABLES
    for con in parsepool['connections']:
        # SIGNAL
        if con['connectionLabel'] is not None and len(con['connectionLabel']) > 0:
            importSignal = {
                "ID": con['connectionLabel'],
                "JTL": 1,
                "TTL": 1,
                "IGNORE": {},
                "ARGS": {}
            }
            s = fsm.Flag(con['connectionLabel'], importSignal["ARGS"], importSignal["JTL"], importSignal["TTL"])
            if len(importSignal["IGNORE"]) > 0:
                ignore = parse_arg_function(importSignal["IGNORE"])
                s.ignore_cb = ignore[0]
                s.ignore_cb_args = ignore[1]
            pool.Signals[importSignal["ID"]] = s
        else:
            con['connectionLabel'] = None

        # TRANSITIONS
        if 'From' not in con.keys() or 'To' not in con.keys():
            log.warning("Connection {0} missing FROM or TO box".format(con))
            continue
        fromBox = (name+'_'+con['From']+'_'+con['SourceId'].split('_')[1]).upper()
        toBox = (name+'_'+con['To']+'_'+con['TargetId']).upper()
        if fromBox in importEtapes.keys():
            if toBox in importEtapes.keys():
                if con['connectionLabel'] == "DEFAULT":
                    importEtapes[fromBox].transitions[False] = importEtapes[toBox]  # Default transition
                else:
                    importEtapes[fromBox].transitions[con['connectionLabel']] = importEtapes[toBox]

    # ETAPES
    for etape in importEtapes.values():
        pool.Etapes_and_Functions[etape.uid] = etape
        log.log('raw', etape.strtrans())


# 4: TIMELINE
# def _parse_timeline(timeline):
#     Sceno = dict()
#
#     # Group
#     groups = dict()  # By scene(keyframe) # By group name # list dispo
#
#     # SCENE & TIMELINE
#     for scene in timeline['scenes']:
#         groups[scene["name"]] = list()  # List group in the scene
#         # GET SCENE DETAILS
#         startEtapes = dict()
#         for device in timeline['pool']:
#             for block in device["blocks"]:
#                 if 'keyframe' in scene:
#                     if block["keyframe"] == scene.get('keyframe'):  # Match device blocks for this scene only
#                         if device["name"] not in startEtapes:
#                             startEtapes[device["name"]] = list()
#                         for scenario in block['scenarios']:
#                             if scenario in SCENARIO.keys():
#                                 for box in SCENARIO[scenario]['boxes']:
#                                     # DETECT STARTING POINT box
#                                     if box['name'] + '_PUBLICBOX' in DECLARED_PUBLICBOXES and \
#                                             DECLARED_PUBLICBOXES[box['name'] + '_PUBLICBOX']['start']:  #
#                                         etape = boxname(scenario, box)
#                                         if etape in pool.Etapes_and_Functions.keys():
#                                             startEtapes[device['name']].append(pool.Etapes_and_Functions[etape])
#                                         else:
#                                             log.warning('PARSING : Can\'t find box {0}'.format(etape))
#                                     # DETECT WANTED MEDIA
#                                     if 'media' in box.keys():
#                                         pool.Cartes[device['name']].media.append(
#                                             os.path.join(box["category"].lower(), box['media']))
#                 else:
#                     log.log("important", "no keyframe found in timeline")
#                     global IS_THERE_SCENARIO_ERROR
#                     IS_THERE_SCENARIO_ERROR = True
#
#         # IMPORT SCENE
#         pool.Scenes[scene['name']] = classes.Scene(scene['name'], startEtapes, dict())
#
#         # TIMELINE SEQUENCE
#         if 'keyframe' in scene:
#             k = scene['keyframe']
#             while (len(pool.Frames) <= k):
#                 pool.Frames.append(None)
#             pool.Frames[scene['keyframe']] = scene['name']
#         else:
#             log.log("important", "no keyframe found in timeline")
#
#         log.debug("end parsing timeline")
#         _parse_timeline(timeline)
#

#
# class FrameScene:
#     def __init__(self, name):
#         self.name = name
#         self.cartes = dict()
#         self.start_etapes = dict()
#         self.groups = dict()


# 4: TIMELINE
def parse_timeline(timeline):
    """
    This function parse the time line !
    :param timeline:
    :return:
    """
    Scenario = dict()

    # Group
    Groups = list()  # By scene(keyframe) # By group name # list dispo

    # Timeline
    Timeline = list()

    old_scenes = copy.copy(pool.Scenes)
    old_frames = copy.copy(pool.Frames)

    for x in timeline['scenes']:
        Timeline.append(None)

    for frame, scene in enumerate(timeline['scenes']):
        Timeline[scene['keyframe']] = classes.Scene(scene['name'])
        # Timeline.append(classes.Scene(scene['name']))
        for dispo in timeline['pool']:
            # Add card in scene
            Timeline[frame].cartes[dispo['name']] = pool.Cartes[dispo['name']]
            if not len(dispo['blocks']) > frame or not isinstance(dispo['blocks'][frame], dict):
                log.warning("There is no frame {0}({1}) for {2}".format(frame, scene['name'], dispo['name']))
                continue
            # Init group in scene
            if dispo['blocks'][frame]['group'] not in Timeline[frame].groups.keys():
                Timeline[frame].groups[dispo['blocks'][frame]['group']] = list()
            # Add in group
            if dispo['blocks'][frame]['group'] is not None:
                Timeline[frame].groups[dispo['blocks'][frame]['group']].append(pool.Cartes[dispo['name']])
            else:
                log.warning("..There is no frame {0}({1}) for {2}".format(frame, scene['name'], dispo['name']))
                continue
            # Init start_etape for dispo
            if dispo['name'] not in Timeline[frame].start_etapes.keys():
                Timeline[frame].start_etapes[dispo['name']] = list()
            # Search in all scenario launched by the card in the current scene
            for scenario in dispo['blocks'][frame]['scenarios']:
                log.important("Read scenario {0} for {1}".format(scenario, dispo['name']))
                if scenario not in SCENARIO.keys():         # Scenario doesn't exist
                    log.warning("{0} try to add scenario {1} but it doesn't exist".format(dispo['name'], scenario))
                    continue
                for etape in SCENARIO[scenario]['boxes']:   # Search start box in this scenario
                    if etape['name'] == "START" and ('Self' in etape['dispositifs'] or dispo['name'] in etape['dispositifs']):
                        log.important("Found start box : {0} for {1}".format(boxname(scenario, etape), dispo['name']))
                        # This START box is for us => append to start_etapes
                        Timeline[frame].start_etapes[dispo['name']].append(
                            pool.Etapes_and_Functions[boxname(scenario, etape)])
        # End parse scene
        pool.Scenes[scene['name']] = Timeline[frame]
        pool.Frames.append(Timeline[frame]) # scene['name']

        pool._Timeline = Timeline
        pool._JSONtimeline = timeline


    log.info("END NEW PARSING")
