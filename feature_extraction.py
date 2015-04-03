#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Fri Apr  3 10:09:28 2015

@author: ddboline
"""

import gzip
import csv

from collections import OrderedDict

WEATHER_VARS_WITH_M_T = (u'tmax', u'tmin', u'tavg', u'depart', u'dewpoint', 
                         u'wetbulb', u'heat', u'cool', u'snowfall', 
                         u'preciptotal', u'stnpressure', u'sealevel', 
                         u'resultspeed', u'resultdir', u'avgspeed')

WEATHER_PHENOMENA = ('BCFG', 'BLDU', 'BLSN', 'BR', 'DU', 'DZ', 'FG', 'FG+', 
                     'FU', 'FZDZ', 'FZFG', 'FZRA', 'GR', 'GS', 'HZ', 'MIFG', 
                     'PL', 'PRFG', 'RA', 'SG', 'SN', 'SQ', 'TS', 'TSRA', 
                     'TSSN', 'UP', 'VCFG', 'VCTS')

def feature_extraction():
    weather_features = OrderedDict()
    weather_labels = []
    store_key_dict = {}
    
    with gzip.open('weather.csv.gz', 'r') as wfile:
        wcsv = csv.reader(wfile)
        weather_labels = next(wcsv)
        for row in wcsv:
            rowdict = OrderedDict(zip(weather_labels, row))
            for k in WEATHER_VARS_WITH_M_T:
                if k in rowdict:
                    rowdict[k] = rowdict[k].replace('M', 'nan')
                    rowdict[k] = rowdict[k].replace('T', '0.0')
            for k in rowdict:
                if rowdict[k] == '-':
                    rowdict[k] = 'nan'
                rowdict[k] = rowdict[k].strip()
            for ph in WEATHER_PHENOMENA:
                rowdict['wp%s' % ph] = '0'
            for ph in rowdict['codesum'].split():
                if ph in WEATHER_PHENOMENA:
                    rowdict['wp%s' % ph] = '1'
            key = '%s_%s' % (rowdict['station_nbr'], rowdict['date'])
            weather_features[key] = rowdict
    for k in ('date', 'depart', 'sunrise', 'sunset', 'codesum'):
        weather_labels.remove(k)
    for ph in WEATHER_PHENOMENA:
        weather_labels.append('wp%s' % ph)
    with gzip.open('key.csv.gz', 'r') as kfile:
        next(kfile)
        for line in kfile:
            store_nbr, station_nbr = [x.strip() for x in line.split(',')]
            store_key_dict[store_nbr] = station_nbr
    
    for prefix in 'train','test':
        outfile = gzip.open('%s_full.csv.gz' % prefix, 'w')
        with gzip.open('%s.csv.gz' % prefix, 'r') as csvfile:
            csv_reader = csv.reader(csvfile)
            labels = next(csv_reader)

            labels_to_keep = ['date', 'store_nbr']
            if prefix == 'train':
                for idx in range(111):
                    labels_to_keep.append('units%s' % (idx+1))

            csv_writer = csv.writer(outfile)
            csv_writer.writerow(labels_to_keep+weather_labels)
            
            current_row = {k: None for k in labels_to_keep}            
            
            for n, row in enumerate(csv_reader):
                if n % 100000 == 0:
                    print n, 'complete'
                rowdict = OrderedDict(zip(labels, row))
                
                if current_row['date'] != rowdict['date'] or\
                   current_row['store_nbr'] != rowdict['store_nbr']:

                    if current_row['date'] != None:
                        station_nbr = store_key_dict[current_row['store_nbr']]
                        key = '%s_%s' % (station_nbr, current_row['date'])
                        outrow = []
                        for label in labels_to_keep:
                            outrow.append(current_row[label])
                        for label in weather_labels:
                            outrow.append(weather_features[key][label])
                        csv_writer.writerow(outrow)
                    for label in 'date', 'store_nbr':
                        current_row[label] = rowdict[label]
                if 'units' in rowdict:
                    k = 'units%s' % rowdict['item_nbr']
                    current_row[k] = rowdict['units']

        outfile.close()
    return

def convert_sample_submission():
    outfile = gzip.open('sample_submit_full.csv.gz', 'wb')
    with gzip.open('sampleSubmission.csv.gz', 'rb') as csvfile:
        csv_reader = csv.reader(csvfile)
        labels = next(csv_reader)
        output_labels = ['date', 'store_nbr']
        for idx in range(111):
            output_labels.append('units%d' % (idx+1))
        
        csv_writer = csv.writer(outfile)
        csv_writer.writerow(output_labels)
        
        current_row = {k: None for k in output_labels}        
        
        for n, row in enumerate(csv_reader):
            if n % 100000 == 0:
                print n, 'complete'

            rowdict = OrderedDict(zip(labels, row))
            
            store_nbr, item_nbr, date = rowdict['id'].split('_')
            
            if current_row['date'] != date or\
               current_row['store_nbr'] != store_nbr:
                
                if current_row['date'] != None:
                    outrow = []
                    for label in output_labels:
                        outrow.append(current_row[label])
                    csv_writer.writerow(outrow)
                
                current_row['date'] = date
                current_row['store_nbr'] = store_nbr
            k = 'units%s' % item_nbr
            current_row[k] = rowdict['units']


if __name__ == '__main__':
#    feature_extraction()
    convert_sample_submission()