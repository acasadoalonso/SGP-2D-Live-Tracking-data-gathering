#!/bin/bash
#
# generate the ADSG registration file
#
cd ~/src/APRSsrc
wget http://www.virtualradarserver.co.uk/Files/BasicAircraftLookup.sqb.gz
rm BasicAircraftLookup.sqb
gunzip BasicAircraftLookup.sqb.gz
python3 genadsbreg.py 


