from pathlib import Path


def load_prompt(prompt_path: str):
    path = Path(__file__).parents[2] / "prompts" / f"{prompt_path}.prompt"
    return path.read_text(encoding="utf-8")

if __name__ == '__main__':
    prompt_content = load_prompt("correct_sql")
    print(prompt_content)