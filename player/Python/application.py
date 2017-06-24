##################
# MAIN APPLICATION
##################

import os
import pprint

from engine.setting import settings
from engine.log import set_default_log_by_settings
set_default_log_by_settings(settings)                   # Set default log level and output via settings

import engine
from engine import fsm, alsa
import scenario
import modules
import modules.scenecontrol
import scenario.patcher
from libs import oscack
log = engine.log.init_log("application")

import threading
import time


POWEROFF = False    # 1: STOP PROGRAM   2: POWEROFF AFTER STOP  3: REBOOT AFTER STOP

log_fnct = log.important


def init(autoload=True):
    # LOAD INPUT KEYBOARD THREAD
    k = inputThread()
    k.start()
    # SET SYSTEM VOLUME
    alsa.set_absolute_amixer()
    alsa.set_alsaequal_profile()
    # INIT THREADS
    engine.init()
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
    # ENGINE START
    engine.start()
    # START POOL
    scenario.start()


def stop():
    log.info("Stop Scenario")
    scenario.stop()
    log.info("Stop OscAck")
    oscack.stop_protocol()
    log.info("Stop Engine & Threads")
    engine.stop()

def restart():
    stop()
    init()
    start()


class inputThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        engine.tools.register_thread(self)
        self._stop = threading.Event()

    def stop(self):
        self._stop.set()

    @staticmethod
    def basic_all_info():
        if not settings.correctly_load:
            log.warning("/!\\ SETTINGS NOT CORRECTLY LOADED /!\\ ")
        log_fnct("uName : {0}, Team : {1}".format(settings["uName"], settings["current_timeline"]))

    @staticmethod
    def path_info():
        log_fnct("--- PATH ---")
        log_fnct("DNC path : {0}".format(settings.get("path", "main")))
        log_fnct("Media path : {0}".format(settings.get_path("media")))
        log_fnct("Scenario path : {0}".format(settings.get_path("media")))
        log_fnct("------------")

    @staticmethod
    def in_info(key="INFO"):
        log_fnct()
        log_fnct("=== {key} ===".format(key=key))

    @staticmethod
    def out_info(key="INFO"):
        log_fnct("=== END {key} ===".format(key=key))
        log_fnct()

    @staticmethod
    def info(fnct, key="INFO", *args, **kwargs):
        inputThread.in_info(key)
        fnct(*args, **kwargs)
        inputThread.out_info(key)

    @staticmethod
    def osc_info(alone=False, info=False):
        if not alone:
            log_fnct("--- OSC ---")
        if alone or info:
            inputThread.basic_osc_info(alone)
        inputThread.media_sync_info()
        inputThread.scenario_sync_info()
        inputThread.rtp_info()
        if not alone:
            log_fnct("-----------")

    @staticmethod
    def basic_osc_info(alone=True):
        if alone:
            inputThread.basic_all_info()
        log_fnct("OSC port : {0}, ACK port : {1}".format(settings.get("OSC", "classicport"), settings.get("OSC", "ackport")))

    @staticmethod
    def media_sync_info(alone=False):
        if alone:
            inputThread.basic_osc_info()
        log_fnct(oscack.protocol.mediasync.machine)
        log_fnct("All media : {0}".format(engine.media.get_all_media_list()))
        log_fnct("Needed media : {0}".format(oscack.protocol.mediasync.needed_media_list))
        log_fnct("Uneeded media : {0}".format(oscack.protocol.mediasync.unwanted_media_list))

    @staticmethod
    def scenario_sync_info(alone=False):
        if alone:
            inputThread.basic_osc_info()
        log_fnct(oscack.protocol.scenariosync.machine)

    @staticmethod
    def rtp_info(alone=False):
        if alone:
            inputThread.basic_osc_info()
        log_fnct(oscack.protocol.discover.machine)
        log_fnct(" = oscack.DNCServer.networkmap : {0} ".format(oscack.DNCserver.networkmap))
        log_fnct(" = oscack.timetag : {0} ".format(oscack.timetag))
        log_fnct(" = oscack.accuracy : {0} ".format(oscack.accuracy))

    @staticmethod
    def basic_scenario_info(alone=True):
        if alone:
            inputThread.basic_all_info()

    @staticmethod
    def scenario_info(alone=False, info=False):
        if alone or info:
            inputThread.basic_scenario_info(alone)
        inputThread.scenario_fsm_info()

    @staticmethod
    def scenario_fsm_info(alone=False):
        if alone:
            inputThread.basic_scenario_info()
        if not alone:
            log_fnct("--- SCENARIO FSM ---")

        # if scenario. is not None:
        #     log_fnct(scenario.SCENE_FSM.current_state)
        for f in scenario.MODULES_FSM:
            log_fnct(f.current_state)
            log_fnct(f._flag_stack)
        for f in scenario.SCENE_FSM:
            log_fnct(f.current_state)
            log_fnct(f._flag_stack)

        if not alone:
            log_fnct("--------------------")


    def run(self):
        # DEV
        flag_group = engine.fsm.Flag("TEST_GROUP").get()
        flag_group.args["dest"] = [settings.get("scenario", "dest_group"), ]
        flag_all = engine.fsm.Flag("TEST_ALL").get()
        flag_all.args["dest"] = [settings.get("scenario", "dest_all"), ]
        global POWEROFF
        pretyprinter = pprint.PrettyPrinter(indent=4)
        try:
            while True and not self._stop.is_set():
                try:
                    c = raw_input("")
                except KeyboardInterrupt:
                    POWEROFF = 1
                    log.debug("Keyboard Exception received")
                except Exception:      # For no shell env
                    log.debug("There is no input sleep 10 and continue...")
                    time.sleep(1)
                    continue
                if c in ("r", "rs", "respawn", "reload"):
                    if c == "rs":   # Prompt all fsm history and quit
                        engine.perf.all_history()
                    POWEROFF = 1
                    break
                if c in ("q", "Q", "quit", "exit", "qs"):
                    if c == "qs":   # Prompt all fsm history and quit
                        engine.perf.all_history()
                    POWEROFF = 0
                    break
                if c == "":
                    continue
                cmd = c.split()
                if cmd[0] == "pw":
                    log_fnct(str(POWEROFF))
                elif cmd[0] == "except":
                    tmpfsm = fsm.FiniteStateMachine("test_fsm")
                    def tmp_fnct(flag):
                        a = 1/0
                    tmpstate = fsm.State("TEST_EXCEPT_STATE", function=tmp_fnct)
                    tmpfsm.start(tmpstate)
                elif cmd[0] == "history":
                    engine.perf.prompt_history()
                elif cmd[0] == "timeline":
                    log_fnct(scenario.pool._Timeline)
                elif cmd[0] == "scene":
                    if len(cmd) > 1 and len(scenario.pool._Timeline) > int(cmd[1]):
                        log_fnct(scenario.pool._Timeline[int(cmd[1])].show_info())
                elif cmd[0] == "move":
                    if len(cmd) > 1:
                        if cmd[1] == "next":
                            flag = engine.fsm.Flag("SCENE_NEXT")
                        elif cmd[1] == "prev":
                            flag = engine.fsm.Flag("SCENE_PREVIOUS")
                        elif cmd[1] == "to":
                            if len(cmd) > 2:
                                flag = engine.fsm.Flag("SCENE_GO")
                                flag.args['frame'] = int(cmd[2])
                        elif cmd[1] == "force":
                            if len(cmd) > 2:
                                modules.scenecontrol.scene_force_to(int(cmd[2]))
                            continue
                        else:
                            continue
                        flag.args['dest'] = list()
                        flag.args['dest'].append("Self")
                        engine.threads.patcher.patch(flag.get())
                elif cmd[0] == "timelinejson":
                    log_fnct(scenario.pool._JSONtimeline)
                elif cmd[0] == "scenariojson":
                    log_fnct(scenario.pool._JSONScenario)
                elif cmd[0] == "mhistory":
                    engine.perf.multiplex_history(cmd[1:])
                elif cmd[0] == "_log":
                    if len(cmd) > 1:
                        engine.tools.log_teleco(" ".join(cmd[1:]))
                elif cmd[0] == "settings":
                    log_fnct()
                    log_fnct("=== SETTINGS ===")
                    to_print = settings
                    if len(cmd) > 1 and cmd[1] in settings.keys():
                        to_print = settings[cmd[1]]
                    log_fnct(pretyprinter.pprint(to_print))
                    log_fnct("=== END SETTINGS ===")
                    log_fnct()
                elif cmd[0] == "msync":
                    inputThread.info(inputThread.media_sync_info, key="MEDIA SYNC", alone=True)
                elif cmd[0] == "ssync":
                    inputThread.info(inputThread.scenario_sync_info, key="SCENARIO SYNC", alone=True)
                elif cmd[0] == "rtp":
                    inputThread.info(inputThread.rtp_info, key="REAL TIME PROTOCOL", alone=True)
                elif cmd[0] == "osc":
                    inputThread.info(inputThread.osc_info, key="OSC", alone=True)
                elif cmd[0] == "scenario":
                    inputThread.info(inputThread.scenario_info, key="SCENARIO", alone=True)
                elif cmd[0] == "sfsm":
                    inputThread.info(inputThread.scenario_fsm_info, key="SCENARIO FSM", alone=True)
                elif cmd[0] == "info":
                    log_fnct()
                    log_fnct("=== INFO ===")
                    inputThread.basic_all_info()
                    inputThread.path_info()
                    inputThread.scenario_info(info=True)
                    inputThread.osc_info(info=True)
                    log_fnct("=== END INFO ===")
                    log_fnct()
                elif cmd[0] == "signal" or cmd[0] == "s":
                    if len(cmd) > 1:
                        if cmd[1] == "testall":
                            engine.threads.patcher.patch(flag_all.get())
                        if cmd[1] == "testgroup":
                            engine.threads.patcher.patch(flag_group.get())
                        else:
                            signal = fsm.Flag(cmd[1])
                            if len(cmd) > 2:
                                if cmd[2].upper() == "GROUP":
                                    signal.args["dest"] = ("Group", )
                                elif cmd[2].upper() == "ALL":
                                    signal.args["dest"] = ("All", )
                            engine.threads.patcher.patch(signal.get())
                            log.info("send signal : {}".format(cmd[1]))
                elif cmd[0] == "teleco":
                    if len(cmd) < 3:
                        log.warning("Need at least a page number an a message")
                        continue
                    engine.tools.log_teleco(cmd[2:], int(cmd[1]))
                elif cmd[0] == "log":
                    if len(cmd) < 3:
                        log.warning("Need at least a page number an a message")
                        continue
                    log.log(cmd[1], " ".join(cmd[2:]))
                elif cmd[0] == "eval":
                    try:
                        eval(" ".join(cmd[1:]))
                    except Exception as e:
                        log_fnct(log.show_exception(e))
                else:
                    log_fnct("Unknown commad in prompt ..")
        except Exception as e:
            log.exception("Unblocking exception in prompt : \n"+log.show_exception(e))
        # BACKUP EXIT
        time.sleep(10)
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

