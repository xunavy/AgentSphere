"""基础模型抽象与适配层 (Model Layer)
负责大模型调用的抽象隔离，解耦业务逻辑与具体模型提供商。
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import json

class LLMResponse:
    """统一模型响应结构体"""
    def __init__(self, content: str, tool_calls: Optional[List[Dict[str, Any]]] = None, usage: Optional[Dict[str, int]] = None):
        self.content = content
        self.tool_calls = tool_calls or []
        self.usage = usage or {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}

    def __repr__(self) -> str:
        return f"<LLMResponse content_len={len(self.content)} tool_calls={len(self.tool_calls)}>"


class BaseLLM(ABC):
    """大模型接口基类"""
    @abstractmethod
    def generate(self, messages: List[Dict[str, str]], tools: Optional[List[Dict[str, Any]]] = None, temperature: float = 0.2) -> LLMResponse:
        """执行大模型推理生成"""
        pass


class MockLLM(BaseLLM):
    """确定性仿真模型，用于测试、离线演示与架构闭环验证"""
    def __init__(self, responses: Optional[Dict[str, str]] = None):
        self.responses = responses or {}
        self.call_history: List[List[Dict[str, str]]] = []

    def register_response(self, keyword: str, response_content: str):
        self.responses[keyword] = response_content

    def generate(self, messages: List[Dict[str, str]], tools: Optional[List[Dict[str, Any]]] = None, temperature: float = 0.2) -> LLMResponse:
        self.call_history.append(messages)
        last_message = messages[-1]["content"] if messages else ""
        
        # 匹配预设的仿真响应
        for kw, resp in self.responses.items():
            if kw in last_message:
                return LLMResponse(content=resp, usage={"prompt_tokens": 120, "completion_tokens": 80, "total_tokens": 200})
        
        # 默认结构化兜底响应
        default_resp = json.dumps({
            "thought": "理解任务并执行分析，推进当前执行步骤。",
            "action": "complete",
            "findings": "根据当前输入完成逻辑归纳，确认无矛盾点。"
        }, ensure_ascii=False)
        return LLMResponse(content=default_resp, usage={"prompt_tokens": 100, "completion_tokens": 50, "total_tokens": 150})
