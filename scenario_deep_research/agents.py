"""深度研究多智能体集群构建 (Deep Research Agent Ensemble)
组装主控编排、专项检索、对比分析与反思核验四大智能体。
"""

import json
from typing import Dict, Any, List
from agent_sphere.model.base import MockLLM, BaseLLM
from agent_sphere.harness.sandbox import ToolSandbox
from agent_sphere.harness.loop import AgentHarness
from agent_sphere.orchestrator.bus import EventBus
from agent_sphere.orchestrator.subagent_manager import SubAgentManager, SubAgentSpec
from .tools import mock_deep_search, mock_benchmark_verify

def build_deep_research_cluster(llm: BaseLLM, event_bus: EventBus) -> SubAgentManager:
    """构建用于深度研究的 Sub-Agent 协同集群"""
    manager = SubAgentManager(event_bus=event_bus)

    # 1. 检索专项子智能体 (Search Sub-Agent)
    search_sandbox = ToolSandbox()
    search_sandbox.register_tool(
        name="deep_search",
        description="检索权威技术报告与学术文献",
        func=mock_deep_search
    )
    search_harness = AgentHarness(
        name="SearchAgent",
        role_desc="资深技术情报检索专家，擅长将宏观课题拆解为精准关键词并收集一手技术证据",
        llm=llm,
        sandbox=search_sandbox
    )
    manager.register_subagent(SubAgentSpec(
        name="SearchAgent",
        role_desc="技术情报检索与线索召回",
        harness=search_harness
    ))

    # 2. 分析与综合子智能体 (Analysis Sub-Agent)
    analysis_sandbox = ToolSandbox()
    analysis_harness = AgentHarness(
        name="AnalysisAgent",
        role_desc="系统架构对比分析专家，擅长梳理技术演进路径、架构分层与工程 Trade-offs",
        llm=llm,
        sandbox=analysis_sandbox
    )
    manager.register_subagent(SubAgentSpec(
        name="AnalysisAgent",
        role_desc="技术方案对比与工程决策权衡",
        harness=analysis_harness
    ))

    # 3. 反思与核查子智能体 (Verifier Sub-Agent)
    verifier_sandbox = ToolSandbox()
    verifier_sandbox.register_tool(
        name="benchmark_verify",
        description="验证论断与技术指标的事实准确性",
        func=mock_benchmark_verify
    )
    verifier_harness = AgentHarness(
        name="VerifierAgent",
        role_desc="架构质量与事实核查员，独立识别逻辑漏洞、幻觉虚构以及前后矛盾",
        llm=llm,
        sandbox=verifier_sandbox
    )
    manager.register_subagent(SubAgentSpec(
        name="VerifierAgent",
        role_desc="事实核验与质量自省",
        harness=verifier_harness
    ))

    return manager
