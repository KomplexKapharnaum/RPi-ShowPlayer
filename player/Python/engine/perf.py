# -*- coding: utf-8 -*-
#
# This file provide tools to keep an eye on perf and stability
#

import weakref
import time

from collections import deque

from engine.setting import settings
from engine.log import init_log
log = init_log("perf")


fsm_declared = list()
old_fsm_declared = deque(maxlen=settings.get("history", "undeclared_fsm"))


class ChangeFSM(object):
    """
    This class represent a change in the state of a FSM
    """
    def __init__(self, changetype, from_state, to_state, flag):
        self.ctime = time.ctime()
        self.changetype = changetype
        self.from_state = from_state
        self.to_state = to_state
        self.flag = flag


class HistoryFSM(deque):
    """
    This class keep an history of the past of an fsm
    """
    def __init__(self, weak_parent):
        """
        :param weak_parent: Weak_ref to the FSM
        """
        self._fsm = weak_parent
        deque.__init__(self, maxlen=settings.get("perf", "history", "length"))

    def change_step(self, from_step, next_step, flag):
        """
        This function log when a fsm change his step and why
        :param from_step: Previous step
        :param next_step: Next step to reach
        :param flag: Flag which pass to this step
        """
        self.append(ChangeFSM("step", from_step, next_step, flag))

    def condition_transition(self, from_step, transition, flag):
        """
        This function log when a fsm perform a transition and why
        :param from_step: Previous step
        :param transition: Transition function which wiil be called
        :param flag: Flag which pass to this transition
        """
        self.append(ChangeFSM("transition", from_step, transition, flag))


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

    @property
    def fsm(self):
        if self._fsm() is not None:
            return self._fsm()
        else:
            log.warning("perf", "Try to access to a defunct FSM {0}".format(self))

    @fsm.setter
    def fsm(self, value):
        log.error("It's forbbiden to change the fsm reference of a declared FSM")

    def __str__(self):
        if self.running:
            return "{name}({fsmtype}) from {source} [run]".format(name=self.name, fsmtype=self.fsmtype, source=self.source)
        else:
            return "{name}({fsmtype}) from {source} [end]".format(name=self.name, fsmtype=self.fsmtype, source=self.source)

    def __repr__(self):
        return self.__str__()


def declare_fsm(fsm, fsmtype="fsm", source=None):
    """
    This function decalred an fsm
    :param fsm: FSM to declare
    :param fsmtype: If True, it's a scenario FSM
    :return:
    """
    fsm_declared.append(DeclaredFSM(fsm, fsmtype, source))


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
        log.warning("Try to undeclared an FSM {0} which doesn't exit or have already died".format(fsm))


