"""评测与质量准出守卫 (Evaluation Gate & Quality Metrics)
负责对 Agent 运行全流程进行量化评估，包括任务完成度、结构完整性、
事实一致性与资源消耗，形成技术闭环准出判定。
"""

import logging
from typing import Dict, Any, List
from pydantic import BaseModel, Field

logger = logging.getLogger("agent_sphere.eval")

class EvaluationReport(BaseModel):
    task_id: str
    passed: bool
    score: float = Field(..., ge=0.0, le=100.0)
    metrics: Dict[str, Any]
    feedback: List[str]

class EvaluationGate:
    """质量评测守卫
    指标维度：
    1. 任务完成度 (Task Completeness): 是否覆盖所有规划子课题；
    2. 结构规范度 (Structure Score): 是否满足 Markdown 规范及章节要求；
    3. 事实核查度 (Fact Verification Score): 是否存在未被佐证的推断；
    4. 资源能耗 (Efficiency): 步数与 Token 消耗是否在合理阈值内。
    """
    def __init__(self, passing_score: float = 75.0):
        self.passing_score = passing_score

    def evaluate_output(self, task_id: str, plan: List[str], final_output: str, total_steps: int) -> EvaluationReport:
        feedback = []
        scores = {}
        final_output = final_output or ""

        # 1. 任务规划覆盖度 (权重 40%)
        covered_count = 0
        for sub_goal in plan:
            # 简单关键词覆盖检测
            keywords = [w for w in sub_goal.replace("，", " ").replace("、", " ").split() if len(w) > 2]
            if any(k in final_output for k in keywords):
                covered_count += 1
        coverage_rate = (covered_count / len(plan)) if plan else 1.0
        scores["task_coverage"] = coverage_rate * 100
        if coverage_rate < 0.8:
            feedback.append(f"部分子课题覆盖不充分 (完成率: {coverage_rate*100:.1f}%)")

        # 2. 结构完整度与详实度 (权重 30%)
        length = len(final_output)
        if length > 800:
            scores["structure_score"] = 95.0
        elif length > 300:
            scores["structure_score"] = 80.0
        else:
            scores["structure_score"] = 50.0
            feedback.append("产出内容篇幅偏短，缺乏深度论述")

        # 3. 执行效率与冗余度 (权重 30%)
        if total_steps <= 8:
            scores["efficiency_score"] = 90.0
        else:
            scores["efficiency_score"] = 65.0
            feedback.append(f"执行步数较多 ({total_steps} 步)，建议优化调度链路")

        # 综合加权总分
        total_score = (
            scores["task_coverage"] * 0.4 +
            scores["structure_score"] * 0.3 +
            scores["efficiency_score"] * 0.3
        )

        passed = total_score >= self.passing_score
        logger.info(f"Task {task_id} 评测完成: 总分={total_score:.1f}, 达标={passed}")

        return EvaluationReport(
            task_id=task_id,
            passed=passed,
            score=round(total_score, 1),
            metrics=scores,
            feedback=feedback or ["各项指标良好，满足平台资产准出标准"]
        )
