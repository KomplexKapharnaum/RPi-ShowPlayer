# -*- coding: utf-8 -*-
#
# This file provide tools to use the rtp sync
#


from libs import rtplib
from engine.setting import settings
from engine.log import init_log

log = init_log("rtpcync")


def wait_sync(abs_time_tuple):
    """
    This function wait absolute time and release
    :param abs_time_tuple: Absolute time (as in rtplib) to wait
    :type abs_time_tuple: list of int
    :return:
    """
    log.debug('+++ BEFORE SYNC PLAY {0}'.format(rtplib.get_time()))
    rtplib.wait_abs_time(*abs_time_tuple)
    return True
    # log.debug('+++ SYNC PLAY {0}'.format(abs_time_tuple))


def flag_wait_sync(flag):
    """
    This function wait absolute time in the flag
    :param flag: Flag which can carry the abs_time
    :type flag: engine.fsm.Flag
    :return:
    """
    if flag is not None and flag.args is not None and 'abs_time_sync' in flag.args.keys():
        return wait_sync(flag.args['abs_time_sync'])
    return False

