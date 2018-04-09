#!/bin/bash

cd /home/delgado/proj/sar2watermask

source activate mongodb

python getLatestPolygons.py
