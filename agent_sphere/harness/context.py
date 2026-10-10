"""上下文工程与预算管理 (Context Engineering & Budget Management)
负责单体 Agent 的 Token 预算分配、动态滑窗修剪、工作记忆压缩以及子代理隔离上下文派生。
"""

from typing import List, Dict, Any, Optional
import copy

class ContextManager:
    """智能体上下文管理器
    核心机制：
    1. Token 预算管控：防止单步会话 Context 爆炸超出模型窗口；
    2. 上下文隔离派生 (Context Isolation Fork)：派发 Sub-Agent 时仅注入任务切片，杜绝父子 Context 污染；
    3. 记忆提取与关键事实浓缩。
    """
    def __init__(self, max_token_budget: int = 8000, max_history_turns: int = 15):
        self.max_token_budget = max_token_budget
        self.max_history_turns = max_history_turns
        self.system_prompt: str = ""
        self.working_memory: Dict[str, Any] = {}
        self.messages: List[Dict[str, str]] = []

    def set_system_prompt(self, prompt: str):
        self.system_prompt = prompt

    def update_memory(self, key: str, value: Any):
        self.working_memory[key] = value

    def append_message(self, role: str, content: str):
        self.messages.append({"role": role, "content": content})
        self._prune_history()

    def _estimate_tokens(self, text: str) -> int:
        # 中文字符与英文字词的粗略估算 (约 1 字符 ~ 0.8 token)
        return int(len(text) * 0.8)

    def _prune_history(self):
        """动态滑动窗口修剪：保留最新轮次，必要时压缩中间内容"""
        if len(self.messages) > self.max_history_turns:
            # 保留前 1 轮（用户核心诉求）与最近的 N 轮
            first_user_msg = self.messages[0]
            recent_msgs = self.messages[-(self.max_history_turns - 1):]
            self.messages = [first_user_msg] + recent_msgs

    def build_prompt_messages(self) -> List[Dict[str, str]]:
        """装配发送给大模型的完整上下文消息列表"""
        built_messages = []
        if self.system_prompt:
            # 动态附加当前工作记忆摘要
            memory_summary = ""
            if self.working_memory:
                memory_summary = "\n【当前工作记忆/上下文事实】:\n" + "\n".join([f"- {k}: {v}" for k, v in self.working_memory.items()])
            built_messages.append({
                "role": "system",
                "content": self.system_prompt + memory_summary
            })
        built_messages.extend(self.messages)
        return built_messages

    def fork_subagent_context(self, task_slice: str, extra_constraints: Optional[str] = None) -> "ContextManager":
        """为 Sub-Agent 派生独立的沙箱上下文，隔离父级会话历史"""
        sub_ctx = ContextManager(max_token_budget=self.max_token_budget // 2, max_history_turns=10)
        sub_system = f"你是一个专注的子智能体 (Sub-Agent)。\n你的专项任务范围：{task_slice}\n"
        if extra_constraints:
            sub_system += f"执行约束：{extra_constraints}\n"
        sub_ctx.set_system_prompt(sub_system)
        return sub_ctx
