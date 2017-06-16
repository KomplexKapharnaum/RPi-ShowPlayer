# -*- coding: utf-8 -*-
#
#
# This file provide an interface for the sched module with thread support
#
#

import time
import threading

from engine.tools import register_thread, unregister_thread
from engine.log import init_log
log = init_log("sched")


class ThreadScheduler:
    """
        This class provide an interface for the sched module with thread support
    """

    def __init__(self):
        register_thread(self)
        self._timers = {}
        self._counter = 0

    def enterasb(self, abstime, action, argument=(), kwargs={}):
        if not hasattr(argument, '__iter__'):
            argument = (argument, )
        self._counter += 1
        timer = threading.Timer(time.time()-abstime, action, argument, kwargs)
        timer.start()
        self._timers[self._counter] = timer
        return self._counter

    def enter(self, delay, action, argument=(), kwargs={}):
        # log.log("raw", "Add new scheduled action {0} in {1} sec".format(action, delay))
        if not hasattr(argument, '__iter__'):
            argument = (argument, )
        self._counter += 1
        timer = threading.Timer(delay, action, argument, kwargs)
        timer.start()
        self._timers[self._counter] = timer
        return self._counter

    def cancel(self, counter):
        self._timers[counter].cancel()
        del self._timers[counter]

    def stop(self):
        log.debug("Stop the {0} scheduler".format(self))
        for timer in self._timers.values():
            timer.cancel()
            del timer
        unregister_thread(self)

    def join(self, *args, **kwargs):
        """
        Emulate join function
        :param args:
        :param kwargs:
        :return:
        """
        return True


class ThreadRepeater(object):
    """
        Timer repeater thread
    """
    def __init__(self, interval, function, *args, **kwargs):
        register_thread(self)
        self._timer = None
        self.interval = interval
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.is_running = False

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self._timer = threading.Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False
        unregister_thread(self)

    def join(self, *args, **kwargs):
        """
        Emulate join function
        """
        return True

class TS_Scheduler(object):
    """
        Scheduler that is threadsafe
    """

    def __init__(self, interval, function, *args, **kwargs):
        register_thread(self)
        self._timer = None
        self.interval = interval
        self.function = function
        self.args = args if args is not None else list()
        self.kwargs = kwargs if kwargs is not None else dict()
        self.is_running = threading.Event()
        self._lock = threading.RLock()

    def _run(self):
        with self._lock:
            self._timer = threading.Timer(self.interval, self._run)
            self.function(*self.args, **self.kwargs)

    def start(self, now=True):
        log.debug("Start thread safe sheduler")
        with self._lock:
            if not self.is_running.isSet():
                register_thread(self)
                self.is_running.set()
                interval = 0 if now else self.interval
                self._timer = threading.Timer(interval, self._run)
            else:
                log.warning("Try to restart and already started TS_Scheduler")

    def cancel(self):
        with self._lock:
            if self.is_running.isSet() and self._timer is not None:
                self._timer.cancel()
                self.is_running.clear()
                unregister_thread(self)

    def stop(self):
        self.cancel()

    def join(self, *args, **kwargs):
        self.cancel()
        return True
