#!/bin/bash
exec 1>6_latest_polygons.log 2>&1

source activate mongodb

python $HOME/proj/buhayra "recent polys"
