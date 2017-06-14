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
log = init_log("test.rtp")

import random
from collections import deque

from libc import rtplib


NS = 1000000000
reach_acc = int(0.005 * NS)

class Testrtplib(unittest.TestCase):

    def setUp(self):
        self.q = deque(maxlen=5)

    def test_accuracy_error(self):
        self.q.append(int(0.012 * NS))
        dt, acc = rtplib.accuracy_dt(reach_acc, tuple(self.q))
        self.assertEqual(dt, -1)

    def test_accuracy_equal(self):
        self.q.append(int(0.012 * NS))
        self.q.append(int(0.012 * NS))
        self.q.append(int(0.012 * NS))
        self.q.append(int(0.012 * NS))
        dt, acc = rtplib.accuracy_dt(reach_acc, tuple(self.q))
        self.assertEqual(dt, 0.012 * NS)
        self.assertEqual(acc, 0)

    def test_accuracy_1(self):
        self.q.append(int(0.012345 * NS))
        self.q.append(int(0.011454 * NS))
        self.q.append(int(0.01356 * NS))
        self.q.append(int(0.01323 * NS))
        dt, acc = rtplib.accuracy_dt(reach_acc, tuple(self.q))
        log.info("Dt : {0}, acc : {1}".format(dt, acc))
        self.assertEqual(dt, 12424500)
        self.assertEqual(acc, 2106000)

    def test_accuracy_rand_short(self):
        global reach_acc
        reach = reach_acc
        basic = 0.00555 * NS
        min_err = int(0.02 * NS)
        n = 1
        while True:
            self.q.append(int(basic+random.randint(0, min_err)))
            dt, acc = rtplib.accuracy_dt(reach, tuple(self.q))
            if dt == -1:
                if acc == 0:
                    continue
                else:
                    n += 1
                    reach = int(reach * 1.02)
            else:
                log.info("Dt : {0}, acc : {1}, reach_acc {2} on {3} tries".format(dt, acc, reach, n))
                break





    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()