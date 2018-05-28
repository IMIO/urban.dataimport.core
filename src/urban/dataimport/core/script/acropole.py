# -*- coding: utf-8 -*-

from sqlalchemy import create_engine
from urban.dataimport.core import utils
from urban.dataimport.core.db import LazyDB

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
        connection = engine.connect()
        self.db = LazyDB(connection, config['database']['schema'])

    def execute(self):
        merged = pd.merge(
            self.db.k2,
            self.db.wrkdossier,
            left_on='K_ID1',
            right_on='WRKDOSSIER_ID',
            how='left',
            left_index=True,
        )


def main():
    """ """
    parser = argparse.ArgumentParser(description='Import data from Acropole Database')
    parser.add_argument('config_file', type=str, help='path to the config')
    parser.add_argument('--limit', type=int, help='number of records')
    args = parser.parse_args()

    ImportAcropole(args.config_file).execute()
