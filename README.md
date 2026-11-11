Code for matching the IceCube times (that have no GPS time, unfortunately) to GPS-timed Telescope Array TALE Infill data, and then correcting the IceCube times to be in UTC.

## General notes:
- The main code is in ```src/```. The data will go in ```data/```, but the data does not come included. Instructions for adding data is below
- The ```tests/``` and ```mock_data/``` directories mimic the structure of ```src/``` and ```data/``` respectively. The mock data comes included, so anyone can download the repository and run the timematching procedure on the mock data.


## Installation
### Clone the repository
```
git clone https://github.com/lucaspavlicek/IceCube_time_matching.git
```

### Navigate to the repository
```
cd IceCube_time_matching
```

### Create and activate an environment (recommended)
- Create a new virtual envirnoment named .venv
```
python3 -m venv .venv
```
- Activate it
```
source .venv/bin/activate
```

### Install dependencies with pip
- either with dev dependencies (needed to run tests):
```
pip install -e '.[dev]'
```
- or without dev dependencies:
```
pip install -e .
```

## Adding the real data
The real data does not come included in the repository. Collaborators should have access to the data and will need to import the right IceCube and Infill data to the repository in a folder named ```data/``` at the root of the repository. The ```data/``` folder will need two subfolders named ```icecube_data/``` and ```infill_data/```.

### IceCube data
This codebase uses **decoded** hitbuffer files from the IceCube SAE built within TALE Infill. There may be a way to include the decoding scripts into the codebase, so that the project may begin with the undecoded binary data files in the future, but not yet. Place the uncompressed IceCube data (with the decoded files included) into the ```icecube_data/``` folder.

### Infill data
This codebase uses the 2025 reconstructed TALE Infill data by ICRR. Place the .bz2 data files for each day of Infill data into the ```infill_data/``` folder.

### Input data file tree
The file structure of the input data should look like this.
```
data/
  icecube_data/
    run_XXXXXXX_YYYYMMDD/
      run_XXXXXXX/
        run_XXXXXXX_chan-i_alldata.txt (needed)
        run_XXXXXXX_chan-i-info.txt (not needed)
        run_XXXXXXX_chan-i.bin (not needed)
        run_XXXXXXX_chan-j_alldata.txt (needed)
        ...
    ...
  infill_data/
    infillsdcalibev_pass2_YYMMDD.event.bz2
    ...
```

## Usage
- To run the full timematching procedure for a given day, from the project root run :
```
python src/timematch.py YYYYMMDD
```

Note that the date is a required positional argument, and the real data for the needed dates must be present. Always run the code from the root of the codebase.

- To run the code on the mock data put "mock" in place of the date:
```
python src/timematch.py mock
```

- To run a specific pass only, run the pass script with the same date/mock convention. Like:
```
python src/passes/pass1_icecube.py YYYYMMDD
```

- All the scripts have a -h or --help option for (brief) usage instructions.

## Mock data
The included mock data does not contain any lines from real data. The times are randomly generated to simulate both noise and real events, and the other parameters in the files are either randomly drawn from distributions parameterized by the real data, or just set to zero in some cases. The mock data is much smaller than the real data (especially compared with IceCube data), which allows it serve as a quick test. The real data takes me an hour to run per day, the mock data takes about 1 minute.

The mock data comes with later passes, not just the input data. This is fine, the relevant output data is just overwritten each time a script is run.

## Tests
Unit tests are written in pytest. See their documentation for more details. The repository comes with the mock data needed to run the tests.

### Run all tests
From the root of the repository, run ```pytest```.

See the [pytest documentation](https://docs.pytest.org/en/stable/) for running individual tests and other options.

### To use the memray plugin to track memory
Place the ```--memray``` option at the end of a command. For example: ```pytest --memray```.

See the [pytest-memray documentation](https://pytest-memray.readthedocs.io/en/latest/) for more options.

### Notes on more tests
More tests can be written. There may come a time where multiple sets of mock data will be needed to test different edge cases. For now, I am trying to keep it contained to only one set of mock data.

### Other notes
- As the program runs, more intermediate folders will be generated that store the data after each pass. The "final" output data will be in ```IceCube-pass3/```
- The file structure resembles the mock_data file structure.
- Changed from previous versions, the input data folders must be named exactly now.
- Changed from previous versions, the Infill data no longer needs to be uncompressed. The .bz2 files will work as is. In fact, the code expects the file names to end in .bz2.

## Python scripts
### timematch.py:
- The main organization script. As is, the script expects a date argument and will time match IceCube data on that day +/- 1 day, with infill data from just the chosen day. It will run through all of the passes.

### paths.py:
- Contains path variables to be used as shorthands throughout the codebase.

### hitbuffer_data_decode_....py
Inputs:
- Uncompressed folder of IceCube data. There should be a run_XXXXXXX_chan-Y.bin for each scintillator (although if a few are missing, it is still fine).
- mymods folder (a needed submodule which is not mine to distribute).

Tasks:
- Decodes the binary files
  
Outputs:
- run_XXXXXXX_chan-Y_alldata.txt file for each channel that will be placed in the same folder as the inputs

Notes:
- This script requires packages made by KIT, stored in a directory called 'mymods'. I won't put those here to keep them private. This is a high-level script. It is only included in this repository because I have modified it.
- This one is out of date, and isn't being used yet.

### pass1_icecube.py:
Inputs:
- Decoded hitbuffer data for each channel. There should be a run_XXXXXXX_chan-Y_alldata.txt for each scintillator (although if a few are missing, it is still fine).

  
Tasks:
- Checks each channel to verify the times are valid and can be used for time matching
- Shifts the times in each channel by the same constant so that the times start at zero (to make life easier)
- Although the IceCube times are already 99.99% sorted, we fully sort the hits so they are all in order of time

Outputs:
- A folder with a .csv file of hitbuffer data, shifted, and sorted by time, for each channel deemed to have working data

### pass2_icecube.py:
Inputs:
- pass1icecube data for each valid SD

Tasks:
- Requires that there is data for at least 3 SDs (or else returns an error)
- Finds coincidences where all working SDs have a hit within 100 microseconds, and records the average time of those hits
  
Outputs:
- A .csv file with, for each big coincidence event, the index of the original hits in all working SDs, and the average time of all the hits (the average time will be used to find a time match)

### pass2_infill.py:
Inputs:
- Reconstructed Infill SD data by ICRR (infillsdcalibev_pass2_YYMMDD.event.bz2). NOTE: the input data is already labeled pass 2, and the output is also labeled pass 2. Sorry for the confusion.
  
Tasks:
- Keep only the events that trigger all 9 SDs surrounding the IceCube SAE test station
- Converts the time from HHMMSS to microseconds
  
Outputs:
- A .csv file containing only the time of the filtered events (these events will be used to find a time match)

### pass3_combined.py:
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

## plans  
- add a way to run the timematch code on output data, to see if the time offset is zero, as a verification
- apply a consistent variable naming convention
- clean up code. Stop using ```sys.exit()``` and raise errors instead. Move helper functions out. Shorten monster functions. finish the switch to ```pathlib``` from os. And much more.
- optimize code