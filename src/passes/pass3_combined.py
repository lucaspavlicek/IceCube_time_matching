#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: lucas
"""

import sys
import os
import argparse
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats
from scipy.interpolate import make_smoothing_spline

from src.paths import *

#This is a monster of a function and needs help
def pass3_combined(
    date: datetime,
    icecube_pass1_folder: Path = ICECUBE_PASS1_DIR,
    icecube_pass2_folder: Path = ICECUBE_PASS2_DIR,
    infill_in_folder: Path = INFILL_PASS2_DIR,
    out_folder: Path = ICECUBE_PASS3_DIR,
    hide_fig: bool = False,
    save_fig: bool = False
):

    print('Starting pass 3 script\n. . .')
    
    newfmtdate = date.strftime('y%Ym%md%d')
    
    #this does the oversampling
    def getcounts(diffs, threshold, times):
    
        count = np.zeros_like(times, dtype=int)
        for i in range(len(count)):
            indices = np.searchsorted(diffs, (times[i] - threshold, times[i] + threshold))
            count[i] = indices[1] - indices[0]
            
    
        return count

    def clearplot(ax, text='no data'):

        ax.clear()

        ax.axis('off')

        ax.text(
            0.5,
            0.5,
            text,
            transform=ax.transAxes,
            ha='center',
            va='center',
            fontsize=14,
            color='gray',
            alpha=0.5
        )
        return
    
    #creates and plots linear regression
    def linregplot(subplot, x, y):
        res = stats.linregress(x, y)
        tinv = lambda p, df: abs(stats.t.ppf(p/2, df))
        ts = tinv(0.05, len(x)-2)
        slopeuncert = ts*res.stderr
        intuncert = ts*res.intercept_stderr
            
        subplot.plot(x, y, '.', color='#fc8961')
        subplot.plot(x, res.slope*(x) + res.intercept, 'k')
            
        subplot.text((max(x) - min(x))*.7 + min(x), (max(y) - min(y))*.85 + min(y), f'y = Ax + B\nA = {res.slope:.3g} ± {slopeuncert:.3g}\nB = {res.intercept:.3g} ± {intuncert:.3g}', size=4)
        subplot.tick_params(axis='both', which='major', labelsize=5)
    
        return res.slope, res.intercept, slopeuncert, intuncert
    
    #plots residuals of linear regression
    def residualplot(subplot, x, y, slope, intercept):
        subplot.plot(x, y - (slope*x + intercept), '.', color='#fc8961')
        subplot.plot(x, np.zeros(len(x)), 'k')
        subplot.tick_params(axis='both', which='major', labelsize=5)
        return
    
    #finds a time match
    def timematch(icecubet, infillt, ax):
    
        differences = np.sort(np.subtract.outer(icecubet, infillt).reshape(-1))
            
        t = np.linspace(int(np.floor(differences[0])), int(np.ceil(differences[-1])), int(-1*np.floor(differences[0]) + np.ceil(differences[-1]))*100 + 1)
        
        print('Beginning oversampling\n. . .')
        counts = getcounts(differences, 0.1, t)
        
        guess = t[np.argmax(counts)]
        print(f'Oversampling finished, initial guess: {guess}')
        print(f'Count number: {max(counts)}')

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
        
        ax.plot(x, N.pdf(x, mu, sigma), 'k', label='Fitted PDF')
        ax.stairs(values, bins, fill=True, color='#fc8961', label='Oversampled data')
        ax.axvspan(mu - sigma, mu + sigma, alpha=0.2, color='grey', label=f'σ = {sigma:.6f}')
        ax.axvline(mu, color='k', ls='--', label=f'µ = {mu:.6f}')
        ax.legend(fontsize=4)
        ax.tick_params(axis='both', which='major', labelsize=5)
        ax.xaxis.get_offset_text().set_fontsize(5)
        ax.yaxis.get_offset_text().set_fontsize(5)
        ax.set_xlabel('Difference in time [s]', fontsize=5)
        ax.set_ylabel('Probability density', fontsize=5)
        ax.set_title(f'Gaussian fit within {searchwidth:.2f} seconds of initial guess', fontsize=6)
        
        return mu, sigma, (sigma**2 < 0.02 and max(counts) > 10) #criteria for checking if there is a time match. needs to be cleaned up eventually.
    
    def timecorrection(mu, sigma, ax1, ax2, ax3, ax4):
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
            icecubeindices = icecubeindices[stats.zscore(d) < 4]
            infillindices = infillindices[stats.zscore(d) < 4]
            after = len(icecubeindices)
            
            numlost = before - after
        
        del x, y, d, before, after, numlost
        
        xfixed = fixedicecube[icecubeindices]
        yfixed = fixedicecube[icecubeindices] - fixedinfill[infillindices]
        print(f'Found IceCube, Infill matching pairs for calibration ({len(xfixed)} data points). Finding linear fit\n. . .')

        A, B, _, _ = linregplot(ax1, xfixed, yfixed)
        ax1.set_title('IceCube - Infill times vs IceCube times', fontsize=6)
        ax1.set_ylabel('IceCube - Infill time [s]', fontsize=5)
        
        residualplot(ax2, xfixed, yfixed, A, B)
        ax2.set_title('error of linear fit versus IceCube times', fontsize=6)
        ax2.set_ylabel('(IceCube - Infill time) - prediction [s]', fontsize=5)
        
        print('Applying linear correction to IceCube times\n. . .')
        
        fixedicecube = fixedicecube - (A*fixedicecube + B)
        
        xfixed = fixedicecube[icecubeindices]
        yfixed = fixedicecube[icecubeindices] - fixedinfill[infillindices]
        
        print('Found IceCube, Infill matching pairs for calibration. Finding interpolated fit\n. . .')
        
        xs = np.linspace(xfixed[0], xfixed[-1], 10000)
        
        spl = make_smoothing_spline(xfixed, yfixed, lam=1e9)
        
        ax3.plot(xfixed, yfixed, '.', color='#fc8961')
        ax3.plot(xs, spl(xs), 'k')
        ax3.set_title('Make Smooth Spline interpolation after linear fit', fontsize=6)
        ax3.set_ylabel('Real values - predictions [s]', fontsize=5)
        ax3.tick_params(axis='both', which='major', labelsize=5)
        ax3.xaxis.get_offset_text().set_fontsize(5)
        ax3.yaxis.get_offset_text().set_fontsize(5)
        
        ax4.plot(xfixed, yfixed - spl(xfixed), '.', color='#fc8961')
        ax4.plot(xs, np.zeros(len(xs)), 'k')
        ax4.set_title('Error in interpolated fit', fontsize=6)
        ax4.set_xlabel('IceCube time [s]', fontsize=5)
        ax4.set_ylabel('Residual [s]', fontsize=5)
        ax4.tick_params(axis='both', which='major', labelsize=5)
        ax4.xaxis.get_offset_text().set_fontsize(5)
        ax4.yaxis.get_offset_text().set_fontsize(5)
        
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
    path = infill_in_folder / f'{newfmtdate}-Infill-pass2' / f'{newfmtdate}-Infill-pass2.csv'
    if os.path.exists(path):
        infilldf = pd.read_csv(path)
        infilltimes = infilldf['Microseconds'].values/1000000
    else:
        sys.exit('!!! No Infill data found')
    

    fig, ax = plt.subplots(5, 3, height_ratios=[2, 2, 1, 2, 1])
    fig.set_size_inches(10, 8)
    fig.suptitle(f'time match for {date.strftime('y%Ym%md%d')}')

    icecubetimes = []
    fitparams = []
    correctionparams = []
    for i in [-1, 0, 1]:
        datei = date + timedelta(days=i)
        newfmtdatei = datei.strftime('y%Ym%md%d')
        path = icecube_pass2_folder / f'{newfmtdatei}-IceCube-pass2' / f'{newfmtdatei}-IceCube-pass2.csv'
        if os.path.exists(path):
            icecubedfi = pd.read_csv(path)
            icecubetimes = icecubedfi['avg_time'].values
            print(f'Found IceCube data for {newfmtdatei}')
            print(f'IceCube events: {icecubetimes.shape}, Infill events: {infilltimes.shape}')
            fitparams.append(timematch(icecubetimes, infilltimes, ax[0, i+1]))
        else:
            print(f'!!! No IceCube data found for {newfmtdatei}. The script will try and proceed without this day')
            fitparams.append((False, False, False))
            clearplot(ax[0, i+1])

        if fitparams[-1][2]:
            correctionparams.append(timecorrection(fitparams[-1][0], fitparams[-1][1], ax[1, i+1], ax[2, i+1], ax[3, i+1], ax[4, i+1]))
        else:
            print('No match found for this day. Moving onto the next.')
            correctionparams.append((False, False, False, False, False))
            clearplot(ax[1, i+1], 'no timematch')
            clearplot(ax[2, i+1], 'no timematch')
            clearplot(ax[3, i+1], 'no timematch')
            clearplot(ax[4, i+1], 'no timematch')

    plt.tight_layout()

    if save_fig:
        plot_dir = ROOT_DIR / 'plots'
        plot_dir.mkdir(parents=True, exist_ok=True)

        plt.savefig(plot_dir / f'{date.strftime('y%Ym%md%d')}.png')

    if not hide_fig:
        plt.show()

    plt.close()

    #creates output directory unless it already exists
    out_sub_folder = out_folder / f'{date.strftime('y%Ym%md%d')}-IceCube-pass3'
    out_sub_folder.mkdir(parents=True, exist_ok=True)
    
    #finds which scintillators we have data for
    validsds = []
    for i in np.linspace(1, 8, 8, dtype = int):
        path = icecube_pass1_folder / f'{newfmtdate}-IceCube-pass1' / f'{newfmtdate}-IceCube-c{i}-pass1.csv'
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
            datei = date + timedelta(days=i-1)
            newfmtdatei = datei.strftime('y%Ym%md%d')
            if fitparams[i][2]:
                path = icecube_pass1_folder / f'{newfmtdatei}-IceCube-pass1' / f'{newfmtdatei}-IceCube-c{sd}-pass1.csv'
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

                    del daytimes, daydata, mask
                else:
                    print(f'!!! No IceCube data found for {newfmtdatei} and channel {sd}. The script will try and proceed')
            else:
                print(f'No time match for date {newfmtdatei}. Moving on to next day.')
        outputdfi = pd.DataFrame(columns=columnnames[1:], data=sddata)
        outputdfi.insert(0, columnnames[0], sdtimes)
            
        outpath = out_sub_folder / f'{newfmtdate}-IceCube-c{sd}-pass3.csv'
        outputdfi.to_csv(outpath, index=False)
        print(f'Made output for channel {sd}')

        del sdtimes, sddata, outputdfi
        
    return


def main():

    parser = argparse.ArgumentParser(
        description='Finds a time match between Infill and IceCube pass 2 data. Creates a correctly timed IceCube output file.'
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
        pass3_combined(
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
        
        pass3_combined(
            date=date,
            hide_fig=args.hideplot,
            save_fig=args.saveplot
        )

    return

if __name__ == '__main__': #only executes if script is run directly
    main()