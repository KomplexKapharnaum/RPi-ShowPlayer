##################
# MAIN APPLICATION
##################
from engine.setting import settings
from engine.log import set_default_log_by_settings
set_default_log_by_settings(settings)                   # Set default log level and output via settings

import engine
import scenario
from scenario import parsing
from modules import MODULES
from libs import oscack
log = engine.log.init_log("application")

import threading
import time


POWEROFF = 0    # 1: STOP PROGRAM   2: POWEROFF AFTER STOP  3: REBOOT AFTER STOP

def init(autoload=True):
    # LOAD INPUT KEYBOARD THREAD
    k = keyboardThread()
    k.start()
    # INIT THREAD
    engine.threads.init()
    # LOAD POOL AND PARSE SCENARIO
    if autoload:
        load(True)


def load(use_archived_scenario=False):
    # CLEAR THE POOL
    scenario.pool.init()
    # RETRIEVE HARD CODED MODULES COMPONENTS
    scenario.init()
    # INIT MODULES FSM
    for manager in settings.get('managers'):
        if manager in MODULES.keys():
            modulefsm = scenario.classes.ScenarioFSM(manager)
            engine.MODULES_FSM[manager] = modulefsm
            log.debug("LOAD MANAGER :: "+manager+" (Auto)")
    # PARSE ACTIVE SCENARIO
    parsing.load(use_archived_scenario)


def reload():
    # STOP RUNNING POOL
    scenario.pool.stop()
    # LOAD
    load()
    # RESTART POOL
    scenario.pool.start()


def start():
    # OSC START
    oscack.start_protocol()
    # START POOL
    scenario.pool.start()
    # MODULES START
    for name, modulefsm in engine.MODULES_FSM.items():
        modulefsm.start(scenario.DECLARED_ETAPES[ MODULES[name]['init_etape'] ])


def stop():
    log.info("Stop Pool Manager")
    scenario.pool.stop()

    log.info("Stop OscAck Servers")
    oscack.stop_protocol()

    log.info("Stop Modules")
    for modulefsm in engine.MODULES_FSM.values():
        modulefsm.stop()
        modulefsm.join()

    log.info("Stop Threads engine")
    engine.threads.stop()


def restart():
    stop()
    init()
    start()


class keyboardThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        engine.tools.register_thread(self)

    def run(self):
        # DEV
        flag_group = engine.fsm.Flag("TEST_GROUP").get()
        flag_group.args["dest"] = [settings.get("scenario", "dest_group"), ]
        flag_all = engine.fsm.Flag("TEST_ALL").get()
        flag_all.args["dest"] = [settings.get("scenario", "dest_all"), ]
        global POWEROFF
        while True:
            try:
                c = raw_input("")
            except:      # For no shell env
                time.sleep(10)
                continue
            if c in ("q", "Q", "quit", "exit"):
                POWEROFF = 1
            if c == "":
                continue
            cmd = c.split()
            if cmd[0] == "settings":
                log.info(settings)
            if cmd[0] == "pw":
                log.info(str(POWEROFF))
            if cmd[0] == "info":
                if scenario.pool.MANAGER is not None:
                    log.info(scenario.pool.MANAGER.current_state)
                log.info(oscack.protocol.discover.machine.current_state)
                log.info(oscack.protocol.scenariosync.machine.current_state)
                for f in scenario.pool.FSM:
                    log.info(f.current_state)
                    log.info(f._flag_stack)
                for f in scenario.pool.DEVICE_FSM:
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
                        engine.threads.patcher.patch(flag_all.get())
                    if cmd[1] == "testgroup":
                        engine.threads.patcher.patch(flag_group.get())
