#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: ethan
modified by lucas
"""

import sys
import os
from datetime import datetime
import bz2

from src.paths import *

def find_path(date: datetime, in_folder: Path):
    """
    Finds path to file number by searching for date string.
    """

    files = [x for x in in_folder.glob(f'*{date.strftime('%y%m%d')}*') if x.is_file()]

    if len(files) < 1:
        raise FileNotFoundError(f'Found no file with the date: {date.strftime('%y%m%d')}.')
        return
    
    elif len(files) > 1:
        raise ValueError(f'Found more than one file with the date: {date.strftime('%y%m%d')}.')
        return

    #returns full path to file
    return files[0]

#TODO: move the helper fuctions outside of the main one
def pass2_infill(date: datetime, in_folder: Path = INFILL_DATA_DIR, out_folder: Path = INFILL_PASS2_DIR):

    print('Starting pass 2 for Infill script\n. . .')
    
    datestr = date.strftime('%Y%m%d')
    newfmtdate = date.strftime('y%Ym%md%d')

    out_sub_folder = out_folder / f'{date.strftime('y%Ym%md%d')}-Infill-pass2'
    out_sub_folder.mkdir(parents=True, exist_ok=True)
    
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
        
        with bz2.open(path, 'rt') as file:
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
    
        with open(out_sub_folder / f"{i}-Infill-pass2.csv", "w") as file:
            file.write("Microseconds\n")
            for i in range(0, len(events)):
                line = f"{hhmmss_to_microseconds(events[i][0][1])+events[i][0][2]}"
                file.write(line + "\n")
    
        return
        
    path = find_path(date, in_folder)

    print(f'Finding 9 detector coincidences for date: {newfmtdate}\n. . .')
    _, e9 = datareading(datestr, path)
    
    print('Creating output\n. . .')
    timingFile(e9, newfmtdate)
        	
    print('Pass 2 Infill done')
    
    return

def main():

    res = input('Use real or mock data? ("real" or "mock") : ')

    if res == 'mock':
        pass2_infill(datetime(1, 1, 2), MOCK_INFILL_DATA_DIR, MOCK_INFILL_PASS2_DIR)

    elif res == 'real':
        date_str = input('Which date? (YYYYMMDD) : ')
        date = datetime.strptime(date_str, '%Y%m%d')
        
        pass2_infill(date)

    else:
        raise ValueError('Not a valid response.')
        return

    return

if __name__ == '__main__': #only executes if script is run directly
    main()