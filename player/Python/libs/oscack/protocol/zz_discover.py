# -*- coding: utf-8 -*-
#
#
# This file is a Finite State Machine for the discover and rtp protocol (which are linked)
#

import random
import os
from collections import deque

from src.threads import network_scheduler
import libs.oscack
from libs import subprocess32
from src import fsm
from libs.oscack import message, network

from libc import rtplib
from src.setting import settings
from src.log import init_log

log = init_log("discov", log_lvl="raw", log_type="Null")

machine = fsm.FiniteStateMachine()

msg_iamhere = network.UnifiedMessageInterpretation("/iamhere", values=(
    ('s', "uName"),
    ('i', "timetag")
))
msg_asktime = network.UnifiedMessageInterpretation("/rtp/asktime", ACK=True)
msg_ping = network.UnifiedMessageInterpretation("/rtp/ping", ACK=True, values=(
    ("i", "ping_1"),
    ("i", "ping_2"),
    ("i", "ping_3"),
    ("i", "ping_4"),
    ("i", "ping_5")
))
msg_pong = network.UnifiedMessageInterpretation("/rtp/pong", ACK=True, values=(
    ("i", "pong_1"),
    ("i", "pong_2"),
    ("i", "pong_3"),
    ("i", "pong_4"),
    ("i", "pong_5")
))
msg_sync = network.UnifiedMessageInterpretation("/rtp/sync", ACK=True, values=(
    ('i', "time_s"),
    ('i', "time_ns"),
    ('i', "dt"),
    ('i', "accuracy"),
    ('i', "timetag")
))
# msg_fail = network.UnifiedMessageInterpretation("/rtp/fail", ACK=True)  # TODO : useless, check before delete


def init_protocol(flag):
    # DESACTIVATE NTP TO FORCE TIME #
    log.debug("*DESACTIVATE NTP TO FORCE TIME*")
    log.debug("  `-> timedatectl set-ntp false")
   # os.system("timedatectl set-ntp false")
    subprocess32.Popen( shlex.split("timedatectl set-ntp false") )
    #


def _pass(*args, **kwargs):
    pass


def send_iamhere(flag):
    message.send(OSC.BroadcastAddress, msg_iamhere.get(uName=settings["uName"],
                                                       timetag=OSC.timetag))


def send_iamhere_to(flag):
    message.send(message.Address(flag.args["src"].get_hostname()),
                 msg_iamhere.get(uName=settings["uName"],
                                 timetag=OSC.timetag))


def add_flag_send_iamhere():
    log.debug('Send IAMHERE')
    machine.append_flag(flag_timeout_send_iamhere.get(JTL=None))
    network_scheduler.enter(settings.get("OSC", "iamhere_interval"),
                            add_flag_send_iamhere)


def addhere(flag):
    # globalContext.network_MAP[flag.args["kwargs"]["uName"]] = network.networkElement(flag.args["kwargs"]["uName"],
    # flag.args["src"].get_hostname()) TODO : check and remove
    OSC.DNCserver.networkmap[flag.args["kwargs"]["uName"]] = OSC.network.NetworkElement(flag.args["kwargs"]["uName"],
                                                                                        flag.args["src"].get_hostname())


def trans_recv_iamhere(flag):
    if flag.args["kwargs"]["uName"] == settings["uName"]:
        return None
    elif flag.args["kwargs"][
        "uName"] not in OSC.DNCserver.networkmap.keys():  # globalContext.network_MAP.keys(): TODO check and remove
        return step_addhere
    else:
        return trans_sync_here


def trans_sync_here(flag):
    if flag.args["kwargs"]["timetag"] > OSC.timetag:
        return step_asktime
    elif flag.args["kwargs"]["timetag"] < OSC.timetag:
        return step_send_iamhere_to
    else:
        return step_main_wait


def send_asktime(flag):
    message.send(message.Address(flag.args["src"].get_hostname()), msg_asktime.get())
    network_scheduler.enter(settings.get("rtp", "timeout"), machine.append_flag,
                            flag_timeout_wait_sync.get(
                                TTL=settings.get("rtp", "timeout") * 1.5, JTL=3))


def sync_time(flag):
    # BEGIN # TIME CRITICAL
    r = rtplib.set_time(*rtplib.add_time(flag.args["kwargs"]["time_s"], flag.args["kwargs"]["time_ns"],
                                         flag.args["kwargs"]["dt"] / 1000000000))
    # END # TIME CRITICAL
    if r != 0:
        log.error("Can't set time system, error code {err}".format(err=r))
    else:
        log.info("Set time system to {sec}.{nsec}".format(sec=flag.args["kwargs"]["time_s"],
                                                          nsec=flag.args["kwargs"]["time_ns"] + flag.args["kwargs"][
                                                              "dt"]))
        log.info("  `-> delta time : {dt} ns, accuracy : {acc} ns".format(dt=flag.args["kwargs"]["dt"],
                                                                          acc=flag.args["kwargs"]["accuracy"]))
        OSC.timetag = flag.args["kwargs"]["timetag"]
        OSC.accuracy = flag.args["kwargs"]["accuracy"]


# TODO : check and remove
# def wait_or_timeout(flag):
# globalContext.scheduler.protocol.enter(10, machine.append_flag, flag_timeout_wait_sync.get(TTL=15, JTL=1))


# def send_failsync(flag):
# message.send(message.Address(flag.args["src"].get_hostname()), msg_fail.get())


def start_send_sync(flag):
    machine.vars["ping_time"] = None
    machine.vars["dt_stack"] = deque(maxlen=settings.get("rtp", "stack_length"))
    machine.vars["reach_acc"] = settings.get("rtp", "accuracy_start_ns")
    network_scheduler.enter(settings.get("rtp", "timeout"), machine.append_flag,
                            flag_timeout_task_sync.get(
                                TTL=settings.get("rtp", "timeout") * 1.5, JTL=4))


kwargs_ping = dict(ping_1=random.randint(-2048, 2048), ping_2=random.randint(-2048, 2048),
                   ping_3=random.randint(-2048, 2048), ping_4=random.randint(-2048, 2048),
                   ping_5=random.randint(-2048, 2048))


def send_ping(flag):
    target = message.Address(flag.args["src"].get_hostname())
    msg = msg_ping.get(**kwargs_ping)
    # BEGIN # Critical time
    machine.vars["ping_time"] = rtplib.get_time()
    message.send(target, msg)
    # END # Critical time


def recv_pong(flag):
    # BEGIN # Time critical
    recv_t = rtplib.get_time()
    # END # Time critical
    _dt = int(((recv_t[0] - machine.vars["ping_time"][0]) * 1000000000 + recv_t[1] - machine.vars["ping_time"][1]) / 2)
    machine.vars["dt_stack"].append(_dt)
    if len(machine.vars["dt_stack"]) < 3:
        log.log("raw", "dt stack too small, skip accuracy")
        return
    sync, dt, acc = rtplib.accuracy_dt(machine.vars["reach_acc"], tuple(machine.vars["dt_stack"]))
    log.log("raw", "Pong : dt : {0}, ~dt {1}, acc {2} ".format(_dt, dt, acc))
    if acc > machine.vars["reach_acc"]:
        log.log("raw", "Accuracy too high ({0}>{1}) ".format(acc, machine.vars["reach_acc"]))
        machine.vars["reach_acc"] = int(machine.vars["reach_acc"] * settings.get("rtp", "accuracy_factor"))
        if machine.vars["reach_acc"] > settings.get("rtp", "accuracy_max_ns"):
            log.log("debug", "Reach accuracy is too bad (less than the limit : {0}), stop trying to sync time !".format(
                settings.get("rtp", "accuracy_max_ns")))
        else:
            log.log("raw", "Reach acc set to {0}".format(machine.vars["reach_acc"]))
    else:
        log.log("debug",
                "FOND DELTA TIME : Dt = {0}, Acc = {1}, with {2} reach acc".format(dt, acc, machine.vars["reach_acc"]))
        flag.args["sync"] = True
        flag.args["sync_dt"] = dt
        flag.args["sync_acc"] = acc


def send_sync(flag):
    kwargs = dict(time_s=0, time_ns=0, dt=flag.args["sync_dt"], accuracy=flag.args["sync_acc"],
                  timetag=OSC.timetag)
    # BEGIN # Time critical
    kwargs["time_s"], kwargs["time_ns"] = rtplib.get_time()
    return message.send(message.Address(flag.args["src"].get_hostname()), msg_sync.get(**kwargs))
    # END # Time critical


def trans_does_sync(flag):
    if "sync" in flag.args:
        log.log("raw", "trans_does_sync flag args :  {0}".format(flag.args))
        if flag.args["sync"]:
            return step_send_sync
    return step_send_ping


flag_timeout_send_iamhere = fsm.Flag("TIMEOUT_SEND_IAMHERE")
flag_timeout_wait_sync = fsm.Flag("TIMEOUT_WAIT_SYNC")
flag_timeout_task_sync = fsm.Flag("TIMEOUT_TASK_SYNC")

step_init = fsm.State("PROTOCOL_INIT", function=init_protocol)
step_main_wait = fsm.State("PROTOCOL_MAIN_WAIT", function=_pass)
step_send_iamhere = fsm.State("PROTOCOL_SEND_NEWHERE", function=send_iamhere)
step_send_iamhere_to = fsm.State("PROTOCOL_SEND_NEWHERE_TO", function=send_iamhere_to)
step_addhere = fsm.State("PROTOCOL_ADD_HERE", function=addhere)
step_asktime = fsm.State("PROTOCOL_SEND_ASKTIME", function=send_asktime)
step_wait_ping = fsm.State("PROTOCOL_WAIT_PING", function=_pass)
step_wait_pong = fsm.State("PROTOCOL_WAIT_PONG", function=_pass)
# step_send_failsync = fsm.State("PROTOCOL_SEND_FAILSYNC", function=send_failsync)
step_sync_start = fsm.State("PROTOCOL_SYNC_START", function=start_send_sync)
step_sync_time = fsm.State("PROTOCOL_SYNC_TIME", function=sync_time)
step_recv_pong = fsm.State("PROTOCOL_RECV_PONG", function=recv_pong)
step_send_sync = fsm.State("PROTOCOL_SEND_SYNC", function=send_sync)
step_send_ping = fsm.State("PROTOCOL_SEND_PING", function=send_ping)
step_send_pong = message.send_state("PROTOCOL_SEND_PONG", None, msg_pong, kwargs={
    "pong_1": random.randint(-2048, 2048),
    "pong_2": random.randint(-2048, 2048),
    "pong_3": random.randint(-2048, 2048),
    "pong_4": random.randint(-2048, 2048),
    "pong_5": random.randint(-2048, 2048),
})

step_init.transitions = {
    None: step_main_wait
}

step_main_wait.transitions = {
    flag_timeout_send_iamhere.uid: step_send_iamhere,
    fsm.Flag("RECV_MSG").uid: network.UnifiedMessageInterpretation.conditional_transition({
        "/iamhere": trans_recv_iamhere,
        "/rtp/asktime": step_sync_start,
        "/rtp/sync": step_sync_time,  # TODO : It's for secure purpose, check if it's really needed
    })
}
step_send_iamhere.transitions = {
    None: step_main_wait
}
step_send_iamhere_to.transitions = {
    None: step_main_wait
}
step_addhere.transitions = {
    True: trans_sync_here
}
step_asktime.transitions = {
    True: step_wait_ping
}
step_wait_ping.transitions = {
    "TIMEOUT_WAIT_SYNC": step_main_wait,
    # "ACK_ERROR": step_send_failsync,  # TODO ack error management OR REMOVE !
    "RECV_MSG": network.UnifiedMessageInterpretation.conditional_transition({
        "/rtp/sync": step_sync_time,
        "/rtp/ping": step_send_pong,
    })
}
# step_send_failsync.transitions = {
#     None: step_main_wait
# }
step_sync_time.transitions = {
    None: step_main_wait
}
step_sync_start.transitions = {
    True: step_send_ping
}
step_wait_pong.transitions = {
    "TIMEOUT_TASK_SYNC": step_main_wait,
    # "ACK_ERROR": step_send_failsync,  # TODO ack error management OR REMOVE !
    "RECV_MSG": network.UnifiedMessageInterpretation.conditional_transition({
        "/rtp/pong": step_recv_pong,
    })
}
step_send_sync.transitions = {
    None: step_main_wait
}
step_send_ping.transitions = {
    True: step_wait_pong
}
step_send_pong.transitions = {
    True: step_wait_ping
}
step_recv_pong.transitions = {
    True: trans_does_sync
}
