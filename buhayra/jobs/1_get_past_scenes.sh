#!/bin/bash

source $HOME/local/miniconda3/bin/activate buhayra

$HOME/local/miniconda3/envs/buhayra/bin/python $HOME/proj/buhayra "get past scenes" $1 $2
