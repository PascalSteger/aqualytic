#!/usr/bin/env python3

##
# @file

# predictors based on fourier analysis of a timeseries
import pdb
from pylab import *
from numpy.fft import rfft
from numpy.fft import irfft

def fourier_transform(data):
    arr = data
    arr1 = arr[1:]
    arr2 = arr[:-1]
    data_diff = arr1-arr2

    F = rfft(data_diff)
    #plot(range(len(F)), F)
    #show()
    pdb.set_trace()
    return F
## \fn fourier_transform(data)
# transform data to Fourier space
# @param data array


def fourier_invtrans(coeff):
    data = irrft(coeff)
    plot(range(len(coeff)), data)
    show()
    return data
## \fn fourier_invtrans(coeff)
# inverse fourier transformation
# @coeff as averaged, or not..


def wavelet_extrapolate(times, data):
    import pywt
    arr = [times, data]
    cA, cD = pywt.dwt2(arr, 'db2')
    pdb.set_trace()
    return forecast, cA, cD
## \fn wavelet_extrapolate(times, data)
# extrapolate with wavelets
# only working with python2.7
# @param times array
# @param data array to be fitted


def try_stuff():
    import pywt
    import matplotlib.pyplot as plt
    import numpy as np
    ts = [2, 56, 3, 22, 3, 4, 56, 7, 8, 9, 44, 23, 1, 4, 6, 2]
    (ca, cd) = pywt.dwt(ts,'haar')

    cat = pywt.thresholding.soft(ca, np.std(ca)/2)
    cdt = pywt.thresholding.soft(cd, np.std(cd)/2)

    ts_rec = pywt.idwt(cat, cdt, 'haar')

    subplot(211)
    # Original coefficients
    plot(ca, '--*b')
    plot(cd, '--*r')
    # Thresholded coefficients
    plot(cat, '--*c')
    plot(cdt, '--*m')
    legend(['ca','cd','ca_thresh', 'cd_thresh'], loc=0)
    grid('on')

    subplot(212)
    plot(ts)
    hold('on')
    plot(ts_rec, 'r')
    legend(['original signal', 'reconstructed signal'])
    grid('on')
    show()
## \fn try_stuff()
# plotting of pywt thresholding effect
