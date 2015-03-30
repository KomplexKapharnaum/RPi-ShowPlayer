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
log = init_log("test.fsm")

import random

from src import fsm


class unittesttateMachineZeroOne(unittest.TestCase):

    def setUp(self):
        pass

    def test_random_machine(self):
        log.log("info", "== test_random_machine ==")
        def init_function(flag):
            log.info("INIT FUNCTION START !")
        def zero_function(flag):
            log.info("ZERO FUNCTION !")
        def one_function(flag):
            log.info("ONE FUNCTION !")
        zero_flag = fsm.Flag("ZERO_FLAG", TTL=None)
        one_flag = fsm.Flag("ONE_FLAG", TTL=None)
        random_flag = fsm.Flag("RANDOM_FLAG", TTL=None)
        state_init = fsm.State("INIT_STATE", function=init_function)
        state_zero = fsm.State("ZERO_STEP", function=zero_function)
        state_one = fsm.State("ONE_STEP", function=one_function)
        state_init.transitions["ZERO_FLAG"] = state_zero
        state_init.transitions["ONE_FLAG"] = state_one
        machine = fsm.FiniteStateMachine()
        machine.start(state_init)
        r = random.randint(0, 1)
        log.info("Random = {0}".format(r))
        if r == 0:
            machine.append_flag(zero_flag.get())
        else:
            machine.append_flag(one_flag.get())
        time.sleep(0.1)
        machine.stop()
        machine.join()

    def test_random_condition(self):
        log.log("info", "== test_random_condition ==")
        def random_condition(flag):
            if flag.args["rand_value"] == 0:
                return state_zero
            else:
                return state_one
        def init_function(flag):
            log.info("INIT FUNCTION START !")
        def zero_function(flag):
            log.info("ZERO FUNCTION !")
        def one_function(flag):
            log.info("ONE FUNCTION !")
        zero_flag = fsm.Flag("ZERO_FLAG", TTL=None)
        one_flag = fsm.Flag("ONE_FLAG", TTL=None)
        random_flag = fsm.Flag("RANDOM_FLAG", TTL=None)
        state_init = fsm.State("INIT_STATE", function=init_function)
        state_zero = fsm.State("ZERO_STEP", function=zero_function)
        state_one = fsm.State("ONE_STEP", function=one_function)
        state_init.transitions["RANDOM_FLAG"] = random_condition
        machine = fsm.FiniteStateMachine()
        machine.start(state_init)
        r = random.randint(0, 1)
        log.info("Random = {0}".format(r))
        machine.append_flag(random_flag.get(args={"rand_value": r}))
        time.sleep(0.1)
        machine.stop()
        machine.join()

    def test_useless_signal(self):
        log.log("info", "== test_useless_signal ==")
        def init_function(flag):
            log.info("INIT FUNCTION START !")
        def zero_function(flag):
            log.info("ZERO FUNCTION !")
        def one_function(flag):
            log.info("ONE FUNCTION !")
        def switch_function(flag):
            log.info("SWITCH FUNCTION")
        zero_flag = fsm.Flag("ZERO_FLAG", TTL=None)
        one_flag = fsm.Flag("ONE_FLAG", TTL=None, JTL=2)
        switch_flag = fsm.Flag("SWITCH_FLAG", TTL=None)
        state_init = fsm.State("INIT_STATE", function=init_function)
        state_zero = fsm.State("ZERO_STEP", function=zero_function)
        state_one = fsm.State("ONE_STEP", function=one_function)
        state_switch = fsm.State("SWITCH_STATE", function=switch_function)
        state_init.transitions["SWITCH_FLAG"] = state_switch
        state_switch.transitions["ZERO_FLAG"] = state_zero
        state_switch.transitions["ONE_FLAG"] = state_one
        machine = fsm.FiniteStateMachine("New")
        machine.start(state_init)
        time.sleep(0.5)
        machine.append_flag(zero_flag.get())
        time.sleep(3)
        machine.append_flag(one_flag.get())
        machine.append_flag(switch_flag.get())
        time.sleep(0.5)
        machine.stop()
        machine.join()




    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()