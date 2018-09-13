# -*- coding: utf-8 -*-

from jsonschema import validate
from urban.dataimport.core.json import DateTimeEncoder

import json
import jsonschema
import os
import re
import time


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


class IterationError(Exception):
    pass


class StateManager:

    def __init__(self, method):
        self.method = method
        self.decorator = self.__class__

    def __call__(self, *args, **kwargs):
        error = None
        try:
            result = self.method(self.instance, *args, **kwargs)
        except IterationError as e:
            error = e
        if getattr(self.instance, '_state_files', None):
            for fname, f in self.instance._state_files.items():
                f.close()
                os.remove(fname)
        if error:
            raise error
        return result

    def __get__(self, instance, cls):
        self.cls = cls
        self.instance = instance
        return self.__call__


class StateHandler:

    def __init__(self, data_attribute, cache_key):
        self.data_attribute = data_attribute
        self.cache_key = cache_key
        self.iteration = 0

    def __call__(dc, method):
        def replacement(self, *args, **kwargs):
            data = getattr(self, dc.data_attribute, [])
            if getattr(self, 'iterate', False) is False:
                if not data:
                    dc.verify_state_file()
                data.append(method(self, *args, **kwargs))
            if not data:
                dc.try_recover_state_data(self)
            if dc.iteration < len(data):
                dc.iteration += 1
                return
            result = method(self, *args, **kwargs)
            state_file = dc.get_state_file(self)
            state_file.write('{0}\n'.format(
                json.dumps(result, cls=DateTimeEncoder)
            ))
            dc.iteration += 1
            data.append(result)
        return replacement

    @property
    def state_filename(self):
        if not hasattr(self, '_state_filename'):
            self._state_filename = '.state_{0}'.format(self.cache_key)
        return self._state_filename

    def try_recover_state_data(self, instance):
        if os.path.exists(self.state_filename):
            with open(self.state_filename, 'r') as f:
                data = getattr(instance, self.data_attribute)
                for line in f.readlines():
                    data.append(json.loads(line))
                print("-- recover {0} folders from previous state --".format(len(data)))

    def verify_state_file(self):
        """Remove the state file if it exist"""
        if os.path.exists(self.state_filename):
            os.remove(self.state_filename)

    def get_state_file(self, instance):
        if not hasattr(instance, '_state_files'):
            instance._state_files = {}
        if self.state_filename not in instance._state_files:
            instance._state_files[self.state_filename] = open(self.state_filename, 'a')
        return instance._state_files[self.state_filename]


class BaseImport:

    @benchmark_decorator
    def validate_data(self, data, type):
        for licence in data:
            self.validate_schema(licence, type)

    @benchmark_decorator
    def validate_schema(self, data, type):
        if not hasattr(self, '_validation_schema'):
            base_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                'schema',
            )
            self._validation_schema = json.load(
                open(os.path.join(base_path, "{0}.json".format(type)))
            )
            self._validation_resolver = jsonschema.RefResolver(
                'file://%s/' % base_path,
                None,
            )
        validate(
            data,
            self._validation_schema,
            resolver=self._validation_resolver,
        )
