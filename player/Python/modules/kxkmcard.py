# -*- coding: utf-8 -*-
#
# This file provide utilities for controlling Video
#
#
import re
from _classes import ExternalProcess, module
from modules import link, exposesignals
from engine.log import init_log
from engine.setting import settings
from engine.tools import search_in_or_default
from libs.oscack.utils import get_ip, get_platform
from engine.tools import search_in_or_default
import json
import subprocess

log = init_log("kxkmcard")

FILTERS = dict()


class KxkmCard(ExternalProcess):
    """
    KXKM Ext card module
    """

    def __init__(self):
        if not settings.get("sys", "raspi"):
            log.warning("KXKM Card should not be launched on no raspi device ")
            return None
        plateform = subprocess.check_output(["/usr/bin/gcc", "-dumpmachine"])
        if "armv6l" in plateform:
            ExternalProcess.__init__(self, 'kxkmcard-armv6l')
        else:
            ExternalProcess.__init__(self, 'kxkmcard-armv7l')
        self.onClose = "CARD_EVENT_CLOSE"
        log.log("debug", "Starting KxkmCard {0}.. ".format(plateform))
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

    def setLedTelecoOk(self, switch):
        cmd = 'setledtelecook'
        if switch:
            cmd += ' -on'
        else:
            cmd += ' -off'
        self.say(cmd)

    def setLedCarteOk(self, switch):
        cmd = 'setledcarteok'
        if switch:
            cmd += ' -on'
        else:
            cmd += ' -off'
        self.say(cmd)

    def setMessage(self, line1=None, line2=None):
        cmd = 'texttitreur'
        if line1 is not None:
            if line1 == "":
                log.warning("Line 1 empty : does teleco prompt it ?")
            cmd += ' -line1 ' + line1.replace(' ', '_')
        if line2 is not None:
            if line2 == "":
                log.warning("Line 1 empty : does teleco prompt it ?")
            cmd += ' -line2 ' + line2.replace(' ', '_')
        self.say(cmd)

    def setLight(self, rgb=None, led10w1=None, led10w2=None, strob=None, fade=None):
        cmd = 'setlight'
        if strob is not None:
            cmd += ' -strob {0}'.format(int(strob))
        if fade is not None:
            cmd += ' -fade {0}'.format(int(fade))
        if rgb is not None:
            rgb = re.split('\W+', rgb)
            if len(rgb) == 0:
                rgb = str(rgb)
                rgb = rgb.lstrip('#')
                lv = len(rgb)
                rgb = list(str(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))  # TODO DEBUG HERE value
            if len(rgb) == 3:
                cmd += ' -rgb {R} {G} {B}'.format(R=rgb[0], G=rgb[1], B=rgb[2])
        if led10w1 is not None:
            cmd += ' -10w1 {0}'.format(int(led10w1))
        if led10w2 is not None:
            cmd += ' -10w2 {0}'.format(int(led10w2))

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

    def popUpTeleco(self, line1=None, line2=None):
        """
        send message on menu popup teleco
        :param line1:
        :param line2:
        :return:
        """
        cmd = 'popup'
        if line1 is not None:
            if line1 == "":
                log.warning("Line 1 empty : does teleco prompt it ?")
            cmd += ' -line1 ' + line1.replace(' ', '_')
        if line2 is not None:
            if line2 == "":
                log.warning("Line 1 empty : does teleco prompt it ?")
            cmd += ' -line2 ' + line2.replace(' ', '_')
        self.say(cmd)

    ##
    # FILTERS
    def initHw(self, cmd=None):
        """
        envoi les info de démarage à la carte
        :param cmd:
        :return:
        """
        log.log("raw", "Init HardWare on KxkmCard ..")
        path = settings.get_path('deviceslist')
        voltage = None
        titreur = None

        try:
            answer = dict()
            with open(path, 'r') as f:  # Use file to refer to the file object
                answer = json.loads(f.read())
            answer['status'] = 'success'
            for device in answer["devices"]:
                if device["hostname"] == settings.get("uName"):
                    voltage = device["tension"]
                    titreur = device["titreur"]
                    break
        except OSError as e:
            log.exception(log.show_exception(e))
            log.log("debug", "devices.json not found")

        self.say(
            'initconfig -carteVolt {volt} -name {name} -ip {ip} -version {v} -status {status} -titreurNbr {tit} '
            .format(name=settings.get("uName"), ip=get_ip(), v=settings.get("version"), status='morning..',
                    volt=voltage, tit=titreur))
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
       "/remote/popup [ligne1] [ligne2]": "kxkm_card_popup_teleco",
       "/remote/ledOkT [on/off]": "kxkm_card_lekOK_teleco",
       "/carte/ledOkC [on/off]": "kxkm_card_lekOK_card",
       "/lumiere/rgb [rgb] [strob] [fade]": "kxkm_card_lights",
       "/lumiere/led1 [led10w1] [strob] [fade]": "kxkm_card_lights",
       "/lumiere/led2 [led10w2] [strob] [fade]": "kxkm_card_lights",
       "/lumiere/gyro [mode] [speed] [strob]": "kxkm_card_gyro"})
def kxkm_card(flag, **kwargs):
    if "kxkmcard" not in kwargs["_fsm"].vars.keys():
        kwargs["_fsm"].vars["kxkmcard"] = KxkmCard()


@link({None: "kxkm_card"})
def kxkm_card_relais(flag, **kwargs):
    switch = str(flag.args["on/off"]).lower() in ['true', 'on', '1']
    kwargs["_fsm"].vars["kxkmcard"].setRelais(switch)

@link({None: "kxkm_card"})
def kxkm_card_lekOK_teleco(flag, **kwargs):
    switch = str(flag.args["on/off"]).lower() in ['true', 'on', '1']
    kwargs["_fsm"].vars["kxkmcard"].setLedTelecoOk(switch)

@link({None: "kxkm_card"})
def kxkm_card_lekOK_card(flag, **kwargs):
    switch = str(flag.args["on/off"]).lower() in ['true', 'on', '1']
    kwargs["_fsm"].vars["kxkmcard"].setLedCarteOk(switch)

@link({None: "kxkm_card"})
def kxkm_card_lights(flag, **kwargs):
    params = search_in_or_default(("rgb", "led10w1", "led10w2", "strob", "fade"),
                                  flag.args, setting=("values", "lights"))
    kwargs["_fsm"].vars["kxkmcard"].setLight(**params)


@link({None: "kxkm_card"})
def kxkm_card_gyro(flag, **kwargs):
    params = search_in_or_default(("speed", "strob", "mode"), flag.args, setting=("values", "gyro"))
    if None in params.values():
        log.warning("Missing default value for at least one argument : {0}".format(params))
    kwargs["_fsm"].vars["kxkmcard"].setGyro(**params)

@link({None: "kxkm_card"})
def kxkm_card_titreur_message(flag, **kwargs):
    kwargs["_fsm"].vars["kxkmcard"].setMessage(flag.args["ligne1"], flag.args["ligne2"])

@link({None: "kxkm_card"})
def kxkm_card_popup_teleco(flag, **kwargs):
    kwargs["_fsm"].vars["kxkmcard"].popUpTeleco(flag.args["ligne1"], flag.args["ligne2"])


@link({None: "kxkm_card"})
def kxkm_card_titreur_text(flag, **kwargs):
    pass



