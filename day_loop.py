#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ....................................................
#        __          __
#    ___/ /__ ___ __/ /__  ___  ___  __ __
#   / _  / _ `/ // / / _ \/ _ \/ _ \/ // /
#   \_,_/\_,_/\_, /_/\___/\___/ .__/\_, /
#            /___/           /_/   /___/
#
#   Author: Andrea Rossoni
#   Scope:  Daemon for parsing every 5 sec current
#           electricity value using serial connection
#           After parsed:
#             * append it to a day history file
#             * notification if over-threshold
# ....................................................

import codecs
import datetime
import os
import subprocess
import time
import timeit

import serial


def cut_between(s, first, last):
    """slice the given hex string (s) between (first) and (last)"""
    try:
        start = s.index(first) + len(first)
        end = s.index(last, start)
        return s[start:end]
    except ValueError:
        return ""


def get_cv(com, lv):
    """
    get current value:
      * send hex signal, to start stream
      * grep the value
      * convert and return it
    if something fails, return last value (lv)
    """
    com.write(bytes.fromhex("aa0200ad"))
    dim = com.in_waiting
    hexstream = str(codecs.encode(com.read(dim), "hex"))
    hexvalue = cut_between(hexstream, "5330323232", "31533033")
    try:
        left_value = int(str(hexvalue[0:2]), 16)
        if len(hexvalue) <= 2:
            right_value = 0
        else:
            right_value = int(str(hexvalue[2:4] + "0" + "0"), 16)
        return left_value + right_value
    except ValueError:
        return lv


def check_cv(cv):
    """if current value (cv) above Enel threshold, play alarm"""
    if cv >= 4200:
        subprocess.call("python3 alarm4200.py &".split(" "))
    else:
        pass


def write_cv(cv):
    """write current value (cv) to file, named as today date"""
    cdate = datetime.datetime.now()
    with open(f'days/{cdate.strftime("%Y-%m-%d")}', "a") as fso:
        fso.write(str(cv) + "\n")


def looper(cv=0):
    """loop read current value (cv) every 5 seconds"""
    while True:
        start = timeit.default_timer()
        cv = get_cv(ser, cv)
        check_cv(cv)
        write_cv(cv)
        stop = timeit.default_timer()
        time.sleep(5.0 + (start - stop))


if __name__ == "__main__":
    ser = serial.Serial("/dev/ttyUSB0", 9600)
    if not os.path.exists("days"):
        os.makedirs("days")
    looper()
