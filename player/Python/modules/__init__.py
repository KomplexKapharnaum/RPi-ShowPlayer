# -*- coding: utf-8 -*-
import os

MODULES = dict()

# Auto Import Every Modules
for module in os.listdir(os.path.dirname(__file__)):
    if module == '__init__.py' or module == 'module.py' or module[-3:] != '.py':
        continue
    __import__(module[:-3], locals(), globals())
del module
