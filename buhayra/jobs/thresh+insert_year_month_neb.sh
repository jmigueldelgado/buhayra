#!/bin/bash
source $HOME/local/miniconda3/bin/activate dask

$HOME/local/miniconda3/envs/dask/bin/python $HOME/proj/buhayra_neb "threshold+insert year month" $1 $2
