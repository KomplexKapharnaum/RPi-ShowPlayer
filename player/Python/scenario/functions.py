# -*- coding: utf-8 -*-
#
# This file provide some task accessible from the scenario editor
#

import os
import cPickle

CREATE_NEW_PROCESS_GROUP = 512

import libs.oscack
from libs.oscack import message
from modules import globalfunction, oscpatcher
from engine.setting import settings
from engine.threads import scenario_scheduler, patcher
from scenario import pool, classes
from engine.fsm import Flag
from engine.log import init_log

log = init_log("functools")


def get_wanted_media_list():
    """
    This function search in the parsed scenario all media wich could be played by the card
    :return: list of Media file objects
    """
    media_list = list()
    for box in pool.Etapes_and_Functions.values():
        if isinstance(box, classes.Etape):
            for action in box.actions:
                if len(action) > 0 and isinstance(action[1], dict):         # If there are some params
                    k = action[1].keys()
                    if "signal" in k and "args" in k:                           # ADD SIGNAL BOX
                        argsk = action[1]["args"].keys()
                        if "dest" in argsk and "media" in argsk:                # It's a PLAY box
                            if settings.get("uName")in action[1]["args"]["dest"]:     # It's for us
                                path = action[1]["args"]["media"]
                                if "VIDEO" in action[1]["signal"]:
                                    path = os.path.join(settings.get("path", "relative", "video"), path)
                                elif "AUDIO" in action[1]["signal"]:
                                    path = os.path.join(settings.get("path", "relative", "audio"), path)
                                else:
                                    log.warning("SIGNAL BOX WITH MEDIA BUT IT'S NOT AN VIDEO/AUDIO_PLAY")
                                if path not in media_list:      # Check and avoid duplications
                                    media_list.append(path)
    return media_list


@oscpatcher("SIGNAL_FORWARDER")
def forward_signal(*args, **kwargs):
    """
    This function forward signal embeded in OSC message with path /signal
    :return:
    """
    if args[0].args["path"] == '/signal':
        flag = cPickle.loads(str(bytearray(args[0].args["args"][1])))
        log.debug('Forwarded signal received {0}'.format(flag.get_info()))
        patcher.serve(flag)
    else:
        return False

@globalfunction("ADD_TIMER")
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


@globalfunction("TRANSIT_AUTO")
def auto_transit(*args, **kwargs):
    """
    If an Etape has no out transition, it adds an auto transition to parent Etape
    :return:
    """
    log.log('debug', kwargs['_etape'].strtrans())
    if len(kwargs['_etape'].transitions) == 0:
        parent = None
        for parent in reversed(kwargs['_fsm'].history):
            if parent.is_blocking():
                kwargs['_etape'].transitions[None] = parent
                kwargs['_etape']._localvars['emptytransit'] = True
                return
        
        log.warning('NO BLOCKING PARENT FOUND')
            


@globalfunction("TRANSIT_CLEAN")
def remove_transitions(*args, **kwargs):
    """
    If an Etape use auto_transit, we must clean transitions before leaving
    :return:
    """
    if 'emptytransit' in kwargs['_etape']._localvars.keys():
        if kwargs['_etape']._localvars['emptytransit']:
            kwargs['_etape'].transitions = dict()
            kwargs['_etape']._localvars['emptytransit'] = False


@globalfunction("ADD_SIGNAL")
def add_signal(*args, **kwargs):
    """
    This function add a signal in the scenario manager
    :param signal: NAME of the signal to add
    :param args: args to pass to the signal
    :return:
    """
    if "args" not in kwargs.keys():
        kwargs["args"] = dict()
    # log.log("raw", "Add signal : {0}, {1}".format(kwargs["signal"], kwargs["args"]))
    log.log("raw", "Add signal : {0}".format(kwargs))
    # for sfsm in pool.FSM:  # TODO : Here we must use the future signal patcher !
    # sfsm.append_flag(pool.Signals[kwargs["signal"]].get(*kwargs["args"]))
    if "signal" in kwargs.keys():
        sig_uid = kwargs["signal"]
        if sig_uid in pool.Signals.keys():
            signal = pool.Signals[sig_uid]
        else:
            signal = Flag(sig_uid)
            log.log("raw", "Signal unknown : {0}".format(sig_uid))
        # CONSERVE SYNC TIME
        if args[0] is not None and args[0] is not False and 'abs_time_sync' in args[0].args:
            kwargs["args"]['abs_time_sync'] = args[0].args['abs_time_sync']
        patcher.patch(signal.get(dict(kwargs["args"])))


@globalfunction("SERVE_SIGNAL")
def serve_signal(*args, **kwargs):
    """
    This function serve directly a signal without patching him
    :param signal: NAME of signal to patch
    :param kwargs: args to pass to the signal
    :return:
    """
    if "args" not in kwargs.keys():
        kwargs["args"] = list()
    # log.log("raw", "Serve signal : {0}, {1}".format(kwargs["signal"], kwargs["args"]))
    log.log("raw", "Serve signal : {0}".format(kwargs["signal"]))
    patcher.serve(pool.Signals[kwargs["signal"]].get(*kwargs["args"]))


@globalfunction("SEND_OSC_NEIGHBOUR")
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
                message.send(libs.oscack.DNCserver.networkmap.get_by_uName(carte).target, msg)
            except KeyError:
                log.error("There is no {0} carte in NetworkMap".format(carte))


@globalfunction("MSG_SIGNAL_PATCHER")
def msg_patcher(*args, **kwargs):
    """
    This function patch a msg if it fit to a path
    :param path: path OSC
    :param signal: NAME of the signal to create
    :return:
    """
    if args[0].args["path"] in kwargs.keys():
        route = kwargs[args[0].args["path"]]
        sig_uid = route['signal']
        # log.log("raw", "Add signal : {0}, {1}".format(sig_uid, args[0].args))
        log.log("debug", "{0} => {1}".format(args[0].args["path"],sig_uid))
        #log.log('shit')
        if sig_uid in pool.Signals.keys():
            signal = pool.Signals[sig_uid]
        else:
            signal = Flag(sig_uid)
            # log.log("raw", "This signal was not declared..  {0}".format(sig_uid))
            log.log("raw", "Signal not declared : {0}".format(sig_uid))
        named_args = dict()
        for i in xrange(len(route['args'])):
            if i < len(args[0].args["args"]):
                named_args[ route['args'][i] ] = args[0].args["args"][i]
            else:
                named_args[ route['args'][i] ] = None
        named_args["oscargs"] = args[0].args["args"]
        patcher.serve(signal.get(args=named_args))
    else:
        return False

@globalfunction("ACTIVE_MSG_SIGNAL_PATCHER")
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


@globalfunction("REBOOT_MANAGER")
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

