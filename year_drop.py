#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ......................................
#
#   Name:   year_drop.py
#   Author: Andrea Rossoni
#   Scope:  Drop all tables on flyio
#           postgresql deployment
# ......................................

import os

import sqlalchemy


def drop_all_tables(uri):
    """drop all tables on flyio postgresql"""
    engine = sqlalchemy.create_engine(uri)
    meta = sqlalchemy.MetaData()
    meta.reflect(engine)
    meta.drop_all(engine)


if __name__ == "__main__":
    db_uri = os.environ["DATABASE_URL"].replace("postgres://", "postgresql://")
    drop_all_tables(db_uri)
