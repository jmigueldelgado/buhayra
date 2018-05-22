#!/bin/bash
exec 1>5.2_validation_funceme.log 2>&1

source /users/stud09/martinsd/local/miniconda2/bin/activate /users/stud09/martinsd/local/miniconda2/envs/requests

python /users/stud09/martinsd/proj/buhayra "update validation"
