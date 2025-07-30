Code for matching the IceCube times (that have no GPS time, unfortunately) to GPS-timed Infill data, and then correcting the IceCube times to be in UTC.

## General notes:
- Each of the passX... scripts is looking to get a date in the format of YYYYMMDD from either the command line, or if there is no input, it will ask the user to input a date. In addition, a couple of them are also looking for an input directory name. The scripts will likely have a problem if you try and run the code from a notebook.
- The scripts after pass1icecube and pass2infill will work from the outputs of the previous scripts as is.
- This allows us to easily industrialize the process with a shell script or something. An example shell script will be included.
- My scripts aren't always the cleanest. They also have some comments to help the user, but they aren't very thorough. Good luck!

## hitbuffer_data_decode_....py
Inputs:
- Uncompressed folders of IceCube data. There should be a run_XXXXXXX_chan-Y.bin for each scintillator (although if a few are missing, it is still fine).

Tasks:
- Decodes the binary files
  
Outputs:
- run_XXXXXXX_chan-Y_alldata.txt file for each channel that will be placed in the same folder as the inputs

## pass1icecube.py:
Inputs:
- Decoded hitbuffer data for each channel (run_XXXXXXX_chan-Y_alldata.txt for each channel). Note that the data must be contained in directories: run_XXXXXXX_YYYYMMDD/run_XXXXXXX/
  
Tasks:
- Checks each channel to verify the times are valid and can be used for time matching
- Shifts the times in each channel by the same constant so that the times start at zero (to make life easier)
- Although the IceCube times are already 99.99% sorted, we fully sort the hits so they are all in order of time

Outputs:
- A folder with a .csv file of hitbuffer data, shifted, and sorted by time, for each channel deemed to have working data

## pass2icecube.py:
Inputs:
- pass1icecube data for each valid SD

Tasks:
- Requires that there is data for at least 3 SDs (or else returns an error)
- Finds coincidences where all working SDs have a hit within 100 microseconds, and records the average time of those hits
  
Outputs:
- A .csv file with, for each big coincidence event, the index of the original hits in all working SDs, and the average time of all the hits (the average time will be used to find a time match)

## pass2infill.py:
Inputs:
- Reconstructed Infill SD data by ICRR (infillsdcalibev_pass2_YYMMDD.event). NOTE: the input data is already labeled pass 2, and the output is also labeled pass 2. Sorry for the confusion.
  
Tasks:
- Keep only the events that trigger all 9 SDs surrounding the IceCube SAE test station
- Converts the time from HHMMSS to microseconds
  
Outputs:
- A .csv file containing only the time of the filtered events (these events will be used to find a time match)

## pass2combined.py:
Inputs:
- pass2infill data for chosen day
- pass1icecube data for chosen day and +/- 1 day (will work with at least one of the days)
- pass2icecube data for chosen day and +/- 1 day (will work with at least one of the days)
  
Tasks:
- Will attempt to find a time match between the strictly selected events in pass2icecube and pass2infill
- If a time match is found, it will shift the IceCube data accordingly, and then find IceCube, Infill pairs of calibration events to do a more accurate match
- Using the calibration pairs of events, it will make an additional linear fit to account for the IceCube clock seemingly counting seconds slightly faster than it should. 
- Finally, it will use scipy's make_smoothing_spline to fit a curve to the calibration events after the linear correction. This is to account for slight fluctuations in the IceCube clock speed throughout the day (likely caused by temperature)
- Using the constant offset, linear fit, and make smooth spline fit for each day's worth of data where a time match was found, the program will correct the original, full IceCube data so that the times are accurate in UTC and prepare an output for one day
  
Outputs:
- UTC timed decoded hitbuffer files (in the format of pass1icecube)
- Possibly more if we want

## timematching.sh
- This is a sample shell script to facilitate the entire time matching process. It is intended to be a working example to show how to supply the Python scripts with the correct dates.
- Note from Lucas: At some point, we will need to loop over all the dates. I know the Python datetime package can work well for this, and possibly another .py script can be created to help organize the dates.
