#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#
import sys
import os

from engine import log
log = log.init_log("main")
log.important('=== KXKM - DNC PLAYER ===')

def set_python_path(depth=0):
    f = sys._getframe(1)
    fname = f.f_code.co_filename
    fpath = os.path.dirname(os.path.abspath(fname))
    PythonPath = os.path.join(fpath, "../".join(["" for x in xrange(depth+1)]))
    sys.path.append(PythonPath)
set_python_path(depth=1)


import time
import application
from engine.setting import settings
from engine.log import set_default_log_by_settings
set_default_log_by_settings(settings)                   # Set default log level and output via settings

try:
    application.init()
    application.start()

    try:
        while application.POWEROFF == 0:
            time.sleep(1)
    except KeyboardInterrupt:
        log.debug("KeyboardException received")
        application.POWEROFF = 1
    except Exception as e:
        log.exception("EXITING after exception in MAIN : \n"+log.show_exception(e))

except Exception as e:
    log.exception(log.show_exception(e))
    log.error(e)

application.stop()

log.important('=== EXIT : '+str(application.POWEROFF)+' ===' )
os._exit(application.POWEROFF)
