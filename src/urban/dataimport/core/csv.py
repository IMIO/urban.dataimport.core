# -*- coding: utf-8 -*-

import pandas as pd


class LoadUrbawebCSV:

    def __init__(self, csv_path, csv_tables, csv_sep, csv_encoding):
        for table in csv_tables.split(','):
            df = pd.read_csv(csv_path + '%s.csv' % (table.strip()), sep=csv_sep, header=0, encoding=csv_encoding, na_filter=False,
                        index_col=0, nrows=10)
            setattr(self, table.strip(), df)
