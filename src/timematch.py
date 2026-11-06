#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: lucaspavlicek
"""

import argparse
from pathlib import Path
from datetime import datetime, timedelta
from src.passes import pass1_icecube, pass2_icecube, pass2_infill, pass3_combined
from src.paths import *

parser = argparse.ArgumentParser(
    description='Runs the full timematching procedure for a chosen day. Expects decoded IceCube hitbuffer files for the chosen date and +/- day, and reconsructed TALE Infill data for the chosen date. The needed file structure is in the README.'
)

parser.add_argument(
    'date', 
    help='Date in the form of YYYYMMDD, or "mock" to use mock data.'
)

args = parser.parse_args()

if args.date == 'mock' or args.date == '00010102':
    date = datetime(1, 1, 2)

    pass1_icecube.pass1_icecube(date - timedelta(days=1), MOCK_ICECUBE_DATA_DIR, MOCK_ICECUBE_PASS1_DIR)
    pass1_icecube.pass1_icecube(date, MOCK_ICECUBE_DATA_DIR, MOCK_ICECUBE_PASS1_DIR)
    pass1_icecube.pass1_icecube(date + timedelta(days=1), MOCK_ICECUBE_DATA_DIR, MOCK_ICECUBE_PASS1_DIR)

    pass2_icecube.pass2_icecube(date - timedelta(days=1), MOCK_ICECUBE_PASS1_DIR, MOCK_ICECUBE_PASS2_DIR)
    pass2_icecube.pass2_icecube(date, MOCK_ICECUBE_PASS1_DIR, MOCK_ICECUBE_PASS2_DIR)
    pass2_icecube.pass2_icecube(date + timedelta(days=1), MOCK_ICECUBE_PASS1_DIR, MOCK_ICECUBE_PASS2_DIR)

    pass2_infill.pass2_infill(date, MOCK_INFILL_DATA_DIR, MOCK_INFILL_PASS2_DIR)

    pass3_combined.pass3_combined(date, MOCK_ICECUBE_PASS1_DIR, MOCK_ICECUBE_PASS2_DIR, MOCK_INFILL_PASS2_DIR, MOCK_ICECUBE_PASS3_DIR)

else:
    date = datetime.strptime(args.date, '%Y%m%d')

    pass1_icecube.pass1_icecube(date - timedelta(days=1))
    pass1_icecube.pass1_icecube(date)
    pass1_icecube.pass1_icecube(date + timedelta(days=1))

    pass2_icecube.pass2_icecube(date - timedelta(days=1))
    pass2_icecube.pass2_icecube(date)
    pass2_icecube.pass2_icecube(date + timedelta(days=1))

    pass2_infill.pass2_infill(date)

    pass3_combined.pass3_combined(date)