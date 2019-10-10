#!/bin/bash
source $HOME/local/miniconda3/bin/activate buhayra

$HOME/local/miniconda3/envs/dask/bin/python $HOME/proj/buhayra_sib "remove finished scenes"
