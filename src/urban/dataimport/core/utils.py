# -*- coding: utf-8 -*-

from jsonschema import validate
from numpy import unicode, basestring
from progress.bar import FillingSquaresBar
from random import shuffle
from urban.dataimport.core.json import DateTimeEncoder

import base64
import csv
import datetime
import glob
import json
import jsonschema
import ntpath
import os
import re
import time
import polib

import pandas as pd


def format_path(path):
    if os.path.exists(path):
        return path

    return os.path.join(os.getcwd(), path)


def represent_int(string):
    try:
        int(string)
        return True
    except ValueError:
        return False
    except TypeError:
        return False

def safe_unicode(value, encoding='utf-8'):
    """Converts a value to unicode, even it is already a unicode string.

        >>> safe_unicode('spam')
        u'spam'
        >>> safe_unicode(u'spam')
        u'spam'
        >>> safe_unicode(u'spam'.encode('utf-8'))
        u'spam'
        >>> safe_unicode('\xc6\xb5')
        u'\u01b5'
        >>> safe_unicode(u'\xc6\xb5'.encode('iso-8859-1'))
        u'\u01b5'
        >>> safe_unicode('\xc6\xb5', encoding='ascii')
        u'\u01b5'
        >>> safe_unicode(1)
        1
        >>> print safe_unicode(None)
        None
    """
    if isinstance(value, unicode):
        return value
    elif isinstance(value, basestring):
        try:
            value = unicode(value, encoding)
        except (UnicodeDecodeError):
            value = value.decode('utf-8', 'replace')
    return value

def parse_cadastral_reference(string):
    cadastral_regex = '\W*(?P<division>\d+)?\W*(?P<section>[A-Z])?\W*(?P<radical>\d+)?\W*/?\s*(?P<bis>\d+)?\W*' \
                      '(?P<exposant>[a-zA-Z])?\W*(?P<puissance>\d+)?\W*(?P<partie>pie)?.*'

    abbreviations = re.match(cadastral_regex, string)

    if abbreviations:
        return abbreviations.groups()


def export_to_customer_json(import_object):
    json_data = json.dumps([import_object.data])
    path = import_object.config['main']['output_customer_path']
    output_customer_licence_type_split = import_object.config['main']['output_customer_licence_type_split']
    creation_date = datetime.datetime.now().strftime("%Y%m%d")
    if output_customer_licence_type_split != 'True':
        translate_and_write(json_data, "{0}.{1}".format(path, "json"))
    else:
        licence_types = ["BuildLicence",
                         "ParcelOutLicence",
                         "EnvClassOne",
                         "EnvClassTwo",
                         "EnvClassThree",
                         "Article127",
                         "UniqueLicence",
                         "NotaryLetter",
                         "Declaration",
                         "Division",
                         "PreliminaryNotice",
                         "CODT_BuildLicence",
                         "CODT_UrbanCertificateTwo",
                         "CODT_ParcelOutLicence",
                         "UrbanCertificateTwo",
                         "UrbanCertificateOne",
                         "CODT_CommercialLicence",
                         "MiscDemand",
                         ]
        licences = pd.DataFrame(import_object.data)
        output_customer_licence_type_count = import_object.config['main']['output_customer_licence_type_count']
        random_selection = import_object.config['main']['output_customer_licence_type_random_selection']
        for licence_type in licence_types:
            filtered_licences = licences[licences.portalType == licence_type]
            json_data = filtered_licences.to_json(orient='records')
            if output_customer_licence_type_count.isdigit():
                if random_selection == 'True':
                    licence_list = json.loads(json_data)
                    shuffle(licence_list)
                    split_string = licence_list[:int(output_customer_licence_type_count)]
                else:
                    split_string = json.loads(json_data)[:int(output_customer_licence_type_count)]
                json_data = json.dumps(split_string)
            if json_data != '[]':
                translate_and_write(json_data, "{0}_{1}_{2}.{3}".format(path, licence_type, creation_date, "json"))


def translate_and_write(json_data, path):
    po = polib.pofile('customer_ouput_fr.po', encoding='utf-8')
    for entry in po:
        json_data = re.sub(r"\b{0}\b".format(entry.msgid), entry.msgstr, json_data)
    with open(path, 'w', encoding='utf8') as output_file:
        json.dump(json.loads(json_data), output_file, cls=DateTimeEncoder)


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


def export_error_csv(errors):
    print("WRITING ERRORS REPORTS")
    for error_list in errors:
        if len(error_list) > 0:
            csv_writer = csv.writer(open('{}_{}.csv'.format(error_list[0].filename, datetime.datetime.now().strftime("%Y%m%d_%H%M%S")), 'w'), delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            csv_writer.writerow(["Référence", "Valeur", "Description Erreur"])
            for error in error_list:
                csv_writer.writerow(error)
    print("ERRORS REPORTS WRITED")


def get_file_data_from_suffix_path(root_documents_path, suffix_path):
    file_path = os.path.dirname("{}{}".format(root_documents_path, suffix_path))
    file_suffix = ntpath.basename(suffix_path)
    byte_content = ''
    for match_file in glob.glob(os.path.join(file_path, "{}{}".format(file_suffix, ".*"))):
        byte_content = open(match_file, "rb").read()
        break

    if byte_content:
        base64_bytes = base64.b64encode(byte_content)
        return base64_bytes.decode("utf-8")


def get_filename_from_suffix_path(root_documents_path, suffix_path):
    file_path = os.path.dirname("{}{}".format(root_documents_path, suffix_path))
    file_suffix = ntpath.basename(suffix_path)
    for match_file in glob.glob(os.path.join(file_path, "{}{}".format(file_suffix, ".*"))):
        return ntpath.basename(match_file)


html_escape_table = {
    "&": "&amp;",
    '"': "&quot;",
    "'": "&apos;",
    ">": "&gt;",
    "<": "&lt;",
    }


def html_escape(text):
    """Produce entities within text."""
    return "".join(html_escape_table.get(c, c) for c in text)


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
        bar = FillingSquaresBar('Validating licences with : {}'.format(type), max=len(data))
        for licence in data:
            self.validate_schema(licence, type)
            bar.next()
        bar.finish()

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


class ErrorToCsv:

    def __init__(self, filename, error, reference, object):
        self.error = error
        self.reference = reference
        self.object = object
        self.filename = filename

    def __iter__(self):
        return iter([self.reference, self.object, self.error])
