#!/usr/bin/python

import matplotlib
matplotlib.use('Agg')
import pandas as pd
import numpy as np
import datetime
from dateutil.parser import parse

def clean_data(indf):
    """
    clean train/test dataframes
    """
    indf['date'] = indf['date'].apply(lambda x: (parse(x).date() 
                                      - datetime.date(year=2010, month=1, 
                                                      day=1)).days)
    for label in 'tmax', 'tmin', 'tavg', 'dewpoint', 'wetbulb':
        cond = indf[label].isnull()
        indf.loc[cond, label] = -400
        
    for label in 'heat', 'cool', 'snowfall', 'preciptotal', 'stnpressure',\
                 'sealevel', 'resultspeed', 'resultdir', 'avgspeed':
        cond = indf[label].isnull()
        indf.loc[cond, label] = -1
    
    return indf

def load_data(do_drop_list=False, do_plots=False):
    train_df = pd.read_csv('train_full.csv.gz', compression='gzip')
    test_df = pd.read_csv('test_full.csv.gz', compression='gzip')
    submit_df = pd.read_csv('sample_submit_full.csv.gz', compression='gzip')

    train_df = clean_data(train_df)
    test_df = clean_data(test_df)

#    print train_df.columns
#    print test_df.columns
    #print submit_df.columns

#    for col in train_df.columns:
#        if any(train_df[col].isnull()):
#            print col, train_df[col].dtype

    if do_plots:
        from plot_data import plot_data
        plot_data(train_df, prefix='html_train')
        plot_data(test_df, prefix='html_test')

    unitlist = ['units%d' % (idx+1) for idx in range(111)]

    ### wanted to keep track of feature_list
    feature_list = train_df.drop(['store_nbr', 'station_nbr']+unitlist, axis=1).columns
#    print 'features', list(feature_list)

    xtrain = train_df.drop(labels=['store_nbr', 'station_nbr']+unitlist, axis=1).values
    ytrain = train_df[unitlist].values
    xtest = test_df.drop(labels=['store_nbr', 'station_nbr'], axis=1).values
    ytest = submit_df

#    xtrain, ytrain, xtest, ytest, feature_list = 5*[None]
    return xtrain, ytrain, xtest, ytest, feature_list

if __name__ == '__main__':
    xtrain, ytrain, xtest, ytest, feature_list = load_data(do_plots=False)
    
    print [v.shape for v in xtrain, ytrain, xtest, ytest]
