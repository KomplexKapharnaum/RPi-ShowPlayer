
# -*- coding: utf-8 -*-
#
#
# This file provide some Etapes which are accessible from the scenario scope
#
#

import liblo
import time
import application
import subprocess
import scenario
from modules import link
from _classes import module
from engine import tools
from engine.log import init_log
from engine.setting import settings,devicesV2
from engine.media import load_scenario_from_fs
log = init_log("devicecontrol")


@module('DeviceControl')
@link({"/device/reload": "device_do_reload",
       "/device/do_reload": "device_do_reload",
        "/device/poweroff": "device_poweroff",
        "/device/reboot": "device_reboot",
        "/device/restart": "device_restart",
        "/device/updatesys": "device_update_system",
        "/device/wifi/restart": "device_restart_wifi",
        "FS_TIMELINE_UPDATED": "device_do_reload",
        "/device/sendInfoTension": "device_send_info_tension",
        "/device/senWarningTension": "device_send_warning_tension"})

def device_control(flag, **kwargs):
    pass


@link({None: "device_control"})
def device_do_reload(flag, **kwargs):
    application.reload()

@link({None: "device_control"})
def device_send_restart(flag, **kwargs):
    """
    This function send a restart signal to all members of the current group
    """
    flag = fsm.Flag("DEVICE_DO_RESTART")
    threads.patcher.patch(flag.get(args={"dest": "Group"}))

@link({None: "device_control"})
def device_restart(flag, **kwargs):
    time.sleep(0.5)
    application.POWEROFF = 1

@link({None: "device_control"})
def device_poweroff(flag, **kwargs):
    application.POWEROFF = 2

@link({None: "device_control"})
def device_reboot(flag, **kwargs):
    application.POWEROFF = 3

@link({None: "device_control"})
def device_restart_wifi(flag, **kwargs):
    tools.restart_netctl()

@link({None: "device_control"})
def device_update_system(flag, **kwargs):
    tools.update_system()

@link({None: "device_reload"})
def device_update_timeline(flag, **kwargs):
    log.debug("Updating timeline ...")
    load_scenario_from_fs(settings["current_timeline"])

@link({None: "device_control"})
def device_send_info_tension(flag, **kwargs):
    cpu_temperature = 0
    link_signal = "no signal"
    link_channel = "no channel"
    with open("/sys/class/thermal/thermal_zone0/temp") as file:
        cpu_temperature = float(file.read())/1000
    link = subprocess.check_output(['iw', 'wlan0', 'link'])
    links = link.splitlines()
    for line in links:
        if "signal:" in line:
            link_signal=line
    link = subprocess.check_output(['iw', 'wlan0', 'info'])
    links = link.splitlines()
    for line in links:
        if "channel" in line:
            link_channel = line
    power = "undefined power"
    if settings.get("uName") in devicesV2:
        power = devicesV2.get(settings.get("uName"), "tension")
    message = liblo.Message("/monitor", settings.get("uName"),
                            settings.get("current_timeline"), scenario.pool.timeline_version, scenario.pool.Frames[scenario.CURRENT_SCENE_FRAME].name,
                            cpu_temperature,
                            link_channel, link_signal,
                            power, float(flag.args["args"][0]))
    #TODO add curent scene name
    log.debug("monitoring send {0}".format(message))
    port = settings.get("log", "tension", "port")
    for dest in settings.get("log", "tension", "ip"):
        liblo.send(liblo.Address(dest, port), message)

@link({None: "device_control"})
def device_send_warning_tension(flag, **kwargs):
    message = liblo.Message("/warningTension",settings.get("uName"))
    log.debug("get warning tension and forward")
    port = settings.get("log","tension","port")
    for dest in settings.get("log","tension","ip"):
        liblo.send(liblo.Address(dest,port),message)




# 'TELECO_MESSAGE_BLINKGROUP': [],
# 'TELECO_MESSAGE_TESTROUTINE': ['testRoutine']


# @globaletape("DEVICE_MANAGER_CONTROL", {
#                 None: "DEVICE_MANAGER"})
# def main_device_control(flag, **kwargs):
#     """
#     This function provide main control on the device
#     :param flag:
#     :param kwargs:
#     :return:
#     """
#     log.debug("=> Device control : {0}".format(flag.args["args"][0]))
#     if flag.args["args"][0] == "reboot_manager":
#         log.log("raw", "call reboot_manager")
#         functions.reboot_manager()
