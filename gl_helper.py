#!/usr/bin/env ipython3

##
# @file
# small functions to be used in main forecast program

import time, datetime

def LOG(level, message, var=''):
    if level > DEBUGLEVEL:
        return
    t = time.time()
    print(time.ctime(t), message, var)
    return
## \fn LOG(level, warning, var)
# print debugging message if level is important enough
# @param level 0: none, 1: some, 2: more, 3: all
# @param warning string
# @param var variable (not mandatory)


def convert_timestamps(arr):
    out = []
    for a in arr:
        out.append(datetime.date.fromordinal(a))
    return out
## \fn convert_timestamps(arr)
# convert from matlab datetime output back to year-month-day
# @param arr array of ordinal dates
