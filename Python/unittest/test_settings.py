# -*- coding: utf-8 -*-
#
# This file provide unit test for the state machine
#

from platform import python_version
print(python_version())

import sys
import os
import unittest
import time

def set_python_path(depth=0):
    f = sys._getframe(1)
    fname = f.f_code.co_filename
    fpath = os.path.dirname(os.path.abspath(fname))
    PythonPath = os.path.join(fpath, "../".join(["" for x in xrange(depth+1)]))
    sys.path.append(PythonPath)
    print(PythonPath)

set_python_path(depth=1)

from src import log
log.DEFAULT_LEVEL = "raw"
log.DEFAULT_LOG_TYPE = "Console"
from src.log import init_log
log = init_log("test.setting")


from src.setting import settings


class unittestettings(unittest.TestCase):

    # def setUp(self):
    #     threads.init()

    def test_setting(self):
        log.info(settings)

    # def tearDown(self):
    #     log.info("Ask threads to stop..")
    #     threads.stop()
    #     log.info(".. done")


if __name__ == '__main__':
    unittest.main()