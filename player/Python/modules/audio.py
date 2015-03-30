# -*- coding: utf-8 -*-
#
#
# This file provide tools for audio
#
#

# -*- coding: utf-8 -*-
#
#
# This should be a temporary module
#
#

import shlex
import threading
import os

from libs import subprocess32
from scenario import signals
from engine.tools import register_thread, unregister_thread
from engine.setting import settings
from engine.threads import patcher

from libs import rtplib
from engine.log import init_log
log = init_log("sound")


class AudioPlayer:
    """
    The Audio Play allow playing a sound and control it
    """

    def __init__(self, path):
        """
        :param path: Path to the media
        :return:
        """
        register_thread(self)
        self.path = path
        self._waiting_th = threading.Thread(target=self._wait_process_end)
        self._popen = None
        self._running = threading.Event()
        self.arguments = ()

    def start(self):
        """
        Start the player
        :return:
        """
        if self._running.is_set():
            return
        self._running.set()
        self._popen = subprocess32.Popen(self.arguments, bufsize=0, executable=None, stdin=None, stdout=None,
                                         stderr=None,
                                         preexec_fn=None, close_fds=False, shell=False, cwd=None, env=None,
                                         universal_newlines=False, startupinfo=None, creationflags=0)
        self._waiting_th.start()

    def stop(self):
        """
        Ask to stop the processus
        :return:
        """
        self._popen.terminate()  # Send SIGTERM to the player, asking to stop
        self._waiting_th.join(timeout=0.1)  # Waiting maximum of 250 ms before killing brutaly the processus
        if self._waiting_th.is_alive():
            self._popen.kill()  # Send SIGNKILL to brutaly kill the process
        unregister_thread(self)

    def _wait_process_end(self):
        """
        This function wait the process to end and add a signal when it appends
        :return:
        """
        self._popen.wait()
        patcher.patch(signals.signal_audio_end_player.get())
        self._running.clear()

    def join(self, timeout=None):
        """
        Join the video player to end
        :return:
        """
        return self._waiting_th.join(timeout=timeout)


class AlsaPlayer(AudioPlayer):
    """
    AlsaPlayer use aplay to provide a simple audio player
    """

    def __init__(self, path):
        AudioPlayer.__init__(self, path)
        self._cmd_line = "{exe} {file}".format(exe=settings.get("path", "aplay"),
                                               file=os.path.join(
                                                   settings.get("path", "media"),
                                                   self.path))
        self.arguments = shlex.split(self._cmd_line)

class Mpg123(AudioPlayer):
    """
    Mpg123  simple audio player
    """

    def __init__(self, path):
        AudioPlayer.__init__(self, path)
        self._cmd_line = "{exe} {file}".format(exe=settings.get("path", "mpg123"),
                                               file=os.path.join(
                                                   settings.get("path", "media"),
                                                   self.path))
        self.arguments = shlex.split(self._cmd_line)




try:
    import pygame

    pygame.init()


    def play_sound_at(time_s, time_ns, path):
        """
        This function load a sound, wait for an absolute time and go !
        :param dt_s:
        :param dt_ns:
        :param path:
        :return:
        """
        log.log("raw", "Load sound {path} at {s}s {ns}ns ".format(path=path, s=time_s, ns=time_ns))
        pygame.mixer.music.load(path)
        log.log("raw", "... load ending, now wait..")
        r = rtplib.wait_abs_time(time_s, time_ns)
        if r != 0:
            log.error("Try to play sound {path} at {s}s {ns}ns but wait_abs_time return : {r}".format(path=path, s=time_s,
                                                                                                     ns=time_ns, r=r))
            return
        #log.log("raw", ".. wait ending, now play !")
        pygame.mixer.music.play(10)
        log.log("debug", "Play sound {path} at {s}s {ns}ns ".format(path=path, s=time_s, ns=time_ns))


    def play_sound(path):
        """
        This function just use pygame to play a sound
        :param path: path to the file
        :return:
        """
        pygame.mixer.music.load(path)
        pygame.mixer.music.play(10)

except ImportError:
    log.warning("No pygame lib found")