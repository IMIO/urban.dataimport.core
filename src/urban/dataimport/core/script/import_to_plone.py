# -*- coding: utf-8 -*-
import sys

from progress.bar import FillingSquaresBar
from urban.dataimport.core import utils

import argparse
import configparser
import json
import time
import traceback
import requests

from urban.dataimport.core.http import post_query, search_query, delete_query, get_query
from urban.dataimport.core.json import DateTimeEncoder
from urban.dataimport.core.utils import BaseImport, benchmark_decorator, ErrorToCsv, export_error_csv

RESPONSE_SUCCESS = 200
RESPONSE_CREATED_SUCCESS = 201
NO_RESPONSE_SUCCESS = 204

DEFAULT_HEADER = {'Accept': 'application/json', 'Content-Type': "application/json;charset=utf-8"}
LOGIN_STRING = '{"login": "%s", "password": "%s"}'


class ImportToPlone(BaseImport):

    def __init__(self, config_file, group_licences=None, limit=None, licence_id=None, licence_type=None, benchmarking=False, noop=False, exit_on_error=False):
        self._log = []
        self._current_licence = ""
        self.licence_errors = []
        self.start_time = time.time()
        self.benchmarking = benchmarking
        self.noop = noop
        self.exit_on_error = exit_on_error
        if self.benchmarking:
            self._benchmark = {}
        config = configparser.ConfigParser()
        config_file = utils.format_path(config_file)
        config.read(config_file)
        self.config = config
        self.group_licences = group_licences
        self.limit = limit
        self.licence_id = licence_id
        self.licence_type = licence_type
        self.plone_site = ('{host}/{site}'.format(**config._sections['plone']))
        self.host = config._sections['plone']['host']
        response = requests.post(self.plone_site + '/@login',
                                 headers=DEFAULT_HEADER,
                                 data=LOGIN_STRING % (config._sections['plone']['user'],
                                                      config._sections['plone']['password']))
        if response.status_code == RESPONSE_SUCCESS:
            self.token = response.json()['token']
            self.head = {'Accept': 'application/json', 'Content-Type': 'application/json',
                         'Authorization': 'Bearer {}'.format(self.token)}
        self.nb_licence = 0
        self.licence_global_list = []

    def execute(self):

        with open(self.config['main']['input_path'], 'r') as input_file:
            data = json.load(input_file)

        try:
            if self.config['plone']['foldermanager']:
                self.foldermanager_uid = self.search_foldermanager(self.config['plone']['foldermanager'])
            bar = FillingSquaresBar('Importing licences', max=len(data))
            self.nb_licence = len(data)
            if self.limit:
                self.nb_licence = self.limit
            if self.group_licences:
                for i in range(0, self.nb_licence, self.group_licences):
                    group_list = data[i: i + self.group_licences]
                    self.import_licence(group_list)
                    for j in group_list:
                        bar.next()
            else:
                for licence in data:
                    self._current_licence = licence
                    if self.licence_type:
                        if licence['portalType'] == self.licence_type:
                            self.import_licence(licence)
                    else:
                        if self.licence_id:
                            if self.licence_id == licence['reference']:
                                self.import_licence([licence])
                        else:
                            self.import_licence(licence)
            bar.finish()
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            self.licence_errors.append(ErrorToCsv("licence_errors",
                                                  "Dossier non traité et en erreur",
                                                  self._current_licence['reference'],
                                                  str(exc_type)))
            print("Erreur: {} *** Licence: {} *** traceback: {}".format(e, group_list, traceback.print_tb(e.__traceback__)))
            if self.exit_on_error:
                export_error_csv([self.licence_errors])
                sys.exit(1)
            pass

        export_error_csv([self.licence_errors])

        if self._log:
            print("--- LOGS ---")
            print(json.dumps(self._log, indent=4, sort_keys=True, cls=DateTimeEncoder))
        print("--- Total Duration --- %s seconds ---" % (time.time() - self.start_time))
        if self.benchmarking:
            print(json.dumps(self._benchmark, indent=4, sort_keys=True, cls=DateTimeEncoder))

    def import_licence(self, licence):
        try:
            self.post_licences(licence)
        except Warning as warn:
            print("\nWarning: {} *** Licence: {}".format(warn, licence))
            self.licence_errors.append(ErrorToCsv("licence_errors",
                                                  "Dossier non traité et en erreur",
                                                  self._current_licence['reference'],
                                                  str(traceback.format_exc())))
            if self.exit_on_error:
                # raise Exception(warn)
                sys.exit(1)
            pass

    @benchmark_decorator
    def post_licences(self, licences):
        main_dict = {'__elements__': licences}
        imio_webservice_json_url = "{}/{}/{}".format(self.host,
                                                     self.config['plone']['site'],
                                                     self.config['plone']['endpoint'])
        response = post_query(url=imio_webservice_json_url, header=self.head, data=json.dumps(main_dict))
        if response.status_code != RESPONSE_CREATED_SUCCESS and response.status_code != RESPONSE_SUCCESS:
            raise Warning("Licence issue : not created :{} with response: {}".format(main_dict, response.text))
        json.loads(response.text)

    @benchmark_decorator
    def post_applicants(self, licence_url, licence):
        for applicant in licence['applicants']:
            # data = {key: val for key, val in applicant.items() if not isinstance(val, list)}
            response = post_query(url=licence_url, header=self.head, data=json.dumps(applicant))
            if response.status_code != RESPONSE_CREATED_SUCCESS:
                self.rollback_licence(licence_url, licence)
                raise Warning("Applicant issue : {} *** not created :{}".format(applicant, response.content))

    @benchmark_decorator
    def post_parcels(self, licence_url, licence):
        for parcel in licence['parcels']:
            if parcel['division'] and parcel['section'] and parcel['radical']:
                response = post_query(url=licence_url, header=self.head, data=json.dumps(parcel))
                if response.status_code != RESPONSE_CREATED_SUCCESS:
                    if "'field': 'division'" in str(response.content):
                        self._log.append({'object': "Problème de division",
                                          'division': parcel['division'],
                                          'id': parcel['id'],
                                          'reference': licence['reference']
                                          })
                    self.rollback_licence(licence_url, licence)
                    raise Warning("Parcel issue : {} *** not created :{}".format(parcel, response.content))

    @benchmark_decorator
    def post_events(self, licence_url, licence):
        urbanevents_folder = "{0}{1}".format(self.plone_site, "/portal_urban/buildlicence/urbaneventtypes/")
        for event in licence['events']:
            event['event_id'] = "{0}{1}".format(urbanevents_folder, event['type'])
            # data = {key: val for key, val in applicant.items() if not isinstance(val, list)}
            response = post_query(url=licence_url, header=self.head, data=json.dumps(event))
            if response.status_code != RESPONSE_CREATED_SUCCESS:
                self.rollback_licence(licence_url, licence)
                raise Warning("Event issue : {} *** not created :{}".format(event, response.content))

    def search_foldermanager(self, foldermanager):
        foldermanager_url = self.plone_site + '/portal_urban/foldermanagers/@search?fullobjects=1&SearchableText={}'.format(foldermanager)
        response = search_query(url=foldermanager_url, header=self.head)
        if response.status_code != RESPONSE_SUCCESS:
            raise ValueError("Search Foldermanager issue :{}".format(response.content))
        response_dict = json.loads(response.text)
        try:
            return response_dict['items'][0]['UID']
        except IndexError as e:
            print("Foldermanager: {}  not found *** Error: {}".format(foldermanager, e))

    def rollback_licence(self, licence_url, licence):
            response = delete_query(url=licence_url, header=self.head)
            if response.status_code != NO_RESPONSE_SUCCESS:
                print("ISSUE WITH ROLLBACK!!! Licence url : {} and Licence : {}".format(licence_url, licence))
                print("STOP THE PROCESS!")
                sys.exit(1)

    def licence_exists(self, licence):
        licence_url = self.plone_site + '/urban/buildlicences/{}/'.format(licence['id'])
        response = get_query(url=licence_url, header=self.head)
        return response.status_code == RESPONSE_SUCCESS


def main():
    """ """
    parser = argparse.ArgumentParser(description='Import data in Urban from json input')
    parser.add_argument('config_file', type=str, help='path to the config')
    parser.add_argument('--group_licences', type=int, help='request with multi-licences number')
    parser.add_argument('--limit', type=int, help='number of records')
    parser.add_argument('--licence_id', type=str, help='reference of a licence')
    parser.add_argument('--licence_type', type=str, help='type of licence')
    parser.add_argument('--benchmarking', type=bool, nargs='?',
                        const=True, default=False, help='add benchmark infos')
    parser.add_argument('--noop', type=bool, nargs='?',
                        const=True, default=False, help='only print result')
    parser.add_argument('--exit_on_error', type=bool, nargs='?',
                        const=True, default=False, help='exit process on error')
    args = parser.parse_args()

    ImportToPlone(
        args.config_file,
        group_licences=args.group_licences,
        limit=args.limit,
        licence_id=args.licence_id,
        licence_type=args.licence_type,
        benchmarking=args.benchmarking,
        noop=args.noop,
        exit_on_error=args.exit_on_error,
    ).execute()
