import log
_log = log.init_log("engine")

MODULES_FSM = dict() # Store ENGINE MODULES FSM


def add_module(name, machine):
    # REGISTER ENGINE MODULES
    MODULES_FSM[name] = machine


def init():
    # INIT ENGINE THREADS
    import threads
    threads.init()


def start():
    # START ENGINE THREADS
    import threads
    threads.start()

    # START ENGINE MODULES
    from modules import DECLARED_ETAPES, MODULES
    for name, modulefsm in MODULES_FSM.items():
        modulefsm.start(MODULES[name])
        _log.info("= MODULE (Engine) :: "+name)


def stop():
    # STOP ENGINE THREADS
    import threads
    threads.stop()

    # STOP ENGINE MODULES
    local_modules = MODULES_FSM.items()
    for name, modulefsm in local_modules:
        _log.info("--- "+name)
        modulefsm.stop()
        modulefsm.join()