#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: lucas
"""

from src.paths import *
import csv
from datetime import datetime
import warnings
import numpy as np
import pandas as pd

def find_run(date: datetime, in_folder: Path):
    """
    Finds run number by searching for date string.
    """

    subdirs = [x for x in in_folder.glob(f'*{date.strftime('%Y%m%d')}*') if x.is_dir()]

    if len(subdirs) < 1:
        raise FileNotFoundError(f'Found no directory with the date: {date.strftime('%Y%m%d')}.')
        return
    
    elif len(subdirs) > 1:
        raise ValueError(f'Found more than one directory with the date: {date.strftime('%Y%m%d')}.')
        return

    #returns "run_XXXXXXX"
    return subdirs[0].name[:11]

def check_data(t: list):
    """
    Checks that a list of times is at least close to sorted and last timestamp < 86400.
    """

    previous = t[0]
    for value in t:
        if previous - value > 1.0:
            raise ValueError('Times are not sorted.')
            return False
        
        previous = value
    
    if t[-1] > 86400:
        raise ValueError('Last timestamp > 86400.')
        return False
    
    return True
    

def pass1_icecube(date: datetime, in_folder: Path = ICECUBE_DATA_DIR, out_folder: Path = ICECUBE_PASS1_DIR):
    
    print('Starting pass 1 for IceCube script\n. . .')

    out_sub_folder = out_folder / f'{date.strftime('y%Ym%md%d')}-IceCube-pass1'
    out_sub_folder.mkdir(parents=True, exist_ok=True)

    run = find_run(date, in_folder)
    
    #finds the constant to subtract from times
    firsts = []
    for i in np.linspace(1, 8, 8, dtype = int):
        full_path = in_folder / f'{run}_{date.strftime('%Y%m%d')}' / run / f'{run}_chan-{i}_alldata.txt'
        with open(full_path, 'r') as f:
            firsts.append(float(next(f).split()[0])) #gets the first timestamp only
    
    constant = min(firsts)
    print(f'Found constant: {constant}')
    
    #checks that the times are sound and if they are, creates output csv
    #TODO stop using pandas and make this more efficient
    for i in np.linspace(1, 8, 8, dtype = int):
        full_path = in_folder / f'{run}_{date.strftime('%Y%m%d')}' / run / f'{run}_chan-{i}_alldata.txt'
        dfi = pd.read_csv(full_path, delimiter=' ', names=['time','ADC0','ADC2','ADC12','CPU_trigger','time/threshold'])
        ti = dfi['time'].values - constant
        
        try:
            check_data(ti)
        except ValueError:
            warnings.warn(f'Data for channel {i} has issues. Skipping this channel.')
            continue

            
    
        dfi['time'] = ti
        dfi.sort_values('time').to_csv(out_sub_folder / f'{date.strftime('y%Ym%md%d')}-IceCube-c{i}-pass1.csv', index=False)
        print(f'Made csv for channel {i}')
    
        del dfi
        
    print('Pass 1 IceCube done')
        
    return

def main():

    res = input('Use real or mock data? ("real" or "mock") : ')

    if res == 'mock':
        pass1_icecube(datetime(1, 1, 2), MOCK_ICECUBE_DATA_DIR, MOCK_ICECUBE_PASS1_DIR)

    elif res == 'real':
        date_str = input('Which date? (YYYYMMDD) : ')
        date = datetime.strptime(date_str, '%Y%m%d')
        
        pass1_icecube(date)

    else:
        raise ValueError('Not a valid response.')
        return

    return

if __name__ == '__main__': #only executes if script is run directly
    main()