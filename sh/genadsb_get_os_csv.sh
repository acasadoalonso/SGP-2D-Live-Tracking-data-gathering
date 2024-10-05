#!/bin/bash
y=$(date +%Y)
m=$(date +%m)
rm -f aircraftDatabase.csv
echo "Get the OpenSky Network Aircraft DB ..."
wget https://opensky-network.org/datasets/metadata/aircraftDatabase.csv
