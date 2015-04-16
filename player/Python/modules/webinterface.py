
# from modules import ExternalProcess
from _classes import module
from scenario import link
# from engine.setting import settings
from engine.log import init_log

import threading
from interface import server

log = init_log("interface")


# Server Thread module
# class Webserver(ExternalProcess):
#     """
#     Serving interface to Web Browser
#     """
#     def __init__(self):
#         ExternalProcess.__init__(self)
#         self.name = 'webinterface'
#         self.command = "python2 {script}".format(script=settings.get("path", "interface"))
#         self.start()

class Webserver():
    def __init__(self):
        self._thread = threading.Thread(target=server.start)
        self._thread.start()


# ETAPE AND SIGNALS
@module('WebInterface')
@link({})
def interface_start(flag, **kwargs):
    if "interface" not in kwargs["_fsm"].vars.keys():
        kwargs["_fsm"].vars["interface"] = Webserver()
    # elif not kwargs["_fsm"].vars["interface"].is_alive():
    #     kwargs["_fsm"].vars["interface"].start()
