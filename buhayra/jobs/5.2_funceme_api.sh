#!/bin/bash
exec 1>5.2_validation_funceme.log 2>&1

source $HOME/miniconda3/bin/activate $HOME/miniconda3/envs/requests

python $HOME/proj/buhayra "update validation"
