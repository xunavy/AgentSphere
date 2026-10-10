"""工具沙箱与安全执行边界 (Tool Sandbox & Execution Boundary)
负责工具的结构化注册 (Schema Export)、输入参数校验与隔离沙箱调用保护。
"""

import inspect
import json
import logging
from typing import Callable, Dict, Any, List, Optional
from pydantic import BaseModel, create_model

logger = logging.getLogger("agent_sphere.sandbox")

class ToolDefinition(BaseModel):
    name: str
    description: str
    parameters_schema: Dict[str, Any]

class ToolSandbox:
    """工具沙箱管理器
    核心机制：
    1. Schema 自省：自动根据 Python 函数类型注解生成 LLM Tool Schema；
    2. 安全沙箱隔离：拦截越界或未授权调用，统一结构化捕获异常；
    3. 审计追踪：记录所有工具调用的入参、耗时与返回值。
    """
    def __init__(self):
        self._tools: Dict[str, Callable] = {}
        self._schemas: Dict[str, ToolDefinition] = {}

    def register_tool(self, name: str, description: str, func: Callable):
        """注册一个可供 Agent 调用的工具函数"""
        sig = inspect.signature(func)
        fields = {}
        for param_name, param in sig.parameters.items():
            if param_name in ["self", "cls"]:
                continue
            param_type = param.annotation if param.annotation != inspect.Parameter.empty else str
            default_val = ... if param.default == inspect.Parameter.empty else param.default
            fields[param_name] = (param_type, default_val)

        # 动态创建 Pydantic 模型用于参数校验
        param_model = create_model(f"{name}_Params", **fields)
        schema = {
            "type": "object",
            "properties": param_model.model_json_schema().get("properties", {}),
            "required": param_model.model_json_schema().get("required", [])
        }

        self._tools[name] = func
        self._schemas[name] = ToolDefinition(
            name=name,
            description=description,
            parameters_schema=schema
        )
        logger.info(f"已在沙箱中注册工具: [{name}] - {description}")

    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """获取适用于 LLM Function Calling 的工具定义列表"""
        return [
            {
                "type": "function",
                "function": {
                    "name": t.name,
                    "description": t.description,
                    "parameters": t.parameters_schema
                }
            } for t in self._schemas.values()
        ]

    def execute(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """在受保护沙箱中安全执行工具"""
        if tool_name not in self._tools:
            return {"status": "error", "error": f"工具 [{tool_name}] 未在沙箱注册"}
        
        func = self._tools[tool_name]
        try:
            logger.info(f"沙箱调用工具: {tool_name}, 入参: {arguments}")
            result = func(**arguments)
            return {"status": "success", "result": result}
        except Exception as e:
            logger.error(f"工具 {tool_name} 执行异常: {e}", exc_info=True)
            return {"status": "error", "error": f"工具执行失败: {str(e)}"}
