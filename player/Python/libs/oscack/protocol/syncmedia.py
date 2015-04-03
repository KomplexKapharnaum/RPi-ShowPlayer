# -*- coding: utf-8 -*-
#
#
# This file provide a FSM for managing media
#
#


import os
from collections import deque

from src.threads import network_scheduler
from src import fsm
from src import media
from oscack import message, network, BroadcastAddress

from src.setting import settings
from src.log import init_log

log = init_log("symedia")

machine = fsm.FiniteStateMachine()

msg_askmedia = network.UnifiedMessageInterpretation("/media/ask", values=(
    ('i', "checksum")
))

msg_ihave = network.UnifiedMessageInterpretation("/media/ihave", values=(
    ('i', "checksum"),
    ('s', "path")
), ACK=True)


def init_media(flag):
    machine.vars["fs_tree"] = media.parse_media_dir()


def analyse_scenario(flag):
    machine.vars["scenario_medias"] = () #  TODO
    machine.vars["need_intervention"] = []
    for path, checksum in machine.vars["scenario_medias"].items():
        r = media.is_onfs(path, checksum, machine.vars["fs_tree"])
        if r is True:
            continue
        else:
            machine.vars["need_intervention"].append(r)

def main_wait(flag):
    pass


def trans_isitok(flag):
    if len(machine.vars["need_intervention"]) == 0:
        return step_main_wait
    else:
        m = machine.vars["need_intervention"].pop()
        flag.args["to_treat"] = m
        if isinstance(m, (media.MediaUnknown, media.MediaChanged):
            return step_ask_media
        elif isinstance(m, media.MediaMoved):
            if settings.get("media", "automove") == "yes":
                media.do_move_file(m.old_path, m.new_path)
                return trans_isitok(flag)
            else:
                return step_ask_media


def ask_media(flag):
    message.send(BroadcastAddress, msg_askmedia.get(flag.args["to_treat"].checksum))




def init_protocol(flag):
    # DESACTIVATE NTP TO FORCE TIME #
    log.debug("DESACTIVATE NTP TO FORCE TIME")
    log.debug("  `-> timedatectl set-ntp false")
    os.system("timedatectl set-ntp false")
    #
