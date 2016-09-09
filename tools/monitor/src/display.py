# -*- coding: utf-8 -*-


import curses
import netelem

from common import Display

screen = None

class ScreenDisplay:

    def __init__(self):
        self._screen = curses.initscr()
        curses.start_color()
        curses.use_default_colors()
        for i in range(0, curses.COLORS):
            curses.init_pair(i + 1, i, -1)
        curses.noecho()
        curses.cbreak()
        self._draw_fnct = draw_list
        self._draw_fnct_args = list()
        self._internal_cursor = 0
        self.list_sort_cursor = 0
        self.list_sort_key = Display[self.list_sort_cursor]
        self.list_sort_order = "up"

    def next_select(self):
        self.list_sort_cursor = min(self.list_sort_cursor+1, len(Display)-1)
        self.list_sort_key = Display[self.list_sort_cursor]

    def prev_select(self):
        self.list_sort_cursor = max(self.list_sort_cursor - 1, 0)
        self.list_sort_key = Display[self.list_sort_cursor]

    def draw(self):
        self._draw_fnct(self._draw_fnct_args, self.list_sort_key)
        self._internal_cursor = 0

    def newline(self, line, *args):
        line = line.split("*X*")
        i = 0
        c = 0
        for elem in line:
            if i % 2 == 0:
                self._screen.addstr(self._internal_cursor,c,elem)
            elif i % 2 == 1:
                self._screen.addstr(self._internal_cursor, c, elem, curses.A_STANDOUT)
            c += len(elem)
            i += 1
        self._internal_cursor += 1

    def update(self):
        self.draw()
        self.refresh()

    def refresh(self):
        self._screen.refresh()



def draw_list(elems, sort_key):
    screen.newline(netelem.get_header(sort_key))
    list_elem = sorted(elems.items(), key=lambda x: x[1].messages[-1].__dict__["sort_"+sort_key]())
    if screen.list_sort_order == "down":
        list_elem = list_elem[::-1]
    for elem in list_elem:
        screen.newline(elem[1].get_line())


def init_display():
    global screen
    screen = ScreenDisplay()




