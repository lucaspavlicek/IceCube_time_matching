Code for matching the IceCube times (that have no GPS time, unfortunately) to GPS-timed Infill data, and then correcting the IceCube times to be in UTC.

## pass1icecube:
inputs:
- decoded hitbuffer data for each channel
tasks:
- checks each channel to verify the times are valid and can be used for time matching
- shifts the times in each channel by the same constant so that the times start at zero (to make life easier)
- although the IceCube times are already 99.99% sorted, we fully sort the hits so they are all in order of time
outputs:
- a .csv file of hitbuffer data, shifted, and sorted by time, for each channel deemed to have working data

## pass2icecube:
  inputs:
    - pass1icecube data for each valid SD
  tasks:
    - requires that there is data for at least 3 SDs (or else returns an error)
    - finds coincidences where all working SDs have a hit within 100 microseconds, and records the average time of those hits
  outputs:
    - a .csv file with, for each big coincidence event, the index of the original hits in all working SDs, and the average time of all the hits (the average time will be used to find a time match)

## pass2infill:
  inputs:
    - reconstructed Infill SD data by ICRR
  tasks:
    - keep only the events that trigger all 9 SDs surrounding the IceCube SAE test station
    - converts the time from HHMMSS to microseconds
  outputs:
    - a .csv file containing only the time of the filtered events (these events will be used to find a time match)

## pass2combined:
  inputs:
    - pass2infill data for chosen day
    - pass2icecube data for chosen day and +/- 1 day
  tasks:
    - to do
  outputs:
    - UTC timed decoded hitbuffer files (in the format of pass1icecube)
    - possibly more if we want
