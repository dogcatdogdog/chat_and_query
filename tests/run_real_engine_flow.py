import sys
import os
import json

# 确保能导入 src
sys.path.append(os.getcwd())

from src.engine import engine, ChatHistory

def run_real_test(user_query: str):
    print(f"Executing real engine process for query: {user_query}")
    history = []
    try:
        response = engine.process(user_query, history)
        print("\n" + "="*60)
        print("FINAL CHAT RESPONSE OBJECT")
        print("="*60)
        print(json.dumps(response.model_dump(), indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Error during execution: {e}")

if __name__ == "__main__":
    # 使用用户提供的复杂查询
    test_query = "帮我查一下有几个任务，并统计一下任务的成功率"
    run_real_test(test_query)
