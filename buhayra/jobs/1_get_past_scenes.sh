#!/bin/bash

source activate buhayra

touch $HOME/what_is_going_on

python $HOME/proj/buhayra "get past scenes" $1 $2
