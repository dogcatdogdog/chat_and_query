import json
from src.engine import engine as officer
from src.engine import ChatHistory

def run_responder_multi_test():
    # 定义测试场景
    # 模拟一个从整体查询到具体设备追问的链路
    conversation = [
        "今天有多少个巡检任务？",
        "哪些设备在线？",
        "查看 UAV-SN-002 的详细高度和电量。",
        "那它的俯仰角和速度现在是多少？" # 这个考验指代消解后 responder 对数据的解读
    ]

    history = []
    print("🧪 [Responder 多轮专项测试启动] - 目标: 验证上下文合成一致性\n")
    print(f"{'轮次':<5} | {'用户提问':<25} | {'状态'}")
    print("-" * 80)

    for i, turn in enumerate(conversation, 1):
        # 执行全流程
        result = officer.process(turn, history=history)
        reply = result.chat_reply
        
        # 检查是否包含上一轮设备 SN 或 关键数值
        is_consistent = "UAV-SN-002" in reply if i >= 3 else True
        status = "✅ 逻辑一致" if is_consistent else "⚠️ 丢失实体"
        
        print(f"R{i:<4} | {turn:<25} | {status}")
        print(f"   [AI 回复]: {reply}\n")
        
        # 更新历史
        history.append(ChatHistory(role="user", content=turn))
        history.append(ChatHistory(role="assistant", content=reply))

    print("\n📊 测试完成。")


if __name__ == "__main__":
    run_responder_multi_test()
