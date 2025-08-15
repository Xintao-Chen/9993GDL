import os
import subprocess

# ✅ 设置 GDL 文件目录（.kif 文件所在目录）
gdl_dir = "/srv/scratch/z5485311/GDL2NL/LLM/gpt/batch_result"

# ✅ 设置 GDL 检查脚本的绝对路径
checker_script = "/srv/scratch/z5485311/GDL2NL/game_checker/gamechecker/gamechecker.sh"

# ✅ 检查脚本路径是否存在
if not os.path.exists(checker_script):
    raise FileNotFoundError(f"❌ 找不到 checker 脚本: {checker_script}")

# ✅ 初始化计数器
total = 0
passed = 0
failed_files = []

# ✅ 遍历目录中所有 .kif 文件
for filename in os.listdir(gdl_dir):
    if not filename.endswith(".kif"):
        continue

    total += 1
    # 注意：传给 shell 的路径是相对于 gamechecker.sh 的路径
    file_path = os.path.join(gdl_dir, filename)

    print(f"\n🔍 Checking: {file_path}")
    result = subprocess.run(
        [checker_script, file_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    output = result.stdout + result.stderr
    print(output)  # 打印完整输出（含错误信息）

    if "-> ok" in output:
        passed += 1
    else:
        failed_files.append(filename)

# ✅ 输出最终统计结果
print("\n✅ 检查完成")
print(f"📄 总文件数: {total}")
print(f"✅ 语法合法: {passed}")
print(f"❌ 语法错误: {total - passed}")
print(f"📊 合法率: {passed / total * 100:.2f}%")

# ✅ 可选：列出失败的文件名
if failed_files:
    print("\n❌ 以下文件不合法：")
    for f in failed_files:
        print(f"  - {f}")
