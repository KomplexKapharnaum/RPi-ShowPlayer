# -*- coding: utf-8 -*-
#
# This file provide some generic utils for the OSC layer
#

import time
import random
from libs import subprocess32

from engine.log import init_log
log = init_log("utils")


def gen_uids(port):
    """
    Generate uids from the ACK port, see README for details
    :param port:
    :return: (uidt,udip)
    """
    t = (0x7FFFFFFF & int(time.time()*1000)) # 1 ms precision
    p = (0x7FFF & int(random.random()*0xFFFF)) << 16
    p |= int(port)
    return t, p


def encode_uid(uid):
    """
    This function encode the complete uid in two integers in order to be transport by OSC
    :param uid:
    :return: uidt, uidp
    """
    return ((0xFFFFFFFF00000000 & uid) >> 32), (0x00000000FFFFFFFF & uid)

def decode_uids(uidt, uidp):
    """
    Decode uids to get an unique ID based on time and random, and the port number to answer
    :param uidt:
    :param uidp:
    :return: uid, port
    """
    return (uidp | (uidt << 32)), (0x0000FFFF & uidp)

def get_ip():
    ip = subprocess32.check_output(['hostname', '-i'])
    return ip
