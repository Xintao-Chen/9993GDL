import os
import json
import uuid
import yaml

def load_yaml_template(yaml_path):
    with open(yaml_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, list):
        raise ValueError("YAML 模板需为 [{role, content}, ...] 列表。")
    for item in data:
        if "role" not in item or "content" not in item:
            raise ValueError("YAML 每项必须包含 role 和 content。")
    return data

def build_messages(template_messages, user_content):
    msgs, replaced = [], False
    for m in template_messages:
        role, content = m["role"], m["content"]
        if role == "user":
            content = content.replace("<description>", user_content) if "<description>" in content else user_content
            replaced = True
        msgs.append({"role": role, "content": content})
    if not replaced:
        msgs.append({"role": "user", "content": user_content})
    return msgs

def create_jsonl(
    input_dir,
    output_dir="prompts",
    output_filename="batch.jsonl",
    yaml_path=None,
    model="gpt-4o",
    temperature=0.3,
    max_tokens=3000,
    endpoint="/v1/chat/completions",
):
    if yaml_path is None:
        raise ValueError("yaml_path 不能为空")

    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, output_filename)

    template = load_yaml_template(yaml_path)

    txt_files = sorted([f for f in os.listdir(input_dir) if f.endswith(".txt")])
    count = 0

    with open(out_path, "w", encoding="utf-8") as fout:
        for filename in txt_files:
            file_path = os.path.join(input_dir, filename)
            with open(file_path, "r", encoding="utf-8") as f:
                game_description = f.read().strip()
            if not game_description:
                continue  # 跳过空文件

            messages = build_messages(template, game_description)

            line = {
                "custom_id": f"{os.path.splitext(filename)[0]}",
                "method": "POST",
                "url": endpoint,
                "body": {
                    "model": model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                },
            }
            fout.write(json.dumps(line, ensure_ascii=False) + "\n")
            count += 1

    print(f"✅ 写入 {out_path}，共 {count} 条。")

if __name__ == "__main__":
    input_dir = "dataset/level1"
    output_dir = "jsonl"
    output_zero_shot_filename = "NL2GDL_zero_shot.jsonl"
    zero_shot_yaml_path = "prompt/NL2GDL_zero_shot.yaml"
    output_zero_shot_BNF_filename = "NL2GDL_zero_shot_BNF.jsonl"
    zero_shot_BNF_yaml_path = "prompt/NL2GDL_zero_shot_BNF.yaml"
    output_one_shot_filename = "NL2GDL_one_shot.jsonl"
    one_shot_yaml_path = "prompt/NL2GDL_one_shot.yaml"
    output_one_shot_BNF_filename = "NL2GDL_one_shot_BNF.jsonl"
    one_shot_BNF_yaml_path = "prompt/NL2GDL_one_shot_BNF.yaml"

    create_jsonl(input_dir, output_dir, output_zero_shot_filename, zero_shot_yaml_path)
    create_jsonl(input_dir, output_dir, output_zero_shot_BNF_filename, zero_shot_BNF_yaml_path)
    create_jsonl(input_dir, output_dir, output_one_shot_filename, one_shot_yaml_path)
    create_jsonl(input_dir, output_dir, output_one_shot_BNF_filename, one_shot_BNF_yaml_path)
    