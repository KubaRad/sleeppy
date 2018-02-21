"""
Created on 12-08-2011

@author: Kuba Radliński
"""

from datetime import time, date, datetime, timedelta
from os.path import splitext
from math import floor


def string_trim_to_0(s):
    found = False
    index = 0
    for i in s:
        if i == 0:
            found = True
            break
        index += 1
    if found:
        return s[0:index].decode("ASCII")
    else:
        return s.decode("ASCII")


def decode_time(tm):
    h = tm // (60 * 60 * 1000)
    m = (tm // (60 * 1000)) % 60
    s = (tm // 1000) % 60
    ms = tm % 1000
    return time(h if 0 <= h <= 23 else h - 24, m, s, ms * 1000)


def decode_time_seconds(tm):
    h = tm // (60 * 60 * 1000)
    m = (tm // (60 * 1000)) % 60
    s = (tm // 1000) % 60
    return time(h if 0 <= h <= 23 else h - 24, m, s, 0)


def time_to_time_seconds(tm):
    return tm.replace(microsecond=0)


def add_seconds_to_time(timeval, secs_to_add):
    return (datetime.combine(date(1, 1, 1), timeval) + timedelta(seconds=secs_to_add)).time()


def ms_to_events_seconds(ms):
    return floor(ms / 1000)


def decode_date(dt):
    y = dt // (31 * 12)
    m = (dt // 31) % 12
    if m == 0:
        m = 12
        y -= 1
    d = dt % 31
    if d == 0:
        d = 31
        m -= 1
    if y <= 0:
        return date(1900, 1, 1)
    return date(y, m, d)


def date_2_remlogic_date(c):
    return str(c.day) + '/' + str(c.month) + '/' + str(c.year)


def make_brainlab_filenames(fn):
    basename = splitext(fn)[0]
    return "".join([basename, ".sig"]), "".join([basename, ".tbl"])

