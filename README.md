# GDL2NL Project

This project is designed to run and evaluate multiple prompting strategies for automatically generating GDL (Game Description Language) code from natural language using Large Language Models (LLMs).

---

## 1. Environment Setup

### 1.1 Install Eclipse
Download and install Eclipse from the [official website](https://www.eclipse.org/downloads/).  
If your workflow requires GDL parsing, you will also need Eclipse Prolog support.

### 1.2 Create and Configure a Python Virtual Environment
```bash
python -m venv myeny
source myeny/bin/activate    # Linux / macOS
# myeny\Scripts\activate     # Windows
pip install -r requirements.txt
export OPENAI_API_KEY="your key"
```

Once the environment is ready:
- Use `inference.sh` to run **GPT-4o inference** with different prompting strategies.
- Use `evaluate.sh` to perform **evaluation** across multiple prompting strategies and generate analysis plots.

---

## 2. Script Descriptions

### 2.1 `inference.sh`

**Contents**
```bash
#!/bin/bash

# Go to working directory
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

# For iterative generation use:
# python LLM/gpt_loop/loop.py --max_iterative 5
```

**Usage**
```bash
bash inference.sh
```
- Change the `--flag` parameter to select a different prompting strategy:
  - `zero_shot`
  - `one_shot`
  - `zero_shot_BNF`
  - `one_shot_BNF`
- For iterative generation:
```bash
python LLM/gpt_loop/loop.py --max_iterative 5
```

---

### 2.2 `evaluate.sh`

**Contents**
```bash
#!/bin/bash
#PBS -M z5485311@ad.unsw.edu.au
#PBS -m ae
#PBS -l select=1:ncpus=4:mem=24gb
#PBS -l walltime=05:00:00
#PBS -j oe

# Go to working directory
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
```

**Usage**
```bash
qsub evaluate.sh
```
- This is a PBS job script for the Katana HPC cluster.
- Runs evaluations for multiple prompting strategies.
- Generates analysis plots using `draw.py`.
- Parameters:
  - `--flag` selects the prompting strategy.
  - `--txt` specifies the analysis file path.
  - `--title` sets the plot title.

---

## 3. Notes
- All secret files (e.g., `.env`) **must be added to `.gitignore`** to avoid accidentally committing sensitive information.
- Ensure your OpenAI API key is valid and that your network can access the OpenAI API.
- Adjust `select`, `mem`, and `walltime` in PBS scripts as needed based on your compute requirements.
