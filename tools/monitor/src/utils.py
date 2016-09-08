# -*- coding: utf-8 -*-

_LOG = False

#from .display import screen

i = 0

def log(msg):
    if _LOG is True:
        print(msg)
    elif _LOG is None:
        pass
        # global i
        # screen._screen.addstr(i,0,msg)
        # i += 1
        # screen._screen.refresh()


def ip_from_addr(addr):
    return str(addr.url.split(':')[1][2:])