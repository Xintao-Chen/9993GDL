import argparse
import os
import matplotlib.pyplot as plt

def read_counts(txt_path):
    total = 0
    counts = {"PASSED": 0, "SYNTAX_FAIL": 0, "SEMANTIC_RULE_FAIL": 0, "SEMANTIC_LOGIC_FAIL": 0}
    with open(txt_path, "r", encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if not s:
                continue
            if s.startswith("Total:"):
                total = int(s.split(":")[1].strip())
            else:
                parts = s.split()
                if len(parts) == 2 and parts[0] in counts:
                    counts[parts[0]] = int(parts[1])
    return total, counts

def main(txt_path, out_path=None, title=None):

    # 如果没传 title，就自动用路径里的模型配置名
    if title is None:
        title = "GDL Evaluation Funnel"

    total, c = read_counts(txt_path)
    if total <= 0:
        raise ValueError("Total must be > 0 in analyze.txt")

    # 漏斗每层数量
    syntax_pass = total - c.get("SYNTAX_FAIL", 0)
    rule_pass = syntax_pass - c.get("SEMANTIC_RULE_FAIL", 0)
    playability_pass = c.get("PASSED", 0)

    stages = ["Total", "Syntax Pass", "Rule Safety Pass", "Playability Pass"]
    values = [total, syntax_pass, rule_pass, playability_pass]

    # 条件比例
    cond_pcts = [1.0] + [(values[i] / values[i-1] if values[i-1] else 0.0) for i in range(1, len(values))]

    # 绘图
    plt.figure(figsize=(7, 5))
    for i, (v, p) in enumerate(zip(values, cond_pcts)):
        plt.barh(i, v, height=0.6)
        plt.text(v + max(total * 0.01, 0.5), i, f"{v} ({p*100:.1f}%)", va="center", fontsize=10)

    plt.yticks(range(len(stages)), stages)
    plt.gca().invert_yaxis()
    plt.xlabel("Number of Games")
    plt.title(title)
    plt.tight_layout()

    if out_path is None:
        base_dir = os.path.dirname(os.path.abspath(txt_path))
        out_path = os.path.join(base_dir, "funnel.png")
    else:
        os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)

    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Saved funnel to: {out_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Draw a funnel chart from analyze.txt")
    parser.add_argument("--txt", required=True, help="Path to analyze.txt")
    parser.add_argument("--out", default=None, help="Output image path (default: alongside txt as funnel.png)")
    parser.add_argument("--title", default="GDL Evaluation Funnel", help="Figure title")
    args = parser.parse_args()
    main(args.txt, args.out, args.title)