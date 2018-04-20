#!/bin/bash
exec 1>6_latest_polygons.log 2>&1

source $HOME/miniconda3/bin/activate $HOME/miniconda3/envs/mongodb

python $HOME/proj/buhayra "recent polys"
