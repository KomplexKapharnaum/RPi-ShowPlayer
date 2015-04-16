# -*- coding: utf-8 -*-
#
#
# This file is a Finite State Machine for the discover and rtp protocol (which are linked)
#

import random
import time
from collections import deque
import Queue
import shlex

from engine.threads import network_scheduler
import libs.oscack
from libs import subprocess32
from engine import fsm
from libs.oscack import message, network

from libs import rtplib
from engine.setting import settings
from engine.log import init_log
from scenario import manager

log = init_log("discov")

machine = fsm.FiniteStateMachine()

msg_iamhere = network.UnifiedMessageInterpretation("/iamhere", values=(
    ('s', "uName"),
    ('i', "timetag")
), flag_name="RECV_IAM_HERE")
msg_asktime = network.UnifiedMessageInterpretation("/rtp/asktime", ACK=True, flag_name="RECV_ASKTIME")
msg_ping = network.UnifiedMessageInterpretation("/rtp/ping", ACK=True, values=(
    ("i", "ping_1"),
    ("i", "ping_2"),
    ("i", "ping_3"),
    ("i", "ping_4"),
    ("i", "ping_5")
), auto_add=False)
msg_pong = network.UnifiedMessageInterpretation("/rtp/pong", ACK=True, values=(
    ("i", "pong_1"),
    ("i", "pong_2"),
    ("i", "pong_3"),
    ("i", "pong_4"),
    ("i", "pong_5")
), auto_add=False)
msg_sync = network.UnifiedMessageInterpretation("/rtp/sync", ACK=True, values=(
    ('i', "time_s"),
    ('i', "time_ns"),
    ('i', "dt"),
    ('i', "accuracy"),
    ('i', "timetag")
), auto_add=False)
# msg_fail = network.UnifiedMessageInterpretation("/rtp/fail", ACK=True)  # TODO : useless, check before delete


def init_protocol(flag):
    # DESACTIVATE NTP TO FORCE TIME #
    log.debug("*DESACTIVATE NTP TO FORCE TIME*")
    #log.debug("  `-> timedatectl set-ntp false")
   # os.system("timedatectl set-ntp false")
    subprocess32.Popen( shlex.split("timedatectl set-ntp false") )


def _pass(*args, **kwargs):
    pass


def add_method_before_patcher(path, types, fnct):
    """
    This function del the scenario wild card before add themself and replug it after
    :param path: OSC path
    :param types: OSC types (None as wildcard)
    :param fnct: callback function
    :return: None
    """
    libs.oscack.DNCserver.del_method(None, None)          # Remove wildcard
    libs.oscack.DNCserver.ackServer.del_method(path, types)         # Remove before add
    libs.oscack.DNCserver.ackServer.add_method(path, types, fnct)   # Add callback
    libs.oscack.DNCserver.add_method(None, None, scenario.manager.patch_msg)  # Replug patcher



def send_iamhere(flag):
    message.send(libs.oscack.BroadcastAddress, msg_iamhere.get(uName=settings["uName"],
                                                       timetag=libs.oscack.timetag))


def send_iamhere_to(flag):
    message.send(message.Address(flag.args["src"].get_hostname()),
                 msg_iamhere.get(uName=settings["uName"],
                                 timetag=libs.oscack.timetag))


def add_flag_send_iamhere():
    machine.append_flag(flag_timeout_send_iamhere.get(JTL=None))
    network_scheduler.enter(settings.get("OSC", "iamhere_interval"),
                            add_flag_send_iamhere)


def addhere(flag):
    # globalContext.network_MAP[flag.args["kwargs"]["uName"]] = network.networkElement(flag.args["kwargs"]["uName"],
    # flag.args["src"].get_hostname()) TODO : check and remove
    libs.oscack.DNCserver.networkmap[flag.args["kwargs"]["uName"]] = libs.oscack.network.NetworkElement(flag.args["kwargs"]["uName"],
                                                                                        flag.args["src"].get_hostname())


def trans_recv_iamhere(flag):
    if flag.args["kwargs"]["uName"] == settings["uName"]:
        return None
    elif flag.args["kwargs"][
        "uName"] not in libs.oscack.DNCserver.networkmap.keys():  # globalContext.network_MAP.keys(): TODO check and remove
        return step_addhere
    else:
        return trans_sync_here


def trans_sync_here(flag):
    if flag.args["kwargs"]["timetag"] > libs.oscack.timetag:
        return step_asktime
    elif flag.args["kwargs"]["timetag"] < libs.oscack.timetag:
        return step_send_iamhere_to
    else:
        return step_main_wait

#
# def send_asktime(flag):
#     message.send(message.Address(flag.args["src"].get_hostname()), msg_asktime.get())
#     network_scheduler.enter(settings.get("rtp", "timeout"), machine.append_flag,
#                             flag_timeout_wait_sync.get(
#                                 TTL=settings.get("rtp", "timeout") * 1.5, JTL=3))


def sync_time(flag):
    # BEGIN # TIME CRITICAL
    r = rtplib.set_time(*rtplib.add_time(flag.args["kwargs"]["time_s"], flag.args["kwargs"]["time_ns"],
                                         flag.args["kwargs"]["dt"] / 1000000000))
    # END # TIME CRITICAL
    if r != 0:
        log.log("error", "Can't set time system, error code {err}".format(err=r))
    else:
        log.log("info", "Set time system to {sec}.{nsec}".format(sec=flag.args["kwargs"]["time_s"],
                                                          nsec=flag.args["kwargs"]["time_ns"] + flag.args["kwargs"][
                                                              "dt"]))
        log.log("info", "  `-> delta time : {dt} ns, accuracy : {acc} ns".format(dt=flag.args["kwargs"]["dt"],
                                                                          acc=flag.args["kwargs"]["accuracy"]))
        libs.oscack.timetag = flag.args["kwargs"]["timetag"]
        libs.oscack.accuracy = flag.args["kwargs"]["accuracy"]
        libs.oscack.sync.set(True)
        log.log("info", "Set oscack.sync.value to true")


def server_sync(flag):
    pong_queue = Queue.Queue()
    reach_acc = settings.get("rtp", "accuracy_start_ns")
    dt_stack = deque(maxlen=settings.get("rtp", "stack_length"))
    target = message.Address(flag.args["src"].get_hostname())
    #msg = msg_ping.get(**kwargs_ping)
    def catch_pong(path, args, types, src):
        pong_queue.put(args)
        message.send(target, msg_ping.get(**kwargs_ping))
    # libs.oscack.DNCserver.ackServer.del_method("/rtp/pong", None)
    # libs.oscack.DNCserver.ackServer.add_method("/rtp/pong", None, catch_pong)
    add_method_before_patcher("/rtp/pong", None, catch_pong)
    network_scheduler.enter(settings.get("rtp", "timeout"), machine.append_flag,
                            flag_timeout_task_sync.get(
                                TTL=settings.get("rtp", "timeout") * 1.5, JTL=4))   # TODO check if work
    machine.current_state.preemptible.set()
    time.sleep(0.5)     # Wait for the client to pass in the correct state
    # BEGIN TIME CRITICAL #
    message.send(target, msg_ping.get(**kwargs_ping))
    t_start = rtplib.get_time()
    # n_try = 0
    while not machine.current_state.stop.is_set():
        try:
            pong = pong_queue.get(True, 5)
        except Queue.Empty as e:
            # n_try += 1
            log.exception(log.show_exception(e))
            # if n_try > 3:
            #     log.critical("Too much try to get pong after timeout ! quit loop => need to be fixed")
            #     break
            # continue
            break
        t_end = rtplib.get_time()
        # END TIME CRITICAL #
        _dt = int(((t_end[0] - t_start[0]) * 1000000000 + t_end[1] - t_start[1]) / 2)
        t_start = t_end
        dt_stack.append(_dt)
        sync, dt, acc = rtplib.accuracy_dt(reach_acc, tuple(dt_stack))
        log.log("raw", "sync {0}, dt {1}, acc {2}".format(sync, dt, acc))
        if sync != 1:
            reach_acc = int(reach_acc * settings.get("rtp", "accuracy_factor"))
        else:
            kwargs = dict(time_s=0, time_ns=0, dt=dt, accuracy=acc,
                  timetag=libs.oscack.timetag)
            # BEGIN # Time critical
            kwargs["time_s"], kwargs["time_ns"] = rtplib.get_time()
            message.send(target, msg_sync.get(**kwargs))
            # END # Time critical
            libs.oscack.sync.set(True)
            log.log("info", "Set oscack.sync.value to true")
            break
    libs.oscack.DNCserver.ackServer.del_method("/rtp/pong", None)
    machine.append_flag(flag_timeout_task_sync.get(TTL=settings.get("OSC", "TTL"), JTL=settings.get("OSC", "JTL")))


def client_sync(flag):
    target = message.Address(flag.args["src"].get_hostname())
    # msg = msg_pong.get(**kwargs_pong)
    def catch_ping(path, args, types, src):
        log.log("error", "catch ping from {0}".format(target))
        # BEGIN # TIME CRITICAL
        message.send(target, msg_pong.get(**kwargs_pong))
        # END # TIME CRITICAL
    # libs.oscack.DNCserver.ackServer.del_method("/rtp/ping", None)
    # libs.oscack.DNCserver.ackServer.add_method("/rtp/ping", None, catch_ping)
    # libs.oscack.DNCserver.ackServer.del_method("/rtp/sync", None)
    # libs.oscack.DNCserver.ackServer.add_method("/rtp/sync", None, client_get_sync)
    add_method_before_patcher("/rtp/ping", None, catch_ping)
    add_method_before_patcher("/rtp/sync", None, client_get_sync)
    network_scheduler.enter(settings.get("rtp", "timeout"), machine.append_flag,
                            flag_timeout_wait_sync.get(
                                TTL=settings.get("rtp", "timeout") * 1.5, JTL=4))
    machine.current_state.preemptible.set()
    log.log("error", "Just before sending asktime")
    message.send(target, msg_asktime.get())
    log.log("error", "Just after sending asktime")


def client_get_sync(path, args, types, src):
    log.log("info", "get sync ! {0}".format(args))
    # BEGIN # TIME CRITICAL
    r = rtplib.set_time(*rtplib.add_time(args[0], args[1],
                                         float(args[2] / 1000000000)))
    # END # TIME CRITICAL
    libs.oscack.DNCserver.ackServer.del_method("/rtp/ping", None)
    libs.oscack.DNCserver.ackServer.del_method("/rtp/sync", None)
    machine.append_flag(flag_get_sync.get())
    if r != 0:
        log.error("Can't set time system, error code {err}".format(err=r))
    else:
        log.info("Set time system to {sec}.{nsec}".format(sec=args[0],
                                                          nsec=args[1] + args[2]))
        log.info("  `-> delta time : {dt} ns, accuracy : {acc} ns".format(dt=args[2],
                                                                          acc=args[3]))
        libs.oscack.timetag = args[4]
        libs.oscack.accuracy = args[3]
        libs.oscack.sync.set(True)
        log.log("info", "Set oscack.sync.value to true")


#
# def start_send_sync(flag):
#     machine.vars["ping_time"] = None
#     machine.vars["dt_stack"] = deque(maxlen=settings.get("rtp", "stack_length"))
#     machine.vars["reach_acc"] = settings.get("rtp", "accuracy_start_ns")
#     network_scheduler.enter(settings.get("rtp", "timeout"), machine.append_flag,
#                             flag_timeout_task_sync.get(
#                                 TTL=settings.get("rtp", "timeout") * 1.5, JTL=4))


kwargs_ping = dict(ping_1=random.randint(-2048, 2048), ping_2=random.randint(-2048, 2048),
                   ping_3=random.randint(-2048, 2048), ping_4=random.randint(-2048, 2048),
                   ping_5=random.randint(-2048, 2048))

kwargs_pong = dict(pong_1=random.randint(-2048, 2048), pong_2=random.randint(-2048, 2048),
                   pong_3=random.randint(-2048, 2048), pong_4=random.randint(-2048, 2048),
                   pong_5=random.randint(-2048, 2048))


# def send_ping(flag):
#     target = message.Address(flag.args["src"].get_hostname())
#     msg = msg_ping.get(**kwargs_ping)
#     # BEGIN # Critical time
#     machine.vars["ping_time"] = rtplib.get_time()
#     message.send(target, msg)
#     # END # Critical time
#
#
# def recv_pong(flag):
#     # BEGIN # Time critical
#     recv_t = rtplib.get_time()
#     # END # Time critical
#     _dt = int(((recv_t[0] - machine.vars["ping_time"][0]) * 1000000000 + recv_t[1] - machine.vars["ping_time"][1]) / 2)
#     machine.vars["dt_stack"].append(_dt)
#     if len(machine.vars["dt_stack"]) < 3:
#         log.log("raw", "dt stack too small, skip accuracy")
#         return
#     sync, dt, acc = rtplib.accuracy_dt(machine.vars["reach_acc"], tuple(machine.vars["dt_stack"]))
#     log.log("raw", "Pong : dt : {0}, ~dt {1}, acc {2} ".format(_dt, dt, acc))
#     if acc > machine.vars["reach_acc"]:
#         log.log("raw", "Accuracy too high ({0}>{1}) ".format(acc, machine.vars["reach_acc"]))
#         machine.vars["reach_acc"] = int(machine.vars["reach_acc"] * settings.get("rtp", "accuracy_factor"))
#         if machine.vars["reach_acc"] > settings.get("rtp", "accuracy_max_ns"):
#             log.log("debug", "Reach accuracy is too bad (less than the limit : {0}), stop trying to sync time !".format(
#                 settings.get("rtp", "accuracy_max_ns")))
#         else:
#             log.log("raw", "Reach acc set to {0}".format(machine.vars["reach_acc"]))
#     else:
#         log.log("debug",
#                 "FOND DELTA TIME : Dt = {0}, Acc = {1}, with {2} reach acc".format(dt, acc, machine.vars["reach_acc"]))
#         flag.args["sync"] = True
#         flag.args["sync_dt"] = dt
#         flag.args["sync_acc"] = acc
#
#
# def send_sync(flag):
#     kwargs = dict(time_s=0, time_ns=0, dt=flag.args["sync_dt"], accuracy=flag.args["sync_acc"],
#                   timetag=oscack.timetag)
#     # BEGIN # Time critical
#     kwargs["time_s"], kwargs["time_ns"] = rtplib.get_time()
#     return message.send(message.Address(flag.args["src"].get_hostname()), msg_sync.get(**kwargs))
#     # END # Time critical

#
# def trans_does_sync(flag):
#     if "sync" in flag.args:
#         log.log("raw", "trans_does_sync flag args :  {0}".format(flag.args))
#         if flag.args["sync"]:
#             return step_send_sync
#     return step_send_ping


flag_timeout_send_iamhere = fsm.Flag("TIMEOUT_SEND_IAMHERE")
flag_timeout_wait_sync = fsm.Flag("TIMEOUT_WAIT_SYNC")
flag_timeout_task_sync = fsm.Flag("TIMEOUT_TASK_SYNC")
flag_get_sync = fsm.Flag("GET_SYNC")

step_init = fsm.State("PROTOCOL_INIT", function=init_protocol)
step_main_wait = fsm.State("PROTOCOL_MAIN_WAIT", function=_pass)
step_send_iamhere = fsm.State("PROTOCOL_SEND_NEWHERE", function=send_iamhere)
step_send_iamhere_to = fsm.State("PROTOCOL_SEND_NEWHERE_TO", function=send_iamhere_to)
step_addhere = fsm.State("PROTOCOL_ADD_HERE", function=addhere)
step_asktime = fsm.State("PROTOCOL_SEND_ASKTIME", function=client_sync)
# step_wait_ping = fsm.State("PROTOCOL_WAIT_PING", function=_pass)
# step_wait_pong = fsm.State("PROTOCOL_WAIT_PONG", function=_pass)
# step_send_failsync = fsm.State("PROTOCOL_SEND_FAILSYNC", function=send_failsync)
step_sync_start = fsm.State("PROTOCOL_SYNC_START", function=server_sync)
step_sync_time = fsm.State("PROTOCOL_SYNC_TIME", function=sync_time)
# step_recv_pong = fsm.State("PROTOCOL_RECV_PONG", function=recv_pong)
# step_send_sync = fsm.State("PROTOCOL_SEND_SYNC", function=send_sync)
# step_send_ping = fsm.State("PROTOCOL_SEND_PING", function=send_ping)
# step_send_pong = message.send_state("PROTOCOL_SEND_PONG", None, msg_pong, kwargs={
#     "pong_1": random.randint(-2048, 2048),
#     "pong_2": random.randint(-2048, 2048),
#     "pong_3": random.randint(-2048, 2048),
#     "pong_4": random.randint(-2048, 2048),
#     "pong_5": random.randint(-2048, 2048),
# })

step_init.transitions = {
    None: step_main_wait
}

step_main_wait.transitions = {
    flag_timeout_send_iamhere.uid: step_send_iamhere,
    # fsm.Flag("RECV_MSG").uid: network.UnifiedMessageInterpretation.conditional_transition({
    #     "/iamhere": trans_recv_iamhere,
    #     "/rtp/asktime": step_sync_start,
    #     "/rtp/sync": step_sync_time,  # TODO : It's for secure purpose, check if it's really needed
    # })
    msg_asktime.flag_name: step_sync_start,
    msg_iamhere.flag_name: trans_recv_iamhere
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
    "TIMEOUT_WAIT_SYNC": step_main_wait,
    "GET_SYNC": step_main_wait
}
# step_wait_ping.transitions = {
#     "TIMEOUT_WAIT_SYNC": step_main_wait,
#     # "ACK_ERROR": step_send_failsync,  # TODO ack error management OR REMOVE !
#     "RECV_MSG": network.UnifiedMessageInterpretation.conditional_transition({
#         "/rtp/sync": step_sync_time,
#         "/rtp/ping": step_send_pong,
#     })
# }
# step_send_failsync.transitions = {
#     None: step_main_wait
# }
step_sync_time.transitions = {
    None: step_main_wait
}
step_sync_start.transitions = {
    "TIMEOUT_TASK_SYNC": step_main_wait
}
# step_wait_pong.transitions = {
#     "TIMEOUT_TASK_SYNC": step_main_wait,
#     # "ACK_ERROR": step_send_failsync,  # TODO ack error management OR REMOVE !
#     "RECV_MSG": network.UnifiedMessageInterpretation.conditional_transition({
#         "/rtp/pong": step_recv_pong,
#     })
# }
# step_send_sync.transitions = {
#     None: step_main_wait
# }
# step_send_ping.transitions = {
#     True: step_wait_pong
# }
# step_send_pong.transitions = {
#     True: step_wait_ping
# }
# step_recv_pong.transitions = {
#     True: trans_does_sync
# }
