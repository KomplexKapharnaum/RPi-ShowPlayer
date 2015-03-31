import shlex
import threading
from libs import subprocess32
import scenario
from engine.tools import register_thread, unregister_thread
from engine.setting import settings
from engine.threads import patcher
from engine.log import init_log

log = init_log("INTERFACE")


# Server Thread module
class Webserver:
    """
    Serving interface to Web Browser
    """
    def __init__(self):
        """
        :return:
        """
        register_thread(self)
        self._waiting_th = threading.Thread(target=self._wait_process_end)
        self._popen = None
        self._running = threading.Event()
        self._cmd_line = "python2 {script}".format(script=settings.get("path", "interface"))
        self.arguments = shlex.split(self._cmd_line)

    def start(self):
        """
        Start Web Server
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
        self._waiting_th.join(timeout=0.1)  # Waiting maximum 100ms
        if self._waiting_th.is_alive():
            self._popen.kill()  # Send SIGNKILL to brutaly kill the process
        unregister_thread(self)

    def _wait_process_end(self):
        """
        This function wait the process to end and add a signal when it appends
        :return:
        """
        self._popen.wait()
        patcher.patch(scenario.signals.signal_web_end_server.get())
        self._running.clear()

    def join(self, timeout=None):
        """
        Join the video player to end
        :return:
        """
        return self._waiting_th.join(timeout=timeout)


def interface_start(flag, **kwargs):
    if "interface" not in kwargs["_fsm"].vars.keys():
        kwargs["_fsm"].vars["interface"] = Webserver()
        try:
            kwargs["_fsm"].vars["interface"].start()
        except Exception as e:
            log.error("CAN'T START INTERFACE !")
            log.error(": " + str(e))

# REGISTER ETAPES & SIGNALS
etape_interface_start = scenario.classes.Etape("INTERFACE_START", actions=((interface_start, {}), ))
scenario.etapes.declareetape(etape_interface_start)
