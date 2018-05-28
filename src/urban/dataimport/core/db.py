# -*- coding: utf-8 -*-

import os
import pandas as pd


class LazyDB:

    def __init__(self, connection, db_schema):
        self.connection = connection
        self.db_schema = db_schema

    def __getattr__(self, name):
        try:
            return self.__getattribute__(name)
        except AttributeError:
            cache_fname = self._cache_fname(name)
            if os.path.exists(cache_fname):
                df = pd.read_pickle(cache_fname)
            else:
                result = self.connection.execute(self._query(name))
                df = pd.DataFrame(result.fetchall())
                df.columns = result.keys()
                df.to_pickle(cache_fname)
            setattr(self, name, df)
            return df

    def _query(self, name):
        return 'SELECT * FROM `{schema}`.{name}'.format(
            schema=self.__dict__['db_schema'],
            name=name,
        )

    def _cache_fname(self, name):
        return '/tmp/{schema}.{name}'.format(
            schema=self.__dict__['db_schema'],
            name=name,
        )

    def __setattr__(self, key, value):
        self.__dict__[key] = value
