# -*- coding: utf-8 -*-
#
#
# This file provide tools for audio
#
#

import shlex
import threading
import os

from libs import subprocess32
import scenario
from engine.tools import register_thread, unregister_thread
from engine.setting import settings
from engine.threads import patcher
from engine.fsm import Flag

from libs import rtplib
from engine.log import init_log
log = init_log("sound")


# GENERIC THREAD FOR EXTERNAL PROCESS
class ExternalProcess:
    """
    Watchdog thread to control external processes
    """
    def __init__(self):
        """
        :return:
        """
        register_thread(self)
        self._watchdog = threading.Thread(target=self._watch)
        self._running = threading.Event()
        self._popen = None
        self.command = ''
        self.onStart = None
        self.onStop = None

    def start(self):
        """
        Start the external process
        :return:
        """
        if self._running.is_set():
            return
        self._running.set()
        self._popen = subprocess32.Popen( shlex.split(self.command), bufsize=0, executable=None, stdin=None, stdout=None,
                                         stderr=None,
                                         preexec_fn=None, close_fds=False, shell=False, cwd=None, env=None,
                                         universal_newlines=False, startupinfo=None, creationflags=0)
        self._watchdog.start()
        if self.onStart:
            patcher.patch(self.onStart.get())

    def _watch(self):
        """
        This function wait the process to end and add a signal when it appends
        :return:
        """
        self._popen.wait()
        if self.onStop:
            patcher.patch(self.onStop.get())
        self._running.clear()

    def stop(self):
        """
        Ask to stop the external process
        :return:
        """
        if self._popen.poll():
            self._popen.terminate()  # Send SIGTERM to the player, asking to stop
        self._watchdog.join(timeout=0.1)  # Waiting maximum of 250 ms before killing brutaly the processus
        if self._watchdog.is_alive():
            self._popen.kill()  # Send SIGNKILL to brutaly kill the process
        unregister_thread(self)

    def join(self, timeout=None):
        """
        Join the video player to end
        :return:
        """
        return self._watchdog.join(timeout=timeout)


class AlsaPlayer(ExternalProcess):
    """
    AlsaPlayer use aplay to provide a simple audio player
    """
    def __init__(self, path):
        ExternalProcess.__init__(self)
        path = os.path.join(settings.get("path", "media"),path)
        self.command = "{exe} {file}".format(exe=settings.get("path", "aplay"), file=path)
        self.onStop = signal_audio_player_end

class Mpg123(ExternalProcess):
    """
    Mpg123  simple audio player
    """
    def __init__(self, path):
        ExternalProcess.__init__(self)
        path = os.path.join(settings.get("path", "media"),path)
        self.command = "{exe} {file}".format(exe=settings.get("path", "mpg123"), file=path)
        self.onStop = signal_audio_player_end


# ETAPE AND SIGNALS


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
    kwargs["_fsm"].vars["player"] = Mpg123(flag.args["args"][0])
                            #video.OMXVideoPlayer(flag.args["args"][0],hardware=False)
                            #audio.Mpg123(flag.args["args"][0]) ou video.VLCPlayer(flag.args["args"][0])

    kwargs["_fsm"].vars["player"].start()
    # log.log("raw", "set preemptible ")
    kwargs["_etape"].preemptible.set()
    # log.log("raw", "end start_playing_audio_media")


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


# SIGNAUX
signal_audio_player_end = Flag("AUDIO_PLAYER_END")
#scenario.signals.declaresignal(signal_audio_player_end)

signal_audio_player_stop = Flag("AUDIO_PLAYER_STOP")
#scenario.signals.declaresignal(signal_audio_player_stop)

signal_play_audio = Flag("AUDIO_PLAYER_PLAY")
#scenario.signals.declaresignal(signal_play_audio)

signal_control_audio = Flag("AUDIO_PLAYER_CTRL")
#scenario.signals.declaresignal(signal_control_audio)

# ETAPES
init_audio_player = scenario.classes.Etape("INIT_AUDIO_PLAYER", actions=((init_audio_player, {}), ))
scenario.etapes.declareetape(init_audio_player)

start_audio_player = scenario.classes.Etape("START_AUDIO_PLAYER", actions=((start_playing_audio_media, {}), ))
scenario.etapes.declareetape(start_audio_player)

wait_control_audio = scenario.classes.Etape("WAIT_CONTROL_AUDIO")
scenario.etapes.declareetape(wait_control_audio)

etape_control_audio = scenario.classes.Etape("CONTROL_AUDIO", actions=((control_player, {}), ))
scenario.etapes.declareetape(etape_control_audio)


init_audio_player.transitions = {
    signal_play_audio.uid: start_audio_player,
}

start_audio_player.transitions = {
    None: wait_control_audio
}


wait_control_audio.transitions = {
    signal_audio_player_end.uid: init_audio_player,
    signal_audio_player_stop.uid: init_audio_player,
    signal_play_audio.uid: start_audio_player,
    signal_control_audio.uid: etape_control_audio
}

etape_control_audio.transitions = {
    None: wait_control_audio
}
