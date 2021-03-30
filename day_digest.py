#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ..........................................................
#        __             ___              __
#    ___/ /__ ___ _____/ (_)__ ____ ___ / /_
#   / _  / _ `/ // / _  / / _ `/ -_|_-</ __/
#   \_,_/\_,_/\_, /\_,_/_/\_, /\__/___/\__/
#            /___/       /___/
#
#   Author: Andrea Rossoni
#   Scope:  (Yester)day digest after midnight:
#              * create a df from history file
#              * adjust df size
#              * label columns, add datetime indexes
#                and resample df using lower resolution
#              * compute (yester)day average
#              * upload df as new day table inside DB
#              * append (yester)day average to 'avg' table
#                inside the DB
# ..........................................................

import datetime
import os
import sqlite3

import numpy as np
import pandas as pd
import sqlalchemy


def adjust_df(df, tsize):
    """
    check if df hasthe correct size, so if the value of the
    day were recorded every 5 seconds, otherwise adjust it
    """
    dsize = tsize - df.size
    if dsize == 0:
        pass
    else:
        if dsize > 0:
            df_tail = df.tail(dsize)
            df = df.append(df_tail).reset_index(drop=True)
        else:
            df = df[:dsize]
    return df


def resample_df(date, df, tsize, res):
    """
    transform the df in a datetime df, adding datetime
    index, after that resample with a lower
    resolution, instead of 5 seconds resolution
    """
    di = pd.to_datetime(f'{date.strftime("%Y-%m-%d")} 00:00:00') + pd.to_timedelta(
        np.arange(0, tsize * 5, 5), "S"
    )
    df = pd.DataFrame(df[0].values.tolist(), index=di, columns=["Wh"])
    df = np.around(df.resample(f"{res*60}S").mean(), 2)
    return df


def refresh_db(uri, date, df, davg):
    """upload yesterday data to local/remote DB"""
    if "postgresql://" in uri:
        engine = sqlalchemy.create_engine(uri)
    else:
        engine = sqlite3.connect(f"{uri}.{date.year}")
    # upload yesterday history
    df.to_sql(date.strftime("%Y-%m-%d"), engine)
    # upload yesterday average
    dfa = pd.DataFrame([davg], index=[date.strftime("%Y-%m-%d")], columns=["kWh"])
    dfa.to_sql("avg", engine, if_exists="append")


if __name__ == "__main__":

    fixed_day_size = 17281  # expected day file lines
    cdate = datetime.datetime.now()  # today date
    db_uri = os.environ["DATABASE_URL"]  # database path/url
    resolution = int(os.environ["MIN_TIME_RES"])  # time resolution in min
    bdate = cdate - datetime.timedelta(days=1)  # yesterday date

    df = pd.read_csv(f'days/{bdate.strftime("%Y-%m-%d")}', header=None)

    df = adjust_df(df, fixed_day_size)

    # compute (yester)day average over the total values collected
    day_avg = np.round(df.sum() * (5.0 / (3600.0 * 1000.0)), 2)[0]
    # over-write the adjusted day history file
    df.to_csv(f'days/{bdate.strftime("%Y-%m-%d")}', header=None, index=False)

    df = resample_df(bdate, df, fixed_day_size, resolution)
    refresh_db(db_uri, bdate, df, day_avg)
