from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Callable

@dataclass
class Tool:
    name: str
    description: str
    schema: dict[str, Any]
    handler: Callable[..., Any]
    dangerous: bool = False

class ToolRegistry:
    def __init__(self): self._tools: dict[str, Tool] = {}
    def register(self, tool: Tool): self._tools[tool.name] = tool
    def get(self, name): return self._tools.get(name)
    def definitions(self):
        return [{"type":"function", "function":{"name":t.name,"description":t.description,"parameters":t.schema}} for t in self._tools.values()]
    def execute(self, name, args, confirmed=False):
        tool = self.get(name)
        if not tool: raise ValueError(f"Tool не зарегистрирован: {name}")
        if tool.dangerous and not confirmed:
            raise PermissionError(f"Tool требует подтверждения: {name}")
        return tool.handler(**args)
