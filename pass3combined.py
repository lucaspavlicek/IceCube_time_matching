#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: lucas
"""

import sys
import os
import psutil
import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats
from scipy.interpolate import make_smoothing_spline

print('Starting pass 3 script\n. . .')

datestr = input('Which date? (enter in yyyymmdd):')

date = datetime.datetime(int(datestr[:4]), int(datestr[4:6]), int(datestr[6:]))

newfmtdate = date.strftime('y%Ym%md%d')

#this does the oversampling
def getcounts(diffs, threshold, times):

    count = np.zeros_like(times, dtype=int)
    for i in range(len(count)):
        indices = np.searchsorted(diffs, (times[i] - threshold, times[i] + threshold))
        count[i] = indices[1] - indices[0]
        

    return count

#creates and plots linear regression
def linregplot(subplot, x, y):
    res = stats.linregress(x, y)
    tinv = lambda p, df: abs(stats.t.ppf(p/2, df))
    ts = tinv(0.05, len(x)-2)
    slopeuncert = ts*res.stderr
    intuncert = ts*res.intercept_stderr
        
    subplot.plot(x, y, '.', color='#fc8961')
    subplot.plot(x, res.slope*(x) + res.intercept, 'k')
        
    subplot.text((max(x) - min(x))*.6, (max(y) - min(y))*.9 + min(y), f'y = Ax + B\nA = {res.slope:.6g} ± {slopeuncert:.6g}\nB = {res.intercept:.6g} ± {intuncert:.6g}', size=8)

    return res.slope, res.intercept, slopeuncert, intuncert

#plots residuals of linear regression
def residualplot(subplot, x, y, slope, intercept):
    subplot.plot(x, y - (slope*x + intercept), '.', color='#fc8961')
    subplot.plot(x, np.zeros(len(x)), 'k')
    return

#finds a time match
def timematch(icecubet, infillt):

    differences = np.sort(np.subtract.outer(icecubet, infillt).reshape(-1))
        
    t = np.linspace(int(np.floor(differences[0])), int(np.ceil(differences[-1])), int(-1*np.floor(differences[0]) + np.ceil(differences[-1]))*100 + 1)
    
    print('Beginning oversampling\n. . .')
    counts = getcounts(differences, 0.1, t)
    
    guess = t[np.argmax(counts)]
    print(f'Oversampling finished, initial guess: {guess}')
    print(f'Count number: {max(counts)}')
    import psutil
    oversampled = []
    searchwidth = 1 #1 second should be plenty here    
    condition = (np.abs(t - guess) < searchwidth).nonzero()
    for i in range(len(counts[condition])):
        oversampled.extend(np.ones(counts[condition][i])*t[condition][i])
    
    numlost = np.inf
    while numlost > 0:
        before = len(oversampled)
        oversampled = np.array(oversampled)[np.abs(stats.zscore(oversampled)) < 3]
        after = len(oversampled)
        numlost = before - after
        
    print(f'Fitting filtered oversampled data (n = {len(oversampled)})\n. . .')
    N = stats.norm
    mu, sigma = N.fit(oversampled)
    print(f'Gaussian fit complete with parameters: µ = {mu}, σ = {sigma}')
    
    x = np.linspace(guess - searchwidth, guess + searchwidth, 1000)
    values, bins = np.histogram(oversampled, bins=10, density=True)
    
    fig, ax = plt.subplots()
    
    ax.plot(x, N.pdf(x, mu, sigma), 'k', label='Fitted PDF')
    ax.stairs(values, bins, fill=True, color='#fc8961', label='Oversampled data')
    ax.axvspan(mu - sigma, mu + sigma, alpha=0.2, color='grey', label=f'σ = {sigma:.6f}')
    ax.axvline(mu, color='k', ls='--', label='µ = {mu:.6f}')
    ax.legend()
    ax.set_xlabel('Difference in time [s]')
    ax.set_ylabel('Probability density')
    ax.set_title(f'Gaussian fit within {searchwidth:.2f} seconds of initial guess')
    plt.show()
    
    return mu, sigma, sigma**2 < 0.02 #criteria for checking if there is a time match

def timecorrection(mu, sigma):
    print('Applying constant correction to IceCube times\n. . .')
    
    fixedicecube = (icecubetimes - mu)
    fixedinfill = infilltimes
    
    outercon = np.subtract.outer(fixedicecube, fixedinfill)
    icecubeindices, infillindices = np.where(np.abs(outercon) < sigma*2)
    
    numlost = np.inf
    while numlost > 0:
        x = fixedicecube[icecubeindices]
        y = fixedicecube[icecubeindices] - fixedinfill[infillindices]
        
        before = len(icecubeindices)
        res = stats.linregress(x, y)
        d = np.abs(y - (res.slope*(x) + res.intercept))
        icecubeindices = icecubeindices[stats.zscore(d) < 6]
        infillindices = infillindices[stats.zscore(d) < 6]
        after = len(icecubeindices)
        
        numlost = before - after
    
    del x, y, d, before, after, numlost
    
    xfixed = fixedicecube[icecubeindices]
    yfixed = fixedicecube[icecubeindices] - fixedinfill[infillindices]
    print(f'Found IceCube, Infill matching pairs for calibration ({len(xfixed)} data points). Finding linear fit\n. . .')

    fig, ax = plt.subplots(2, gridspec_kw={'height_ratios': [2, 1]}, figsize=(6,8))
    fig.tight_layout(pad=4)
    
    A, B, _, _ = linregplot(ax[0], xfixed, yfixed)
    ax[0].set_title('IceCube - Infill times vs IceCube times')
    ax[0].set_xlabel('IceCube time [s]')
    ax[0].set_ylabel('IceCube - Infill time [s]')
    
    residualplot(ax[1], xfixed, yfixed, A, B)
    ax[1].set_title('error of linear fit versus IceCube times')
    ax[1].set_xlabel('IceCube time [s]')
    ax[1].set_ylabel('(IceCube - Infill time) - prediction [s]')
    
    plt.show()
    
    print('Applying linear correction to IceCube times\n. . .')
    
    fixedicecube = fixedicecube - (A*fixedicecube + B)
    
    xfixed = fixedicecube[icecubeindices]
    yfixed = fixedicecube[icecubeindices] - fixedinfill[infillindices]
    
    print('Found IceCube, Infill matching pairs for calibration. Finding interpolated fit\n. . .')
    
    xs = np.linspace(xfixed[0], xfixed[-1], 10000)
    
    spl = make_smoothing_spline(xfixed, yfixed, lam=1e9)
    
    fig, ax = plt.subplots(2, gridspec_kw={'height_ratios': [2, 1]}, figsize=(6,8))
    fig.tight_layout(pad=4)
    
    ax[0].plot(xfixed, yfixed, '.', color='#fc8961')
    ax[0].plot(xs, spl(xs), 'k')
    ax[0].set_title('Make Smooth Spline interpolation after linear fit')
    ax[0].set_xlabel('IceCube time [s]')
    ax[0].set_ylabel('Real values - predictions [s]')
    
    ax[1].plot(xfixed, yfixed - spl(xfixed), '.', color='#fc8961')
    ax[1].plot(xs, np.zeros(len(xs)), 'k')
    ax[1].set_title('Error in interpolated fit')
    ax[1].set_xlabel('IceCube time [s]')
    ax[1].set_ylabel('Residual [s]')
    
    plt.show()
    
    print('Applying interpolated correction to IceCube times\n. . .')
        
    #creates output file of residuals
    #fixedicecube = fixedicecube - (spl(fixedicecube))
    #xfixed = fixedicecube[icecubeindices]
    #yfixed = fixedicecube[icecubeindices] - fixedinfill[infillindices]
    #resids = pd.DataFrame()
    #resids['residual'] = yfixed
    #resids.to_csv(newfmtdate+'-residuals.csv')

    return A, B, spl, min(xfixed), max(xfixed)

#load infill data
path = f'Infill-pass2/{newfmtdate}-Infill-pass2/{newfmtdate}-Infill-pass2.csv'
if os.path.exists(path):
    infilldf = pd.read_csv(path)
    infilltimes = infilldf['Microseconds'].values/1000000
else:
    sys.exit('!!! No Infill data found')

    
icecubetimes = []
fitparams = []
correctionparams = []
for i in [-1, 0, 1]:
    datei = date + datetime.timedelta(days=i)
    newfmtdatei = datei.strftime('y%Ym%md%d')
    path = f'IceCube-pass2/{newfmtdatei}-IceCube-pass2/{newfmtdatei}-IceCube-pass2.csv'
    if os.path.exists(path):
        icecubedfi = pd.read_csv(path)
        icecubetimes = icecubedfi['avg_time'].values
        print(f'Found IceCube data for {newfmtdatei}')
        print(f'IceCube events: {icecubetimes.shape}, Infill events: {infilltimes.shape}')
        fitparams.append(timematch(icecubetimes, infilltimes))
    else:
        print(f'!!! No IceCube data found for {newfmtdatei}. The script will try and proceed without this day')
        fitparams.append((False, False, False))
    if fitparams[-1][2]:
        correctionparams.append(timecorrection(fitparams[-1][0], fitparams[-1][1]))
    else:
        print('No match found for this day. Moving onto the next.')
        correctionparams.append((False, False, False, False, False))

#creates output directory unless it already exists
if not os.path.exists(f'IceCube-pass3/{newfmtdate}-IceCube-pass3'):
    os.makedirs(f'IceCube-pass3/{newfmtdate}-IceCube-pass3')

#finds which scintillators we have data for
validsds = []
for i in np.linspace(1, 8, 8, dtype = int):
    path = f'IceCube-pass1/{newfmtdate}-IceCube-pass1/{newfmtdate}-IceCube-c{i}-pass1.csv'
    if os.path.exists(path):
        validsds.append(i)

if len(validsds) < 1:
    sys.exit('!!! IceCube pass 1 data is missing')

#creates output for each scintillator
for sd in validsds:
    print(f'Creating output for SD {sd}\n. . .')
    sdtimes = []
    sddata = []
    for i in range(3):
        datei = date + datetime.timedelta(days=i-1)
        newfmtdatei = datei.strftime('y%Ym%md%d')
        if fitparams[i][2]:
            path = f'IceCube-pass1/{newfmtdatei}-IceCube-pass1/{newfmtdatei}-IceCube-c{sd}-pass1.csv'
            if os.path.exists(path):
                print(f'Time match and file found for {newfmtdatei}. Correcting times\n. . .')
                daytimes = []
                daydata = []
                with open(path, "r") as file:
                    columnnames = file.readline().strip().split(',')
                    for line in file:
                        parts = line.strip().split(',')
                        daytimes.append(float(parts[0]))
                        #daydata.append(parts[1:])
                        daydata.append([int(parts[1]),
                                        int(parts[2]),
                                        int(parts[3]),
                                        int(parts[4]),
                                        int(parts[5])])
                        #make the code stop after some lines (for testing)
                        if len(daytimes) > 1000000:
                            break
                            
                del file
                
                daytimes = daytimes - fitparams[i][0]
                daytimes = daytimes - (correctionparams[i][0]*daytimes + correctionparams[i][1])
                
                #filter out data outside of interpolation interval
                mask = (daytimes > correctionparams[i][3]) & (daytimes < correctionparams[i][4])
                daytimes = daytimes[mask]
                daydata = list(np.array(daydata)[mask])

                #applies SPL
                daytimes = daytimes - correctionparams[i][2](daytimes)
                sdtimes.extend(daytimes)
                sddata.extend(daydata)
                process = psutil.Process()
                print(f'mb of memory used: {process.memory_info().rss/1000000}')  # in megabytes
                del daytimes, daydata, mask
            else:
                print(f'!!! No IceCube data found for {newfmtdatei} and channel {sd}. The script will try and proceed')
        else:
            print(f'No time match for date {newfmtdatei}. Moving on to next day.')
    outputdfi = pd.DataFrame(columns=columnnames[1:], data=sddata)
    outputdfi.insert(0, columnnames[0], sdtimes)
        
    outpath = f'IceCube-pass3/{newfmtdate}-IceCube-pass3/{newfmtdate}-IceCube-c{sd}-pass3.csv'
    outputdfi.to_csv(outpath, index=False)
    print(f'Made output for channel {sd}')
    process = psutil.Process()
    print(f'mb of memory used: {process.memory_info().rss/1000000}')  # in megabytes
    del sdtimes, sddata, outputdfi
