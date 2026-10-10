"""子智能体生命周期与调度管理器 (Sub-Agent Lifecycle & Scheduling Manager)
负责任务解构 (Task Decomposition)、子智能体隔离派发、并发调度与成果合流。
"""

import logging
from typing import Dict, Any, List
from ..harness.loop import AgentHarness
from .bus import EventBus

logger = logging.getLogger("agent_sphere.subagent_manager")

class SubAgentSpec:
    """子智能体声明规范"""
    def __init__(self, name: str, role_desc: str, harness: AgentHarness):
        self.name = name
        self.role_desc = role_desc
        self.harness = harness

class SubAgentManager:
    """子智能体调度器
    核心机制：
    1. 声明式注册：按专职角色管理子智能体（如 Searcher, Synthesizer, Verifier）；
    2. 上下文隔离派发：将父级大任务切片为专职子任务，独立执行，防止 Context 膨胀；
    3. 结果汇聚与事件通知：通过 EventBus 实时同步任务进展。
    """
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self._registry: Dict[str, SubAgentSpec] = {}

    def register_subagent(self, spec: SubAgentSpec):
        self._registry[spec.name] = spec
        logger.info(f"SubAgent [{spec.name}] 已注册，角色：{spec.role_desc}")

    def dispatch(self, subagent_name: str, task_description: str, extra_vars: Dict[str, Any] = None) -> Dict[str, Any]:
        """向特定 Sub-Agent 派发隔离子任务"""
        spec = self._registry.get(subagent_name)
        if not spec:
            raise KeyError(f"未找到指定的子智能体: {subagent_name}")

        logger.info(f"调度 SubAgent [{subagent_name}] 执行子任务: {task_description[:60]}...")
        self.event_bus.publish(
            sender="MasterOrchestrator",
            recipient=subagent_name,
            topic="subtask.started",
            payload={"task": task_description, "extra": extra_vars or {}}
        )

        # 在隔离 Harness 中执行
        result = spec.harness.execute_turn(task_description)

        self.event_bus.publish(
            sender=subagent_name,
            recipient="MasterOrchestrator",
            topic="subtask.completed",
            payload={"output": result.get("output"), "status": result.get("status")}
        )
        return result

    def dispatch_batch(self, tasks: List[Dict[str, str]]) -> Dict[str, Any]:
        """批量调度多个子智能体执行并行/串行任务切片"""
        batch_results = {}
        for item in tasks:
            name = item["agent"]
            desc = item["task"]
            res = self.dispatch(name, desc)
            batch_results[name] = res
        return batch_results
