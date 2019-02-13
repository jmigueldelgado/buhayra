#!/bin/bash


export JAVA_TOOL_OPTIONS="-Xmx30g"
export _JAVA_OPTIONS="-Xmx32g -Xss2m"
source $HOME/local/miniconda3/bin/activate buhayra

$HOME/local/miniconda3/envs/buhayra/bin/python $HOME/proj/buhayra_neb "sar scene" $1
