import json
import re
from src.engine import engine as officer

def run_router_test():
    # 1. 定义基于 router_prompt.md 的基准测试用例
    test_cases = [
        {
            "id": "FLOW_1_2",
            "name": "基础任务查询",
            "input": "今天有多少个巡检任务？",
            "expect": {"intent": "query", "module": "任务管理", "api": "/api/missions/stats"}
        },
        {
            "id": "FLOW_3",
            "name": "设备状态查询",
            "input": "哪些设备在线？",
            "expect": {"intent": "query", "module": "设备管理", "api": "/api/devices/count"}
        },
        {
            "id": "FLOW_4",
            "name": "复杂数据分析",
            "input": "分析一下最近的AI告警事件",
            "expect": {"intent": "analysis", "module": "事件管理", "api": "/api/events/analysis"}
        },
        {
            "id": "FLOW_5",
            "name": "处置建议",
            "input": "设备 DJI-003 已离线超过 2 小时，建议怎么处理？",
            "expect": {"intent": "suggestion", "module": "事件管理", "api": "/api/events/analysis"}
        }
    ]

    print("🧪 [Router 专项测试启动] - 目标: 验证意图识别与 API 路由\n")
    print(f"{'ID':<10} | {'输入内容':<25} | {'结果':<10} | {'详情'}")
    print("-" * 80)

    for case in test_cases:
        # 仅执行意图识别逻辑
        raw_res = officer.llm.call_llm(officer.router_prompt, case['input'])
        try:
            actual = json.loads(officer._extract_json(raw_res))
            api_path = actual.get("api", "")
            mapped_module = officer._map_path_to_module(api_path)
            
            # 验证核心字段是否匹配
            intent_ok = actual.get("intent") == case['expect']['intent']
            module_ok = case['expect']['module'] in mapped_module
            api_ok = case['expect']['api'] in api_path
            
            is_pass = intent_ok and module_ok and api_ok
            status = "✅ PASS" if is_pass else "❌ FAIL"
            
            print(f"{case['id']:<10} | {case['input']:<25} | {status:<10} | 识别为: {actual.get('intent')}/{mapped_module}")
            
            if not is_pass:
                print(f"   [预期]: {case['expect']}")
                print(f"   [实际 JSON]: {actual}")
                print(f"   [映射模块]: {mapped_module}")
        except Exception as e:
            print(f"{case['id']:<10} | {case['input']:<25} | ❌ ERROR    | 解析失败: {e}")

if __name__ == "__main__":
    run_router_test()
