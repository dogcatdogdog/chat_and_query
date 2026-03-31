import os
import json
import re
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from src.client import LLMClient
from src.processor import processor

class ChatHistory(BaseModel):
    role: str
    content: str

class DataSource(BaseModel):
    moduleName: str
    apiCalled: str
    dataReturned: Optional[Any] = None

class ChatRequest(BaseModel):
    conversationId: str
    message: str
    context: Optional[List[ChatHistory]] = []

class ChatResponse(BaseModel):
    chat_reply: str
    intentType: str # query/analysis/suggestion
    dataSource: List[DataSource]

class ExecutionEngine:
    def __init__(self):
        self.llm = LLMClient()
        self.router_prompt = self._load_prompt("prompts/router_prompt.md")
        self.responder_prompt = self._load_prompt("prompts/responder_prompt.md")

    def _load_prompt(self, path: str) -> str:
        if not os.path.exists(path):
            # Fallback if path is different relative to execution
            path = os.path.join(os.path.dirname(__file__), "..", path)
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    def _extract_json(self, text: str) -> str:
        pattern = r"\{.*\}"
        match = re.search(pattern, text, re.DOTALL)
        return match.group(0) if match else text

    def _map_path_to_module(self, path: str) -> str:
        if "mission" in path.lower(): return "任务管理"
        if "device" in path.lower(): return "设备管理"
        if "event" in path.lower(): return "事件管理"
        return "通用模块"

    def process(self, message: str, history: List[ChatHistory] = []) -> ChatResponse:
        # 1. Intent Recognition
        router_res = self.llm.call_llm(self.router_prompt, message, history)
        try:
            intent_data = json.loads(self._extract_json(router_res))
            intent_type = intent_data.get("intent", "query")
            api_path = intent_data.get("api", "GET /api/general")
            params = intent_data.get("params", {})
            
            if "{sn}" in api_path and params.get("sn"):
                api_path = api_path.replace("{sn}", params["sn"])
        except:
            intent_type, api_path, params = "query", "GET /api/general", {}

        # 2. Call Data Processor (Mock API)
        data_returned = processor.call_api(api_path, params)
        
        # 3. Response Generation
        responder_system = self.responder_prompt.replace("{context_data}", json.dumps(data_returned, ensure_ascii=False))
        final_reply = self.llm.call_llm(responder_system, message, history)

        return ChatResponse(
            chat_reply=final_reply,
            intentType=intent_type,
            dataSource=[DataSource(
                moduleName=self._map_path_to_module(api_path),
                apiCalled=api_path,
                dataReturned=data_returned
            )]
        )

engine = ExecutionEngine()
