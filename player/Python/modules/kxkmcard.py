# -*- coding: utf-8 -*-
#
# This file provide utilities for controlling Video
#
#
from modules import ExternalProcess
from scenario import link
from engine.log import init_log
from engine.setting import settings
from libs.oscack.utils import get_ip
log = init_log("kxkmcard")


class KxkmCard(ExternalProcess):
    """
    KXKM Ext card module
    """
    def __init__(self):
        ExternalProcess.__init__(self, 'kxkmcard')
        self.onClose = "CARD_EVENT_CLOSE"
        self.start()


# ETAPE AND SIGNALS
@link({"KXKMCARD_INITHARDWARE": "kxkm_card_init",
       "/titreur/message": "kxkm_card_titreur"})
def kxkm_card(flag, **kwargs):
    if "kxkmcard" not in kwargs["_fsm"].vars.keys():
        kwargs["_fsm"].vars["kxkmcard"] = KxkmCard()


@link({None: "kxkm_card"})
def kxkm_card_init(flag, **kwargs):
    kwargs["_fsm"].vars["kxkmcard"].say(
        'initconfig -titreurNbr 1 -carteVolt 24 -name {name} -ip {ip}'
        .format(name=settings.get("uName"), ip=get_ip()))


@link({None: "kxkm_card"})
def kxkm_card_titreur(flag, **kwargs):
    message = flag.args["args"][0] if len(flag.args["args"]) >= 1 else ''
    kwargs["_fsm"].vars["kxkmcard"].say('texttitreur -line1 '+message.replace(' ', '_'))
    kwargs["_etape"].preemptible.set()
