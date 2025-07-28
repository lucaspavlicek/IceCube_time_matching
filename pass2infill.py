#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: ethan
modified by lucas
"""

import sys
import os
import datetime

print('Starting pass 1 for Infill script\n. . .')

if len(sys.argv) > 1:
    directory = sys.argv[1]
    print('Received directory from command line:', directory)
else:
    directory = input('In which directory is the Infill data?')


if len(sys.argv) > 2:
    datestr = sys.argv[2]
    print('Received date from command line:', datestr)
else:
    datestr = input('Which date? (enter in yyyymmdd):')

date = datetime.datetime(int(datestr[:4]), int(datestr[4:6]), int(datestr[6:]))

newfmtdate = 'y'+date.strftime('%Y')+'m'+date.strftime('%m')+'d'+date.strftime('%d')

#finds the directory name that contains the chosen date
def finddir(directory, datestr):
    found = False
    for file in os.listdir(directory):
        if (datestr in file) or (datestr[2:] in file):
            if not found:
                datafolder = directory + os.sep + file
                found = True
                if os.path.isdir(directory + os.sep + file):
                    sys.exit('!!! Found a directory containing the date but wanted a file')
                print('Found file for day:', datestr, 'named', file)
            
            else:
                sys.exit('!!! Found another file/directory containing the date')

    if not found:
        sys.exit('!!! No file/directory found containing the date')
        
    return datafolder

def datareading(i, path):
    events, events9 = [], []
    current_event, current_event9 = [], []
    in9range = [9105, 9106, 9107, 9205, 9206, 9207, 9305, 9306, 9307]

    def finalize_event():
        if current_event:
            events.append(current_event.copy())
            found_ids = {int(row[0]) for row in current_event9[1:]}  # skip header
            if set(in9range).issubset(found_ids):
                filtered_subs = [row for row in current_event9[1:] if int(row[0]) in in9range]
                events9.append([current_event9[0]] + filtered_subs)

    if not os.path.exists(path):
        sys.exit('!!! No Infill data found for this date')
    
    with open(path, "r") as file:
        for line in file:
            parts = line.strip().split(',')
            if not parts:
                continue

            if not parts[0].startswith("9"):  # Header line
                finalize_event()
                current_event = [[float(p) for p in parts]]
                current_event9 = [[float(p) for p in parts]]
            else:  # Subdetector line
                parts = line.strip().split()
                subdetector_id = int(parts[0])
                reordered = [float(parts[0])] + [float(p) for p in parts[1:]]
                current_event.append(reordered)
                if subdetector_id in in9range:
                    current_event9.append(reordered)

    finalize_event()
    return events, events9

def timingFile(events, i):
    def hhmmss_to_microseconds(hhmmss):
            hours = hhmmss // 10000
            minutes = (hhmmss // 100) % 100
            seconds = hhmmss % 100

            seconds = hours * 3600 + minutes * 60 + seconds
            microseconds = seconds * 1000000
            return microseconds

    with open(f"Infill-pass2/{i}-Infill-pass2/{i}-Infill-pass2.csv", "w") as file:
        file.write("Microseconds\n")
        for i in range(0, len(events)):
            line = f"{hhmmss_to_microseconds(events[i][0][1])+events[i][0][2]}"
            file.write(line + "\n")

    return

for i in [-1, 0, 1]:
    datei = date + datetime.timedelta(days=i)
    newfmtdatei = 'y'+datei.strftime('%Y')+'m'+datei.strftime('%m')+'d'+datei.strftime('%d')
    datestri = datei.strftime('%Y')+datei.strftime('%m')+datei.strftime('%d')
    if not os.path.exists('Infill-pass2/'+newfmtdatei+'-Infill-pass2/'+newfmtdatei+'-Infill-pass2.csv'):
        #creates output directory unless it already exists
        if not os.path.exists('Infill-pass2/'+newfmtdatei+'-Infill-pass2'):
            os.makedirs('Infill-pass2/'+newfmtdatei+'-Infill-pass2')
        pathi = finddir(directory, datestri)
        print('Finding 9 detector coincidences for date:', newfmtdatei, '\n. . .')
        _, e9 = datareading(datestri, pathi)

        print('Creating output\n. . .')
        timingFile(e9, newfmtdatei)
    	
    else:
        print('File for date', newfmtdatei, 'already exists')
print('Pass 2 Infill done')