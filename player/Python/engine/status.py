# -*- coding: utf-8 -*-
#
# This file regroup the status of the app to be displayed
#

from engine.log import init_log
from engine.setting import settings, devices

log = init_log("status")


class StateValue(bool):
    """
    This class represent a state value (as git stat)
    """

    def __init__(self, value=False, symb="_"):
        """

        :type value: *
        :type symb: str
        :param value: Value of the state
        :param symb: Symbole of the state (as G for git or T for tension)
        """
        bool.__init__(self)
        self._value = value
        self.symb = symb

    def set(self, value):
        """
        Set value o
        :type value: object
        """
        before = bool(self)
        self._value = value
        if before != bool(self):
            return True
        return None

    def is_ok(self):
        if self._value is True:
            return True
        else:
            return False

    def error_message(self):
        return "ERROR"

    @staticmethod
    def _false():
        return False

    @staticmethod
    def _true():
        return True

    def __bool__(self):
        return self.is_ok()

    __nonzero__ = __bool__


class TensionState(StateValue):
    def __init__(self, device):
        """
        :type device: dict or None
        """
        StateValue.__init__(self, value=0, symb=settings.get("log", "symb", "tension"))
        self.device = device
        self._minvalue = settings.get("sys", "lowvoltage", self.device["tension"])
        if settings.get("sys", "raspi") is False:       # If it's not raspi, tension always ok
            self.is_ok = StateValue._true
        elif device is None:
            log.debug("Init tension state of an unknown device")
            self.is_ok = StateValue._false              # If no device it's always false

    def is_ok(self):
        if self._value <= self._minvalue:
            return False
        else:
            return True

    def error_message(self):
        return "Low voltage\n{0}V / {1}V".format(self._value, self._minvalue)


class MediaState(StateValue):
    def __init__(self):
        StateValue.__init__(self, value=[0, 0], symb=settings.get("log", "symb", "media"))

    def is_ok(self):
        if self._value[0] <= self._value[1]:
            return False
        else:
            return True

    def error_message(self):
        return "Need media\n{0} / {1}".format(*self._value)


class RTPState(StateValue):
    def __init__(self):
        StateValue.__init__(self, value=False, symb=settings.get("log", "symb", "rtp"))

    def error_message(self):
        return "No time sync"


class ErrorState(StateValue):
    def __init__(self):
        StateValue.__init__(self, value=True, symb=settings.get("log", "symb", "error"))

    def error_message(self):
        return "Error line {0}\n{1}".format(*self._value)


class ScenarioState(StateValue):
    def __init__(self):
        StateValue.__init__(self, value=True, symb=settings.get("log", "symb", "scenario"))

    def error_message(self):
        return "Scenario error\n{0}".format(self._value)


class GitState(StateValue):
    def __init__(self):
        StateValue.__init__(self, value=True, symb=settings.get("log", "symb", "git"))

    def error_message(self):
        return "Git {0}\n{1}".format(*self._value)


class State():
    """
    This class define the current state of the app
    """

    def __init__(self):
        self._device = None
        for elem in devices:
            if elem["hostname"] == settings.get("uName"):
                self._device = None

        self.tension = TensionState(self._device)
        self.media = MediaState()
        self.rtp = RTPState()
        self.error = ErrorState()
        self.scenario = ScenarioState()
        self.git = GitState()


