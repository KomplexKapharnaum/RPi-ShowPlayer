# -*- coding: utf-8 -*-
#
# This file load settings and can modify them
#   Settings are store in a JSON file
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


DEFAULT_SETTING["localport"] = dict()
DEFAULT_SETTING["localport"]["inhplayer"] = 9000
DEFAULT_SETTING["localport"]["interface"] = 8080

DEFAULT_SETTING["path"] = dict()
DEFAULT_SETTING["path"]["main"] = "/dnc"
DEFAULT_SETTING["path"]["logs"] = "/dnc/logs"
DEFAULT_SETTING["path"]["soft"] = os.path.join(DEFAULT_SETTING["path"]["main"], "DNC_Prog")
DEFAULT_SETTING["path"]["media"] = "/dnc/media"
DEFAULT_SETTING["path"]["scp"] = "/usr/bin/scp"
DEFAULT_SETTING["path"]["tmp"] = "/tmp/dnc"
DEFAULT_SETTING["path"]["scenario"] = "/dnc/scenario"
DEFAULT_SETTING["path"]["activescenario"] = "/dnc/scenario/__active"
DEFAULT_SETTING["path"]["sharedmemory"] = "/var/tmp/"
DEFAULT_SETTING["path"]["kxkmcard"] = "/dnc/player/Hardware/hardware/hardware"
DEFAULT_SETTING["path"]["hplayer"] = "/dnc/HPlayer/bin/HPlayer"
DEFAULT_SETTING["path"]["omxplayer"] = "/usr/bin/omxplayer"
DEFAULT_SETTING["path"]["vlcvideo"] = "/usr/local/bin/cvlc --vout mmal_vout --aout alsa -I rc  --no-autoscale --zoom=0.35 --no-osd"
DEFAULT_SETTING["path"]["vlcaudio"] = "/usr/local/bin/cvlc --vout none --aout alsa -I rc  --no-autoscale --zoom=0.35 --no-osd"
DEFAULT_SETTING["path"]["aplay"] = "/usr/bin/aplay"
DEFAULT_SETTING["path"]["mpg123"] = "/usr/bin/mpg123 -C"
DEFAULT_SETTING["path"]["interface"] = "/dnc/player/Python/interface/bottleserver.py"

DEFAULT_SETTING["sync"] = dict()
DEFAULT_SETTING["sync"]["video"] = True                 # Explain if the scyn protocol must sync video or not
DEFAULT_SETTING["sync"]["enable"] = True                # Put False to disable sync
DEFAULT_SETTING["sync"]["max_scenario_sync"] = 5        # Max scenario of the same group to be sync
DEFAULT_SETTING["sync"]["scenario_sync_timeout"] = 30   # 30 seconds
DEFAULT_SETTING["sync"]["escape_scenario_dir"] = "__"   # 3 seconds

DEFAULT_SETTING["scenario"] = dict()
DEFAULT_SETTING["scenario"]["date_format"] = "%Y-%m-%d_%H:%M:%S"
DEFAULT_SETTING["scenario"]["date_len"] = 24            # extension + date length + @
DEFAULT_SETTING["scenario"]["dest_all"] = "All"         # string for all dest in a signal
DEFAULT_SETTING["scenario"]["dest_group"] = "Group"     # string for group dest in a signal
DEFAULT_SETTING["scenario"]["dest_self"] = "Self"       # string for self dest in a signal
DEFAULT_SETTING["scenario"]["play_sync_delay"] = 0.500  # time delta before run sync between cards

DEFAULT_SETTING["media"] = dict()
DEFAULT_SETTING["media"]["automove"] = "yes"

DEFAULT_SETTING["OSC"] = dict()
DEFAULT_SETTING["OSC"]["iamhere_interval"] = 5
DEFAULT_SETTING["OSC"]["checkneighbour_interval"] = 130
DEFAULT_SETTING["OSC"]["classicport"] = 1781
DEFAULT_SETTING["OSC"]["ackport"] = 1782
DEFAULT_SETTING["OSC"]["TTL"] = 1
DEFAULT_SETTING["OSC"]["JTL"] = 1

DEFAULT_SETTING["rtp"] = dict()
DEFAULT_SETTING["rtp"]["enable"] = True                 # Put False to unactive rtp
DEFAULT_SETTING["rtp"]["timeout"] = 5
DEFAULT_SETTING["rtp"]["stack_length"] = 3
DEFAULT_SETTING["rtp"]["accuracy_start_ns"] = 3000000   # 3 ms
DEFAULT_SETTING["rtp"]["accuracy_max_ns"] = 12000000   # 12 ms
DEFAULT_SETTING["rtp"]["accuracy_factor"] = 1.05   # 5% per try

DEFAULT_SETTING["ack"] = dict()
DEFAULT_SETTING["ack"]["stack_recv"] = 256
DEFAULT_SETTING["ack"]["interval_critical"] = (0.010, 0.015, 0.020, 0.025, 0.050, 0.100, 0.100, 0.100, 0.100, 0.100)
DEFAULT_SETTING["ack"]["interval_classical"] = (0.30, 0.50, 0.50, 0.50, 0.50, 0.100, 0.100, 0.100, 0.100, 0.250, 0.250)
DEFAULT_SETTING["ack"]["interval_protocol"] = (0.75, 0.100, 0.125, 0.200, 0.500)
DEFAULT_SETTING["ack"]["interval_short"] = (0.100, 0.150, 0.200)
DEFAULT_SETTING["ack"]["interval_default"] = (0.75, 0.100, 0.125, 0.200, 0.500)

DEFAULT_SETTING["log"] = dict()
DEFAULT_SETTING["log"]["level"] = "debug"
DEFAULT_SETTING["log"]["output"] = "Console"


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
        dict.__init__(self, DEFAULT_SETTING)
        try:
            with open(path, 'r') as fp:
                try:
                    self.update(json.load(fp))
                    log.info("Settings loaded from {0}".format(path))
                except:
                    log.error("Could not load settings")
        except IOError:
            log.info("No settings found at path {0}, create one".format(path))
            with open(path, 'wr') as fp:
                pass
        except json.scanner.JSONDecodeError as e:
            log.error("Could not load settings : {0}".format(e))

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
        d = self
        for elem in args:
            if elem in d.keys():
                d = d[elem]
            else:
                return Settings.get_default(*args)
        return d


settings = Settings(os.path.expanduser(DEFAULT_SETTING_PATH))
if not os.path.exists(settings.get("path", "tmp")):
    os.makedirs(settings.get("path", "tmp"))
# log.info("uName set to : {0}".format(settings["uName"]))
# log.info(settings)
