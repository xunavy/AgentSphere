"""持久化执行引擎 (Durable Task Engine)
负责驱动长程任务 (Long-Horizon Tasks) 的分步执行、断点续跑、异常重试与故障自愈。
"""

import logging
from typing import Callable, Dict, Any, Optional
from .state import DurableStateStore, TaskState, TaskStatus, Checkpoint

logger = logging.getLogger("agent_sphere.durable_engine")

class DurableExecutionEngine:
    """持久化执行引擎
    核心机制：
    1. 步骤幂等性保证：执行步骤前先持久化 Intent，执行成功后写入 Checkpoint；
    2. 断点恢复：引擎重启后直接加载最新有效 Checkpoint，无缝继续推进；
    3. 异步暂停与人工介入 (Human-in-the-loop)：任务可随时挂起，接收外部事件后恢复。
    """
    def __init__(self, store: DurableStateStore):
        self.store = store
        self._step_handlers: Dict[str, Callable[[TaskState], Any]] = {}

    def register_step_handler(self, step_type: str, handler: Callable[[TaskState], Any]):
        """注册步骤处理器"""
        self._step_handlers[step_type] = handler

    def init_task(self, task_id: str, name: str, initial_vars: Optional[Dict[str, Any]] = None) -> TaskState:
        """初始化一个全新的持久化任务"""
        state = TaskState(
            task_id=task_id,
            name=name,
            status=TaskStatus.PENDING,
            current_step=0,
            variables=initial_vars or {}
        )
        self.store.save_task(state)
        self.store.create_checkpoint(state, description="任务初始化创建")
        logger.info(f"Task {task_id} 初始化完成，已保存初始检查点。")
        return state

    def run_step(self, task_id: str, step_type: str, description: str = "") -> TaskState:
        """执行单步长程任务，并自动打桩 Checkpoint"""
        state = self.store.load_task(task_id)
        if not state:
            raise ValueError(f"未找到任务: {task_id}")

        if state.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
            logger.warning(f"任务 {task_id} 已经处于终态 {state.status.value}，忽略步进。")
            return state

        handler = self._step_handlers.get(step_type)
        if not handler:
            raise KeyError(f"未注册的步骤处理器类型: {step_type}")

        state.status = TaskStatus.RUNNING
        state.current_step += 1
        logger.info(f"Task {task_id} 开始执行步骤 {state.current_step}: [{step_type}] - {description}")

        try:
            # 执行业务步骤
            step_output = handler(state)
            if step_output and isinstance(step_output, dict):
                state.variables.update(step_output)
                if "final_output" in step_output:
                    state.final_output = step_output["final_output"]
                if "status" in step_output:
                    state.status = step_output["status"]
            
            # 步骤成功完成，持久化快照
            self.store.save_task(state)
            ckpt = self.store.create_checkpoint(state, description=f"步骤 {state.current_step} 完成: {step_type} - {description}")
            logger.info(f"Task {task_id} 步骤 {state.current_step} 成功，写入检查点: {ckpt.checkpoint_id}")
            return state
        except Exception as e:
            state.status = TaskStatus.FAILED
            self.store.save_task(state)
            self.store.create_checkpoint(state, description=f"步骤 {state.current_step} 异常失败: {str(e)}")
            logger.error(f"Task {task_id} 步骤 {state.current_step} 发生故障: {e}", exc_info=True)
            raise e

    def pause_task(self, task_id: str, reason: str = "") -> TaskState:
        """挂起/暂停任务（支持等待外部事件、人工审核或模拟进程中断）"""
        state = self.store.load_task(task_id)
        if not state:
            raise ValueError(f"未找到任务: {task_id}")
        state.status = TaskStatus.PAUSED
        self.store.save_task(state)
        self.store.create_checkpoint(state, description=f"任务已暂停: {reason}")
        logger.info(f"Task {task_id} 已挂起，原因: {reason}")
        return state

    def resume_task(self, task_id: str) -> TaskState:
        """从最新检查点无缝恢复任务执行"""
        state = self.store.load_task(task_id)
        if not state:
            raise ValueError(f"未找到任务: {task_id}")
        if state.status == TaskStatus.PAUSED:
            state.status = TaskStatus.RUNNING
            self.store.save_task(state)
            self.store.create_checkpoint(state, description="任务从暂停状态恢复执行")
            logger.info(f"Task {task_id} 已从最新检查点恢复执行。")
        return state

    def complete_task(self, task_id: str, final_output: str) -> TaskState:
        """标记任务圆满结束"""
        state = self.store.load_task(task_id)
        if not state:
            raise ValueError(f"未找到任务: {task_id}")
        state.status = TaskStatus.COMPLETED
        state.final_output = final_output
        self.store.save_task(state)
        self.store.create_checkpoint(state, description="任务圆满完成，产出最终交付物")
        logger.info(f"Task {task_id} 全部执行完毕。")
        return state
