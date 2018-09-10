# -*- coding: utf-8 -*-
import json
import os
import re
import time

import jsonschema
from jsonschema import validate


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


def benchmark_decorator(method):
    def replacement(self, *args, **kwargs):
        if not self.benchmarking:
            return method(self, *args, **kwargs)
        if not self._benchmark.get(method.__name__):
            self._benchmark[method.__name__] = {'counter': 0, 'elapsed_time': 0}
        self._benchmark[method.__name__]['counter'] += 1
        start_time = time.time()
        returned_value = method(self, *args, **kwargs)
        self._benchmark[method.__name__]['elapsed_time'] += time.time() - start_time
        self._benchmark[method.__name__]['average_time'] = \
            self._benchmark[method.__name__]['elapsed_time'] / self._benchmark[method.__name__]['counter']
        return returned_value

    return replacement


class BaseImport:

    @benchmark_decorator
    def validate_schema(self, data, type):
        base_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'schema')
        schema = json.load(open(os.path.join(base_path, "{0}.json".format(type))))
        resolver = jsonschema.RefResolver('file://%s/' % base_path, None)
        for licence in data:
            validate(licence, schema, resolver=resolver)
