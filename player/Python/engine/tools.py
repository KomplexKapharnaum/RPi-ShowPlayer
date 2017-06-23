# -*- coding: utf-8 -*-
#
# Define some basic tools for the project
#
#
import liblo
import weakref
import sys
import traceback
import os
import time
import unicodedata
import subprocess
import shlex
import threading
import Queue

from libs.unidecode import unidecode

from setting import settings
import engine
import scenario
from engine.log import init_log
from libs import subprocess32

log = init_log("tools")

_to_stop_thread = dict()

flag_popup = engine.fsm.Flag("REMOTE_POPUP")


def remove_nonspacing_marks(s):
    """Decompose the unicode string s and remove non-spacing marks."""
    return ''.join(c for c in unicodedata.normalize('NFKD', s)
                   if unicodedata.category(c) != 'Mn')


def register_thread(thread):
    """
    This function register a thread to stop it at the end of
    :param thread:
    :return:
    """
    global _to_stop_thread
    _to_stop_thread[id(thread)] = weakref.ref(thread)


def unregister_thread(thread):
    """
    This function unregister a thread to avoid keeping a weakref to it
    :param thread: thread to unreference
    :return:
    """
    global _to_stop_thread
    del _to_stop_thread[id(thread)]


def get_smallest_difference(elements, n):
    min_value = None
    min_elems = None
    for elem in elements:
        tmp_elements = list(elements)
        tmp_elements.remove(elem)
        final_list = list()
        for i in xrange(n):
            a = min(tmp_elements, key=lambda x: abs(x - elem))
            tmp_elements.remove(a)
            final_list.append(a)
        if min_value > (max(final_list) - min(final_list)) or min_value is None:
            min_value = (max(final_list) - min(final_list))
            min_elems = final_list
    return min_value, min_elems


def sleep_thread(time, dt=0.5):
    pass


def set_python_path(depth=0):
    f = sys._getframe(1)
    fname = f.f_code.co_filename
    fpath = os.path.dirname(fname)
    PythonPath = os.path.join(fpath, "../".join(["" for x in xrange(depth + 1)]))
    sys.path.append(PythonPath)


def search_in_or_default(key, indict, setting=False, default=None):
    """
    This function search the key into the indict or return default value
    :param key: Key or tuple of keys to search in, if tuple it will return a dict of found values
    :param indict: Dict of values to search in
    :param setting: If not false it must be a tuple of keys to search in settings as ("values","gyro")
    :param default: If really not found it will return None
    :return:
    """
    if isinstance(key, (list, tuple)):
        outdict = dict()
        for k in key:
            outdict[k] = search_in_or_default(k, indict, setting=setting, default=default)
        return outdict
    if key in indict.keys():
        return indict[key]
    elif setting is not False:
        try:
            setting.append(key)
            return settings.get(*setting)
        except AttributeError, KeyError:
            log.log("raw", "Search for a setting value which doesn't exist")
            return None
    return default


def old_log_teleco(ligne1=" ", ligne2=" ", error=False, encode="utf-8"):
    """
    This function log a message to the teleco
    :param ligne1:
    :param ligne2:
    :param error: Set if it's an error or not, if True wait for the error_delay teleco setting
    :param encode: Encoding of input strings, if none, assume data are already encoded
    :return:
    """
    if encode is not None:
        if ligne1 is not None:
            ligne1 = ligne1.decode(encode)
        if ligne2 is not None:
            ligne2 = ligne2.decode(encode)
    ligne1 = remove_nonspacing_marks(ligne1)
    ligne2 = remove_nonspacing_marks(ligne2)
    engine.threads.patcher.patch(flag_popup.get(args={"ligne1": ligne1, "ligne2": ligne2}))
    if error:
        time.sleep(settings.get("log", "teleco", "error_delay"))


def log_teleco(lines, page="log", encode="utf-8"):
    """
    This function log a message to the teleco
    :param lines: Lines to display
    :param page: Page number where the message must be displayed
    :param encode: Encoding of input strings, if none, assume data are already encoded
    :return:
    """
    try:
        if settings.get("log", "teleco", "active") is not True and page == "log":
            return
        if not isinstance(lines, (list, tuple)):
            lines = [lines, ]
        encoded_lines = list()
        encode = None
        if encode is not None:
            for line in lines:
                encoded_lines.append(remove_nonspacing_marks(line.decode(encode)))
        else:
            encoded_lines = lines
        engine.threads.log_teleco.add_message(encoded_lines, page)
    except Exception as e:
        log.warning(log.show_exception(e))


def check_internet_link():
    """
    This function check if internet is present (by ping at google dns..)
    :return True if success, False otherwise
    """
    with open(os.devnull, 'r') as DEVNULL:
        return subprocess32.call(['ping', '-c', '3', '-i', '0.5', '-W', '2', '8.8.8.8'], stdout=DEVNULL) == 0


def check_fs_mode(fs="/dnc"):
    """
    This function check if a file system is in read only or read write mode
    :return True if read-write, False if read-only
    """
    return subprocess32.call("cat /proc/mounts|grep \" {0} \"|cut -d\" \" -f 4|grep ^rw >/dev/null".format(fs),
                             shell=True) == 0


def remount_fs(fs="/dnc", mode="ro"):
    """
    This function remount the given file system in the given mode
    :return True if success, False otherwise
    """
    return subprocess32.call(['mount', '-o', '{mode},remount'.format(mode=mode), fs]) == 0


def update_system():
    """
    This function check if there is a need and a way to update current code from the git repo, is it's the case
    it stash changes and pull new code from git
    """
    log.log("important", "UPDATE: start system update")
    if check_internet_link():
        # There is an internet connexion
        if subprocess32.call(
                "cd /dnc; [ $(git ls-remote origin -h refs/heads/$(git rev-parse --abbrev-ref HEAD)|cut -f 1) == $(git rev-parse HEAD) ];",
                shell=True) == 0:
            # There is no update needed : abort
            log.log("important", "UPDATE: no update needed")
            return
        remount_ro = False
        if check_fs_mode("/dnc") is not True:
            log.log("important", "UPDATE: set filesystem to READ-WRITE during update ...")
            if remount_fs("/dnc", "rw"):
                remount_ro = True
            else:
                log.log("error", "UPDATE: impossible to set filesystem in READ-WRITE mode : abort update")
                return
        try:
            git = subprocess32.check_output(['git', 'stash']).strip()
            log.log("important", "UPDATE: {0}".format(git))
            git = subprocess32.check_output(['git', 'pull']).strip()
            log.log("important", "UPDATE: {0}".format(git))
        except subprocess32.CalledProcessError:
            log.log("error", "UPDATE: impossible to update : git error")
        if remount_ro:
            remount_fs("/dnc", "ro")
    else:
        log.log("warning", "UPDATE: no internet connexion : abort update")


def restart_netctl():
    """
    This function restart netctl
    :return:
    """
    if settings.get("sys", "raspi"):
        log.info("Restarting NETCTL auto-wifi ...")
        log.debug("Restart netctl return {0}".format(
            subprocess.check_call(
                shlex.split(settings.get("path", "systemctl") + " restart netctl-auto@wlan0.service"))))
        log_teleco(("network restart", "succes"), "sync")
    else:
        log.debug("Don't restart netctl because we are not on a raspi")


# TOOLS 
def send_monitoring_message(oscMessage):
    port = settings.get("log", "monitor", "port")
    for dest in settings.get("log", "monitor", "ip"):
	try:
	        liblo.send(liblo.Address(dest, port), oscMessage)
	except IOError:
		log.debug("Fail to send monitoring message ..")


def sendPing():
    message = liblo.Message("/ping", settings.get("uName"))
    send_monitoring_message(message)
    log.raw("send ping")


class ThreadTeleco(threading.Thread):
    """
    This thread is here to display messages in teleco. If the given message his too large it will be cut in smaller
    parts and displayed parts by parts
    """

    def __init__(self):
        threading.Thread.__init__(self)
        register_thread(self)
        self._stop = threading.Event()
        self._pages = Queue.Queue()
        # self._pages = list()
        # self._pages.append(list())  # Page 0
        # self._pages.append(list())  # Page 1
        # self._pages.append(list())  # Page 2
        # self._pages_lock = threading.Lock()
        # self._something_new = threading.Event()

    def stop(self):
        self._stop.set()

    def run(self):
        while not self._stop.is_set():
            try:
                to_display = self._pages.get(timeout=2)
            except Exception:
                continue
            # with self._pages_lock:
            # for n, page in enumerate(self._pages):
            #         if len(page) < 1:       # There is nothing to display
            #             continue
            #         to_display = self._pages.pop(n), n
            #         break
            ThreadTeleco._display_message(*to_display)

    def add_message(self, message, page=0):
        """
        This function add a message to be displayed in a page
        :rtype : object
        :param message: message to display : list of lines
        :param page: page where the message must be displayed
        :return:
        """
        self._pages.put((message, page))

    @staticmethod
    def _display_message(message, page):
        """
        This function display a message in a page
        :param message: message to display
        :param page: page where the message must be displayed
        :return:
        """
        try:
            message = ThreadTeleco.prepare_message(message)
            if message is not None:
                for n, bloc in enumerate(message):
                    args = dict()
                    if len(bloc) > 0:
                        args["ligne1"] = str(bloc[0])
                        if len(bloc) > 1:
                            args["ligne2"] = str(bloc[1])
                        else:
                            args["ligne2"] = ""
                        args["page"] = page
                        if page == "error":  # TODO process error in fsm of popup rather than here
                            args["ligne1"] = "error"
                            args["ligne2"] = "no show"
                        engine.threads.patcher.patch(flag_popup.get(args=args))
                        if len(message) >= n + 1:
                            time.sleep(settings.get("log", "teleco", "autoscroll"))
        except Exception as e:
            log.warning(log.show_exception(e))

    @staticmethod
    def prepare_message(message):
        """
        This function prepare a message to be displayed by checking his lines
        :param message: message to prepare
        :return:
        """
        try:
            linelength = settings.get("log", "teleco", "linelength")
            lines = list()
            blocs = list()
            blocs.append(list())
            for line in message:
                if hasattr(line, '__len__'):
                    while len(line) > linelength:
                        lines.append(line[:linelength])
                        line = line[linelength:]
                    lines.append(line)
            for line in lines:
                if len(blocs[-1]) == 2:
                    blocs.append(list())  # New block
                blocs[-1].append(line)
            return blocs
        except Exception as e:
            log.warning(log.show_exception(e))
            return None


def show_trace():
    traceback.print_stack()

def get_git_branch():
    """
    :return: current git branch
    """
    branch = subprocess.check_output(['git', 'branch']).split("\n")
    for line in branch:
        if len(line) > 0 and line[0] == "*":
            return line[2:]


def get_git_last_commit():
    """
    :return: tuple: commit id, commit date, commit msg
    """
    commit = subprocess.check_output(['git', 'show', '--pretty="%h%n%ai%n%s"',
                                      '--raw']).split("\n")
    return (commit[0][1:], commit[1], commit[2][:-1])


def get_state_dict(key):
    if key not in scenario.pool.State.keys():
        scenario.pool.State[key] = dict()
    return scenario.pool.State[key]


engine.log.log_teleco = log_teleco  # This add log_teleco real function to log to avoid circular import
