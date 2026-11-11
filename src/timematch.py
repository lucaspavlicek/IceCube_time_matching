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
    help='date in the form of YYYYMMDD, or "mock" to use mock data'
)

parser.add_argument(
    '--hideplot', 
    action='store_true', 
    help='will suppress output plot, shown by default'
)

parser.add_argument(
    '--saveplot',
    action='store_true', 
    help='will save plot in plots/, off by default'
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

    pass3_combined.pass3_combined(
        date=datetime(1, 1, 2),
        icecube_pass1_folder=MOCK_ICECUBE_PASS1_DIR,
        icecube_pass2_folder=MOCK_ICECUBE_PASS2_DIR,
        infill_in_folder=MOCK_INFILL_PASS2_DIR,
        out_folder=MOCK_ICECUBE_PASS3_DIR,
        hide_fig=args.hideplot,
        save_fig=args.saveplot
    )

else:
    date = datetime.strptime(args.date, '%Y%m%d')

    pass1_icecube.pass1_icecube(date - timedelta(days=1))
    pass1_icecube.pass1_icecube(date)
    pass1_icecube.pass1_icecube(date + timedelta(days=1))

    pass2_icecube.pass2_icecube(date - timedelta(days=1))
    pass2_icecube.pass2_icecube(date)
    pass2_icecube.pass2_icecube(date + timedelta(days=1))

    pass2_infill.pass2_infill(date)

    pass3_combined.pass3_combined(
        date=date,
        hide_fig=args.hideplot,
        save_fig=args.saveplot
    )