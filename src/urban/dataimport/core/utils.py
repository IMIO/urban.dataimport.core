# -*- coding: utf-8 -*-

import os
import re


def format_path(path):
    if os.path.exists(path):
        return path

    return os.path.join(os.getcwd(), path)


def parse_cadastral_reference(string):
    cadastral_regex = '\W*(?P<division>\d+)?\W*(?P<section>[A-Z])?\W*(?P<radical>\d+)?\W*/?\s*(?P<bis>\d+)?\W*' \
                      '(?P<exposant>[a-zA-Z])?\W*(?P<puissance>\d+)?\W*(?P<partie>pie)?.*'

    abbreviations = re.match(cadastral_regex, string)

    if abbreviations:
        return abbreviations.groups()
