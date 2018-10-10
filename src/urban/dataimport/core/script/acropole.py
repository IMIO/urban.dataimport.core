# -*- coding: utf-8 -*-
import re

from progress.bar import FillingSquaresBar
from sqlalchemy import create_engine
from urban.dataimport.core import utils
from urban.dataimport.core.db import LazyDB
from urban.dataimport.core.mapping.acropole_mapping import events_types, portal_type_mapping, \
    state_mapping, title_types, division_mapping, main_state_id_mapping, refused_main_label_mapping, \
    accepted_main_label_mapping, custom_state_label_mapping

import argparse
import configparser
import json
import time

from urban.dataimport.core.json import DateTimeEncoder, get_applicant_dict, get_event_dict, get_licence_dict, \
    get_parcel_dict, get_work_locations_dict
from urban.dataimport.core.utils import parse_cadastral_reference, benchmark_decorator, BaseImport,\
    export_to_customer_json
from urban.dataimport.core.utils import StateManager
from urban.dataimport.core.utils import StateHandler
from urban.dataimport.core.utils import IterationError
from urban.dataimport.core.views.acropole_views import create_views
from urban.dataimport.core.views.cadastral_views import create_cadastral_views
from urban.dataimport.core.views.bestaddress_views import create_bestaddress_views


class ImportAcropole(BaseImport):

    def __init__(self, config_file, limit=None, licence_id=None, ignore_cache=False, benchmarking=False, noop=False, iterate=False):
        self.start_time = time.time()
        self.benchmarking = benchmarking
        self.noop = noop
        self.iterate = iterate
        if self.benchmarking:
            self._benchmark = {}
        config = configparser.ConfigParser()
        config_file = utils.format_path(config_file)
        config.read(config_file)
        self.config = config
        self.limit = limit
        self.licence_id = licence_id
        self.search_old_parcels = config['main']['search_old_parcels']
        engine = create_engine('mysql://{user}:{password}@{host}:{port}'.format(**config._sections['database']))
        connection = engine.connect()
        self.db = LazyDB(
            connection,
            config['database']['schema'],
            ignore_cache=ignore_cache,
        )
        engine_cadastral = create_engine('postgresql://{user}:{password}@{host}:{port}'.format(
            **config._sections['cadastral_database']))
        connection_cadastral = engine_cadastral.connect()
        self.cadastral = LazyDB(
            connection_cadastral,
            config['cadastral_database']['schema'],
            ignore_cache=ignore_cache,
        )
        engine_bestaddress = create_engine('postgresql://{user}:{password}@{host}:{port}'.format(
            **config._sections['bestaddress_database']))
        connection_bestaddress = engine_bestaddress.connect()
        self.bestaddress = LazyDB(
            connection_bestaddress,
            config['bestaddress_database']['schema'],
            ignore_cache=ignore_cache,
        )
        create_views(self)
        create_cadastral_views(self)
        create_bestaddress_views(self, config['main']['locality'])

    def execute(self):
        self.data = []

        error = None
        try:
            self.extract_data()
        except Exception as e:
            error = e

        if self.noop:
            print(json.dumps(self.data, indent=4, sort_keys=True, cls=DateTimeEncoder))
        if not self.noop and error is None:
            with open("{0}.{1}".format(self.config['main']['output_path'], "json"), 'w') as output_file:
                json.dump(self.data, output_file, cls=DateTimeEncoder)
            export_to_customer_json(self)
        print("-- {0} folders extracted --".format(len(self.data)))
        print("--- Total Duration --- %s seconds ---" % (time.time() - self.start_time))
        if self.benchmarking:
            print(json.dumps(self._benchmark, indent=4, sort_keys=True))
        if error:
            raise error

    @StateManager
    def extract_data(self):
        folders = self.db.wrkdossier
        if self.limit:
            folders = folders.head(self.limit)
        if self.licence_id:
            folders = folders[folders.DOSSIER_NUMERO == self.licence_id]

        bar = FillingSquaresBar('Processing licences', max=folders.shape[0])
        for id, licence in folders.iterrows():
            self.get_licence(id, licence)
            bar.next()
        bar.finish()
        if self.iterate is True:
            try:
                self.validate_data(self.data, 'GenericLicence')
            except Exception:
                raise IterationError('Schema change during iterative process')

    @StateHandler('data', 'acropole_get_licence')
    def get_licence(self, id, licence):
        self.licence_description = []
        licence_dict = get_licence_dict()
        licence_dict['id'] = str(licence.WRKDOSSIER_ID)
        licence_dict['portalType'] = self.get_portal_type(licence)  # licence type must be the first licence set
        if not licence_dict['portalType']:
            return
        # licence completionState must be the second licence set
        licence_dict['completionState'] = state_mapping.get(licence.DOSSIER_OCTROI)
        licence_dict['investigationStart'] = self.get_inquiry_values(licence, 'investigationStart')
        licence_dict['investigationEnd'] = self.get_inquiry_values(licence, 'investigationEnd')
        licence_dict['investigationReasons'] = self.get_inquiry_values(licence, 'investigationReasons')
        licence_dict['reference'] = licence.DOSSIER_NUMERO
        licence_dict['referenceDGATLP'] = licence.DOSSIER_REFURB and licence.DOSSIER_REFURB or ''
        licence_dict['licenceSubject'] = self.get_subject_licence(licence)
        licence_dict['workLocations'] = self.get_work_locations(licence)
        licence_dict['applicants'] = self.get_applicants(licence)
        licence_dict['parcels'] = self.get_parcels(licence)
        licence_dict['events'] = self.get_events(licence)
        licence_dict['description'] = self.licence_description  # description must be the last licence set
        self.validate_schema(licence_dict, 'GenericLicence')
        return licence_dict

    @benchmark_decorator
    def get_portal_type(self, licence):
        portal_type = portal_type_mapping.get(licence.DOSSIER_TDOSSIERID, None)
        if portal_type == 'UrbanCertificateOne' and licence.DOSSIER_TYPEIDENT == 'CU2':
            portal_type = 'UrbanCertificateTwo'
        return portal_type

    @benchmark_decorator
    def get_subject_licence(self, licence):
        subject_licence = self.db.dossier_infos_vue[
            (self.db.dossier_infos_vue.WRKDOSSIER_ID == licence.WRKDOSSIER_ID)]
        return subject_licence.iloc[0]['OBJET_KEY']

    @benchmark_decorator
    def get_inquiry_values(self, licence, field):
        inquiry = self.db.dossier_enquete
        if field == 'investigationReasons':
            inquiry_value = inquiry[
                (inquiry.WRKDOSSIER_ID == licence.WRKDOSSIER_ID) &
                (inquiry.PARAM_IDENT == 'EnqObjet')
            ]
            if inquiry_value.REMARQ_LIB.shape[0] == 1:
                return inquiry_value.iloc[0]['REMARQ_LIB']
        elif field == 'investigationStart':
            inquiry_value = inquiry[
                (inquiry.WRKDOSSIER_ID == licence.WRKDOSSIER_ID) &
                (inquiry.PARAM_IDENT == 'EnqDatDeb')
            ]
            if inquiry_value.PARAM_VALUE.shape[0] == 1:
                return inquiry_value.iloc[0]['PARAM_VALUE']
        elif field == 'investigationEnd':
            inquiry_value = inquiry[
                (inquiry.WRKDOSSIER_ID == licence.WRKDOSSIER_ID) &
                (inquiry.PARAM_IDENT == 'EnqDatFin')
            ]
            if inquiry_value.PARAM_VALUE.shape[0] == 1:
                return inquiry_value.iloc[0]['PARAM_VALUE']

    @benchmark_decorator
    def get_work_locations(self, licence):
        work_locations_list = []

        work_locations = self.db.dossier_adresse_vue[
            (self.db.dossier_adresse_vue.WRKDOSSIER_ID == licence.WRKDOSSIER_ID)]

        for id, work_location in work_locations.iterrows():
            work_locations_dict = get_work_locations_dict()

            if work_location.ADR_ADRESSE:
                # remove parentheses and its content
                acropole_street = re.sub(r'\([^)]*\)', '', work_location.ADR_ADRESSE).strip()

                bestaddress_streets = self.bestaddress.bestaddress_vue[
                    (self.bestaddress.bestaddress_vue.street == acropole_street)
                ]
                if bestaddress_streets.shape[0] == 0:
                    # second chance without street number
                    acropole_street_without_digits = ''.join([letter for letter in acropole_street if not letter.isdigit()]).strip()
                    bestaddress_streets = self.bestaddress.bestaddress_vue[
                        (self.bestaddress.bestaddress_vue.street == acropole_street_without_digits)
                    ]
                    if bestaddress_streets.shape[0] == 0:
                        # last chance : try to remove last char, for example : 1a or 36C
                        acropole_street_without_last_char = acropole_street_without_digits.strip()[:-1]
                        bestaddress_streets = self.bestaddress.bestaddress_vue[
                            (self.bestaddress.bestaddress_vue.street == acropole_street_without_last_char.strip())
                        ]
                        if bestaddress_streets.shape[0] == 0:
                            self.licence_description.append({'object': "Pas de résultat pour cette rue",
                                                             'street': work_location.ADR_ADRESSE,
                                                             'number': work_location.ADR_NUM,
                                                             'zipcode': work_location.ADR_ZIP,
                                                             'entity': work_location.ADR_LOCALITE
                                                             })
                            pass

                result_count = bestaddress_streets.shape[0]
                if result_count == 1:
                    work_locations_dict['street'] = bestaddress_streets.iloc[0]['street']
                    work_locations_dict['number'] = str(work_location.ADR_NUM)
                    work_locations_dict['zipcode'] = bestaddress_streets.iloc[0]['zip']
                    work_locations_dict['entity'] = bestaddress_streets.iloc[0]['entity']
                elif result_count > 1:
                    self.licence_description.append({'object': "Plus d'un seul résultat pour cette rue",
                                                     'street': work_location.ADR_ADRESSE,
                                                     'number': work_location.ADR_NUM,
                                                     'zipcode': work_location.ADR_ZIP,
                                                     'entity': work_location.ADR_LOCALITE
                                                     })

            work_locations_list.append(work_locations_dict)

        return work_locations_list

    @benchmark_decorator
    def get_applicants(self, licence):
        applicant_list = []
        applicants = self.db.dossier_personne_vue[
            (self.db.dossier_personne_vue.WRKDOSSIER_ID == licence.WRKDOSSIER_ID) &
            (self.db.dossier_personne_vue.K2KND_ID == -204)]
        for id, applicant in applicants.iterrows():
            applicant_dict = get_applicant_dict()
            applicant_dict['personTitle'] = title_types.get(applicant.CPSN_TYPE, None)
            applicant_dict['name1'] = applicant.CPSN_NOM
            applicant_dict['name2'] = applicant.CPSN_PRENOM
            applicant_dict['email'] = applicant.CPSN_EMAIL
            applicant_dict['phone'] = applicant.CPSN_TEL1
            applicant_dict['gsm'] = applicant.CPSN_GSM
            applicant_dict['fax'] = applicant.CPSN_FAX
            applicant_dict['street'] = applicant.CLOC_ADRESSE
            applicant_dict['zipcode'] = applicant.CLOC_ZIP
            applicant_dict['city'] = applicant.CLOC_LOCALITE
            applicant_list.append(applicant_dict)

        return applicant_list

    @benchmark_decorator
    def get_parcels(self, licence):
        parcels_list = []
        parcels = self.db.dossier_parcelles_vue[
            (self.db.dossier_parcelles_vue.WRKDOSSIER_ID == licence.WRKDOSSIER_ID)]
        for id, parcels in parcels.iterrows():
            parcels_dict = get_parcel_dict()
            parcels_dict['complete_name'] = parcels.CAD_NOM
            parcels_args = parse_cadastral_reference(parcels.CAD_NOM)
            if parcels_args[0] and parcels_args[1] and parcels_args[2]:
                division = division_mapping.get(parcels_args[0], None)
                parcelles_cadastrales = self.cadastral.parcelles_cadastrales_vue
                cadastral_parcels = parcelles_cadastrales[
                    (parcelles_cadastrales.division == division) &
                    (parcelles_cadastrales.section == parcels_args[1]) &
                    (parcelles_cadastrales.radical == parcels_args[2]) &
                    (parcelles_cadastrales.bis == (parcels_args[3] and
                                                   parcels_args[3] or '0')) &
                    (parcelles_cadastrales.exposant == parcels_args[4]) &
                    (parcelles_cadastrales.puissance == (parcels_args[5] and
                                                         parcels_args[5] or '0'))
                ]

                result_count = cadastral_parcels.shape[0]
                if result_count == 1:
                    parcels_dict['old_parcel'] = 'False'
                    parcels_dict['division'] = cadastral_parcels.iloc[0]['division']
                    parcels_dict['section'] = cadastral_parcels.iloc[0]['section']
                    parcels_dict['radical'] = cadastral_parcels.iloc[0]['radical']
                    parcels_dict['bis'] = cadastral_parcels.iloc[0]['bis']
                    parcels_dict['exposant'] = cadastral_parcels.iloc[0]['exposant']
                    parcels_dict['puissance'] = cadastral_parcels.iloc[0]['puissance']
                elif result_count > 1:
                    self.licence_description.append({'object': "Trop de résultats pour cette parcelle",
                                                     'old': 'False',
                                                     'parcel': parcels.CAD_NOM,
                                                     })
                else:
                    if self.search_old_parcels:
                        # Looking for old parcels
                        vieilles_parcelles_cadastrales = self.cadastral.vieilles_parcelles_cadastrales_vue
                        old_cadastral_parcels = vieilles_parcelles_cadastrales[
                            (vieilles_parcelles_cadastrales.division == division) &
                            (vieilles_parcelles_cadastrales.section == parcels_args[1]) &
                            (vieilles_parcelles_cadastrales.radical == parcels_args[2]) &
                            (vieilles_parcelles_cadastrales.bis == (parcels_args[3] and
                                                                    parcels_args[3] or '0')) &
                            (vieilles_parcelles_cadastrales.exposant == parcels_args[4]) &
                            (vieilles_parcelles_cadastrales.puissance == (parcels_args[5] and
                                                                          parcels_args[5] or '0'))
                            ]
                        old_result_count = old_cadastral_parcels.shape[0]
                        if old_result_count == 1:
                            parcels_dict['old_parcel'] = 'True'
                            parcels_dict['division'] = old_cadastral_parcels.iloc[0]['division']
                            parcels_dict['section'] = old_cadastral_parcels.iloc[0]['section']
                            parcels_dict['radical'] = str(old_cadastral_parcels.iloc[0]['radical'])
                            parcels_dict['bis'] = old_cadastral_parcels.iloc[0]['bis']
                            parcels_dict['exposant'] = old_cadastral_parcels.iloc[0]['exposant']
                            parcels_dict['puissance'] = old_cadastral_parcels.iloc[0]['puissance']
                        elif old_result_count > 1:
                            self.licence_description.append({'object': "Trop de résultats pour cette parcelle",
                                                             'old': 'True',
                                                             'parcel': parcels.CAD_NOM,
                                                             })
                        else:
                            pass

            parcels_list.append(parcels_dict)

        return parcels_list

    @benchmark_decorator
    def get_events(self, licence):
        event_list = []
        events = self.db.dossier_evenement_vue
        for key, values in events_types.items():
            events_etape = events[
                (events.ETAPE_TETAPEID.isin(values['etape_ids'])) &
                (events.WRKDOSSIER_ID == licence.WRKDOSSIER_ID)]
            events_param = None
            method = getattr(self, 'get_{0}_event'.format(key))
            result_list = method(licence, events_etape, events_param)
            if result_list:
                event_list.extend(result_list)

        return event_list

    def get_recepisse_event(self, licence, events_etape, events_param):
        events_dict = []
        for id, event in events_etape.iterrows():
            event_dict = get_event_dict()
            event_dict['type'] = 'recepisse'
            event_dict['eventDate'] = event.ETAPE_DATEDEPART
            events_dict.append(event_dict)
        return events_dict

    def get_completefolder_event(self, licence, events_etape, events_param):
        events_dict = []
        for id, event in events_etape.iterrows():
            event_dict = get_event_dict()
            event_dict['type'] = 'completefolder'
            event_dict['eventDate'] = event.ETAPE_DATEDEPART
            events_dict.append(event_dict)
        return events_dict

    def get_incompletefolder_event(self, licence, events_etape, events_param):
        events_dict = []
        for id, event in events_etape.iterrows():
            event_dict = get_event_dict()
            event_dict['type'] = 'incompletefolder'
            event_dict['eventDate'] = event.ETAPE_DATEDEPART
            events_dict.append(event_dict)
        return events_dict

    def get_sendtofd_event(self, licence, events_etape, events_param):
        events_dict = []
        for id, event in events_etape.iterrows():
            event_dict = get_event_dict()
            event_dict['type'] = 'sendtofd'
            event_dict['eventDate'] = event.ETAPE_DATEDEPART
            events_dict.append(event_dict)
        return events_dict

    def get_sendtoapplicant_event(self, licence, events_etape, events_param):
        events_dict = []
        for id, event in events_etape.iterrows():
            event_dict = get_event_dict()
            event_dict['type'] = 'sendtoapplicant'
            event_dict['eventDate'] = event.ETAPE_DATEDEPART
            events_dict.append(event_dict)
        return events_dict

    def get_decision_event(self, licence, events_etape, events_param):
        events_dict = []
        event_dict = get_event_dict()
        event_dict['type'] = 'decision'
        event_dict['eventDate'] = str(licence.DOSSIER_DATEDELIV)
        if str(licence.DOSSIER_OCTROI) == 'nan':
            self.licence_description.append({'Intitulé de décision': 'indéterminé / NaN'})
        else:
            state = int(licence.DOSSIER_OCTROI)
            decision_label = "NON CONNU"
            if state in main_state_id_mapping:
                portal_type = self.get_portal_type(licence)
                if state == 0:  # refusé
                    decision_label = refused_main_label_mapping.get(portal_type)
                elif state == 1:  # accepté
                    decision_label = accepted_main_label_mapping.get(portal_type)
                self.licence_description.append({'Intitulé de décision': decision_label})
            else:
                decision_label = custom_state_label_mapping.get(str(state))
                self.licence_description.append({'Intitulé de décision': decision_label})
            event_dict['decision_label'] = decision_label
            event_dict['decision'] = state_mapping.get(licence.DOSSIER_OCTROI)
            if events_etape.shape[0] > 1:
                raise ValueError('Too many decision events')
            elif events_etape.shape[0] == 1:
                event = events_etape.iloc[0]
                event_dict['decisionDate'] = event.ETAPE_DATEDEPART
                # if eventDate don't exist, decisionDate is used
                if not event_dict['eventDate'] or event_dict['eventDate'] == 'NaT':
                    event_dict['decisionDate'] = event.ETAPE_DATEDEPART
        events_dict.append(event_dict)
        return events_dict


def main():
    """ """
    parser = argparse.ArgumentParser(description='Import data from Acropole Database')
    parser.add_argument('config_file', type=str, help='path to the config')
    parser.add_argument('--limit', type=int, help='number of records')
    parser.add_argument('--licence_id', type=str, help='reference of a licence')
    parser.add_argument('--ignore_cache', type=bool, nargs='?',
                        const=True, default=False, help='ignore local cache')
    parser.add_argument('--benchmarking', type=bool, nargs='?',
                        const=True, default=False, help='add benchmark infos')
    parser.add_argument('--noop', type=bool, nargs='?',
                        const=True, default=False, help='only print result')
    parser.add_argument('--iterate', type=bool, nargs='?',
                        const=True, default=False, help='Use a special cache to iterate')
    args = parser.parse_args()

    ImportAcropole(
        args.config_file,
        limit=args.limit,
        licence_id=args.licence_id,
        ignore_cache=args.ignore_cache,
        benchmarking=args.benchmarking,
        noop=args.noop,
        iterate=args.iterate
    ).execute()
