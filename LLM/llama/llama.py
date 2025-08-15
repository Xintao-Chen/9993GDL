import os
import yaml
import torch
from transformers import pipeline

# 初始化 LLaMA pipeline
model_id = "meta-llama/Meta-Llama-3.1-8B-Instruct"
pipe = pipeline(
    "text-generation",
    model=model_id,
    model_kwargs={"torch_dtype": torch.bfloat16},
    device_map="auto"
)

# 加载 prompt 模板
with open("prompt/NL2GDL_one_shot_BNF.yaml", "r") as f:
    prompt_data = yaml.safe_load(f)

input_dir = "dataset/level1"
output_dir = "result/llama/one_shot_BNF"

for filename in os.listdir(input_dir):
    if filename.endswith(".txt"):
        file_path = os.path.join(input_dir, filename)

        with open(file_path, "r", encoding="utf-8") as f:
            game_description = f.read()
        
        prompt_data[1]["content"] = game_description

        outputs = pipe(
            prompt_data,
            max_new_tokens=2048,
        )

        output_str = outputs[0]["generated_text"][-1]

        # === 输出路径 ===
        base_name = os.path.splitext(filename)[0]
        base_name = base_name.replace("_NL", "")
        output_path = os.path.join(output_dir, base_name + ".kif")

        with open(output_path, "w", encoding="utf-8") as f_out:
            f_out.write(output_str["content"])

            print(f"✅ Processed: {filename} → {output_path}")

