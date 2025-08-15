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

python evaluate/evaluate_class.py --flag="zero_shot"
python evaluate/evaluate_class.py --flag="zero_shot_BNF"
python evaluate/evaluate_class.py --flag="one_shot"
python evaluate/evaluate_class.py --flag="one_shot_BNF"
python evaluate/evaluate_class.py --flag="iterative"
python evaluate/evaluate_class.py --flag="llama_one_shot_BNF"
python evaluate/evaluate_class.py --flag="SFT_llama_one_shot_BNF"

python evaluate/draw.py --txt "evaluate/gpt-4o/zero_shot/analyze.txt"  --title "zero_shot"
python evaluate/draw.py --txt "evaluate/gpt-4o/zero_shot_BNF/analyze.txt" --title "zero_shot_BNF"
python evaluate/draw.py --txt "evaluate/gpt-4o/one_shot/analyze.txt" --title "one_shot"
python evaluate/draw.py --txt "evaluate/gpt-4o/one_shot_BNF/analyze.txt" --title "one_shot_BNF"
python evaluate/draw.py --txt "evaluate/gpt-4o_iterative/analyze.txt" --title "gpt-4o-iterative"
python evaluate/draw.py --txt "evaluate/llama/one_shot_BNF/analyze.txt" --title "llama"
python evaluate/draw.py --txt "evaluate/llama/SFT_one_shot_BNF/analyze.txt" --title "SFT-llama"