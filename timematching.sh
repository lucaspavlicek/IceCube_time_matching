#!/bin/bash

icecubedirectory='IceCubedata'
infilldirectory='Infilldata'
date='20231221'

echo Starting IceCube pass 1 at local machine time:
date
python pass1icecube.py $icecubedirectory $date

echo Finished IceCube pass 1
echo Starting IceCube pass 2 at local machine time:
date
python pass2icecube.py $date

echo Finished IceCube pass 2
echo Starting Infill pass 2 at local machine time:
date
python pass2infill.py $infilldirectory $date

echo Finished Infill pass 2
echo Starting combined pass 3 at local machine time:
date
python pass3combined.py $date

echo Finished time matching for $date at local machine time:
date
