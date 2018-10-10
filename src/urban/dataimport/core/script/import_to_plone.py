# -*- coding: utf-8 -*-

from urban.dataimport.core import utils


import argparse
import configparser
import json
import time
import requests

from urban.dataimport.core.json import DateTimeEncoder
from urban.dataimport.core.utils import BaseImport

RESPONSE_SUCCESS = 200
RESPONSE_CREATED_SUCCESS = 201


class ImportToPlone(BaseImport):

    def __init__(self, config_file, limit=None, licence_id=None, licence_type=None, benchmarking=False, noop=False):
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
        self.licence_type = licence_type

        self.plone_site = ('{host}/{site}'.format(**config._sections['plone']))
        self.host = config._sections['plone']['host']
        response = requests.post(self.plone_site + '/@login',
                                 headers={'Accept': 'application/json',
                                          'Content-Type': "application/json;charset=utf-8"},
                                 data='{"login": "%s", "password": "%s"}' % (config._sections['plone']['user'],
                                                                             config._sections['plone']['password']))
        if response.status_code == RESPONSE_SUCCESS:
            self.token = response.json()['token']
            self.head = {'Accept': 'application/json', 'Content-Type': 'application/json',
                         'Authorization': 'Bearer {}'.format(self.token)}
        else:
            print(response.status_code)

    def execute(self):

        print("--- Total Duration --- %s seconds ---" % (time.time() - self.start_time))
        if self.benchmarking:
            print(json.dumps(self._benchmark, indent=4, sort_keys=True, cls=DateTimeEncoder))


def main():
    """ """
    parser = argparse.ArgumentParser(description='Consolidate data from json input')
    parser.add_argument('config_file', type=str, help='path to the config')
    parser.add_argument('--limit', type=int, help='number of records')
    parser.add_argument('--licence_id', type=str, help='reference of a licence')
    parser.add_argument('--licence_type', type=str, help='type of licence')
    parser.add_argument('--benchmarking', type=bool, nargs='?',
                        const=True, default=False, help='add benchmark infos')
    parser.add_argument('--noop', type=bool, nargs='?',
                        const=True, default=False, help='only print result')
    args = parser.parse_args()

    ImportToPlone(
        args.config_file,
        limit=args.limit,
        licence_id=args.licence_id,
        licence_type=args.licence_type,
        benchmarking=args.benchmarking,
        noop=args.noop,
    ).execute()
