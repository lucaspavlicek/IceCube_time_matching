#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: lucas
"""

import sys
import os
import datetime
import numpy as np
import pandas as pd

print('Starting pass 2 for IceCube script\n. . .')

if len(sys.argv) > 1:
    datestr = sys.argv[1]
    print('Received date from command line:', datestr)
else:
    datestr = input('Which date? (enter in yyyymmdd):')

date = datetime.datetime(int(datestr[:4]), int(datestr[4:6]), int(datestr[6:]))

newfmtdate = 'y'+date.strftime('%Y')+'m'+date.strftime('%m')+'d'+date.strftime('%d')

def ncomparison(times, threshold):
    n = len(times)
    
    i = np.zeros(n, dtype=int)
    
    indices = np.zeros((1, n), dtype=int)

    done = False
    while not done:

        smallest = np.argmin([times[j][i[j]] for j in range(n)])
        minn = times[smallest][i[smallest]]
        maxx = max([times[j][i[j]] for j in range(n)])

        if maxx - minn < threshold:
            I = np.zeros(n, dtype=int)
            for j in range(n):
                while times[j][i[j] + I[j]] - times[j][i[j]] < 2*threshold:
                    I[j] += 1
        
            indexer = np.zeros(I, dtype=int)
            for J, _ in np.ndenumerate(indexer):

                mminn = min([times[j][i[j] + J[j]] for j in range(n)])
                mmaxx = max([times[j][i[j] + J[j]] for j in range(n)])

                if mmaxx - mminn < threshold:
                    indices = np.append(indices, (i + J)[np.newaxis], axis = 0)

                for j in range(n):
                    i[j] += 1

        else:
            i[smallest] += 1
        
        for j in range(n):
            if i[j] == len(times[j]):
                print('done')
                done = True

    return indices[1:]


def createoutput(i, sds, outputpath):
    output = pd.DataFrame()
    matchtimes = np.zeros((len(i), len(sds)))

    for j in range(len(sds)):
        path = 'IceCube-pass1/'+newfmtdate+'-IceCube-pass1/'+newfmtdate+'-IceCube-c'+str(sds[j])+'-pass1.csv'
        dfj = pd.read_csv(path)
        matchtimes[:, j] = dfj['time'].values[i[:, j]]
        c = 'c'+str(sds[j])
        
        output[c+'_index'] = i[:, j]
        del dfj, c

    output['avg_time'] = np.mean(matchtimes, axis=1)
    output.to_csv(outputpath, index=False)

#creates output directory unless it already exists
if not os.path.exists('IceCube-pass2/'+newfmtdate+'-IceCube-pass2'):
    os.makedirs('IceCube-pass2/'+newfmtdate+'-IceCube-pass2')   

t = ()
validsds = []

for i in np.linspace(1, 8, 8, dtype = int):
    path = 'IceCube-pass1/'+newfmtdate+'-IceCube-pass1/'+newfmtdate+'-IceCube-c'+str(i)+'-pass1.csv'
    if os.path.exists(path):
        validsds.append(i)

if len(validsds) < 3:
    print('Found IceCube data for channels', validsds)
    sys.exit('!!! Not enough channels of IceCube data were found')

for i in validsds:
    path = 'IceCube-pass1/'+newfmtdate+'-IceCube-pass1/'+newfmtdate+'-IceCube-c'+str(i)+'-pass1.csv'
    dfi = pd.read_csv(path)
    ti = dfi['time'].values
    t += (ti, )
    del dfi

print('Found IceCube data for channels', validsds, '. Finding coincidences\n. . .')
matchindices = ncomparison(t, 0.0001)

print('Coincidences found. Creating output\n. . .')
createoutput(matchindices, validsds, 'IceCube-pass2/'+newfmtdate+'-IceCube-pass2/'+newfmtdate+'-IceCube-pass2.csv')

print('Pass 2 IceCube done')
