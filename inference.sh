#!/bin/bash
#PBS -M z5485311@ad.unsw.edu.au
#PBS -m ae
#PBS -l select=1:ncpus=4:mem=24gb
#PBS -l walltime=05:00:00
#PBS -j oe

# 进入工作目录
cd $PBS_O_WORKDIR

export base_dir="/srv/scratch/$USER/GDL2NL/"
export env_path="$base_dir/myeny"
module purge
module load python
source "$env_path/bin/activate"

python LLM/gpt-4o/inference.py --flag="zero_shot"
#python LLM/gpt-4o/inference.py --flag="one_shot"
#python LLM/gpt-4o/inference.py --flag="zero_shot_BNF"
#python LLM/gpt-4o/inference.py --flag="one_shot_BNF"

#For iterative generation use:
#python LLM/gpt_loop/loop.py --max_iterative 5

