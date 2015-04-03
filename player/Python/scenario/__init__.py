# -*- coding: utf-8 -*-


import pool
from scenario.classes import Patch, Etape
from engine.fsm import Flag
from engine.log import init_log
log = init_log("scenario")

DECLARED_FUNCTIONS = dict()
DECLARED_ETAPES = dict()
DECLARED_SIGNALS = dict()
DECLARED_PATCHER = dict()
DECLARED_TRANSITION = dict()
DECLARED_MANAGER = []

def init_declared_objects():
    import functions
    import etapes
    import signals
    import modules
    global DECLARED_ETAPES, DECLARED_FUNCTIONS, DECLARED_SIGNALS, DECLARED_PATCHER, DECLARED_TRANSITION
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
        global DECLARED_ETAPES
        DECLARED_ETAPES[self.uid] = Etape(self.uid, actions=((f, self.options),))
        DECLARED_TRANSITION[self.uid] = self.transitions
        if self.autoload and self.uid not in DECLARED_MANAGER:
            DECLARED_MANAGER.append(self.uid)
            log.warning("AUTO MANAGER : "+self.uid)
        return f
