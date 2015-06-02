
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
from engine import tools, threads, fsm
from engine.log import init_log
from engine.setting import settings, devicesV2
from engine.media import load_scenario_from_fs
log = init_log("devicecontrol")

TENSION = 0

@module('DeviceControl')
@link({"/device/reload": "device_reload",
       "/device/do_reload": "device_reload",
        "/device/poweroff": "device_poweroff",
        "/device/reboot": "device_reboot",
        "/device/restart": "device_restart",
        "/device/updatesys": "device_update_system",
        "/device/wifi/restart": "device_restart_wifi",
        "FS_TIMELINE_UPDATED": "device_restart",         # TODO : replace by device_update_timeline, but seems broken...
        "/device/updateTension": "device_update_tension",
        "/device/info": "device_send_info",
        "/device/warningTension": "device_send_warning_tension"})

def device_control(flag, **kwargs):
    pass


@link({None: "device_control"})
def device_reload(flag, **kwargs):
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
def device_send_info(flag, **kwargs):
    cpu_temperature = 0
    link_signal = "no signal"
    link_channel = "no channel"
    power = "-"
    scene_name = "NoScene"

    # TEMPERATURE
    try:
        with open("/sys/class/thermal/thermal_zone0/temp") as file:
            cpu_temperature = float(file.read())/1000
    except:
        log.warning('Can\'t retrieve temperature')

    # BRANCH
    try:
        branch = subprocess.check_output(['git', 'branch'])
        branch = branch.split('*')[1].rstrip().split((' '))[0]
    except:
        log.warning('Can\'t retrieve branch')

    # WIFI SIGNAL
    try:
        link = subprocess.check_output(['iw', 'dev', 'wlan0', 'link'])
        links = link.splitlines()
        for line in links:
            if "signal:" in line:
                link_signal=line
    except:
        log.warning('Can\'t retrieve Wlan0 signal power (iw dev wlan0 link)')

    # WIFI CHANNEL
    try:
        link = subprocess.check_output(['iw', 'dev', 'wlan0', 'info'])
        links = link.splitlines()
        for line in links:
            if "channel" in line:
                link_channel = line
    except:
        log.warning('Can\'t retrieve Wlan0 channel (iw dev wlan0 info)')

    # TENSION
    if settings.get("uName") in devicesV2:
        power = devicesV2.get(settings.get("uName"), "tension")

    # SCENE
    if len(scenario.pool.Frames) >= scenario.CURRENT_SCENE_FRAME + 1:
        scene_name = scenario.pool.Frames[scenario.CURRENT_SCENE_FRAME].name
    
    # MESSAGE
    message = liblo.Message("/monitor", settings.get("uName"),
                            settings.get("current_timeline"), scenario.pool.timeline_version, scene_name,
                            cpu_temperature,
                            link_channel, link_signal,
                            power, TENSION, branch)

    log.raw("monitoring send {0}".format(message))
    tools.send_monitoring_message(message)


@link({None: "device_send_info"})
def device_update_tension(flag, **kwargs):
    if len(flag.args["args"]) > 0:
        global TENSION
        TENSION = float(flag.args["args"][0])


@link({None: "device_control"})
def device_send_warning_tension(flag, **kwargs):
    message = liblo.Message("/warningTension",settings.get("uName"))
    log.debug("get warning tension and forward")
    tools.send_monitoring_message(message)


