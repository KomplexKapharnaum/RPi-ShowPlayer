# -*- coding: utf-8 -*-
#
#
# This module provide a simple sync protocol
# It's sync only scenario
#

import os

from libs.oscack import message, network, DNCserver #, BroadcastAddress
from engine.threads import network_scheduler, patcher

from engine import media
from engine import fsm
from engine.setting import settings
from engine.log import init_log

# import libs

BroadcastAddress = None # libs.oscack.BroadcastAddress


log = init_log("ssync")

OSC_PATH_SCENARIO_VERSION = "/sync/scenario/version"
OSC_PATH_SCENARIO_ASK = "/sync/scenario/amiuptodate"

msg_PATH_SCENARIO_VERSION = network.UnifiedMessageInterpretation(OSC_PATH_SCENARIO_VERSION, values=None)
msg_PATH_SCENARIO_ASK = network.UnifiedMessageInterpretation(OSC_PATH_SCENARIO_ASK, values=None)

machine = fsm.FiniteStateMachine(name="syncscenario")

flag_timeout = fsm.Flag("TIMEOUT_SEND_VERSION")


def init_scenprotocol(flag):
    """
    This function init the sync by asking if you are uptodate
    :param flag:
    :return:
    """
    from libs.oscack import BroadcastAddress as _bc
    from libs.oscack import DNCserver as _ds
    global BroadcastAddress, DNCserver
    BroadcastAddress = _bc
    DNCserver = _ds
    log.log("debug", "Start scenario sync protocol machine")
    groups = media.get_scenario_by_group_in_fs()
    log.log("raw", "Parsed fs groups {0}".format(groups))
    if settings.get("current_timeline") in groups.keys():
        current_newer_timeline = media.get_newer_scenario(groups[settings.get("current_timeline")])
        log.log("debug", "Current timeline : {0}".format(current_newer_timeline))
        message.send(BroadcastAddress, message.Message(OSC_PATH_SCENARIO_ASK,
                                                                        ('s', current_newer_timeline.group),
                                                                        ('s', current_newer_timeline.date)))
    else:
        log.log("warning",
                "Searching for {0} timeline but not found on filesystem".format(settings.get("current_timeline")))
        current_newer_timeline = None
    add_timeout_flag()


def add_timeout_flag():
    machine.append_flag(flag_timeout.get(JTL=None))
    network_scheduler.enter(settings.get("sync", "scenario_sync_timeout"), add_timeout_flag)


def _pass(*args, **kwargs):
    pass


def send_version(flag):
    """
    This function send the list of scenario version ordered by group
    :param flag:
    :return:
    """
    args = list()
    groups = media.get_scenario_by_group_in_fs()
    for groupname, group in groups.items():
        group.sort(key=lambda r: r.dateobj, reverse=True)
        for scenario in group[:settings.get("sync", "max_scenario_sync")]:   # In order to avoid 100000 sync files
            args.append(('s', groupname))
            args.append(('s', scenario.date))
    log.log("raw", "Send timeline versions : {0}".format(args))
    message.send(BroadcastAddress, message.Message(OSC_PATH_SCENARIO_VERSION, *args, ACK=False))


def trans_must_i_get_scenario(flag):
    """
    This function is a transition which check if there is scenario to get into the request
    :param flag: Flag
    :return:
    """
    log.log("raw", "Transition..")
    if flag.args["path"] != OSC_PATH_SCENARIO_VERSION or \
                    flag.args["src"].get_hostname() == DNCserver.net_elem._ip:
        log.log("raw", "Not a scenario/version msg")
        if flag.args["path"] == OSC_PATH_SCENARIO_ASK:  # We ask if someone is newer than me
            log.log("raw", "It's a newer asking {0}@{1}".format(flag.args["args"][0], flag.args["args"][1]))
            local_scenario = media.get_scenario_by_group_in_fs()
            newer = media.get_newer_scenario(local_scenario[flag.args["args"][0]])
            if flag.args["args"][0] in local_scenario.keys():  # If we have this scenario group
                if media.ScenarioFile.create_by_OSC(flag.args["args"][0],
                                                    flag.args["args"][1]).dateobj < newer.dateobj:  # He is old
                    log.log("raw", "He is older than us")
                    log.log("raw", "His : {0}, us {1}".format(
                        media.ScenarioFile.create_by_OSC(flag.args["args"][0], flag.args["args"][1]), newer))
                    message.send(flag.args["src"], message.Message(OSC_PATH_SCENARIO_VERSION,
                                                                                 ('s', flag.args["args"][0]),
                                                                                 ('s', newer.date)))
                    # We send our newer version of scenario
        return None  # Not a distant OSC version message
    log.log("raw", ".. It's a OSC_PATH_SCENARIO_VERSION ")
    if "scenario" not in flag.args.keys():  # We just recv the OSC msg
        log.log("raw", "First iter on loop get_scenario")
        flag.args["scenario"] = media.get_scenario_by_group_in_osc(flag.args["args"])
        flag.args["local_scenario"] = media.get_scenario_by_group_in_fs()
        if settings.get("current_timeline") in flag.args["local_scenario"].keys():
            flag.args["local_newer"] = media.get_newer_scenario(
                flag.args["local_scenario"][settings.get("current_timeline")])
        else:
            flag.args["local_newer"] = None
    for groupname, group in flag.args["scenario"].items():
        log.log("raw", "For loop groupname {0} , group {1} ".format(groupname, group))
        new_group = False
        if groupname not in flag.args["local_scenario"]:
            new_group = True
            os.mkdir(os.path.join(settings.get("path", "scenario"), groupname))
        while len(group) > 0:
            scenario = group.pop()
            if new_group or scenario not in flag.args["local_scenario"][groupname]:  # It's newer # TODO waring
                log.log("raw", "It's newer : {0} ".format(scenario))
                flag.args["to_get"] = scenario
                return step_get_scenario
    if "reload" in flag.args.keys():
        log.log("debug", "There is a new timeline to reload : Emit signal ")
        patcher.patch(fsm.Flag("FS_TIMELINE_UPDATED").get())   # Emit signal to warn somewhere there is new T.L.
    return step_main_wait  # End treatment


def get_scenario(flag):
    """
    This function copy a scenario from a distant client into the fs
    :param flag:
    :return:
    """
    to_get = flag.args["to_get"]
    log.log("debug", "Try to get wia scp : {0}".format(to_get))
    to_get.get_from_distant(flag.args["src"].get_hostname())
    if flag.args["local_newer"] is not None:
        log.log("raw", "Check is distant group : {0} is same as us {1}".format(to_get.group, flag.args["local_newer"].group))
        log.log("raw", "Flag args keys : {0}".format(flag.args.keys()))
        if "reload" not in flag.args.keys() and flag.args["local_newer"].group == to_get.group:
            log.log("raw", "{0} is same group as us".format(to_get))
            if to_get.dateobj > flag.args["local_newer"].dateobj:
                log.log("debug", "{0} is a newer version of our group, we should update".format(to_get))
                flag.args["reload"] = True

step_init = fsm.State("SYNC_SCENARIO_INIT", function=init_scenprotocol)
step_main_wait = fsm.State("SYNC_SCENARIO_MAIN_WAIT", function=_pass)
step_send_version = fsm.State("SYNC_SCENARIO_SEND_VERSION", function=send_version)
step_get_scenario = fsm.State("SYNC_GET_SCENARIO", function=get_scenario)

step_init.transitions = {
    None: step_main_wait
}

step_main_wait.transitions = {
    "RECV_MSG": trans_must_i_get_scenario,
    flag_timeout.uid: step_send_version
}

step_get_scenario.transitions = {
    True: trans_must_i_get_scenario
}

step_send_version.transitions = {
    None: step_main_wait
}

