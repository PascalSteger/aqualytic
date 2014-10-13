#!/usr/bin/env python3
import pdb
import numpy as np

## Load files
import csv

# load from csv file with NaNs
P_Dec_ERA40 = np.genfromtxt("data/data_P_Dec_ERA40.csv", skiprows=1, unpack=False, delimiter=',', filling_values=-1)
P_Dec_ERAint = np.genfromtxt("data/data_P_Dec_ERAint.csv", skiprows=1, unpack=False, delimiter=',', filling_values=-1)

P_Dec_MetStations = np.genfromtxt("data/data_P_Dec_MetStations.csv", skiprows=1, unpack=False, delimiter=',', filling_values=-1)
P_Mon_MetStations = np.genfromtxt("data/data_P_Mon_MetStations.csv", skiprows=1, unpack=False, delimiter=',', filling_values=-1)
Q_Dec = np.genfromtxt("data/data_Q_Dec.csv", skiprows=1, unpack=False, delimiter=',', filling_values=-1)
Q_Mon = np.genfromtxt("data/data_Q_Mon.csv", skiprows=1, unpack=False, delimiter=',', filling_values=-1)

T_Dec_ERA_All = np.genfromtxt("data/data_T_Dec_ERA_All.csv", skiprows=1, unpack=False, delimiter=',', filling_values=-1)
T_Mon_ERA_All = np.genfromtxt("data/data_T_Mon_ERA_All.csv", skiprows=1, unpack=False, delimiter=',', filling_values=-1)
