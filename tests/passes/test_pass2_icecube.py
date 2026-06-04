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
from src.passes import *

date =  datetime(1, 1, 2)

def create_pass1_icecube_data():
    """
    Creates mock pass1_icecube data for testing if it doesn't already exist. This is necessary because the pass2_icecube tests depend on the pass1_icecube output file.
    """

    if (MOCK_ICECUBE_PASS1_DIR / f'{date.strftime('y%Ym%md%d')}-IceCube-pass1' / f'{date.strftime('y%Ym%md%d')}-IceCube-pass1.csv').exists():
        return
    

    pass1_icecube.pass1_icecube(date, in_folder=MOCK_ICECUBE_DATA_DIR, out_folder=MOCK_ICECUBE_PASS1_DIR)
    
    return

def test_pass2_coicidence_count():
    """
    Tests that the pass2_icecube output file has the correct number of coincidences.
    """

    create_pass1_icecube_data()
    pass2_icecube.pass2_icecube(date, in_folder=MOCK_ICECUBE_PASS1_DIR, out_folder=MOCK_ICECUBE_PASS2_DIR)
    
    with open(MOCK_ICECUBE_PASS2_DIR / f'{date.strftime('y%Ym%md%d')}-IceCube-pass2' / f'{date.strftime('y%Ym%md%d')}-IceCube-pass2.csv', 'r') as f:
        reader = csv.reader(f)
        next(reader)  #skips header

        row_count = sum(1 for row in reader)

    assert row_count == 140, f'Found {row_count} coincidences when there should be 140.'
    
    return        

def test_pass2_timestamps():
    """
    Tests that the first and last timestamps in the pass2_icecube output file are correct.
    """
    
    create_pass1_icecube_data()
    pass2_icecube.pass2_icecube(date, in_folder=MOCK_ICECUBE_PASS1_DIR, out_folder=MOCK_ICECUBE_PASS2_DIR)
    
    with open(MOCK_ICECUBE_PASS2_DIR / f'{date.strftime('y%Ym%md%d')}-IceCube-pass2' / f'{date.strftime('y%Ym%md%d')}-IceCube-pass2.csv', 'r') as f:
        reader = csv.reader(f)
        next(reader)  #skips header

        #checks that the first timestamp is correct
        first_row = next(reader)

        last_row = next(reader)
        for item in reader:
            last_row = item

    assert np.isclose(float(first_row[-1]), 619.0324242993811), 'First timestamp is incorrect.'
    assert np.isclose(float(last_row[-1]), 75553.41926616526), 'Last timestamp is incorrect.'

    return        