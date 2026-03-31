import json
from src.engine import engine as officer
from src.engine import ChatHistory

def run_multi_turn_test():
    # 模拟一个典型的多轮对话序列
    conversation = [
        {
            "user": "今天有多少个巡检任务？",
            "expect_api": "/api/missions/stats"
        },
        {
            "user": "哪些设备在线？",
            "expect_api": "/api/devices/count"
        },
        {
            "user": "查询 UAV-SN-002 的实时高度。",
            "expect_api": "/api/devices/UAV-SN-002/telemetry"
        },
        {
            "user": "那它的俯仰角是多少？", # 考验指代消解
            "expect_api": "/api/devices/UAV-SN-002/telemetry"
        }
    ]

    history = []
    print("🧪 [多轮对话上下文测试启动]\n")
    print(f"{'轮次':<5} | {'用户输入':<25} | {'识别 API':<30} | {'指代消解'}")
    print("-" * 90)

    for i, turn in enumerate(conversation, 1):
        user_msg = turn['user']
        
        # 1. 调用 Router (传入 history 模拟真实 Context)
        # 这里我们直接调用 officer.process 来观察完整链路
        result = officer.process(user_msg, history=history)
        
        actual_api = result.dataSource[0].apiCalled
        actual_reply = result.chat_reply
        
        # 2. 验证 API 路由是否正确
        # 特别是最后一轮，API 应该包含 UAV-SN-002，尽管用户只说了“它”
        is_refer_ok = "UAV-SN-002" in actual_api if i == 4 else True
        symbol = "✅" if is_refer_ok else "❌"
        
        print(f"R{i:<4} | {user_msg:<25} | {actual_api:<30} | {symbol}")
        
        # 3. 更新历史记录 (模拟真实会话追加)
        history.append(ChatHistory(role="user", content=user_msg))
        history.append(ChatHistory(role="assistant", content=actual_reply))

    print("\n📊 测试完成。如果 R4 显示 ✅，说明 Router 已成功通过上下文识别出“它”指代的是 UAV-SN-002。")


if __name__ == "__main__":
    run_multi_turn_test()
