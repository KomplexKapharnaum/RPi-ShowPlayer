import shlex
import threading

from libs import subprocess32
from engine.threads import patcher
from engine.tools import register_thread, unregister_thread

# GENERIC THREAD TO HANDLE EXTERNAL PROCESS
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
        self.onOpen = None
        self.onClose = None

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
        if self.onOpen:
            patcher.patch(self.onOpen.get())

    def _watch(self):
        """
        This function wait the process to end and add a signal when it appends
        :return:
        """
        self._popen.wait()
        if self.onClose:
            patcher.patch(self.onClose.get())
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

    def is_alive():
        return self._running.is_set()

    def join(self, timeout=None):
        """
        Join the video player to end
        :return:
        """
        return self._watchdog.join(timeout=timeout)
