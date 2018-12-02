#!/bin/bash

export JAVA_TOOL_OPTIONS="-Xmx30g"
export _JAVA_OPTIONS="-Xmx32g -Xss2m"

$HOME/local/miniconda3/envs/buhayra/bin/python $HOME/proj/buhayra "sar2sigma year month" $1 $2
