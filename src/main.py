import os
import sys
from src.engine import engine, ChatHistory

def main():
    print("========================================")
    print("🚀 General LLM Verification Framework")
    print("模式: 交互式 CLI 问答 Demo (多轮对话)")
    print("输入 'exit' 或 'quit' 退出，输入 'clear' 清空历史")
    print("========================================\n")

    history = []

    while True:
        try:
            # 获取用户输入
            user_input = input("👤 用户: ").strip()
            
            if not user_input:
                continue
                
            if user_input.lower() in ['exit', 'quit']:
                print("\n👋 再见！")
                break
                
            if user_input.lower() == 'clear':
                history = []
                print("🧹 对话历史已清空。\n")
                continue

            # 调用引擎处理
            # 注意: engine.process 接收 history 列表并返回 ChatResponse 对象
            result = engine.process(user_input, history=history)
            
            # 打印 AI 回复
            print(f"\n🤖 AI: {result.chat_reply}")
            
            # 打印调试信息（可选，展示意图识别和 API 调用）
            api_called = result.dataSource[0].apiCalled if result.dataSource else "None"
            print(f"   [意图: {result.intentType} | API: {api_called}]\n")
            print("-" * 40)

            # 更新历史记录 (保持多轮对话能力)
            history.append(ChatHistory(role="user", content=user_input))
            history.append(ChatHistory(role="assistant", content=result.chat_reply))
            
            # 限制历史长度，避免 Token 溢出 (可选，如只保留最近 10 轮)
            if len(history) > 20:
                history = history[-20:]

        except KeyboardInterrupt:
            print("\n\n👋 程序已终止。")
            break
        except Exception as e:
            print(f"\n❌ 发生错误: {e}")

if __name__ == "__main__":
    # 确保 PYTHONPATH 包含当前目录
    sys.path.append(os.getcwd())
    main()
