##################
# MAIN APPLICATION
##################

import os
import pprint

from engine.setting import settings
from engine.log import set_default_log_by_settings
set_default_log_by_settings(settings)                   # Set default log level and output via settings

import engine
import scenario
import modules
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
    # LOAD SUPER-MODULES IN ENGINE
    for name in settings.get('managers'):
        if name in modules.MODULES.keys():
            engine.add_module(name, scenario.classes.ScenarioFSM(name))
    # INITIALIZE SCENARIO
    scenario.init()
    # PARSE SCENARIO
    if autoload:
        scenario.load()


def reload():
    # RELOAD SCENARIO
    oscack.DNCserver.del_method(None, None)         # Disconnect WILD CARD from DNC Server
    scenario.reload()
    # INFORM MEDIA WATCHER
    oscack.media_list_updated()


def start():
    # OSC START
    oscack.start_protocol()
    # START POOL
    scenario.start()
    # MODULES START
    engine.start_modules()


def stop():
    log.info("Stop Scenario")
    scenario.stop()
    log.info("Stop OscAck")
    oscack.stop_protocol()
    log.info("Stop Modules")
    engine.stop_modules()
    log.info("Stop Threads")
    engine.threads.stop()


def restart():
    stop()
    init()
    start()


class keyboardThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        engine.tools.register_thread(self)

    @staticmethod
    def in_info(key="INFO"):
        log.info()
        log.info("=== {key} ===".format(key=key))

    @staticmethod
    def out_info(key="INFO"):
        log.info("=== END {key} ===".format(key=key))
        log.info()

    @staticmethod
    def info(fnct, key="INFO", *args, **kwargs):
        keyboardThread.in_info(key)
        fnct(*args, **kwargs)
        keyboardThread.out_info(key)

    @staticmethod
    def osc_info():
        pass

    @staticmethod
    def basic_osc_info():
        pass

    @staticmethod
    def media_sync_info(alone=False):
        if not alone:
            keyboardThread.basic_osc_info()
        log.info(oscack.protocol.mediasync.machine)
        log.info("All media : {0}".format(engine.media.get_all_media_list()))
        log.info("Needed media : {0}".format(oscack.protocol.mediasync.needed_media_list))
        log.info("Uneeded media : {0}".format(oscack.protocol.mediasync.unwanted_media_list))

    def run(self):
        # DEV
        flag_group = engine.fsm.Flag("TEST_GROUP").get()
        flag_group.args["dest"] = [settings.get("scenario", "dest_group"), ]
        flag_all = engine.fsm.Flag("TEST_ALL").get()
        flag_all.args["dest"] = [settings.get("scenario", "dest_all"), ]
        global POWEROFF
        pretyprinter = pprint.PrettyPrinter(indent=4)
        try:
            while True:
                try:
                    c = raw_input("")
                except KeyboardInterrupt:
                    POWEROFF = 1
                except Exception:      # For no shell env
                    time.sleep(10)
                    continue
                if c in ("q", "Q", "quit", "exit"):
                    POWEROFF = 1
                    break
                if c == "":
                    continue
                cmd = c.split()
                if cmd[0] == "pw":
                    log.info(str(POWEROFF))
                elif cmd[0] == "settings":
                    log.info()
                    log.info("=== SETTINGS ===")
                    to_print = settings
                    if len(cmd) > 1 and cmd[1] in settings.keys():
                        to_print = settings[cmd[1]]
                    log.info(pretyprinter.pprint(to_print))
                    log.info("=== END SETTINGS ===")
                    log.info()
                elif cmd[0] == "msync":
                    keyboardThread.info(keyboardThread.media_sync_info, key="MEDIA SYNC", alone=True)
                elif cmd[0] == "info":
                    log.info()
                    log.info("=== INFO ===")
                    log.info("--- SCENARIO FSM ---")
                    if scenario.SCENARIO_FSM is not None:
                        log.info(scenario.SCENARIO_FSM.current_state)
                    log.info("--------------------")
                    log.info(oscack.protocol.discover.machine)
                    log.info(oscack.protocol.scenariosync.machine)
                    keyboardThread.media_sync_info()
                    for f in scenario.FSM:
                        log.info(f.current_state)
                        log.info(f._flag_stack)
                    for f in scenario.DEVICE_FSM:
                        log.info(f.current_state)
                        log.info(f._flag_stack)
                    log.info(" = oscack.DNCServer.networkmap : {0} ".format(oscack.DNCserver.networkmap))
                    log.info(" = oscack.timetag : {0} ".format(oscack.timetag))
                    log.info(" = oscack.accuracy : {0} ".format(oscack.accuracy))
                    log.info("=== END INFO ===")
                    log.info()
                elif cmd[0] == "signal":
                    if len(cmd) > 1:
                        if cmd[1] == "testall":
                            engine.threads.patcher.patch(flag_all.get())
                        if cmd[1] == "testgroup":
                            engine.threads.patcher.patch(flag_group.get())
                else:
                    log.info("Unknown commad in prompt ..")
        except Exception as e:
            log.exception("Unblocking exception in prompt : \n"+log.show_exception(e))
        # BACKUP EXIT
        time.sleep(5)
        log.log("debug", "Exit by backupexit, should not be that")
        os._exit(POWEROFF)
