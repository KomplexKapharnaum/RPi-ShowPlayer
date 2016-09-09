# -*- coding: utf-8 -*-

import time
import curses

from src.display import init_display
init_display()
from src.display import screen

from src.network import OSCServer

server = OSCServer(1783)
screen._draw_fnct_args = server.netelems
screen.update()
server.start()


time.sleep(1)
while 1:
    c = screen._screen.getch()
    if c == ord('q'):
        break  # Exit the while()
    elif c == ord('i'):
        screen.list_sort_key = "ip"
        screen.update()
    elif c == ord('h'):
        screen.list_sort_key = "hostname"
        screen.update()
    elif c == curses.KEY_ENTER:
        screen.update()
    elif c == 68:
        screen.prev_select()
        screen.update()
    elif c == 67:
        screen.next_select()
        screen.update()
    elif c == 65:
        screen.list_sort_order = "up"
        screen.update()
    elif c == 66:
        screen.list_sort_order = "down"
        screen.update()
    # else:
    #     print ("key "+ str(c))

server.stop()
server.free()
