# -*- coding: utf-8 -*-
import os

import shlex
import threading

from libs.subprocess32 import Popen, PIPE
from engine.threads import patcher
from engine.tools import register_thread, unregister_thread
from engine.fsm import Flag
from engine.setting import settings
from engine.log import init_log, dumpclean
log = init_log("modules")


# GENERIC THREAD TO HANDLE EXTERNAL PROCESS
class ExternalProcess(object):
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
        self.stderr = None
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
        self.stderr = open(logfile, 'w')
        self._running.set()
        self._popen = Popen( shlex.split(self.command), bufsize=0, executable=None, stdin=PIPE, stdout=PIPE, stderr=self.stderr,
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
                #os.system("sudo kill %d"%(self._popen.pid))
                self._popen.kill()  # Send SIGNKILL to brutaly kill the process
            unregister_thread(self)
        self.join()# Wait for watchdog thread to terminate

    def is_running(self):
        return self._running.is_set()

    def say(self, message):
        if self.is_running():
            self._popen.stdin.write(message+"\n")
            log.log("raw"," "+message)
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
            patcher.patch(Flag(self.onClose).get())
        self._running.clear()
        self.stderr.close()

    def join(self, timeout=None):
        """
        Join the video player to end
        :return:
        """
        if not self._watchdog:
            return True
        return self._watchdog.join(timeout=timeout)

    @staticmethod
    def setFilters():
        return {}

    def onEvent(self, args=dict()):
        args[0] = args[0][1:]
        doEmmit = True
        filters = self.setFilters()
        if args[0] in filters.keys():
            filz = filters[ args[0] ][0]
            if not isinstance(filz, list):
                filz = [filz]
            for fn in filz:
                doEmmit = fn(self, args) and doEmmit
        if doEmmit:
            self.emmit(args)

    def emmit(self, args=dict()):
        signal_name = args[0].upper()
        log.log("raw", signal_name+' '+' '.join(args[1:]))
        flag = Flag(signal_name).get(args={"args": args[1:]})
        patcher.patch(flag)

    def __del__(self):
        log.log("raw", "Module thread destroyed")
        pass



# Auto Import Every Modules
for module in os.listdir(os.path.dirname(__file__)):
    if module == '__init__.py' or module == 'module.py' or module[-3:] != '.py':
        continue
    __import__(module[:-3], locals(), globals())
del module
