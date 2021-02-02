#!/bin/bash

source $HOME/local/miniconda3/bin/activate r-sf

$HOME/local/miniconda3/envs/r-sf/bin/python $HOME/proj/buhayra_manuscript "call concaveman year month" $1 $2
