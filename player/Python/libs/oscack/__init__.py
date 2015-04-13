# -*- coding: utf-8 -*-

from collections import deque

from libs import rtplib
#import time
from engine.log import init_log
from engine import shared

log = init_log("Osc Ack")

DNCserver = None
discover_machine = None
BroadcastAddress = None
accuracy = -1
timetag = rtplib.get_time()
timetag = int((timetag[0] & 0xFFFF0000 | timetag[1] & 0x0000FFFF))
#timetag = int(round(time.time() * 1000))
sync = shared.SharedVar("sync", "?")
sync.set(False)
ack_threads = {}
broadcast_ack_threads = deque(maxlen=128)

log.debug("Init time tag : {0} ".format(timetag))

from engine.setting import settings

import protocol
import message
import server


def start_protocol():
    global DNCserver, discover_machine, BroadcastAddress
    if not isinstance(DNCserver, server.DNCServer):
        DNCserver = server.DNCServer(settings["uName"], classicport=settings["OSC"]["classicport"],
                                     ackport=settings["OSC"]["ackport"])
    if not DNCserver.started.is_set():
        DNCserver.start()
    BroadcastAddress = message.Address("255.255.255.255")
    discover_machine = protocol.discover.machine
    protocol.discover.machine.start(protocol.discover.step_init)
    protocol.discover.add_flag_send_iamhere()
    sync_machine = protocol.scenariosync.machine
    sync_machine.start(protocol.discover.step_init)


def stop_protocol():
    DNCserver.stop()
    protocol.discover.machine.stop()


# log.info("End Import OSC")
