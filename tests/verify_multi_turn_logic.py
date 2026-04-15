import sys
import os
import json

# 添加当前目录到路径
sys.path.append(os.getcwd())

from src.engine import ExecutionEngine, ChatHistory

def run_multi_turn_test():
    engine = ExecutionEngine()
    history = []

    print("\n" + "="*60)
    print("🛸 多轮对话指代消解专项测试 (v1.1 Context Check)")
    print("="*60)

    # 第一轮: 建立明确对象
    q1 = "查询 UAV-001 的详细信息"
    print(f"\n[Turn 1] 用户: {q1}")
    res1 = engine.process(q1, history)
    print(f"🤖 AI: {res1.content}")
    history.append(ChatHistory(role="user", content=q1))
    history.append(ChatHistory(role="assistant", content=res1.content or ""))

    # 第二轮: 使用代词“它”
    q2 = "它现在的电量百分比是多少？"
    print(f"\n[Turn 2] 用户: {q2}")
    res2 = engine.process(q2, history)
    print(f"🤖 AI: {res2.content}")
    print(f"🔍 意图识别: {res2.intentType}")
    if res2.dataSource:
        print(f"📦 调用 API: {res2.dataSource[0].api}")
    
    history.append(ChatHistory(role="user", content=q2))
    history.append(ChatHistory(role="assistant", content=res2.content or ""))

    # 第三轮: 使用代词“这台设备”触发操作
    q3 = "帮我报修这台设备，标题是机翼磨损"
    print(f"\n[Turn 3] 用户: {q3}")
    res3 = engine.process(q3, history)
    if res3.type == "action":
        print(f"🎬 触发动作: {res3.action.menuName}")
        print(f"📝 捕获上下文 (rawContext): {res3.action.formData.get('rawContext')}")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    run_multi_turn_test()
