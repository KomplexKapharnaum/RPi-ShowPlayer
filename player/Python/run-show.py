#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#

import sys
import os
import time
from engine.setting import settings
from engine.log import set_default_log_by_settings
set_default_log_by_settings(settings)                   # Set default log level and output via settings

from engine import log, fsm, threads
import scenario
from scenario import parsing, pool, manager
from libs import oscack
from engine.log import dumpclean


def set_python_path(depth=0):
    f = sys._getframe(1)
    fname = f.f_code.co_filename
    fpath = os.path.dirname(os.path.abspath(fname))
    PythonPath = os.path.join(fpath, "../".join(["" for x in xrange(depth+1)]))
    sys.path.append(PythonPath)
    # print(PythonPath)

set_python_path(depth=1)


# log.DEFAULT_LEVEL = settings.get("log", "level")
# log.DEFAULT_LOG_TYPE = settings.get("log", "output")

log = log.init_log("main")

try:
    threads.init()
    oscack.start_protocol()


    parsing.clear_scenario()

    basescenario = os.path.join(settings.get("path", "scenario"), "timeline_timeline1.json")
    mypool = parsing.parse_file(basescenario)['pool']
    parsing.parse_customdevices(mypool)
    parsing.parse_customlibrary("library_library.json")
    parsing.parse_customscenario("scenario_play_btn.json")
    parsing.parse_customtimeline(mypool)

    if settings["uName"] in pool.Cartes.keys():
        pool.Cartes[settings["uName"]].device.launch_manager()
        managefsm = fsm.FiniteStateMachine("Manager")
        managefsm.start(manager.step_init)
        pool.MANAGER = managefsm
        managefsm.append_flag(manager.start_flag.get())
    else:
        log.info("== NO SCENARIO FOR: {0}".format(settings["uName"]))

    while True:
        try:
            c = raw_input("$ :")
        except Exception as e:      # For no shell env
            time.sleep(10)
            continue
        if c in ("q", "Q", "quit", "exit"):
            break
        if c == "":
            continue
        cmd = c.split()
        if cmd[0] == "info":
            log.info(managefsm.current_state)
            log.info(oscack.protocol.discover.machine.current_state)
            log.info(oscack.protocol.scenariosync.machine.current_state)
            for f in pool.FSM:
                log.info(f.current_state)
                log.info(f._flag_stack)
            for f in pool.DEVICE_FSM:
                log.info(f.current_state)
                log.info(f._flag_stack)
            log.info(" = oscack.DNCServer.networkmap : ")
            log.info(oscack.DNCserver.networkmap)
            log.info(" = oscack.timetag : ")
            log.info(oscack.timetag)
            log.info(" = oscack.accuracy : ")
            log.info(oscack.accuracy)
except Exception as e:
    log.exception(log.show_exception(e))
    log.error(e)

managefsm.stop()
managefsm.join()
log.info("Ending Manager")
for sfsm in pool.FSM:
    sfsm.stop()
    sfsm.join()
for sfsm in pool.DEVICE_FSM:
    sfsm.stop()
    sfsm.join()
log.info("Ending OscAck Servers")
oscack.stop_protocol()
threads.stop()
os._exit(0)
