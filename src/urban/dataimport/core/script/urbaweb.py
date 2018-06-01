# -*- coding: utf-8 -*-

from urban.dataimport.core import utils
from urban.dataimport.core.csv import LoadUrbawebCSV

import argparse
import configparser


class ImportUrbaweb:

    def __init__(self, config_file):
        config = configparser.ConfigParser()
        config_file = utils.format_path(config_file)
        config.read(config_file)
        self.config = config
        self.csv = LoadUrbawebCSV(**self.config._sections['csv'])

    def execute(self):
        return self.csv


def main():
    """ """
    parser = argparse.ArgumentParser(description='Import data from Urbaweb CSV Files')
    parser.add_argument('config_file', type=str, help='path to the config')
    parser.add_argument('--limit', type=int, help='number of records')
    args = parser.parse_args()

    ImportUrbaweb(args.config_file).execute()
