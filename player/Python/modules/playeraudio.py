# -*- coding: utf-8 -*-
#
#
# This file provide tools for audio
#
#
import os
from modules import ExternalProcess
from engine.setting import settings
from scenario import globaletape
from engine.log import init_log
log = init_log("audio")


# VLC AUDIO PLAYER CLASS
## FILE2FILE: GOOD
## LOOP: BAD
class VlcAudio(ExternalProcess):
    def __init__(self):
        ExternalProcess.__init__(self, 'vlcaudio')
        self.onClose = "AUDIO_EVENT_CLOSE"
        self.start()

    def play(self, filename=None, repeat=None):
        media = os.path.join(settings.get("path", "media"),filename) if filename is not None else self.media
        if os.path.isfile(media):
            self.media = media
            self.say("clear")
            self.say("add {media}".format(media=self.media))
            if repeat is not None:
                self.repeat = repeat
                switch = 'on' if self.repeat else 'off'
                self.say("repeat {switch}".format(switch=switch))
            self.say("pause")
        else:
            log.warning("Media File not found {0}".format(media))

    def stop(self):
        self.say("stop")

    def pause(self):
        self.say("pause")


# MPG123 AUDIO PLAYER CLASS
## FILE2FILE: BAD
## LOOP: GOOD
## NO SUPPORT OF WAVE (MP3 ONLY)
class Mpg123(ExternalProcess):
    def __init__(self):
        ExternalProcess.__init__(self, 'mpg123')
        self.onClose = "AUDIO_EVENT_STOP"

    def play(self, filename=None, repeat=None):
        media = os.path.join(settings.get("path", "media"), filename) if filename is not None else self.media
        if os.path.isfile(media):
            self.media = media
            self.repeat = repeat
            self.command = self.executable+" "
            if (self.repeat):
                self.command += "--loop -1 "
            self.command += self.media
            self.start()
        else:
            log.warning("Media File not found {0}".format(media))

    def pause(self):
        self.say("s")

# ETAPE AND SIGNALS
@globaletape("AUDIO_PLAYER", {
                "AUDIO_PLAY": "AUDIO_PLAYER_PLAY",
                "AUDIO_PAUSE": "AUDIO_PLAYER_PAUSE",
                "AUDIO_STOP": "AUDIO_PLAYER_STOP"})
def audio_init(flag, **kwargs):
    if "audio" not in kwargs["_fsm"].vars.keys():
        #kwargs["_fsm"].vars["audio"] = Mpg123()
        kwargs["_fsm"].vars["audio"] = VlcAudio()


@globaletape("AUDIO_PLAYER_PLAY", {
                None: "AUDIO_PLAYER"})
def audio_play(flag, **kwargs):
    media = flag.args["args"][0] if len(flag.args["args"]) >= 1 else None
    repeat = flag.args["args"][1] if len(flag.args["args"]) >= 2 else None
    kwargs["_fsm"].vars["audio"].play(media, repeat)
    kwargs["_etape"].preemptible.set()


@globaletape("AUDIO_PLAYER_STOP", {
                None: "AUDIO_PLAYER"})
def audio_stop(flag, **kwargs):
    kwargs["_fsm"].vars["audio"].stop()


@globaletape("AUDIO_PLAYER_PAUSE", {
                None: "AUDIO_PLAYER"})
def audio_pause(flag, **kwargs):
    kwargs["_fsm"].vars["audio"].pause()

    # dest = ["a", "b"]
    # for elem in dest:
    #    oscack.message.send(oscack.DNCserver.networkmap[elem].target, oscack.message.Message("/test", args1, args2, ('f', args3), ACK=True))


@globaletape("WAIT_CONTROL_AUDIO", {
                "AUDIO_PLAYER_CLOSE": "AUDIO_PLAYER"})
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
