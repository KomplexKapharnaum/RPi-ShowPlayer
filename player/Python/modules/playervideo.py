# -*- coding: utf-8 -*-
#
# This file provide utilities for controlling Video
#
#

import os
import socket
import subprocess

from modules import ExternalProcess
from engine.setting import settings
from scenario import globaletape
from engine.log import init_log
log = init_log("video")


class VlcPlayer(ExternalProcess):
    """
    Video Lan VLC Player interface
    """
    def __init__(self):
        ExternalProcess.__init__(self, 'vlcvideo')
        self.onClose = "VIDEO_EVENT_CLOSE"
        self.start()
        # self._rcport = 1250
        # self.command += " -I rc --rc-host 0.0.0.0:{port} --no-osd --aout alsa".format(port=self._rcport)

    # def say(self, message):
    #     cmd = "echo {txt} | nc -c localhost {port}".format(txt=message, port=self._rcport)
    #     subprocess.call(cmd, shell=True)

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
        else:
            log.warning("Media File not found {0}".format(media))

    def stop(self):
        self.say("stop")

    def pause(self):
        self.say("pause")


# ETAPE AND SIGNALS
@globaletape("VIDEO_PLAYER", {
                "VIDEO_PLAY": "VIDEO_PLAYER_PLAY",
                "VIDEO_PAUSE": "VIDEO_PLAYER_PAUSE",
                "VIDEO_STOP": "VIDEO_PLAYER_STOP"})
def video_init(flag, **kwargs):
    if "video" not in kwargs["_fsm"].vars.keys():
        kwargs["_fsm"].vars["video"] = VlcPlayer()
    #elif not kwargs["_fsm"].vars["video"].is_running():
    #    kwargs["_fsm"].vars["video"].start()


@globaletape("VIDEO_PLAYER_PLAY", {
                None: "VIDEO_PLAYER"})
def video_play(flag, **kwargs):
    media = flag.args["args"][0] if len(flag.args["args"]) >= 1 else None
    repeat = flag.args["args"][1] if len(flag.args["args"]) >= 2 else None
    kwargs["_fsm"].vars["video"].play(media, repeat)
    kwargs["_etape"].preemptible.set()


@globaletape("VIDEO_PLAYER_STOP", {
                None: "VIDEO_PLAYER"})
def video_stop(flag, **kwargs):
    kwargs["_fsm"].vars["video"].stop()


@globaletape("VIDEO_PLAYER_PAUSE", {
                None: "VIDEO_PLAYER"})
def video_pause(flag, **kwargs):
    kwargs["_fsm"].vars["video"].pause()




# def control_video_player(flag, **kwargs):
#     """
#     Control media player
#     :param flag:
#     :param kwargs:
#     :return:
#     """
#     try:
#         if flag.args["args"][0] == "toggle":
#             kwargs["_fsm"].vars["video"].toggle_play()
#         elif flag.args["args"][0] == "vup":
#             kwargs["_fsm"].vars["video"].volume_up()
#         elif flag.args["args"][0] == "vdown":
#             kwargs["_fsm"].vars["video"].volume_down()
#         elif flag.args["args"][0] == "info":
#             kwargs["_fsm"].vars["video"].show_info()
#     except Exception as e:
#         log.error(log.show_exception(e))


'''
class HPlayer(ExternalProcess):
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



class OMXVideoPlayer(ExternalProcess):
    """
    The OMX Video Play allow playing a video via omxplayer
    """

    def __init__(self, path, audio="both", hardware=True, args=()):
        """
        :param path: Path to the media
        :param video_output: Audio output to use (local = jack, hdmi = hdmi )
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
            video_output = "hdmi"
        elif audio == "both":
            video_output = "both"
        else:
            video_output = "local"
        self._cmd_line = "{exe} -o {audio}  {params} {file} < {fifo}".format(exe=settings.get("path", "omxplayer"),
                                                                  audio=video_output,
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
    '''

