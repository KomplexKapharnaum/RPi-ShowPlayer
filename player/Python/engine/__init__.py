import log
_log = log.init_log("engine")
# Store SUPER MODULES FSM
MODULES_FSM = dict()


def add_module(name, machine):
    MODULES_FSM[name] = machine


def start():
    from modules import DECLARED_ETAPES, MODULES
    for name, modulefsm in MODULES_FSM.items():
        modulefsm.start(MODULES[name])
        _log.info("= MODULE (Engine) :: "+name)


def stop():
    for name, modulefsm in MODULES_FSM.items():
        _log.info("--- "+name)
        modulefsm.stop()
        modulefsm.join()
