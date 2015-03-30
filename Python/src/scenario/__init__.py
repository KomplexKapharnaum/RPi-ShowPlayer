# -*- coding: utf-8 -*-


import pool

DECLARED_FUNCTIONS = dict()
DECLARED_ETAPES = dict()
DECLARED_SIGNALS = dict()



def init_declared_objects():
    import functions
    import etapes
    import signals
    global DECLARED_ETAPES, DECLARED_FUNCTIONS, DECLARED_SIGNALS
    pool.Etapes_and_Functions.update(DECLARED_FUNCTIONS)
    pool.Etapes_and_Functions.update(DECLARED_ETAPES)
    pool.Signals.update(DECLARED_SIGNALS)
