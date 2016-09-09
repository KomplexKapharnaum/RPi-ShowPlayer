# -*- coding: utf-8 -*-

import time, datetime

from utils import log, ip_from_addr

from common import Display, Battery

Fields = dict()




class NetworkElement:

    def __init__(self,src):
        """
        """
        self.src = src
        self.messages = list()

    def add_monitor(self, args):
        self.messages.append(MonitorMessage(*([self.src, ]+args)))
        log(str(self.messages[-1]))

    def get_line(self):
        return str(self.messages[-1])


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

class MonitorMessage:
    def __init__(self,src,hostname,timeline,timeline_vers,scene,temp,chan,rssi,battery,voltage,git):
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


    def __str__(self):
        s = ""
        for field in Display:
            s += Fields[field].get_field(self.__dict__[field], self)
            s += " "
        if len(s) > 0:
            s = s[:-1]  # Remove last space
        return s


def get_float(field, value, *args):
    f = "{:." + str(field.fnct_args) + "f}"
    return f.format(float(value))

def show_float(field, value, *args):
    return field.header_string.format(get_float(field, value))

def show_unit(field, value, unit, *args):
    s = get_float(field, value)
    return field.header_string.format(s+" "+str(unit))

def show_temp(field, value, *args):
    temp = show_unit(field, value, "°C")
    if value > 60:
        temp = "*X*" + temp + "*X*"
    return temp


def show_rssi(field, value, *args):
    rssi = show_unit(field, value, "dBm")
    if value < -83:
        rssi = "*X*"+rssi+"*X*"
    return rssi

def show_voltage(field, value, *args):
    voltage = Battery[args[0].battery]["warn"]
    v = show_unit(field, value, "V")
    if value <= voltage:
        v = "*X*"+v+"*X*"
    return v

def show_ip(field, value, *args):
    return field.header_string.format(ip_from_addr(value))

def show_time(field, value, *args):
    dt = datetime.datetime.fromtimestamp(value)
    t = field.header_string.format(dt.isoformat())
    if time.time() - value > 70:
        t = "*X*"+t+"*X*"
    return t


Fields["ip"] = MonitorField("ip",14,show_ip)
Fields["hostname"] = MonitorField("hostname",15)
Fields["timeline"] = MonitorField("timeline",17)
Fields["timeline_vers"] = MonitorField("timeline_vers",23)
Fields["scene"] = MonitorField("scene",12)
Fields["temp"] = MonitorField("temp",10,show_temp,1)
Fields["chan"] = MonitorField("chan",6)
Fields["rssi"] = MonitorField("rssi",10,show_rssi,0)
Fields["battery"] = MonitorField("battery",8)
Fields["voltage"] = MonitorField("voltage",8,show_voltage,2)
Fields["git"] = MonitorField("git",25)
Fields["time"] = MonitorField("time",29,show_time)


def get_header(current):
    header = ""
    for field in Display:
        if Fields[field].name == current:
            header += '*X*'
        header += Fields[field].header
        if Fields[field].name == current:
            header += '*X*'

    return header