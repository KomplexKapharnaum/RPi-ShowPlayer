# -*- coding: utf-8 -*-

import liblo
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

test = 0

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
    elif c == 10:   # ENTER
        if screen.list_sort_order == "up":
            screen.list_sort_order = "down"
        else:
            screen.list_sort_order = "up"
        screen.update()
    elif c == 68:   # LEFT
        screen.prev_select()
        screen.update()
    elif c == 67:   # RIGHT
        screen.next_select()
        screen.update()
    elif c == 65:   # UP
        for elem in server.netelems.values():
            elem.selected = False
        if screen.select_dispo > 0:
            list_elem = sorted(server.netelems.items(), key=lambda x: x[1].sort(screen.list_sort_key))
            screen.select_dispo -= 1
            list_elem[screen.select_dispo][1].selected = True
        else:
            screen.select_dispo = -1
        screen.update()
    elif c == 66:   # DOWN
        for elem in server.netelems.values():
            elem.selected = False
        if screen.select_dispo < len(server.netelems.values()) - 1:
            list_elem = sorted(server.netelems.items(), key=lambda x: x[1].sort(screen.list_sort_key))
            screen.select_dispo += 1
            list_elem[screen.select_dispo][1].selected = True
        else:
            screen.select_dispo = -1
        screen.update()
    elif c == ord('t'): # test
        liblo.send(liblo.Address("127.0.0.1", server.osc_port), "/monitor", "test{0}".format(test), "none", "2016-09-08_12:34:00", "none", 32.43, "\tchannel 36 (5180 MHz), width: 20 MHz, center1: 5180 MHz", "\tsignal: -60 dBm", "lipo12", 12.0, "test/master\n", "-")
        test += 1
    elif c == ord('r'): # remove test
        try:
            del server.netelems["127.0.0.1_test{0}".format(test-1)]
            test -= 1
            screen.update()
        except KeyError:
            pass
    elif c == ord("s"):
        if screen.select_dispo != -1:
            list_elem = sorted(server.netelems.items(), key=lambda x: x[1].sort(screen.list_sort_key))
            list_elem[screen.select_dispo][1].open_ssh()
    # else:
    #     print ("key "+ str(c))

server.stop()
server.free()
