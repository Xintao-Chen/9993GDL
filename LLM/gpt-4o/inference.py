import os
import time
import json
import uuid
import argparse
from openai import OpenAI
import yaml

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def call_line(line_obj):
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

def run_jsonl(jsonl_path, output_dir):
    
    os.makedirs(output_dir, exist_ok=True)

    with open(jsonl_path, "r", encoding="utf-8") as fin:
        for i, line in enumerate(fin, 1):
            if not line.strip():
                continue

            obj = json.loads(line)
            content, kif_filename = call_line(obj)

            out_file = os.path.join(output_dir, os.path.basename(kif_filename))

            os.makedirs(os.path.dirname(out_file), exist_ok=True)
            with open(out_file, "w", encoding="utf-8") as fout:
                fout.write(content)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run GPT requests from JSONL and save each as .kif")
    parser.add_argument("--flag", required=True, choices=["zero_shot", "one_shot", "zero_shot_BNF", "one_shot_BNF"], help="Choose prompt type")
    args = parser.parse_args()

    if args.flag == "zero_shot":
        jsonl_file = "jsonl/NL2GDL_zero_shot.jsonl"
        out_path = "result/gpt-4o/zero_shot"
    elif args.flag == "one_shot":
        jsonl_file = "jsonl/NL2GDL_one_shot.jsonl"
        out_path = "result/gpt-4o/one_shot"
    elif args.flag == "zero_shot_BNF":
        jsonl_file = "jsonl/NL2GDL_zero_shot_BNF.jsonl"
        out_path = "result/gpt-4o/zero_shot_BNF"
    elif args.flag == "one_shot_BNF":
        jsonl_file = "jsonl/NL2GDL_one_shot_BNF.jsonl"
        out_path = "result/gpt-4o/one_shot_BNF"
    else:
        raise ValueError("Unsupported flag")

    run_jsonl(jsonl_file, out_path)