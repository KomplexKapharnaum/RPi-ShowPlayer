# -*- coding: utf-8 -*-
#
#
# This file provide class and function to manage media on the Raspebrry Pi
#

import os
import shutil

from libs import pyhashxx
from engine.setting import settings

from engine.log import init_log
log = init_log("media")


class MediaMoved:
    """
    This class just represent the fact that the file as change his place
    """
    def __init__(self, old_path, new_path):
        self.old_path = old_path
        self.new_path = new_path


class MediaChanged:
    """
    This class just represent the fact that the file as change his place
    """
    def __init__(self, path, current_checksum, new_checksum):
        self.path = path
        self.current_checksum = current_checksum
        self.new_checksum = new_checksum


class MediaUnknown:
    """
    This class just represent the fact that the file isn't in the filesystem at all
    """
    def __init__(self, path, checksum):
        self.path = path
        self.current = checksum


def get_fs_checksum(path):
    """
    This function return the checksum of a file on the filesystem
    :param path: Path to the file
    :return:
    """
    with open(path, "rb") as ofile:
        return pyhashxx.hashxx(ofile.read())


def parse_media_dir():
    """
    This function parse the media directory to check current existing files
    :return:
    """
    tree = dict()
    for root, dirs, files in os.walk(settings.get("path", "media")):
        for f in files:
            tree[os.path.join(root, f)] = get_fs_checksum(os.path.join(root, f))
    return tree


def is_onfs(path, checksum, fs_tree):
    """
    This function search in the media directory if the media is in there
    :param path: Media path
    :param checksum: Checksum of the media
    :param fs_tree: filesystem tree return by parse_media_dir
    :return:
    """
    if path in fs_tree.keys():          # A file have the same name in the fs
        if fs_tree[path] == checksum:   # The file is the same
            return True
        else:                           # The file have changed
            return MediaChanged(path, fs_tree[path], checksum)
    elif checksum in fs_tree.values():
        for old_path, cs in fs_tree.items():
            if cs == checksum:
                return MediaMoved(old_path, path)   # Old path of the file
    else:
        return MediaUnknown(path, checksum)                    # The file is not present at all


def do_move_file(old_path, new_path, retry=False):
    """
    This function move a file from a path to another
    :param old_path:
    :param new_path:
    :param retry: If True, an erro will be fatal
    :return:
    """
    try:
        shutil.move(old_path, new_path)
        return True
    except Exception:
        if retry is not True:
            os.remove(new_path)
            return do_move_file(old_path, new_path)
        else:
            return False




