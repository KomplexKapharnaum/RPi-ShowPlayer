from engine.threads import patcher
from engine.fsm import Flag
from engine.log import init_log
from engine.setting import settings
from scenario import publicbox
log = init_log("public")

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
    log.log("debug", "SEND BOX : "+signal_uid)


@publicbox('[dispo]', start=True)
def start(flag, **kwargs):
    '''
    START Box: for concerned DEST only
    '''
    log.log("debug", "START BOX")
    concerned = False
    for dest in kwargs['args']['dest']:
        if dest in ['All', 'Self', 'Group', settings.get('uName')]:
            concerned = True
    if not concerned:
        kwargs['_fsm'].stop()
