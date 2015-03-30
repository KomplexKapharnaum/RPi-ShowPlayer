# -*- coding: utf-8 -*-
#
# This file provide utilities for controlling Video
#
#

import shlex
import threading
import os
import signal
import time
import socket

import liblo

from libc import subprocess32, rtplib
from src.scenario import signals
from src.tools import register_thread, unregister_thread
from src.setting import settings
from src.threads import patcher
from src.log import init_log

# liblo.send(liblo.Address(3456), liblo.Message("path", "Args", "args", 1, 345, ('f', 1.2)))

log = init_log("video")

class VideoPlayer:
    """
    The Video Play allow playing a video and control it
    """

    def __init__(self, path, *args, **kwargs):
        """
        :param path: Path to the media
        :param audio_output: Audio output to use (local = jack, hdmi = hdmi )
        :param hardware: Use the -hw option to decode audio with hardware
        :param args: Stings args to add to the omxplayer commande
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
        log.log("raw", "Start video player : {0} ".format(self.arguments))
        if self._running.is_set():
            return
        self._running.set()
        self._popen = subprocess32.Popen(self.arguments, bufsize=0, executable=None, stdin=None, stdout=None,
                                         stderr=None,
                                         preexec_fn=os.setsid, close_fds=False, shell=True, cwd=None, env=None,
                                         universal_newlines=False, startupinfo=None, creationflags=0)
        self._waiting_th.start()

    def stop(self):
        """
        Ask to stop the processus
        :return:
        """
        log.log("raw", "Asking to end the video")
        log.log("raw", "Process : {0}".format(self._popen))
        self._terminate()
        self._waiting_th.join(timeout=0.1)  # Waiting maximum of 250 ms before killing brutaly the processus
        if self._waiting_th.is_alive():
            log.log("raw", "Send kill to the process")
            self._kill()
        unregister_thread(self)
        log.log("raw", "end the video")

    def toggle_play(self):
        log.log("raw", "Not implemented")

    def volume_up(self):
        log.log("raw", "Not implemented")

    def volume_down(self):
        log.log("raw", "Not implemented")

    def show_info(self):
        log.log("raw", "Not implemented")

    def _terminate(self):
        """
        Send the terminate (15) signal to the process
        :return:
        """
        self._popen.terminate()  # Send SIGTERM to the player, asking to stop

    def _kill(self):
        """
        Send the kill (9) signal to the process
        :return:
        """
        self._popen.kill()  # Send SIGNKILL to brutaly kill the process

    def _wait_process_end(self):
        """
        This function wait the process to end and add a signal when it appends
        :return:
        """
        self._popen.wait()
        patcher.patch(signals.signal_video_end_player.get())
        log.log("raw", "Watcinh process end thread ok !")
        self._running.clear()

    def join(self, timeout=None):
        """
        Join the video player to end
        :return:
        """
        return self._waiting_th.join(timeout=timeout)


class HVideoPlayer(VideoPlayer):
    """
    The HVideoPlayer allow playing a video and control it via HPlayer
    """

    def __init__(self, path, hdmi_audio=False, *_args):
        """
        :param path: Path to the media
        :param hdmi_audio: Output audio via hdmi or not
        """
        VideoPlayer.__init__(self, path)
        args = list(_args)
        self._file = os.path.join(settings.get("path", "media"), self.path)
        self._target = liblo.Address("127.0.0.1", settings.get("localport", "inhplayer"))

        self._msg = dict()
        self._msg["play"] = liblo.Message("/play", ("s", self._file))
        self._msg["stop"] = liblo.Message("/stop")
        self._msg["pause"] = liblo.Message("/pause")
        self._msg["resume"] = liblo.Message("/resume")
        self._msg["quit"] = liblo.Message("/quit")

        self._cmd_line = "{exe} --ahdmi {audio} --media {file} {params} --in {portin}".format(
            exe=settings.get("path", "hplayer"),
            file=self._file,
            audio=hdmi_audio,
            params=" ".join(args),
            portin=settings.get("localport", "inhplayer"))
        self.arguments = shlex.split(self._cmd_line)

    def start(self):
        """
        This function play the file into the running server
        """
        VideoPlayer.start(self)
        liblo.send(self._target, self._msg["play"])

    def stop(self):
        liblo.send(self._target, self._msg["stop"])
        liblo.send(self._target, self._msg["quit"])
        VideoPlayer.stop(self)

    def pause(self):
        """
        This function send an OSC message to the HPlayer to ask pause
        """
        liblo.send(self._target, self._msg["pause"])

    def resume(self):
        """
        This function send an OSC message to the HPlayer to ask resume
        """
        liblo.send(self._target, self._msg["resume"])


class OldOMXVideoPlayer(VideoPlayer):
    """
    The OMX Video Play allow playing a video via omxplayer
    """

    def __init__(self, path, hdmi_audio=False, hardware=True, *_args):
        """
        :param path: Path to the media
        :param audio_output: Audio output to use (local = jack, hdmi = hdmi )
        :param hardware: Use the -hw option to decode audio with hardware
        :param args: Stings args to add to the omxplayer commande
        :return:
        """
        VideoPlayer.__init__(self, path)
        args = list(_args)

        if hardware:
            args.append("--hw")
        if hdmi_audio:
            audio_output = "hdmi"
        else:
            audio_output = "local"
        self._cmd_line = "{exe} -o {audio} {params} {file}".format(exe=settings.get("path", "omxplayer"),
                                                                   audio=audio_output,
                                                                   params=" ".join(args),
                                                                   file=os.path.join(
                                                                       settings.get("path", "media"), path))
        # self.arguments = shlex.split(self._cmd_line)  # TODO : if Shell=True, this line is useless
        self.arguments = self._cmd_line
        log.log("raw", "Video player arguments : {0}".format(self.arguments))

    def _terminate(self):
        """
        Send the terminate (15) signal to the process
        :return:
        """
        os.killpg(self._popen.pid, signal.SIGTERM)  # Send SIGTERM to the player, asking to stop

    def _kill(self):
        """
        Send the kill (9) signal to the process
        :return:
        """
        os.killpg(self._popen.pid, signal.SIGKILL)  # Send SIGNKILL to brutaly kill the process


class OMXVideoPlayer(VideoPlayer):
    """
    The OMX Video Play allow playing a video via omxplayer
    """

    def __init__(self, path, audio="both", hardware=True, args=()):
        """
        :param path: Path to the media
        :param audio_output: Audio output to use (local = jack, hdmi = hdmi )
        :param hardware: Use the -hw option to decode audio with hardware
        :param args: Stings args to add to the omxplayer commande
        :return:
        """
        VideoPlayer.__init__(self, path)
        t = rtplib.get_time()
        t = int((t[0] & 0xFFFF0000 | t[1] & 0x0000FFFF))
        args = list(args)
        self._fifo_path = os.path.join(settings.get("path", "tmp"), ".omx_{0}.fifo".format(t))
        os.mkfifo(self._fifo_path)

        if hardware:
            args.append("--hw -b ")
        if audio is True:
            audio_output = "hdmi"
        elif audio == "both":
            audio_output = "both"
        else:
            audio_output = "local"
        self._cmd_line = "{exe} -o {audio}  {params} {file} < {fifo}".format(exe=settings.get("path", "omxplayer"),
                                                                  audio=audio_output,
                                                                  params=" ".join(args),
                                                                  file=os.path.join(
                                                                      settings.get("path", "media"), path),
                                                                  fifo=self._fifo_path)
        # self.arguments = shlex.split(self._cmd_line)  # TODO : if Shell=True, this line is useless
        self.arguments = self._cmd_line
        VideoPlayer.start(self)  # Start player because it will wait the fifo
        log.log("raw", "Video player arguments : {0}".format(self.arguments))

    def _write_fifo(self, data):
        """
        Write to the fifo
        :param data:
        :return:
        """
        if self._popen.poll() is None:  # Process doesn't finish
            log.log("raw", "Write in fifo : {0}".format(data))
            try:
                fifo = os.open(self._fifo_path, os.O_WRONLY)
                os.write(fifo, data)
                os.close(fifo)
            except Exception as e:
                log.error(log.show_exception(e))
        else:
            log.log("raw", "Ast to rite in fifo : {0}, but process end !".format(data))

    def start(self):
        """
        Redifine start which will just launch the player by the fifo
        :return:
        """
        self._write_fifo(".\n")

    def toggle_play(self):
        """
        Toggle the player between play / pause
        :return:
        """
        self._write_fifo("p")

    def volume_up(self):
        """
        Up the volume
        :return:
        """
        self._write_fifo("+")

    def volume_down(self):
        """
        Down the volume
        :return:
        """
        self._write_fifo("-")

    def show_info(self):
        """
        Show information about the current media
        :return:
        """
        self._write_fifo("z")

    def stop(self):
        """
        Asking top stop the omx player
        :return:
        """
        try:
            self._write_fifo("q")
            time.sleep(0.250)
            VideoPlayer.stop(self)
        except Exception as e:
            log.error(log.show_exception(e))
        finally:
            os.remove(self._fifo_path)
        log.log("raw", "Video player correctly end !")

    def _terminate(self):
        """
        Send the terminate (15) signal to the process
        :return:
        """
        os.killpg(self._popen.pid, signal.SIGTERM)  # Send SIGTERM to the player, asking to stop

    def _kill(self):
        """
        Send the kill (9) signal to the process
        :return:
        """
        os.killpg(self._popen.pid, signal.SIGKILL)  # Send SIGNKILL to brutaly kill the process


class VLCPlayer(VideoPlayer):
    """
    Video Lan VLC Player interface
    """

    def __init__(self, path, *args, **kwargs):
        VideoPlayer.__init__(self, path)
        t = rtplib.get_time()
        t = int((t[0] & 0xFFFF0000 | t[1] & 0x0000FFFF))
        self._socket_path = os.path.join(settings.get("path", "tmp"), ".vlc_{0}.socket".format(t))
        self._cmd_line = "{exe} --play-and-exit -I oldrc --rc-unix {socket} --rc-fake-tty {file}".format(exe=settings.get("path", "vlc"),
                                                file=os.path.join(settings.get("path", "media"), path),
                                                socket=self._socket_path)
        # self.arguments = shlex.split(self._cmd_line)  # TODO : if Shell=True, this line is useless
        self.arguments = self._cmd_line
        self.start()

    def toggle_play(self):
        log.info("VLC PAUSE")
        try:
            s = socket.socket(socket.AF_UNIX)
            s.connect(self._socket_path)
            s.send("pause")
        except Exception as e:
            log.error(log.show_exception(e))
        finally:
            try:
                s.close()
            except Exception as e:
                log.error(log.show_exception(e))

    def stop(self):
        VideoPlayer.stop(self)







