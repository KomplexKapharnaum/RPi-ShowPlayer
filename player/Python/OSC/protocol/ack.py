# -*- coding: utf-8 -*-
#
# This file provide msg and function for the ACK OSC Protocol
#

import liblo

from weakref import WeakValueDictionary


from OSC import message
from src.log import init_log

log = init_log("proto.ack")


def get_ack_msg(uid):
    log.log("raw", "uid1 : {uidt}, uid2 : {uidp}".format(uidt=uid[0], uidp=uid[1]))
    return message.Message("/ack", False, ('i', uid[0]), ('i', uid[1]))