import os
import sys
import json
import uuid

# 确保 PYTHONPATH 包含当前目录
sys.path.append(os.getcwd())

from src.engine import engine, ChatHistory, ChatResponse

def render_response(res: ChatResponse):
    """根据 v1.1 统一协议渲染响应"""
    # --- 1. 人性化渲染 (User View) ---
    print(f"\n[{res.intentType or 'SYSTEM'}]" if res.type != "error" else "\n[ERROR]")
    
    if res.type == "text":
        print(f"🤖 AI: {res.content}")
        if res.dataSource:
            sources = ", ".join([f"{s.module} ({s.api})" for s in res.dataSource])
            print(f"   💡 数据来源: {sources}")
        if res.relatedResources:
            btns = " | ".join([f"[{r.label}]" for r in res.relatedResources])
            print(f"   🔗 建议操作: {btns}")

    elif res.type == "action":
        act = res.action
        print(f"🎬 页面跳转: {res.content}")
        if act:
            print(f"   📍 目标路由: {act.pageRoute} ({act.menuName})")
            print(f"   📝 表单预填: {json.dumps(act.formData, ensure_ascii=False)}")
            print(f"   💬 确认语: {act.confirmMessage}")

    elif res.type == "error":
        err = res.error
        if err:
            print(f"❌ 发生异常: {err.code} | {err.message}")
        else:
            print(f"❌ 发生未知异常")

    # --- 2. 完整数据结构展示 (Debug View) ---
    print("\n" + "." * 15 + " [DEBUG RAW DATA] " + "." * 15)
    # 使用 Pydantic 的 .model_dump() 配合 json.dumps
    raw_json = json.dumps(res.model_dump(), indent=2, ensure_ascii=False)
    print(raw_json)
    print("." * 48)
    print("-" * 50)

def main():
    print("==================================================")
    print("🛸 无人机智能巡检系统 v1.1 - 交互式验证终端 (Debug Mode)")
    print("功能: 意图路由 | 业务查询 | 操作触发 | 原始数据回显")
    print("输入 'exit' 退出 | 'clear' 重置对话")
    print("==================================================\n")

    history = []

    while True:
        try:
            user_input = input("👤 用户: ").strip()
            
            if not user_input: continue
            if user_input.lower() in ['exit', 'quit']: break
            if user_input.lower() == 'clear':
                history = []
                print("🧹 对话历史已重置。\n")
                continue

            # 调用引擎处理
            result = engine.process(user_input, history=history)
            
            # 渲染回复与原始数据
            render_response(result)

            # 更新历史
            if result.type != "error":
                history.append(ChatHistory(role="user", content=user_input))
                history.append(ChatHistory(role="assistant", content=result.content or "已触发操作页面"))
            
            if len(history) > 10:
                history = history[-10:]

        except KeyboardInterrupt:
            print("\n\n👋 验证结束。")
            break
        except Exception as e:
            print(f"\n❌ 系统崩溃: {str(e)}")

if __name__ == "__main__":
    main()
