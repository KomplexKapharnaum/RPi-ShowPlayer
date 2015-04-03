# -*- coding: utf-8 -*-
#
#
# This file provide tools for audio
#
#
import os

from libs import oscack
from modules.basemodule import ExternalProcess
from engine.setting import settings
from scenario import globaletape
from engine.log import init_log
log = init_log("sound")


#AUDIO PLAYER CLASS
class AlsaPlayer(ExternalProcess):
    """
    AlsaPlayer use aplay to provide a simple audio player
    """
    def __init__(self, path):
        ExternalProcess.__init__(self)
        path = os.path.join(settings.get("path", "media"),path)
        self.command = "{exe} {file}".format(exe=settings.get("path", "aplay"), file=path)
        self.onClose = "AUDIO_PLAYER_CLOSE"
        self.start()


# AUDIO PLAYER CLASS
class Mpg123(ExternalProcess):
    """
    Mpg123  simple audio player
    """
    def __init__(self, path):
        ExternalProcess.__init__(self)
        path = os.path.join(settings.get("path", "media"),path)
        self.command = "{exe} {file}".format(exe=settings.get("path", "mpg123"), file=path)
        self.onClose = "AUDIO_PLAYER_CLOSE"
        self.start()


# ETAPE AND SIGNALS
@globaletape("INIT_AUDIO_PLAYER", {
                "AUDIO_PLAYER_PLAY": "START_AUDIO_PLAYER"})
def init_audio_player(flag, **kwargs):
    """
    Stop an eventual existing audio player
    :param flag:
    :param kwargs:
    :return:
    """
    if "audio" in kwargs["_fsm"].vars.keys():
        try:
            kwargs["_fsm"].vars["audio"].stop()
        except Exception as e:
            log.error("CAN'T EXIT AUDIO PLAYER !")
            log.error(": " + str(e))


@globaletape("START_AUDIO_PLAYER", {
                None: "WAIT_CONTROL_AUDIO"})
def start_playing_audio_media(flag, **kwargs):
    """
    Start playing a media
    :param flag:
    :return:
    """
    if "player" in kwargs["_fsm"].vars.keys():
        try:
            kwargs["_fsm"].vars["player"].stop()
        except Exception as e:
            log.error("CAN'T EXIT AUDIO PLAYER !")
            log.error(": " + str(e))
    kwargs["_fsm"].vars["player"] = Mpg123(flag.args["args"][0])
    # kwargs["_fsm"].vars["player"].start()
    # log.log("raw", "set preemptible ")

    # dest = ["a", "b"]
    # for elem in dest:
    #    oscack.message.send(oscack.DNCserver.networkmap[elem].target, oscack.message.Message("/test", args1, args2, ('f', args3), ACK=True))

    kwargs["_etape"].preemptible.set()
    # log.log("raw", "end start_playing_audio_media")


@globaletape("WAIT_CONTROL_AUDIO", {
                "AUDIO_PLAYER_CLOSE": "INIT_AUDIO_PLAYER"})
def wait_player_audio(flag, **kwargs):
    pass


# @globaletape("CONTROL_AUDIO")
# def control_audio_player(flag, **kwargs):
#     """
#     Control media player
#     :param flag:
#     :param kwargs:
#     :return:
#     """
#     try:
#         log.log("raw", "Control player : {0}".format(flag.args["args"][0]))
#         if flag.args["args"][0] == "toggle":
#             kwargs["_fsm"].vars["player"].toggle_play()
#         elif flag.args["args"][0] == "vup":
#             kwargs["_fsm"].vars["player"].volume_up()
#         elif flag.args["args"][0] == "vdown":
#             kwargs["_fsm"].vars["player"].volume_down()
#         elif flag.args["args"][0] == "info":
#             kwargs["_fsm"].vars["player"].show_info()
#     except Exception as e:
#         log.error(log.show_exception(e))


# SIGNAUX
# signal_audio_player_stop = globalsignal("AUDIO_PLAYER_STOP")
# signal_play_audio = globalsignal("AUDIO_PLAYER_PLAY")
# signal_control_audio = globalsignal("AUDIO_PLAYER_CTRL")
# signal_audio_player_close = globalsignal("AUDIO_PLAYER_CLOSE")

# ETAPES
# init_audio_player = Etape("INIT_AUDIO_PLAYER", actions=((init_audio_player, {}), )).register()
# start_audio_player = Etape("START_AUDIO_PLAYER", actions=((start_playing_audio_media, {}), )).register()
# wait_control_audio = Etape("WAIT_CONTROL_AUDIO").register()
# etape_control_audio = Etape("CONTROL_AUDIO", actions=((control_audio_player, {}), )).register()

# TRANSITIONS
# init_audio_player.transitions = {
#     signal_play_audio.uid: start_audio_player,
# }

# start_audio_player.transitions = {
#     None: wait_control_audio
# }


# wait_control_audio.transitions = {
#     signal_audio_player_close.uid: init_audio_player,
#     signal_audio_player_stop.uid: init_audio_player,
#     signal_play_audio.uid: start_audio_player,
#     signal_control_audio.uid: etape_control_audio
# }

# etape_control_audio.transitions = {
#     None: wait_control_audio
# }
