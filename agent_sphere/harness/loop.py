"""智能体线束与执行循环 (Agent Harness & Loop)
负责组织 Plan -> Act -> Reflect -> Verify 标准执行环，
将模型思考、工具调用与结果自省解耦装配。
"""

import json
import logging
from typing import Dict, Any, Optional
from ..model.base import BaseLLM, LLMResponse
from .context import ContextManager
from .sandbox import ToolSandbox

logger = logging.getLogger("agent_sphere.harness")

class AgentHarness:
    """智能体线束封装器 (Harness)
    核心职责：
    1. 组织 Agent Loop（思考 ➔ 工具动作 ➔ 自我反思 ➔ 结果校验）；
    2. 控制最大循环步数，防止死循环与 Token 无底线消耗；
    3. 规范化结构化输出。
    """
    def __init__(self, name: str, role_desc: str, llm: BaseLLM, sandbox: Optional[ToolSandbox] = None):
        self.name = name
        self.role_desc = role_desc
        self.llm = llm
        self.sandbox = sandbox or ToolSandbox()
        self.context = ContextManager()
        self.context.set_system_prompt(
            f"你是 [{name}]，职责定位：{role_desc}。\n"
            "请遵循结构化思考模式：\n"
            "1. Thought: 剖析当前问题与下一步规划；\n"
            "2. Action: 决定调用的工具或交付产物；\n"
            "3. Reflection: 对中间产物进行自我审查，确保符合客观事实。"
        )

    def execute_turn(self, user_instruction: str, max_steps: int = 5) -> Dict[str, Any]:
        """执行一个完整的指令轮次"""
        self.context.append_message("user", user_instruction)
        step_count = 0
        execution_trace = []

        while step_count < max_steps:
            step_count += 1
            messages = self.context.build_prompt_messages()
            tools_def = self.sandbox.get_tool_definitions()
            
            logger.info(f"[{self.name}] 开始第 {step_count} 步推理...")
            response: LLMResponse = self.llm.generate(messages=messages, tools=tools_def)
            self.context.append_message("assistant", response.content)

            trace_entry = {
                "step": step_count,
                "thought": response.content,
                "tool_executions": []
            }

            # 解析是否需要调用沙箱工具
            try:
                # 尝试解析模型输出中的结构化指令
                parsed = json.loads(response.content) if response.content.strip().startswith("{") else {}
                action = parsed.get("action")
                action_input = parsed.get("action_input", {})

                if action and action != "complete":
                    tool_res = self.sandbox.execute(action, action_input)
                    trace_entry["tool_executions"].append({
                        "tool": action,
                        "input": action_input,
                        "output": tool_res
                    })
                    # 将工具结果反馈至上下文
                    self.context.append_message("system", f"工具 [{action}] 返回结果: {json.dumps(tool_res, ensure_ascii=False)}")
                else:
                    # 任务视为完成
                    execution_trace.append(trace_entry)
                    return {
                        "agent": self.name,
                        "status": "completed",
                        "total_steps": step_count,
                        "trace": execution_trace,
                        "output": parsed.get("findings", response.content)
                    }
            except json.JSONDecodeError:
                # 非 JSON 格式直接作为最终输出
                execution_trace.append(trace_entry)
                return {
                    "agent": self.name,
                    "status": "completed",
                    "total_steps": step_count,
                    "trace": execution_trace,
                    "output": response.content
                }

            execution_trace.append(trace_entry)

        return {
            "agent": self.name,
            "status": "max_steps_reached",
            "total_steps": step_count,
            "trace": execution_trace,
            "output": "达到单步循环上限，自动返回当前已完成的部分成果。"
        }
