#!/bin/bash
#PBS -N 4_insert
#PBS -M martinsd@uni-potsdam.de
#PBS -j oe
#PBS -l ncpus=1
#PBS -l nodes=1:ppn=1
#PBS -l walltime=24:00:00
#PBS -l mem=5gb

source activate fiorio_orson
python /users/stud09/martinsd/proj/buhayra "insert"
