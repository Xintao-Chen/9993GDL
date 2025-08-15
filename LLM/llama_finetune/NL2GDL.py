import os
import yaml
import torch
from transformers import pipeline
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer, default_data_collator
from peft import PeftModel

# ---------------- 1. 路径配置 ----------------
base_model_id = "meta-llama/Meta-Llama-3.1-8B-Instruct"
lora_ckpt_dir = "LLM/llama_finetune/llama3_finetuned" 
input_dir = "dataset/level1"
output_dir = "result/llama/one_shot_BNF"
os.makedirs(output_dir, exist_ok=True)

# ---------------- 2. 加载 tokenizer + 基座 + LoRA ----------------
tokenizer = AutoTokenizer.from_pretrained(base_model_id)
tokenizer.pad_token = tokenizer.eos_token             

base_model = AutoModelForCausalLM.from_pretrained(
    base_model_id,
    torch_dtype=torch.bfloat16,                       
    device_map="auto"
)

model = PeftModel.from_pretrained(base_model, lora_ckpt_dir)
model.eval()                     

# ---------------- 3. 构建 pipeline ----------------
pipe = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    device_map="auto",
    torch_dtype=torch.bfloat16                          # 与 model 一致
)


with open("prompt/NL2GDL_one_shot_BNF.yaml", "r") as f:
    prompt_data = yaml.safe_load(f)

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