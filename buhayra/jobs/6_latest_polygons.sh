#!/bin/bash
source $HOME/miniconda3/bin/activate $HOME/miniconda3/envs/mongodb

# choose how old polygons should be in months
python $HOME/proj/buhayra "recent polys" 0
