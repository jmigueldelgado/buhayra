#!/bin/bash
exec 1>5_insert_polys_mongo.log 2>&1

source /users/stud09/martinsd/local/miniconda2/bin/activate /users/stud09/martinsd/local/miniconda2/envs/mongodb

python /users/stud09/martinsd/proj/buhayra "insert"
