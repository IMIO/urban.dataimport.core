# -*- coding: utf-8 -*-

from urban.dataimport.core import utils


import argparse
import configparser
import json
import time

from urban.dataimport.core.json import DateTimeEncoder
from urban.dataimport.core.utils import BaseImport


class ImportConsolidate(BaseImport):

    def __init__(self, config_file, limit=None, licence_id=None, ignore_cache=False, benchmarking=False):
        self.start_time = time.time()
        self.benchmarking = benchmarking
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

        data = []

        self.validate_schema(data, 'GenericLicence')
        print(json.dumps(data, indent=4, sort_keys=True, cls=DateTimeEncoder))
        print("--- Total Duration --- %s seconds ---" % (time.time() - self.start_time))
        if self.benchmarking:
            print(json.dumps(self._benchmark, indent=4, sort_keys=True))


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
    args = parser.parse_args()

    ImportConsolidate(
        args.config_file,
        limit=args.limit,
        licence_id=args.licence_id,
        ignore_cache=args.ignore_cache,
        benchmarking=args.benchmarking,
    ).execute()