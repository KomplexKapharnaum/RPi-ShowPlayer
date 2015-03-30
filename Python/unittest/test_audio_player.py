# -*- coding: utf-8 -*-
#
# This file provide unit test for shared page system
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

from src.setting import settings
from src import log
log.DEFAULT_LEVEL = settings.get("log", "level")
log.DEFAULT_LOG_TYPE = settings.get("log", "output")
from src.log import init_log
log = init_log("main", log_lvl="raw", log_type="Console")


class TestParsingScenario(unittest.TestCase):

    def test_create_write_read(self):
        """
        This the main test, wich just run the discover protocol
        :return:
        """




if __name__ == '__main__':
    try:
        unittest.main()
    except Exception:
        pass
    finally:
        pass