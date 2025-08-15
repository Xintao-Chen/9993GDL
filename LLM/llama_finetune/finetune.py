from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer, default_data_collator
from peft import get_peft_model, LoraConfig, TaskType
from datasets import load_dataset
import torch
import os
import pandas as pd
import matplotlib.pyplot as plt

# === 模型名称和路径 ===
base_model = "meta-llama/Meta-Llama-3.1-8B-Instruct"
data_path = "/srv/scratch/z5485311/GDL2NL/LLM/llama_finetune/llama_gdl_finetune_dataset.json"  # ← 你生成的数据集路径
output_dir = "/srv/scratch/z5485311/GDL2NL/LLM/llama_finetune/llama3_finetuned_2"

# === 加载 tokenizer 和模型 ===
tokenizer = AutoTokenizer.from_pretrained(base_model)
tokenizer.pad_token = tokenizer.eos_token  # 避免 padding 报错

dataset = load_dataset("json", data_files=data_path)["train"]

def format(batch):
    input_ids_list = []
    labels_list = []

    for ins, inp, out in zip(batch["instruction"], batch["input"], batch["output"]):
        prompt = f"### Instruction:\n{ins}\n\n### Input:\n{inp}\n\n### Response:\n"
        prompt_tokens = tokenizer(prompt, truncation=True, max_length=2048, add_special_tokens=False)
        output_tokens = tokenizer(out, truncation=True, max_length=2048, add_special_tokens=False)

        input_ids = prompt_tokens["input_ids"] + output_tokens["input_ids"]
        input_ids = input_ids[:4096]
        labels = [-100] * len(prompt_tokens["input_ids"]) + output_tokens["input_ids"]
        labels = labels[:4096]

        # padding
        pad_len = 4096 - len(input_ids)
        input_ids += [tokenizer.pad_token_id] * pad_len
        labels += [-100] * pad_len

        input_ids_list.append(input_ids)
        labels_list.append(labels)

    return {"input_ids": input_ids_list, "labels": labels_list}

# === 执行 map（batch_size=32）===
tokenized_dataset = dataset.map(
    format,
    batched=True,
    batch_size=32,
    remove_columns=dataset.column_names
)

model = AutoModelForCausalLM.from_pretrained(
    base_model,
    device_map="auto",
    torch_dtype=torch.bfloat16
)

lora_config = LoraConfig(
    r=8,
    lora_alpha=16,
    lora_dropout=0.05,
    bias="none",
    task_type=TaskType.CAUSAL_LM
)

model = get_peft_model(model, lora_config)
model.print_trainable_parameters()  # 🔍 显示哪些参数是可训练的（LoRA adapter）

training_args = TrainingArguments(
    output_dir=output_dir,
    num_train_epochs=5,
    per_device_train_batch_size=1,
    gradient_accumulation_steps=4,
    learning_rate=5e-6,
    logging_dir=output_dir + "/logs",
    logging_steps=10,
    save_strategy="epoch",
    bf16=True,                    # ✅ 推荐使用 bf16
    fp16=False,                   # ❌ 禁用 fp16 避免 unscale 报错
    gradient_checkpointing=False,  # ✅ H200显存足够可以关掉
    max_grad_norm=1.0,            # 或设置为 0.0（关闭 clip）
    label_names=["labels"],
    report_to="none"
)


trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset,
    tokenizer=tokenizer,
    data_collator=default_data_collator,
)

trainer.train()

model.save_pretrained(output_dir)

loss_logs = [x for x in trainer.state.log_history if 'loss' in x]
df = pd.DataFrame(loss_logs)  # 通常包含: step, loss, learning_rate, epoch

# 可选：保存原始日志为 CSV，便于复用
df.to_csv(f"{output_dir}/loss_history.csv", index=False)

# 绘图（注意：不要指定颜色；一张图一个曲线）
plt.figure()
plt.plot(df["step"], df["loss"])
plt.xlabel("Step")
plt.ylabel("Training Loss")
plt.title("Supervised Fine-Tuning Loss (LLaMA 3.1-8B-Instruct)")
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(f"{output_dir}/loss_curve.png", dpi=200)