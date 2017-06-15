import time

import liblo

from engine.threads import patcher
from engine.fsm import Flag
from engine.log import init_log
from engine.setting import settings
from engine.tools import search_in_or_default
from modules import publicbox
log = init_log("publicbox")

#
# Declare function in DECLARED_PUBLICBOXES (scenario)
# Imported in the pool as ETAPE (by scenario init)
# Imported in interface as NAME_PUBLICFUNC
#

@publicbox('[signal:str] [dispo]')
def sendSignal(flag, **kwargs):
    '''
    SENDSIGNAL Box: Emmit SIGNAL to DEST
    '''
    signal_uid = kwargs['args']["signal"] if 'signal' in kwargs['args'] else None
    signal = Flag(signal_uid, TTL=settings.get("scenario", "TTL"), JTL=settings.get("scenario", "JTL"))
    patcher.patch(signal.get(dict(kwargs["args"])))
    log.log("raw", "SEND BOX : "+signal_uid)

@publicbox('[signal:str] [TTL:float] [JTL:int] [dispo]', default=settings.get("values", "signaux"))
def sendSignalPlus(flag, **kwargs):
    '''
    SENDSIGNAL Box: Emmit SIGNAL to DEST
    '''
    log.debug("send signal : {0}".format(kwargs['args']))
    signal_uid = kwargs['args']["signal"] if 'signal' in kwargs['args'] else None
    if 'TTL' in kwargs['args'].keys() and kwargs['args']['TTL'] is not None:
        TTL = float(kwargs['args']['TTL'])
    else:
        TTL = settings.get("scenario", "TTL")
    if 'JTL' in kwargs['args'].keys() and kwargs['args']['JTL'] is not None:
        JTL = float(kwargs['args']['JTL'])
    else:
        JTL = settings.get("scenario", "JTL")
    signal = Flag(signal_uid, TTL=TTL, JTL=JTL)
    patcher.patch(signal.get(dict(kwargs["args"])))
    log.log("raw", "SEND BOX : "+signal_uid)


@publicbox('[dispo]', start=True)
def start(flag, **kwargs):
    '''
    START Box: for concerned DEST only
    '''
    log.log("raw", "START BOX")
    concerned = False
    for dest in kwargs['args']['dest']:
        if dest in ['All', 'Self', 'Group', settings.get('uName')]:
            concerned = True
    if not concerned:
        kwargs['_fsm'].stop()


@publicbox('[none]')
def wait(flag, **kwargs):
    '''
    START Box: for concerned DEST only
    '''
    pass


@publicbox('[duration:float]')
def delay(flag, **kwargs):
    """
    This function (box) delay for a givent time and be ready for a transition after that
    :param flag:
    :param kwars:
    :return:
    """
    duration = search_in_or_default("duration", kwargs['args'], default=0)
    time.sleep(float(duration))


@publicbox('[signal:str]')
def split_dispo(flag, **kwargs):
    """
    This function (box) send a signal with the dispo name inside in order
    to allow you to split the fsm logic depending of which dispo is running it
    :param flag:
    :param kwars:
    :return:
    """
    params = search_in_or_default(("signal", ),
                                  kwargs['args'],
                                  setting=("values", "split_dispo"))
    signal_uid = "{signal}_{dispo}".format(signal=params["signal"],
                                           dispo=settings.get('uName'))
    signal = Flag(signal_uid, TTL=settings.get("scenario", "TTL"),
                  JTL=settings.get("scenario", "JTL"))
    patcher.patch(signal.get())
    log.log("raw", "SEND BOX : " + signal_uid)


@publicbox('[ip:str] [port:int] [msg:str]')
def rawosc(flag, **kwargs):
    """
    This function send a raw OSC message to an IP : PORT
    :param flag:
    :param kwars:
    :return:
    """
    ip = kwargs['args']['ip']
    port = int(kwargs['args']['port'])
    msg = kwargs['args']['msg'].split(' ')
    path = msg[0]
    args = list()
    for arg in msg[1:]:
        if len(arg) > 2:
            if "_" == arg[0]:
                arg = (arg[1], arg[2:])
        args.append(arg)
    liblo.send(liblo.Address(ip, int(port)), liblo.Message(path, *args))
