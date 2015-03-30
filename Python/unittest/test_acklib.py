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
log.DEFAULT_LEVEL = "info"
log.DEFAULT_LOG_TYPE = "Null"
from src.log import init_log
log = init_log("test.ack", log_type="Console")


from libc import acklib
from OSC import utils


class TestACKDiverse(unittest.TestCase):

    def setUp(self):
        pass

    # def test_encode_uid(self):
    #     log.info("--START-- test_encode_uid")
    #     uidt, uidp = acklib.gen_uids(1782)
    #     uid, port = acklib.decode_uids(uidt, uidp)
    #     start_c = time.clock()
    #     for i in xrange(100000):
    #         acklib.encode_uid(uid)
    #     end_c = time.clock()
    #     start_py = time.clock()
    #     for i in xrange(100000):
    #         utils.encode_uid(uid)
    #     end_py = time.clock()
    #     speed_c = end_c - start_c
    #     speed_py = end_py - start_py
    #     log.info("SPEED C  : %f " % speed_c)
    #     log.info("SPEED PY : %f " % speed_py)
    #     log.info("--END-- test_encode_uid")

    def test_gen_uids_speed(self):
        log.info("--START-- test_gen_uids_speed")
        start_c = time.clock()
        for i in xrange(100000):
            acklib.gen_uids(1782)
        end_c = time.clock()
        start_py = time.clock()
        for i in xrange(100000):
            utils.gen_uids(1782)
        end_py = time.clock()
        speed_c = end_c - start_c
        speed_py = end_py - start_py
        log.info("SPEED C  : %f " % speed_c)
        log.info("SPEED PY : %f " % speed_py)
        log.info("--END-- test_gen_uids_speed")

    def test_gen_uids(self):
        log.info("--START-- test_gen_uids")
        log.info(" acklib.gen_uids() = {0}".format(acklib.gen_uids()))
        log.info("--END-- test_gen_uids")

    # def test_decode_uids(self):
    #     log.info("--START-- test_decode_uids")
    #     uidt, uidp = acklib.gen_uids(1782)
    #     start_c = time.clock()
    #     for i in xrange(100000):
    #         acklib.decode_uids(uidt, uidp)
    #     end_c = time.clock()
    #     start_py = time.clock()
    #     for i in xrange(100000):
    #         utils.decode_uids(uidt, uidp)
    #     end_py = time.clock()
    #     speed_c = end_c - start_c
    #     speed_py = end_py - start_py
    #     log.info("SPEED C  : %f " % speed_c)
    #     log.info("SPEED PY : %f " % speed_py)
    #     log.info("--END-- test_decode_uids")

    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()