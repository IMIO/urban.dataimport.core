# -*- coding: utf-8 -*-

import os


def format_path(path):
    if os.path.exists(path):
        return path

    return os.path.join(os.getcwd(), path)
