#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 26 15:49:09 2026

@author: lucaspavlicek
"""

from datetime import datetime
import csv

from src.paths import *
from src.passes import pass2_icecube

date =  datetime(1, 1, 2)

def test_pass2_coicidence_count():
    """
    Tests that the pass2_icecube output file has the correct number of coincidences.
    """
    
    pass2_icecube.pass2_icecube(date, in_folder=MOCK_ICECUBE_PASS1_DIR, out_folder=MOCK_ICECUBE_PASS2_DIR)
    
    with open(MOCK_ICECUBE_PASS2_DIR / f'{date.strftime('y%Ym%md%d')}-IceCube-pass2' / f'{date.strftime('y%Ym%md%d')}-IceCube-pass2.csv', 'r') as f:
        reader = csv.reader(f)
        next(reader)  #skips header

        row_count = sum(1 for row in reader)

    assert row_count == 46, f'Found {row_count} coincidences when there should be 46.'
    
    return        