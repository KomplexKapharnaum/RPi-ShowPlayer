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

@publicbox('[signal] [dispo]')
def sendSignal(flag, **kwargs):
    '''
    SENDSIGNAL Box: Emmit SIGNAL to DEST
    '''
    signal_uid = kwargs['args']["signal"] if 'signal' in kwargs['args'] else None
    signal = Flag(signal_uid, TTL=1, JTL=3)
    patcher.patch(signal.get(dict(kwargs["args"])))
    log.log("raw", "SEND BOX : "+signal_uid)

@publicbox('[signal] [TTL] [JTL] [dispo]')
def sendSignalPlus(flag, **kwargs):
    '''
    SENDSIGNAL Box: Emmit SIGNAL to DEST
    '''
    log.error("send signal : {0}".format(kwargs['args']))
    signal_uid = kwargs['args']["signal"] if 'signal' in kwargs['args'] else None
    if 'TTL' in kwargs['args'].keys() and kwargs['args']['TTL'] is not None:
        TTL = float(kwargs['args']['TTL'])
    else:
        TTL = 1
    if 'JTL' in kwargs['args'].keys() and kwargs['args']['JTL'] is not None:
        JTL = float(kwargs['args']['JTL'])
    else:
        JTL = 3
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


@publicbox('[duration]')
def delay(flag, **kwargs):
    """
    This function (box) delay for a givent time and be ready for a transition after that
    :param flag:
    :param kwars:
    :return:
    """
    duration = search_in_or_default("duration", kwargs['args'], default=0)
    time.sleep(float(duration))


@publicbox('[ip] [port] [msg]')
def rawosc(flag, **kwargs):
    """
    This function send a raw OSC message to an IP : PORT
    :param flag:
    :param kwars:
    :return:
    """
    ip = kwargs['args']['ip']
    port = int(kwargs['args']['port'])
    liblo.send(liblo.Address(ip, int(port)), liblo.Message(*kwargs['args']['msg'].split(' ')))
