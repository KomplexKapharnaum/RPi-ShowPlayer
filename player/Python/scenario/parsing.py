# -*- coding: utf-8 -*-
#
# This file provides tools for parsing JSON objects to real python object
#
#

import os

from engine import fsm
import scenario
from scenario import classes, pool
from engine.setting import settings
from operator import itemgetter
import libs.simplejson as json

from engine.log import init_log, dumpclean
log = init_log("parse")


def parse_file(path):
    with open(path, 'r') as fp:
        return json.load(fp)


def parse_function(jobj):
    fnct = None
    exec "\n".join(jobj["CODE"])
    pool.Etapes_and_Functions[jobj["ID"]] = fnct  # fnct define in the exec CODE
    return fnct


def parse_arg_function(jfunction):
    fnct = jfunction["function"]
    del jfunction["function"]
    return pool.Etapes_and_Functions[fnct], jfunction


def parse_etape(jobj):
    actions = list()
    for elem in jobj["ACTIONS"]:
        actions.append(parse_arg_function(elem))
    out_actions = list()
    for elem in jobj["OUT_ACTIONS"]:
        out_actions.append(parse_arg_function(elem))
    transitions = dict()
    e = classes.Etape(jobj["ID"], actions, out_actions, transitions)
    for elem in jobj["TRANSITIONS"]:
        if elem["signal"] == "None":
                elem["signal"] = None
        if elem["goto"] in pool.Etapes_and_Functions:
            e.transitions[elem["signal"]] = pool.Etapes_and_Functions[elem["goto"]]
        else:  # Need cross ref cause reference isn't already defined
            pool.cross_ref.append((e.transitions, elem["signal"], elem["goto"]))
    pool.Etapes_and_Functions[jobj["ID"]] = e
    return e


def parse_signal(jobj):
    s = fsm.Flag(jobj["ID"], jobj["ARGS"], jobj["JTL"], jobj["TTL"])
    if len(jobj["IGNORE"]) > 0:
        ignore = parse_arg_function(jobj["IGNORE"])
        s.ignore_cb = ignore[0]
        s.ignore_cb_args = ignore[1]
    pool.Signals[jobj["ID"]] = s
    return s


def parse_patch(jobj):
    p = classes.Patch(jobj["ID"], jobj["SIGNAL"], parse_arg_function(jobj["TREATMENT"]))
    pool.Patchs[jobj["ID"]] = p
    return p


def parse_device(jobj):
    managers = dict()
    patchs = list()
    for etape in jobj["MANAGERS"]:
        managers[etape] = pool.Etapes_and_Functions[etape]
    for patch in jobj["OTHER_PATCH"]:
        patchs.append(pool.Patchs[patch])
    d = classes.Device(jobj["ID"], jobj["MODULES"], patchs, managers)  # TODO : End correct parsing !
    pool.Devices[jobj["ID"]] = d
    return d


def parse_carte(jobj):
    c = classes.Carte(jobj["ID"], pool.Devices[jobj["DEVICE"]])
    pool.Cartes[jobj["ID"]] = c
    return c


def parse_scene(jobj):
    cartes = dict()
    for carte in jobj["INIT_ETAPES"]:
        cartes[carte["carte"]] = list()
        for etape in carte["etapes"]:
            cartes[carte["carte"]].append(pool.Etapes_and_Functions[etape])
    s = classes.Scene(jobj["ID"], cartes)
    pool.Scenes[jobj["ID"]] = dict()
    pool.Scenes[jobj["ID"]]["obj"] = s
    return s


def parse_timeline(jobj):
    before = None
    for frame in jobj:
        pool.Frames.append(None)
        for scene in frame:
            if settings["uName"] in scene["cartes"]:
                if before is None:
                    pool.Scenes[scene["scene"]]["before"] = None
                else:
                    pool.Scenes[before]["after"] = pool.Scenes[scene["scene"]]["obj"]
                    pool.Scenes[before]["until"] = len(pool.Frames)-1
                    pool.Scenes[scene["scene"]]["before"] = pool.Scenes[before]["after"]
                pool.Frames[-1] = pool.Scenes[scene["scene"]]["obj"]
                before = scene["scene"]
            else: log.debug('"{0}" not in cards'.format(settings["uName"]))
    return True


def parse_media(jobj):
    m = classes.Media(jobj["ID"], os.path.join(settings.get("path", "media"), jobj["PATH"]), jobj["CHECKSUM"])
    pool.Medias[jobj["ID"]] = m
    return m


def clear_scenario():
    pool.init()
    scenario.init_declared_objects()


def get_scenario(name):
    try:
        path = os.path.join(settings.get("path", "activescenario"),'scenario_'+name+'.json')
        return parse_file(path)
    except:
        log.log('warning', 'SCENARIO '+name+' not found')
        return dict()


def get_timeline(name):
    try:
        path = os.path.join( settings.get("path", "activescenario"), 'timeline_'+name+'.json')
        return parse_file(path)['pool']
    except:
        log.log('warning', 'TIMELINE '+name+' not found')
        return dict()

def get_library(name):
    try: 
        path = os.path.join(settings.get("path", "activescenario"), 'library_'+name+'.json')
        return parse_file(path)
    except:
        log.log('warning', 'LIBRARY '+name+' not found')
        return dict()


def parse_customdevices(name):
    parsepool = get_timeline(name)
    for device in parsepool:
        importDevice = {
            "ID" : device['name'],
            "MODULES" : [],
            "PATCH_IN_NUM" : [],
            "PATCH_OUT_NUM" : [],
            "PATCH_IN_ANA" : [],
            "PATCH_OUT_ANA" : [],
            "MANAGERS" : device['modules'],
            "OTHER_PATCH" : []
        }
        parse_device(importDevice)
        importCarte = {
            "ID" : device['name'],
            "DEVICE" : device['name']
        }
        parse_carte(importCarte)


def parse_customtimeline(name):
    Sceno = dict()
    parsepool = get_timeline(name)
    for device in parsepool:
        for block in device["blocks"]: 
            SC = {
                    "carte": device['name'],
                    "scenarios": block['scenarios'],
                    "etapes": [],
                    "start": block['start'],
                    "end": block['end']
                }
            #FIND START ETAPE FOR EACH ACTIVATED SCENARIO IN THE SCENE
            for scenario in block['scenarios']:
                scenard = get_scenario(scenario)
                for box in scenard['origins']:
                    boxname = (scenario+'_'+box).upper()
                    SC['etapes'].append(boxname)
            # ADD SCENE
            scene_name = block['scene']['name']
            if scene_name not in Sceno.keys():
                Sceno[scene_name] = []
            Sceno[scene_name].append(SC)


    # Import SCENES
    for name, sceneDevices in Sceno.items():
        cartes = dict()
        for carte in sceneDevices:
            cartes[carte["carte"]] = list()
            for etape in carte["etapes"]:
                if etape in pool.Etapes_and_Functions.keys():
                    cartes[carte["carte"]].append(pool.Etapes_and_Functions[etape])
                else:
                    log.warning('CAN\'T FIND {0}'.format(etape))
        s = classes.Scene(name, cartes)
        pool.Scenes[name] = dict()
        pool.Scenes[name]["obj"] = s

    # Import TIMELINE
    importTimeline = []
    for device in parsepool:
        if device['name'] == settings["uName"]:
            for block in device["blocks"]: 
                importTimeline.append({
                    "scene" : block['scene']['name'],
                    "start": block['start'],
                    "end": block['end']
                })
            importTimeline = sorted(importTimeline, key=itemgetter('start'))
            before = None
            for scene in importTimeline:
                pool.Frames.append(None)
                if before is None:
                    pool.Scenes[scene["scene"]]["before"] = None
                else:
                    pool.Scenes[before]["after"] = pool.Scenes[scene["scene"]]["obj"]
                    pool.Scenes[before]["until"] = len(pool.Frames)-1
                    pool.Scenes[scene["scene"]]["before"] = pool.Scenes[before]["after"]
                pool.Frames[-1] = pool.Scenes[scene["scene"]]["obj"]
                before = scene["scene"]


def parse_customlibrary(name):
    libs = get_library(name)
    for fn in libs:
        importFn = {
            "ID" : fn['category']+'_'+fn['name']+'_USERFUNC',
            "CODE" : [
                "def fnct(flag, **kwargs):",
                    "    log.info('WAITING')"]
        }
        parse_function(importFn)


def parse_customscenario(name):
    jobject = get_scenario(name)
    importEtapes = {}
    if 'boxes' not in jobject:
        return
    for box in jobject['boxes']:
        etapename = box['category']+'_'+box['name']
        boxname = (name+'_'+box['boxname']).upper()

        # Prebuild Etape "SEND SIGNAL"
        if 'SEND_'+etapename in pool.Etapes_and_Functions.keys():
            etape = pool.Etapes_and_Functions['SEND_'+etapename].get()
            etape.uid = boxname
            if 'allArgs' in box:
                etape.actions[0][1]["args"] = box['allArgs']
            importEtapes[etape.uid] = etape
            log.log('raw', 'ADD PREBUILD ETAPE '+etape.uid)
        # Parsed function from JSON
        elif etapename+'_USERFUNC' in pool.Etapes_and_Functions.keys():
            fn = pool.Etapes_and_Functions[box['category']+'_'+box['name']+'_USERFUNC']
            etape = classes.Etape(boxname, actions=((fn, {'args': box['allArgs']}),))
            importEtapes[etape.uid] = etape
            log.log('raw', 'ADD USER FUNC '+etape.uid)
        else:
            log.log('warning', 'Can\'t create '+etapename)

    for con in jobject['connections']:
        #Signal
        importSignal = {
            "ID" : con['connectionId'],
            "JTL" : 1,
            "TTL" : 1,
            "IGNORE" : {},
            "ARGS" : {}
        }
        parse_signal(importSignal)

        # Transitions
        fromBox = (name+'_'+con['SourceId'].split('_')[1]).upper()
        toBox = (name+'_'+con['TargetId']).upper()
        if fromBox in importEtapes.keys():
            if toBox in importEtapes.keys():
                importEtapes[fromBox].transitions[con['connectionId']] = importEtapes[toBox]

    for etape in importEtapes.values():
        pool.Etapes_and_Functions[etape.uid] = etape
