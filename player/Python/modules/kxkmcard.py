# -*- coding: utf-8 -*-
#
# This file provide utilities for controlling Video
#
#
import re
import threading
from _classes import ExternalProcessFlag, module
from scenario import classes
from modules import link, exposesignals
from engine.log import init_log
from engine.setting import settings, devicesV2
from engine.threads import patcher
from engine.tools import search_in_or_default
from libs.oscack.utils import get_ip, get_platform
import json
import subprocess

log = init_log("kxkmcard")

FILTERS = {
    # filtre qui s'enchaine, si les fonctions appelées return true, alors passe à la suivante
    # le dernier true de la ligne rend le signal dispo pour l’éditeur de scénario
    'INITHARDWARE': ['initHw'],
    'HARDWAREREADY': ['transTo /hardware/ready'],
    'TELECO_GET_INFO': ['sendInfo'],

    'CARTE_PUSH_1': ['btnDown', True],
    'CARTE_PUSH_2': ['btnDown', True],
    'CARTE_PUSH_3': ['btnDown', True],
    'CARTE_FLOAT': ['btnDown', True],

    'CARTE_MESSAGE_POWEROFF': [True],

    "CARTE_TENSION": ['transTo /device/updateTension'],
    "CARTE_TENSION_BASSE": ['transTo /device/warningTension'],

    'TELECO_PUSH_A': ['btnDown', True],
    'TELECO_PUSH_B': ['btnDown', True],
    'TELECO_PUSH_OK': ['btnDown', True],

    'TELECO_PUSH_REED': [True],
    'TELECO_PUSH_FLOAT': [True],

    # old version for compatibility

    'TELECO_MESSAGE_BLINKGROUP': [],
    'TELECO_MESSAGE_TESTROUTINE': ['testRoutine'],

    'TELECO_MESSAGE_PREVIOUSSCENE': ['transTo /scene/previous', True],
    'TELECO_MESSAGE_RESTARTSCENE': ['transTo /scene/restart', True],
    'TELECO_MESSAGE_NEXTSCENE': ['transTo /scene/next', True],

    'TELECO_MESSAGE_POWEROFF': ['transTo /device/poweroff'],
    'TELECO_MESSAGE_REBOOT': ['transTo /device/reboot'],

    "TELECO_MESSAGE_RESTARTWIFI": ['transTo /device/wifi/restart'],
    "TELECO_MESSAGE_UPDATESYS": ['transTo /device/updatesys'],


    # new version

    "TELECO_MESSAGE_PREVIOUSSCENE": ['transTo /scene/previous', True],  #argument Self / Group / All
    "TELECO_MESSAGE_RESTARTSCENE": ['transTo /scene/restart', True], #argument Self / Group / All
    "TELECO_MESSAGE_NEXTSCENE": ['transTo /scene/next', True], #argument Self / Group / All


    "TELECO_MESSAGE_SETTINGS_LOG_DEBUG": [],
    "TELECO_MESSAGE_SETTINGS_LOG_ERROR": [],
    "TELECO_MESSAGE_SETTINGS_VOLPLUS": [],
    "TELECO_MESSAGE_SETTINGS_VOLMOINS": [],
    "TELECO_MESSAGE_SETTINGS_VOLSAVE": [],
    "TELECO_MESSAGE_SETTINGS_VOLBACK": [],

    "TELECO_MESSAGE_MODE_SHOW": [],
    "TELECO_MESSAGE_MODE_REPET": [],
    "TELECO_MESSAGE_MODE_DEBUG": [],
    "TELECO_MESSAGE_LOG_ERROR": [],
    "TELECO_MESSAGE_LOG_DEBUG": [],

    "TELECO_MESSAGE_BLINKGROUP": [],
    "TELECO_MESSAGE_TESTROUTINE": ['testRoutine'],

    "TELECO_MESSAGE_SYS_RESTARTPY": [],
    "TELECO_MESSAGE_SYS_RESTARTWIFI": ['transTo /device/wifi/restart'],
    "TELECO_MESSAGE_SYS_UPDATESYS": ['transTo /device/updatesys'],
    "TELECO_MESSAGE_SYS_POWEROFF": ['transTo /device/poweroff'],
    "TELECO_MESSAGE_SYS_REBOOT": ['transTo /device/reboot'],

    "TELECO_MESSAGE_GET_INFO": [],

    "TELECO_MESSAGE_MEDIA_VOLPLUS": ['transTo /media/volup'], #argument Self / Group / All TODO : clean this
    "TELECO_MESSAGE_MEDIA_VOLMOINS": ['transTo /media/voldown'], #argument Self / Group / All TODO : clean this
    "TELECO_MESSAGE_MEDIA_MUTE": [], #argument Self / Group / All
    "TELECO_MESSAGE_MEDIA_PAUSE": [], #argument Self / Group
    "TELECO_MESSAGE_MEDIA_PLAY": [], #argument Self / Group
    "TELECO_MESSAGE_MEDIA_STOP": [] #argument Self / Group
}


class KxkmCard(ExternalProcessFlag):
    """
    This class define the KXKM card
    """

    def __init__(self):
        if not settings.get("sys", "raspi"):
            log.warning("KXKM Card should not be launched on no raspi device ")
            return None
        plateform = subprocess.check_output(["/usr/bin/gcc", "-dumpmachine"])
        if "armv6l" in plateform:
            ExternalProcessFlag.__init__(self, 'kxkmcard-armv6l', filters=FILTERS)
            log.debug('CARD: kxkmcard-armv6l')
        else:
            ExternalProcessFlag.__init__(self, 'kxkmcard-armv7l', filters=FILTERS)
            log.debug('CARD: kxkmcard-armv7l')

    def say(self, msg):
        """
        Retro compatibility for old style ExternalProcess : put msg into stdin queue
        :param msg:
        :return:
        """
        self.stdin_queue.put_nowait(msg)

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
        if line1 is not None and not line1 == "":
            cmd += ' -line1 ' + line1.replace(' ', '_')
        if line2 is not None and not line2 == "":
            cmd += ' -line2 ' + line2.replace(' ', '_')
        self.say(cmd)

    def setLight(self, rgb=None, led10w1=None, led10w2=None, strob=None, fade=None):
        cmd = 'setlight'
        if strob is not None and strob != '' and int(strob) > 0:
            cmd += ' -strob {0}'.format(int(strob))
        if fade is not None and fade != '' and int(fade) > 0:
            cmd += ' -fade {0}'.format(int(fade))
        if rgb is not None:
            rgb = re.split('\W+', rgb)
            if len(rgb) == 0:
                rgb = str(rgb)
                rgb = rgb.lstrip('#')
                lv = len(rgb)
                rgb = list(rgb[i:i + lv // 3] for i in range(0, lv, lv // 3))
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

    def popUpTeleco(self, line1=None, line2=None, page=None):
        """
        send message on menu popup teleco
        :param line1:
        :param line2:
        :param page: could be "log" "scenario" "usb" "media" "sync" "user" "error"
        :return:
        """
        cmd = 'popup'
        if page is not None:
            cmd += ' -type {0}'.format(page)
            if line1 is not None and not line1 == "":
                cmd += ' -line1 ' + line1.replace(' ', '_')
            if line2 is not None and not line2 == "":
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
        log.log("important", "Init HardWare on KxkmCard ..")
        voltage = devicesV2.get(settings.get("uName"), "tension")
        titreur = devicesV2.get(settings.get("uName"), "titreur")
        invertedSwitch = devicesV2.get(settings.get("uName"), "inverted_switch")


        # BRANCH
        try:
            branch = subprocess.check_output(['git', 'branch'])
            branch = branch.split(' ')[1]
        except:
            log.warning('Can\'t retrieve branch')

        self.say(
            'initconfig -carteVolt {volt} -name {name} -ip {ip} -version {v} -status {status} -titreurNbr {tit} -ins {ins}'.format(
                name=settings.get("uName"), ip=get_ip(), v=settings.get("version"),
                volt=voltage, tit=titreur, ins=invertedSwitch, status=branch))
        return False

    def sendInfo(self, cmd=None):
        self.say('info -status {status}'.format(status='yeah!'))
        return False

    def testRoutine(self, cmd=None):
        self.say('testroutine -nbr 2')
        return True

    def btnDown(self, cmd):
        return float(cmd[1]) > 0

    def btnUp(self, cmd):
        return float(cmd[1]) == 0

exposesignals(FILTERS)


@module('KxkmCard')
@link({"/hardware/ready": "kxkm_card"})
def init_kxkm_card(flag, **kwargs):
    """
    This function is an Etape for the KXKM Card FSM wich wait the end of the initialisation of the C prog
    :param flag:
    :return:
    """
    if "kxkmcard" not in kwargs["_fsm"].vars.keys() and settings.get("sys", "raspi"):
        kwargs["_fsm"].vars["kxkmcard"] = KxkmCard()
        kwargs["_fsm"].vars["kxkmcard"].start()


# ETAPE AND SIGNALS
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
        kwargs["_fsm"].vars["kxkmcard"].start()


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
    kwargs["_etape"].preemptible.set()


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
    if "page" not in flag.args.keys():
        flag.args["page"] = "user"
    kwargs["_fsm"].vars["kxkmcard"].popUpTeleco(flag.args["ligne1"], flag.args["ligne2"], flag.args["page"])


@link({None: "kxkm_card"})
def kxkm_card_titreur_text(flag, **kwargs):
    pass



