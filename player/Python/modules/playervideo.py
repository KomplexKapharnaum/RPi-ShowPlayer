# -*- coding: utf-8 -*-
#
# This file provide utilities for controlling Video
#
#

import os
import time
import copy

from _classes import AbstractVLC, ExternalProcess, module
from modules import link, exposesignals
from engine.setting import settings
from engine.log import init_log
from libs import rtplib

log = init_log("video")


class VideoVLCPlayer(AbstractVLC):
    """
    This class define an VideoPlayer with VLC as player backend
    """

    def __init__(self):
        command = copy.copy(settings.get_path("mvlc"))
        """:type: str"""
        arguments = copy.copy(settings.get("vlc", "options", "default"))
        """:type: dict"""
        arguments.update(settings.get("vlc", "options", "video"))
        log.log("debug", "Vlc arguments : {0}".format(arguments))
        AbstractVLC.__init__(self, name="videovlc", command=command.format(**arguments))

    def check_media(self, media):
        """
        Add video to the media path
        """
        return AbstractVLC.check_media(self, os.path.join(settings.get("path", "relative", "video"), media))

    Filters = {
        "MEDIA_END": ["transTo /video/end", True],
        "VIDEO_END": [True]
    }

#
# class VlcPlayer(ExternalProcess):
# """
#     Video Lan VLC Player interface
#     """
#     def __init__(self, start=True, name='vlcvideo', *args, **kwargs):
#         ExternalProcess.__init__(self, name=name, *args, **kwargs)
#         self.onClose = "VIDEO_END"
#         self.media = None
#         self.repeat = False
#         self.preloaded = False
#         if start:
#             self.start()
#
#     def preload(self, filename=None, repeat=None, mediatype='video'):
#         if filename is not None:
#             media = os.path.join(settings.get_path("media", mediatype), filename)
#             if os.path.isfile(media):
#                 self.media = media
#
#         if repeat is not None:
#             self.repeat = True if repeat else False
#
#         if self.media is None or not os.path.isfile(self.media):
#             log.warning("Media File not found {0}".format(self.media))
#             self.preloaded = False
#         else:
#             self.preloaded = True
#
#     def play(self, filename=None, repeat=None):
#         if filename is not None:
#             self.preload(filename, repeat)
#         if self.preloaded:
#             #self.say("clear")
#             self.say("add {media}".format(media=self.media))
#             self.say("volume {0}".format(settings.get("sys", "vlc_volume")))        # Set default VLC volume
#             #self.say("play")
#             repeat = 'on' if self.repeat else 'off'
#             self.say("repeat {switch}".format(switch=repeat))
#
#     def pause(self):
#         self.say("pause")
#
#     def stop(self):
#         if self.is_running():
#             self.say("stop")
#         time.sleep(0.01)
#         ExternalProcess.stop(self)
#
#     def set_volume(self, value):
#         self.say("volume {0}".format(value))
#
#     def volume_up(self):
#         self.say("volup")
#
#     def volume_down(self):
#         self.say("voldown")
#
#     Filters = {
#         'VIDEO_END': [True]
#     }
#
#
# class VlcPlayerOneShot(VlcPlayer):
#
#     def __init__(self, *args, **kwargs):
#         kwargs['start'] = False
#         VlcPlayer.__init__(self, *args, **kwargs)
#
#     def play(self, filename=None, repeat=None):
#         if filename is not None:
#             self.preload(filename, repeat)
#         if self.preloaded:
#             self.command = self.executable+' --play-and-exit '
#             if repeat:
#                 self.command += ' --repeat '
#             self.command += self.media
#             self.start()

exposesignals(VideoVLCPlayer.Filters)



# ETAPE AND SIGNALS
@module('VideoPlayer')
@link({"/video/play [media] [repeat]": "video_play",
       "/video/pause": "video_pause",
       "/video/resume": "video_resume",
       "/video/toggle": "video_toggle",
       "/video/stop": "video_stop",
       "/video/volumeup": "video_volume_up",
       "/video/volumedown": "video_volume_down",
       "/video/set_volume [volume]": "video_set_volume",
       "SCENE_STOP": "video_stop"})
def video_player(flag, **kwargs):
    if kwargs["_fsm"].process is None:
        kwargs["_fsm"].process = VideoVLCPlayer()
        kwargs["_fsm"].process.start()


@link({None: "video_player"})
def video_play(flag, **kwargs):
    if kwargs["_fsm"].process is None:
        video_player(flag, kwargs)

    media = flag.args["media"] if 'media' in flag.args else None
    kwargs["_fsm"].process.load(media)
    repeat = flag.args["repeat"] if 'repeat' in flag.args else None
    kwargs["_fsm"].process.repeat(repeat)

    if flag is not None and flag.args is not None and 'abs_time_sync' in flag.args:
        log.debug('+++ BEFORE SYNC PLAY {0}'.format(rtplib.get_time()))
        rtplib.wait_abs_time(*flag.args['abs_time_sync'])
        log.debug('+++ SYNC PLAY {0}'.format(flag.args['abs_time_sync']))
    kwargs["_fsm"].process.play()
    # kwargs["_etape"].preemptible.set()


@link({None: "video_player"})
def video_stop(flag, **kwargs):
    kwargs["_fsm"].process.stop_media()


@link({None: "video_player"})
def video_pause(flag, **kwargs):
    kwargs["_fsm"].process.pause()


@link({None: "video_player"})
def video_resume(flag, **kwargs):
    kwargs["_fsm"].process.resume()


@link({None: "video_player"})
def video_toggle(flag, **kwargs):
    kwargs["_fsm"].process.toggle()


@link({None: "video_player"})
def video_set_volume(flag, **kwargs):
    if isinstance(kwargs["_fsm"].process, VideoVLCPlayer):
        kwargs["_fsm"].process.set_volume(flag.args["volume"])
    else:
        log.warning("Ask to set volume on an unlauched process (VlcPlayer)")


@link({None: "video_player"})
def video_volume_up(flag, **kwargs):
    if isinstance(kwargs["_fsm"].process, VideoVLCPlayer):
        kwargs["_fsm"].process.volume_up()
    else:
        log.warning("Ask to volume up on an unlauched process (VlcPlayer)")


@link({None: "video_player"})
def video_volume_down(flag, **kwargs):
    if isinstance(kwargs["_fsm"].process, VideoVLCPlayer):
        kwargs["_fsm"].process.volume_down()
    else:
        log.warning("Ask to volume down on an unlauched process (VlcPlayer)")


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

