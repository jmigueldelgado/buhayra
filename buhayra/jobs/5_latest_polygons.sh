#!/bin/bash

cd /home/delgado/proj/buhayra/sar2watermask

source activate mongodb

python getLatestPolygons.py
