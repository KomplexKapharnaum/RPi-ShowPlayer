# -*- coding: utf-8 -*-


import pool
from scenario.classes import Patch, Etape
from engine.fsm import Flag
from engine.log import init_log, dumpclean
log = init_log("scenario")

DECLARED_FUNCTIONS = dict()
DECLARED_ETAPES = dict()
DECLARED_SIGNALS = dict()
DECLARED_PATCHER = dict()
DECLARED_OSCROUTES = dict()
DECLARED_TRANSITION = dict()
DECLARED_MANAGER = []


def init_declared_objects():
    import functions
    import etapes
    import signals
    import modules
    global DECLARED_ETAPES, DECLARED_FUNCTIONS, DECLARED_SIGNALS, DECLARED_PATCHER, DECLARED_TRANSITION, DECLARED_OSCROUTES
    #dumpclean(DECLARED_TRANSITION)
    # ..
    # Attach declared Transition to declared Etapes and create corresponding signals
    for etape_uid, transition in DECLARED_TRANSITION.items():
        for signal_uid, goto_uid in transition.items():
            # If origine Etape exist
            if etape_uid in DECLARED_ETAPES:
                # Prevent Etape looping on himself with non blocking transition
                if (signal_uid is None or signal_uid is True) and etape_uid == goto_uid:
                    log.warning("Circular non blocking transition forbidden !")
                else:
                    # If valid signal, add it to the declared stack
                    if signal_uid is not None:
                        DECLARED_SIGNALS[signal_uid] = Flag(signal_uid)
                    # If goto is a valid Etape
                    if goto_uid in DECLARED_ETAPES:
                        DECLARED_ETAPES[etape_uid].transitions[signal_uid] = DECLARED_ETAPES[goto_uid]
                    # Or If goto is a valid Function
                    elif goto_uid in DECLARED_FUNCTIONS:
                        DECLARED_ETAPES[etape_uid].transitions[signal_uid] = DECLARED_FUNCTIONS[goto_uid]
                    else:
                        log.warning("Etape {0}: No destination {1} for declared transition".format(etape_uid, goto_uid))
            else:
                log.warning("Can't find Etape {0} to attach a declared transition".format(etape_uid))
    # ..
    # Import declared elements to Poll
    pool.Etapes_and_Functions.update(DECLARED_FUNCTIONS)
    pool.Etapes_and_Functions.update(DECLARED_ETAPES)
    pool.Signals.update(DECLARED_SIGNALS)
    #..
    # Import declared OSC routes in one common patcher
    if len(DECLARED_OSCROUTES) > 0:
        fn_sgn_patcher = pool.Etapes_and_Functions["MSG_SIGNAL_PATCHER"]
        DECLARED_PATCHER["DECLARED_OSCROUTES"] = Patch("DECLARED_OSCROUTES", "RECV_MSG", (fn_sgn_patcher, DECLARED_OSCROUTES))
    #..
    # Import declared Patches
    pool.Patchs.update(DECLARED_PATCHER)


class globalfunction(object):
    """
    This is a decorator which declare function in scenario scope
    """
    def __init__(self, public_name=None):
        """
        :param public_name: Name of the function in the scenario scope
        """
        self.public_name = public_name

    def __call__(self, f):
        if self.public_name is None:
            self.public_name = f.__name__
        global DECALRED_FUNCTIONS
        DECLARED_FUNCTIONS[self.public_name] = f
        return f


class globalpatcher(object):
    """
    This is a decorator which declare function as patcher in scenario scope
    """
    def __init__(self, public_name=None, trigger_signal=None, options=dict()):
        """
        :param public_name: Name of the function in the scenario scope
        """
        self.public_name = public_name
        self.trigger_signal = trigger_signal
        self.options = options

    def __call__(self, f):
        if self.public_name is None:
            self.public_name = f.__name__
        global DECLARED_PATCHER
        DECLARED_PATCHER[self.public_name] = Patch(self.public_name, self.trigger_signal, (f, self.options))
        return f


class oscpatcher(globalpatcher):
    def __init__(self, public_name=None, trigger_signal="RECV_MSG", options=dict()):
        globalpatcher.__init__(self, public_name, trigger_signal, options)


class globaletape(object):
    """
    This is a decorator which declare function as etape in scenario scope
    """
    def __init__(self, uid=None, transitions=dict(), options=dict(), autoload=False):
        """
        :param public_name: Name of the function in the scenario scope
        """
        self.uid = uid
        self.options = options
        self.transitions = transitions
        self.autoload = autoload

    def __call__(self, f):
        global DECLARED_ETAPES, DECLARED_TRANSITION, DECLARED_MANAGER
        DECLARED_ETAPES[self.uid] = Etape(self.uid, actions=((f, self.options),))
        DECLARED_TRANSITION[self.uid] = self.transitions
        # log.debug("DECLARE ETAPE: "+self.uid+" -> "+f.__name__)
        # for transfrom, transto in DECLARED_TRANSITION[self.uid].items():
            # log.debug("DECLARE TRANS: {0} -> {1}".format(transfrom,transto))
        if self.autoload and self.uid not in DECLARED_MANAGER:
            DECLARED_MANAGER.append(self.uid)
            log.debug("START ETAPE :: "+self.uid+" (Auto)")
        return f


class link(globaletape):
    """
    This is a decorator which declare function as etape
    The signal is added
    If an osc path is supplied, it is converted into signal, 
    and the corresponding patch is added
    """
    def __init__(self, routes=dict(), autoload=False):
        globaletape.__init__(self, None, dict(), dict(), autoload)
        self.oscroutes = routes

    def __call__(self, f):
        self.uid = f.__name__.upper()
        global DECLARED_OSCROUTES
        for oscpath in self.oscroutes.keys():
            if oscpath is None or oscpath == '':
                signal_osc = None
            elif oscpath[0] == '/':
                signal_osc = oscpath.replace('/','_')[1:].upper()
                DECLARED_OSCROUTES[oscpath] = signal_osc
                # log.debug("DECLARE ROUTE: "+oscpath+" -> "+signal_osc)
            else:
                signal_osc = oscpath.upper()
            self.transitions[signal_osc] = self.oscroutes[oscpath].upper()
        super(link, self).__call__(f)


def oscroute(from_oscpath, to_signal):
    DECLARED_OSCROUTES[from_oscpath] = to_signal
