# -*- coding: utf-8 -*-
#
# This file provide tools to manipulate shared memory
#
#

###
# TODO # Update value on change
###

###
# WARNING #
#
# Unusable in this state
#
###

import os
import mmap
import struct
import ctypes


from engine.setting import settings
from engine.log import init_log
log = init_log("shared")


class SharedException(Exception):
    pass


class SharedPageOneWayWriter:
    """
    This class represent a shared page in memory
    OneWayWritter is because this process must be the only one which write into the mmap
    """

    def __init__(self, path):
        """
        :param path: Path of the public shared page
        """
        self._path = os.path.join(settings.get("path", "sharedmemory"), path)
        self._fd = os.open(self._path, os.O_CREAT | os.O_TRUNC | os.O_RDWR)
        assert os.write(self._fd, '\x00' * mmap.PAGESIZE) == mmap.PAGESIZE
        self._mmap = mmap.mmap(self._fd, mmap.PAGESIZE, mmap.MAP_SHARED, mmap.PROT_WRITE)
        self._offset = 0

    def get_new(self, name, _v_type):
        v_type = None
        s_type = None
        if _v_type is int:
            v_type = ctypes.c_int
            s_type = 'i'
        elif _v_type is bool:
            v_type = ctypes.c_bool
            s_type = '?'
        elif _v_type is float:
            v_type = ctypes.c_float
            s_type = 'f'
        else:
            raise SharedException("This type : {0} is not supported by SharedPage".format(_v_type))

        size = struct.calcsize(s_type)
        with open(self._path+".map", "a") as fd:    # Reference name and size of object
            fd.write("{name},{type},{size}|".format(name=name, size=size, type=s_type))
        var = v_type.from_buffer(self._mmap, self._offset)
        self._offset += size

        return var

    def __del__(self):
        self._mmap.close()
        os.close(self._fd)


class SharedPageReader:
    """
    This class represent a shared page in memory in order to read some datas
    """

    def __init__(self, path):
        """
        :param path: Path of the public shared page
        :return:
        """

        self._path = os.path.join(settings.get("path", "sharedmemory"), path)
        self._fd = os.open(self._path, os.O_RDONLY)
        self._mmap = mmap.mmap(self._fd, mmap.PAGESIZE, mmap.MAP_SHARED, mmap.PROT_READ)
        self.mapped = os.path.exists(self._path+".map")
        if self.mapped:
            self._update_map()

    def _update_map(self):
        self._map = dict()
        with open(self._path+".map", "r") as fd:
            content = fd.readline()
        log.log("info", "map content : {0}".format(content))
        var_list = content.split("|")
        log.log("info", "var list : {0}".format(var_list))
        offset = 0
        for var in var_list:
            try:
                name, s_type, size = var.split(",")
            except ValueError:
                break
            self._map[name] = (s_type, offset, offset+int(size))
            offset += int(size)

    def get_var_by_name(self, name):
        """
        This function try to get a variable by his name in the mmap
        :param name: name of the var
        :return:
        """
        if name not in self._map.keys():
            raise SharedException("This variable {0} is not defined in the shared page map".format(name))
        var = self._map[name]
        var, = struct.unpack(var[0], self._mmap[var[1]:var[2]])
        return var

    def __del__(self):
        self._mmap.close()
        os.close(self._fd)


class SharedVar:
    """
    This class define a simple shared var by a file
    """

    def __init__(self, name, s_type):
        """
        Name of the var, so the name of the file
        :param name:
        :return:
        """
        self._name = name
        self._path = os.path.join(settings.get("path", "sharedmemory"), "var_"+name)
        self.type = s_type

    @property
    def value(self):
        return self.get()

    @value.setter
    def value(self, value):
        log.log("raw", "Set Shared Var {0} to {1}".format(self._name, value))
        self.set(value)

    def get(self):
        log.log("raw", "Try to read Shared Var {0} at {1}".format(self._name, self._path))
        with open(self._path, "rb") as fd:
            v, = struct.unpack(self.type, fd.read())
            return v
        raise SharedException("Cannot read this value")

    def set(self, value):
        log.log("raw", "Try to set Shared Var {0} to {1} at {2}".format(self._name, value, self._path))
        with open(self._path, "wb+") as fd:
            log.log("raw", "Set Shared Var {0} to {1} at {2}".format(self._name, value, self._path))
            fd.write(struct.pack(self.type, value))
