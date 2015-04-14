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
from scenario import parsing, pool, manager, classes, patcher
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
    # INIT
    threads.init()
    pool.init(manager)
    scenario.init()

    # GLOBAL MACHINES
    webfsm = classes.ScenarioFSM("WebInterface")
    patcher.FSM_GLOBAL.append(webfsm)
    webfsm.start(scenario.DECLARED_ETAPES["INTERFACE_START"])

    devicefsm = classes.ScenarioFSM("DeviceControl")
    devicefsm.start(scenario.DECLARED_ETAPES["DEVICE_CONTROL"])
    patcher.FSM_GLOBAL.append(devicefsm)

    # START
    parsing.load()
    oscack.start_protocol()
    pool.start()

    # DEV
    flag_group = fsm.Flag("TEST_GROUP").get()
    flag_group.args["dest"] = [settings.get("scenario", "dest_group"), ]
    flag_all = fsm.Flag("TEST_ALL").get()
    flag_all.args["dest"] = [settings.get("scenario", "dest_all"), ]

    while True:
        try:
            c = raw_input("")
        except Exception as e:      # For no shell env
            time.sleep(10)
            continue
        if c in ("q", "Q", "quit", "exit"):
            break
        if c == "":
            continue
        cmd = c.split()
        if cmd[0] == "settings":
            log.info(settings)
        if cmd[0] == "info":
            if pool.MANAGER is not None:
                log.info(pool.MANAGER.current_state)
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
        if cmd[0] == "signal":
            if len(cmd) > 1:
                if cmd[1] == "testall":
                    threads.patcher.patch(flag_all.get())
                if cmd[1] == "testgroup":
                    threads.patcher.patch(flag_group.get())

except Exception as e:
    log.exception(log.show_exception(e))
    log.error(e)


log.info("Ending Pool Managers")
pool.stop()

log.info("Ending OscAck Servers")
oscack.stop_protocol()

log.info("Ending WebInterface")
webfsm.stop()
webfsm.join()

log.info("Ending Device Control")
devicefsm.stop()
devicefsm.join()

threads.stop()
os._exit(0)
