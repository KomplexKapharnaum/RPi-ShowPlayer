# -*- coding: utf-8 -*-
#
# This file provide utilities for controlling Video
#
#

import os

from _classes import ExternalProcess, module
from modules import link, exposesignals
from engine.setting import settings
from engine.log import init_log
from libs import rtplib
log = init_log("video")


class VlcPlayer(ExternalProcess):
    """
    Video Lan VLC Player interface
    """
    def __init__(self, start=True):
        ExternalProcess.__init__(self, 'vlcvideo')
        self.onClose = "VIDEO_END"
        self.media = None
        self.repeat = False
        self.preloaded = False
        if start:
            self.start()

    def preload(self, filename=None, repeat=None, mediatype='video'):
        if filename is not None:
            media = os.path.join(settings.get_path("media", mediatype), filename)
            if os.path.isfile(media):
                self.media = media

        if repeat is not None:
            self.repeat = True if repeat else False

        if self.media is None or not os.path.isfile(self.media):
            log.warning("Media File not found {0}".format(self.media))
            self.preloaded = False
        else:
            self.preloaded = True

    def play(self, filename=None, repeat=None):
        if filename is not None:
            self.preload(filename, repeat)
        if self.preloaded:
            #self.say("clear")
            self.say("add {media}".format(media=self.media))
            #self.say("play")
            repeat = 'on' if self.repeat else 'off'
            self.say("repeat {switch}".format(switch=repeat))

    def pause(self):
        self.say("pause")

    def stop(self):
        self.say("stop")

    def set_volume(self, value):
        self.say("volume {0}".format(value))

    Filters = {
        'VIDEO_END': [True]
    }


class VlcPlayerOneShot(VlcPlayer):

    def __init__(self):
        VlcPlayer.__init__(self, start=False)

    def play(self, filename=None, repeat=None):
        if filename is not None:
            self.preload(filename, repeat)
        if self.preloaded:
            self.command = self.executable+' --play-and-exit '
            if repeat:
                self.command += ' --repeat '
            self.command += self.media
            self.start()

exposesignals(VlcPlayer.Filters)



# ETAPE AND SIGNALS
@module('VideoPlayer')
@link({"/video/play [media] [repeat]": "video_play",
        "/video/pause": "video_pause",
        "/video/stop": "video_stop",
        "/video/volume [volume]": "video_volume"})
def video_player(flag, **kwargs):
    if kwargs["_fsm"].process is None:
        kwargs["_fsm"].process = VlcPlayerOneShot()


@link({None: "video_player"})
def video_play(flag, **kwargs):
    kwargs["_fsm"].process.stop()
    kwargs["_fsm"].process = VlcPlayerOneShot()


    media = flag.args["media"] if 'media' in flag.args else None
    repeat = flag.args["repeat"] if 'repeat' in flag.args else None

    if flag is not None and flag.args is not None and 'abs_time_sync' in flag.args:
        kwargs["_fsm"].process.preload(media, repeat)
        rtplib.wait_abs_time(*flag.args['abs_time_sync'])
        kwargs["_fsm"].process.play()
        log.debug('+++ SYNC PLAY')
    else:
        kwargs["_fsm"].process.play(media, repeat)

    kwargs["_etape"].preemptible.set()


@link({None: "video_player"})
def video_stop(flag, **kwargs):
    kwargs["_fsm"].process.stop()


@link({None: "video_player"})
def video_pause(flag, **kwargs):
    kwargs["_fsm"].process.pause()


@link({None, "video_player"})
def video_volume(flag, **kwargs):
    if isinstance(kwargs["_fsm"].process, VlcPlayer):
        kwargs["_fsm"].process.set_volume(flag.args["volume"])
    else:
        log.warning("Ask to set volume on an unlauched process (VlcPlayer)")




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

