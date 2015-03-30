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

set_python_path(depth=2)

from src import log
log.DEFAULT_LEVEL = "raw"
log.DEFAULT_LOG_TYPE = "Both"
from src.log import init_log
log = init_log("test.state")

import random

from src import state


class unittesttateMachineZeroOne(unittest.TestCase):

    def setUp(self):
        pass

    def test_random_machine(self):
        """
        Test random
        :return:
        """
        log.log("info", "== test_random_machine ==")
        def init_function(flag):
            log.info("INIT FUNCTION START !")
        def zero_function(flag):
            log.info("ZERO FUNCTION !")
        def one_function(flag):
            log.info("ONE FUNCTION !")
        zero_flag = state.FlagPattern("ZERO_FLAG", TTL=None)
        one_flag = state.FlagPattern("ONE_FLAG", TTL=None)
        random_flag = state.FlagPattern("RANDOM_FLAG", TTL=None)
        state_init = state.StepPattern("INIT_STATE", function=init_function)
        state_zero = state.StepPattern("ZERO_STEP", function=zero_function)
        state_one = state.StepPattern("ONE_STEP", function=one_function)
        state_init.transitions["ZERO_FLAG"] = state.DirectTransition(state_zero)
        state_init.transitions["ONE_FLAG"] = state.DirectTransition(state_one)
        machine = state.StateMachine()
        machine.add_step(state_init)
        machine.add_step(state_one)
        machine.add_step(state_zero)
        machine.start("INIT_STATE")
        r = random.randint(0, 1)
        log.info("Random = {0}".format(r))
        if r == 0:
            machine.add_flag(zero_flag.get_flag())
        else:
            machine.add_flag(one_flag.get_flag())
        time.sleep(0.1)
        machine.stop()

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
        zero_flag = state.FlagPattern("ZERO_FLAG", TTL=None)
        one_flag = state.FlagPattern("ONE_FLAG", TTL=None)
        random_flag = state.FlagPattern("RANDOM_FLAG", TTL=None)
        state_init = state.StepPattern("INIT_STATE", function=init_function)
        state_zero = state.StepPattern("ZERO_STEP", function=zero_function)
        state_one = state.StepPattern("ONE_STEP", function=one_function)
        state_init.transitions["RANDOM_FLAG"] = random_condition
        machine = state.StateMachine()
        machine.add_step(state_init)
        machine.add_step(state_one)
        machine.add_step(state_zero)
        machine.start("INIT_STATE")
        r = random.randint(0, 1)
        log.info("Random = {0}".format(r))
        machine.add_flag(random_flag.get_flag(args={"rand_value": r}))
        time.sleep(0.1)
        machine.stop()


    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()