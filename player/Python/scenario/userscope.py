from engine.threads import patcher
from engine.fsm import Flag
from engine.log import init_log
from engine.setting import settings
log = init_log("public")

#
# This file define user accessible function in the Scope of the Interface Editor
#

def sendSignal(uid):
    signal = Flag(uid, TTL=settings.get("scenario", "TTL"), JTL=settings.get("scenario", "JTL"))
    patcher.patch(signal.get())   # Removed get to improv perf (not necessary because it is generated just before
    log.log("debug", "user signal : {0}".format(uid))
