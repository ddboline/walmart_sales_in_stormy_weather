#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Train model, test model, write out submission

@author: Daniel Boline <ddboline@gmail.com>
"""

import os
import gzip

import cPickle as pickle

import numpy as np

from sklearn.ensemble import RandomForestRegressor,\
                             GradientBoostingRegressor
from sklearn.cross_validation import train_test_split
from sklearn.metrics import mean_squared_error

from load_data import load_data

def transform_to_log(y):
    if any(y < 0):
        y[y < 0] = 0
    return np.log(y+1)

def transform_from_log(yl):
    return np.exp(yl)-1

def train_model_parallel(model, xtrain, ytrain, index=0, prefix=''):
    xTrain, xTest, yTrain, yTest = train_test_split(xtrain, 
                                                    transform_to_log(ytrain[:,
                                                                      index]),
                                                    test_size=0.12)
    model.fit(xTrain, yTrain)
    print 'score', model.score(xTest, yTest)
    ypred = model.predict(xTest)
    if any(ypred < 0):
        print ypred[ypred < 0]
        ypred[ypred < 0] = 0

    print 'RMSE', np.sqrt(mean_squared_error(ypred, yTest))
    with gzip.open('model%s%d.pkl.gz', 'wb') as pklfile:
        pickle.dump(model, pklfile, protocol=2)
    return

def my_model(xtrain, ytrain, xtest, ytest, index=0):
#    model = RandomForestRegressor(n_jobs=-1, n_estimators=100)
#    train_model_parallel(model, xtrain, ytrain, index, prefix='rf100')
    
    model = GradientBoostingRegressor(loss='ls', verbose=1, max_depth=7, 
                                      n_estimators=200)
    train_model_parallel(model, xtrain, ytrain, index, prefix='gbr200_7')

    
    return

if __name__ == '__main__':
    xtrain, ytrain, xtest, ytest, feature_list = load_data()

    index = -1
    for arg in os.sys.argv:
        try:
            index = int(arg)
            my_model(xtrain, ytrain, xtest, ytest)
        except:
            pass

