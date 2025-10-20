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

print('Starting pass 1 for IceCube script\n. . .')

if len(sys.argv) > 1:
    directory = sys.argv[1]
    print(f'Received directory from command line: {directory}')
else:
    directory = input('In which directory is the IceCube data?')


if len(sys.argv) > 2:
    datestr = sys.argv[2]
    print(f'Received date from command line: {datestr}')
else:
    datestr = input('Which date? (enter in yyyymmdd):')

date = datetime.datetime(int(datestr[:4]), int(datestr[4:6]), int(datestr[6:]))

newfmtdate = f'y{date.strftime('%Y')}m{date.strftime('%m')}d{date.strftime('%d')}'

#finds the directory name that contains the chosen date
found = False
for file in os.listdir(directory):
    if datestr in file:
        if not found:
            datafolder = directory + os.sep + file
            run = file[4:11]
            found = True
            if not os.path.isdir(directory + os.sep + file):
                sys.exit('!!! Found a file containing the date but it is not a directory')
            print(f'Found directory containing {datestr} named {file}')
            
        else:
            sys.exit('!!! Found another file/directory containing the date')

if not found:
    sys.exit('!!! No file/directory found containing the date')

#creates output directory unless it already exists
if not os.path.exists(f'IceCube-pass1/{newfmtdate}-IceCube-pass1'):
    os.makedirs(f'IceCube-pass1/{newfmtdate}-IceCube-pass1')   

#function to check if times are close to being sorted
#to help verify that scintillator data is sound
def checksorted(t):
    previous = t[0]
    for value in t:
        if previous - value > 0.1:
            return False
        previous = value
    return True

#finds the constant to subtract from times
firsts = []
for i in np.linspace(1, 8, 8, dtype = int):
    path = f'{datafolder}/run_{run}/run_{run}_chan-{i}_alldata.txt'
    dfi = pd.read_csv(path, delimiter=' ', names=['time','ADC0','ADC2','ADC12','CPU_trigger','time/threshold'], nrows=1)
    firsts.append(dfi['time'][0])
    del dfi

constant = min(firsts)
print(f'Found constant: {constant}')

#checks that the times are sound and if they are, creates output csv
for i in np.linspace(1, 8, 8, dtype = int):
    path = f'{datafolder}/run_{run}/run_{run}_chan-{i}_alldata.txt'
    dfi = pd.read_csv(path, delimiter=' ', names=['time','ADC0','ADC2','ADC12','CPU_trigger','time/threshold'])
    ti = dfi['time'].values - constant
    if checksorted(ti):
        if ti[-1] < 86400:
            print(f'Channel {i} times are good')
        else:
            print(f'!!! Channel {i} times range greater than 86400')
            continue
    else:
        print(f'!!! Channel {i} times are not in ascending order')
        continue

    dfi['time'] = ti
    dfi.sort_values('time').to_csv(f'IceCube-pass1/{newfmtdate}-IceCube-pass1/{newfmtdate}-IceCube-c{i}-pass1.csv', index=False)
    print(f'Made csv for channel {i}')

    del dfi
    
print('Pass 1 IceCube done')
