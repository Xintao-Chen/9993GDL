import os
import time
import json
import uuid
import argparse
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def cancel_all_queued():
    page = client.batches.list(limit=50)
    total_cancelled = 0

    while True:
        for b in page.data:
            if getattr(b, "status", None) in ("in_progress", "validating", "finalizing"):
                print(f"发现 {b.status} 批次: {b.id} → 尝试取消")
                try:
                    client.batches.cancel(b.id)
                    print(f"✅ 已取消 {b.id}")
                    total_cancelled += 1
                except Exception as e:
                    print(f"❌ 取消 {b.id} 失败: {e}")

        if not page.has_more:
            break
        page = client.batches.list(limit=50, before=page.last_id)

    print(f"完成: 共取消 {total_cancelled} 个批次。")

if __name__ == "__main__":
    cancel_all_queued()

# jsonl_path = "batch_output.jsonl"

# # 你的 Batch ID
# batch_id = "batch_689730fb9e9481909e1a67db7c3c4384"

# # 获取 batch 详情
# batch = client.batches.retrieve(batch_id)

# # 下载 Output 文件
# if batch.output_file_id:
#     output_file = client.files.content(batch.output_file_id)
#     with open(jsonl_path, "wb") as f:
#         f.write(output_file.read())
#     print("✅ Output 文件已保存为 batch_output.jsonl")


# output_dir = "/srv/scratch/z5485311/GDL2NL/result/gpt-4o/one_shot"
# with open(jsonl_path, "r", encoding="utf-8") as f:
#     for line in f:
#         if not line.strip():  # 跳过空行
#             continue
#         data = json.loads(line)  # 把这一行转成 Python 字典

#         custom_id = data.get("custom_id", "")
#         content = (
#             data.get("response", {})
#                 .get("body", {})
#                 .get("choices", [{}])[0]
#                 .get("message", {})
#                 .get("content", "")
#         )

#         if custom_id and content:
#             filename = f"{custom_id.replace('_NL', '')}.kif"
#             filepath = os.path.join(output_dir, filename)
#             with open(filepath, "w", encoding="utf-8") as out:
#                 out.write(content)
