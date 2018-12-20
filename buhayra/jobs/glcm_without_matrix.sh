#!/bin/bash

source $HOME/local/miniconda3/bin/activate dask

$HOME/local/miniconda3/envs/buhayra/bin/python $HOME/proj/buhayra "test parallel without matrix"
