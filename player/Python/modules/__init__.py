# -*- coding: utf-8 -*-
import os

import shlex
import threading

from libs.subprocess32 import Popen, PIPE
from engine.threads import patcher
from engine.tools import register_thread, unregister_thread
from engine.fsm import Flag
from engine.setting import settings
from engine.log import init_log
log = init_log("modules")


# GENERIC THREAD TO HANDLE EXTERNAL PROCESS
class ExternalProcess:
    """
    Watchdog thread to control external processes
    """
    def __init__(self, name=None):
        """
        :return:
        """
        self.name = name
        self._watchdog = None
        self._running = threading.Event()
        self._popen = None
        self.command = ''
        self.stdout = None
        self.onOpen = None
        self.onClose = None
        if name:
            self.executable = settings.get("path", name)
            self.command = self.executable

    def start(self):
        """
        Start the external process
        :return:
        """
        self.stop()# Stop current process
        self._watchdog = threading.Thread(target=self._watch)
        logfile = settings.get("path", "logs")+'/'+self.name+'.log'
        self.stdout = open(logfile, 'w')
        self._running.set()
        self._popen = Popen( shlex.split(self.command), bufsize=0, executable=None, stdin=PIPE, stdout=self.stdout, stderr=self.stdout,
                                         preexec_fn=None, close_fds=False, shell=False, cwd=None, env=None,
                                         universal_newlines=False, startupinfo=None, creationflags=0)
        self._watchdog.start()
        register_thread(self)
        if self.onOpen:
            patcher.patch(Flag(self.onOpen).get())

    def stop(self):
        """
        Ask to stop the external process
        :return:
        """
        if self.is_running():
            if self._popen.poll():
                self._popen.terminate()  # Send SIGTERM to the player, asking to stop
            self._watchdog.join(timeout=0.1)  # Waiting maximum of 250 ms before killing brutaly the processus
            if self._watchdog.is_alive():
                self._popen.kill()  # Send SIGNKILL to brutaly kill the process
            unregister_thread(self)
        self.join()# Wait for watchdog thread to terminate

    def is_running(self):
        return self._running.is_set()

    def say(self, message):
        if self.is_running():
            self._popen.stdin.write(message+"\n")
            # log.log("debug",message)
        else:
            # log.log("debug", "Message aborted, Thread not active ")
            pass

    def _watch(self):
        """
        This function wait the process to end and add a signal when it appends
        :return:
        """
        self._popen.wait()
        if self.onClose:
            patcher.patch(Flag(self.onClose).get())
        self._running.clear()
        self.stdout.close()

    def join(self, timeout=None):
        """
        Join the video player to end
        :return:
        """
        if not self._watchdog:
            return True
        return self._watchdog.join(timeout=timeout)

    def __del__(self):
        log.log("raw", "Module thread destroyed")
        pass



# Auto Import Every Modules
for module in os.listdir(os.path.dirname(__file__)):
    if module == '__init__.py' or module == 'module.py' or module[-3:] != '.py':
        continue
    __import__(module[:-3], locals(), globals())
del module
