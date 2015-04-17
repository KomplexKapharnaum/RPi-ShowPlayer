
import cPickle

from modules import oscpatcher
from engine.threads import patcher
from engine.log import init_log
log = init_log("intercom")

@oscpatcher("SIGNAL_FORWARDER")
def forward_signal(*args, **kwargs):
    """
    This function forward signal embeded in OSC message with path /signal
    :return:
    """
    if args[0].args["path"] == '/signal':
        flag = cPickle.loads(str(bytearray(args[0].args["args"][1])))
        log.debug('Forwarded signal received {0}'.format(flag.get_info()))
        patcher.serve(flag)
    else:
        return False
