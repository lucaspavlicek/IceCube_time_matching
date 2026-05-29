#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 26 15:49:09 2026

@author: lucaspavlicek
"""

from datetime import datetime
import csv

from src.paths import *
from src.passes import pass2_infill

date =  datetime(1, 1, 2)

def test_pass2_coicidence_count():
    """
    Tests that the pass2_infill output file has the correct number of coincidences.
    """
    
    pass2_infill.pass2_infill(date, in_folder=MOCK_INFILL_DATA_DIR, out_folder=MOCK_INFILL_PASS2_DIR)
    
    with open(MOCK_INFILL_PASS2_DIR / f'{date.strftime('y%Ym%md%d')}-Infill-pass2' / f'{date.strftime('y%Ym%md%d')}-Infill-pass2.csv', 'r') as f:
        reader = csv.reader(f)
        next(reader)  #skips header

        row_count = sum(1 for row in reader)

    assert row_count == 570, f'Found {row_count} coincidences when there should be 570.'
    
    return        