# -*- coding: utf-8 -*-
#
#
# This file provide threads for patching signals in the scenario system
#

import threading
import Queue
import cPickle
from copy import deepcopy

from libs.oscack import message
from libs.oscack import BroadcastAddress
import libs.oscack
# import libs.oscack.message
# import libs.oscack.
from libs import rtplib
import engine
from engine.setting import settings
from engine.tools import register_thread, unregister_thread
import scenario
from engine.log import init_log
log = init_log("patcher")

class ThreadPatcher(threading.Thread):
    """
    This class define a thread which wait a signal into the queue and apply to him a patch if there is some defined
    """
    def __init__(self):
        threading.Thread.__init__(self)
        register_thread(self)
        self._stop = threading.Event()
        self._patchs = dict()
        self._queue = Queue.Queue()

    def add_patch(self, signal_uid, function, kwargs):
        """
        This function is called when the manager init
        :param signal_uid: ID of the signal
        :param function: function to call
        :param kwargs: dict to pass to the function as kwargs
        :return:
        """
        if signal_uid not in self._patchs.keys():
            self._patchs[signal_uid] = list()
        self._patchs[signal_uid].append((function, kwargs))

    @staticmethod
    def serve(signal):
        """
        This function is public and can be called to serve a signal (after getting him) to all running ScenarioFSM
        :param signal: signal to serve
        :return:
        """
        for fsm in scenario.FSM:
            fsm.append_flag(signal)
        for fsm in scenario.DEVICE_FSM:
            fsm.append_flag(signal)
        for fsm in engine.MODULES_FSM.values():
            fsm.append_flag(signal)

    def patch(self, signal):
        """
        This function is public and can be called to patch a signal (after getting him)
        :param signal: Signal to patch
        :return:
        """
        self._queue.put(signal)

    @staticmethod
    def _patch(signal, function_list):
        """
        This function is called in the thread by run
        :param signal: Signal to patch
        :param function_list: List of function to apply as patch
        :return:
        """
        for function in function_list:
            if function[0](signal, **function[1]) is False:
                ThreadPatcher.serve(signal)

    def _dispatch(self, signal):
        # envoyer au destinataire via 
        # sendto = copy(signal.args["dest"])
        # del signal.args["dest"]
        log.log("debug", "dispatch to : {0}".format(signal))

        sendto = deepcopy(signal.args["dest"])
        signal.args["dest"] = list()
        if "abs_time_sync" not in signal.args.keys():
            s, ns = rtplib.get_time()
            signal.args["abs_time_sync"] = rtplib.add_time(s, ns, settings.get("scenario", "play_sync_delay"))
        if settings.get("scenario", "dest_all") in sendto:
            log.log("raw", "dispatch to all dest")
            msg_to_send = message.Message("/signal", signal.uid, ('b', cPickle.dumps(signal, 2)), ACK=False)
            message.send(message.Address("255.255.255.255"), msg_to_send)
        else:
            msg_to_send = message.Message("/signal", signal.uid, ('b', cPickle.dumps(signal, 2)), ACK=True)
            if settings.get("scenario", "dest_group") in sendto:
                log.log("raw", "add group in dispatch list")
                sendto.remove(settings.get("scenario", "dest_group"))
                sendto += [x for x in scenario.CURRENT_SCENE.cartes if x not in sendto]
            for dest in sendto:
                if dest in libs.oscack.DNCserver.networkmap.keys():
                    if dest != settings["uName"] or settings.get("scenario", "dest_self") not in sendto:     # Avoid multiple self send
                        message.send(libs.oscack.DNCserver.networkmap[dest].target, msg_to_send)
                elif dest != settings.get("scenario", "dest_self"):
                    log.warning('Unknown Dest <{0}> for signal <{1}>'.format(dest, signal.uid))

            # reposer dans la pile si _self_
            if settings.get("scenario", "dest_self") in sendto:
                self._queue.put(signal)

    def run(self):
        while not self._stop.is_set() or not self._queue.empty():
            signal = self._queue.get() 
            if signal is None:
                continue
            log.log('raw', '{0}'.format(signal))
            if "dest" not in signal.args.keys():
                signal.args["dest"] = list()
            if len(signal.args["dest"]) > 0 and settings.get("scenario", "dest_self") not in signal.args["dest"]:
                self._dispatch(signal)
            elif signal.uid in self._patchs.keys():
                ThreadPatcher._patch(signal, self._patchs[signal.uid])
            else:
                ThreadPatcher.serve(signal)
        log.log("raw", "Exiting thread patcher")

    def stop(self):
        """
        Ask to stop the thread
        :return:
        """
        log.log("raw", "Asking to exit thread patcher")
        self._stop.set()
        self._queue.put(None)  # To unblock the get in run function
        unregister_thread(self)
