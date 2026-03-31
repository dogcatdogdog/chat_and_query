import json
import re
from src.engine import engine as officer

def run_exception_test():
    # 定义异常场景测试用例
    exception_cases = [
        {
            "id": "ERR_NON_EXISTENT_UAV",
            "name": "查询不存在的无人机",
            "input": "查询无人机 UAV-UNKNOWN-999 的高度和电量。",
            "expect_error": "Device Not Found: UAV-UNKNOWN-999"
        },
        {
            "id": "ERR_OUT_OF_SCOPE",
            "name": "业务范围外请求 (闲聊)",
            "input": "帮我查一下去上海的高铁票。",
            "expect_intent": "GENERAL_CHAT"
        }
    ]

    print("🧪 [异常处理测试启动]\n")
    print(f"{'ID':<20} | {'输入内容':<25} | {'响应结果'}")
    print("-" * 100)

    for case in exception_cases:
        # 调用全流程 (Router -> Mock -> Responder)
        result = officer.process(case['input'])
        
        reply = result.chat_reply
        intent = result.intentType
        data = result.dataSource[0].dataReturned
        
        status = "✅ 捕获异常" if ("抱歉" in reply or "未找到" in reply or "无法" in reply or intent == "GENERAL_CHAT") else "❌ 未妥善处理"
        
        print(f"{case['id']:<20} | {case['input']:<25} | {status}")
        print(f"   [AI 回复]: {reply}")
        print(f"   [意图类型]: {intent}")
        print(f"   [API 返回]: {data}")
        print("-" * 100)


if __name__ == "__main__":
    run_exception_test()
