#!/bin/bash
exec 1>6_latest_polygons.log 2>&1

source $HOME/miniconda3/bin/activate $HOME/miniconda3/envs/mongodb

python $HOME/proj/buhayra "1 month old polys"

sed -i 's/id_funceme/id_cogerh/g' $HOME/load_to_postgis/latest.geojson
