#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 26 15:49:09 2026

@author: lucaspavlicek
"""

from datetime import datetime
import csv
import numpy as np

from src.paths import *
from src.passes import pass3_combined

date =  datetime(1, 1, 2)

def test_pass3_timestamp():
    """
    Tests that the pass3_combined output file starts at the correct time.
    """
    
    pass3_combined.pass3_combined(date, MOCK_ICECUBE_PASS1_DIR, MOCK_ICECUBE_PASS2_DIR, MOCK_INFILL_PASS2_DIR, MOCK_ICECUBE_PASS3_DIR)
    
    with open(MOCK_ICECUBE_PASS3_DIR / f'{date.strftime('y%Ym%md%d')}-IceCube-pass3' / f'{date.strftime('y%Ym%md%d')}-IceCube-c1-pass3.csv', 'r') as f:
        reader = csv.reader(f)
        next(reader)  #skips header

        row = next(reader)

    time = float(row[0])

    assert np.isclose(time, 2112.569062466651), f'Found timestamp {time} when it should be 2112.569062466651.'
    
    return        