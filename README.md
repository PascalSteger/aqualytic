Aqualytic
=========

This hack aims to

1) predict the runoff rates at several points in the river network in central Asia with machine learning

2) present the forecasts with geo-tagged information in a browser

The main functionality is found in forecast.py. The data which the timeseries prediction uses is found in subdirectory data/.

Requirements
------------
You need following python packages installed:
- python3, any version is fine
- numpy and scipy
- matplotlib
- MultiNest and pymultinest
- pywavelets

Syntax
------
Call

>  ./forecast.py --help

to see a list of supported options.


Batch processing
----------------

Call

>  for i in $(seq 0 8); do ./forecast.py -N 3 -m 2 -R $i; done

to run all rivers with the current settings for N_year = 10 and forecast method 2.

and a more complicated

>  for m in $(seq 1 4); do for N in $(seq 1 10); do for r in $(seq 0 8); do ./forecast.py -N $N -m $m -R $r; done; done; done

to cycle through all possible combinations.


Documentation
-------------

An overview on motivation and methodology of the project can be found on the Wiki on github, see button to the right.
A more technical documentation of each function is available in the doc/html folder. To rebuild, execute

doxygen Doxyfile



For bugs and feature request, contact
Pascal Steger, psteger@phys.ethz.ch
