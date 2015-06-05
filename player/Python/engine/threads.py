# -*- coding: utf-8 -*-
#
#
# This file store running threads inside a same file to control them easier
#


from engine.scheduling import ThreadScheduler, ThreadRepeater
from scenario.patcher import ThreadPatcher
from engine import tools
from setting import settings
from engine.log import init_log
log = init_log("threads")

network_scheduler = ThreadScheduler()
scenario_scheduler = ThreadScheduler()
ping_sender = ThreadRepeater(settings.get("log", "monitor", "pingtime"), tools.sendPing)
patcher = ThreadPatcher()
log_teleco = tools.ThreadTeleco()


def init():
    global patcher, log_teleco
    log_teleco.start()
    if not isinstance(patcher, ThreadPatcher):
        patcher = ThreadPatcher()
    if not patcher.is_alive():
        patcher.start()


def start():
    if settings.get("log", "monitor", "active"):
        ping_sender.start()


def stop():
    log.debug("STOPPING THREADS")
    to_stop = tools._to_stop_thread.values() #local dict to avoid size index change in for loop
    for thread in to_stop:
        th = thread()   # Get the reference
        """:type: threading.Thread"""
        log.debug("  Try to stop thread : {0}".format(th))
        if th is not None:
            try:
                th.stop()
                th.join(timeout=1)
            except AttributeError as e:
                log.error(e)
            except RuntimeError as e:
                log.error("Thread do not join unitl 1 seconde..")
                log.error(log.show_exception(e))
