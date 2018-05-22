#!/bin/bash
exec 1>5.2_validation_funceme.log 2>&1

source $HOME/local/miniconda2/bin/activate $HOME/local/miniconda2/envs/requests

python $HOME/proj/buhayra "update validation"
