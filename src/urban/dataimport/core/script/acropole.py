# -*- coding: utf-8 -*-

from sqlalchemy import create_engine
from urban.dataimport.core import utils

import argparse
import configparser
import pandas as pd


class ImportAcropole:

    def __init__(self, config_file):
        config = configparser.ConfigParser()
        config_file = utils.format_path(config_file)
        config.read(config_file)
        self.config = config
        engine = create_engine('mysql://{user}:{password}@{host}:{port}'.format(**config._sections['database']))
        self.connection = engine.connect()

    def execute(self):
        resoverall = self.connection.execute("""
        SELECT *
        FROM `{schema}`.wrkdossier AS DOSSIER
        LEFT JOIN `{schema}`.k2 AS K2
               ON DOSSIER.WRKDOSSIER_ID = K2.K_ID1
        """.format(
            **self.config._sections['database']))

        df = pd.DataFrame(resoverall.fetchall())
        df.columns = resoverall.keys()


def main():
    """ """

    parser = argparse.ArgumentParser(description='Import data from Acropole Database')
    parser.add_argument('config_file', type=str, help='path to the config')
    args = parser.parse_args()

    ImportAcropole(args.config_file).execute()
