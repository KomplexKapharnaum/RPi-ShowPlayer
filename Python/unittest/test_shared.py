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
from src import shared
from src import log
log.DEFAULT_LEVEL = settings.get("log", "level")
log.DEFAULT_LOG_TYPE = settings.get("log", "output")
from src.log import init_log
log = init_log("main", log_lvl="raw", log_type="Console")


class TestParsingScenario(unittest.TestCase):

    def setUp(self):
        self.writer = shared.SharedPageOneWayWriter("test_mmap")
        self.reader = shared.SharedPageReader("test_mmap")

    def test_create_write_read(self):
        """
        This the main test, wich just run the discover protocol
        :return:
        """
        w_int = self.writer.get_new("v_int", int)
        w_int.value = 1
        self.reader._update_map()
        r_int = self.reader.get_var_by_name("v_int")
        log.info("W_int : {0} , R_int {1}".format(w_int, r_int))
        w_int.value = 10
        log.info("W_int : {0} , R_int {1}".format(w_int, r_int))
        self.assertEqual(r_int, w_int)

    def tearDown(self):
        del self.writer
        del self.reader



if __name__ == '__main__':
    try:
        unittest.main()
    except Exception:
        pass
    finally:
        pass