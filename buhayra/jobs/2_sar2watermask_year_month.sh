#!/bin/bash

source activate buhayra

export JAVA_TOOL_OPTIONS="-Xmx30g"
export _JAVA_OPTIONS="-Xmx32g -Xss2m"

python $HOME/proj/buhayra "sar2sigma year month" $1 $2
