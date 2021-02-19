#!/bin/bash

source $HOME/local/miniconda3/bin/activate concaveman

$HOME/local/miniconda3/envs/concaveman/bin/python $HOME/proj/buhayra_manuscript "concave hull and insert year month" $1 $2
