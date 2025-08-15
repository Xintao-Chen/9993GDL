import os
import yaml
from openai import OpenAI
from openai import APIError

# === 初始化 OpenAI 客户端 ===
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY")
)

# === 加载 prompt 模板 ===
with open("NL2GDL.yaml", "r", encoding="utf-8") as f:
    prompt_data = yaml.safe_load(f)

# === 输入输出路径设置 ===
input_dir = "/srv/scratch/z5485311/GDL2NL/ggp_dataset/level1_5sample"
output_dir = "/srv/scratch/z5485311/GDL2NL/game_checker/gamechecker/games/gpt/level1_5sample"  # 与输入目录相同，原地生成 .txt 文件

# === 遍历 .kif 文件 ===
for filename in os.listdir(input_dir):
    if filename.endswith(".txt"):
        file_path = os.path.join(input_dir, filename)
        
        with open(file_path, "r", encoding="utf-8") as f:
            game_description = f.read()
        
        prompt_data[1]["content"] = game_description

        try:
            # === 调用 GPT-4o 接口生成自然语言描述 ===
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=prompt_data,
                temperature=0.3,
                max_tokens=2048
            )

            output_str = response.choices[0].message.content

            # === 输出路径 ===
            base_name = os.path.splitext(filename)[0]
            output_path = os.path.join(output_dir, base_name + ".kif")

            with open(output_path, "w", encoding="utf-8") as f_out:
                f_out.write(output_str)

            print(f"✅ Processed: {filename} → {output_path}")

        except APIError as e:
            print(f"❌ OpenAI API Error while processing {filename}: {e}")
        except Exception as e:
            print(f"❌ Other Error while processing {filename}: {e}")
