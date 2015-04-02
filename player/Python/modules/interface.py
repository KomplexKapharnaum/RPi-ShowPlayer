
from modules.module import ExternalProcess
from scenario.classes import Etape
from engine.setting import settings
from engine.log import init_log

log = init_log("INTERFACE")


# Server Thread module
class Webserver(ExternalProcess):
    """
    Serving interface to Web Browser
    """
    def __init__(self):
        ExternalProcess.__init__(self)
        self.command = "python2 {script}".format(script=settings.get("path", "interface"))
        self.start()


# ETAPE AND SIGNALS
def interface_start(flag, **kwargs):
    if "interface" not in kwargs["_fsm"].vars.keys():
        kwargs["_fsm"].vars["interface"] = Webserver()
    elif not kwargs["_fsm"].vars["interface"].is_alive():
        kwargs["_fsm"].vars["interface"].start()


# REGISTER ETAPES & SIGNALS
etape_interface_start = Etape("INTERFACE_START", actions=((interface_start, {}), ))
