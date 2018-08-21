# -*- coding: utf-8 -*-

from sqlalchemy import create_engine
from urban.dataimport.core import utils
from urban.dataimport.core.db import LazyDB

import argparse
import configparser
import json

from urban.dataimport.core.json import DateTimeEncoder, get_applicant_dict, get_event_dict, get_licence_dict, \
    get_parcel_dict, get_work_locations_dict


class ImportAcropole:
    events_types = {
        'recepisse': {
            'etape_ids': (-65091, -55774, -48189, -46732, -42670, -33521),
            'param_ids': (),
        },
        'decision': {
            'etape_ids': (-43439, -33545, -63967, -55736, -38452, -49801),
            'param_ids': (-35039, -79378, -78845, -78319, -49413, -62984),
        },
    }

    portal_type_mapping = {
        -67348: 'EnvClassTwo',
        -62737: 'ParcelOutLicence',
        -53925: 'UniqueLicence',
        -49306: 'Article127',
        -46623: 'EnvClassThree',
        -42575: 'BuildLicence',
        -37624: 'EnvClassTwo',
        -36624: '',  # infractions, not yet implemented
        -34766: 'NotaryLetter',
        -32669: 'BuildLicence',  # ?
        -15200: 'Declaration',
        -14179: 'Division',
    }

    state_mapping = {
        -58: 'refuse',  # irrecevable (validé par chatelet)
        -49: 'accept',  # -49 = octroyé
        -46: 'refuse',  # -46 = annulé par le FD
        -30: 'accept',  # recevable (validé par chatelet)
        -27: 'accept',  # recevable avec condition (validé par chatelet)
        -26: 'accept',  # -26 = octroyé
        -20: 'refuse',  # refus, ministre sur recours (validé par chatelet)
        -19: 'retire',  # -19 = périmé
        -17: 'refuse',  # refus (FT) (validé par chatelet)
        -15: 'accept',  # accepté (FT) (validé par chatelet)
        -14: 'accept',  # -14 = octroyé
        -12: 'accept',  # -12 = octroyé (validé par Fl)
        -11: 'retire',  # -11 = retiré
        -10: 'retire',  # -10 = retiré (validé par Fl)
        -8: 'refuse',  # irrecevable (validé par chatelet)
        -7: 'accept',  # recevable (validé par chatelet)
        -6: 'accept',  # -6 = octroyé (validé par Fl)
        -5: 'refuse',  # -5 = refusé
        -4: 'retire',  # -4 = suspendu
        -3: 'accept',  # -3 = octroyé
        -2: 'retire',  # -2 = abandonné
        -1: '',  # -1 = en cours
        0: 'refuse',  # -1 = refusé
        1: 'accept',  # 1 = octroyé
    }

    title_types = {
        -1000: 'mister',
        21607: 'misters',
        -1001: 'madam',
        171280: 'ladies',
        -1002: 'miss',
        -1003: 'madam_and_mister',
        676263: 'madam_and_mister',
        850199: 'madam_and_mister',
        89801: 'master',
    }

    division_mapping = {
        '01': '52012',
        '02': '52013',
        '03': '52502',
        '04': '52007',
    }

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
        self.create_views()

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
            licence_dict['completionState'] = self.state_mapping.get(licence.DOSSIER_OCTROI, '')
            licence_dict['workLocations'] = self.get_work_locations(licence)
            licence_dict['applicants'] = self.get_applicants(licence)
            licence_dict['parcels'] = self.get_parcels(licence)
            licence_dict['events'] = self.get_events(licence)
            data.append(licence_dict)

        print(json.dumps(data, cls=DateTimeEncoder))

    def get_portal_type(self, licence):
        portal_type = self.portal_type_mapping.get(licence.DOSSIER_TDOSSIERID, None)
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
            applicant_dict['personTitle'] = self.title_types.get(applicant.CPSN_TYPE, None)
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

        for key, values in self.events_types.items():
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

    def create_views(self):
        self.db.create_view("dossier_enquete",
                            """
                                SELECT DOSSIER.WRKDOSSIER_ID,
                                       DOSSIER.DOSSIER_NUMERO,
                                       PARAM.PARAM_IDENT,
                                       PARAM.PARAM_VALUE,
                                        PARAM.PARAM_NOMFUSION,
                                       REMARQUE.REMARQ_LIB
                                FROM
                                    wrkdossier AS DOSSIER
                                INNER JOIN k2 AS MAIN_JOIN
                                ON MAIN_JOIN.K_ID1 = DOSSIER.WRKDOSSIER_ID
                                INNER JOIN wrkparam AS PARAM
                                ON MAIN_JOIN.K_ID2 = PARAM.WRKPARAM_ID
                                LEFT JOIN cremarq AS REMARQUE
                                ON PARAM.PARAM_VALUE = REMARQUE.CREMARQ_ID
                                WHERE PARAM.PARAM_IDENT in ('EnqDatDeb', 'EnqDatFin', 'EnqObjet')
                            """
                            )

        self.db.create_view("dossier_personne_vue",
                            """
                                SELECT DOSSIER.WRKDOSSIER_ID, DOSSIER.DOSSIER_NUMERO,
                                       PERSONNE.CPSN_NOM,
                                       PERSONNE.CPSN_PRENOM,
                                       PERSONNE.CPSN_TYPE,
                                       PERSONNE.CPSN_TEL1,
                                       PERSONNE.CPSN_TEL2,
                                       PERSONNE.CPSN_FAX,
                                       PERSONNE.CPSN_GSM,
                                       PERSONNE.CPSN_EMAIL,
                                       PERSONNE.CPSN_RN,
                                       PERSONNE.CPSN_TVA,
                                       PERSONNE.CPSN_ENABLED,
                                       PERSONNE.CPSN_BCE,
                                       ADRESSE_PERSONNE.CLOC_ID,
                                       ADRESSE_PERSONNE.CLOC_ADRESSE,
                                       ADRESSE_PERSONNE.CLOC_ZIP,
                                       ADRESSE_PERSONNE.CLOC_LOCALITE,
                                       ADRESSE_PERSONNE.CLOC_NOM,
                                       ADRESSE_PERSONNE.CLOC_TEL1,
                                       ADRESSE_PERSONNE.CLOC_TEL2,
                                       ADRESSE_PERSONNE.CLOC_FAX,
                                       ADRESSE_PERSONNE.CLOC_EMAIL,
                                       ADRESSE_PERSONNE.CLOC_GSM,
                                       ADRESSE_PERSONNE.CLOC_TVA,
                                       MAIN_JOIN.K2KND_ID
                                FROM
                                    wrkdossier AS DOSSIER
                                INNER JOIN k2 AS MAIN_JOIN
                                ON MAIN_JOIN.K_ID2 = DOSSIER.WRKDOSSIER_ID
                                INNER JOIN cpsn AS PERSONNE
                                ON MAIN_JOIN.K_ID1 = PERSONNE.CPSN_ID
                                INNER JOIN k2 AS MAIN_JOIN_BIS
                                ON MAIN_JOIN_BIS.K_ID2 = PERSONNE.CPSN_ID
                                INNER JOIN cloc AS ADRESSE_PERSONNE
                                ON MAIN_JOIN_BIS.K_ID1 = ADRESSE_PERSONNE.CLOC_ID;
                            """
                            )

        self.db.create_view("dossier_parcelles_vue",
                            """
                                SELECT DOSSIER.WRKDOSSIER_ID, DOSSIER.DOSSIER_NUMERO,
                                       CADASTRE.CAD_NOM
                                FROM
                                    wrkdossier AS DOSSIER
                                INNER JOIN urbcadastre AS CADASTRE
                                ON CADASTRE.CAD_DOSSIER_ID = DOSSIER.WRKDOSSIER_ID;
                            """
                            )
        self.db.create_view("dossier_adresse_vue",
                            """
                                SELECT DOSSIER.WRKDOSSIER_ID, DOSSIER.DOSSIER_NUMERO,
                                       ADR.ADR_ADRESSE,
                                       ADR.ADR_NUM,
                                       ADR.ADR_ZIP,
                                       ADR.ADR_LOCALITE
                                FROM
                                    wrkdossier AS DOSSIER
                                INNER JOIN k2adr AS MAIN_JOIN
                                ON MAIN_JOIN.K_ID1 = DOSSIER.WRKDOSSIER_ID
                                INNER JOIN adr AS ADR
                                ON MAIN_JOIN.K_ID2 = ADR.ADR_ID;
                            """
                            )
        self.db.create_view("dossier_evenement_vue",
                            """
                                SELECT DOSSIER.WRKDOSSIER_ID, DOSSIER.DOSSIER_NUMERO,
                                       WRKETAPE_ID,
                                       ETAPE_NOMFR,
                                       ETAPE_TETAPEID,
                                       ETAPE_DATEDEPART,
                                       ETAPE_DATEBUTOIR,
                                       ETAPE_DELAI,
                                       MAIN_JOIN.K2KND_ID
                                FROM
                                    wrkdossier AS DOSSIER
                                INNER JOIN k2 AS MAIN_JOIN
                                ON MAIN_JOIN.K_ID1 = DOSSIER.WRKDOSSIER_ID
                                INNER JOIN wrketape AS ETAPE
                                ON MAIN_JOIN.K_ID2 = ETAPE.WRKETAPE_ID;
                            """
                            )
        self.db.create_view("dossier_param_vue",
                            """
                                SELECT DOSSIER.WRKDOSSIER_ID, DOSSIER.DOSSIER_NUMERO,
                                       WRKPARAM_ID,
                                       PARAM_TPARAMID,
                                       PARAM_NOMFUSION,
                                       PARAM_VALUE,
                                       MAIN_JOIN.K2KND_ID
                                FROM
                                    wrkdossier AS DOSSIER
                                INNER JOIN k2 AS MAIN_JOIN
                                ON MAIN_JOIN.K_ID1 = DOSSIER.WRKDOSSIER_ID
                                INNER JOIN wrkparam AS PARAM
                                ON MAIN_JOIN.K_ID2 = PARAM.WRKPARAM_ID;
                            """
                            )
        self.cadastral.create_view("vieilles_parcelles_cadastrales_vue",
                                   """
                                    SELECT DISTINCT prca,
                                            prcc,
                                            prcb1 as prc,
                                            DA.divname,
                                            PAS.da as division,
                                            section,
                                            radical,
                                            exposant,
                                            bis,
                                            puissance
                                    FROM pas AS PAS
                                    LEFT JOIN DA on DA.da = PAS.da;
                                   """,
                                   without_use=True
                                   )
        self.cadastral.create_view("parcelles_cadastrales_vue",
                                   """
                                    SELECT CAPA.da as division,
                                            divname,
                                            prc,
                                            section,
                                            radical,
                                            exposant,
                                            bis,
                                            puissance,
                                            pe as proprietary,
                                            adr1 as proprietary_city,
                                            adr2 as proprietary_street,
                                            sl1 as location
                                    FROM map AS MAP
                                    LEFT JOIN capa AS CAPA
                                    ON MAP.capakey = CAPA.capakey
                                    LEFT JOIN da AS DA
                                    ON CAPA.da = DA.da;
                                   """,
                                   without_use=True
                                   )


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
