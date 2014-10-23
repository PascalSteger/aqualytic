#!/usr/bin/env python3

import pdb
import datetime

# new date
to = datetime.date.fromordinal(735948) #693966)
print('from ordinal: ', to)

tt = datetime.date.fromtimestamp(735948) #693966)
print('from timestamp: ', tt)



import pandas as pd
df = pd.read_csv('data/data_Q_Dec.csv')


def convert_timestamps(arr):
    out = []
    for a in arr:
        out.append(datetime.date.fromordinal(a))
    return out
## \fn convert_timestamps(arr)
# convert from matlab datetime output back to year-month-day
# @param arr array of ordinal dates

ct = convert_timestamps(df.time)

pdb.set_trace()
