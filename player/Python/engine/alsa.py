# -*- coding: utf-8 -*-
#
# This file provide functions to manipulate ALSA
#

import subprocess
import shlex

from engine.setting import settings
from engine.log import init_log

log = init_log("alsa")


def set_absolute_amixer():
    if settings.get("sys", "raspi"):
        try:
            subprocess.check_call("{cmd} {value}dB".format(cmd=shlex.split(settings.get("path", "amixer")),
                                                           value=settings.get("sys", "volume")))
        except subprocess.CalledProcessError as e:
            log.exception("Cannont set alsamixer volume")
            log.show_exception(e)
    else:
        log.debug("Avoid setting alsamixer volume because we aren't a raspi")