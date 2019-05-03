#!/bin/bash

source $HOME/local/miniconda3/bin/activate buhayra

export JAVA_TOOL_OPTIONS="-Xmx30g"
export _JAVA_OPTIONS="-Xmx32g -Xss2m"

$HOME/local/miniconda3/envs/buhayra/bin/python $HOME/proj/buhayra_sib "sar2sigma"
