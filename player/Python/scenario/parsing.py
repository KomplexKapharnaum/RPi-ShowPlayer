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
#from libc import simplejson as json
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
    return True


def parse_media(jobj):
    m = classes.Media(jobj["ID"], os.path.join(settings.get("path", "media"), jobj["PATH"]), jobj["CHECKSUM"])
    pool.Medias[jobj["ID"]] = m
    return m


def clear_scenario():
    pool.init()
    scenario.init_declared_objects()


def parse_customlibrary(path):
    jobject = parse_file(path)
    for fn in jobject:
        importFn = {
            "ID" : fn['category']+'_'+fn['name']+'_USERFUNC',
            "CODE" : [
                "def fnct(flag, **kwargs):",
                    "    log.info('WAITING')"]
        }
        parse_function(importFn)

        # {  
        #     "name":"WAIT",
        #     "category":"GENERAL",
        #     "dispos":false,
        #     "medias":false,
        #     "arguments":[  
        #        "",
        #        "",
        #        ""
        #     ],
        #     "code":"print \"WAITING\""
        #  }


def parse_customscenario(path):
    jobject = parse_file(path)
    importEtapes = {}
    for box in jobject['boxes']:
        etapename = box['category']+'_'+box['name']
        
        # Prebuild Etape "SEND SIGNAL"
        if 'SEND_'+etapename in pool.Etapes_and_Functions.keys():
            etape = pool.Etapes_and_Functions['SEND_'+etapename].get()
            etape.uid = box['boxname'].upper()
            if 'allArgs' in box:
                etape.actions[0][1]["args"] = box['allArgs']
            importEtapes[box['boxname']] = etape
        
        # Parsed function from JSON
        elif etapename+'_USERFUNC' in pool.Etapes_and_Functions.keys():
            fn = pool.Etapes_and_Functions[box['category']+'_'+box['name']+'_USERFUNC']
            etape = classes.Etape(box['boxname'].upper(), actions=((fn, {'args':None}),))
            importEtapes[box['boxname']] = etape
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
        fromBox = con['SourceId'].split('_')[1]
        toBox = con['TargetId']
        if fromBox in importEtapes.keys():
            if toBox in importEtapes.keys():
                importEtapes[fromBox].transitions[con['connectionId']] = importEtapes[toBox]

    for etape in importEtapes.values():
        pool.Etapes_and_Functions[etape.uid] = etape

    # dumpclean(pool.Etapes_and_Functions)
    #log.debug('Etape Exist '+'SEND_'+etapename)

        # importEtape = {
        #     "ID" : box.name,
        #     "ACTIONS" : [{
        #             "function": "FNCT_SAY",
        #             "text": "ENTER INIT !"
        #                 }],
        #     "OUT_ACTIONS" : [{
        #             "function": "FNCT_SAY",
        #             "text": "QUIT INIT !"
        #                 }],
        #     "TRANSITIONS" : [
        #         {
        #             "signal" : "..",
        #             "goto" : "CONTROL_PLAYER"
        #         }
        #                     ]
        # }
        # parse_signal(importEtape)



        # ETAPE:
        # {
        #     "ID" : "INIT_SCENE_1",
        #     "ACTIONS" : [{
        #             "function": "FNCT_SAY",
        #             "text": "ENTER INIT !"
        #                 }],
        #     "OUT_ACTIONS" : [{
        #             "function": "FNCT_SAY",
        #             "text": "QUIT INIT !"
        #                 }],
        #     "TRANSITIONS" : [
        #         {
        #             "signal" : "..",
        #             "goto" : "CONTROL_PLAYER"
        #         }
        #                     ]
        # }

        # SIGNAL:
        # {
        #     "ID" : "ONE_FLAG",
        #     "JTL" : 1,
        #     "TTL" : 1,
        #     "IGNORE" : {},
        #     "ARGS" : {}
        # }

        # {  
        #    "boxes":[  
        #       {  
        #          "name":"WAIT",
        #          "boxname":"box1",
        #          "category":"GENERAL",
        #          "positionX":111,
        #          "positionY":154,
        #          "dispoBOO":false,
        #          "arguments":{  
        #             "":null
        #          }
        #       },
        #       {  
        #          "name":"PLAY",
        #          "boxname":"box2",
        #          "category":"AUDIO",
        #          "positionX":388,
        #          "positionY":212,
        #          "dispoBOO":true,
        #          "dispositifs":[  
        #             "Self"
        #          ],
        #          "media":"drums.mp3",
        #          "arguments":{  
        #             "repeat":"1"
        #          }
        #       }
        #    ],
        #    "connections":[  
        #       {  
        #          "connectionId":"CARTE_PUSH_1",
        #          "From":"WAIT",
        #          "To":"PLAY",
        #          "SourceId":"Connector_box1",
        #          "TargetId":"box2"
        #       }
        #    ],
        #    "origins":[  
        #   