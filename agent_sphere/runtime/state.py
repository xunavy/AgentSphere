"""任务状态机与持久化仓储 (Runtime State & Checkpoint Store)
负责支持从 Session-based 向 Task-based / Durable Agent 的演进，
提供事件溯源 (Event Sourcing) 与检查点 (Checkpoint) 快照管理。
"""

import sqlite3
import json
import time
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    PENDING = "PENDING"
    PLANNING = "PLANNING"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    WAITING_FOR_INPUT = "WAITING_FOR_INPUT"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class Checkpoint(BaseModel):
    """状态检查点快照"""
    checkpoint_id: str
    task_id: str
    step_id: int
    status: TaskStatus
    state_payload: Dict[str, Any]
    created_at: float = Field(default_factory=time.time)
    description: str = ""


class TaskState(BaseModel):
    """持久化任务全局状态模型"""
    task_id: str
    name: str
    status: TaskStatus = TaskStatus.PENDING
    current_step: int = 0
    plan: List[Any] = Field(default_factory=list)
    variables: Dict[str, Any] = Field(default_factory=dict)
    sub_task_results: Dict[str, Any] = Field(default_factory=dict)
    final_output: Optional[str] = None
    last_checkpoint_id: Optional[str] = None
    created_at: float = Field(default_factory=time.time)
    updated_at: float = Field(default_factory=time.time)


class DurableStateStore:
    """基于 SQLite 的持久化状态存储引擎，确保断电/重启后状态零丢失"""
    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # 任务主表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    task_id TEXT PRIMARY KEY,
                    name TEXT,
                    status TEXT,
                    current_step INTEGER,
                    state_json TEXT,
                    created_at REAL,
                    updated_at REAL
                )
            """)
            # 检查点快照表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS checkpoints (
                    checkpoint_id TEXT PRIMARY KEY,
                    task_id TEXT,
                    step_id INTEGER,
                    status TEXT,
                    state_payload TEXT,
                    created_at REAL,
                    description TEXT,
                    FOREIGN KEY(task_id) REFERENCES tasks(task_id)
                )
            """)
            conn.commit()

    def save_task(self, state: TaskState):
        """保存或更新任务整体状态"""
        state.updated_at = time.time()
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO tasks (task_id, name, status, current_step, state_json, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(task_id) DO UPDATE SET
                    name = excluded.name,
                    status = excluded.status,
                    current_step = excluded.current_step,
                    state_json = excluded.state_json,
                    updated_at = excluded.updated_at
            """, (
                state.task_id,
                state.name,
                state.status.value,
                state.current_step,
                state.model_dump_json(),
                state.created_at,
                state.updated_at
            ))
            conn.commit()

    def load_task(self, task_id: str) -> Optional[TaskState]:
        """读取任务最新状态"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT state_json FROM tasks WHERE task_id = ?", (task_id,))
            row = cursor.fetchone()
            if row:
                data = json.loads(row[0])
                return TaskState(**data)
            return None

    def create_checkpoint(self, state: TaskState, description: str = "") -> Checkpoint:
        """为当前任务生成并持久化不可变检查点快照"""
        checkpoint_id = f"ckpt_{state.task_id}_step{state.current_step}_{int(time.time()*1000)}"
        ckpt = Checkpoint(
            checkpoint_id=checkpoint_id,
            task_id=state.task_id,
            step_id=state.current_step,
            status=state.status,
            state_payload=state.model_dump(),
            description=description
        )
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO checkpoints (checkpoint_id, task_id, step_id, status, state_payload, created_at, description)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                ckpt.checkpoint_id,
                ckpt.task_id,
                ckpt.step_id,
                ckpt.status.value,
                json.dumps(ckpt.state_payload, ensure_ascii=False),
                ckpt.created_at,
                ckpt.description
            ))
            conn.commit()
        
        state.last_checkpoint_id = checkpoint_id
        self.save_task(state)
        return ckpt

    def list_checkpoints(self, task_id: str) -> List[Checkpoint]:
        """列出指定任务的所有历史检查点"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT checkpoint_id, task_id, step_id, status, state_payload, created_at, description
                FROM checkpoints WHERE task_id = ? ORDER BY step_id ASC, created_at ASC
            """, (task_id,))
            rows = cursor.fetchall()
            return [
                Checkpoint(
                    checkpoint_id=r[0],
                    task_id=r[1],
                    step_id=r[2],
                    status=TaskStatus(r[3]),
                    state_payload=json.loads(r[4]),
                    created_at=r[5],
                    description=r[6]
                ) for r in rows
            ]

    def rollback_to_checkpoint(self, checkpoint_id: str) -> Optional[TaskState]:
        """将任务状态回滚至指定的检查点快照"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT state_payload FROM checkpoints WHERE checkpoint_id = ?", (checkpoint_id,))
            row = cursor.fetchone()
            if row:
                payload = json.loads(row[0])
                state = TaskState(**payload)
                self.save_task(state)
                return state
            return None
