# -*- coding: utf-8 -*-
#
# This file provide unit test for the state machine
#

from platform import python_version
print(python_version())

import sys
import os
import time

def set_python_path(depth=0):
    f = sys._getframe(1)
    fname = f.f_code.co_filename
    fpath = os.path.dirname(os.path.abspath(fname))
    PythonPath = os.path.join(fpath, "../".join(["" for x in xrange(depth+1)]))
    sys.path.append(PythonPath)
    print(PythonPath)

set_python_path(depth=1)

from src.setting import settings
from src import log
log.DEFAULT_LEVEL = settings.get("log", "level")
log.DEFAULT_LOG_TYPE = settings.get("log", "output")
from src.log import init_log
log = init_log("main")

import OSC
from src import fsm, threads
from src.scenario import parsing, pool
from src.scenario import manager

from libc import rtplib, subprocess32
from src.modules import video, audio


# def test_sound_omx(path, args, types, src):
#     log.info("recv")
#     player = video.OMXVideoPlayer("test_sound.wav", hardware=False, audio=False)
#     player.start()
#     time.sleep(1.500)
#     player._write_fifo("p")
#     time.sleep(1.500)
#     player._write_fifo("i")
#     t = rtplib.get_time()
#     log.info("test_sound current time {0}s {1}ns ".format(t[0], t[1]))
#     log.info("test_sound wanted  time {0}s {1}ns ".format(args[0], args[1]))
#     # BEGIN TIME CRITICAL
#     rtplib.wait_abs_time(args[0], args[1])
#     player._write_fifo("p")
#     # END TIME CRITICAL
#     log.info("release !")
#
#
# def test_sound_aplay(path, args, types, src):
#     log.info("recv")
#     t = rtplib.get_time()
#     log.info("test_sound current time {0}s {1}ns ".format(t[0], t[1]))
#     log.info("test_sound wanted  time {0}s {1}ns ".format(args[0], args[1]))
#     path = os.path.join(settings.get("path", "media"), "test_sound.wav")
#     # BEGIN TIME CRITICAL
#     rtplib.wait_abs_time(args[0], args[1])
#     subprocess32.Popen(["/usr/bin/aplay", "-q", path])
#     # END TIME CRITICAL
#
#
# def test_sound_pygame(path, args, types, src):
#     log.info("recv")
#     t = rtplib.get_time()
#     log.info("test_sound current time {0}s {1}ns ".format(t[0], t[1]))
#     log.info("test_sound wanted  time {0}s {1}ns ".format(args[0], args[1]))
#     path = os.path.join(settings.get("path", "media"), "test_sound.wav")
#     # BEGIN TIME CRITICAL
#     audio.play_sound_at(args[0], args[1], path)
#     # END TIME CRITICAL
#
# def test_nosync_sound_omx(path, args, types, src):
#     log.info("recv")
#     player = video.OMXVideoPlayer("test_sound.wav", hardware=False, audio=False)
#     player.start()
#     log.info("release !")
#
#
# def test_nosync_sound_aplay(path, args, types, src):
#     log.info("recv")
#     path = os.path.join(settings.get("path", "media"), "test_sound.wav")
#     subprocess32.Popen(["/usr/bin/aplay", "-q", path])
#
#
# def test_nosync_sound_pygame(path, args, types, src):
#     log.info("recv")
#     path = os.path.join(settings.get("path", "media"), "test_sound.wav")
#     audio.play_sound(path)
#


try:
    threads.init()
    OSC.start_protocol()
    # OSC.DNCserver.add_method("/test/sync/omx", None, test_sound_omx)
    # OSC.DNCserver.add_method("/test/sync/aplay", None, test_sound_aplay)
    # OSC.DNCserver.add_method("/test/sync/pygame", None, test_sound_pygame)
    # OSC.DNCserver.add_method("/test/nosync/omx", None, test_nosync_sound_omx)
    # OSC.DNCserver.add_method("/test/nosync/aplay", None, test_nosync_sound_aplay)
    # OSC.DNCserver.add_method("/test/nosync/pygame", None, test_nosync_sound_pygame)
    parsing.parse_scenario(os.path.join(settings.get("path", "scenario"), "scenario_sotteville.json"))
    pool.Cartes[settings["uName"]].device.launch_manager()
    managefsm = fsm.FiniteStateMachine("Manager")
    managefsm.start(manager.step_init)
    pool.MANAGER = managefsm
    managefsm.append_flag(manager.start_flag.get())



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
            log.info(OSC.protocol.discover.machine.current_state)
            for f in pool.FSM:
                log.info(f.current_state)
                log.info(f._flag_stack)
            for f in pool.DEVICE_FSM:
                log.info(f.current_state)
                log.info(f._flag_stack)
            log.info(" = OSC.DNCServer.networkmap : ")
            log.info(OSC.DNCserver.networkmap)
            log.info(" = OSC.timetag : ")
            log.info(OSC.timetag)
            log.info(" = OSC.accuracy : ")
            log.info(OSC.accuracy)
        # elif cmd[0] == "test_sync":
        #         if len(cmd) < 3:
        #             prog = "aplay"
        #         else:
        #             prog = cmd[2]
        #         if len(cmd) < 2:
        #             wait = 1
        #         else:
        #             wait = cmd[1]
        #         t = rtplib.get_time()
        #         t = rtplib.add_time(t[0], t[1], float(wait))
        #         OSC.message.send(OSC.BroadcastAddress, OSC.message.Message("/test/sync/"+str(prog), t[0], t[1], ACK=True))
        # elif cmd[0] == "test_nosync":
        #     if len(cmd) < 2:
        #         prog = "aplay"
        #     else:
        #         prog = cmd[1]
        #     OSC.message.send(OSC.BroadcastAddress, OSC.message.Message("/test/nosync/"+str(prog), ACK=True))
        # elif cmd[0] == "resync":
        #     OSC.timetag = 5000
        #     OSC.protocol.discover.machine.append_flag(OSC.protocol.discover.flag_timeout_send_iamhere.get())
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
OSC.stop_protocol()
threads.stop()


