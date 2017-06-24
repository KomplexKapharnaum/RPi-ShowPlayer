# -*- coding: utf-8 -*-
#
# This module contain an (ACK) OSC and a Classical OSC server merge into a DNC Server
#

import inspect as _inspect
import threading

from collections import deque

import liblo

from protocol import ack
import message
import network

# OLD # import utils # REPLACE BY :
from libs import acklib as utils
from engine.threads import network_scheduler
from engine.setting import settings
from libs.oscack.network import NetworkElement, NetworkMap

from engine.log import init_log

log = init_log("server")


class ClassicalOSCServer(liblo.ServerThread):
    def __init__(self, port=None):
        try:
            liblo.ServerThread.__init__(self, port=int(port))
        except liblo.ServerError as e:
            log.error("Fail to start OSC server on {}".format(port))
            raise e


class AckOSCServer(ClassicalOSCServer):
    def __init__(self, port=None):
        ClassicalOSCServer.__init__(self, port=port)
        self._ack_recv_stack = deque(maxlen=settings.get("ack", "stack_recv"))

        # Active ACK reception
        def _pass(path, args, type, src):
            log.log("raw", "Get ack from {ip} with args : {args} ".format(ip=src.get_hostname(), args=args))
            # pass

        self.add_method("/ack", None, _pass)
        #

    def _recv_header(self, ack_order, ack_uid, ip):
        """
        First opperation when an ACK message is received. If it's a SYN message, check if it's haven't been done.
        If it's a ACK message stop the send thread
        :param ack_order: True == SYN // False == ACK
        :param ack_uid:
        :return: True == Execute callback, False == Ignore callback
        """
        if ack_order:  # SYN
            return self._recv_syn(ack_uid, ip)  # Check if already been executed
        else:  # ACK
            message.unregister(ack_uid)  # Stop the send thread

    def _recv_syn(self, ack_uid, ip):
        """
        Check if uid is in recv stack, if it will ignore msg returing False, else it will send a ack,
        add the uid in the stack and return True
        :param ack_uid:
        :return: False (ignore) or True (run callback)
        """
        # log.log("raw", "SYN : ack_uid = "+str(ack_uid))
        # log.log("raw", "    : ack_recv_stack : "+str(self._ack_recv_stack))
        if ack_uid in self._ack_recv_stack:
            if log.isEnabledFor("net_raw"):
                log.log("net_raw", "SYN : already executed SKIP (uid = " + str(ack_uid) + ")")
                log.log("net_raw", "    : ack_recv_stack : " + str(self._ack_recv_stack))
            return False  # Already been executed : SKIP
        else:
            self._ack_recv_stack.append(ack_uid)
            message.send_ack(ip, ack.get_ack_msg(ack_uid))
            return True

    def return_method(self, callback_func):
        def _ack_callback(path, args, types=None, src=None, user_data=None):
            if log.isEnabledFor("net_raw"):
                log.log("net_raw", "[recv_osc] : " + str(path) + " :(" + str(types) + "): " + str(args))
                log.log("net_raw", "  [callback :] " + str(callback_func))
            types = types[3:]  # remove Tii from types
            ack_order = args.pop(0)  # T of F (T=SYN, F=ACK)
            ack_uid = (args.pop(0), args.pop(0))

            if self._recv_header(ack_order, ack_uid, src.get_hostname()) is False:  # Ignore
                return

            # COPIED FROM pyliblo.pyx
            func_args = (path, args, types, src, user_data)
            # call function
            if _inspect.getargspec(callback_func)[1] is None:
                # determine number of arguments to call the function with
                n = len(_inspect.getargspec(callback_func)[0])
                if _inspect.ismethod(callback_func):
                    n -= 1  # self doesn't count
                r = callback_func(*func_args[0:n])
            else:
                # function has argument list, pass all arguments
                r = callback_func(*func_args)
            if log.isEnabledFor("net_raw"):
                log.log("net_raw", "end call back, return " + str(r))
            return r
            # END #

        return _ack_callback

    #
    # def _return_method(self, callback_func):
    # def _ack_callback(*args):
    #         args = list(args)
    #         log.debug("Recv OSC paquet : Args : "+str(args))
    #         ack_order = args[1].pop(0)  # T of F (T=SYN, F=ACK)
    #         args[2] = args[2][3:]  # remove Tii from types
    #         ack_uid, ack_port = utils.decode_uids(args[1].pop(0), args[1].pop(0))
    #         # log.debug("recv_header call with : "+str((ack_order, ack_uid, args[3].get_hostname, ack_port)))
    #
    #         if self._recv_header(ack_order, ack_uid, args[3].get_hostname(), ack_port) is False:  # Ignore
    #             return
    #
    #         log.debug("Args : "+str(args))
    #         # COPIED FROM pyliblo.pyx
    #         func_args = tuple(args)
    #         log.debug("Func Args : "+str(func_args))
    #         # call function
    #         if _inspect.getargspec(callback_func)[1] == None:
    #             # determine number of arguments to call the function with
    #             n = len(_inspect.getargspec(callback_func)[0])
    #             if _inspect.ismethod(callback_func):
    #                 n -= 1  # self doesn't count
    #             log.debug("Will call (cutted) "+str(callback_func)+" with : "+str(func_args[0:n]))
    #             r = callback_func(*func_args[0:n])
    #         else:
    #             # function has argument list, pass all arguments
    #
    #             log.debug("Will call "+str(callback_func)+" with : "+str(func_args))
    #             r = callback_func(*func_args)
    #
    #         return r
    #         # END #
    #     return _ack_callback

    def add_method(self, *args, **kwargs):
        """
        Encapsulate call back in ack_callback before adding to the server via the liblo method
        :param args:
        :param kwargs:
        :return:
        """
        if log.isEnabledFor("raw"):
            log.log("raw",
                    "Add method : " + str([self, args[0], args[1], self.return_method(args[2]), args[3:], kwargs]))
        liblo.ServerThread.add_method(self, args[0], args[1], self.return_method(args[2]), *args[3:], **kwargs)

    def del_method(self, *args, **kwargs):
        liblo.Server.del_method(self, *args, **kwargs)


class DNCServer(object):
    def __init__(self, uname, groups="", classicport=settings.get("OSC", "classicport"),
                 ackport=settings.get("OSC", "ackport")):
        self.classicServer = ClassicalOSCServer(port=classicport)
        log.log("raw","Server Classic init on " + str(self.classicServer.get_port()))
        self.ackServer = AckOSCServer(port=ackport)
        log.log("raw","Server ACK init on " + str(self.ackServer.get_port()))
        self.networkmap = NetworkMap()
        self.net_elem = NetworkElement(uname, "127.0.0.1")
        self.networkmap[uname] = self.net_elem
        self.groups = groups
        self.started = threading.Event()
        self.started.clear()

    def start(self, auto_add=True):
        self.started.set()
        if auto_add:
            for method in network.to_auto_add:
                self.add_method(*method)
        self.classicServer.start()
        log.info("Server Classic start on " + str(self.classicServer.get_port()))
        self.ackServer.start()
        log.info("Server ACK start on " + str(self.ackServer.get_port()))

    def __del__(self):
        self.stop()

    def stop(self):
        log.info("Stopping DNC_Server ...")
        self.classicServer.stop()
        self.ackServer.stop()
        # try:
        # network_scheduler.stop()
        # except TypeError as e:
        #     log.exception(e)
        log.info("... Stop !")
        self.started.clear()

    def add_method(self, *args, **kwargs):
        self.classicServer.add_method(*args, **kwargs)
        self.ackServer.add_method(*args, **kwargs)

    def del_method(self, *args, **kwargs):
        self.classicServer.del_method(*args, **kwargs)
        self.ackServer.del_method(*args, **kwargs)
