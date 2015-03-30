# -*- coding: utf-8 -*-
#
# Define some basic tools for the project
#
#

import weakref
import sys
import os


_to_stop_thread = dict()


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
