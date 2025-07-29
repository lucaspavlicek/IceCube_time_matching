#!/usr/bin/env python3

"""
@author: William
Lucas's copy
"""

import sys, os
import glob
import numpy as np
import matplotlib.pyplot as plt
import datetime

sys.path.append('Hitbuffer_decode_Will/mymods')
from udaq_decoder import *
from utils import *
from log_parser import *

#  The main variables needed to find the run data
#-------------------------------------------------
spooldir = 'run_0000010_20231201'
# This is where your run data is stored
#-------------------------------------------------

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
