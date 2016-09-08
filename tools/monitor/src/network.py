# -*- coding: utf-8 -*-


import liblo
from utils import log, ip_from_addr
import netelem
from display import screen

class OSCServer(liblo.ServerThread):
    def __init__(self, port):
        liblo.ServerThread.__init__(self, port=port)
        self.add_method("/monitor",None,self._recv_monitor_data)
        self.netelems = dict()

    def _recv_monitor_data(self, path, args, types=None, src=None, user_data=None):
        ip_host = ip_from_addr(src) + "_" + args[0]
        if ip_host not in self.netelems.keys():
            # NEW NETWORK ELEM
            log("new net elem {0}".format(ip_host))
            self.netelems[ip_host] = netelem.NetworkElement(src)
        self.netelems[ip_host].add_monitor(args)
        screen.update()

