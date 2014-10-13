#!/usr/bin/env python3


##
# @file
# MAJOR OPTIONS

import numpy as np

# RIVER SELECTION

adjRiv = True   # boolean
metS = True     # boolean
ERA_T = True    # boolean
ERAint_P = True # boolean
overlayType1 = '1111' # choice vector - type manually!
lags = [1,2,3] # this is for adjRiv if one wants to also use lagged values of these time series
nOverlays = [2,2,2,2] # Vector with corresponding numbers of highest correlated timeseries to consider
# (applies to corresponding overlays).

# TIME SERIES PREPROCESSING
nonSeasSeasDiff = 0

# FORECAST TYPE
fcT = 'monthly' ## forecastType: options: 'decadal', monthly' or 'seasonal'

# GAP FILLING
gapFill = 0

# LAGS
minLag = 1

# TRAINING AND TEST SETS
if fcT == 'decadal':
    nDecY = 36
    # TODO timestamp with pandas
    trainS = [1936,1,5]
    trainE = [1992,12,25]
    testS = [1993,1,5]
    testE = [2002,12,25]
    currentT = [1992,12,25]
    fcLength = 1;
elif fcT == 'monthly':
    nDecY = 12
    trainS = [1936,1,15]
    trainE = [1992,12,15]
    testS = [1993,1,15]
    testE = [2002,12,15]
    currentT = [1992,12,15]
    fcLength = 1;
elif fcT == 'seasonal':
    fcLength = 18;
else:
    error('wrong forecasting type');

def assign_rivername(iRiver):
    if iRiver == 0:
        riverName = 'akSuu'
    elif iRiver == 1:
        riverName = 'alaArcha'
    elif iRiver == 2:
        riverName = 'Alamedin'
    elif iRiver == 3:
        riverName = 'ChonKayindi'
    elif iRiver == 4:
        riverName = 'ChonKemin'
    elif iRiver == 5:
        riverName = 'KaraBalta'
    elif iRiver == 6:
        riverName = 'Kegety'
    elif iRiver == 7:
        riverName = 'Kochkor'
    elif iRiver == 8:
        riverName = 'Sokuluk'
    else:
        raise Exception('iRiver out of bounds')
    return riverName
## \fn assign_rivername(iRiver)
# Assign riverName with iRiver value
# @param iRiver


def parse_options():
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-N", "--knowledgebase", dest="N",
                      default=1, help="knowledgebase in years, or knowledgebase in length of bins before time to be forecasted")
    parser.add_option("-m", "--method", dest="method",
                      default=1, help="method for forecasting:\n1: use mean of N last data,\n 2: use mean in log space of N last data,\n 3: use weighted average of N last data,\n 4: use weighted average in log space of N last data,\n 5: use linear yearly sparsed spline to extrapolate,\n 6: use linear yearly sparsed spline in log space,\n \n 7: use lin spline on N last points of order 1,\n 8: same in log space,\n 9: use lin spline on N last points of order 2,\n 10: same in log space,\n 11: wavelets (only in python2),\n 12: real Fast Fourier Transformation averaged over N years\n 13: neural network.")
    parser.add_option("-R", "--river", dest="iRiver",
                      default=1, help="river to predict")
    parser.add_option("-e", "--error", help='show error', dest =
                      'showerror', default = True, action = 'store_true')
    (options, args) = parser.parse_args()

    N = int(options.N)
    iRiver = int(options.iRiver)
    riverName = assign_rivername(iRiver)
    print('River ', riverName)
    method = int(options.method)
    showerror = options.showerror
    return N, iRiver, riverName, method, showerror
## \fn parse_options()
# read commandline arguments, return their values


def fill_longterm(tvec, qvec):
    # get long-term average from non-NaN values
    ## binning
    if fcT == 'decadal':
        bins = [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],\
                [],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
    elif fcT == 'monthly':
        bins = [[],[],[],[],[],[],[],[],[],[],[],[]]

    for k in range(len(tvec)):
        idx = int(tvec[k]/(365.25/nDecY))%nDecY
        bins[idx].append(qvec[k])

    for k in range(len(bins)):
        bins[k] = np.nanmean(bins[k])
    # replace NaN with their respective long-term average
    for k in range(len(tvec)):
        if np.isnan(qvec[k]):
            idx = int(tvec[k]/(365.25/nDecY))%nDecY
            qvec[k] = bins[idx]
    return qvec
## \fn fill_longterm(vec)
# replace NaN (no measurement) with longterm mean values of corresponding time in year
