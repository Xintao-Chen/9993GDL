import os, json, time, argparse, subprocess, re
from enum import Enum
from openai import OpenAI, APIError
import tiktoken

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
_enc = tiktoken.encoding_for_model("gpt-4o")

class CheckResult(Enum):
    PASSED = "PASS"
    SYNTAX_FAIL = "SYNTAX_FAIL"
    SEMANTIC_RULE_FAIL = "SEMANTIC_RULE_FAIL"
    SEMANTIC_LOGIC_FAIL = "SEMANTIC_LOGIC_FAIL"

def run_checker(gdl_file_path, checker_script):
    result = subprocess.run(
        [checker_script, "--mc-time=5", gdl_file_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=30
    )
    output = result.stdout + result.stderr

    _ids = _enc.encode(output) 
    if len(_ids) >= 1000:
        _ids = _ids[:1000]
        output = _enc.decode(_ids) 

    if "gdl parse error before" in output:
        result_flag = CheckResult.SYNTAX_FAIL
    elif "ERROR: unsafe rule" in output:
        result_flag = CheckResult.SEMANTIC_RULE_FAIL
    elif "checking game tree with random walks" in output and "ERROR:" in output:
        result_flag = CheckResult.SEMANTIC_LOGIC_FAIL
    else:
        result_flag = CheckResult.PASSED

    return result_flag, output
def init_call_line(line_obj):
    body = line_obj["body"]
    kif_filename = line_obj["custom_id"].replace("_NL", ".kif")

    for attempt in range(5):
        try:
            resp = client.chat.completions.create(
                model=body["model"],
                messages=body["messages"],
                temperature=body.get("temperature", 0.3),
                max_tokens=body.get("max_tokens", 3000),
            )
            return resp.choices[0].message.content, kif_filename
        except Exception:
            if attempt == 4:
                raise
            time.sleep(2 ** attempt)

def iterative_call_gpt(line_obj, gdl_file_path, checker_script, iterative_count, flag):
    while(iterative_count > 0):
        
        result_flag, error_msg = run_checker(gdl_file_path, checker_script)
        if (result_flag == CheckResult.PASSED):
            flag[0] = True
            return iterative_count
        
        with open(gdl_file_path, "r", encoding="utf-8") as f:
            error_gdl = f.read()

        msg = []
        for m in line_obj["body"]["messages"]:
            if m["role"] in ("system",):
                msg.append(m)
            elif m["role"] == "user":
                msg.append(m)
                break
        
        msg.append({
            "role": "assistant",
            "content": error_gdl,
        })
        msg.append({
            "role": "user",
            "content": (
                "The previous GDL failed the game check.\n"
                f"Error message:\n{error_msg}\n\n"
                "Please return a fully corrected GDL only. Do not include any explanations."
            )
        })

        resp = client.chat.completions.create(
            model="gpt-4o",
            messages=msg,
            temperature= 0.3,
            max_tokens=3000,
        )

        corrected_gdl = resp.choices[0].message.content

        with open(gdl_file_path, "w", encoding="utf-8") as fout:
            fout.write(corrected_gdl)

        iterative_count -= 1
    
    return  iterative_count

def run_jsonl(jsonl_path, output_dir, checker_script, iterative_count=3):
    
    os.makedirs(output_dir, exist_ok=True)

    with open(jsonl_path, "r", encoding="utf-8") as fin:
        for i, line in enumerate(fin, 1):
            if not line.strip():
                continue

            obj = json.loads(line)
            content, kif_filename = init_call_line(obj)

            out_file = os.path.join(output_dir, os.path.basename(kif_filename))

            os.makedirs(os.path.dirname(out_file), exist_ok=True)
            with open(out_file, "w", encoding="utf-8") as fout:
                fout.write(content)

            flag = [False]
            it_count = iterative_call_gpt(obj, out_file, checker_script, iterative_count, flag)
            print(kif_filename, it_count, flag)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Iterative GPT-4o")
    parser.add_argument(
        "--max_iterative",
        default=3,             # 默认值 3
        type=int,              # 转成整数
        help="Max iterative time (default: 3)"
    )
    args = parser.parse_args()

    input_dir = "jsonl/NL2GDL_one_shot_BNF.jsonl"
    output_dir = "result/gpt-4o_iterative"
    checker_script = "game_checker/gamechecker/gamechecker.sh"

    run_jsonl(input_dir, output_dir, checker_script, iterative_count=args.max_iterative)