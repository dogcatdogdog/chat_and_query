import sys
import os
import json

# 添加当前目录到路径
sys.path.append(os.getcwd())

from src.client import LLMClient

def verify_example_contamination():
    llm = LLMClient()
    
    # 模拟 Responder Prompt (含示例)
    with open("prompts/responder_prompt.md", "r", encoding="utf-8") as f:
        prompt_template = f.read()

    # 1. 只有一台设备的数据 (UAV-DEBUG)
    single_device_data = {
        "id": "UAV-DEBUG",
        "name": "测试机",
        "status": "online",
        "battery": 95,
        "flightHours": 10
    }

    # 替换背景数据
    system_prompt = prompt_template.replace("{context_data}", json.dumps(single_device_data, ensure_ascii=False))
    
    user_message = "帮我查询 UAV-DEBUG 的信息"
    
    print("\n" + "="*50)
    print("复现提示词示例污染 (Prompt Contamination Check)")
    print("="*50)
    print(f"输入数据量: 1 台设备 (UAV-DEBUG)")
    print("-" * 30)

    # 调用 LLM
    response = llm.call_llm(system_prompt, user_message, [])
    
    print(f"LLM 实际输出:\n{response}")
    
    if "18" in response:
        print("\n[判定结果]: 失败 (存在示例污染 - 模型输出了示例中的 18 台)")
    else:
        print("\n[判定结果]: 成功 (模型根据实际数据进行了回答)")
    
    print("="*50)

if __name__ == "__main__":
    verify_example_contamination()
