# -*- coding: utf-8 -*-
#
# Define some basic tools for the project
#
#

import weakref
import sys
import os
import time

from libs.unidecode import unidecode

from setting import settings
import engine
from engine.log import init_log

log = init_log("tools")


_to_stop_thread = dict()

flag_popup = engine.fsm.Flag("REMOTE_POPUP")


def register_thread(thread):
    """
    This function register a thread to stop it at the end of
    :param thread:
    :return:
    """
    global _to_stop_thread
    _to_stop_thread[id(thread)] = weakref.ref(thread)


def unregister_thread(thread):
    """
    This function unregister a thread to avoid keeping a weakref to it
    :param thread: thread to unreference
    :return:
    """
    global _to_stop_thread
    del _to_stop_thread[id(thread)]


def get_smallest_difference(elements, n):
    min_value = None
    min_elems = None
    for elem in elements:
        tmp_elements = list(elements)
        tmp_elements.remove(elem)
        final_list = list()
        for i in xrange(n):
            a = min(tmp_elements, key=lambda x:abs(x-elem))
            tmp_elements.remove(a)
            final_list.append(a)
        if min_value > (max(final_list) - min(final_list)) or min_value is None:
            min_value = (max(final_list) - min(final_list))
            min_elems = final_list
    return min_value, min_elems


def sleep_thread(time, dt=0.5):
    pass


def set_python_path(depth=0):
    f = sys._getframe(1)
    fname = f.f_code.co_filename
    fpath = os.path.dirname(fname)
    PythonPath = os.path.join(fpath, "../".join(["" for x in xrange(depth+1)]))
    sys.path.append(PythonPath)


def search_in_or_default(key, indict, setting=False, default=None):
    """
    This function search the key into the indict or return default value
    :param key: Key or tuple of keys to search in, if tuple it will return a dict of found values
    :param indict: Dict of values to search in
    :param setting: If not false it must be a tuple of keys to search in settings as ("values","gyro")
    :param default: If really not found it will return None
    :return:
    """
    if isinstance(key, (list, tuple)):
        outdict = dict()
        for k in key:
            outdict[k] = search_in_or_default(k, indict, setting=setting, default=default)
        return outdict
    if key in indict.keys():
        return indict[key]
    elif setting is not False:
        try:
            setting.append(key)
            return settings.get(*setting)
        except AttributeError, KeyError:
            log.log("debug", "Search for a setting value which doesn't exist")
    return default


def log_teleco(ligne1=" ", ligne2=" ", error=False, encode="utf-8"):
    """
    This function log a message to the teleco
    :param ligne1:
    :param ligne2:
    :param error: Set if it's an error or not, if True wait for the error_delay teleco setting
    :param encode: Encoding of input strings, if none, assume data are already encoded
    :return:
    """
    if encode is not None:
        if ligne1 is not None:
            ligne1 = ligne1.decode(encode)
        if ligne2 is not None:
            ligne2 = ligne2.decode(encode)
    ligne1 = unidecode(ligne1)
    ligne2 = unidecode(ligne2)
    engine.threads.patcher.patch(flag_popup.get(args={"ligne1": ligne1, "ligne2": ligne2}))
    if error:
        time.sleep(settings.get("log", "teleco", "error_delay"))
