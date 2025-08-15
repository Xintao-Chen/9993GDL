import argparse
import os
import re
import subprocess
import sys
from datetime import datetime
from typing import Tuple, Dict, Any, List
from enum import Enum

# ✅ 设置 GDL 文件目录（.kif 文件所在目录）
gdl_dir = "/srv/scratch/z5485311/GDL2NL/LLM/gpt/batch_result"
#gdl_dir = "/srv/scratch/z5485311/GDL2NL/game_checker/gamechecker/games/gpt/test"
checker_script = "/srv/scratch/z5485311/GDL2NL/game_checker/gamechecker/gamechecker.sh"

class CheckResult(Enum):
    PASSED = "PASS"
    SYNTAX_FAIL = "SYNTAX_FAIL"
    SEMANTIC_RULE_FAIL = "SEMANTIC_RULE_FAIL"
    SEMANTIC_LOGIC_FAIL = "SEMATNTIC_LOGIC_FAIL"

def run_checker(gdl_file_path):
    result = subprocess.run(
        [checker_script, "--mc-time=5", gdl_file_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=30
    )
    output = result.stdout + result.stderr
    if "error while parsing gdl!" in output:
        result_flag = CheckResult.SYNTAX_FAIL
    elif "ERROR: unsafe rule" in output:
        result_flag = CheckResult.SEMANTIC_RULE_FAIL
    elif "checking game tree with random walks" in output and "ERROR:" in output:
        result_flag = CheckResult.SEMANTIC_LOGIC_FAIL
    else:
        result_flag = CheckResult.PASSED

    return result_flag, result.stdout + result.stderr

total = 0
files = {
    CheckResult.PASSED: 0,
    CheckResult.SYNTAX_FAIL: 0,
    CheckResult.SEMANTIC_RULE_FAIL: 0,
    CheckResult.SEMANTIC_LOGIC_FAIL: 0,
}

for filename in os.listdir(gdl_dir):
    if not filename.endswith(".kif"):
        continue

    total += 1
    file_path = os.path.join(gdl_dir, filename)

    result_flag, _ = run_checker(file_path)

    # 按分类统计
    files[result_flag] += 1

print("总数:", total)
for k, v in files.items():
    print(k.name, v)