#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@author: William and KIT
Lucas's copy
"""

import sys, os
import glob
import numpy as np
import matplotlib.pyplot as plt
import datetime

# Path to mymods folder
sys.path.append('Hitbuffer_decode_Will/mymods')
from udaq_decoder import *
from utils import *
from log_parser import *

print('Starting hitbuffer decode script\n. . .')
#  The main variables needed to find the run data
#-------------------------------------------------
if len(sys.argv) > 1:
    directory = sys.argv[1]
    print(f'Received directory from command line: {directory}')
else:
    directory = input('In which directory is the IceCube data?')


if len(sys.argv) > 2:
    datestr = sys.argv[2]
    print(f'Received date from command line: {datestr}')
else:
    datestr = input('Which date? (enter in yyyymmdd):')
#-------------------------------------------------

found = False
for file in os.listdir(directory):
    if datestr in file:
        if not found:
            spooldir = directory + os.sep + file

            found = True
            if not os.path.isdir(directory + os.sep + file):
                sys.exit('!!! Found a file containing the date but it is not a directory')
            print(f'Found directory containing {datestr} named {file}')
            
        else:
            sys.exit('!!! Found another file/directory containing the date')

if not found:
    sys.exit('!!! No file/directory found containing the date')

adc_values = np.arange(4096)

datafolders = sorted(glob.glob(os.path.join(spooldir, 'run_*')))
for datafolder in datafolders:
    for run in range(0, len(datafolders)):

        runNum = datafolder.split('_')[1]
        path = datafolder

        if not os.path.exists(path):
            print('run dir not found -> run_{0}'.format(runNum))

        ### decode the hit buffer
        DEBUG = False
        COBS = False

        print(datafolder)
        for chan in range(1, 9):
            chandata = []
            datafile = os.path.join(path, f'run_{runNum}_chan-{chan}_alldata.txt')
            runfile = os.path.join(path, f'run_{runNum}_chan-{chan}.bin')

            if os.path.exists(runfile):
                print(f'Run-{runNum}, Chan-{chan}: decoding...')
                chandata = microdaqChargestamps(runfile, cobs_decode=COBS, debug=DEBUG)

                with open(datafile, 'w') as file:
                    for line in chandata:
                        file.write(' '.join(map(str, line)) + "\n")
                print(f'Run-{runNum}, Chan-{chan}, All Data: file written')

            else:
                continue

print('DONE\n')
