# -*- coding: utf-8 -*-
#
#
# This file provide some Etapes which are accessible from the scenario scope
#
#

from scenario.classes import Etape
from engine.fsm import Flag
from scenario import functions
from engine.log import init_log

log = init_log("etapes")


def main_device_control(flag, **kwargs):
    """
    This function provide main control on the device
    :param flag:
    :param kwargs:
    :return:
    """
    log.debug("=> Device control : {0}".format(flag.args["args"][0]))
    if flag.args["args"][0] == "reboot_manager":
        log.log("raw", "call reboot_manager")
        functions.reboot_manager()


etape_main_device_manager_wait = Etape("MAIN_DEVICE_MANAGER_WAIT")
etape_main_device_manager_control = Etape("MAIN_DEVICE_MANAGER_CONTROL", actions=((main_device_control, {}), ))

signal_device_control = Flag("MAIN_DEVICE_CONTROL")

etape_main_device_manager_wait.transitions = {
    signal_device_control.uid: etape_main_device_manager_control
}

etape_main_device_manager_control.transitions = {
    None: etape_main_device_manager_wait
}
