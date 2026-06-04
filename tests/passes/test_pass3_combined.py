#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 26 15:49:09 2026

@author: lucaspavlicek
"""

from datetime import datetime, timedelta
import csv
import numpy as np

from src.paths import *
from src.passes import *

date =  datetime(1, 1, 2)

def create_input_data():
    """
    Creates mock pass1_icecube, pass2_icecube, and pass2_infill data for testing if they don't already exist. This is necessary because the pass3_combined tests depend on the pass2_icecube and pass2_infill output files.
    """

    for d in [date - timedelta(days=1), date, date + timedelta(days=1)]:
        if (MOCK_ICECUBE_PASS2_DIR / f'{d.strftime("y%Ym%md%d")}-IceCube-pass2' / f'{d.strftime("y%Ym%md%d")}-IceCube-pass2.csv').exists():
            continue

        pass1_icecube.pass1_icecube(d, in_folder=MOCK_ICECUBE_DATA_DIR, out_folder=MOCK_ICECUBE_PASS1_DIR)
        pass2_icecube.pass2_icecube(d, in_folder=MOCK_ICECUBE_PASS1_DIR, out_folder=MOCK_ICECUBE_PASS2_DIR)
    
    if (MOCK_INFILL_PASS2_DIR / f'{date.strftime("y%Ym%md%d")}-Infill-pass2' / f'{date.strftime("y%Ym%md%d")}-Infill-pass2.csv').exists():
        return
    
    pass2_infill.pass2_infill(date, in_folder=MOCK_INFILL_DATA_DIR, out_folder=MOCK_INFILL_PASS2_DIR)
    
    return


def test_pass3_timestamp():
    """
    Tests that the pass3_combined output file starts at the correct time.
    """
    
    create_input_data()
    pass3_combined.pass3_combined(date, MOCK_ICECUBE_PASS1_DIR, MOCK_ICECUBE_PASS2_DIR, MOCK_INFILL_PASS2_DIR, MOCK_ICECUBE_PASS3_DIR)
    
    first_timestamps_key = [
        2112.569062466651,
        2112.033381797188,
        2111.888975053805,
        2112.0487193854606,
        2111.1391961170807,
        2111.1391960826213,
        2111.139196116033,
        2111.1391961170807 
        ]
    
    last_timestamps_key = [
        75411.29246377206,
        75411.29246376659,
        75411.29246376158,
        75411.29246376624,
        75411.292463761,
        75411.29246373562,
        75409.83384370635,
        75409.89246122232
    ]

    first_timestamps = []
    last_timestamps = []
    for c in range(1, 9):
        with open(MOCK_ICECUBE_PASS3_DIR / f'{date.strftime("y%Ym%md%d")}-IceCube-pass3' / f'{date.strftime("y%Ym%md%d")}-IceCube-c{c}-pass3.csv', 'r') as f:
            reader = csv.reader(f)
            next(reader)  #skips header

            first_row = next(reader)
            first_timestamps.append(float(first_row[0]))

            last_row = next(reader)
            for item in reader:
                last_row = item

            last_timestamps.append(float(last_row[0]))

        assert np.isclose(first_timestamps[-1], first_timestamps_key[c-1]), f"First timestamp for c{c} does not match expected value. Expected {first_timestamps_key[c-1]}, got {first_timestamps[-1]}"
        assert np.isclose(last_timestamps[-1], last_timestamps_key[c-1]), f"Last timestamp for c{c} does not match expected value. Expected {last_timestamps_key[c-1]}, got {last_timestamps[-1]}"
    
    return        