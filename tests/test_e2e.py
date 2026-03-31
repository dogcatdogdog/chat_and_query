import json
from src.engine import engine as officer
from src.engine import ChatHistory

def run_e2e_test():
    # 1. 单轮全链路测试用例
    single_cases = [
        {
            "id": "E2E_001",
            "name": "任务统计全链路",
            "input": "今天有多少个巡检任务？",
            "expect_keyword": "42"
        },
        {
            "id": "E2E_002",
            "name": "设备细节全链路",
            "input": "帮我看看 UAV-SN-001 的电量和高度。",
            "expect_keyword": "85%"
        },
        {
            "id": "E2E_003",
            "name": "事件分析全链路",
            "input": "分析一下最近 7 天的告警事件分布。",
            "expect_keyword": "156"
        },
        {
            "id": "E2E_004",
            "name": "异常查询全链路",
            "input": "查询 UAV-ERROR-999 的状态。",
            "expect_keyword": "404"
        }
    ]

    # 2. 多轮全链路测试用例
    multi_cases = [
        "哪些设备在线？",
        "查询 UAV-SN-002 的详细高度 and 电量。",
        "那它的俯仰角 and 速度现在是多少？"
    ]

    print("🚀 [全链路 E2E 联调测试启动] - 目标: 验证 Router -> Mock -> Responder 闭环\n")
    
    print("--- [Part 1: 单轮全链路验证] ---")
    for case in single_cases:
        result = officer.process(case['input'])
        reply = result.chat_reply
        api = result.dataSource[0].apiCalled
        
        status = "✅" if case['expect_keyword'] in reply or case['expect_keyword'] in str(result.dataSource[0].dataReturned) else "❌"
        print(f"[{case['id']}] 输入: {case['input']}")
        print(f"   -> 路由 API: {api}")
        print(f"   -> AI 回复: {reply[:100]}...")
        print(f"   -> 结果判定: {status}")
        print("-" * 60)

    print("\n--- [Part 2: 多轮全链路验证] ---")
    history = []
    for i, turn in enumerate(multi_cases, 1):
        result = officer.process(turn, history=history)
        reply = result.chat_reply
        api = result.dataSource[0].apiCalled
        
        print(f"R{i} 输入: {turn}")
        print(f"   -> 路由 API: {api}")
        print(f"   -> AI 回复: {reply}")
        
        history.append(ChatHistory(role="user", content=turn))
        history.append(ChatHistory(role="assistant", content=reply))
        print("-" * 60)

    print("\n📊 E2E 测试完成。")

if __name__ == "__main__":
    run_e2e_test()
