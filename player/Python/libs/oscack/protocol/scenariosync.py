# -*- coding: utf-8 -*-
#
#
# This module provide a simple sync protocol
# It's sync only scenario
#

from libs.oscack import message, DNCserver, BroadcastAddress

from engine import media
from engine import fsm
from engine.setting import settings
from engine.log import init_log


log = init_log("ssync")

OSC_PATH_SCENARIO_VERSION = "/sync/scenario/version"
OSC_PATH_SCENARIO_ASK = "/sync/scenario/amiuptodate"

machine = fsm.FiniteStateMachine(name="syncscenario")


def init_scenprotocol(flag):
    """
    This function init the sync by asking if you are uptodate
    :param flag:
    :return:
    """
    log.log("debug", "Start scenario sync protocol machine")
    groups = media.get_scenario_by_group_in_fs()
    current_newer_timeline = media.get_newer_scenario(groups[settings.get("current_timeline")])
    log.log("debug", "Current timeline : {0}".format(current_newer_timeline))
    message.send(BroadcastAddress, message.Message(OSC_PATH_SCENARIO_ASK,
                                                                        ('s', current_newer_timeline.group),
                                                                        ('s', current_newer_timeline.date)))


def _pass():
    pass


def send_version(flag):
    """
    This function send the list of scenario version ordered by group
    :param flag:
    :return:
    """
    args = list()
    groups = media.get_scenario_by_group_in_fs()
    for group in groups:
        i = 0
        for scenario in group:
            if i >= settings.get("sync", "max_scenario_sync"):  # In order to avoid 100000 sync files
                break
            args.append(('s', scenario.group))
            args.append(('s', scenario.date))
            i += 1
    message.send(BroadcastAddress, message.Message(OSC_PATH_SCENARIO_VERSION, *args, ACK=False))


def trans_must_i_get_scenario(flag):
    """
    This function is a transition which check if there is scenario to get into the request
    :param flag: Flag
    :return:
    """
    if flag.args["path"] != OSC_PATH_SCENARIO_VERSION or \
                    flag.args["src"].get_hostname() == DNCserver.net_elem._ip:
        if flag.args["path"] == OSC_PATH_SCENARIO_ASK:  # We ask if someone is newer than me
            local_scenario = media.get_scenario_by_group_in_fs()
            newer = media.get_newer_scenario(local_scenario[flag.args["args"][0]])
            if flag.args["args"][0] in local_scenario.keys():  # If we have this scenario group
                if media.ScenarioFile.create_by_OSC(flag.args["args"][0], flag["args"][1]) < newer:  # He is old
                    message.send(flag.args["src"], message.Message(OSC_PATH_SCENARIO_VERSION,
                                                                                 ('s', flag.args["args"][0]),
                                                                                 ('s', newer.date)))
                    # We send our newer version of scenario
        return False  # Not a distant OSC version message
    if "scenario" not in flag.args.keys():  # We just recv the OSC msg
        log.log("raw", "First iter on loop get_scenario")
        flag.args["scenario"] = media.get_scenario_by_group_in_osc(flag.args["args"])
        flag.args["local_scenario"] = media.get_scenario_by_group_in_fs()
    for groupname, group in flag.args["scenario"].items():
        while len(group) > 0:
            scenario = group.pop()
            if scenario.dateobj > media.get_newer_scenario(flag.args["local_scenario"][groupname]):  # It's newer
                flag.args["to_get"] = scenario
                return step_get_scenario
    return step_main_wait  # End treatment


def get_scenario(flag):
    """
    This function copy a scenario from a distant client into the fs
    :param flag:
    :return:
    """
    to_get = flag.args["to_get"]
    log.log("raw", "Try to get wia scp : {0}".format(to_get))
    to_get.get_from_distant(flag.args["src"].get_hostname())


flag_timeout_send_iamhere = fsm.Flag("TIMEOUT_SEND_VERSION")

step_init = fsm.State("SYNC_SCENARIO_INIT", function=init_scenprotocol)
step_main_wait = fsm.State("SYNC_SCENARIO_MAIN_WAIT", function=_pass)
step_send_version = fsm.State("SYNC_SCENARIO_SEND_VERSION", function=send_version)
step_get_scenario = fsm.State("SYNC_GET_SCENARIO", function=get_scenario)

step_init.transitions = {
    None: step_main_wait
}

step_main_wait.transitions = {
    "RECV_MSG": trans_must_i_get_scenario
}

step_get_scenario.transitions = {
    True: trans_must_i_get_scenario
}

