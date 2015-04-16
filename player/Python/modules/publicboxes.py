from engine.threads import patcher
from engine.fsm import Flag
from engine.log import init_log
from scenario import publicbox
log = init_log("publicboxes")

@publicbox('[signal]')
def sendSignal(flag, **kwargs):
    signal_uid = kwargs['args']["signal"] if 'signal' in kwargs['args'] else None
    signal = Flag(signal_uid, TTL=1, JTL=3)
    patcher.patch(signal.get())
    log.log("debug", "box sendsignal : "+signal_uid)
