# -*- coding: utf-8 -*-
#
# This file provide functions to manipulate ALSA
#

import subprocess
import shlex

from engine.setting import settings
from engine.log import init_log

log = init_log("alsa")


def get_rel_dB(value):
    """
    This function return correct string to set volume relativly
    :param value: value in dB (integer)
    :return:
    """
    sign = "+"
    if value < abs(value):          # Negative
        sign = "-"
    return "{0}dB{1}".format(abs(value), sign)


def set_absolute_amixer():
    """
    This function set the system volume
    :return:
    """
    if settings.get("sys", "raspi"):
        try:
            subprocess.check_call(shlex.split("{cmd} {value}dB".format(cmd=settings.get("path", "amixer"),
                                                                       value=settings.get("sys", "ref_volume"))))
            subprocess.check_call(shlex.split("{cmd} {value}".format(cmd=settings.get("path", "amixer"),
                                                                     value=get_rel_dB(settings.get("sys", "volume")))))
        except subprocess.CalledProcessError as e:
            log.exception("Cannont set alsamixer volume")
            log.show_exception(e)
    else:
        log.debug("Avoid setting alsamixer volume because we aren't a raspi")


def set_alsaequal_profile():
    """
    This function set the alsaequal EQ profile
    :return:
    """
    if settings.get("sys", "raspi"):
        try:
            profile = settings.get("sys", "alsaequal")
            chan = 1
            for value in profile:
                if type(value) is tuple:
                    val = '{0},{1}'.format(value[0],value[1])
                else:
                    val = '{0}'.format(value)

                subprocess.check_call(shlex.split("{cmd} cset numid={channel} {val}".format(val=val, channel=chan, cmd=settings.get("path", "alsaequal"))))
                chan+=1

        except subprocess.CalledProcessError as e:
            log.exception("Cannont set alsaequal EQ")
            log.show_exception(e)
    else:
        log.debug("Avoid setting alsaequal EQ because we aren't a raspi")