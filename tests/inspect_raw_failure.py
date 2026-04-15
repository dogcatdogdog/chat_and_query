import sys
import os

# 添加当前目录到路径
sys.path.append(os.getcwd())

from src.client import LLMClient

def inspect_failures():
    llm = LLMClient()
    
    with open("prompts/router_prompt.md", "r", encoding="utf-8") as f:
        prompt = f.read()

    fail_queries = [
        "asdfghjkl;''123123",
        "今天中午吃什么好呢？"
    ]

    print("\n" + "="*60)
    print("🔍 探测失败用例的 LLM 原始输出 (Raw Inspection)")
    print("="*60)

    for q in fail_queries:
        print(f"\n[输入]: {q}")
        raw_res = llm.call_llm(prompt, q, [])
        print("-" * 20 + " [RAW OUTPUT] " + "-" * 20)
        print(f"'{raw_res}'")
        print("-" * 54)

    print("\n" + "="*60)

if __name__ == "__main__":
    inspect_failures()
