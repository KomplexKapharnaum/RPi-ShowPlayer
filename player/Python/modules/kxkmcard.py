# -*- coding: utf-8 -*-
#
# This file provide utilities for controlling Video
#
#
from modules import ExternalProcess
from scenario import link, exposesignals, module
from engine.log import init_log, dumpclean
from engine.setting import settings
from libs.oscack.utils import get_ip
log = init_log("kxkmcard")

##
# FILTERS
def initHw(card, cmd):
    card.say(
        'initconfig -titreurNbr 1 -carteVolt 24 -name {name} -ip {ip}'
        .format(name=settings.get("uName"), ip=get_ip()))

def btnUp(card, cmd):
    if float(cmd[1]) > 0:
        return True

def btnDown(card, cmd):
    if float(cmd[1]) == 0:
        return True

class KxkmCard(ExternalProcess):
    """
    KXKM Ext card module
    """
    def __init__(self):
        ExternalProcess.__init__(self, 'kxkmcard')
        self.onClose = "CARD_EVENT_CLOSE"
        self.start()

    @staticmethod
    def setFilters():
        return {
            'INITHARDWARE': [initHw],
            'CARTE_PUSH_1': [btnUp, True],
            'CARTE_PUSH_2': [btnUp, True],
            'CARTE_PUSH_3': [btnUp, True],
            'CARTE_FLOAT': [btnUp, True]
        }

    # def signals(self, cmd, args):
    #     # DONT'T ROUTE FOR 0 VALUES
    #     if cmd not in self.commands().keys() or args[0] != '0':
    #         super(KxkmCard, self).signals(cmd, args)


exposesignals(KxkmCard.setFilters())



# ETAPE AND SIGNALS
@module()
@link({"KXKMCARD_EVENT": "kxkm_card_event",
       "/titreur/message [ligne1] [ligne2]": "kxkm_card_titreur"})
def kxkm_card(flag, **kwargs):
    if "kxkmcard" not in kwargs["_fsm"].vars.keys():
        kwargs["_fsm"].vars["kxkmcard"] = KxkmCard()
        # kwargs["_fsm"].vars["kxkmcard"].say(
        #  'initconfig -titreurNbr 1 -carteVolt 24 -name {name} -ip {ip}'
        #  .format(name=settings.get("uName"), ip=get_ip()))


@link({None: "kxkm_card"})
def kxkm_card_event(flag, **kwargs):

    if flag.args['path'] == '#INITHARDWARE':
        kwargs["_fsm"].vars["kxkmcard"].say(
            'initconfig -titreurNbr 1 -carteVolt 24 -name {name} -ip {ip}'
            .format(name=settings.get("uName"), ip=get_ip()))


@link({'/test/ok': "kxkm_card"})
def kxkm_card_event(flag, **kwargs):
    pass


@link({None: "kxkm_card"})
def kxkm_card_titreur(flag, **kwargs):
    cmd = 'texttitreur'
    if flag.args["ligne1"] is not None:
        cmd += ' -line1 '+flag.args["ligne1"].replace(' ', '_')
    if flag.args["ligne2"] is not None:
        cmd += ' -line2 '+flag.args["ligne2"].replace(' ', '_')

    kwargs["_fsm"].vars["kxkmcard"].say(cmd)
    kwargs["_etape"].preemptible.set()



