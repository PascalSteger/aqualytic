#!/usr/bin/env python3

##
# @file

# write output files based on time of forecast
# 3 files: comparison (real) flux, predicted flux, error

import numpy as np
import csv
import pdb

def write_output_files(fname, T_forecast, Q_compare, Q_forecast):
    Q_err = Q_compare - Q_forecast

    # open csv file
    with open(fname, 'w') as csvfile:
        print('T_forecast [day], Q_compare [m3/s], Q_forecast [m3/s]', file=csvfile)
        for k in range(len(T_forecast)):
            #print(T_forecast[k], ',',  Q_compare[k],',', Q_forecast[k],',', Q_err[k], file=csvfile)
            year = int(T_forecast[k]/365.25)
            daysleft = T_forecast[k]-365.25*year
            month = int(daysleft/30)
            daysleft = daysleft - month*30
            day = int(daysleft)

            hoursleft = (daysleft-day)*24
            hour = int(hoursleft)
            minleft = (hoursleft-hour)*60
            min = int(minleft)

            fill_month=""; fill_day=""; fill_hour=""; fill_min=""
            if len(str(month)) == 1:
                fill_month="0"
            if len(str(day)) == 1:
                fill_day="0"
            if len(str(hour)) == 1:
                fill_hour="0"
            if len(str(min)) == 1:
                fill_min="0"
            datestring = str(year)+'-'+fill_month+str(month)+'-'+\
                         fill_day+str(day)+' '+fill_hour+str(hour)+':'+\
                         fill_min+str(min)
            print(datestring,',',T_forecast[k],',0,',Q_forecast[k], Q_err[k], file=csvfile)

## \fn write_output_files(fname, T_forecast, Q_compare, Q_forecast)
# write csv
# @param fname string filename
# @param T_forecast time domain
# @param Q_compare data, actual flux timeseries
# @param Q_forecast forecast
