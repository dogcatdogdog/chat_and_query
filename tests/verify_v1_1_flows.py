import sys
import os
import json

# 添加当前目录到路径
sys.path.append(os.getcwd())

from src.engine import ExecutionEngine, ChatHistory

def test_v1_1_full_flow():
    engine = ExecutionEngine()
    history = []

    print("\n" + "="*50)
    print("无人机智能巡检系统 v1.1 综合流程验证")
    print("="*50)

    # --- 流程 1: 简单聊天 ---
    print("\n[流程 1] 测试意图: chat")
    q1 = "你好，你是谁？"
    print(f"用户: {q1}")
    res1 = engine.process(q1, history)
    print(f"AI: {res1.content}")
    print(f"意图: {res1.intentType}")
    
    # 更新历史
    history.append(ChatHistory(role="user", content=q1))
    history.append(ChatHistory(role="assistant", content=res1.content or ""))

    # --- 流程 2: 业务查询 (触发低电量预警) ---
    print("\n" + "-"*30)
    print("[流程 2] 测试意图: query (低电量预警验证)")
    # 注意: 数据池中 UAV-003 的电池为 15%
    q2 = "查询 UAV-003 的详细信息"
    print(f"用户: {q2}")
    res2 = engine.process(q2, history)
    print(f"AI:\n{res2.content}")
    print(f"意图: {res2.intentType}")
    if res2.dataSource:
        print(f"数据来源: {res2.dataSource[0].module} ({res2.dataSource[0].api})")
    
    history.append(ChatHistory(role="user", content=q2))
    history.append(ChatHistory(role="assistant", content=res2.content or ""))

    # --- 流程 3: 操作触发 (触发菜单跳转) ---
    print("\n" + "-"*30)
    print("[流程 3] 测试意图: action (操作触发验证)")
    q3 = "帮我为这台设备创建一个维修工单，标题是电池异常"
    print(f"用户: {q3}")
    res3 = engine.process(q3, history)
    print(f"AI 提示文字: {res3.content}")
    print(f"意图: {res3.intentType}")
    if res3.action:
        print(f"触发动作: {res3.action.menuName} (ID: {res3.action.pageRoute})")
        print(f"formData 捕获: {res3.action.formData}")

    print("\n" + "="*50)
    print("验证结束")

if __name__ == "__main__":
    test_v1_1_full_flow()
