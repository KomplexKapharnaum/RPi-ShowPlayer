# -*- coding: utf-8 -*-
#
# This file provide utilities for controlling Video
#
#
from modules import ExternalProcess
from scenario import link
from engine.log import init_log
log = init_log("kxkmcard")


class KxkmCard(ExternalProcess):
    """
    KXKM Ext card module
    """
    def __init__(self):
        ExternalProcess.__init__(self, 'kxkmcard')
        self.onClose = "CARD_EVENT_CLOSE"
        self.start()

    def titreur(self, message=None, mode=None):
        self.say('#titreClear')
        if mode is not None:
            self.say('#titreMode '+mode)
        if message is not None:
            self.say('initname '+message)


# ETAPE AND SIGNALS
@link({"/titreur/message": "kxkm_card_titreur"})
def kxkm_card(flag, **kwargs):
    if "kxkmcard" not in kwargs["_fsm"].vars.keys():
        kwargs["_fsm"].vars["kxkmcard"] = KxkmCard()


@link({None: "kxkm_card"})
def kxkm_card_titreur(flag, **kwargs):
    message = flag.args["args"][0] if len(flag.args["args"]) >= 1 else None
    mode = flag.args["args"][1] if len(flag.args["args"]) >= 2 else None
    kwargs["_fsm"].vars["kxkmcard"].titreur(message=message, mode=mode)
    kwargs["_etape"].preemptible.set()
