input_path = "NL2GDL_batch.jsonl"  # 原始 jsonl 文件路径
output_prefix = "NL2GDL_split_part_"   # 输出文件前缀
num_parts = 3                   # 想分成的份数

# 读取所有行
with open(input_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 每份多少行（最后一份可能多一点）
avg = len(lines) // num_parts
remainder = len(lines) % num_parts

start = 0
for i in range(num_parts):
    # 计算这一份的结束位置
    end = start + avg + (1 if i < remainder else 0)
    part_lines = lines[start:end]

    # 写入新文件
    with open(f"{output_prefix}{i+1}.jsonl", 'w', encoding='utf-8') as out:
        out.writelines(part_lines)

    start = end

print(f"✅ 已将 {len(lines)} 行平均分成 {num_parts} 个文件。")
