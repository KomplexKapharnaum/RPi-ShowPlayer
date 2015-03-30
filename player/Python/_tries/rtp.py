# -*- coding: utf-8 -*-
#
#
# This file provide a standalone rtp sync client
#


#
# from platform import python_version
# print(python_version())

import sys
import os

def set_python_path(depth=0):
    f = sys._getframe(1)
    fname = f.f_code.co_filename
    fpath = os.path.dirname(os.path.abspath(fname))
    PythonPath = os.path.join(fpath, "../".join(["" for x in xrange(depth+1)]))
    sys.path.append(PythonPath)
    print(PythonPath)

set_python_path(depth=1)


import OSC
import time

from src import threads
from src.setting import settings
from src import log
log.DEFAULT_LEVEL = settings.get("log", "level")
log.DEFAULT_LOG_TYPE = settings.get("log", "output")
from src.log import init_log
log = init_log("main", log_lvl="debug", log_type="File")

if __name__ == '__main__':
    try:
        threads.init()
        OSC.start_protocol()
        while True:
            try:
                c = raw_input("$ :")
            except Exception as e:      # For no shell env
                time.sleep(10)
                continue
            if c in ("exit", "quit", "q"):
                break
            if c == "":
                continue
            cmd = c.split()
            if cmd[0] == "info":
                log.info(" = OSC.protocol.discover.machine.current_state :")
                log.info(OSC.protocol.discover.machine.current_state)
                log.info(" = OSC.DNCServer.networkmap : ")
                log.info(OSC.DNCserver.networkmap)
                log.info(" = OSC.timetag : ")
                log.info(OSC.timetag)
                log.info(" = OSC.accuracy : ")
                log.info(OSC.accuracy)
            elif cmd[0] == "resync":
                OSC.timetag = 5000
                OSC.protocol.discover.machine.append_flag(OSC.protocol.discover.flag_timeout_send_iamhere.get())
    except Exception:
        pass
    finally:
        OSC.stop_protocol()
        threads.stop()