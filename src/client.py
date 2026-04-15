import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(dotenv_path="config/.env")

class LLMClient:
    def __init__(self):
        self.api_key = os.getenv("API_KEY")
        self.base_url = os.getenv("BASE_URL")
        self.model = os.getenv("MODEL", "qwen-turbo")
        self.client = OpenAI(
            api_key=self.api_key, 
            base_url=self.base_url
        )

    def call_llm(self, system: str, user: str, history: list = [], tools: list = None):
        messages = [{"role": "system", "content": system}]
        for h in history:
            messages.append({"role": h.role if hasattr(h, 'role') else h['role'], 
                             "content": h.content if hasattr(h, 'content') else h['content']})
        messages.append({"role": "user", "content": user})
        
        try:
            params = {
                "model": self.model,
                "messages": messages,
                "temperature": 0.1
            }
            if tools:
                params["tools"] = tools
                # 设置 tool_choice="auto" 让模型自主决定是否调工具
                params["tool_choice"] = "auto"

            res = self.client.chat.completions.create(**params)
            return res.choices[0].message
        except Exception as e:
            # 这里的 error 处理稍后在 engine 层统一适配
            raise e
