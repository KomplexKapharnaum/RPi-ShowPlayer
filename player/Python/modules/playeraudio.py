# -*- coding: utf-8 -*-
#
#
# This file provide tools for audio
#
#
import os
import copy
from _classes import ExternalProcess, module
from modules import link, exposesignals
from modules._classes import AbstractVLC
from engine.setting import settings
from engine.log import init_log
from libs import rtplib
log = init_log("audio")


# VLC AUDIO PLAYER CLASS
## FILE2FILE: GOOD
## LOOP: BAD
# class VlcAudio(VlcPlayerOneShot):
#     def __init__(self, *args, **kwargs):
#         VlcPlayerOneShot.__init__(self, name='vlcaudio', *args, **kwargs)
#
#     def preload(self, *args, **kwargs):
#         VlcPlayerOneShot.preload(self, *args, mediatype='audio', **kwargs)
#
#     Filters = {
#         'AUDIO_END': [True]
#     }


FILTERS = {
        "MEDIA_END": ["transTo /audio/end", True],
        "AUDIO_END": [True]
    }

class AudioVLCPlayer(AbstractVLC):
    """
    This class define an audio player with VLC as backend
    """
    def __init__(self):
        command = copy.copy(settings.get_path("mvlc"))
        """:type: str"""
        arguments = copy.copy(settings.get("vlc", "options", "default"))
        """:type: dict"""
        arguments.update(settings.get("vlc", "options", "audio"))
        log.log("debug", "Vlc arguments : {0}".format(arguments))
        AbstractVLC.__init__(self, name="audiovlc", command=command.format(**arguments), filters=FILTERS)

    def check_media(self, media):
        """
        Add audio to the media path
        """
        return AbstractVLC.check_media(self, os.path.join(settings.get("path", "relative", "audio"), media))


exposesignals(FILTERS)


# MPG123 AUDIO PLAYER CLASS
## FILE2FILE: BAD
## LOOP: GOOD
## NO SUPPORT OF WAVE (MP3 ONLY)
class Mpg123(ExternalProcess):
    def __init__(self):
        ExternalProcess.__init__(self, 'mpg123')
        self.onClose = "AUDIO_END"

    def play(self, filename=None, repeat=None):
        media = os.path.join(settings.get_path("audio"), filename) if filename is not None else self.media
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

    Filters = {
        'AUDIO_END': [True]
    }


# ETAPE AND SIGNALS
@module('AudioPlayer')
@link({"/audio/play [media:str] [repeat:bool] [volume:int]": ["audio_play", settings.get("values", "vlc")],
        "/audio/pause": "audio_pause",
        "/audio/stop": "audio_stop",
        "/audio/volumeup": "audio_volume_up",
        "/audio/volumedown": "audio_volume_down",
        "/audio/set_volume [volume:int]": "audio_set_volume",
        "SCENE_STOPPING": "audio_stop",
        "/media/volup": "audio_volume_up",
        "/media/voldown": "audio_volume_down"})
def audio_player(flag, **kwargs):
    if kwargs["_fsm"].process is None:
        kwargs["_fsm"].process = AudioVLCPlayer()
        kwargs["_fsm"].process.start()


@link({None: "audio_player"})
def audio_play(flag, **kwargs):
    if kwargs["_fsm"].process is None:
        audio_player(flag, kwargs)

    media = flag.args["media"] if 'media' in flag.args else None
    kwargs["_fsm"].process.load(media)
    repeat = bool(flag.args["repeat"]) if 'repeat' in flag.args else False
    if repeat is None:
        repeat = False
    kwargs["_fsm"].process.repeat(repeat)

    if flag is not None and flag.args is not None and 'abs_time_sync' in flag.args:
        log.debug('+++ BEFORE SYNC PLAY {0}'.format(rtplib.get_time()))
        rtplib.wait_abs_time(*flag.args['abs_time_sync'])
        log.debug('+++ SYNC PLAY {0}'.format(flag.args['abs_time_sync']))
    kwargs["_fsm"].process.play()


@link({None: "audio_player"})
def audio_stop(flag, **kwargs):
    kwargs["_fsm"].process.stop_media()


@link({None: "audio_player"})
def audio_pause(flag, **kwargs):
    kwargs["_fsm"].process.pause()

    # dest = ["a", "b"]
    # for elem in dest:
    #    oscack.message.send(oscack.DNCserver.networkmap[elem].target, oscack.message.Message("/test", args1, args2, ('f', args3), ACK=True))


@link({None: "audio_player"})
def audio_set_volume(flag, **kwargs):
    if isinstance(kwargs["_fsm"].process, AudioVLCPlayer):
        kwargs["_fsm"].process.set_volume(flag.args["volume"])
    else:
        log.warning("Ask to set volume on an unlauched process (VlcPlayer)")


@link({None: "audio_player"})
def audio_volume_up(flag, **kwargs):
    if isinstance(kwargs["_fsm"].process, AudioVLCPlayer):
        kwargs["_fsm"].process.volume_up()
    else:
        log.warning("Ask to volume up on an unlauched process (VlcPlayer)")


@link({None: "audio_player"})
def audio_volume_down(flag, **kwargs):
    if isinstance(kwargs["_fsm"].process, AudioVLCPlayer):
        kwargs["_fsm"].process.volume_down()
    else:
        log.warning("Ask to volume down on an unlauched process (VlcPlayer)")





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
