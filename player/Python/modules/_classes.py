# -*- coding: utf-8 -*-
#

import os
import shlex
import threading
import sys
import codecs
import signal

signal.signal(signal.SIGCLD, signal.SIG_IGN)    # Avoid defunct process (just ignore them if they crash
                                                # More info :
                                                # http://stackoverflow.com/questions/16944886/how-to-kill-zombie-process
                                                # http://bugs.python.org/issue15756

from modules import MODULES
from libs.subprocess32 import Popen, PIPE
from engine.threads import patcher
from engine.tools import register_thread, unregister_thread
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


# GENERIC THREAD TO HANDLE EXTERNAL PROCESS
class ExternalProcess(object):
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
        self._running = threading.Event()
        self._popen = None
        self.command = ''
        self.stderr = None
        self.onOpen = None
        self.onClose = None
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
        self.stop()# Stop current process
        self._watchdog = threading.Thread(target=self._watch)
        logfile = settings.get_path("logs")+'/'+self.name+'.log'
        try:
            self.stderr = open(logfile, 'w')
        except IOError:
            log.warning("There is no where ({0}) to put log of {1}".format(logfile, self.name))
            self.stderr = None
        self._running.set()
        # if self.name == 'vlcvideo':
        #     log.debug('HIGH PRIORITY')
        #     self._popen = Popen( 'chrt -r 80 '+self.command, bufsize=0, executable=None, stdin=PIPE, stdout=PIPE, stderr=self.stderr,
        #                                      close_fds=False, shell=True, cwd=None, env=None,
        #                                      universal_newlines=False, startupinfo=None, creationflags=0, preexec_fn=None) 
        #                                     # preexec_fn=lambda : os.nice(-20)
        # else: 
        self._popen = Popen(shlex.split(self.command), bufsize=0, executable=None, stdin=PIPE, stdout=PIPE, stderr=self.stderr,
                                         close_fds=False, shell=False, cwd=None, env=None,
                                         universal_newlines=False, startupinfo=None, creationflags=0, preexec_fn=None) 
                                        # preexec_fn=lambda : os.nice(-20)
        self._watchdog.start()
        register_thread(self)
        if self.onOpen:
            self.onEvent([self.onOpen])

    def stop(self):
        """
        Ask to stop the external process
        :return:
        """
        if self.is_running():
            try:
                self._popen.terminate()  # Send SIGTERM to the player, asking to stop
                log.debug('SIGTERM '+self.name)
            except:
                pass
            self._watchdog.join(timeout=0.2)  # Waiting maximum of 250 ms before killing brutaly the processus
            if self._watchdog.is_alive():
                self._popen.kill()  # Send SIGNKILL to brutaly kill the process
                log.warning('KILLED '+self.name)
            unregister_thread(self)
        self.join()# Wait for watchdog thread to terminate

    def is_running(self):
        return self._running.is_set()

    def say(self, message):
        if self.is_running():
            message += "\n"
            m = message.encode("utf-8")
            self._popen.stdin.write(m)
            log.log("raw", " "+message)
        else:
            # log.log("debug", "Message aborted, Thread not active ")
            pass

    def _watch(self):
        """
        This function wait the process to end and add a signal when it appends
        :return:
        """
        #self._popen.wait()
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
        log.log("raw", signal_name+' '+' '.join(args[1:]))
        flag = Flag(signal_name).get(args={"args": args[1:]})
        patcher.patch(flag)

    def __del__(self):
        log.log("raw", "Module thread destroyed")
        pass
