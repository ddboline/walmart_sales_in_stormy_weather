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
    with gzip.open('model_%s_%d.pkl.gz' % (prefix, index), 'wb') as pklfile:
        pickle.dump(model, pklfile, protocol=2)
    return

def test_model_parallel(xtrain, ytrain, prefix=''):
    xTrain, xTest, yTrain, yTest = train_test_split(xtrain, 
                                                    transform_to_log(ytrain),
                                                    test_size=0.12)
    RMSLE_VAL = []
    for index in range(111):
        with gzip.open('model_%s_%d.pkl.gz' % (prefix, index), 'rb') as pklfile:
            model = pickle.load(pklfile)
            ypred = model.predict(xTest)
            if any(ypred < 0):
                print ypred[ypred < 0]
                ypred[ypred < 0] = 0
            RMSLE_VAL.append(np.sqrt(mean_squared_error(ypred, 
                                                        yTest[:,index])))
    print np.mean(RMSLE_VAL)

def prepare_submission_parallel(xtrain, ytrain, xtest, ytest, prefix=''):
    for index in range(111):
        with gzip.open('model_%s_%d.pkl.gz' % (prefix, index), 'rb') as pklfile:
            model = pickle.load(pklfile)
            ylpred = model.predict(xtest)
            if any(ylpred < 0):
                print ylpred[ylpred < 0]
                ylpred[ylpred < 0] = 0
            ytest['units%d' % (index+1)] = transform_from_log(ylpred)\
                                            .astype(np.int64)
    ytest.to_csv('submit_full_%s.csv' % prefix, index=False)

def my_model(xtrain, ytrain, xtest, ytest, index=0):
    
    #model = RandomForestRegressor(n_jobs=-1, n_estimators=100)
    #train_model_parallel(model, xtrain, ytrain, index, prefix='rf100')
    
    model = GradientBoostingRegressor(loss='ls', verbose=1, max_depth=5, 
                                        n_estimators=100)
    train_model_parallel(model, xtrain, ytrain, index, prefix='gbr100_5')

    
    return

if __name__ == '__main__':
    xtrain, ytrain, xtest, ytest, feature_list = load_data()

    jobidx = -1
    for arg in os.sys.argv:
        try:
            jobidx = int(arg)
        except:
            continue
    if jobidx == -1:
        my_model(xtrain, ytrain, xtest, ytest, index=0)
    elif jobidx >=0 and jobidx < 10:
        for idx in range(jobidx*12,min(jobidx*12+12,111)):
            my_model(xtrain, ytrain, xtest, ytest, index=idx)
    elif jobidx == 10:
        test_model_parallel(xtrain, ytrain, prefix='rf100')
    elif jobidx == 11:
        pass
