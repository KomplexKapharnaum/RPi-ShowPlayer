# -*- coding: utf-8 -*-


import curses
import netelem

screen = None

class Display:

    def __init__(self):
        self._screen = curses.initscr()
        curses.noecho()
        curses.cbreak()
        self._draw_fnct = draw_list
        self._draw_fnct_args = list()
        self._internal_cursor = 0

    def draw(self):
        self._draw_fnct(self._draw_fnct_args)
        self._internal_cursor = 0

    def newline(self, line, *args):
        self._screen.addstr(self._internal_cursor,0,line,*args)
        self._internal_cursor += 1

    def update(self):
        self.draw()
        self.refresh()

    def refresh(self):
        self._screen.refresh()



def draw_list(elems):
    screen.newline(netelem.get_header())
    for elem in elems.values():
        screen.newline(elem.get_line())


def init_display():
    global screen
    screen = Display()




