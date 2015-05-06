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