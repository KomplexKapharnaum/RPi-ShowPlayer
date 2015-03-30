# -*- coding: utf-8 -*-
#
# This file provide some task accessible from the scenario editor
#

import os
import shlex
from libs import subprocess32

CREATE_NEW_PROCESS_GROUP = 512

import libs.oscack
from libs.oscack import message
import scenario
from engine.setting import settings
from engine.threads import scenario_scheduler, patcher
from scenario import pool
from engine.log import init_log

log = init_log("tools")


class decalrefunction(object):
    """
    This is a decorator which declare function in scenario scope
    """

    def __init__(self, public_name=None):
        """
        :param public_name: Name of the function in the scenario scope
        """
        self.public_name = public_name

    def __call__(self, f):
        if self.public_name is None:
            self.public_name = f.__name__
        global DECALRED_FUNCTIONS
        scenario.DECLARED_FUNCTIONS[self.public_name] = f
        return f


@decalrefunction("ADD_TIMER")
def add_timer(*args, **kwargs):
    """
    This function add a timer which wait some time and launch the function whith args
    :param time: Time to wait (in seconds)
    :param task: NAME of the function to call
    :param args: List of args to pass to the function
    :return:
    """
    log.log("raw", "Add timer : {0}, {1}, {2}".format(kwargs["time"], kwargs["task"], kwargs["args"]))
    scenario_scheduler.enter(kwargs["time"], pool.Etapes_and_Functions[kwargs["task"]], kwargs=kwargs["args"])


@decalrefunction("ADD_SIGNAL")
def add_signal(*args, **kwargs):
    """
    This function add a signal in the scenario manager
    :param signal: NAME of the signal to add
    :param args: args to pass to the signal
    :return:
    """
    if "args" not in kwargs.keys():
        kwargs["args"] = list()
    log.log("raw", "Add signal : {0}, {1}".format(kwargs["signal"], kwargs["args"]))
    # for sfsm in pool.FSM:  # TODO : Here we must use the future signal patcher !
    # sfsm.append_flag(pool.Signals[kwargs["signal"]].get(*kwargs["args"]))
    patcher.patch(pool.Signals[kwargs["signal"]].get(*kwargs["args"]))


@decalrefunction("SERVE_SIGNAL")
def serve_signal(*args, **kwargs):
    """
    This function serve directly a signal without patching him
    :param signal: NAME of signal to patch
    :param kwargs: args to pass to the signal
    :return:
    """
    if "args" not in kwargs.keys():
        kwargs["args"] = list()
    log.log("raw", "Serve signal : {0}, {1}".format(kwargs["signal"], kwargs["args"]))
    patcher.serve(pool.Signals[kwargs["signal"]].get(*kwargs["args"]))


@decalrefunction("SEND_OSC_NEIGHBOUR")
def send_osc_neighbour(*args, **kwargs):
    """
    This function send an OSC message to all neighbour (cartes in the same scene)
    :param path: path of the OSC message
    :param kwargs:
    :return:
    """
    path = kwargs["path"]
    del kwargs["path"]
    msg = message.Message(path, **kwargs)
    for carte in pool.CURRENT_SCENE.cartes:
        if carte != settings["uName"]:
            try:
                message.send(libs.oscack.DNCserver.networkmap[carte].target, msg)
            except KeyError:
                log.error("There is no {0} carte in NetworkMap".format(carte))


@decalrefunction("MSG_SIGNAL_PATCHER")
def msg_patcher(*args, **kwargs):
    """
    This function patch a msg if it fit to a path
    :param path: path OSC
    :param signal: NAME of the signal to create
    :return:
    """
    if args[0].args["path"] in kwargs.keys():
        patcher.serve(pool.Signals[kwargs[args[0].args["path"]]].get(args=args[0].args))
    else:
        return False

@decalrefunction("ACTIVE_MSG_SIGNAL_PATCHER")
def active_msg_patcher(*args, **kwargs):
    """
    This function serve signal only if the device is in active mode
    :param args:
    :param kwargs:
    :return:
    """
    if "active" not in pool.GLOBALS.keys():
        pool.GLOBALS["active"] = True
    if "/signal/active/" in args[0].args["path"]:
        if args[0].args["args"][0] != settings["uName"]:
            return False
    if args[0].args["path"] == "/signal/active/on":
        pool.GLOBALS["active"] = True
        return False
    elif args[0].args["path"] == "/signal/active/off":
        pool.GLOBALS["active"] = False
        return False
    if not pool.GLOBALS["active"]:
        return False
    else:
        msg_patcher(*args, **kwargs)


@decalrefunction("REBOOT_MANAGER")
def reboot_manager(*args, **kwargs):
    """
    This function called the reboot_dnc script
    :param args:
    :param kwargs:
    :return:
    """
    log.log("raw", "reboot_manager..")
    log.log("raw", "Try to reboot manager : "+"{0}\n".format(settings.get("OSC", "classicport")))
    try:
        f = os.open("/tmp/restart", os.O_WRONLY | os.O_NONBLOCK)
        log.log("raw", "Try to write..")
        os.write(f, "{0}\n".format(settings.get("OSC", "classicport")))
        log.log("raw", "Try to close..")
        os.close(f)
    except OSError as e:
        log.error("No restart deamon watching on /tmp/restart fifo")
        log.error(log.show_exception(e))

    # global CREATE_NEW_PROCESS_GROUP
    # cmd = "{script} {classicport} {ackport}".format(
    #     script=os.path.join(settings.get("path", "soft"), "Linux", "Scripts", "reboot_dnc.sh"),
    #     classicport=settings.get("OSC", "classicport"), ackport=settings.get("OSC", "ackport"))
    # arg = shlex.split(cmd)
    # log.log("raw", "rebbot manager cmd (Shell False, Flag NEW_PROCESS_GROUP]: {0}".format(cmd))
    # subprocess32.Popen(arg,
    #                    bufsize=0, executable=None, stdin=None, stdout=None, stderr=None, preexec_fn=os.setsid,
    #                    close_fds=False, shell=False, cwd=None, env=None, universal_newlines=False, startupinfo=None,
    #                    creationflags=0)
