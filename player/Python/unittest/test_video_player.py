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
log = init_log("test.video")


from src import threads
from src.modules import video


class TestParsingScenario(unittest.TestCase):

    def setUp(self):
        threads.init()

    # def test_simpliest_machine(self):
    #     parsing.parse_scenario("data/exemple_scenario_random.json")
    #     machine = classes.ScenarioFSM("MainFSM")
    #     machine.start(pool.Etapes_and_Functions["INIT_ETAPE"])
    #     r = random.randint(0, 1)
    #     log.info("Random = {0}".format(r))
    #     if r == 0:
    #         machine.append_flag(pool.Signals["ZERO_FLAG"].get())
    #     else:
    #         machine.append_flag(pool.Signals["ONE_FLAG"].get())
    #     time.sleep(0.1)
    #     machine.stop()
    #     machine.join()

    # def test_scenario_complet(self):
    #     parsing.parse_scenario("data/exemple_scenario_complet.json")
    #     managefsm = fsm.FiniteStateMachine("Manager")
    #     managefsm.start(manager.step_init)
    #     pool.MANAGER = managefsm
    #     managefsm.append_flag(manager.start_flag.get())
    #     time.sleep(6)
    #     managefsm.stop()
    #     managefsm.join()
    #     for sfsm in pool.FSM:
    #         sfsm.stop()
    #         sfsm.join()
    #     log.info("Ending Manager")

    def test_video_omx(self):
        try:
            video_player = video.OMXVideoPlayer(path="video/LYON_jeanjack_illustr_marche.mp4")
            video_player.start()
        except Exception as e:
            log.error(e)
        while True:
            c = raw_input("$ :")
            if c in ("stop", "q", "quit", "exit"):
                video_player.stop()
                break
        video_player.join()

    def test_video_hplayer(self):
        try:
            video_player = video.HVideoPlayer(path="video/LYON_jeanjack_illustr_marche.mp4")
            video_player.start()
        except Exception as e:
            log.error(e)
        while True:
            c = raw_input("$ :")
            if c in ("stop", "q", "quit", "exit"):
                video_player.stop()
                break
            elif c == "pause":
                video_player.pause()
            elif c == "resume":
                video_player.resume()
        video_player.join()

    def tearDown(self):
        log.info("Ask threads to stop..")
        threads.stop()
        log.info(".. done")


if __name__ == '__main__':
    unittest.main()