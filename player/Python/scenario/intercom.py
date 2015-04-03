
import cPickle

from scenario import globalpatcher
from engine.threads import patcher
from engine.log import init_log
log = init_log("intercom")

@globalpatcher("SIGNAL_FORWARDER", "RECV_MSG")
def forward_signal(*args, **kwargs):
    """
    This function forward signal embeded in OSC message with path /signal
    :return:
    """
    if args[0].args["path"] == '/signal':
        log.debug('Forwarded signal received {0}'.format(args[0].args["args"][0]))
        patcher.serve(cPickle.loads(args[0].args["args"][1]))
    else:
        return False


# REGISTER PATCHER
# Patch("SIGNAL Forwarder", "RECV_MSG", (forward_signal, dict()))
