import json
from src.engine import engine as officer

def run_responder_single_test():
    # 定义测试场景
    scenarios = [
        {
            "id": "MSG_001",
            "name": "标准任务查询 (验证加粗和列表)",
            "input": "今天有多少个巡检任务？"
        },
        {
            "id": "MSG_002",
            "name": "详细遥测数据 (验证高度/速度/俯仰角字段)",
            "input": "查询 UAV-SN-002 的实时遥测信息。"
        },
        {
            "id": "MSG_003",
            "name": "复杂分析意图 (验证分析逻辑)",
            "input": "分析一下最近 7 天的告警事件。"
        },
        {
            "id": "MSG_004",
            "name": "错误查询 (验证 404 容错)",
            "input": "查询无人机 UAV-9999-ERROR 的状态。"
        }
    ]

    print("🧪 [Responder 单轮专项测试启动] - 目标: 验证 Markdown 格式与数据准确性\n")
    print(f"{'ID':<10} | {'场景名称':<30} | {'意图':<10} | {'Markdown 检查'}")
    print("-" * 100)

    for case in scenarios:
        # 执行全流程
        result = officer.process(case['input'])
        reply = result.chat_reply
        intent = result.intentType
        
        # 检查是否包含 Markdown 加粗 (**) 
        has_bold = "**" in reply
        # 检查是否包含列表标志 (• 或 - 或 1.)
        has_list = any(sym in reply for sym in ["•", "-", "1.", "2."])
        
        status = "✅ 良好" if has_bold else "⚠️ 缺少加粗"
        
        print(f"{case['id']:<10} | {case['name']:<30} | {intent:<10} | {status}")
        print(f"   [用户输入]: {case['input']}")
        print(f"   [AI 回复]:\n{reply}\n")
        print("-" * 100)


if __name__ == "__main__":
    run_responder_single_test()
