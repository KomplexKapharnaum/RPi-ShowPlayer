# -*- coding: utf-8 -*-
import os
from scenario.classes import Patch, Etape
from engine.log import init_log
from engine.setting import settings
from engine import tools

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
        global DECLARED_ETAPES, DECLARED_TRANSITION, DECLARED_OSCROUTES
        signal = [signal for signal in DECLARED_OSCROUTES.values() if self.uid == signal['signal']]
        if len(signal) > 0:
            signal = signal[0]
            def fn(flag, *args, **kwargs):
                # if 'args' in kwargs.keys():
                #     kwargs['args'] = parse_args_etape_function(kwargs['args'], signal['args'], signal['types'], signal['default'])
                flag.args = parse_args_etape_function(flag.args, signal['args'], signal['types'], signal['default'])
                return f(flag, *args, **kwargs)
        else:
            fn = f
        DECLARED_ETAPES[self.uid] = Etape(self.uid, actions=((fn, self.options),))
        DECLARED_TRANSITION[self.uid] = self.transitions
        return DECLARED_ETAPES[self.uid]


# class dec_parse_args_etape_function(object):
#     """
#     This decorator create a new function which parsed arguments
#     """
#
#     def __init__(self, args=None, types=None, default=None):
#         """
#         :param args: Args list to parsed
#         :param types: Types list of args to parsed (same size)
#         :param default: Dict where search default values
#         :type args: list of str
#         :type types: list of str
#         :type default: dict
#         """
#         if args is None:
#             args = dict()
#         self.args = args
#         if types is None:
#             types = dict()
#         self.types = types


def parse_arg_from_type(arg, types):
    """
    This function perform the parsing a the givent value in function of the givent type
    :param arg: Arg to parse
    :param types: Type to parsed arg
    :type types: str
    :return:
    """
    try:
        log.debug("Parsing {0} of type {1} ..".format(arg, types))
        if types == "str":
            # log.warning("parsing str is not implemented")
            try:
                arg = arg.encode("utf8")
            except Exception:
                log.warning("Unable to parse str arg.. (can't prompt it safely), remove utf-8 char")
                arg = tools.remove_nonspacing_marks(arg)
        elif types == "int":
            arg = int(arg)
        elif types == "float":
            arg = float(arg)
        elif types == "bool":
            arg = arg.lower() in ['1','true','oui','yes','y','o']
        else:
            log.warning("parsing of {0} is not implemented at all".format(types))
    except Exception as e:
        log.error("Error during parsing {0} of type {1}".format(arg, types))
        log.error(log.show_exception(e))
    log.debug("End parsing {0} of type {1}".format(arg, types))
    return arg


def parse_args_etape_function(kwargs, args, types, default):
    """
        :param kwargs: Dict of args wich are givent to the etape function
        :param args: Args list to parsed
        :param types: Types list of args to parsed (same size)
        :param default: Dict where search default values
        :type kwargs: dict
        :type args: list of str
        :type types: list of str
        :type default: dict
        """
    log.debug("Pre-parse {0} for {1} types {2} default {3}".format(kwargs, args, types, default))
    for arg_n in xrange(len(args)):
        arg_name = args[arg_n]
        if arg_n < len(types):
            type_name = types[arg_n]
        else:
            type_name = "none"
        if arg_name not in kwargs.keys():
            if arg_name != "dispo":
                log.log("warning", "search for {0} in parameters but not found in {1}".format(arg_name, kwargs))
            continue
        if kwargs[arg_name] is None:  # There is no value.. searching for a default one
            if arg_name in default.keys():  # There is one default
                log.debug("Taking default value <{1}> for <{0}>".format(arg_name, default[arg_name]))
                kwargs[arg_name] = default[arg_name]
                continue
            elif type_name in settings.get("values", "types"):
                log.debug("Taking default types {1} value for {0}".format(arg_name,
                                                                          settings.get("values", "types", type_name)))
                kwargs[arg_name] = settings.get("values", "types", type_name)
                continue
            else:
                kwargs[arg_name] = parse_arg_from_type(kwargs[arg_name], type_name)
                log.warning("Set parameter {0} to {1}, because he was nonn, it's can be unwanted".format(arg_name, kwargs[arg_name]))
                continue
        else:
            kwargs[arg_name] = parse_arg_from_type(kwargs[arg_name], type_name)
            continue
    return kwargs


class publicbox(object):
    def __init__(self, args='', start=False, default=None):
        """
        :param args: args to ask from interface [param:paramtype]
        :param start: Set if it's a start box or not
        :param default: default value to take if args is not filled
        :type args: str
        :type start: bool
        :type default: dict
        """
        if default is None:
            default = dict()
        self.default = default
        self.start = start
        self.args = list()
        self.types = list()
        for arg in args.split(' '):
            unpack = arg.strip('[').strip(']').split(':')
            _arg = unpack[0]
            if len(unpack) > 1:
                _type = unpack[1]
            else:
                _type = None
            self.args.append(_arg)
            self.types.append(_type)

    def __call__(self, f):
        global DECLARED_PUBLICBOXES
        def fn(flag, *args, **kwargs):
            if 'args' in kwargs.keys():
                kwargs['args'] = parse_args_etape_function(kwargs['args'], self.args, self.types, self.default)
            return f(flag, *args, **kwargs)
        DECLARED_PUBLICBOXES[f.__name__.upper() + '_PUBLICBOX'] = {'function': fn,
                                                                   'args': self.args,
                                                                   'start': self.start,
                                                                   'types': self.types}


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
                    signal_osc = oscpath.replace('/', '_')[1:].upper()
                    # args, types = [arg[1:-1] for arg in oscargs].split(":")  # types is for parsing values after
                    args = list()
                    types = list()
                    for arg in oscargs:
                        unpack = arg[1:-1].split(':')
                        _arg = unpack[0]
                        if len(unpack) > 1:
                            _type = unpack[1]
                        else:
                            _type = None
                        args.append(_arg)
                        types.append(_type)
                    args.append('dispo')
                    if isinstance(self.oscroutes[osccmd], (tuple, list)):
                        default = self.oscroutes[osccmd][1]
                    else:
                        default = dict()
                    DECLARED_OSCROUTES[oscpath] = {'signal': signal_osc,
                                                   'args': args,
                                                   'types': types,
                                                   'default': default}
                # Internal transition
                else:
                    signal_osc = oscpath.upper()
            # Add transition
            if isinstance(self.oscroutes[osccmd], (tuple, list)):
                transition = self.oscroutes[osccmd][0].upper()
            else:
                transition = self.oscroutes[osccmd].upper()
            self.transitions[signal_osc] = transition
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
