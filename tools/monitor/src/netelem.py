# -*- coding: utf-8 -*-

import time, datetime

from utils import log, ip_from_addr

from common import Display, Battery
import sys
import subprocess

from show import *

Fields = dict()








class MonitorField:
    def __init__(self,name,column_width,fnct=None,args=None):
        self.name = name
        self.column_width = column_width
        self.header_string = "{:<"+str(column_width)+"}"
        self.header_string_plus = "{:^"+str(column_width-1)+"}"
        self.header = "["+self.header_string_plus.format(self.name)+"]"
        self.fnct_args = args
        if fnct is not None:
            self.fnct = fnct
        else:
            self.fnct = MonitorField.default_field

    def get_field(self, value, msg):
        return self.fnct(self,value, msg)

    def default_field(self, value, autre):
        return self.header_string.format(str(value))

class NetworkElement:

    def __init__(self, src):
        """
        """
        self.src = src
        self.messages = list()
        self._ping = datetime.datetime.now()
        self.selected = False
        self.ssh = None

    def add_monitor(self, args):
        self.messages.append(MonitorMessage(*([self.src, ] + args)))
        log(str(self.messages[-1]))

    def get_line(self):
        if self.selected:
            line = " * "
        else:
            line = "   "
        line += str(self.messages[-1])
        if "ping" in Display :
            line += Fields["ping"].header_string.format(self._ping.strftime("%H:%M:%S"))
        return line

    def sort(self, key):
        if key == "ping":
            return self._ping
        else:
            return self.messages[-1].__dict__["sort_"+key]()

    def ping(self):
        self._ping = datetime.datetime.now()

    def open_ssh(self):
        p = subprocess.Popen(["/usr/bin/terminator", "-x", "ssh", "root@{0}".format(ip_from_addr(self.src))], stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        # p.wait()



class MonitorMessage:
    def __init__(self,src,hostname,timeline,timeline_vers,scene,temp,chan,rssi,battery,voltage,git,commit="-"):
        self.time = time.time()
        self.ip = src
        self.hostname = hostname
        self.timeline = timeline
        self.timeline_vers = timeline_vers
        self.scene = scene
        self.temp = temp
        self.chan = int(chan.split('\tchannel')[1].split(' ')[1])
        self.rssi = int(rssi.split('\tsignal')[1].split('dBm')[0][1:])
        self.battery = battery
        self.voltage = voltage
        self.git = git.split("\n")[0]
        self.commit = commit.split("\n")[0]
        self.last = self.time

        self.sort_ip = self._sort_ip
        self.sort_hostname = self._sort_hostname
        self.sort_time = self._sort_time
        self.sort_git = self._sort_git
        self.sort_voltage = self._sort_voltage
        self.sort_battery = self._sort_battery
        self.sort_rssi = self._sort_rssi
        self.sort_chan = self._sort_chan
        self.sort_temp = self._sort_temp
        self.sort_scene = self._sort_scene
        self.sort_timeline_vers = self._sort_timeline_vers
        self.sort_timeline = self._sort_timeline
        self.sort_commit = self._sort_commit
        self.sort_last = self._sort_last
        

    def _sort_ip(self):
        ip = ip_from_addr(self.ip).split(".")
        _ip = int(ip[0]) * 256 ** 3
        _ip += int(ip[1]) * 256 ** 2
        _ip += int(ip[2]) * 256 ** 1
        _ip += int(ip[3]) * 256 ** 0
        return _ip

    def _sort_hostname(self):
        return self.hostname

    def _sort_time(self):
        return self.time

    def _sort_timeline(self):
        return self.timeline

    def _sort_timeline_vers(self):
        return self.timeline_vers

    def _sort_scene(self):
        return self.scene

    def _sort_temp(self):
        return self.temp

    def _sort_chan(self):
        return self.chan

    def _sort_rssi(self):
        return self.rssi

    def _sort_battery(self):
        return self.battery

    def _sort_voltage(self):
        return self.voltage

    def _sort_git(self):
        return self.git

    def _sort_commit(self):
        return self.commit

    def _sort_last(self):
        return time.time()-self.time


    def __str__(self):
        s = ""
        for field in Display:
            try:
                s += Fields[field].get_field(self.__dict__[field], self)
                s += " "
            except KeyError:
                pass
        if len(s) > 0:
            s = s[:-1]  # Remove last space
        return s




Fields["ip"] = MonitorField("ip", 14, show_ip)
Fields["hostname"] = MonitorField("hostname", 15)
Fields["timeline"] = MonitorField("timeline", 17)
Fields["timeline_vers"] = MonitorField("timeline_vers", 23)
Fields["scene"] = MonitorField("scene", 12)
Fields["temp"] = MonitorField("temp", 10, show_temp, 1)
Fields["chan"] = MonitorField("chan", 6)
Fields["rssi"] = MonitorField("rssi", 10, show_rssi, 0)
Fields["battery"] = MonitorField("battery", 8)
Fields["voltage"] = MonitorField("voltage", 8, show_voltage, 2)
Fields["git"] = MonitorField("git", 32, show_git)
Fields["time"] = MonitorField("time", 9, show_time)
Fields["commit"] = MonitorField("commit", 8)
Fields["last"] = MonitorField("last", 6, show_last, 0)
Fields["ping"] = MonitorField("ping", 9)



def get_header(current):
    header = ""
    for field in Display:
        if Fields[field].name == current:
            header += '*X*'
        header += Fields[field].header
        if Fields[field].name == current:
            header += '*X*'

    return header