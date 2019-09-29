#!/bin/bash
cd /nfs/OGN/SWdata/archive
rm APRS$(date +%y)*.log
mv *$(date +%y)*.log Y$(date +%y)
bash compress.sh     Y$(date +%y)


