# -*- coding: utf-8 -*-

from urban.dataimport.core import utils


import argparse
import configparser
import json
import time

from urban.dataimport.core.json import DateTimeEncoder
from urban.dataimport.core.utils import BaseImport


class ImportConsolidate(BaseImport):

    def __init__(self, config_file, limit=None, licence_id=None, ignore_cache=False, benchmarking=False, noop=False):
        self.start_time = time.time()
        self.benchmarking = benchmarking
        self.noop = noop
        if self.benchmarking:
            self._benchmark = {}
        config = configparser.ConfigParser()
        config_file = utils.format_path(config_file)
        config.read(config_file)
        self.config = config
        self.limit = limit
        self.licence_id = licence_id
        self.ignore_cache = ignore_cache

    def execute(self):

        with open(self.config['main']['input_path'], 'r') as input_file:
            data = json.load(input_file)
        self.validate_data(data, 'GenericLicence')

        for licence in data:
            self.consolidate_licence(licence)

        self.validate_data(data, 'GenericLicence_Consolidate')
        if self.noop:
            print(json.dumps(data, indent=4, sort_keys=True, cls=DateTimeEncoder))
        else:
            with open(self.config['main']['output_path'], 'w') as output_file:
                json.dump(data, output_file, cls=DateTimeEncoder)
        print("--- Total Duration --- %s seconds ---" % (time.time() - self.start_time))
        if self.benchmarking:
            print(json.dumps(self._benchmark, indent=4, sort_keys=True, cls=DateTimeEncoder))

    def consolidate_licence(self, licence):
        print(licence)


def main():
    """ """
    parser = argparse.ArgumentParser(description='Consolidate data from json input')
    parser.add_argument('config_file', type=str, help='path to the config')
    parser.add_argument('--limit', type=int, help='number of records')
    parser.add_argument('--licence_id', type=str, help='reference of a licence')
    parser.add_argument('--ignore_cache', type=bool, nargs='?',
                        const=True, default=False, help='ignore local cache')
    parser.add_argument('--benchmarking', type=bool, nargs='?',
                        const=True, default=False, help='add benchmark infos')
    parser.add_argument('--noop', type=bool, nargs='?',
                        const=True, default=False, help='only print result')
    args = parser.parse_args()

    ImportConsolidate(
        args.config_file,
        limit=args.limit,
        licence_id=args.licence_id,
        ignore_cache=args.ignore_cache,
        benchmarking=args.benchmarking,
        noop=args.noop,
    ).execute()
