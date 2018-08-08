# -*- coding: utf-8 -*-

from sqlalchemy import create_engine
from urban.dataimport.core import utils
from urban.dataimport.core.db import LazyDB

import argparse
import configparser
import json

from urban.dataimport.core.json import get_licence_dict


class ImportAcropole:

    def __init__(self, config_file):
        config = configparser.ConfigParser()
        config_file = utils.format_path(config_file)
        config.read(config_file)
        self.config = config
        engine = create_engine('mysql://{user}:{password}@{host}:{port}'.format(**config._sections['database']))
        connection = engine.connect()
        self.db = LazyDB(connection, config['database']['schema'])
        self.create_views()

    def execute(self):

        # partir d un dictionnaire template (methode dans json.py) de dossier et puis le nourrir dans une boucle sur le dataframe
        # export json à partir du dictionnaire
        # utiliser json
        # schema pour valider le dossier (methode dans json.py)
        # merged = pd.merge(
        #     self.db.k2,
        #     self.db.wrkdossier,
        #     left_on='K_ID1',
        #     right_on='WRKDOSSIER_ID',
        #     how='left',
        #     left_index=True,
        # )
        # return merged
        data = []
        for licence in self.db.wrkdossier:
            licence_dict = get_licence_dict()
            licence_dict['reference'] = licence.DOSSIER_NUMERO
            data.append(licence_dict)

        print(json.dumps(data))

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

        self.db.create_view("dossier_personne",
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
                                       ADRESSE_PERSONNE.CLOC_TVA
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


def main():
    """ """
    parser = argparse.ArgumentParser(description='Import data from Acropole Database')
    parser.add_argument('config_file', type=str, help='path to the config')
    parser.add_argument('--limit', type=int, help='number of records')
    args = parser.parse_args()

    ImportAcropole(args.config_file).execute()
