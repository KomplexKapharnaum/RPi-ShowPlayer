# -*- coding: utf-8 -*-


from src.display import init_display
init_display()
from src.display import screen

from src.network import OSCServer

server = OSCServer(1783)
server.start()

screen._draw_fnct_args = server.netelems

input("press a key to quit")

server.stop()
server.free()
