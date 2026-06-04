#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 24 22:48:51 2026

@author: lucaspavlicek
"""

import csv
from datetime import datetime

from src.paths import *
from src.passes import pass1_icecube

date =  datetime(1, 1, 2)
    

def test_pass1_time_range():
    """
    Tests that pass1_icecube output file timestamps are within 0 and 86400 seconds.
    """
    
    print(MOCK_ICECUBE_DATA_DIR)
    pass1_icecube.pass1_icecube(date, in_folder=MOCK_ICECUBE_DATA_DIR, out_folder=MOCK_ICECUBE_PASS1_DIR)

    times = []
    for c in [1, 2, 3, 4, 5, 6, 7, 8]:
        with open(MOCK_ICECUBE_PASS1_DIR / f'{date.strftime('y%Ym%md%d')}-IceCube-pass1' / f'{date.strftime('y%Ym%md%d')}-IceCube-c{c}-pass1.csv', 'r') as f:
            reader = csv.reader(f)
            next(reader)  #skips header
            
            for row in reader:
                times.append(float(row[0]))
                
    
    assert min(times) >= 0 and max(times) < 86400, 'mock_IceCube-pass1 times are not within [0, 86400)'
    
    return        
                
        
    
    
    