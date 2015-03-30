# -*- coding: utf-8 -*-
from distutils.core import setup, Extension

module_rtplib = Extension('rtplib', sources=['rtp.c'], extra_compile_args=['-Wall'], extra_link_args=['-Wall'])

setup(name='Rtp Librairy',
      version='0.1',
      description='This package provide C function for rtp time tasks',
      ext_modules=[module_rtplib])

