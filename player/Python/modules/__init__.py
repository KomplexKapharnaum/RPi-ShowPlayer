# -*- coding: utf-8 -*-
import os
from scenario.classes import Patch, Etape
from engine.log import init_log
log = init_log("modules")

MODULES = dict()
DECLARED_FUNCTIONS = dict()
DECLARED_ETAPES = dict()
DECLARED_SIGNALS = dict()
DECLARED_PATCHER = dict()
DECLARED_OSCROUTES = dict()
DECLARED_TRANSITION = dict()
DECLARED_PUBLICSIGNALS = []
DECLARED_PUBLICBOXES = dict()

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
        global DECLARED_ETAPES, DECLARED_TRANSITION
        DECLARED_ETAPES[self.uid] = Etape(self.uid, actions=((f, self.options),))
        DECLARED_TRANSITION[self.uid] = self.transitions
        return self.uid


class publicbox(object):
    def __init__(self, args='', start=False):
        self.start = start
        self.args = [arg.strip('[').strip(']') for arg in args.split(' ')]

    def __call__(self, f):
        global DECLARED_PUBLICBOXES
        DECLARED_PUBLICBOXES[f.__name__.upper()+'_PUBLICBOX'] = {'function': f,
                                                                    'args': self.args,
                                                                    'start': self.start}


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
                    args = [arg[1:-1] for arg in oscargs]
                    args.append('dispo')
                    DECLARED_OSCROUTES[oscpath] = {'signal': signal_osc,
                                                    'args': args}
                # Internal transition
                else:
                    signal_osc = oscpath.upper()
            # Add transition
            self.transitions[signal_osc] = self.oscroutes[osccmd].upper()
        return super(link, self).__call__(f)


def exposesignals(sigs=dict()):
    global DECLARED_PUBLICSIGNALS
    for key, filter in sigs.items():
        if len(filter) > 0 and filter[-1] is True:
            DECLARED_PUBLICSIGNALS.append(key)



# Auto Import Every Modules
for module in os.listdir(os.path.dirname(__file__)):
    if module == '__init__.py' or module == 'module.py' or module[-3:] != '.py':
        continue
    __import__(module[:-3], locals(), globals())
del module
