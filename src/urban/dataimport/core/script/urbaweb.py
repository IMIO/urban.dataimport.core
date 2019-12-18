# -*- coding: utf-8 -*-
import re

from progress.bar import FillingSquaresBar
from urban.dataimport.core import utils
from sqlalchemy import create_engine

import argparse
import configparser
import json
import time

from urban.dataimport.core.db import LazyDB
from urban.dataimport.core.json import get_licence_dict, get_work_locations_dict, DateTimeEncoder, get_applicant_dict, \
    get_organization_dict, get_parcel_dict, get_event_dict
from urban.dataimport.core.mapping.acropole_mapping import state_mapping, decision_vocabulary_mapping, \
    custom_state_label_mapping, refused_main_label_mapping, accepted_main_label_mapping, main_state_id_mapping, \
    events_types
from urban.dataimport.core.mapping.urbaweb_mapping import division_mapping
from urban.dataimport.core.mapping.urbaweb_mapping import portal_type_mapping
from urban.dataimport.core.utils import BaseImport, StateManager, StateHandler, benchmark_decorator, \
    export_to_customer_json, represent_int, IterationError
from urban.dataimport.core.views.bestaddress_views import create_bestaddress_views
from urban.dataimport.core.views.cadastral_views import create_cadastral_views
from urban.dataimport.core.views.urbaweb_views import create_views, create_concat_views


class ImportUrbaweb(BaseImport):

    def __init__(self, config_file, view, limit=None, range=None, licence_id=None, ignore_cache=False, benchmarking=False, noop=False, iterate=False):
        print("INITIALIZING")
        self.view = view
        self.limit = limit
        self.range = range
        self.licence_id = licence_id
        self.start_time = time.time()
        self.benchmarking = benchmarking
        self.noop = noop
        self.iterate = iterate
        config = configparser.ConfigParser()
        config_file = utils.format_path(config_file)
        config.read(config_file)
        self.config = config
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
            ignore_cache=False,
        )
        engine_bestaddress = create_engine('postgresql://{user}:{password}@{host}:{port}'.format(
            **config._sections['bestaddress_database']))
        connection_bestaddress = engine_bestaddress.connect()
        self.bestaddress = LazyDB(
            connection_bestaddress,
            config['bestaddress_database']['schema'],
            ignore_cache=False,
        )
        create_concat_views(self)
        create_views(self)
        create_cadastral_views(self)
        create_bestaddress_views(self, config['main']['locality'])
        print("INITIALIZATION COMPLETED")

    def execute(self):
        self.data = []
        error = None
        try:
            self.extract_data()
        except Exception as e:
            error = e

        if error:
            raise error

        if not self.noop and error is None:
            with open("{0}.{1}".format(self.config['main']['output_path'], "json"), 'w') as output_file:
                json.dump(self.data, output_file, cls=DateTimeEncoder)
            export_to_customer_json(self)
        print("-- {0} folders extracted --".format(len(self.data)))
        print("--- Total Duration --- %s seconds ---" % (time.time() - self.start_time))

    @StateManager
    def extract_data(self):
        folders = getattr(self.db, self.view)
        if self.range:
            folders = folders[int(self.range.split(':')[0]):int(self.range.split(':')[1])]
        if self.limit:
            folders = folders.head(self.limit)
        if self.licence_id:
            folders = folders[folders.reference == self.licence_id]

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

    @StateHandler('data', 'urbaweb_get_licence')
    def get_licence(self, id, licence):
        self.licence_description = []
        licence_dict = get_licence_dict()
        # licence_dict['id'] = str(licence.WRKDOSSIER_ID)
        licence_dict['portalType'] = self.get_portal_type(licence)  # licence type must be the first licence set
        if not licence_dict['portalType']:
            return
        licence_dict["@type"] = licence_dict["portalType"]
        # # licence completionState must be the second licence set
        # licence_dict['review_state'] = state_mapping.get(licence.DOSSIER_OCTROI)
        # licence_dict['investigationStart'] = self.get_inquiry_values(licence, 'investigationStart')
        # licence_dict['investigationEnd'] = self.get_inquiry_values(licence, 'investigationEnd')
        # investigation_reasons = self.get_inquiry_values(licence, 'investigationReasons')
        # if investigation_reasons:
        #     licence_dict['investigationReasons'] = [investigation_reasons]
        licence_dict['reference'] = "{}/{}".format(licence.id, licence.REFERENCE)
        # print(' ***{}***'.format(licence_dict['reference']))
        # licence_dict['referenceDGATLP'] = licence.DOSSIER_REFURB and licence.DOSSIER_REFURB or ''
        licence_dict['licenceSubject'] = licence.NATURE_TITRE
        licence_dict['usage'] = 'not_applicable'
        licence_dict['workLocations'] = self.get_work_locations(licence)
        # licence_dict['architects'] = self.get_organisation(licence, 'architect')
        self.get_organization(licence, licence_dict)
        # licence_dict['notaries'] = self.get_organisation(licence, 'notary')
        self.get_applicants(licence, licence_dict['__children__'])
        self.get_parcels(licence, licence_dict['__children__'])
        # self.get_events(licence, licence_dict['__children__'])
        description = str(''.join(str(d) for d in self.licence_description))
        licence_dict['description'] = {
            'data': "{}{} - {} {}{}".format("<p>", description, licence.NATURE_DETAILS, licence.REMARQUES, "</p>"),
            'content-type': 'text/html'
        }  # description must be the last licence set
        # self.validate_schema(licence_dict, 'GenericLicence')
        # request_dict = get_request_dict()
        # request_dict['parameters'] = licence_dict
        request_dict = licence_dict

        return request_dict

    @benchmark_decorator
    def get_portal_type(self, licence):
        portal_type = portal_type_mapping.get(licence.type_permis_fk, None)
        if portal_type == 'EnvClassOne' and licence.CLASSE == 2:
            portal_type = 'EnvClassTwo'
        return portal_type

    @benchmark_decorator
    def get_work_locations(self, licence):
        work_locations_list = []

        work_locations_dict = get_work_locations_dict()
        if licence.LOCALITE_RUE:
            # remove parentheses and its content
            urbaweb_street = re.sub(r'\([^)]*\)', '', licence.LOCALITE_RUE).strip()
            bestaddress_streets = self.bestaddress.bestaddress_vue[
                (self.bestaddress.bestaddress_vue.street == urbaweb_street)
            ]
            if bestaddress_streets.shape[0] == 0:
                # second chance without street number
                urbaweb_street_without_digits = ''.join([letter for letter in urbaweb_street if not letter.isdigit()]).strip()
                bestaddress_streets = self.bestaddress.bestaddress_vue[
                    (self.bestaddress.bestaddress_vue.street == urbaweb_street_without_digits)
                ]
                if bestaddress_streets.shape[0] == 0:
                    # last chance : try to remove last char, for example : 1a or 36C
                    urbaweb_street_without_last_char = urbaweb_street_without_digits.strip()[:-1]
                    bestaddress_streets = self.bestaddress.bestaddress_vue[
                        (self.bestaddress.bestaddress_vue.street == urbaweb_street_without_last_char.strip())
                    ]
                    if bestaddress_streets.shape[0] == 0:
                        self.licence_description.append({'object': "Pas de résultat pour cette rue",
                                                         'street': licence.LOCALITE_RUE,
                                                         'number': licence.LOCALITE_NUM,
                                                         'zipcode': licence.LOCALITE_CP,
                                                         'entity': licence.LOCALITE_LABEL
                                                         })
                        pass

            result_count = bestaddress_streets.shape[0]
            if result_count == 1:
                work_locations_dict['street'] = bestaddress_streets.iloc[0]['street']
                work_locations_dict['street_ins'] = str(bestaddress_streets.iloc[0]['key'])
                work_locations_dict['number'] = licence.LOCALITE_NUM
                work_locations_dict['zipcode'] = bestaddress_streets.iloc[0]['zip']

                work_locations_dict['entity'] = bestaddress_streets.iloc[0]['entity']
            elif result_count > 1:
                self.licence_description.append({'object': "Plus d'un seul résultat pour cette rue",
                                                 'street': licence.LOCALITE_RUE,
                                                 'number': licence.LOCALITE_NUM,
                                                 'zipcode': licence.LOCALITE_CP,
                                                 'entity': licence.LOCALITE_LABEL
                                                 })

        work_locations_list.append(work_locations_dict)

        return work_locations_list

    @benchmark_decorator
    def get_applicants(self, licence, licence_children):
        applicant_dict = get_applicant_dict()
        applicants = licence.INFOS_DEMANDEURS
        try:
            for applicant_infos in applicants.split("#"):
                applicant = applicant_infos.split("|")
                applicant_dict['personTitle'] = ""  # TODO mapping civilite / urban title
                applicant_dict['name1'] = applicant[1]
                applicant_dict['name2'] = applicant[2]
                applicant_dict['number'] = applicant[3]
                applicant_dict['street'] = applicant[4]
                applicant_dict['city'] = applicant[5]
                applicant_dict['phone'] = applicant[6]
                applicant_dict['gsm'] = applicant[7]
                applicant_dict['email'] = applicant[8]

                licence_children.append(applicant_dict)
        except:
            print("debug applicant")

    @benchmark_decorator
    def get_parcels(self, licence, licence_children):
        parcels = licence.INFOS_PARCELLES
        if parcels:
            try:
                for parcel in parcels.split("@"):
                    parcels_dict = get_parcel_dict()
                    parcels_dict['complete_name'] = parcel
                    parcels_args = parcel.split("|")
                    division_num = parcels_args[0]
                    section = parcels_args[1]
                    radical_bis_exp_puissance = parcels_args[2]

                    if division_num and section and radical_bis_exp_puissance:
                        # capakey without division and section is 11 character long.
                        if len(radical_bis_exp_puissance) == 11:
                            radical = radical_bis_exp_puissance[0:4]
                            bis = radical_bis_exp_puissance[5:7]
                            exposant = radical_bis_exp_puissance[7:8]
                            exposant = '' if exposant == '#' else exposant
                            puissance = radical_bis_exp_puissance[8:11]
                            if represent_int(puissance) and int(puissance) < 100:
                                if represent_int(radical) and represent_int(bis) and represent_int(puissance):
                                    try:
                                        division = division_mapping.get('{0:02d}'.format(int(division_num)), None)
                                        parcelles_cadastrales = self.cadastral.cadastre_parcelles_vue
                                        cadastral_parcels = parcelles_cadastrales[
                                            (parcelles_cadastrales.division == int(division)) &
                                            (parcelles_cadastrales.section == section) &
                                            (parcelles_cadastrales.radical == int(radical)) &
                                            ((parcelles_cadastrales.bis.isnull()) if not int(bis)
                                             else parcelles_cadastrales.bis == int(bis)) &
                                            ((parcelles_cadastrales.exposant.isnull()) if not exposant
                                             else parcelles_cadastrales.exposant == exposant) &
                                            ((parcelles_cadastrales.puissance.isnull()) if not int(puissance)
                                             else parcelles_cadastrales.puissance == puissance)
                                            ]
                                    except Exception as e:
                                        print("debug")

                                    result_count = cadastral_parcels.shape[0]
                                    if result_count == 1:
                                        parcels_dict['outdated'] = 'False'
                                        parcels_dict['is_official'] = 'True'
                                        parcels_dict['division'] = str(cadastral_parcels.iloc[0]['division'])
                                        parcels_dict['section'] = cadastral_parcels.iloc[0]['section']
                                        parcels_dict['radical'] = str(cadastral_parcels.iloc[0]['radical'])
                                        parcels_dict['bis'] = str(cadastral_parcels.iloc[0]['bis'])
                                        parcels_dict['exposant'] = cadastral_parcels.iloc[0]['exposant']
                                        parcels_dict['puissance'] = str(cadastral_parcels.iloc[0]['puissance'])
                                    elif result_count > 1:
                                        self.licence_description.append({'object': "Trop de résultats pour cette parcelle",
                                                                         'parcel': parcels_dict['complete_name'],
                                                                         })
                                    else:
                                        parcels_dict['outdated'] = 'False'
                                        parcels_dict['is_official'] = 'False'
                                        parcels_dict['division'] = str(int(division))
                                        parcels_dict['section'] = section
                                        parcels_dict['radical'] = str(radical)
                                        parcels_dict['bis'] = str(int(bis))
                                        parcels_dict['exposant'] = exposant
                                        parcels_dict['puissance'] = str(int(puissance))
                                        self.licence_description.append({'object': "Pas de résultat pour cette parcelle",
                                                                         'parcel': parcels_dict['complete_name'],
                                                                         })
                                else:
                                    self.licence_description.append({'object': "Parcelle incomplète ou non valide",
                                                                     'parcel': parcels_dict['complete_name'],
                                                                     })
                            else:
                                self.licence_description.append({'object': "Parcelle incomplète ou non valide",
                                                                 'parcel': parcels_dict['complete_name'],
                                                                 })
                        else:
                            self.licence_description.append({'object': "Parcelle incomplète ou non valide",
                                                             'parcel': parcels_dict['complete_name'],
                                                             })
                    else:
                        self.licence_description.append({'object': "Parcelle incomplète ou non valide",
                                                         'parcel': parcels_dict['complete_name'],
                                                         })
                    if parcels_dict['division'] and parcels_dict['section']:
                        licence_children.append(parcels_dict)
            except:
                print("debug)")

    @benchmark_decorator
    def get_organization(self, licence, licence_dict):
        organization_dict = get_organization_dict()
        if licence.ORG_NOM:
            organization_dict['personTitle'] = ""  # TODO mapping civilite / urban title
            organization_dict['name1'] = licence.ORG_NOM
            organization_dict['name2'] = licence.ORG_PRENOM
            organization_dict['number'] = licence.ORG_NUMERO
            organization_dict['street'] = licence.ORG_RUE
            organization_dict['zipcode'] = licence.ORG_CP
            organization_dict['city'] = licence.ORG_LOCALITE
            organization_dict['phone'] = licence.ORG_TEL
            organization_dict['gsm'] = licence.ORG_MOBILE
            organization_dict['email'] = licence.ORG_MAIL

            if licence.ORG_TYPE == 'ARCHITECTE' or \
               licence.ORG_TYPE == 'ARCHITECTE|DEMANDEUR_CU' or \
               licence.ORG_TYPE == 'AUTEUR_ETUDE' or \
               licence.ORG_TYPE == 'CONTACT_PEB' or \
               licence.ORG_TYPE == 'BUREAU':
                organization_dict['@type'] = 'Architect'
                licence_dict['architects'].append(organization_dict)
            elif licence.ORG_TYPE == 'NOTAIRE':
                organization_dict['@type'] = 'Notary'
                licence_dict['notaries'].append(organization_dict)
            elif licence.ORG_TYPE == 'GEOMETRE':
                organization_dict['@type'] = 'Geometrician'
                licence_dict['geometricians'].append(organization_dict)

    @benchmark_decorator
    def get_events(self, licence, licence_children):
        events = self.db.dossier_evenement_vue
        for key, values in events_types.items():
            events_etape = events[
                (events.ETAPE_TETAPEID.isin(values['etape_ids'])) &
                (events.WRKDOSSIER_ID == licence.WRKDOSSIER_ID)]
            events_param = None
            method = getattr(self, 'get_{0}_event'.format(key))
            method(licence, events_etape, events_param, licence_children)

    def get_recepisse_event(self, licence, events_etape, events_param, licence_children):
        for id, event in events_etape.iterrows():
            event_dict = get_event_dict()
            event_dict['title'] = 'Récépissé'
            event_dict['type'] = 'recepisse'
            event_dict['event_id'] = 'depot-de-la-demande'
            event_dict['eventDate'] = event.ETAPE_DATEDEPART
            licence_children.append(event_dict)

    def get_decision_event(self, licence, events_etape, events_param, licence_children):
        event_dict = get_event_dict()
        event_dict['title'] = 'Décision'
        event_dict['event_id'] = 'delivrance-du-permis-octroi-ou-refus'
        # event_dict['type'] = 'delivrance-du-permis-octroi-ou-refus'
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
            if decision_vocabulary_mapping.get(state_mapping.get(licence.DOSSIER_OCTROI)):
                event_dict['decision'] = decision_vocabulary_mapping.get(state_mapping.get(licence.DOSSIER_OCTROI))
            if events_etape.shape[0] > 1:
                raise ValueError('Too many decision events')
            elif events_etape.shape[0] == 1:
                event = events_etape.iloc[0]
                event_dict['decisionDate'] = event.ETAPE_DATEDEPART
                # if eventDate don't exist, decisionDate is used
                if not event_dict['eventDate'] or event_dict['eventDate'] == 'NaT':
                    event_dict['decisionDate'] = event.ETAPE_DATEDEPART
        licence_children.append(event_dict)


def main():
    """ """
    parser = argparse.ArgumentParser(description='Import data from Urbaweb CSV Files')
    parser.add_argument('config_file', type=str, help='path to the config')
    parser.add_argument('--limit', type=int, help='number of records')
    parser.add_argument('--view', type=str, default='permis_urbanisme_vue', help='give licence view to call')
    parser.add_argument('--licence_id', type=str, help='reference of a licence')
    parser.add_argument('--range', type=str, help="input slice, example : '5:10'")
    parser.add_argument('--ignore_cache', type=bool, nargs='?',
                        const=True, default=False, help='ignore local cache')
    parser.add_argument('--benchmarking', type=bool, nargs='?',
                        const=True, default=False, help='add benchmark infos')
    parser.add_argument('--noop', type=bool, nargs='?',
                        const=True, default=False, help='only print result')
    parser.add_argument('--iterate', type=bool, nargs='?',
                        const=True, default=False, help='Use a special cache to iterate')
    args = parser.parse_args()

    ImportUrbaweb(
        args.config_file,
        view=args.view,
        limit=args.limit,
        range=args.range,
        licence_id=args.licence_id,
        ignore_cache=args.ignore_cache,
        benchmarking=args.benchmarking,
        noop=args.noop,
        iterate=args.iterate
    ).execute()
