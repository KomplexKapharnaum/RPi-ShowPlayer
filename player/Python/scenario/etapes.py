# -*- coding: utf-8 -*-
#
#
# This file provide some Etapes which are accessible from the scenario scope
#
#


import scenario
from modules import audio, video
from scenario import signals
from scenario import classes
from scenario import functions

from engine.log import init_log

log = init_log("etapes")


def declareetape(etape, public_name=None):
    """
    This function declare an Etape in the scenario scope
    :param etape: Etape to declare
    :param public_name: Pulbic name of the etape, if None, it will use etape uid
    :return:
    """
    if public_name is None:
        public_name = etape.uid
    scenario.DECLARED_ETAPES[public_name] = etape
    return etape


def main_device_control(flag, **kwargs):
    """
    This function provide main control on the device
    :param flag:
    :param kwargs:
    :return:
    """
    log.debug("=> Device control : {0}".format(flag.args["args"][0]))
    if flag.args["args"][0] == "reboot_manager":
        log.log("raw", "call reboot_manager")
        functions.reboot_manager()


def control_player(flag, **kwargs):
    """
    Control media player
    :param flag:
    :param kwargs:
    :return:
    """
    try:
        log.log("raw", "Control player : {0}".format(flag.args["args"][0]))
        if flag.args["args"][0] == "toggle":
            kwargs["_fsm"].vars["player"].toggle_play()
        elif flag.args["args"][0] == "vup":
            kwargs["_fsm"].vars["player"].volume_up()
        elif flag.args["args"][0] == "vdown":
            kwargs["_fsm"].vars["player"].volume_down()
        elif flag.args["args"][0] == "info":
            kwargs["_fsm"].vars["player"].show_info()
    except Exception as e:
        log.error(log.show_exception(e))


def init_video_player(flag, **kwargs):
    """
    Stop an eventual existing audio player
    :param flag:
    :param kwargs:
    :return:
    """
    if "player" in kwargs["_fsm"].vars.keys():
        try:
            kwargs["_fsm"].vars["player"].stop()
        except Exception as e:
            log.error("CAN'T EXIT VIDEO PLAYER !")
            log.error(": " + str(log.show_exception(e)))


def start_playing_video_media(flag, **kwargs):
    """
    Start playing a media
    :param flag:
    :return:
    """
    if "player" in kwargs["_fsm"].vars.keys():
        try:
            kwargs["_fsm"].vars["player"].stop()
        except Exception as e:
            log.error("CAN'T EXIT VIDEO PLAYER !")
            log.error(": " + str(log.show_exception(e)))
    kwargs["_fsm"].vars["player"] = video.OMXVideoPlayer(flag.args["args"][0], args=("--loop", "--video_queue 1",
                                                                                     "--video_fifo 0.5"))
                                    # video.HPlayer(flag.args["args"][0]) #     # video.VLCPlayer(flag.args["args"][0])
    kwargs["_fsm"].vars["player"].start()
    log.log("raw", "end start_playing_video_media")


def init_audio_player(flag, **kwargs):
    """
    Stop an eventual existing audio player
    :param flag:
    :param kwargs:
    :return:
    """
    if "player" in kwargs["_fsm"].vars.keys():
        try:
            kwargs["_fsm"].vars["player"].stop()
        except Exception as e:
            log.error("CAN'T EXIT AUDIO PLAYER !")
            log.error(": " + str(e))


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
    kwargs["_fsm"].vars["player"] = audio.Mpg123(flag.args["args"][0]) 
                            #video.OMXVideoPlayer(flag.args["args"][0],hardware=False)
                            #audio.Mpg123(flag.args["args"][0]) ou video.VLCPlayer(flag.args["args"][0])

    kwargs["_fsm"].vars["player"].start()
    log.log("raw", "set preemptible ")
    kwargs["_etape"].preemptible.set()
    log.log("raw", "end start_playing_audio_media")


init_audio_player = classes.Etape("INIT_AUDIO_PLAYER", actions=((init_audio_player, {}), ))
declareetape(init_audio_player)
start_audio_player = classes.Etape("START_AUDIO_PLAYER", actions=((start_playing_audio_media, {}), ))
declareetape(start_audio_player)
wait_control_audio = classes.Etape("WAIT_CONTROL_AUDIO")
declareetape(wait_control_audio)
etape_control_audio = classes.Etape("CONTROL_AUDIO", actions=((control_player, {"player": "audio"}), ))
declareetape(etape_control_audio)

init_audio_player.transitions = {
    signals.signal_play_audio.uid: start_audio_player,
}
start_audio_player.transitions = {
    None: wait_control_audio
}
wait_control_audio.transitions = {
    signals.signal_audio_end_player.uid: init_audio_player,
    signals.signal_audio_player_stop.uid: init_audio_player,
    signals.signal_play_audio.uid: start_audio_player,
    signals.signal_control_media.uid: etape_control_audio
}
etape_control_audio.transitions = {
    None: wait_control_audio
}

init_video_player = classes.Etape("INIT_VIDEO_PLAYER", actions=((init_video_player, {}), ))
declareetape(init_video_player)
start_video_player = classes.Etape("START_VIDEO_PLAYER", actions=((start_playing_video_media, {}), ))
declareetape(start_video_player)
wait_control_video = classes.Etape("WAIT_CONTROL_VIDEO")
declareetape(wait_control_video)
etape_control_video = classes.Etape("CONTROL_VIDEO", actions=((control_player, {"player": "video"}), ))
declareetape(etape_control_video)

init_video_player.transitions = {
    signals.signal_play_video.uid: start_video_player
}
start_video_player.transitions = {
    None: wait_control_video
}
wait_control_video.transitions = {
    signals.signal_video_end_player.uid: init_video_player,
    signals.signal_video_player_stop.uid: init_video_player,
    signals.signal_play_video.uid: start_video_player,
    signals.signal_control_media.uid: etape_control_video
}
etape_control_video.transitions = {
    None: wait_control_video
}

etape_main_device_manager_wait = classes.Etape("MAIN_DEVICE_MANAGER_WAIT")
declareetape(etape_main_device_manager_wait)

etape_main_device_manager_control = classes.Etape("MAIN_DEVICE_MANAGER_CONTROL", actions=((main_device_control, {}), ))
declareetape(etape_main_device_manager_control)

etape_main_device_manager_wait.transitions = {
    signals.signal_device_control.uid: etape_main_device_manager_control
}

etape_main_device_manager_control.transitions = {
    None: etape_main_device_manager_wait
}
