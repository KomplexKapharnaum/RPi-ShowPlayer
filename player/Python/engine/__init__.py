import log
_log = log.init_log("engine")
# Store SUPER MODULES FSM
MODULES_FSM = dict()


def add_module(name, machine):
    MODULES_FSM[name] = machine
    _log.debug("LOAD MANAGER :: "+name+" (Auto)")


def start_modules():
    from modules import DECLARED_ETAPES, MODULES
    for name, modulefsm in MODULES_FSM.items():
            _log.debug('modules {0}'.format(DECLARED_ETAPES[ MODULES[name]['init_etape'] ].strfunc()))
            modulefsm.start(DECLARED_ETAPES[ MODULES[name]['init_etape'] ])


def stop_modules():
    for name, modulefsm in MODULES_FSM.items():
        _log.info("--- "+name)
        modulefsm.stop()
        modulefsm.join()
