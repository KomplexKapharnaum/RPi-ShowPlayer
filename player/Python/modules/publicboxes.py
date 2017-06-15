import time
import threading
import os
import json

import liblo

from engine.threads import patcher
from engine.fsm import Flag
from engine.log import init_log
from engine.setting import settings
from engine.tools import search_in_or_default
from scenario import pool
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

@publicbox('[duration:float] [signal:str]', default=settings.get("values",
                                                                 "autodelay"), timer=True)
def auto_delay(flag, **kwargs):
    """
    This function (box) delay for a givent time and emit a signal at the end
    :param flag:
    :param kwars:
    :return:
    """
    signal_uid = kwargs['args']["signal"] if 'signal' in kwargs['args'] else None
    duration = search_in_or_default("duration", kwargs['args'], default=0)
    signal = Flag(signal_uid, TTL=float(duration) + 0.5, JTL=1).get()
    kwargs["_etape"]._localvars["__timer"] = list()
    kwargs["_etape"]._localvars["__timer"].append(threading.
        Timer(float(duration), patcher.patch, (signal, ), dict()))
    kwargs["_etape"]._localvars["__timer"][0].start()


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
    signal_uid = "{signal}_{dispo}".format(signal=params["signal"] if params[
        "signal"] != "" else settings.get("values", "split_dispo", "signal"),
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

def __kxkm_next_titreur(lines, m_type, m_speed, m_delay,
                            m_loop, timer):

    # setMessage(lines["lines"][lines["current"]][0].decode("utf8"),
    #            lines["lines"][lines["current"]][0].decode("utf8"), m_type,
    #            m_speed)
    patcher.serve(Flag("TITREUR_MESSAGEPLUS", args={
        'ligne1':lines["lines"][lines["current"]][0].decode("utf8"),
        'ligne2':lines["lines"][lines["current"]][1].decode("utf8"),
        'type':m_type,
        'speed':m_speed
    }
                ))
    lines["current"] += 1
    if lines["current"] == len(lines["lines"]):
        if m_loop is True:
            lines["current"] = 0
        else:
            ()
            timer[0] = threading.Timer(float(m_delay), patcher.patch,
                                       (Flag("END_TEXT", JTL=0.5+float(m_delay)).get(), ))
            timer[0].start()
            return
    timer[0] = threading.Timer(float(m_delay), __kxkm_next_titreur,
                               (lines,
                                m_type,
                                m_speed,
                                m_delay,
                                m_loop,
                                timer))
    timer[0].start()


@publicbox("[dispo] [media] [ids:str] [delay:float] [loop:int] [type:str] ["
           "speed:str]", category="titreur",
           timer=True)
def text_multi(flag, **kwargs):
    concerned = False
    for dest in kwargs['args']['dest']:
        if dest in ['All', 'Self', 'Group', settings.get('uName')]:
            concerned = True
    if not concerned:
        log.debug("Skip TEXT_MULTI because not concerned")

    media = kwargs['args']["media"]
    if media not in pool.Texts.keys():
        log.warning("text file {} not exist ! : {}".format(
            media, pool.Texts))
        return
    params = search_in_or_default(("delay", "loop", "type", "speed"), kwargs['args'],
                                  setting=("values", "text_multi"))
    m_txt1 = ''
    m_txt2 = ''
    m_type = params["type"]
    m_speed = params["speed"]
    m_delay = params["delay"]
    m_loop = True if params["loop"] == 1 else False

    ids = kwargs['args']["ids"].split(",")
    lines = list()


    for line_id in ids:
        if line_id in pool.Texts[media].keys():
            lines.append(pool.Texts[media][line_id])
        else:
            lines.append(("..missing..", ""))
            log.warning("Missing id {} in TEXT_MULTI box".format(id))



    kwargs["_etape"]._localvars["__timer"] = list()
    kwargs["_etape"]._localvars["__timer"].append(
        threading.Timer(float(0), __kxkm_next_titreur, ({"lines": lines,
                                                         "current": 0},
                                                        m_type,
                                                        m_speed,
                                                        m_delay,
                                                        m_loop,
                                                        kwargs["_etape"]._localvars[
                                                            "__timer"]
                                                        )))
    kwargs["_etape"]._localvars["__timer"][0].start()
