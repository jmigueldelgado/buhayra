#!/bin/bash

source activate buhayra

export JAVA_TOOL_OPTIONS="-Xmx16g"
export _JAVA_OPTIONS="-Xmx18g -Xss2m"

python $HOME/proj/buhayra "sar2sigma"
