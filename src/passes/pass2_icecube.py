#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: lucas
"""

import sys
import os
from datetime import datetime
import numpy as np
import pandas as pd

from src.paths import *

#TODO: move the helper functions outside.
def pass2_icecube(date: datetime, in_folder: Path = ICECUBE_PASS1_DIR, out_folder: Path = ICECUBE_PASS2_DIR):

    print('Starting pass 2 for IceCube script\n. . .')
    
    new_fmt_date = date.strftime('y%Ym%md%d')
    
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
    
    
    def createoutput(i, sds, out_path):
        output = pd.DataFrame()
        matchtimes = np.zeros((len(i), len(sds)))
    
        for j in range(len(sds)):
            path = in_folder / f'{new_fmt_date}-IceCube-pass1' / f'{new_fmt_date}-IceCube-c{sds[j]}-pass1.csv'
            dfj = pd.read_csv(path)
            matchtimes[:, j] = dfj['time'].values[i[:, j]]
            c = f'c{sds[j]}'
            
            output[f'{c}_index'] = i[:, j]
            del dfj, c
    
        output['avg_time'] = np.mean(matchtimes, axis=1)
        output.to_csv(out_path, index=False)
    
    #creates output directory unless it already exists

    out_sub_folder = out_folder / f'{new_fmt_date}-IceCube-pass2'
    out_sub_folder.mkdir(parents=True, exist_ok=True)  
    
    t = ()
    validsds = []
    
    for i in np.linspace(1, 8, 8, dtype = int):
        path = in_folder / f'{new_fmt_date}-IceCube-pass1' / f'{new_fmt_date}-IceCube-c{i}-pass1.csv'
        if os.path.exists(path):
            validsds.append(i)
    
    if len(validsds) < 3:
        print(f'Found IceCube data for channels {validsds}')
        sys.exit('!!! Not enough channels of IceCube data were found')
    
    for i in validsds:
        path = in_folder / f'{new_fmt_date}-IceCube-pass1' / f'{new_fmt_date}-IceCube-c{i}-pass1.csv'
        dfi = pd.read_csv(path)
        ti = dfi['time'].values
        t += (ti, )
        del dfi
    
    print(f'Found IceCube data for channels {validsds}. Finding coincidences\n. . .')
    matchindices = ncomparison(t, 0.0001)
    
    print('Coincidences found. Creating output\n. . .')
    createoutput(matchindices, validsds, out_sub_folder / f'{new_fmt_date}-IceCube-pass2.csv')
    
    print('Pass 2 IceCube done')

    return

def main():

    res = input('Use real or mock data? ("real" or "mock") : ')

    if res == 'mock':
        pass2_icecube(datetime(1, 1, 2), MOCK_ICECUBE_PASS1_DIR, MOCK_ICECUBE_PASS2_DIR)

    elif res == 'real':
        date_str = input('Which date? (YYYYMMDD) : ')
        date = datetime.strptime(date_str, '%Y%m%d')
        
        pass2_icecube(date)

    else:
        raise ValueError('Not a valid response.')
        return

    return

if __name__ == '__main__': #only executes if script is run directly
    main()