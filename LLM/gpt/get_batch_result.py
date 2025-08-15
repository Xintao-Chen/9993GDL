import os
import json
from openai import OpenAI

# ====== 配置 ======
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY")
)

batch_id = "batch_6894b0ea2f948190bc61f1fc8bba8b56"
output_dir = "/srv/scratch/z5485311/GDL2NL/LLM/gpt/batch_result"
os.makedirs(output_dir, exist_ok=True)

# ====== 获取 batch ======
batch = client.batches.retrieve(batch_id)
if batch.status != "completed" or not batch.output_file_id:
    raise RuntimeError(f"❌ Batch 未完成或无输出，当前状态：{batch.status}")

# ====== 下载并处理数据流 ======
output_stream = client.files.content(batch.output_file_id)

count = 0
for line in output_stream.iter_lines():
    if not line:
        continue
    item = json.loads(line)

    custom_id = item.get("custom_id", f"gdl_{count+1}")
    response = item.get("response", {})

    if "body" not in response or "choices" not in response["body"]:
        error_message = response.get("error", {}).get("message", "Unknown error")
        print(f"⚠️ 请求 {custom_id} 没有生成 GDL,原因: {error_message}")
        continue

    gdl_content = response["body"]["choices"][0]["message"]["content"].strip()
    output_path = os.path.join(output_dir, f"{custom_id}.kif")

    with open(output_path, "w", encoding="utf-8") as fout:
        fout.write(gdl_content)

    count += 1

print(f"✅ 已成功写入 {count} 个 GDL 文件到目录：{output_dir}")
