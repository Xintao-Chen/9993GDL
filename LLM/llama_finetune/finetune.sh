#!/bin/bash
#PBS -M z5485311@ad.unsw.edu.au
#PBS -m ae
#PBS -l select=1:ncpus=4:mem=48GB:ngpus=1:gpu_model=H200
#PBS -l walltime=02:00:00
#PBS -j oe

cd $PBS_O_WORKDIR

module load python

source /srv/scratch/z5485311/GDL2NL/myeny/bin/activate

python finetune.py