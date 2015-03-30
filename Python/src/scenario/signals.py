# -*- coding: utf-8 -*-
#
#
# This provides a lot of basics signals
#
#

from src import scenario
from src.fsm import Flag


def declaresignal(signal, public_name=None):
    """
    This function declare a signal in the scenario scope
    :param signal: signal to declare
    :param public_name: Name of the signal to declare, if None, use the uid of signal
    :return:
    """
    if public_name is None:
        public_name = signal.uid
    scenario.DECLARED_SIGNALS[public_name] = signal


# signal_media_play = Flag("MEDIA_PLAY")
# declaresignal(signal_media_play)

signal_video_end_player = Flag("VIDEO_PLAYER_END")
declaresignal(signal_video_end_player)
signal_video_player_stop = Flag("VIDEO_PLAYER_STOP")
declaresignal(signal_video_player_stop)

signal_audio_end_player = Flag("AUDIO_PLAYER_END")
declaresignal(signal_audio_end_player)
signal_audio_player_stop = Flag("AUDIO_PLAYER_STOP")
declaresignal(signal_audio_player_stop)

signal_play_video = Flag("PLAY_MEDIA_VIDEO")
declaresignal(signal_play_video)
signal_play_audio = Flag("PLAY_MEDIA_AUDIO")
declaresignal(signal_play_audio)
signal_control_media = Flag("CONTROL_MEDIA")
declaresignal(signal_control_media)

signal_next_scene = Flag("NEXT_SCENE")
declaresignal(signal_next_scene)

signal_device_control = Flag("DEVICE_CONTROL")
declaresignal(signal_device_control)



