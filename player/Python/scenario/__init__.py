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
DECLARED_MANAGERS = dict()
DECLARED_PUBLICSIGNALS = []


def init_declared_objects():
    import functions
    import modules
    global DECLARED_ETAPES, DECLARED_FUNCTIONS, DECLARED_SIGNALS, DECLARED_PATCHER, DECLARED_TRANSITION, DECLARED_OSCROUTES
    #dumpclean(DECLARED_TRANSITION)
    
    # ..
    # Import declared elements to Poll
    pool.Etapes_and_Functions.update(DECLARED_FUNCTIONS)
    
    #..
    # Import declared OSC routes in one common patcher
    if len(DECLARED_OSCROUTES.keys()) > 0:
        fn_sgn_patcher = pool.Etapes_and_Functions["MSG_SIGNAL_PATCHER"]
        oscroutes_patch = dict()
        for path, route in DECLARED_OSCROUTES.items():
            oscroutes_patch[path] = route
        DECLARED_PATCHER["DECLARED_OSCROUTES"] = Patch("DECLARED_OSCROUTES", "RECV_MSG", (fn_sgn_patcher, oscroutes_patch))
        #..
        # Create Etape Senders for OSCROUTES
        fn_sgn_sender = pool.Etapes_and_Functions["ADD_SIGNAL"]
        fn_auto_transit = pool.Etapes_and_Functions["TRANSIT_AUTO"]
        fn_auto_transit_clean = pool.Etapes_and_Functions["TRANSIT_CLEAN"]
        for path, route in DECLARED_OSCROUTES.items():
            etape_sender = Etape('SEND_'+route['signal'], actions=((fn_sgn_sender, {'signal':route['signal']}),
                                                                   (fn_auto_transit, {})),
                                                          out_actions= ((fn_auto_transit_clean, {}),)
                                                        )
            DECLARED_ETAPES[etape_sender.uid] = etape_sender

    #..
    # Import declared Patches
    pool.Patchs.update(DECLARED_PATCHER)


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
    pool.Etapes_and_Functions.update(DECLARED_ETAPES)
    pool.Signals.update(DECLARED_SIGNALS)


   


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
    def __init__(self, uid=None, transitions=dict(), options=dict()):
        """
        :param public_name: Name of the function in the scenario scope
        """
        self.uid = uid
        self.options = options
        self.transitions = transitions

    def __call__(self, f):
        global DECLARED_ETAPES, DECLARED_TRANSITION, DECLARED_MANAGERS
        DECLARED_ETAPES[self.uid] = Etape(self.uid, actions=((f, self.options),))
        DECLARED_TRANSITION[self.uid] = self.transitions
        return f


class module(object):
    def __init__(self, autoload=False):
        self.autoload = autoload

    def __call__(self, f):
        uid = f.__name__.upper()
        global DECLARED_MANAGERS
        DECLARED_MANAGERS[uid] = {'autoload':self.autoload}
        return f


class link(globaletape):
    """
    This is a decorator which declare function as etape
    The signal is added
    If an osc path is supplied, it is converted into signal, 
    and the corresponding patch is added
    """
    def __init__(self, routes=dict()):
        globaletape.__init__(self, None, dict(), dict())
        self.oscroutes = routes

    def __call__(self, f):
        self.uid = f.__name__.upper()
        global DECLARED_OSCROUTES
        for osccmd in self.oscroutes.keys():
            if osccmd is None or osccmd == '':
                # None transition
                signal_osc = None
                oscpath = None
            else:
                oscpath = osccmd.split(' ')[0]
                oscargs = osccmd.split(' ')[1:]
                
                # OSC Transition => create patch + etape sender
                if oscpath[0] == '/':
                    # log.debug("DECLARE ROUTE: "+oscpath+" -> "+signal_osc) 
                    signal_osc = oscpath.replace('/','_')[1:].upper()
                    DECLARED_OSCROUTES[oscpath] = {'signal': signal_osc,
                                                    'args': [arg[1:-1] for arg in oscargs]}
                # Internal transition
                else:
                    signal_osc = oscpath.upper()
            # Add transition
            self.transitions[signal_osc] = self.oscroutes[osccmd].upper()
        super(link, self).__call__(f)
        return f


def exposesignals(sigs=dict()):
    global DECLARED_PUBLICSIGNALS
    for key, filter in sigs.items():
        if len(filter) > 1 and filter[1]:
            DECLARED_PUBLICSIGNALS.append(key)

