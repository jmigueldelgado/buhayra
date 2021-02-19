#!/bin/bash

source $HOME/local/miniconda3/bin/activate ogr-pg12

$HOME/local/miniconda3/envs/ogr-pg12/bin/python $HOME/proj/buhayra_manuscript "threshold+insert year month" $1 $2
