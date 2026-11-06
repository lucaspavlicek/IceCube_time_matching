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