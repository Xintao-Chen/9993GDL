import os
import json

# 替换成你的文件夹路径
folder_path = "/srv/scratch/z5485311/GDL2NL/ggp_dataset/grouped_by_level/cleaned_level"

# 收集所有NL.txt文件
nl_files = [f for f in os.listdir(folder_path) if f.endswith("_NL.txt")]

# 输出文件路径
output_path = "llama_gdl_finetune_dataset.json"

# 存储所有记录
records = []

for nl_file in nl_files:
    base_name = nl_file.replace("_NL.txt", "")
    kif_file = f"{base_name}.kif"

    nl_path = os.path.join(folder_path, nl_file)
    kif_path = os.path.join(folder_path, kif_file)

    if not os.path.exists(kif_path):
        print(f"⚠️ 找不到对应的 kif 文件: {kif_file}")
        continue

    with open(nl_path, "r", encoding="utf-8") as f_nl, open(kif_path, "r", encoding="utf-8") as f_kif:
        nl_text = f_nl.read().strip()
        kif_text = f_kif.read().strip()

        record = {
            "instruction": "You are an expert in the Game Description Language (GDL) used by the General Game Playing community. Your task is to translate the provided natural-language rules into GDL.",
            "input": nl_text,
            "output": kif_text
        }

        records.append(record)

# 写入 json 文件（列表形式）
with open(output_path, "w", encoding="utf-8") as outfile:
    json.dump(records, outfile, ensure_ascii=False, indent=2)

print(f"✅ 成功将 {len(records)} 条样本写入 {output_path}")
