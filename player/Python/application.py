##################
# MAIN APPLICATION
##################

import os
import pprint

from engine.setting import settings
from engine.log import set_default_log_by_settings
set_default_log_by_settings(settings)                   # Set default log level and output via settings

import sys
import engine
from engine import fsm
import scenario
import modules
from libs import oscack
log = engine.log.init_log("application")

import threading
import time


POWEROFF = 0    # 1: STOP PROGRAM   2: POWEROFF AFTER STOP  3: REBOOT AFTER STOP

def init(autoload=True):
    # LOAD INPUT KEYBOARD THREAD
    k = inputThread()
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
    # oscack.DNCserver.del_method(None, None)         # Disconnect WILD CARD from DNC Server
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


class inputThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        engine.tools.register_thread(self)

    @staticmethod
    def basic_all_info():
        if not settings.correctly_load:
            log.warning("/!\\ SETTINGS NOT CORRECTLY LOADED /!\\ ")
        log.info("uName : {0}, Team : {1}".format(settings["uName"], settings["current_timeline"]))

    @staticmethod
    def path_info():
        log.info("--- PATH ---")
        log.info("DNC path : {0}".format(settings.get("path", "main")))
        log.info("Media path : {0}".format(settings.get_path("media")))
        log.info("Scenario path : {0}".format(settings.get_path("media")))
        log.info("------------")

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
    def osc_info(alone=False, info=False):
        if not alone:
            log.info("--- OSC ---")
        if alone or info:
            keyboardThread.basic_osc_info(alone)
        keyboardThread.media_sync_info()
        keyboardThread.scenario_sync_info()
        keyboardThread.rtp_info()
        if not alone:
            log.info("-----------")

    @staticmethod
    def basic_osc_info(alone=True):
        if alone:
            keyboardThread.basic_all_info()
        log.info("OSC port : {0}, ACK port : {1}".format(settings.get("OSC", "classicport"), settings.get("OSC", "ackport")))

    @staticmethod
    def media_sync_info(alone=False):
        if alone:
            keyboardThread.basic_osc_info()
        log.info(oscack.protocol.mediasync.machine)
        log.info("All media : {0}".format(engine.media.get_all_media_list()))
        log.info("Needed media : {0}".format(oscack.protocol.mediasync.needed_media_list))
        log.info("Uneeded media : {0}".format(oscack.protocol.mediasync.unwanted_media_list))

    @staticmethod
    def scenario_sync_info(alone=False):
        if alone:
            keyboardThread.basic_osc_info()
        log.info(oscack.protocol.scenariosync.machine)

    @staticmethod
    def rtp_info(alone=False):
        if alone:
            keyboardThread.basic_osc_info()
        log.info(oscack.protocol.discover.machine)
        log.info(" = oscack.DNCServer.networkmap : {0} ".format(oscack.DNCserver.networkmap))
        log.info(" = oscack.timetag : {0} ".format(oscack.timetag))
        log.info(" = oscack.accuracy : {0} ".format(oscack.accuracy))

    @staticmethod
    def basic_scenario_info(alone=True):
        if alone:
            keyboardThread.basic_all_info()

    @staticmethod
    def scenario_info(alone=False, info=False):
        if alone or info:
            keyboardThread.basic_scenario_info(alone)
        keyboardThread.scenario_fsm_info()

    @staticmethod
    def scenario_fsm_info(alone=False):
        if alone:
            keyboardThread.basic_scenario_info()
        if not alone:
            log.info("--- SCENARIO FSM ---")

        if scenario.SCENARIO_FSM is not None:
            log.info(scenario.SCENARIO_FSM.current_state)
        for f in scenario.FSM:
            log.info(f.current_state)
            log.info(f._flag_stack)
        for f in scenario.DEVICE_FSM:
            log.info(f.current_state)
            log.info(f._flag_stack)

        if not alone:
            log.info("--------------------")


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
                if c in ("q", "Q", "quit", "exit", "qs"):
                    if c == "qs":   # Prompt all fsm history and quit
                        engine.perf.all_history()
                    POWEROFF = 1
                    break
                if c == "":
                    continue
                cmd = c.split()
                if cmd[0] == "pw":
                    log.info(str(POWEROFF))
                elif cmd[0] == "except":
                    tmpfsm = fsm.FiniteStateMachine("test_fsm")
                    def tmp_fnct(flag):
                        a = 1/0
                    tmpstate = fsm.State("TEST_EXCEPT_STATE", function=tmp_fnct)
                    tmpfsm.start(tmpstate)
                elif cmd[0] == "history":
                    engine.perf.prompt_history()
                elif cmd[0] == "mhistory":
                    engine.perf.multiplex_history(cmd[1:])
                elif cmd[0] == "log":
                    if len(cmd) > 1:
                        engine.tools.log_teleco(ligne1=" ".join(cmd[1:]))
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
                elif cmd[0] == "ssync":
                    keyboardThread.info(keyboardThread.scenario_sync_info, key="SCENARIO SYNC", alone=True)
                elif cmd[0] == "rtp":
                    keyboardThread.info(keyboardThread.rtp_info, key="REAL TIME PROTOCOL", alone=True)
                elif cmd[0] == "osc":
                    keyboardThread.info(keyboardThread.osc_info, key="OSC", alone=True)
                elif cmd[0] == "scenario":
                    keyboardThread.info(keyboardThread.scenario_info, key="SCENARIO", alone=True)
                elif cmd[0] == "sfsm":
                    keyboardThread.info(keyboardThread.scenario_fsm_info, key="SCENARIO FSM", alone=True)
                elif cmd[0] == "info":
                    log.info()
                    log.info("=== INFO ===")
                    keyboardThread.basic_all_info()
                    keyboardThread.path_info()
                    keyboardThread.scenario_info(info=True)
                    keyboardThread.osc_info(info=True)
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

        # import os, stat
        # mode = os.fstat(0).st_mode
        # if stat.S_ISFIFO(mode):
        #      print "stdin is piped"
        # elif stat.S_ISREG(mode):
        #      print "stdin is redirected"
        # else:
        #      print "stdin is terminal"
	# while True:
        #     try:
        #         c = raw_input("")
        #     except:      # For no shell env
        #         time.sleep(10)
        #         continue
        #     if c in ("q", "Q", "quit", "exit"):
        #         POWEROFF = 1
        #     if c == "":
        #         continue
        #     cmd = c.split()
        #     if cmd[0] == "settings":
        #         log.info(settings)
        #     if cmd[0] == "pw":
        #         log.info(str(POWEROFF))
        #     if cmd[0] == "info":
        #         if scenario.SCENARIO_FSM is not None:
        #             log.info(scenario.SCENARIO_FSM.current_state)
        #         log.info(oscack.protocol.discover.machine.current_state)
        #         log.info(oscack.protocol.scenariosync.machine.current_state)
        #         log.info(oscack.protocol.mediasync.machine.current_state)
        #         log.info("Needed media : {0}".format(oscack.protocol.mediasync.needed_media_list))
        #         log.info("Uneeded media : {0}".format(oscack.protocol.mediasync.unwanted_media_list))
        #         for f in scenario.FSM:
        #             log.info(f.current_state)
        #             log.info(f._flag_stack)
        #         for f in scenario.DEVICE_FSM:
        #             log.info(f.current_state)
        #             log.info(f._flag_stack)
        #         log.info(" = oscack.DNCServer.networkmap : ")
        #         log.info(oscack.DNCserver.networkmap)
        #         log.info(" = oscack.timetag : ")
        #         log.info(oscack.timetag)
        #         log.info(" = oscack.accuracy : ")
        #         log.info(oscack.accuracy)
        #     if cmd[0] == "signal":
        #         if len(cmd) > 1:
        #             if cmd[1] == "testall":
        #                 engine.threads.patcher.patch(flag_all.get())
        #             if cmd[1] == "testgroup":
        #                 engine.threads.patcher.patch(flag_group.get())

