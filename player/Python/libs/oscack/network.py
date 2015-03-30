# -*- coding: utf-8 -*-
#
# This file define network element and map
#
#

import threading


from engine.threads import network_scheduler
import libs.oscack
from engine import fsm
from engine import threads
from libs.oscack import message
# from oscack.protocol import discover
from engine.setting import settings
from engine.log import init_log
log = init_log("network")


# Read by server at stratup and add method
to_auto_add = []


recv_msg = fsm.Flag("RECV_MSG")


class NetworkElement:
    """
        This class describe an element over the network :
          uName  : Unique name of the element
          groups : Groups of the element (i.e. group1:group2:group23)
          IP     : IP address of the element
          near   : Boolean which describe if the element is near, get thoses iamhere messages
    """

    def __init__(self, uName, ip, near=False):
        self.uName = uName
        #self._groups_string = groups.split(":")
        self._groups = None
        #self.groups = groups  # There is a property trick here ;)
        self._ip = ip
        self.near = threading.Event()
        self.iamhere_recv = threading.Event()  # Set when received iamhere from this uName, use to clear near if not
        self.iamhere_recv.set()  # Set it at the init to avoid to eject him directly by the NetworkMap scheduler
        if near:
            self.near.set()
        self._target = None
        self.target = message.Address(ip)

    @property
    def ip(self):
        return self._ip

    @ip.setter
    def ip(self, ip):
        self._ip = ip
        self.target = message.Address(ip)

    @property
    def target(self):
        return self._target

    @target.setter
    def target(self, target):
        self._ip = target.get_hostname()
        self._target = target

    # @property
    # def groups(self):
    #     return self._groups
    #
    # @groups.setter
    # def groups(self, groups):
    #     self._groups_string = groups
    #     self._groups = groups.split(":")

    def __str__(self):
        return "NetworkElement : {uName}@{ip}, near : {near}".format(uName=self.uName,
                                                                    #groups=self._groups_string,
                                                                     ip=self._ip,
                                                                     near=self.near.is_set())


class NetworkMap(dict):  # TODO : Implement check neighbour
    """
        This class define the network map, it's a dict of NetworkElement, keys are uName
         ==> This dictionnary used locked to protect thread concurrency
    """

    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        self.lock = threading.RLock()
        self._delay_check_neighbourhood = settings.get("OSC", "checkneighbour_interval")
        #self._scheduler_id = globalContext.scheduler.protocol.enter(self._delay_check_neighbourhood,
        #                                                            self.check_neighbourhood)
        self._stop_sched_check_neighbourhood = threading.Event()

    def __getitem__(self, item):
        with self.lock:
            return dict.__getitem__(self, item)

    def __setitem__(self, key, value):
        with self.lock:
            return dict.__setitem__(self, key, value)

    def __delitem__(self, key):
        with self.lock:
            return dict.__delitem__(self, key)

    def __contains__(self, key):
        with self.lock:
            return dict.__contains__(self, key)

    def __len__(self):
        with self.lock:
            return dict.__len__(self)

    def __iter__(self):
        # log.log("raw", "NetworkMap iter")
        with self.lock:
            return dict.__iter__(self)

    def __str__(self):
        r = ""
        for netelem in self.values():
            r += str(netelem) + "\n"
        return r

    # def netelems_in(self, group):
    #     """
    #     This is a generator for parsing netelems of the network map which are in a given group
    #     :param group: the given group to watch for in netelems
    #     :return: yiel each netelem wich are in the given group
    #     """
    #     for netelem in self.values():
    #         if group in netelem.groups:
    #             yield netelem

    def check_neighbourhood(self):
        """
        This function is called by scheduler and regard if, for each netelem, we received a iamnewhere
        :return:
        """
        log.log("raw", "Cheking neighbourhood...")
        for netelem in self.values():
            if netelem.iamhere_recv.is_set() is not True:
                netelem.near.clear()
            netelem.iamhere_recv.clear()
        if self._stop_sched_check_neighbourhood.is_set() is False:  # Rescheduling
            self._scheduler_id = network_scheduler.enter(self._delay_check_neighbourhood,
                                                                        self.check_neighbourhood)


def add_signal_to_protocol(*args, **kwargs):
    """
    Wrapper for oscack.discover_machine.append_flag
    :param args:
    :param kwargs:
    :return:
    """
    libs.oscack.discover_machine.append_flag(*args, **kwargs)


class UnifiedMessageInterpretation:
    """
    This class provide a wrapper for an OSC message and provide a get_msg, and a recv_msg_function
    """

    def __init__(self, path, get=None, values=(), ACK=False, recv=None, JTL=settings.get("OSC", "JTL"), TTL=settings.get("OSC", "TTL"), ignore_cb=None,
                 ignore_cb_args=(), auto_add=True, connected=None):
        self.path = path
        if get is not None:
            def _get(*args, **kwargs):
                return get(path, *args, **kwargs)

            self.get = _get
        if recv is not None:
            self.recv = recv
        if connected is None:
            connected = (add_signal_to_protocol, )
        self.connected = connected
        self.values = values
        self.ACK = ACK
        self.JTL = JTL
        self.TTL = TTL
        self.ignore_cb = ignore_cb
        self.ignore_cb_args = ignore_cb_args
        # self.ignore_raise = ignore_raise
        if auto_add:
            global to_auto_add
            to_auto_add.append((path, None, self.recv))

    def recv(self, path, args, types, src):
        log.log("raw", "recv catch an message {path} with : {args}".format(path=path, args=args))
        kwargs = {}
        try:
            for i in xrange(len(args)):
                kwargs[self.values[i][1]] = args[i]
        except TypeError as e:
            log.error("Error parsing message : args : {args}, values : {values}".format(args=args, values=self.values))
            log.exception(e)
        log.log("raw", "add flag ..")
        flag = recv_msg.get(args={
            "path": path,
            "args": args,
            "kwargs": kwargs,
            "types": types,
            "src": src
        }, JTL=self.JTL, TTL=self.TTL, ignore_cb=self.ignore_cb,
           ignore_cb_args=self.ignore_cb_args)
        for fnct in self.connected:
            fnct(flag)
            log.log("raw", "Add flag with the function : {0}".format(fnct))
        log.log("raw", ".. add flag done")

    def get(self, *args, **kwargs):
        msg_args = list()
        for value in self.values:
            msg_args.append((value[0], kwargs[value[1]]))
        return message.Message(self.path, *msg_args, ACK=self.ACK)

    @staticmethod
    def conditional_transition(link={}):
        def _conditional_transition(flag):
            if flag.args["path"] in link.keys():
                return link[flag.args["path"]]
            else:
                return None

        return _conditional_transition


def get_flag_from_msg(path, args, types, src):
    """
    Basic flag creator for message
    :param path:
    :param args:
    :param types:
    :param src:
    :return:
    """
    log.log("raw", "recv catch an message {path} with : {args}".format(path=path, args=args))
    flag = recv_msg.get(args={
        "path": path,
        "args": args,
        "types": types,
        "src": src
    }, JTL=settings.get("OSC", "JTL"), TTL=settings.get("OSC", "TTL"))  # TODO : Set TTL and JTL and other as settings !
    return flag