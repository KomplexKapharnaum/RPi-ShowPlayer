# -*- coding: utf-8 -*-
#
# This file provide utilities for controlling Video
#
#
import re
from _classes import ExternalProcess, module
from scenario import link, exposesignals
from engine.log import init_log
from engine.setting import settings
from libs.oscack.utils import get_ip
log = init_log("kxkmcard")

FILTERS = dict()



class KxkmCard(ExternalProcess):
    """
    KXKM Ext card module
    """
    def __init__(self):
        ExternalProcess.__init__(self, 'kxkmcard')
        self.onClose = "CARD_EVENT_CLOSE"
        self.start()

    ##
    # COMMANDS
    def setRelais(self, switch):
        cmd = 'setrelais'
        if switch:
            cmd += ' -on'
        else:
            cmd += ' -off'
        self.say(cmd)

    def setMessage(self, line1=None, line2=None):
        cmd = 'texttitreur'
        if line1 is not None:
            cmd += ' -line1 '+line1.replace(' ', '_')
        if line2 is not None:
            cmd += ' -line2 '+line2.replace(' ', '_')
        self.say(cmd)

    def setLight(self, rgb=None, led10A=None, led10B=None, strob=None, fade=None):
        cmd = 'setlight'
        if rgb is not None:
            rgb = re.split('\W+', rgb)
            if len(rgb) == 0:
                rgb = str(rgb)
                rgb = rgb.lstrip('#')
                lv = len(rgb)
                rgb = list(str(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))
            if len(rgb) == 3:
                cmd += ' -rgb {R} {G} {B}'.format(R=rgb[0], G=rgb[1], B=rgb[2])
        if led10A is not None:
            cmd += ' -10w1 {0}'.format(int(led10A))
        if led10B is not None:
            cmd += ' -10w2 {0}'.format(int(led10B))
        if strob is not None:
            cmd += ' -strob {0}'.format(int(strobe))
        if fade is not None:
            cmd += ' -fade {0}'.format(int(fade))
        self.say(cmd)

    def setGyro(self, speed=None, strob=None, mode=None):
        cmd = 'setgyro'
        if speed is not None:
            cmd += ' -speed {0}'.format(int(speed))
        if strob is not None:
            cmd += ' -strob {0}'.format(int(strob))
        if mode is not None:
            cmd += ' -mode {0}'.format(mode)
        self.say(cmd)

    ##
    # FILTERS
    def initHw(self, cmd=None):
        self.say(
            'initconfig -titreurNbr 1 -carteVolt 24 -name {name} -ip {ip} -version {v} -status {status}'
            .format(name=settings.get("uName"), ip=get_ip(), v=settings.get("version"), status='morning..'))
        return False

    def sendInfo(self, cmd=None):
        self.say('info -status {status}'.format(status='yeah!'))
        return False

    def translate(self, cmd=None, args=[]):
        if len(args) > 0:
            cmd[0] = args[0]
            self.emmit(cmd)
            return False
        return True

    def testRoutine(self, cmd=None):
        self.say('testroutine -nbr 2')
        return True

    def btnDown(self, cmd):
        return float(cmd[1]) > 0

    def btnUp(self, cmd):
        return float(cmd[1]) == 0


    Filters = {
        'INITHARDWARE': ['initHw'],
        'TELECO_GET_INFO': ['sendInfo'],

        'CARTE_PUSH_1': ['btnDown', True],
        'CARTE_PUSH_2': ['btnDown', True],
        'CARTE_PUSH_3': ['btnDown', True],
        'CARTE_FLOAT': ['btnDown', True],

        'TELECO_PUSH_A': ['btnDown', True],
        'TELECO_PUSH_B': ['btnDown', True],
        'TELECO_PUSH_OK': ['btnDown', True],

        'TELECO_PUSH_REED': [True],
        'TELECO_PUSH_FLOAT': [True],

        'TELECO_MESSAGE_BLINKGROUP': [],
        'TELECO_MESSAGE_TESTROUTINE': ['testRoutine'],

        'TELECO_MESSAGE_PREVIOUSSCENE': ['translate /scene/previous', True],
        'TELECO_MESSAGE_RESTARTSCENE': ['translate /scene/restart', True],
        'TELECO_MESSAGE_NEXTSCENE': ['translate /scene/next', True],
        'TELECO_MESSAGE_POWEROFF': ['translate /device/poweroff'],
        'TELECO_MESSAGE_REBOOT': ['translate /device/reboot'],
    }


exposesignals(KxkmCard.Filters)



# ETAPE AND SIGNALS
@module('KxkmCard')
@link({"/titreur/message [ligne1] [ligne2]": "kxkm_card_titreur_message",
       "/titreur/texte [media] [numero]": "kxkm_card_titreur_text",
       "/carte/relais [on/off]": "kxkm_card_relais",
       "/carte/lights [rgb] [led10w-1] [led10w-2] [strob] [fade]": "kxkm_card_lights",
       "/carte/gyro [speed] [strob] [mode]": "kxkm_card_gyro"})
def kxkm_card(flag, **kwargs):
    if "kxkmcard" not in kwargs["_fsm"].vars.keys():
        kwargs["_fsm"].vars["kxkmcard"] = KxkmCard()


@link({None: "kxkm_card"})
def kxkm_card_relais(flag, **kwargs):
    switch = str(flag.args["on/off"]).lower() in ['None', 'off', '0']
    kwargs["_fsm"].vars["kxkmcard"].setRelais(switch)


@link({None: "kxkm_card"})
def kxkm_card_lights(flag, **kwargs):
    kwargs["_fsm"].vars["kxkmcard"].setLight(rgb=flag.args["rgb"],
                                                led10A=flag.args["led10w-1"], led10B=flag.args["led10w-2"],
                                                strob=flag.args["strob"], fade=flag.args["fade"])


@link({None: "kxkm_card"})
def kxkm_card_gyro(flag, **kwargs):
    kwargs["_fsm"].vars["kxkmcard"].setMessage(speed=flag.args["speed"], strob=flag.args["strob"], mode=flag.args["mode"])


@link({None: "kxkm_card"})
def kxkm_card_titreur_message(flag, **kwargs):
    kwargs["_fsm"].vars["kxkmcard"].setMessage(flag.args["ligne1"], flag.args["ligne2"])


@link({None: "kxkm_card"})
def kxkm_card_titreur_text(flag, **kwargs):
    pass


@link({None: "kxkm_card"})
def kxkm_card_titreur_text(flag, **kwargs):
    pass


@link({None: "kxkm_card"})
def kxkm_card_titreur_text(flag, **kwargs):
    pass


@link({None: "kxkm_card"})
def kxkm_card_titreur_text(flag, **kwargs):
    pass


@link({None: "kxkm_card"})
def kxkm_card_titreur_text(flag, **kwargs):
    pass


@link({None: "kxkm_card"})
def kxkm_card_titreur_text(flag, **kwargs):
    pass

