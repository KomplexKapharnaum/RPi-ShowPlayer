# -*- coding: utf-8 -*-
#
# This file define classes needed by the scenario manager
#
#

import threading
import sys
import os
import traceback
from collections import deque

from engine import fsm
# from engine import media
from engine.setting import settings
from scenario import pool
import scenario
from engine.log import init_log, dumpclean
log = init_log("classes")


class Etape(fsm.State):
    """
        This class overide the State class and represent an Etape in the scenario system
    """
    def __init__(self, uid, actions=[], out_actions=[], transitions={}):
        """
        Etape init function
        :param uid: Unique ID
        :param actions: list of functions wich will be run at Etape start
        :param out_actions: list of function wich will be run when leaving this Etape
        :param transitions: list of couple signal-action wich allow fsm to switch Etape
        :return:
        """
        fsm.State.__init__(self, uid, None)
        self.actions = list(actions)
        self.out_actions = list(out_actions)
        self.transitions = dict(transitions)
        self._localvars = dict()
        self.parent = None
        self._current_running_function = None

    def get(self):
        return Etape(self.uid, self.actions, self.out_actions, self.transitions)

    def is_blocking(self):
        if None in self.transitions.keys(): return False
        if True in self.transitions.keys(): return False
        return True

    def _run_fnct(self, _fsm, fnct, flag, kwargs):
        """
        This function run a function, when it's end set preemptible
        :param _fsm: FSM in wich etape is played
        :param fnct: fnct to run
        :param flag: flag to pass
        :param kwargs: kwargs to pass
        :return:
        """
        if kwargs is None:
            kwargs = dict()
        kwargs["_fsm"] = _fsm
        kwargs["_etape"] = self
        try:
            fnct(flag, **kwargs)
        except Exception as e:
            log.error(" == ERROR DURING A ETAPE ({0}) FUNCTION ({1}) !!".format(self.uid, fnct))
            log.error(e)
            log.error(traceback.format_exc())
            log.error(sys.exc_info()[0])
            log.error(" ==")
        if self._current_running_function is fnct:
            self.preemptible.set()
        else:  # Something else have set the function premptible
            pass

    def run_in(self, _fsm, flag):
        """
        This function is called by the FSM when entering the Etape
        :param flag: flag wich cause the change
        :return:
        """
        log.log("debug", "START ETAPE :: {0}".format(self.uid))
        if len(self.actions) > 0:
            return self._run(_fsm, flag, self.actions)

    def run_out(self, _fsm, flag):
        """
        This function is called by the FSM when quiting the Etape
        :param flag: flag wich cause the change
        :return:
        """
        if len(self.out_actions) > 0:
            return self._run(_fsm, flag, self.out_actions)

    def _run(self, _fsm, flag, fnct_list):
        """
        This function is called by the Etape when entering or escaping it
        :param flag: flag wich cause the change
        :param fnct_list: Function list with [function, {arguments} (optional)]
        """
        for fnct in fnct_list:
            self.preemptible.clear()
            self._current_running_function = fnct[0]
            th = threading.Thread(target=self._run_fnct, args=(_fsm, fnct[0], flag, fnct[1]))
            th.start()
            self.preemptible.wait()

    def __str__(self):
        return "Etape : {0}".format(self.uid)

    def __repr__(self):
        return self.__str__()


class ScenarioFSM(fsm.FiniteStateMachine):
    """
        This class overide the FiniteStateMachine class to adapt it with the scenario system
    """
    def __init__(self, name, flag_stack_len=256):
        """
        :param name: Unique name of the FSM
        :param flag_stack_len: Lenght of the signal flag stack
        :return:
        """
        fsm.FiniteStateMachine.__init__(self, name, flag_stack_len)
        self.history = deque(maxlen=32)

    def _change_state(self, flag, state):
        """
        This function is called when the FSM will change current state
        :param flag: Flag wich cause the change
        :param state: Next state to run
        :return:
        """
        if self.current_state is not None:
            self.history.append(self.current_state)
            # state.parent = self.current_state
            self.current_state.run_out(self, flag)  # blocking
        self.current_state = state
        log.log("raw", "- Start etape functions")
        state.run_in(self, flag)  # blocking
        log.log("raw", "- End etape functions")
        self._clean_flag_stack(jump=True)
        # Now watch if there is some direct transition to perform
        if True in state.transitions.keys():
            self._catch_flag(flag, state.transitions[True])
        elif None in state.transitions.keys():
            self._catch_flag(None, state.transitions[None])
        self._event_flag_stack_new.set()  # An old signal can now be interesting !
        log.log("raw", "- End change state")
        return True


class Scene:
    """
    This class describe a scene in the scenario system
    """
    def __init__(self, uid, cartes):
        """
        :param uid: Unique ID
        :param cartes: foreach Carte present in the Scene define which Etapes must be start
        :return:
        """
        self.uid = uid
        self.cartes = cartes

    def start(self):
        """
        This function is called by the Manager to start the new scene
        """
        for etape in self.cartes[settings["uName"]]:
            fsm = ScenarioFSM(etape.uid)
            fsm.start(etape)
            pool.FSM.append(fsm)

    def __str__(self):
        return "Scene : {0}".format(self.uid)

    def __repr__(self):
        return self.__str__()


class Carte:
    """
    This class define a Carte which is only a unique name and a device type
    """
    def __init__(self, uid, device):
        """
        :param uid: Unique ID
        :param device: Device type of the card
        :return:
        """
        self.uid = uid
        self.device = device

    def __str__(self):
        return "Carte : {0}".format(self.uid)

    def __repr__(self):
        return self.__str__()


class Device:
    """
    This class describe a Device
    """
    def __init__(self, uid, modules, patchs, managers):
        """
        :param uid: Unique ID
        :param modules: list of modules used by the Device
        :param patchs: list of patchs wich must be run
        :param managers: list of etapes which must be run in a FSM to manage the device
        :return:
        """
        self.uid = uid
        self.modules = modules
        self.patchs = patchs
        self.managers = managers
        for manager_uid in scenario.DECLARED_MANAGER:
            if manager_uid in pool.Etapes_and_Functions.keys():
                self.managers[manager_uid] = pool.Etapes_and_Functions[manager_uid]

    def launch_manager(self):
        """
        This function is launch at startup and init device managers fsm
        """
        log.log("raw", "Launching manager devices")
        for manager in self.managers.values():
            log.log("raw", "--  manager devices {0} launch..".format(manager.uid))
            pool.DEVICE_FSM.append(ScenarioFSM(manager.uid))
            pool.DEVICE_FSM[-1].start(manager)

    def __str__(self):
        return "Device : {0}".format(self.uid)

    def __repr__(self):
        return self.__str__()


class Patch:
    """
    This class describ a basic patch
    """
    def __init__(self, uid, signal, treatment):
        """
        :param uid: Unique ID
        :param signal: Signal to patch
        :param treatment: function which realize the patch
        :return:
        """
        self.uid = uid
        self.signal = signal
        self.treatment = treatment

    def __str__(self):
        return "Patch : {0}".format(self.uid)

    def __repr__(self):
        return self.__str__()
#
#
# class Media:
#     """
#     This class provide an interface for media files
#     """
#     def __init__(self, uid, path, checksum):
#         """
#         :param uid: Unique ID
#         :param path: Path to the media file
#         :param checksum: Checksum of the media
#         :return:
#         """
#         self.uid = uid
#         self.path = path
#         self.checksum = checksum
#
#     def _get_fs_checksum(self):
#         """
#         This function return the real checksum of the current file on the filesystem
#         :return:
#         """
#         return media.get_fs_checksum(self.path)
#
#     def is_onfs(self):
#         """
#         This function test if the media is on the filesystem
#         :return:
#         """
#         if not os.path.exists(self.path):
#             return False
#         return self.checksum == self._get_fs_checksum()