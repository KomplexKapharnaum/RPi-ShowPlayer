# -*- coding: utf-8 -*-
#
# This file provide tools to keep an eye on perf and stability
#

import weakref
import time
import datetime
import inspect
import os
import sys
import traceback

from collections import deque

from engine.setting import settings
from engine.log import init_log

log = init_log("perf")

fsm_declared = list()
old_fsm_declared = deque(maxlen=settings.get("perf", "undeclared_fsm"))

history_max_len = settings.get("perf", "history", "length")
default_format = settings.get("perf", "history", "format")

log_fnct = log.important

class HistoryEvent(object):
    """
    Main class of all event which can append during the life of a fsm
    """

    def __init__(self, *args, **kwargs):
        """
        :param fsm: FSM which event is atteched
        """
        self._time = datetime.datetime.now()
        self.parent_fsm = kwargs["fsm"]
        self.indice = kwargs["indice"]

    def get_raw_time(self):
        return self._time

    @property
    def time(self):
        return str(self._time.strftime("%H:%M:%S:%f"))
        #return str(self._time.strftime("%Y-%m-%d %H:%M:%S:%f"))

    def prompt(self, p_format=default_format):
        pass


class ExceptionEvent(HistoryEvent):
    """
    This class represent an excpetion appended during a FSM state function
    """

    def __init__(self, exception, exec_info, *args, **kwargs):
        """
        :param exception: Exception object of the error
        """
        HistoryEvent.__init__(self, *args, **kwargs)
        self.exception = exception
        self.sys_info = exec_info
        self.sys_formated = traceback.format_exception(*self.sys_info)
        # self.sys_formated = traceback.extract_stack()[-1]

    def add_line_begin(self, line):
        """
        Add line begin
        :param line: Line to treat
        """

    def _simple_format(self):
        """
        This function return a prompt entry of the exception
        """
        r = "({ctime}) {:<40}".format(self.exception, ctime=self.time)
        sep = "                        "
        sep_return = "\n" + sep
        lines = []
        for line in self.sys_formated:
            line = line.split("\n")
            for real_line in line:
                if real_line != "":
                    lines.append(real_line)
        r += sep_return.join(lines)
        # r += sep.join([sep_return.join(line.split("\n")) for line in self.sys_formated])
        return r

    def prompt(self, p_format=default_format):
        return self._simple_format()


class ChangeFSM(HistoryEvent):
    """
    This class represent a change in the state of a FSM
    """

    def __init__(self, changetype, from_state, to_state, flag, *args, **kwargs):
        HistoryEvent.__init__(self, *args, **kwargs)
        self.changetype = changetype
        self.from_state = from_state
        self.to_state = to_state
        self.flag = flag

    def _simple_format(self):
        """
        This function return a prompt of this change in a simple format
        """
        r = "({ctime}) {:<40} ".format(self.from_state.uid, ctime=self.time)
        if self.changetype == "transition":
            r += "~~"
        else:
            r += "=>"
        flag = self.flag
        if flag in (None, True, False):
            flag = str(flag)
        else:
            flag = flag.uid
        return r + " {0} caused by {1}".format(self.to_state, flag)

    def prompt(self, p_format=default_format):
        """
        This function prompt a change according to a given format
        """
        if p_format == "simple":
            return self._simple_format()


class FlagEvent(HistoryEvent):
    """
    This class represent a flag event as event add to a fsm, perform transition or be remove cause to TTL or JTL
    """

    def __init__(self, flag, event, event_args, *args, **kwargs):
        """
        :param flag: Ref to the flag
        :param event: Can be : ADDED, REMOVED, CATCHED
        :param event_args: Args to explain what append during the event, should be a dict
        """
        HistoryEvent.__init__(self, *args, **kwargs)
        self.ctime = time.ctime()
        self.flag = flag  # Becarefull, it add a reference so the flag won't be garbage until this die
        self.event = event
        self.event_args = event_args

    def _simple_format(self):
        """
        This function return a prompt of this event in a simple format
        """
        if self.flag in (None, True, False):
            uid = self.flag
        else:
            uid = self.flag.uid
        r = "({ctime})      - {:<10} {:<25}".format(self.event.upper(), uid, ctime=self.time)
        if self.event == "add":
            frame = inspect.getframeinfo(self.event_args["frame"])
            r += " in {0:<30} with (JTL:{JTL:<4},TTL:{TTL:<4}) at {1}:{2}".format(frame.function,
                                                                        os.path.relpath(frame.filename,
                                                                                        settings.get_path("codepy")),
                                                                        frame.lineno,
                                                                        JTL=self.event_args["JTL"],
                                                                        TTL=self.event_args["TTL"])
        elif self.event == "removed":
            r += " because of {0} : {1}".format(self.event_args["reason"], self.event_args["value"])
        # elif self.event == "catched":
        # r += " to {0} "
        return r

    def prompt(self, p_format=default_format):
        return self._simple_format()


class HistoryFSM(deque):
    """
    This class keep an history of the past of an fsm
    """

    def __init__(self, weak_parent):
        """
        :param weak_parent: Weak_ref to the FSM
        """
        self._fsm = weak_parent
        self._indice = 0
        deque.__init__(self, maxlen=history_max_len)

    def append(self, *args, **kwargs):
        """
        This function override append to keep an history of how many change the FSM performed
        :param args:
        :param kwargs:
        :return:
        """
        self._indice += 1
        deque.append(self, *args, **kwargs)

    def show(self, p_format=default_format, n=None):
        """
        This function show the history according to a given format
        :param p_format:
        :param n: Number of elem to show, None = all
        """
        r = ""
        if n is None:
            n = len(self)
        if n < 1:
            log.debug("Show {0} history elem".format(n))
            return False
        for i in range(n):
            change_indice = self._indice + i - n
            r += "[{:>3}] {change}\n".format(change_indice, change=self[len(self) + i - n].prompt(p_format=p_format))
        return r


class DeclaredFSM(object):
    """
    This class explain why the fsm have start
    """

    def __init__(self, fsm, fsmtype, source=None):
        """
        :param fsm: FSM to delcared
        :param fsmtype: Type of FSM (classic of scenario)
        :param source: Source of the FSM, ex : (rtp, manager, media sync, scenario ..)
        """
        self._fsm = weakref.ref(fsm)
        self.name = fsm.name
        self.fsmtype = fsmtype
        self.source = source
        self.running = True
        self._history = HistoryFSM(self._fsm)
        self.get_history = self._history.show

    def get_raw_history(self):
        """
        Return raw history of the FSM
        :return:
        """
        return self._history

    def change_step(self, from_step, next_step, flag):
        """
        This function log when a fsm change his step and why
        :param from_step: Previous step
        :param next_step: Next step to reach
        :param flag: Flag which pass to this step
        """
        self._history.append(ChangeFSM("step", from_step, next_step, flag, fsm=self._fsm, indice=self._history._indice))

    def condition_transition(self, from_step, transition, flag):
        """
        This function log when a fsm perform a transition and why
        :param from_step: Previous step
        :param transition: Transition function which wiil be called
        :param flag: Flag which pass to this transition
        """
        self._history.append(ChangeFSM("transition", from_step, transition, flag, fsm=self._fsm, indice=self._history._indice))

    def flag_event(self, flag, event, event_args):
        """
        This function add a Flag event into the history
        :param flag: Flag to log
        :param event: Event to record (added, removed)
        :param event_args: Agrs to explain what happends
        """
        self._history.append(FlagEvent(flag, event, event_args, fsm=self._fsm, indice=self._history._indice))

    def log_exception(self, exception, exec_info):
        """
        This function log an exception from a FSM state
        """
        self._history.append(ExceptionEvent(exception, exec_info, fsm=self._fsm, indice=self._history._indice))

    @property
    def fsm(self):
        if self._fsm() is not None:
            return self._fsm()
        else:
            log.warning("Try to access to a defunct FSM {0}".format(self))

    @fsm.setter
    def fsm(self, value):
        log.error("It's forbbiden to change the fsm reference of a declared FSM")

    def __str__(self):
        if self.running:
            return "{name}({fsmtype}) from {source} [run]".format(name=self.name, fsmtype=self.fsmtype,
                                                                  source=self.source)
        else:
            return "{name}({fsmtype}) from {source} [end]".format(name=self.name, fsmtype=self.fsmtype,
                                                                  source=self.source)

    def __repr__(self):
        return self.__str__()


def declare_fsm(fsm, fsmtype="fsm", source=None):
    """
    This function decalred an fsm
    :param fsm: FSM to declare
    :param fsmtype: If True, it's a scenario FSM
    :return:
    """
    dec_fsm = DeclaredFSM(fsm, fsmtype, source)
    fsm_declared.append(dec_fsm)
    return dec_fsm


def undeclare_fsm(fsm):
    """
    This function undeclared a previous declared fsm
    :param fsm:
    :return:
    """
    fsm_to_remove = None
    for dec_fsm in fsm_declared:
        if fsm is dec_fsm.fsm:
            fsm_to_remove = dec_fsm
            fsm_declared.remove(dec_fsm)
            break
    if fsm_to_remove is not None:
        old_fsm_declared.append(fsm_to_remove)
    else:
        log.debug("Try to undeclare an FSM which is already gone {0} ".format(fsm))


def list_fsm(list_all=True):
    """
    This function list FSMs
    :param list_all: If True list undeclared fsm
    :return:
    """
    i = 0
    r = ""
    for fsm in fsm_declared:
        r += "[{:>3}] {_fsm}\n".format(i, _fsm=fsm)
        i += 1
    if list_all:
        for fsm in old_fsm_declared:
            r += "[{:>3}] (stop){_fsm}\n".format(i, _fsm=fsm)
            i += 1
    return r


def prompt_history(list_all=True):
    """
    This function ask for a given FSM and prompt his history
    :param list_all: If True list undeclared fsm
    :return:
    """
    try:
        log_fnct("Which FSM history do you want to see ? (* for all)\n{0}".format(list_fsm(list_all)))
        selected = raw_input("Chose one or * for all : ")
        if selected == "*":
            all_history(stopped=True)
        else:
            try:
                selected = int(selected)
            except TypeError:
                log_fnct("Incorrect.. {0} (we need an int)".format(selected))
                return False
            to_show = fsm_declared
            if selected >= len(fsm_declared):
                log.debug("It's will be an old fsm (selected {2}, declared : {0}, stopped {1})".format(
                    len(fsm_declared, old_fsm_declared, selected)))
                selected -= len(fsm_declared)
                to_show = old_fsm_declared
                if selected >= len(old_fsm_declared):
                    log.warning("Too high, choose a correct number")
                    return False
            log_fnct("History for {0} :\n".format(to_show[selected]) + str(to_show[selected].get_history()))
    except Exception as e:
        log_fnct(log.show_exception(e))


def all_history(stopped=False):
    """
    This function return the history of all FSM
    :param stopped: If True return stopped FSM with running ones
    :return:
    """
    to_show = fsm_declared
    if stopped:
        to_show += old_fsm_declared
    for fsm in to_show:
        log_fnct("History for {0} :\n".format(fsm) + str(fsm.get_history()))


def multiplex_history(fsm_list):
    """
    Show multiple FSM in the same output
    :param fsm_list: list of FSM to show, if * it takes all declared, if ** takes old fsm with declared
    :return:
    """
    try:
        to_show = list()
        if fsm_list == list("*"):
            to_show = fsm_declared
        elif fsm_list == list("**"):
            to_show = fsm_declared + old_fsm_declared
        else:
            for n in fsm_list:
                if int(n) < len(fsm_declared):
                    to_show.append(fsm_declared[int(n)])
                else:
                    to_show.append(old_fsm_declared[int(n)-len(fsm_declared)])
        global_history = []
        for fsm in to_show:
            global_history += fsm.get_raw_history()
        global_history.sort(key=lambda x: x.get_raw_time())
        r = ""
        for i, entry in enumerate(global_history):
            uid = entry.parent_fsm()
            if uid is not None:
                uid = uid.name
            r += "[{i:<3}] in {fsm:<20} [{indice:<3}] {change}".format(i=i, fsm=uid, indice=entry.indice, change=entry.prompt()) + "\n"
        log_fnct(r)
    except Exception as e:
        log_fnct(log.show_exception(e))








