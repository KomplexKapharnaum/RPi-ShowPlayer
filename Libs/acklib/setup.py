# -*- coding: utf-8 -*-
from distutils.core import setup, Extension

module_acklib = Extension('acklib', sources=['ack.c'], extra_compile_args=['-Wall'], extra_link_args=['-Wall'])

setup(name='Ack Librairy',
      version='0.1',
      description='This package provide C function for ACK tasks',
      ext_modules=[module_acklib])

