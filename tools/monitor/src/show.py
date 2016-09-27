# -*- coding: utf-8 -*-

import datetime
import time
import sys


from common import Battery
from utils import ip_from_addr, log

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
    try:
        voltage = Battery[args[0].battery]["warn"]
    except KeyError as e:
        log(e.message)
        voltage = 100
    v = show_unit(field, value, "V")
    if value <= voltage:
        v = "*X*"+v+"*X*"
    return v

def show_ip(field, value, *args):
    return field.header_string.format(ip_from_addr(value))

def show_time(field, value, *args):
    dt = datetime.datetime.fromtimestamp(value)
    t = field.header_string.format(dt.strftime("%H:%M:%S"))
    if time.time() - value > 70:
        t = "*X*"+t+"*X*"
    return t

def show_git(field, value, *args):
    git = field.header_string.format(value)
    if value not in ["master",] + sys.argv:
        git = "*X*" + git + "*X*"
    return git

def show_last(field, value, *args):
    last = time.time() - value
    return show_unit(field, last, "s")