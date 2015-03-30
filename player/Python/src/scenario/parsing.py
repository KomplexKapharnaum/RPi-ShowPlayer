# -*- coding: utf-8 -*-
#
# This file provides tools for parsing JSON objects to real python object
#
#

import os

from src import fsm
from src import scenario
from src.scenario import classes, pool
from src.setting import settings
#from libc import simplejson as json
import simplejson as json

from src.log import init_log
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
    managers = list()
    patchs = list()
    for etape in jobj["MANAGERS"]:
        managers.append(pool.Etapes_and_Functions[etape])
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


def parse_scenario(path):
    pool.init()
    scenario.init_declared_objects()
    jobject = parse_file(path)
    for fnct in jobject["Function"]:
        parse_function(fnct)
    for signal in jobject["Signal"]:
        parse_signal(signal)
    for etape in jobject["Etape"]:
        parse_etape(etape)
    pool.do_cross_ref()  # Resolve cross-references
    for patch in jobject["Patch"]:
        parse_patch(patch)
    for device in jobject["Device"]:
        parse_device(device)
    for carte in jobject["Carte"]:
        parse_carte(carte)
    for scene in jobject["Scene"]:
        parse_scene(scene)
    parse_timeline(jobject["Timeline"])
