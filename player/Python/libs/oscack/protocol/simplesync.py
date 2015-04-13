# -*- coding: utf-8 -*-
#
#
# This module provide a simple sync protocol
#   It's sync media and scenario
#

from libs import oscack
from engine import fsm
from engine.setting import settings
from engine.log import init_log


log = init_log("sync")

machine = fsm.FiniteStateMachine(name="simplesync")



