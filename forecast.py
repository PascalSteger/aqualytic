#!/usr/bin/env python3

##
# @file
# Forecast of Water Levels in Central Asia using a diverse set of forecast methods:
# - annual mean in lin/log space, with and without sliding window with weights
# - spline extrapolation
# - Fourier Transform
# - Neural Network based on last season and last precipitation / temperature data

# (c) GPL v.3 Pascal S.P. Steger, psteger@phys.ethz.ch
# original idea: Tobias Siegfried, 21 / 05 / 2014

## output verbosity
DEBUGLEVEL = 3

import pdb, os
import numpy as np
# for advanced timestamp and timeseries handling: use pandas
import pandas as pd
from scipy.interpolate import splrep, splev
import matplotlib
matplotlib.use('tkagg')
from pylab import *

import gl_helper as gh
import gl_file
import fc_fourier

if __name__ == "__main__":
    ## use commandline parameters for most common specifications
    import gl_params as gp
    N, iRiver, riverName, method, showerror = gp.parse_options()

    ### get data
    import gl_data as data

    # Process river that will be run through the forecast
    # if gp.fcT == 'decadal':
    #     tRiver = data.Q_Dec[:, 0]
    #     qRiver = gp.fill_longterm(tRiver, data.Q_Dec[:, iRiver+1])
    #     pRiver = gp.fill_longterm(tRiver, data.P_Dec_ERA40[:, iRiver+1])
    #     TRiver = gp.fill_longterm(tRiver, data.T_Dec_ERA_All[:, iRiver+1])
    # elif gp.fcT == 'monthly':
    #     tRiver = data.Q_Mon[:, 0]
    #     qRiver = gp.fill_longterm(tRiver, data.Q_Mon[:, iRiver+1])
    #     pRiver = np.zeros(len(tRiver))
    #     # TODO get data, then fill_longterm(data.P_Mon_ERA40[:, iRiver+1])
    #     TRiver = gp.fill_longterm(tRiver, data.T_Mon_ERA_All[:, iRiver+1])


    # better: read in all data via pandas
    datqdec = pd.read_csv('data/data_Q_Dec.csv')
    datpdec = pd.read_csv('data/data_P_Dec_ERA40.csv')
    datpdecint = pd.read_csv('data/data_P_Dec_ERAint.csv')
    dattdec = pd.read_csv('data/data_T_Dec_ERA_All.csv')

    datqmon = pd.read_csv('data/data_Q_Mon.csv')
    dattmon = pd.read_csv('data/data_T_Mon_ERA_All.csv')

    datmetpdec = pd.read_csv("data/data_P_Dec_MetStations.csv")
    datmetpmon = pd.read_csv("data/data_P_Mon_MetStations.csv")

    # TODO convert each timestamp in the above datasets
    ipdb.set_trace()
    dataqdec = gh.convert_timestamps(datqdec)


    ### calculate allowable error according to Andrey
    if gp.fcT == 'decadal':
        diffMat = [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],\
                   [],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
    elif gp.fcT == 'monthly':
        diffMat = [[],[],[],[],[],[],[],[],[],[],[],[]]
    for k in range(1, len(tRiver)):
        diffMat[int(tRiver[k]/(365.25/gp.nDecY))%gp.nDecY].append(qRiver[k]-qRiver[k-1])
    allowableError = np.zeros(gp.nDecY)
    for k in range(gp.nDecY):
        allowableError[k] = 0.674*np.nanstd(np.abs(diffMat[k]))

    def nanzscore(val):
        valWithoutNaNs = val[1-np.isnan(val)]
        valMean = np.nanmean(valWithoutNaNs)
        valSD = np.nanstd(valWithoutNaNs)
        valZscore = (val-valMean)/valSD
        return valZscore
    ## \fn nanzscore(val)
    # get zscore for vector with many NaN entries
    # @param val value vector

    # identify temperature / precipitation time series with highest x-correlation of runoff for use in
    # regression
    if gp.fcT == 'decadal':
        X = nanzscore(data.Q_Dec[:,1:])
        Y1 = nanzscore(data.P_Dec_MetStations[:,1:])
        Y1[np.isnan(Y1)] = 0
        Y2 = nanzscore(data.T_Dec_ERA_All[:,1:])
        Y2[np.isnan(Y2)] = 0
    elif gp.fcT == 'monthly':
        X = nanzscore(data.Q_Mon[:,1:])
        Y1 = nanzscore(data.P_Mon_MetStations[:,1:])
        Y1[np.isnan(Y1)] = 0
        Y2 = nanzscore(data.T_Mon_ERA_All[:,1:])
        Y2[np.isnan(Y2)] = 0


    ### main forecast functionality
    # TODO training set newly specified in gl_data
    T_start = min(tRiver)+365.25*N
    T_end   = max(tRiver)
    T_forecast = tRiver[(tRiver >= T_start)*(tRiver <= T_end)]
    Q_compare  = qRiver[(tRiver >= T_start)*(tRiver <= T_end)]

    Q_forecast = []
    for t in T_forecast:
        # the first few methods rely on annual repetitions, thus, we use
        # a buffer to store Tue 16th last year, two years back,... in qBase
        qBase = []; qTime = []
        for k in range(1, N+1):
            idxstart=np.argmin(np.abs(tRiver - (t-k*365.25)))
            qBase.append(qRiver[idxstart])
            qTime.append(tRiver[idxstart])
        # put in correct temporal order to get splines fine in the end
        qBase = qBase[::-1]; qTime = qTime[::-1]
        if method == 1:
            # create mean of previous years
            Q_forecast.append(np.mean(qBase))
        elif method == 2:
            # create exp(mean of log values for years)
            Q_forecast.append(np.exp(np.mean(np.log(qBase))))
        elif method == 3:
            # create weighted mean, with exponentially decaying window
            w = np.exp((1-np.arange(1, N+1)))#/N) # uncommented: make it less strict
            Q_forecast.append(np.average(qBase, weights=w))
        elif method == 4:
            # weighted mean, exp decaying window, on log values
            w = np.exp((1-np.arange(1, N+1)))
            Q_forecast.append(np.exp(np.average(np.log(qBase), weights=w)))
        elif method == 5:
            # use spline interpolation to capture trend
            # need at least k=2 for spline, thus at least N = 4
            tck = splrep(qTime, qBase, k=1, s=0.1)
            Q_forecast.append(splev(t, tck))
        elif method == 6:
            # same, but in log space for q
            tck = splrep(qTime, np.log(qBase), k=1, s=0.1)
            Q_forecast.append(np.exp(splev(t, tck)))


    for t in T_forecast:
        # for all the following methods, we need only the last N data entries
        # use decadal data if possible
        qBase = []; tBase = []
        # index where "today" lies:
        idxstart = np.argmin(np.abs(tRiver-t))
        qBase = qRiver[idxstart-N:idxstart]
        tBase = tRiver[idxstart-N:idxstart]
        for j in range(len(qBase)):
            if np.isnan(qBase[j]):
                qBase[j]=0
        if method == 7:
            # prediction with splines order 1 in lin space
            # only use for short-term prediction
            # need at least N=4, bad offset
            # NO GOOD ON monthly DATA
            tck = splrep(tBase[-N:-2], qBase[-N:-2], k=1, s=0.1)
            Q_forecast.append(splev(tBase[-1], tck))
        elif method == 8:
            # prediction with splines order 1 in log space
            # only use for short-term prediction
            # NO GOOD ON monthly DATA
            tck = splrep(tBase[-N:-2], np.log(qBase[-N:-2]), k=1, s=0.1)
            Q_forecast.append(np.exp(splev(tBase[-1], tck)))
        elif method == 9:
            # prediction with splines order 2 in lin space
            # only use for up to medium-term prediction
            # NO GOOD ON monthly DATA
            tck = splrep(tBase[-N:-2], qBase[-N:-2], k=2, s=0.1)
            Q_forecast.append(splev(tBase[-1], tck))
        elif method == 10:
            # prediction with splines order 2 in log space
            # only use for up to medium-term prediction
            # NO GOOD ON MONTHLY DATA
            tck = splrep(tBase[-N:-2], np.log(qBase[-N:-2]), k=2, s=0.1)
            Q_forecast.append(np.exp(splev(tBase[-1], tck)))
        elif method == 11:
            # prediction based on wavelet modes, only possible with python2.7!
            Q_forecast, cA, cW = fc_fourier.wavelet_extrapolate(tRiver, qRiver, T_forecast)
        elif method == 12:
            qBase = []
            # prediction based on polynomial extension of rfftw parameters
            for k in range(1, N+1):
                idxstart = np.argmin(np.abs(tRiver-(t-k*365.25)))
                idxstop  = np.argmin(np.abs(tRiver-(t-(k-1)*365.25)))
                # qBase holds Fourier coefficients, year-wise
                qRdata = qRiver[idxstart:idxstop]
                for j in range(len(qRdata)):
                    if np.isnan(qRdata[j]):
                        # fill up NaN values from later data
                        qRdata[j] = qRiver[idxstop+j]
                        if np.isnan(qRdata[j]): qRdata[j]=0
                qBase.append(fc_fourier.fourier_transform(qRdata))
            # now need to average them, and invert to get actual data
            av_coeff = np.mean(qBase)
            Q_forecast = fc_fourier.fourier_invtrans(av_coeff)

    # test data (Jan. 1993 - Dec. 2002)
    tS = 1993*365.25+1*30+5
    tE = 2002*365.25+12*30+25


    if method == 13:
        # use neural network on training set consisting of all entries for this river,
        # all current and last values for all other rivers,
        # snow status, temperature, and precipitation on last 6 months
        sel=(tRiver < tS) # select training data TODO specified in gl_data
        import json
        json.dumps(tRiver[sel].tolist())
        json.dump(tRiver[sel].tolist(), open('output/tRiver.json', 'w'))
        json.dump(qRiver[sel].tolist(), open("output/qRiver.json", "w"))
        json.dump(pRiver[sel].tolist(), open("output/pRiver.json", "w"))
        json.dump(TRiver[sel].tolist(), open("output/TRiver.json", "w"))
        qnewRiver = qRiver[(tRiver>tS)*(tRiver<tE)] # select data in range for testing
        pnewRiver = pRiver[(tRiver>tS)*(tRiver<tE)]
        TnewRiver = TRiver[(tRiver>tS)*(tRiver<tE)]
        json.dump(qnewRiver.tolist(), open("output/qnewRiver.json", "w"))
        json.dump(pnewRiver.tolist(), open("output/pnewRiver.json", "w"))
        json.dump(TnewRiver.tolist(), open("output/TnewRiver.json", "w"))
        os.system('python2.7 nn.py')
        #replaces : predict = nn.NeuralNetwork(tRiver, qRiver, pRiver, TRiver, qnewRiver)
        prediction = np.array(json.load(open("output/prediction.json", "r")))

    Q_forecast = np.array(Q_forecast)
    gh.LOG(1,'FORECASTING DONE!')

    ## Evaluation
    sel = (T_forecast > tS)*(T_forecast < tE)
    Q_compare = Q_compare[sel]
    Q_forecast = Q_forecast[sel]
    T_forecast = T_forecast[sel]

    err = Q_compare - Q_forecast

    # basic visualization
    figure(11)
    ax1=subplot(311)
    plot(T_forecast, Q_forecast, 'r+-', label='forecast')
    plot(T_forecast, Q_compare,  'k+-', label='observation')
    legend(loc='upper right')
    ylim([0, 1.5*max(Q_compare)])
    ylabel('decadal runoff [m^3/s]')

    # nicely spaced ticks
    years = np.arange(np.floor(min(T_forecast/365.25)),\
                     np.floor(max(T_forecast/365.25))+1)
    strings = years
    for k in range(len(strings)):
        strings[k] = str(int(strings[k]))
    setp( ax1.get_xticklabels(), visible=False)

    ax2=subplot(312, sharex=ax1)
    plot(T_forecast, err)
    ylim([-max(Q_compare)/2, max(Q_compare)/2])
    xlabel('year')
    ylabel('diff. obs & fc [m^3/s]')
    ax2.set_xticks(years*365.25)
    ax2.set_xticklabels(years)
    for label in ax2.get_xticklabels():
        label.set_rotation(45)

    ax3=subplot(313)
    plot(np.array(np.arange(len(allowableError))), -np.abs(allowableError),'b.-')
    plot(np.array(np.arange(len(allowableError))),  np.abs(allowableError), 'b.-')
    if gp.fcT == 'decadal':
        errby = [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],\
                 [],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
    elif gp.fcT == 'monthly':
        errby = [[],[],[],[],[],[],[],[],[],[],[],[]]

    for k in range(len(T_forecast)):
        errby[int(T_forecast[k]/(365.25/gp.nDecY)%gp.nDecY)].append(Q_forecast[k]-Q_compare[k])

    for k in range(len(errby)):
        el = len(errby[k])
        scatter(np.ones(el)*k, np.array(errby[k]), c='k')
    xlabel('decade')
    ylabel('forecast error [m^3/s]')
    xlim([1, gp.nDecY])

    errMAE = np.nanmean(np.abs(err))

    def nanrms(x, axis=None):
        return sqrt(np.nanmean(x**2, axis=axis))
    ## \fn nanrms(x, axis)
    # calculate root mean square from data with spurious NaN
    # @param x data
    # @param axis dimension

    errRMS = nanrms(err)
    errMSE = np.nanmean(err**2)


    gh.LOG(1,'Error Metrics')
    gh.LOG(1,'=============')
    gh.LOG(1, 'MAE: ', errMAE)
    gh.LOG(1, 'RMS: ', errRMS)
    gh.LOG(1, 'MSE: ', errMSE)

    # long-term
    fcQualityAndrey = np.nanstd(err) / np.nanstd(qRiver)
    gh.LOG(1, 'FQC: ', fcQualityAndrey)

    if gp.fcT == 'decadal':
        fcstr = ' - Decadal Forecast'
    elif gp.fcT == 'monthly':
        fcstr = ' - Monthly Forecast'
    elif gp.fcT == 'seasonal':
        fcstr = ' - Seasonal Forecast'

    suptitle(riverName + ' '+ fcstr+',\n'+\
             ' method '+str(method) + ', based on last '+str(N)+' years\n' +
             'MAE: ' + str(errMAE) + ',   RMS: ' + str(errRMS) + \
             ',   MSE: ' + str(errMSE) + ',   FQC: ' + str(fcQualityAndrey))

    # output files
    fname = 'output/'+gp.fcT+'_png/forecast_river_'+str(iRiver)+'_method_'+str(method)+'_N_'+str(N)+'.png'
    savefig(fname)

    # write csv file so we can plot it differently
    fname = 'output/'+gp.fcT+'_csv/forecast_river_'+str(iRiver)+'_method_'+str(method)+'_N_'+str(N)+'.csv'
    gl_file.write_output_files(fname, T_forecast, Q_compare, Q_forecast)
    show() # turn on on-the-fly-visualization
