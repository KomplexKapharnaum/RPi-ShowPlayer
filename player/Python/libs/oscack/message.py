# -*- coding: utf-8 -*-
#
# This file describe a Meta Class for OSC Message in order to perform a transparent switch between
# Classic OSC messages and Ack OSC messages
#

import threading
import time

import liblo

import libs.oscack
# OLD # import utils # REPLACE BY :
from libs import acklib
from engine.setting import settings
from engine.log import init_log
log = init_log("message")
from engine import fsm


class Address():
    """
        This classe encapsulate liblo.Address in order to switch port beetween ACK or not
    """

    def __init__(self, ip=None):
        self.ip = ip
        if ip is None:
            self.target = liblo.Address(settings.get("OSC", "classicport"))
            self.ACKtarget = liblo.Address(settings.get("OSC", "ackport"))
        else:
            self.target = liblo.Address(ip, settings.get("OSC", "classicport"))
            self.ACKtarget = liblo.Address(ip, settings.get("OSC", "ackport"))

    def get_address(self, ACK=False):
        if ACK:
            return self.ACKtarget
        else:
            return self.target

    def get_hostname(self):
        return self.ip


class Message(liblo.Message):
    """
        Message can handle a classic OSC Message or an ACK OSC Message
    """

    def __init__(self, *args, **kwargs):
        """
        Special parameters : ACK, ACKSPEED, SEND_PORT
            other parameters will be passed to the liblo.Message init.
        :param args:
        :param kwargs:
        :return:
        """
        self.ACK = False
        self.ACKSPEED = None
        add_port = False
        self._args = args
        self._kwargs = kwargs

        # if "SEND_PORT" in kwargs.keys(): TODO : check and delete
        #     if kwargs["SEND_PORT"]:
        #         add_port = True
        #     del kwargs["SEND_PORT"]
        if "ACK" in kwargs.keys():
            if kwargs["ACK"]:
                self.ACK = True
                self.uid = acklib.gen_uids()
                args = [args[0], True, ('i', self.uid[0]), ('i', self.uid[1])] + list(args[1:])
                if add_port:
                    args.append(settings.get("OSC", "ackport"))
                # self.uid = acklib.decode_uids(self._uidt, self._uidp)
            del kwargs["ACK"]
        # else: TODO : check and delete
        #     if add_port:
        #         args.append(globalContext.settings.oscack.RAW.port)
        if "ACKSPEED" in kwargs.keys():
            self.ACKSPEED = kwargs["ACKSPEED"].upper()
            del kwargs["ACKSPEED"]

        try:
            liblo.Message.__init__(self, *args, **kwargs)
        except OverflowError as e:
            log.critical(log.show_exception(e))
            log.critical(str(args))
            log.critical(str(**kwargs))
            raise e

    def __str__(self):
        return "OSC MSG : " + str(self._args) + "  ::  " + str(self._kwargs)


class ThreadSendMessage(threading.Thread):
    """
        This class send a message until been stop. It's used to send ACK messages
    """

    def __init__(self, target, msg):
        threading.Thread.__init__(self)
        self.target = target
        self.msg = msg
        self.broadcast = False
        self._stop = threading.Event()
        self._n_send = 0
        if msg.ACKSPEED is None:
            ack_speed = settings.get("ack", "interval_default")
        else:
            try:
                ack_speed = settings.get("ack", msg.ACKSPEED)
            except KeyError:
                log.error("No ackspeed named : {0}".format(msg.ACKSPEED))
                ack_speed = settings.get("ack", "interval_default")
        self._interval_table = ack_speed
        if target.get_hostname() != "255.255.255.255":  # Broadcast
            # Register in order to be stop when a ACK is received
            register(self, self.msg.uid)
        else:
            self.broadcast = True
            oscack.broadcast_ack_threads.append(self.msg.uid)
            # globalContext.protocol.ack.ACK_BROADCAST_REGISTER.append(self.msg.uid) TODO : check and remove
        self.sending = threading.Lock()

    def stop(self):
        self._stop.set()

    def run(self):
        with self.sending:
            while not self._stop.is_set() and self._n_send < len(self._interval_table) + 1:
                try:
                    liblo.send(self.target, self.msg)
                except (liblo.AddressError, IOError) as err:
                    log.exception(
                        "Impossible d'envoyer le message depuis le thread \n Error : " + str(
                            err) + " \n Message : " + str(
                            self.msg) + " \n Target : " + str(self.target))
                else:
                    if self._n_send == len(self._interval_table):
                        break
                    time.sleep(float(self._interval_table[self._n_send]))
                    self._n_send += 1

    def is_recv(self):
        """
            This function return True if the msg have been recv (reply ack), None if it's currently sending or False
        """
        if self.target.get_hostname() == "255.255.255.255":
            # raise ImportWarning("We can't know if a broadcast msg arrieved") #
            log.error("Ask if is recv but it's a broadcast message so we can't know it !")
        if self._stop.is_set():
            return True
        elif self._n_send < len(self._interval_table) + 1:
            return None
        else:
            return False

    def wait_recv(self, n_tries=0):
        """
            This function block until the end of the thread
            If an ack have been recv it ends
            If not you can ask for retrying n_tries times
        """
        with self.sending:
            if self.is_recv():
                return
            else:
                if n_tries > 0:
                    self.start()  # Don't need to re-register because we haven't been unregistered
                    return self.wait_recv(n_tries - 1)
                else:
                    raise RuntimeWarning("Wait reception of a message which haven't been received")


def send(target, msg):
    if type(target) == liblo.Address:
        log.warning("Target : {0} is a liblo Address, please update to message.Address ")
        target = Address(ip=target.get_hostname())
    if log.isEnabledFor("raw"):
        log.log("raw",
                "Try to send " + str(msg) + " at " + str(target.get_hostname()) + ":{port} with ACK={ACK}".format(
                    port=target.get_address(msg.ACK).get_port(), ACK=msg.ACK))
    if msg.ACK:
        t = ThreadSendMessage(target.ACKtarget, msg)
        t.start()
        return msg.uid
    else:
        try:
            liblo.send(target.target, msg)
        except (liblo.AddressError, IOError) as err:
            log.exception(
                "Impossible d'envoyer le message depuis \n Error : " + str(err) + " \n Message : " + str(
                    msg) + " \n Target : " + str(target.target))


def send_ack(ip, msg):
    if log.isEnabledFor("raw"):
        log.log("raw",
                "Try to send " + str(msg) + " at " + str(ip) + ":{port} with ACK={ACK}".format(
                    port=settings.get("OSC", "ackport"), ACK=msg.ACK))
    liblo.send(liblo.Address(ip, settings.get("OSC", "ackport")), msg)


def unregister(uid):
    """
    Stop a thread which has been registered
    :param uid:
    :return:
    """
    if uid in oscack.broadcast_ack_threads:
            return  # It's a broadcast ack so pass
    try:
        if log.isEnabledFor("raw"):
            log.log("raw", "Try to unresgister : " + str(uid) + " on " + str(
                oscack.ack_threads))
        oscack.ack_threads[uid].stop()
        del oscack.ack_threads[uid]
    except Exception as e:
        log.exception(
            "Try to unregister a ack send thread which doesn't exist :\n Error : " + str(e) + " \n UID : " + str(uid))
        log.exception("ACK_THREAD_REGISTER : " + str(oscack.ack_threads))
        log.exception("UID1, UID2 : " + str(uid))


def register(thread, uid):
    """
    Register a send thread in order to be stopped when received ACK
    :param thread:
    :param uid:
    :return:
    """
    log.log("raw", "Register thread send ack : " + str(uid))
    oscack.ack_threads[uid] = thread
    # globalContext.protocol.ack.ACK_THREAD_REGISTER[uid] = thread TODO: check and remove


def send_state(name, target, msg, args=(), kwargs={}):
    """
    This function return a state which send a message.
        the goal is to simplify the writting of protocol
    :param target: None = take target bia flag, other target are followed directly
    :param msg: Message to send
    :param args: List of args to take in flag to send in the message, True = take all of msg args in flag
    :param kwargs: Dict of additional args to send
    :return: send state function
    """
    if args is True:  # Args are all of msg args name
        args = [x[1] for x in msg.values]

    def _send_state(flag):
        _kwargs = {}
        for arg in args:
            _kwargs[arg] = flag.args["msg_"+arg]
        if target is None:
            host = Address(flag.args["src"].get_hostname())
        else:
            host = target
        _kwargs.update(kwargs)
        send(host, msg.get(**_kwargs))

    return fsm.State(name, _send_state)

