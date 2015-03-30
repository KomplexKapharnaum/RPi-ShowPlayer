# -*- coding: utf-8 -*-
#
#
# This file store running threads inside a same file to control them easier
#


from src.scheduling import ThreadScheduler
from src.scenario.patcher import ThreadPatcher
from src import tools
from src.log import init_log
log = init_log("threads")

network_scheduler = ThreadScheduler()
scenario_scheduler = ThreadScheduler()
patcher = ThreadPatcher()


def init():
    global patcher
    if not isinstance(patcher, ThreadPatcher):
        patcher = ThreadPatcher()
    if not patcher.is_alive():
        patcher.start()


def stop():
    for thread in tools._to_stop_thread.values():
        th = thread()   # Get the reference
        if th is not None:
            try:
                th.stop()
            except AttributeError as e:
                log.error(e)