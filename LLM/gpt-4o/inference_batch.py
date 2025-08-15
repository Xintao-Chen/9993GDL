import json
import os
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

batch_jsonl_path = "/srv/scratch/z5485311/GDL2NL/jsonl/NL2GDL_zero_shot_BNF.jsonl"

with open(batch_jsonl_path, "rb") as f:
    batch_input_file = client.files.create(
        file=f,
        purpose="batch"
    )

batch = client.batches.create(
    input_file_id=batch_input_file.id,
    endpoint="/v1/chat/completions",
    completion_window="24h",
    metadata={"project": "GDL-gdl2nl"}
)

# ✅ 修复：转成 dict 再保存
with open("batch_metadata.json", "w", encoding="utf-8") as f:
    json.dump(batch.model_dump(), f, ensure_ascii=False, indent=2)

with open("batch_tracking_ids.txt", "w", encoding="utf-8") as f:
    f.write(f"input_file_id: {batch_input_file.id}\n")
    f.write(f"batch_id: {batch.id}\n")
    f.write(f"status: {batch.status}\n")

print("✅ Batch 创建成功，已保存 metadata 和 ID")

