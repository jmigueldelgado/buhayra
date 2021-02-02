#!/bin/bash

source $HOME/local/miniconda3/bin/activate image-processing

$HOME/local/miniconda3/envs/image-processing/bin/python $HOME/proj/buhayra_manuscript "edge detection year month" $1 $2
