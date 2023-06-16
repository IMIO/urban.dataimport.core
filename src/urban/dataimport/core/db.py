# -*- coding: utf-8 -*-

import os
import pandas as pd


class LazyDB:

    def __init__(self, connection, db_schema, ignore_cache=False):
        self.connection = connection
        self.db_schema = db_schema
        self.ignore_cache = True

    def __getattr__(self, name):
        try:
            return self.__getattribute__(name)
        except AttributeError:
            cache_fname = self._cache_fname(name)
            if os.path.exists(cache_fname) and self.ignore_cache is False:
                df = pd.read_pickle(cache_fname)
            else:
                result = self.connection.execute(self._query(name))
                df = pd.DataFrame(result.fetchall())
                df.columns = result.keys()
                df.to_pickle(cache_fname)
            setattr(self, name, df)
            return df

    def _query(self, name):
        if not ('postgresql' in str(self.connection.engine)):
            return 'SELECT * FROM `{schema}`.{name}'.format(
                schema=self.__dict__['db_schema'],
                name=name,
            )
        else:
            return 'SELECT * FROM {name}'.format(
                name=name,
            )

    def _cache_fname(self, name):
        return '/tmp/{schema}.{name}'.format(
            schema=self.__dict__['db_schema'],
            name=name,
        )

    def __setattr__(self, key, value):
        self.__dict__[key] = value

    def create_view(self, view_name, view_query):
        query = "{schema} CREATE OR REPLACE VIEW {name} AS {query}".format(
            schema=(not ('postgresql' in str(self.connection.engine))) and ("USE " + self.__dict__['db_schema']) + ";" or "",
            name=view_name,
            query=view_query,
        )
        self.connection.execute(query)
