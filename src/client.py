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

    def call_llm(self, system: str, user: str, history: list = []) -> str:
        messages = [{"role": "system", "content": system}]
        for h in history:
            messages.append({"role": h.get('role') if isinstance(h, dict) else getattr(h, 'role'), 
                             "content": h.get('content') if isinstance(h, dict) else getattr(h, 'content')})
        messages.append({"role": "user", "content": user})
        
        try:
            res = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.1
            )
            return res.choices[0].message.content
        except Exception as e:
            return f"Error: {e}"
