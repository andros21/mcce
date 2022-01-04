#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ......................................
#
#   Name:   year_drop.py
#   Author: Andrea Rossoni
#   Scope:  Drop all tables on heroku
#           postgresql deployment
# ......................................

import os

import sqlalchemy


def drop_all_tables(uri):
    """drop all tables on heroku postgresql"""
    engine = sqlalchemy.create_engine(uri)
    insp = sqlalchemy.inspect(engine)
    meta = sqlalchemy.MetaData(engine)

    sqlalchemy.MetaData.reflect(meta)

    tables = insp.get_table_names()
    for table in tables:
        table_obj = meta.tables[table]
        table_obj.drop()


if __name__ == "__main__":
    db_uri = os.environ["DATABASE_URL"]
    drop_all_tables(db_uri)
