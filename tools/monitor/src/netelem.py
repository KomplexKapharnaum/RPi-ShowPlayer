# -*- coding: utf-8 -*-

import time, datetime

from utils import log, ip_from_addr


Fields = dict()

Display = ("ip", "hostname", "timeline", "timeline_vers", "scene", "temp", "chan", "rssi", "battery", "voltage", "git", "time")


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

    def default_field(self, value):
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
    return show_unit(field, value, "°C")

def show_rssi(field, value, *args):
    return show_unit(field, value, "dBm")

def show_voltage(field, value, *args):
    voltage = int(args[0].battery[:-2])
    if voltage == 12:
        if value < 12.3:
            # TODO : color if the tension is too low
            pass
    return show_unit(field, value, "V")

def show_ip(field, value, *args):
    return field.header_string.format(ip_from_addr(value))

def show_time(field, value, *args):
    dt = datetime.datetime.fromtimestamp(value)
    return field.header_string.format(dt.isoformat())


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
Fields["git"] = MonitorField("git",15)
Fields["time"] = MonitorField("time",29,show_time)


def get_header():
    header = ""
    for field in Display:
        header += Fields[field].header
    return header