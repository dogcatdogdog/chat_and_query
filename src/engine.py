import os
import json
import re
import uuid
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from src.client import LLMClient
from src.mock_api import mock_api

class ChatHistory(BaseModel):
    role: str
    content: str

# --- v1.1 统一响应结构子模型 ---

class DataSource(BaseModel):
    module: str           # 业务模块名（如：设备管理）
    api: str              # 调用的后端接口路径
    dataReturned: str     # 返回的数据摘要描述

class RelatedResource(BaseModel):
    type: str             # 操作类型：navigate (跳转) | create (创建)
    label: str            # 按钮显示的文字
    pageRoute: str        # 前端路由路径
    action: Optional[str] = None # 具体动作（如：create）

class ActionDetail(BaseModel):
    pageRoute: str        # 目标页面路由
    actionType: str       # 操作类型：create | edit | view | export
    menuName: str         # 菜单中文名称
    confirmRequired: bool # 是否需要二次确认
    formData: Dict[str, Any] = Field(default_factory=dict) # LLM 自动填充的表单数据
    emptyFields: List[str] = Field(default_factory=list)   # 未能自动填充的必填项列表
    confirmMessage: str      # 给用户的确认提示语

class ErrorInfo(BaseModel):
    code: str             # 错误码：TIMEOUT | PARTIAL_DATA | PERMISSION_DENIED | INTENT_UNKNOWN
    message: str          # 错误描述
    retryable: bool = True

class ChatResponse(BaseModel):
    conversationId: str = Field(default_factory=lambda: str(uuid.uuid4())) # 会话 ID
    messageId: str = Field(default_factory=lambda: str(uuid.uuid4()))      # 消息唯一 ID
    type: str             # 响应类型：text | action | error
    
    # 当 type = "text" 时使用
    content: Optional[str] = None        # Markdown 格式的回答正文
    intentType: Optional[str] = None     # 意图类型：query | statistics | analysis | suggestion | chat
    dataSource: Optional[List[DataSource]] = None
    relatedResources: Optional[List[RelatedResource]] = None
    
    # 当 type = "action" 时使用
    action: Optional[ActionDetail] = None
    
    # 当 type = "error" 时使用
    error: Optional[ErrorInfo] = None

class ExecutionEngine:
    def __init__(self):
        self.llm = LLMClient()
        self.router_prompt = self._load_prompt("prompts/router_prompt.md")
        self.responder_prompt = self._load_prompt("prompts/responder_prompt.md")
        self.menu_definitions = self._load_json("data/v1.1/menu_definitions.json")
        self.tools_registry = self._load_json("data/v1.1/tools_registry.json")

    def _load_prompt(self, path: str) -> str:
        if not os.path.exists(path):
            path = os.path.join(os.path.dirname(__file__), "..", path)
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    def _load_json(self, path: str) -> Any:
        if not os.path.exists(path):
            path = os.path.join(os.path.dirname(__file__), "..", path)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def process(self, message: str, history: List[ChatHistory] = []) -> ChatResponse:
        context_window = history[-10:] if len(history) > 10 else history
        
        try:
            # 1. 意图识别与工具分发 (Router using Function Calling ONLY)
            llm_msg = self.llm.call_llm(self.router_prompt, message, context_window, tools=self.tools_registry)
            
            # 核心约束：必须有 tool_calls
            if not llm_msg.tool_calls:
                return ChatResponse(
                    type="error",
                    error=ErrorInfo(code="PROTOCOL_ERROR", message="模型未能按协议触发工具调用")
                )

            tool_call = llm_msg.tool_calls[0]
            method = tool_call.function.name
            params = json.loads(tool_call.function.arguments)
            intent_type = params.get("intent", "query")

            # --- 流程 1: 直接回复工具 (direct_response) ---
            if method == "direct_response":
                reply_content = params.get("reply", "抱歉，我暂时无法回答。")
                return ChatResponse(
                    type="text" if intent_type == "chat" else "error",
                    content=reply_content if intent_type == "chat" else None,
                    intentType=intent_type,
                    error=ErrorInfo(code="INTENT_UNKNOWN", message=reply_content) if intent_type == "error" else None
                )

            # --- 流程 2: 操作触发工具 (trigger_menu) ---
            if intent_type == "action":
                menu_id = params.get("menuId")
                menu_config = self.menu_definitions.get(menu_id, {})
                return ChatResponse(
                    type="action",
                    content=f"已为您准备好「{menu_config.get('menuName', menu_id)}」页面。",
                    intentType="action",
                    action=ActionDetail(
                        pageRoute=menu_config.get("pageRoute", ""),
                        actionType=menu_config.get("action", "create"),
                        menuName=menu_config.get("menuName", ""),
                        confirmRequired=menu_config.get("confirmRequired", True),
                        formData=params,
                        confirmMessage=f"请确认是否执行{menu_config.get('menuName')}操作？"
                    )
                )

            # --- 流程 3: 业务处理工具 (Query/Stats/Analysis) ---
            api_data = mock_api.call(method, params)
            responder_system = self.responder_prompt.replace("{context_data}", json.dumps(api_data, ensure_ascii=False))
            
            # 信息加工 (Responder 调用，确保格式和预警)
            final_msg = self.llm.call_llm(responder_system, message, context_window)
            
            return ChatResponse(
                type="text",
                content=final_msg.content,
                intentType=intent_type,
                dataSource=[DataSource(
                    module=method, 
                    api=f"/{method}", 
                    dataReturned="已获取实时业务数据"
                )]
            )

        except Exception as e:
            return ChatResponse(
                type="error",
                error=ErrorInfo(code="RUNTIME_ERROR", message=str(e))
            )

        except Exception as e:
            return ChatResponse(
                type="error",
                error=ErrorInfo(code="RUNTIME_ERROR", message=str(e))
            )

engine = ExecutionEngine()
