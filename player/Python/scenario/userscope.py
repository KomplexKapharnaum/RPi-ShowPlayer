from engine.threads import patcher
from engine.fsm import Flag
from engine.log import init_log
log = init_log("public")

#
# This file define user accessible function in the Scope of the Interface Editor
#

def sendSignal(uid):
    signal = Flag(uid, TTL=1, JTL=3)
    patcher.patch(signal.get())
    log.log("debug", "user signal : {0}".format(uid))