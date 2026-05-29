#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 25 00:43:02 2026

@author: lucaspavlicek
"""


import datetime
from passes import pass1_icecube, pass2_icecube
from src.paths import *

date = datetime.datetime(2023, 12, 22)

pass1_icecube.pass1_icecube(date - datetime.timedelta(days=1))
pass1_icecube.pass1_icecube(date)
pass1_icecube.pass1_icecube(date + datetime.timedelta(days=1))

pass2_icecube.pass2_icecube(date - datetime.timedelta(days=1))
pass2_icecube.pass2_icecube(date)
pass2_icecube.pass2_icecube(date + datetime.timedelta(days=1))

#pass2_infill.pass2_infill(INFILL_DATA_DIR, date)

#pass3_combined.pass3_combined(date)
