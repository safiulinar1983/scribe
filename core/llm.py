from __future__ import annotations
import requests
from dataclasses import dataclass
from typing import Any

@dataclass
class LLMResponse:
    content: str
    tool_calls: list[dict[str, Any]]
    raw: dict[str, Any]

class LLMProvider:
    def chat(self, messages: list[dict[str, Any]], tools: list[dict[str, Any]] | None = None) -> LLMResponse:
        raise NotImplementedError

class OllamaProvider(LLMProvider):
    def __init__(self, base_url: str, model: str, temperature: float = 0.2, timeout: int = 180):
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.temperature = temperature
        self.timeout = timeout

    def chat(self, messages, tools=None):
        payload = {"model": self.model, "messages": messages, "stream": False,
           "think": False,
           "options": {"temperature": self.temperature}}
        if tools:
            payload["tools"] = tools
        r = requests.post(self.base_url + "/api/chat", json=payload, timeout=self.timeout)
        r.raise_for_status()
        data = r.json()
        msg = data.get("message", {})
        calls = msg.get("tool_calls") or []
        return LLMResponse(msg.get("content", ""), calls, data)
