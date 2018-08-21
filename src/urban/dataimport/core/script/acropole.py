# -*- coding: utf-8 -*-

from sqlalchemy import create_engine
from urban.dataimport.core import utils
from urban.dataimport.core.db import LazyDB
from urban.dataimport.core.mapping.acropole_mapping import events_types, portal_type_mapping, \
    state_mapping, title_types

import argparse
import configparser
import json

from urban.dataimport.core.json import DateTimeEncoder, get_applicant_dict, get_event_dict, get_licence_dict, \
    get_parcel_dict, get_work_locations_dict
from urban.dataimport.core.views.acropole_views import create_views


class ImportAcropole:

    def __init__(self, config_file, limit=None, licence_id=None, ignore_cache=False):
        config = configparser.ConfigParser()
        config_file = utils.format_path(config_file)
        config.read(config_file)
        self.config = config
        self.limit = limit
        self.licence_id = licence_id
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
        create_views(self)

    def execute(self):

        # utiliser json
        # schema pour valider le dossier (methode dans json.py)
        data = []
        folders = self.db.wrkdossier
        if self.limit:
            folders = folders.head(self.limit)
        if self.licence_id:
            folders = folders[folders.DOSSIER_NUMERO == self.licence_id]
        for id, licence in folders.iterrows():
            licence_dict = get_licence_dict()
            licence_dict['id'] = licence.WRKDOSSIER_ID
            licence_dict['portalType'] = self.get_portal_type(licence)
            if not licence_dict['portalType']:
                continue
            licence_dict['reference'] = licence.DOSSIER_NUMERO
            licence_dict['referenceDGATLP'] = licence.DOSSIER_REFURB
            licence_dict['completionState'] = state_mapping.get(licence.DOSSIER_OCTROI, '')
            licence_dict['workLocations'] = self.get_work_locations(licence)
            licence_dict['applicants'] = self.get_applicants(licence)
            licence_dict['parcels'] = self.get_parcels(licence)
            licence_dict['events'] = self.get_events(licence)
            data.append(licence_dict)

        print(json.dumps(data, cls=DateTimeEncoder))

    def get_portal_type(self, licence):
        portal_type = portal_type_mapping.get(licence.DOSSIER_TDOSSIERID, None)
        if portal_type == 'UrbanCertificateOne' and licence.DOSSIER_TYPEIDENT == 'CU2':
            portal_type = 'UrbanCertificateTwo'
        return portal_type

    def get_work_locations(self, licence):
        work_locations_list = []

        work_locations = self.db.dossier_adresse_vue[
            (self.db.dossier_adresse_vue.WRKDOSSIER_ID == licence.WRKDOSSIER_ID)]

        for id, work_location in work_locations.iterrows():
            work_locations_dict = get_work_locations_dict()
            work_locations_dict['address'] = work_location.ADR_ADRESSE
            work_locations_dict['number'] = work_location.ADR_NUM
            work_locations_dict['postalcode'] = work_location.ADR_ZIP
            work_locations_dict['locality'] = work_location.ADR_LOCALITE
            work_locations_list.append(work_locations_dict)

        return work_locations_list

    def get_applicants(self, licence):
        applicant_list = []
        applicants = self.db.dossier_personne_vue[
            (self.db.dossier_personne_vue.WRKDOSSIER_ID == licence.WRKDOSSIER_ID) &
            (self.db.dossier_personne_vue.K2KND_ID == -204)]
        for id, applicant in applicants.iterrows():
            applicant_dict = get_applicant_dict()
            applicant_dict['personTitle'] = title_types.get(applicant.CPSN_TYPE, None)
            applicant_dict['lastname'] = applicant.CPSN_NOM
            applicant_dict['firstname'] = applicant.CPSN_PRENOM
            applicant_list.append(applicant_dict)

        return applicant_list

    def get_parcels(self, licence):
        parcels_list = []
        parcels = self.db.dossier_parcelles_vue[
            (self.db.dossier_parcelles_vue.WRKDOSSIER_ID == licence.WRKDOSSIER_ID)]
        for id, parcels in parcels.iterrows():
            parcels_dict = get_parcel_dict()
            parcels_dict['complete_name'] = parcels.CAD_NOM
            parcels_list.append(parcels_dict)

        return parcels_list

    def get_events(self, licence):
        event_list = []

        for key, values in events_types.items():
            events_etape = self.db.dossier_evenement_vue[
                (self.db.dossier_evenement_vue.ETAPE_TETAPEID.isin(values['etape_ids'])) &
                (self.db.dossier_evenement_vue.WRKDOSSIER_ID == licence.WRKDOSSIER_ID) &
                (self.db.dossier_evenement_vue.K2KND_ID == -207)]

            events_param = self.db.dossier_param_vue[
                (self.db.dossier_param_vue.PARAM_TPARAMID.isin(values['param_ids'])) &
                (self.db.dossier_param_vue.WRKDOSSIER_ID == licence.WRKDOSSIER_ID) &
                (self.db.dossier_param_vue.K2KND_ID == -208) &
                (self.db.dossier_param_vue.PARAM_VALUE.notnull())]
            method = getattr(self, 'get_{0}_event'.format(key))
            result_list = method(events_etape, events_param)
            if result_list:
                event_list.extend(result_list)

        return event_list

    def get_recepisse_event(self, events_etape, events_param):
        events_dict = []
        for id, event in events_etape.iterrows():
            event_dict = get_event_dict()
            event_dict['type'] = 'recepisse'
            event_dict['eventDate'] = event.ETAPE_DATEDEPART
            events_dict.append(event_dict)
        return events_dict

    def get_decision_event(self, events_etape, events_param):
        events_dict = []
        if events_etape.shape[0] > 1:
            raise ValueError('Too many decision events')
        elif events_etape.shape[0] == 1:
            event = events_etape.iloc[0]
            event_dict = get_event_dict()
            event_dict['type'] = 'decision'
            event_dict['eventDate'] = event.ETAPE_DATEDEPART
            if events_param.shape[0] == 1:
                if events_param.iloc[0].PARAM_VALUE == '1':
                    event_dict['decision'] = 'favorable'
                else:
                    event_dict['decision'] = 'défavorable'
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
    args = parser.parse_args()

    ImportAcropole(
        args.config_file,
        limit=args.limit,
        licence_id=args.licence_id,
        ignore_cache=args.ignore_cache,
    ).execute()
