#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#
import sys
import os

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
from engine import log, fsm, threads
from scenario import pool
from libs import oscack
log = log.init_log("main")


try:
    application.init()
    application.start()

    while application.POWEROFF == 0:
        time.sleep(1)

except Exception as e:
    log.exception(log.show_exception(e))
    log.error(e)

application.stop()

log.log('info', 'PowerOff : '+str(application.POWEROFF) )
os._exit(application.POWEROFF)
