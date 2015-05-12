# -*- coding: utf-8 -*-
#
# This file load settings and can modify them
# Settings are store in a JSON file
#

import os

# from libc import simplejson as json
# import json
import libs.simplejson as json
from engine.log import init_log
from libs import subprocess32

log = init_log("setting")

DEFAULT_SETTING_PATH = "~/.dnc_settings.json"

DEFAULT_SETTING = dict()
DEFAULT_SETTING["uName"] = subprocess32.check_output(['hostname']).strip()
DEFAULT_SETTING["current_timeline"] = "DEFAULT_TIMELINE"
DEFAULT_SETTING["version"] = '0.2'

DEFAULT_SETTING["localport"] = dict()
DEFAULT_SETTING["localport"]["inhplayer"] = 9000
DEFAULT_SETTING["localport"]["interface"] = 8080

DEFAULT_SETTING["path"] = dict()
DEFAULT_SETTING["path"]["main"] = "/dnc"
#DEFAULT_SETTING["path"]["logs"] = "/dnc/logs"
#DEFAULT_SETTING["path"]["soft"] = os.path.join(DEFAULT_SETTING["path"]["main"], "DNC_Prog")

#DEFAULT_SETTING["path"]["media"] = "/dnc/media"
#DEFAULT_SETTING["path"]["video"] = os.path.join(DEFAULT_SETTING["path"]["media"], 'video')
#DEFAULT_SETTING["path"]["audio"] = os.path.join(DEFAULT_SETTING["path"]["media"], 'audio')
#DEFAULT_SETTING["path"]["text"] = os.path.join(DEFAULT_SETTING["path"]["media"], 'text')
DEFAULT_SETTING["path"]["scp"] = "/usr/bin/scp"
DEFAULT_SETTING["path"]["cp"] = "/usr/bin/cp"
DEFAULT_SETTING["path"]["umount"] = "/usr/bin/umount"
DEFAULT_SETTING["path"]["mount"] = "/usr/bin/mount"
DEFAULT_SETTING["path"]["tmp"] = "/tmp/dnc"
# DEFAULT_SETTING["path"]["usb"] = "/dnc/usb"
# DEFAULT_SETTING["path"]["scenario"] = "/dnc/scenario"
# DEFAULT_SETTING["path"]["activescenario"] = "/dnc/scenario/__active"
DEFAULT_SETTING["path"]["sharedmemory"] = "/var/tmp/"
# DEFAULT_SETTING["path"]["kxkmcard-armv6l"] = "/dnc/player/Hardware/hardware/hardware6"
# DEFAULT_SETTING["path"]["kxkmcard-armv7l"] = "/dnc/player/Hardware/hardware/hardware7"
# DEFAULT_SETTING["path"]["hplayer"] = "/dnc/HPlayer/bin/HPlayer"
DEFAULT_SETTING["path"]["omxplayer"] = "/usr/bin/omxplayer"
DEFAULT_SETTING["path"]["systemctl"] = "/usr/bin/systemctl"
DEFAULT_SETTING["path"]["vlc"] = "/usr/local/bin/cvlc"
DEFAULT_SETTING["path"]["vlcvideo"] = "/usr/local/bin/cvlc --vout mmal_vout --aout alsa -I rc  --no-osd -f "
DEFAULT_SETTING["path"][
    "vlcaudio"] = "/usr/local/bin/cvlc --vout none --aout alsa -I rc --no-osd"  # --no-autoscale --zoom=0.7
DEFAULT_SETTING["path"]["aplay"] = "/usr/bin/aplay"
DEFAULT_SETTING["path"]["amixer"] = "/usr/bin/amixer set PCM"
DEFAULT_SETTING["path"]["mpg123"] = "/usr/bin/mpg123 -C"
# DEFAULT_SETTING["path"]["interface"] = "/dnc/player/Python/interface/bottleserver.py"
# DEFAULT_SETTING["path"]["deviceslist"] = "/dnc/devices.json"

DEFAULT_SETTING["path"]["relative"] = dict()  # Relatives path from path:main
DEFAULT_SETTING["path"]["relative"]["usb"] = "usb"
DEFAULT_SETTING["path"]["relative"]["log"] = "logs"
DEFAULT_SETTING["path"]["relative"]["scenario"] = "scenario"
DEFAULT_SETTING["path"]["relative"]["activescenario"] = "__active"
DEFAULT_SETTING["path"]["relative"]["codepy"] = "player/Python"
DEFAULT_SETTING["path"]["relative"]["kxkmcard-armv6l"] = "player/Hardware/hardware/hardware6"
DEFAULT_SETTING["path"]["relative"]["kxkmcard-armv7l"] = "player/Hardware/hardware/hardware7"
DEFAULT_SETTING["path"]["relative"]["hplayer"] = "player/HPlayer/bin/HPlayer"
DEFAULT_SETTING["path"]["relative"]["interface"] = "player/Python/interface/bottleserver.py"
DEFAULT_SETTING["path"]["relative"]["mvlc"] = "player/Multimedia/HPlayer-vlc/hplayer-vlc "
DEFAULT_SETTING["path"]["relative"]["mvlc"] += \
    "--vout {vout} --aout {aout} --rt-priority --rt-offset {priority} --file-caching {fcache}"
DEFAULT_SETTING["path"]["relative"]["mvlc"] += \
    "--no-keyboard-events --no-mouse-events --audio-replay-gain-mode none --no-volume-save --volume-step {vstep}"
DEFAULT_SETTING["path"]["relative"]["mvlc"] += \
    "--gain {gain} --no-a52-dynrng --alsa-gain {again}"
DEFAULT_SETTING["path"]["relative"]["deviceslist"] = "devices.json"
DEFAULT_SETTING["path"]["relative"]["media"] = "media"
DEFAULT_SETTING["path"]["relative"]["video"] = "video"
DEFAULT_SETTING["path"]["relative"]["audio"] = "audio"
DEFAULT_SETTING["path"]["relative"]["text"] = "text"
DEFAULT_SETTING["path"]["relative"]["logs"] = "logs"

DEFAULT_SETTING["vlc"] = dict()
DEFAULT_SETTING["vlc"]["options"] = dict()
DEFAULT_SETTING["vlc"]["options"]["default"] = {
    "vout": "none",
    "aout": "alsa",
    "priority": -20,
    "fcache": 600,
    "vstep": 25,
    "gain": 1,
    "again": 1
}
DEFAULT_SETTING["vlc"]["options"]["audio"] = {
    "vout": "none"
}
DEFAULT_SETTING["vlc"]["options"]["video"] = {
    "vout": "mmal_vout"
}

DEFAULT_SETTING["vlc"]["volume"] = dict()
DEFAULT_SETTING["vlc"]["volume"]["master"] = 256        # Master volume for VLC (256 seems to be the 100% volume)

DEFAULT_SETTING["sync"] = dict()
DEFAULT_SETTING["sync"]["scp"] = dict()
DEFAULT_SETTING["sync"]["scp"]["recv"] = False  # Active or not the scp commande getting media on the network
DEFAULT_SETTING["sync"]["scp"]["send"] = True  # Active or not the sending of media ist
DEFAULT_SETTING["sync"]["video"] = True  # Explain if the scyn protocol must sync video or not
DEFAULT_SETTING["sync"]["media"] = True  # GLOBAL Put False to disable only media sync
DEFAULT_SETTING["sync"]["usb"] = True  # GLOBAL Put False to disable USB copy
DEFAULT_SETTING["sync"]["scenario"] = True  # GLOABL Put False to disable only scenario sync
DEFAULT_SETTING["sync"]["rtp"] = True  # GLOBAL Put False to disable RTP
DEFAULT_SETTING["sync"]["enable"] = True  # GLOBAL Put False to disable sync
DEFAULT_SETTING["sync"]["flag_timestamp"] = 0  # flag_timestamp
DEFAULT_SETTING["sync"]["max_scenario_sync"] = 5  # Max scenario of the same group to be sync
DEFAULT_SETTING["sync"]["scenario_sync_timeout"] = 60  # 180 seconds
DEFAULT_SETTING["sync"]["escape_scenario_dir"] = "__"  # 3 seconds
DEFAULT_SETTING["sync"]["usb_mount_timeout"] = 5  # 5 seconds max for mounting/unmounting usb device
DEFAULT_SETTING["sync"]["netctl_autorestart"] = False  # 5 seconds max for mounting/unmounting usb device
DEFAULT_SETTING["sync"]["usb_speed_min"] = 5000  # (Ko/s) Behind 5 Mo/s it's not intresting to usb usb sync
DEFAULT_SETTING["sync"]["scp_speed_min"] = 500  # (Ko/s) Behind 100 Ko/s it's too slow for scp
DEFAULT_SETTING["sync"]["protected_space"] = 20000  # (Ko) Space protected to keep the rest of the project safe
DEFAULT_SETTING["sync"]["timeout_wait_syncflag"] = 3  # Wait 3 sec, if no newer flag, we are update
DEFAULT_SETTING["sync"]["timeout_rm_mountpoint"] = 2  # 2 sec before remove mount point
DEFAULT_SETTING["sync"]["timeout_restart_netctl"] = 15  # 15 sec before restart netctl after unplug usb storage device
DEFAULT_SETTING["sync"]["timeout_media_version"] = 360  # 180 sec between each send media list version
DEFAULT_SETTING["sync"]["scp_options"] = "-p -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no"  # -p useless

DEFAULT_SETTING["managers"] = ['DeviceControl', 'SceneControl', 'WebInterface', 'KxkmCard']

DEFAULT_SETTING["scenario"] = dict()
DEFAULT_SETTING["scenario"]["date_format"] = "%Y-%m-%d_%H:%M:%S"
DEFAULT_SETTING["scenario"]["date_len"] = 24  # extension + date length + @
DEFAULT_SETTING["scenario"]["dest_all"] = "All"  # string for all dest in a signal
DEFAULT_SETTING["scenario"]["dest_group"] = "Group"  # string for group dest in a signal
DEFAULT_SETTING["scenario"]["dest_self"] = "Self"  # string for self dest in a signal
DEFAULT_SETTING["scenario"]["play_sync_delay"] = 0.800  # 500 ms : time delta before run sync between cards, if sync
DEFAULT_SETTING["scenario"]["TTL"] = 1.5                # TTL default value for scenario
DEFAULT_SETTING["scenario"]["JTL"] = 3                  # JTL default value for scenario
# fail try to increase this value

DEFAULT_SETTING["media"] = dict()
DEFAULT_SETTING["media"]["automove"] = "yes"
DEFAULT_SETTING["media"]["usb_mount_timeout"] = 3  # 3 sec max for mount before killing it

DEFAULT_SETTING["OSC"] = dict()
DEFAULT_SETTING["OSC"]["iamhere_interval"] = 15
DEFAULT_SETTING["OSC"]["checkneighbour_interval"] = 130
DEFAULT_SETTING["OSC"]["classicport"] = 1781
DEFAULT_SETTING["OSC"]["ackport"] = 1782
DEFAULT_SETTING["OSC"]["TTL"] = 1
DEFAULT_SETTING["OSC"]["JTL"] = 1

DEFAULT_SETTING["rtp"] = dict()
DEFAULT_SETTING["rtp"]["enable"] = True  # Put False to unactive rtp
DEFAULT_SETTING["rtp"]["timeout"] = 5
DEFAULT_SETTING["rtp"]["stack_length"] = 3  # TODO this setting is useless, it's hard written in rtplib.c
DEFAULT_SETTING["rtp"]["accuracy_start_ns"] = 3000000  # 3 ms
DEFAULT_SETTING["rtp"]["accuracy_max_ns"] = 12000000  # 12 ms
DEFAULT_SETTING["rtp"]["accuracy_factor"] = 1.05  # 5% per try

DEFAULT_SETTING["ack"] = dict()
DEFAULT_SETTING["ack"]["stack_recv"] = 256
DEFAULT_SETTING["ack"]["interval_critical"] = (0.010, 0.015, 0.020, 0.025, 0.050, 0.100, 0.100, 0.100, 0.100, 0.100)
DEFAULT_SETTING["ack"]["interval_classical"] = (0.30, 0.50, 0.50, 0.50, 0.50, 0.100, 0.100, 0.100, 0.100, 0.250, 0.250)
DEFAULT_SETTING["ack"]["interval_protocol"] = (0.75, 0.100, 0.125, 0.200, 0.500)
DEFAULT_SETTING["ack"]["interval_short"] = (0.100, 0.150, 0.200)
DEFAULT_SETTING["ack"]["interval_default"] = (0.75, 0.100, 0.125, 0.200, 0.500)

DEFAULT_SETTING["values"] = dict()  # Dictionary for default values
DEFAULT_SETTING["values"]["gyro"] = dict()
DEFAULT_SETTING["values"]["gyro"]["speed"] = 200
#DEFAULT_SETTING["values"]["gyro"]["strob"] = 0
DEFAULT_SETTING["values"]["lights"] = dict()
DEFAULT_SETTING["values"]["lights"]["fade"] = 0
DEFAULT_SETTING["values"]["lights"]["strob"] = 0

DEFAULT_SETTING["log"] = dict()
DEFAULT_SETTING["log"]["level"] = "debug"
DEFAULT_SETTING["log"]["output"] = "Console"
DEFAULT_SETTING["log"]["symb"] = dict()
DEFAULT_SETTING["log"]["symb"]["tension"] = "T"
DEFAULT_SETTING["log"]["symb"]["media"] = "M"
DEFAULT_SETTING["log"]["symb"]["rtp"] = "R"
DEFAULT_SETTING["log"]["symb"]["error"] = "E"
DEFAULT_SETTING["log"]["symb"]["scenario"] = "S"
DEFAULT_SETTING["log"]["symb"]["git"] = "G"
DEFAULT_SETTING["log"]["tension"] = dict()
DEFAULT_SETTING["log"]["tension"]["port"] = 1783
DEFAULT_SETTING["log"]["tension"]["ip"] = ["255.255.255.255"]
DEFAULT_SETTING["log"]["tension"]["active"] = True  # Active the propagation of info tension
DEFAULT_SETTING["log"]["teleco"] = dict()
DEFAULT_SETTING["log"]["teleco"]["active"] = False  # Unactive log teleco
DEFAULT_SETTING["log"]["teleco"]["error_delay"] = 1.5  # Block 1.5 s for assure error displaying
DEFAULT_SETTING["log"]["teleco"]["autoscroll"] = 3  # Block 1.5 s before displaying an other message
DEFAULT_SETTING["log"]["teleco"]["linelength"] = 16  # Number of char per line
DEFAULT_SETTING["log"]["teleco"]["level"] = "warning"  # For the teleco

DEFAULT_SETTING["perf"] = dict()
DEFAULT_SETTING["perf"]["enable"] = True  # Enable FSM register (need for history)
DEFAULT_SETTING["perf"]["history"] = dict()
DEFAULT_SETTING["perf"]["history"]["enable"] = True  # Enable log history for each FSM
DEFAULT_SETTING["perf"]["history"]["withflag"] = True  # Enable flag log in history
DEFAULT_SETTING["perf"]["history"]["withexception"] = True  # Enable excpetion log in history
DEFAULT_SETTING["perf"]["history"]["length"] = 300  # Maximum length of an FSM history (keep older)
DEFAULT_SETTING["perf"]["history"]["format"] = "simple"  # History prompt format #TODO
DEFAULT_SETTING["perf"]["undeclared_fsm"] = 10  # Undeclared FSM (stopped) to be keept with history

DEFAULT_SETTING["sys"] = dict()
DEFAULT_SETTING["sys"]["raspi"] = True  # This settings is for debug, if raspi is False it will prevent pc for error
DEFAULT_SETTING["sys"]["ref_volume"] = 0  # Set the default system volume to 0dB (no negative !)
DEFAULT_SETTING["sys"]["volume"] = 0  # Set the volume difference with the reference (in dB) can be neg
DEFAULT_SETTING["sys"]["vlc_volume"] = 512  # Default vlc volume. 512 = 100%

DEFAULT_SETTING["speed"] = dict()
DEFAULT_SETTING["speed"]["thread_check_interval"] = 0.1  # Check thread interval

DEFAULT_SETTING["temp"] = dict()  # TEMP SETTINGS FOR TEST
DEFAULT_SETTING["temp"]["wanted_media"] = ["text/blabla.txt", "drums.wav", "sintel.mp4", "drums.mp3", "mistake.mp3"]


class Settings(dict):
    """
    This class old settings
    """

    def __init__(self, path):
        """
        :param path: path to the settings file
        :return:
        """
        self._path = path
        self.correctly_load = None
        dict.__init__(self, DEFAULT_SETTING)
        try:
            with open(path, 'r') as fp:
                try:
                    self.update(json.load(fp))
                    log.info("Settings loaded from {0}".format(path))
                    self.correctly_load = True
                except Exception as e:
                    log.error("Could not load settings at {0}".format(path))
                    log.exception(log.show_exception(e))
                    self.correctly_load = False
        except IOError:
            log.info("No settings found at path {0}, create one".format(path))
            with open(path, 'wr') as fp:
                Settings.__init__(self)  # Restart loading settings
        except json.scanner.JSONDecodeError as e:
            log.error("Could not load settings : {0}".format(e))
            self.correctly_load = False

    def save(self):
        return self._save(self._path, "w")

    def save_as(self, path):
        return self._save(path, "a")

    def _save(self, path, mode):
        with open(path, mode) as fp:
            json.dump(self, fp)

    def __getitem__(self, item):
        if item not in self.keys():
            return DEFAULT_SETTING[item]
        return dict.__getitem__(self, item)

    @staticmethod
    def get_default(*args):
        """
        Return the default value, act as get but for the default dictionnarie
        :param args:
        :return:
        """
        global DEFAULT_SETTING
        d = DEFAULT_SETTING
        for elem in args:
            d = d[elem]
        return d

    def get(self, *args):
        """
        Return the correct value
        :param args: path to the setting (ex: ("OSC", "ackport"))
        :return:
        """
        if args[0] == "path" and len(args) > 1 and args[1] != "relative" and args[1] in self.get("path",
                                                                                                 "relative").keys():
            log.warning("Depreciated : use relative path with get_path(*args) instead. [called with {0}] ".format(args))
        d = self
        for elem in args:
            if elem in d.keys():
                d = d[elem]
            else:
                return Settings.get_default(*args)
        return d

    def set(self, *args):
        """
        Set a value to the settings and save it
        :param args: path to the settings, and last is value ( "log", "teleco", "level", "debug" )
        :return:
        """
        args = list(args)
        value = args.pop()
        d = self
        for elem in args[0:-1]:
            if elem not in d.keys():
                d[elem] = dict()
            d = d[elem]
        d[args[-1]] = value

    def get_path(self, *args):
        """
        This function return a path based on settings with ("path","main") as root path
        :param args: each relative path to cross
        :return:
        """
        if args[0] not in self.get("path", "relative").keys():
            return self.get("path", *args)
        abs_path = self.get("path", "main")
        for path in args:
            abs_path = os.path.join(abs_path, settings.get("path", "relative", path))
        return abs_path


settings = Settings(os.path.expanduser(DEFAULT_SETTING_PATH))
devices = Settings(os.path.join(settings.get_path("deviceslist")))
# status = Settings(settings.get("path", "status"))
if not os.path.exists(settings.get("path", "tmp")):
    os.makedirs(settings.get("path", "tmp"))
# log.info("uName set to : {0}".format(settings["uName"]))
# log.info(settings)
