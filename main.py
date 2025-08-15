from LLM.models.utils import setup_llm
from LLM.models.llm import LLMConfig

def main():
    # 创建配置
    config = LLMConfig(
        engine="llama3",
        tokenizer="meta-llama/Meta-Llama-3.1-8B-Instruct",  # 或者你的本地路径
        cache_dir="./.cache",
        temperature=0.7,
        input_max_tokens=2048,
        output_max_tokens=2048,
        top_p=0.9,
        repetition_penalty=1.0,
        freq_penalty=0.0,
        load_in_4bit=False,   # 如果你用量化模型，否则设为 False
        load_in_8bit=False,
        model_name="meta-llama/Meta-Llama-3.1-8B-Instruct",  # 必须和 tokenizer 保持一致
    )

    # 加载 prompt 模板
    with open("prompt/prompt_template.yaml", "r") as f:
        prompt_data = yaml.safe_load(f)

    # 替换游戏描述
    game_description = "Tic-Tac-Toe is played by two players who take turns. The game is played on a 3x3 square grid. Each player takes turns placing their symbol on an empty cell: the first player uses “X”, and the second player uses “O”. A player wins if they manage to place three of their symbols in a straight line—either in the same row, the same column, or diagonally. If all cells are filled and no player has won, the game ends in a draw."

    system_prompt = prompt_data["system"]
    user_prompt = prompt_data["user_template"].replace("{{description}}", game_description)

    llm = setup_llm(config)

    res = llm._sample_completions(sys_prompt, user_prompt)

if __name__ == "__main__":
    main()