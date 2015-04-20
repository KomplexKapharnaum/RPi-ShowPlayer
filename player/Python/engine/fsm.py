# -*- coding: utf-8 -*-

import copy
import threading

from collections import deque

from libs import rtplib
from engine.log import init_log
from engine.setting import settings

is_perf_enabled = settings.get("perf", "enable")
if is_perf_enabled:
    import inspect
    import sys
    from engine import perf
    is_history_enabled = settings.get("perf", "history", "enable")
    is_flag_enabled = settings.get("perf", "history", "withflag")
    is_exception_enabled = settings.get("perf", "history", "withexception")
# import scenario

log = init_log("fsm")


class FSMException(Exception):
    pass


class Flag:
    """
    This class define a Flag.
    A Flag is like a signal in the FSM theory, but here there are some additions
     * TTL and JTL, in order to control time aspect to prevent some problems in protocol fsm
     * Ignore management, if a Flag do not perform a transition or die we can manage this
     * Args, flag can carry some informations like an OSC message
    """

    def __init__(self, flag_uid, args={}, JTL=0, TTL=0.500, ignore_cb=None, ignore_cb_args=(), public_name=None):
        """
        Init method
        :param flag_uid: unique id for the Flag type
        :param args: args to carry
        :param JTL: Jump To Live, number of jump a Flag can live, None = never die by JTL
        :param TTL: Time To Live, time a Flag can live, None = never die by TTL
        :param ignore_cb: If Flag is ignore, this function will be call, if True it raise an excpt.
        :param ignore_cb_args: Args for the ignore_cb function
        :return:
        """
        self.uid = flag_uid
        self.args = dict(args)
        self.JTL = JTL
        self._TTL = TTL
        self.TTL = None
        self.ignore_cb = ignore_cb
        self.ignore_cb_args = tuple(ignore_cb_args)
        self._time_created = None  # This object haven't been get

    def get(self, args=None, **kwargs):
        """
        This method return a copy of the flag but ready to be a real signal and not just a patern
        :param args: If None, ignore, if not, replace current args
        :param **kwargs: Can overload default parameter for the copy
        :return: Flag object, but initialized to be a real signal
        """
        flag = copy.deepcopy(self)
        # flag = Flag(self.uid, args=copy.deepcopy(self.args),
        # JTL=self.JTL, TTL=self.TTL, ignore_cb=copy.deepcopy(self.ignore_cb),
        # ignore_cb_args=copy.deepcopy(self.ignore_cb_args), public_name=None)
        if args is not None:
            flag.args = args
        for key, item in kwargs.items():
            flag.__dict__[key] = item
        flag._time_created = rtplib.get_time()
        log.log("raw", "Create flag to : {0}s {1}ns".format(*flag._time_created))
        if flag._TTL is not None:  # Initialize time TTL
            log.log("raw", "Add TTL : {0}".format(flag._TTL))
            flag.TTL = rtplib.add_time(flag._time_created[0], flag._time_created[1], flag._TTL)
            log.log("raw", "TTL init to : {0}s {1}ns".format(*flag.TTL))
        return flag

    def ignore(self, reason=None):
        """
        This method is called when a Flag is ignored
        :param reason: Can be set to explain the reason (TTL, JTL etc..)
        :return:
        """
        log.log("raw", "Ingore flag {0} cause of : {1}".format(self, reason))
        if self.ignore_cb is not None:
            if self.ignore_cb is True:
                raise FSMException(reason)
            else:
                log.log("raw", "Ignore FLAG {uid}, reason : {r}".format(uid=self.uid, r=reason))
                threading.Thread(target=self.ignore_cb, args=self.ignore_cb_args).start()

    def __str__(self):
        return "Flag : {0} - {1}".format(self.uid, self.args)
        # return "Flag : {0}".format(self.uid)

    def get_info(self):
        """
        This function return large info on a flag
        """
        return "Flag : {0} [TTL:{2}, JTL:{3}] - {1}".format(self.uid, self.args, self.TTL, self.JTL)

    def __repr__(self):
        return self.__str__()


class State:
    """
    This function define a State in the FSM theory
     * A State have a main method which is run when the FSM launch it.
        This function can be run in a thread so it must release the premptible Event as soon as it can
     * A State must define some transitions to allow the FSM to evolve
        If True : The transition is cross asap but carry up the flag (Conditional transsition)
        If None : The transition is cross asap but don"t carry the flag
        If Flag : The transition is cross if the Flag is present in the FSM flag stack
    """

    def __init__(self, state_uid, function, transitions={}):
        """
        Init methode
        :param state_uid: Unique id for the State
        :param function: the function wich is run during the State
        :param transitions: Dict of transitions, can't be empty !
        :return:
        """
        self.uid = state_uid
        self.function = function
        self.transitions = dict(transitions)
        self.preemptible = threading.Event()
        self.stop = threading.Event()

    # def __call__(self, *args, **kwargs):
    # return self.run(*args, **kwargs)

    def run(self, flag):
        """
        This method run the function define in the State and manage preemetible state
        :param flag: The flag wich trigged the State
        :return:
        """
        return_code = True
        log.log("raw", "Run state, uid : {0}, flag : {1}".format(self.uid, flag))
        self.stop.clear()
        self.preemptible.clear()
        try:
            self.function(flag)
        except Exception as e:
            log.log("error", "State function faill !")
            log.exception(e)
            if is_history_enabled and is_exception_enabled:
                return_code = e, sys.exc_info()
            pass
        finally:
            self.preemptible.set()
            log.log("raw", "Preemptible state, uid : {0}".format(self.uid, flag))
            return return_code

    def __str__(self):
        return "State : {0}".format(self.uid)

    def __repr__(self):
        return self.__str__()


class FiniteStateMachine:
    """
    A Finite-state machine (https://en.wikipedia.org/wiki/Finite-state_machine) have a define
        and finite number of State. Each State can have transition in order to allow the FSM to
        evole when it get signals
    """

    def __init__(self, name="FSM", flag_stack_len=256, fsmtype="fsm", source=None):
        """
        Init method
        :param name: optional name for the FSM, usefull for debug
        :param flag_stack_len: Define the length of the flag stack
        :param fsmtype: For perf : Type of FSM (fsm or scenario)
        :param source: For perf : Source of the FSM
        :return:
        """
        self.name = name
        self.vars = {}
        self._flag_stack = deque(maxlen=flag_stack_len)
        self._lock_flag_stack = threading.Lock()
        # self._event_flag_stack_not_empty = threading.Event()
        self._event_flag_stack_new = threading.Event()
        self.current_state = None
        # self.states = {}
        self._event_stop = threading.Event()
        self._event_stop.set()
        self.main_thread = None
        self._perf_ref = None  # Ref to the perf FSM object
        if is_perf_enabled:
            self._perf_ref = perf.declare_fsm(self, fsmtype, source=source)

    def stop(self):
        log.log("raw", "Asking {0} FiniteStateMachine to stop".format(self.name))
        self._event_stop.set()
        self._event_flag_stack_new.set()  # To directly stop the FSM if it waits for flag
        if is_perf_enabled:
            perf.undeclare_fsm(self)
            # self._event_flag_stack_not_empty.set()

    def join(self):
        if self.main_thread is None:
            return True
        else:
            return self.main_thread.join()

    def append_flag(self, flag):
        """
        This method is run by an environemental element which want to add a flag to the stack
        :param flag: The flag to add
        :return:
        """
        with self._lock_flag_stack:
            log.log("raw", "Append flag {0} to {1}".format(flag, self))
            if is_perf_enabled and is_history_enabled and is_flag_enabled:
                self._perf_ref.flag_event(flag, event="add", event_args={"frame": inspect.stack()[1][0],
                                                                         "JTL": flag.JTL,
                                                                         "TTL": flag._TTL})
            self._flag_stack.append(flag)
            # self._event_flag_stack_not_empty.set()
            self._event_flag_stack_new.set()
            # log.log("raw", "Flag stack of {1} : {0}".format(self._flag_stack, self))

    def _catch_flag(self, flag, state):
        """
        This method is called only by the FSM when a Flag correspond to a transition to a state
        :param flag: The concern flag
        :param state: The state which is in the transition
        :return: False = do not consume flag, None = do consume flag, True = new state + consume flag
        """
        log.log("raw", "[{2}] Catch flag {0} to state {1}".format(flag, state, self))
        if not isinstance(state, State):  # This is not directly a State
            if state in (True, None):
                return state  # Do not perform transition
            else:  # It's a transition
                if is_perf_enabled and is_history_enabled:
                    self._perf_ref.condition_transition(self.current_state, state, flag)
                return self._catch_flag(flag, state(flag))  # Go throw it
        else:
            if is_perf_enabled and is_history_enabled:
                self._perf_ref.change_step(self.current_state, state, flag)
            return self._change_state(flag, state)

    def _change_state(self, flag, state):
        """
        This method is called only by the FSM when a Flag perform a transition
        :param flag: The flag which perform the transition
        :param state: The new state to run
        :return:
        """
        log.log("raw", "[{0}] - Start change state to {1} because of {2}".format(self, state, flag))
        if self.current_state is not None:
            self.current_state.stop.set()
        self.current_state = state
        return_code = state.run(flag)       # Can be a thread inside or not
        if return_code is not True and is_perf_enabled and is_history_enabled and is_exception_enabled:
            self._perf_ref.log_exception(*return_code)
        self._clean_flag_stack(jump=True)
        state.preemptible.wait()
        # Now watch if there is some direct transition to perform
        if True in state.transitions.keys():
            log.log("raw", "[{0}]:{1} - Auto goto {2} cause to TRUE in transition".format(self, state,
                                                                                          state.transitions[True]))
            self._catch_flag(flag, state.transitions[True])
        elif None in state.transitions.keys():
            log.log("raw", "[{0}]:{1} - Auto goto {2} cause to NONE in transition".format(self, state,
                                                                                          state.transitions[None]))
            self._catch_flag(None, state.transitions[None])
        self._event_flag_stack_new.set()  # An old signal can now be interesting !
        log.log("raw", "[{0}] - End change state".format(self))
        return True

    def _clean_flag_stack(self, jump=False):
        """
        This method is only called by the FSM. It cleans all current flag wich must be clean in stack
        :param jump: If jump is True, decrease JTL
        :return:
        """
        with self._lock_flag_stack:
            # log.log("raw", "- FSM ({0}) : Start clean flag stack ".format(self.name))
            expired_flags = list()
            for flag in self._flag_stack:
                if flag.JTL is not None:
                    if jump:
                        flag.JTL -= 1
                    if flag.JTL < 0:
                        flag.ignore(reason="JTL")
                        if is_perf_enabled and is_history_enabled and is_flag_enabled:
                            self._perf_ref.flag_event(flag, event="removed",
                                                      event_args={"reason": "JTL", "value": flag.JTL})
                        expired_flags.append(flag)
                        # log.log("raw", "JTL Expiration: {0}".format(flag.uid))
                if flag.TTL is not None and flag not in expired_flags:
                    if rtplib.is_expired(*flag.TTL):
                        flag.ignore(reason="TTL")
                        if is_perf_enabled and is_history_enabled and is_flag_enabled:
                            self._perf_ref.flag_event(flag, event="removed",
                                                      event_args={"reason": "TTL", "value": flag._TTL})
                        expired_flags.append(flag)
                        # log.log("raw", "TTL Expiration: {0}".format(flag.uid))
            for flag in expired_flags:
                try:
                    # log.log("raw", "[{1}] Remove flag {0}".format(flag.uid, self))
                    self._flag_stack.remove(flag)
                except ValueError:
                    log.log("debug", "[{1}] ERROR Removing flag {0}".format(flag.uid, self.name))
            if len(self._flag_stack) == 0:
                # self._event_flag_stack_not_empty.clear()
                self._event_flag_stack_new.clear()
            #log.log("raw", "- FSM ({0}) : End clean flag stack ".format(self))

    def _wait_for_transition(self):
        """
        This method only wait that a transition can change the state of the FSM
        :return:
        """
        while self._event_stop.is_set() is not True:
            # self._event_flag_stack_not_empty.wait()
            log.log("raw", "- FSM ({0}) : Wait for interesting flags ! ".format(self))
            self._event_flag_stack_new.wait()
            log.log("raw", "- FSM ({0}) : Something append in flag stack ".format(self))
            if self._event_stop.is_set():
                break
            self._clean_flag_stack(jump=False)
            with self._lock_flag_stack:
                transition = None
                for flag in self._flag_stack:
                    if flag.uid in self.current_state.transitions.keys():
                        log.log("raw", "- FSM ({0}) : Found transition on flag {0}".format(self, flag.uid))
                        transition = flag
                        break
            if transition is not None:
                consume = self._catch_flag(transition, self.current_state.transitions[flag.uid])
                if consume is not False:
                    if isinstance(flag, Flag):
                        with self._lock_flag_stack:
                            # log.log("raw", "- FSM ({0}) : Consume {0} flag".format(self, flag))
                            try:
                                self._flag_stack.remove(flag)
                            except ValueError:
                                pass
                else:
                    log.log("warning", "- FSM ({0}) : Don't consume {0} flag cause return False".format(self, flag))
            else:  # There isn't any interesting flag !
                self._event_flag_stack_new.clear()
        log.log("debug", "{0} Finite state machine stop".format(self.name))

    def start(self, init_state):
        """
        This method is run by the environnement, and there can not be two same FSM
            running in the same time
        :param init_state: The state which must run at start
        :return: False = can't start, True = started
        """
        if self._event_stop.is_set() is not True:
            return False
        self._event_stop.clear()
        self._change_state(None, init_state)
        self.main_thread = threading.Thread(target=self._wait_for_transition)
        self.main_thread.start()
        return True

    def __str__(self):
        return "FSM : {name} on step {step}".format(name=self.name, step=self.current_state)

    def __repr__(self):
        return self.__str__()
