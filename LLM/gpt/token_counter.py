import os
import yaml
import tiktoken

# 加载 prompt 模板
with open("NL.yaml", "r", encoding="utf-8") as f:
    prompt_data = yaml.safe_load(f)

system_prompt = prompt_data["prompt"]["description"]
user_template = "\n".join(prompt_data["prompt"]["requirements"])
user_prompt_template = system_prompt + "\n" + user_template + "\n\n{{description}}"

# 设置输入输出路径
input_dir = "/srv/scratch/z5485311/GDL2NL/ggp_dataset/game_with_description"
report_path = "/srv/scratch/z5485311/GDL2NL/ggp_dataset/with_des_token_report.txt"

# 使用 OpenAI 的 GPT-4o tokenizer
enc = tiktoken.encoding_for_model("gpt-4o")

total_tokens = 0
report_lines = []
report_lines.append("📊 各 .kif 文件 token 使用统计\n")

def count_message_tokens(messages, model="gpt-4o"):
    tokens_per_message = 3
    tokens_per_name = 1
    total = 0
    for m in messages:
        total += tokens_per_message
        for key, value in m.items():
            total += len(enc.encode(value))
            if key == "name":
                total += tokens_per_name
    total += 3  # assistant 回复消息起始补 3 个
    return total

# 遍历所有 .kif 文件
for filename in os.listdir(input_dir):
    if filename.endswith(".kif"):
        file_path = os.path.join(input_dir, filename)

        with open(file_path, "r", encoding="utf-8") as f:
            gdl_code = f.read()

        user_prompt = user_prompt_template.replace("{{description}}", gdl_code)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        num_tokens = count_message_tokens(messages)
        total_tokens += num_tokens

        line = f"{filename:<40} {num_tokens:>6} tokens"
        report_lines.append(line)

# 添加汇总信息
report_lines.append("\n🧾 总 token 数：{}".format(total_tokens))
report_lines.append("💰 GPT-4o 输入成本估算：${:.2f} USD".format(total_tokens / 1_000_000 * 5))

# 写入文件
with open(report_path, "w", encoding="utf-8") as out_f:
    out_f.write("\n".join(report_lines))

print(f"✅ Token 报告已写入：{report_path}")
