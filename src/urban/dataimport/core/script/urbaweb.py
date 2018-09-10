# -*- coding: utf-8 -*-

from urban.dataimport.core import utils
from urban.dataimport.core.csv import LoadUrbawebCSV

import argparse
import configparser

from urban.dataimport.core.views.urbaweb_views import create_views


class ImportUrbaweb:

    def __init__(self, config_file):
        config = configparser.ConfigParser()
        config_file = utils.format_path(config_file)
        config.read(config_file)
        self.config = config
        self.db = LoadUrbawebCSV(**self.config._sections['csv'])
        create_views(self)

    def execute(self):
        return self.csv


def main():
    """ """
    parser = argparse.ArgumentParser(description='Import data from Urbaweb CSV Files')
    parser.add_argument('config_file', type=str, help='path to the config')
    parser.add_argument('--limit', type=int, help='number of records')
    args = parser.parse_args()

    ImportUrbaweb(args.config_file).execute()
