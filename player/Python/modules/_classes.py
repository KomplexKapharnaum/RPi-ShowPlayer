# -*- coding: utf-8 -*-
#

import os
import shlex
import threading
import time
import collections
import sys
import codecs
from Queue import Queue
# import signal
#
# signal.signal(signal.SIGCLD, signal.SIG_IGN)    # Avoid defunct process (just ignore them if they crash
# More info :
# http://stackoverflow.com/questions/16944886/how-to-kill-zombie-process
# http://bugs.python.org/issue15756

from modules import MODULES
from libs.subprocess32 import Popen, PIPE
from engine.threads import patcher
from engine.tools import register_thread, unregister_thread, show_trace
from engine.fsm import Flag
from engine.setting import settings
from engine.log import init_log

log = init_log("modulesClass")


class module(object):
    def __init__(self, name=None, process=None):
        self.name = name
        self.process = process

    def __call__(self, etape):
        if self.name is None:
            self.name = etape.uid
        MODULES[self.name] = etape
        return etape


class ExternalProcess(object):
    """
    This class define an external process
    """

    def __init__(self, name, command=None):
        """
        :param name: Name of the process to identify it
        :param command: Command to run in the process
        :type name: str
        :type command: str
        """
        self.name = name
        if command is None:
            if name in settings.get("path", "relative").keys():
                command = settings.get_path(name)
            elif name in settings.get("path").keys():
                command = settings.get("path", name)
            else:
                raise AttributeError("There is no commande in settings for {0}".format(name))
        else:
            if not os.path.isabs(command.split(" ")[0]):
                log.warning("The commande path {0} for {1} is relative".format(command, name))
        self.command = command

        self.stdin_queue = Queue(maxsize=256)
        self._stdin_thread = threading.Thread(target=self._stdin_writer)
        self._stdin_lock = threading.RLock()
        self.stdout_queue = Queue(maxsize=256)
        self._stdout_thread = threading.Thread(target=self._stdout_reader)
        self.stderr = None
        try:
            self._logpath = os.path.join(settings.get_path("log"), "{0}.log".format(name))
            self.stderr = open(self._logpath, 'w+')
        except IOError:
            log.warning("There is no where ({0}) to put log of {1}".format(self._logpath, self.name))

        self._defunctdog_thread = threading.Thread(target=self._defunctdog)
        self._request_stop = threading.Event()

        self._check_interval = settings.get("speed", "thread_check_interval")
        self._popen = None
        self._priority = 0
        self.return_code = None
        self._is_launched = threading.Event()
        self._is_running = threading.Event()
        self._ask_to_stop = threading.Event()
        self._is_stopping = False

    def start(self):
        """
        This function start the process and all his threads
        :return:
        """
        if self._is_launched.is_set():
            self._log("warning", "try to start an already started process")
            return False

        self._popen = Popen(shlex.split(self.command), bufsize=0, executable=None, stdin=PIPE, stdout=PIPE,
                            stderr=self.stderr, close_fds=False, shell=False, cwd=None, env=None,
                            universal_newlines=True, startupinfo=None, creationflags=0,
                            preexec_fn=lambda: os.nice(self._priority))

        self._defunctdog_thread.start()
        self._stdin_thread.start()
        self._stdout_thread.start()
        register_thread(self)
        self._is_launched.set()
        self._is_running.set()

    def _process_ended(self):
        """
        This function clean thread and process logic when the process end
        """
        self._is_stopping = True
        self.stdin_queue.put_nowait(None)  # Ask stdin_thread to stop
        self._is_running.clear()
        unregister_thread(self)

    def _stop_process(self):
        """
        This function terminate the process : BLOCKING
        """
        self._is_stopping = True
        try:
            self._popen.terminate()  # Send SIGTERM to the player, asking to stop
            self._log("debug", 'SIGTERM')
        except Exception as e:
            self._log("debug", "Cannot sigterm")
        self._stdout_thread.join(timeout=settings.get("speed", "wait_before_kill"))  # Waiting maximum of 250 ms before killing brutaly the processus
        if self._stdout_thread.is_alive():
            self._popen.kill()  # Send SIGNKILL to brutaly kill the process
            self._log("debug", 'KILLED')

    def stop(self):
        """
        This function ask to stop the process : NOT BLOCKING
        """
        self._ask_to_stop.set()

    def join(self, *args, **kwargs):
        """
        Wait all thread and process to be stopped
        """
        if not self._is_launched.is_set():
            self._log("warning", "Ask to join before it has been launched")
            return False
        self._defunctdog_thread.join(*args, **kwargs)
        self._stdin_thread.join(*args, **kwargs)
        self._stdout_thread.join(*args, **kwargs)
        return True

    def _stdin_writer(self):
        """
        This funtion write in stdin the current
        """
        self._is_launched.wait()
        while True:
            message = self.stdin_queue.get()
            if message is None or self._is_stopping or not self._is_running.is_set():
                if message is not None:
                    log.debug("Ignore {0} on process {1} because it's stopped".format(message, self.name))
                break
            self._log("error", "write to stdin : {0}".format(message))
            self._direct_stdin_writer(message)

    def _direct_stdin_writer(self, msg):
        """
        This function direct write to stdin the given message
        :param msg: Message to write on stdin
        :type msg: str
        """
        with self._stdin_lock:
            msg += "\n"
            m = msg.encode("utf-8")
            self._log("debug", "write to stdin : {0}".format(m))
            self._popen.stdin.write(m)

    def _stdout_reader(self):
        """
        This function read the stdout and put message to the stdout queue
        """
        self._is_launched.wait()
        stdout_iterator = iter(self._popen.stdout.readline, b"")
        for line in stdout_iterator:
            self._log("error", "stdout : {0}".format(line.strip()))
            self.stdout_queue.put_nowait(line.strip())
        self.stdout_queue.put_nowait(None)              # Stop queue consumers

    def _defunctdog(self):
        """
        This function try to get return code of the process to avoid defunct
        """
        self._is_running.wait()
        while self._is_running.is_set() and not self._ask_to_stop.is_set():
            self.return_code = self._popen.poll()
            if self.return_code is not None:
                break
            time.sleep(self._check_interval)
        if self.return_code is None:  # If loop end by ask to stop
            self._stop_process()  # Really stop the thread
            self.return_code = self._popen.poll()
        else:
            self._log("raw", "ended itself with {0} code".format(self.return_code))
        self._process_ended()

    def _log(self, lvl, msg):
        """
        This function log message
        """
        log.log(lvl, "Proc[{0}] : {1}".format(self.name, msg))


class ExternalProcessFlag(ExternalProcess):
    """
    This class provide a stdout consumer which emit signal on #MSG recv
    """

    def __init__(self, name, filters=None, *args, **kwargs):
        """
        :param filters: Filters to apply on stdout
        :type filters: dict of list
        """
        ExternalProcess.__init__(self, name, *args, **kwargs)
        if filters is None:
            filters = dict()
        self.Filters = filters
        self._stdout_to_flag_thread = threading.Thread(target=self._stdout_to_flag)

    def start(self):
        ExternalProcess.start(self)
        self._stdout_to_flag_thread.start()

    def _stdout_to_flag(self):
        """
        This thread function consume stdout to create flag with it
        """
        self._is_running.wait()
        while self._is_running.is_set():
            msg = self.stdout_queue.get()
            if msg is None or len(msg) < 1:                 # It's time to stop
                break
            if msg[0] == "#":                               # It's a signal from the kxkmcard program
                self.onEvent(msg[1:].split(' '))
            else:
                self._log("warning", "unknown stdout line {0}".format(msg))

    def join(self):
        """
        Wait the process and thread to end
        """
        ExternalProcess.join()
        self._stdout_thread.join()

    def onEvent(self, cmd=[]):        # TODO : doc or change implmentation
        cmd[0] = cmd[0].lstrip('#')
        self._log("error", "cmd : {0}".format(cmd))
        doEmmit = True
        if cmd[0] in self.Filters.keys():
            for fn in self.Filters[cmd[0]]:
                if isinstance(fn, str):
                    filt = fn.split(' ')
                    method = getattr(self, filt[0], None)
                    self._log("error", "filt : {0}, merhod {1}".format(filt, method))
                    if callable(method):
                        if len(filt) > 1:
                            doEmmit = method(cmd, filt[1:]) and doEmmit
                        else:
                            doEmmit = method(cmd) and doEmmit
        if doEmmit:
            self.emmit(cmd)

    def emmit(self, args=[]):   # TODO : doc or change implementation
        signal_name = args[0].upper()
        if signal_name[0] == '/':
            signal_name = signal_name.replace('/', '_')[1:].upper()
        log.log("raw", signal_name + ' ' + ' '.join(args[1:]))
        if signal_name == "DEVICE_SENDINFOTENSION" and not settings.get("log", "tension", "active"):
            return  # Avoid patch flag if setting unactive send tension info
        flag = Flag(signal_name).get(args={"args": args[1:]})
        patcher.patch(flag)


class ExternalProcessTemplate(object):
    """
    This class define an external processus template to generate ExternalProcess objects
    """

    def __init__(self, name, template, commande, arguments=None):
        """

        :param name: Name of the process template to identify it
        :param template: ExternalProcess class reference
        :param commande: Commande to run with optionnaly option ({0})
        :param arguments: Argument to pass to the commande
        :type commande: str
        :type template: class ExternalProcess
        :type name: str
        :type arguments: dict
        """
        if arguments is None:
            arguments = dict()
        self.arguments = arguments
        self.template = template
        self.name = name
        self.commande = commande
        self.process = list()

    def get(self, name=None, args=dict()):
        """
        Generate an external process
        :param name: Name of the process to identify it (should be unique)
        :param args: args to pass to add into the commande
        :type name: str
        :type args: dict
        """
        if name is None:
            name = "{0}_{1}".format(self.name, len(self.process))
        args = self.arguments.update(args)
        process = self.template(name, self.commande.format(args))
        self.process.append(process)
        return process

    def stop(self):
        """
        Stop all launched process
        """
        for process in self.process:
            process.stop()

    def join(self):
        """
        Join all launched process
        """
        for process in self.process:
            process.join()


class AbstractVLC(ExternalProcessFlag):
    """
    This class represent a VLC player
    """
    def __init__(self, *args, **kwargs):
        ExternalProcessFlag.__init__(self, *args, **kwargs)

    def _stop_process(self):
        """
        Ask to stop VLC in a clean way before call parent setop_process methode
        """
        self.stdin_queue.put_nowait("quit")
        ExternalProcess._stop_process(self)

    def check_media(self, media):
        """
        This function check if the media is present on the file system
        :param media: relative media path from the media directory
        :type media: str
        """
        path = os.path.join(settings.get_path("media"), media)
        if os.path.exists(path):
            return path
        else:
            return False

    def load(self, media):
        """
        This function add a media to the play list
        :param media: relative media path from the media directory
        :type media: str
        """
        path = self.check_media(media)
        if path is False:
            self._log("warning", "Unknown media {0} => aborting".format(media))
            return False
        # self.stdin_queue.put_nowait()
        self._direct_stdin_writer("load {0}".format(path))

    def repeat(self, value):
        """
        Set repeat falg
        :param value: True for repeat, False for no repeat
        :type value: bool
        :return:
        """
        self._direct_stdin_writer("repeat {0}".format(int(value)))

    def play(self):
        """
        Start VLC on the last added media
        """
        # self.stdin_queue.put("play")
        self._direct_stdin_writer("play")

    def toggle_pause(self):
        """
        This function toggle the pause statue of the current played media
        """
        self.stdin_queue.put("toggle")

    def pause(self):
        """
        This function pause the current played media
        """
        self.stdin_queue.put("pause")

    def resume(self):
        """
        This function resume the current played media
        """
        self.stdin_queue.put("resume")

    def stop_media(self):
        """
        This function ask VLC to stop the current played media
        """
        self.stdin_queue.put("stop")

    def _get_volume_value(self, volume):
        """
        This function return
         :param volume: Relative volume value betwenn 0 and 200 ( percent )
         :type volume: int
         :return: Absolute volume for VLC between 0 and 1024
         :rtype: int
        """
        return settings.get("vlc", "volume", "master") * (volume/100)

    def set_volume(self, volume):
        """
        This function set the volume of the current played file
         :param volume: Relative volume value betwenn 0 and 200 ( percent )
         :type volume: int
        """
        self.stdin_queue.put_nowait("volume {0}".format(self._get_volume_value(volume)))

    def volume_up(self):
        """
        This function add one step of volume. Volume step are defined in vlc command settings
        """
        self.stdin_queue.put("volup")

    def volume_down(self):
        """
        This function sub one step of volume. Volume step are defined in vlc command settings
        """
        self.stdin_queue.put("voldown")


# GENERIC THREAD TO HANDLE EXTERNAL PROCESS
class _ExternalProcess(object):
    """
    Watchdog thread to control external processes
    """
    Filters = {}

    def __init__(self, name=None):
        """
        :return:
        """
        self.name = name
        self._watchdog = None
        self._defunctdog = None
        self._running = threading.Event()
        self._popen = None
        self.command = ''
        self.stderr = None
        self.onOpen = None
        self.onClose = None
        self._c = 0
        self._stdin_queue = Queue(maxsize=16)
        self._stdin_thread = None
        if name:
            if name not in settings.get("path", "relative").keys():
                self.executable = settings.get("path", name)
            else:
                self.executable = settings.get_path(name)
            self.command = self.executable

    def start(self):
        """
        Start the external process
        :return:
        """
        self.stop()  # Stop current process
        self._watchdog = threading.Thread(target=self._watch)
        self._defunctdog = threading.Thread(target=self._defunct)
        self._stdin_thread = threading.Thread(target=self.stdin_thread)
        logfile = settings.get_path("logs") + '/' + self.name + '.log'
        try:
            self.stderr = open(logfile, 'w')
        except IOError:
            log.warning("There is no where ({0}) to put log of {1}".format(logfile, self.name))
            self.stderr = None
        self._running.set()
        # if self.name == 'vlcvideo':
        # log.debug('HIGH PRIORITY')
        #     self._popen = Popen( 'chrt -r 80 '+self.command, bufsize=0, executable=None, stdin=PIPE, stdout=PIPE, stderr=self.stderr,
        #                                      close_fds=False, shell=True, cwd=None, env=None,
        #                                      universal_newlines=False, startupinfo=None, creationflags=0, preexec_fn=None) 
        #                                     # preexec_fn=lambda : os.nice(-20)
        # else: 
        self._popen = Popen(shlex.split(self.command), bufsize=0, executable=None, stdin=PIPE, stdout=PIPE,
                            stderr=self.stderr,
                            close_fds=False, shell=False, cwd=None, env=None,
                            universal_newlines=False, startupinfo=None, creationflags=0, preexec_fn=None)
        # preexec_fn=lambda : os.nice(-20)
        self._watchdog.start()
        self._defunctdog.start()
        self._stdin_thread.start()
        register_thread(self)
        if self.onOpen:
            self.onEvent([self.onOpen])

    def _defunct(self):
        """
        Try to collect process to avoid defunct
        :return:
        """
        while self._popen.poll() is None:
            time.sleep(0.1)

    def clean_queue(self):
        """
        This function clean the queue
        :return:
        """
        self._stdin_queue.put_nowait(None)  # Release thread


    def stop(self):
        """
        Ask to stop the external process
        :return:
        """
        if self.is_running():
            self._stdin_queue.put_nowait(None)  # Ask to stop the stdin_thread
            try:
                self._popen.terminate()  # Send SIGTERM to the player, asking to stop
                log.debug('SIGTERM ' + self.name)
            except:
                pass
            self._watchdog.join(timeout=0.2)  # Waiting maximum of 250 ms before killing brutaly the processus
            if self._watchdog.is_alive():
                self._popen.kill()  # Send SIGNKILL to brutaly kill the process
                log.warning('KILLED ' + self.name)
            unregister_thread(self)
        self.join()  # Wait for watchdog thread to terminate

    def is_running(self):
        return self._running.is_set()

    def stdin_thread(self):
        """
        This function wait for a message to write into the stdin
        :return:
        """
        while True:
            if not self.is_running():
                time.sleep(0.1)
                continue
            msg = self._stdin_queue.get()
            if msg is None:
                break  # Ask to stop
            self._say(msg)

    def say(self, message):
        """
        This function overwrite the say ExternalProcess Function to add a queue
        :param message:
        :return:
        """
        log.important("Add {0} message to {1} queue".format(message, self.name))
        if message == "stop":
            log.important(show_trace())
        if not self.is_running() and message == "stop":
            log.error("CATCH AND AVOID stop BEFORE LAUNCED VLC")
            return
        self._stdin_queue.put_nowait(message)

    def _say(self, message):
        """
        This function is only used by the thread which write in the stdin
        :param message:
        :return:
        """
        if self.is_running():
            message += "\n"
            m = message.encode("utf-8")
            self._popen.stdin.write(m)
            log.log("important", " " + message)
        else:
            log.log("debug", "Message aborted, Thread not active ")

    def _watch(self):
        """
        This function wait the process to end and add a signal when it appends
        :return:
        """
        # self._popen.wait()
        lines_iterator = iter(self._popen.stdout.readline, b"")
        for line in lines_iterator:
            line = line.strip()
            # log.log("raw",self.name.upper()+" SAYS: "+line)
            # cmd = line.split(' ')[0]
            # args = line.split(' ')[1:]
            if line[0] == '#':
                self.onEvent(line.split(' '))
        if self.onClose:
            self.onEvent([self.onClose])
        self._running.clear()
        if self.stderr is not None:
            self.stderr.close()

    def join(self, timeout=None):
        """
        Join the video player to end
        :return:
        """
        if not self._watchdog:
            return True
        return self._watchdog.join(timeout=timeout)

    def onEvent(self, cmd=[]):
        cmd[0] = cmd[0].lstrip('#')
        doEmmit = True
        if cmd[0] in self.Filters.keys():
            for fn in self.Filters[cmd[0]]:
                if isinstance(fn, str):
                    filt = fn.split(' ')
                    method = getattr(self, filt[0], None)
                    if callable(method):
                        if len(filt) > 1:
                            doEmmit = method(cmd, filt[1:]) and doEmmit
                        else:
                            doEmmit = method(cmd) and doEmmit
        if doEmmit:
            self.emmit(cmd)

    def emmit(self, args=[]):
        signal_name = args[0].upper()
        if signal_name[0] == '/':
            signal_name = signal_name.replace('/', '_')[1:].upper()
        log.log("raw", signal_name + ' ' + ' '.join(args[1:]))
        if signal_name == "DEVICE_SENDINFOTENSION" and not settings.get("log", "tension", "active"):
            return  # Avoid patch flag if setting unactive send tension info
        flag = Flag(signal_name).get(args={"args": args[1:]})
        patcher.patch(flag)

    def __del__(self):
        log.log("raw", "Module thread destroyed")
        pass
