#!/usr/bin/env python2.7

##
# @file

# set up neural network and fill it with data
# as pybrain has not yet a stable version for python3, we are using pytho2 here,
# and need to read in the data that was previously stored by the main program

import numpy as np
from pybrain.tools.shortcuts import buildNetwork
from pybrain.structure import TanhLayer
from pybrain.datasets import SupervisedDataSet
from pybrain.supervised.trainers import BackpropTrainer

def NeuralNetwork(tRiver, qRiver, pRiver, TRiver, qnewRiver, pnewRiver, TnewRiver):
    # build neural network with 20 neurons for historic data on flux, 3 for last 3 temp data, 3 for last precipitation,
    # hidden layer with more than input neurons (hinder specification)
    # and 3 output neurons (flux for next day, first derivative, second derivative

    Ndim = 10+3+3
    Nout = 3
    net = buildNetwork(Ndim, Ndim, Nout, hiddenclass=TanhLayer)
    ds = SupervisedDataSet(Ndim, Nout)

    # next big job: find data values to build up library of training set
    for t in range(len(tRiver)-3):
        input_flow = qRiver[t-20:2:t]
        input_prec = pRiver[t-3:t]
        input_temp = TRiver[t-3:t]
        input_vec = np.hstack([input_flow, input_prec, input_temp])

        output_flow = np.hstack([qRiver[t:t+3]]) # first approx, split later for long predictions
        ds.addSample(input_vec, output_flow)

    trainer = BackpropTrainer(net, ds)
    #trainer.train()
    trainer.trainUntilConvergence()

    # now call it repeatedly on the second set

    prediction = net.activate(np.hstack([qnewRiver[:20], pnewRiver[:3], TnewRiver[:3]]))
    return prediction
## \fn NeuralNetwork(tRiver, qRiver, pRiver, TRiver, qnewRiver)
# build and train a NeuralNetwork, then apply to new data for prediction
# @param tRiver array of all training data timestamps
# @param qRiver array of all training flow data
# @param pRiver array of all training precipitation data
# @param TRiver array of all training temperature data
# @param qnewRiver array of untrained data, where application happens

if __name__=="__main__":
    import json
    tRiver=np.array(json.load( open("output/tRiver.json", "r")))
    qRiver=np.array(json.load( open('output/qRiver.json', 'r')))
    pRiver=np.array(json.load( open('output/pRiver.json', 'r')))
    TRiver=np.array(json.load( open('output/TRiver.json', 'r')))
    qnewRiver=np.array(json.load(open('output/qnewRiver.json', 'r')))
    pnewRiver=np.array(json.load(open('output/pnewRiver.json', 'r')))
    TnewRiver=np.array(json.load(open('output/TnewRiver.json', 'r')))
    prediction = NeuralNetwork(tRiver, qRiver, pRiver, TRiver, qnewRiver, pnewRiver, TnewRiver)
    json.dump(prediction.tolist(), open('output/prediction.json', 'w'))
