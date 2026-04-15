import sys
import os
import json
from typing import List, Dict, Any

# 将 src 目录添加到路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.engine import engine
from src.mock_api import mock_api

# --- 劫持器 (Interceptors) ---

captured_data = {
    "tool_calls": [],
    "api_calls": [],
    "responder_context": None
}

original_call_llm = engine.llm.call_llm
original_mock_call = mock_api.call

def wrapped_call_llm(prompt, message, history, tools=None):
    res = original_call_llm(prompt, message, history, tools)
    if tools: # Router 阶段
        captured_data["tool_calls"] = [
            {"name": tc.function.name, "args": json.loads(tc.function.arguments)} 
            for tc in (res.tool_calls or [])
        ]
    else: # Responder 阶段
        captured_data["responder_context"] = prompt
    return res

def wrapped_mock_call(method, params):
    res = original_mock_call(method, params)
    captured_data["api_calls"].append({
        "method": method,
        "params": params,
        "result": res
    })
    return res

# 注入劫持
engine.llm.call_llm = wrapped_call_llm
mock_api.call = wrapped_mock_call

def reset_capture():
    captured_data["tool_calls"] = []
    captured_data["api_calls"] = []
    captured_data["responder_context"] = None

def run_test_case(name: str, user_input: str):
    print(f"\n{'='*20} 测试案例: {name} {'='*20}")
    print(f"输入: {user_input}")
    
    reset_capture()
    response = engine.process(user_input)

    # 1. 验证 Router 输出
    print("\n[阶段 1: Router 输出 (意图拆解)]")
    if not captured_data["tool_calls"]:
        print(" ❌ 失败: Router 未触发任何工具调用")
    else:
        for i, tc in enumerate(captured_data["tool_calls"]):
            print(f"  {i+1}. 工具: {tc['name']} | 参数: {tc['args']}")

    # 2. 验证 API 输出
    print("\n[阶段 2: API 响应 (数据检索)]")
    if not captured_data["api_calls"]:
        print(" ❌ 失败: API 未被调用")
    else:
        for i, ac in enumerate(captured_data["api_calls"]):
            # 简化输出结果
            res_summary = str(ac['result'])[:100] + "..." if len(str(ac['result'])) > 100 else str(ac['result'])
            print(f"  {i+1}. {ac['method']}({ac['params']}) -> {res_summary}")

    # 3. 验证 Responder 输出
    print("\n[阶段 3: Responder 响应 (信息整合)]")
    print(f" - 最终类型: {response.type}")
    print(f" - 意图分类: {response.intentType}")
    
    # 检查 Responder 是否拿到了正确的数据上下文
    if captured_data["responder_context"] and "context_data" in captured_data["responder_context"]:
        print(" ✅ 验证: Responder Prompt 已注入上下文数据")
    
    print(f"\n--- 最终回复内容 ---\n{response.content}\n--------------------")

if __name__ == "__main__":
    test_cases = [
        ("简单复合意图", "帮我看看 UAV-001 的具体信息，然后统计一下本月任务的成功率"),
        ("多实体并发查询", "对比一下 UAV-001 和 UAV-002 的当前电量和状态"),
        ("统计+导出操作", "统计一下这周的飞行时长，并把详细记录导出为报表"),
        ("分析+查询", "为什么最近任务失败率升高了？列出最近 3 个失败的任务详情看看")
    ]

    for name, text in test_cases:
        run_test_case(name, text)
