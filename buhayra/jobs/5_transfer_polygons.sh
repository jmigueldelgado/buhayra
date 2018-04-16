#!/bin/bash

cd /mnt/scratch/martinsd/watermasks

sftp delgado@141.89.96.184

put *simplified.geojson ./from_orson
exit

rm *simplified.geojson
