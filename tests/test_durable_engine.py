"""单元测试：持久化执行引擎与检查点存储 (Durable Engine & State Store)"""

import unittest
import os
import tempfile
from agent_sphere.runtime.state import DurableStateStore, TaskState, TaskStatus
from agent_sphere.runtime.engine import DurableExecutionEngine

class TestDurableEngine(unittest.TestCase):
    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.temp_db.close()
        self.store = DurableStateStore(db_path=self.temp_db.name)
        self.engine = DurableExecutionEngine(store=self.store)

    def tearDown(self):
        if os.path.exists(self.temp_db.name):
            try:
                os.remove(self.temp_db.name)
            except OSError:
                pass

    def test_task_lifecycle_and_checkpoints(self):
        task_id = "TEST_TASK_001"
        self.engine.init_task(task_id, "测试任务", initial_vars={"counter": 0})
        
        # 验证初始状态
        state = self.store.load_task(task_id)
        self.assertEqual(state.status, TaskStatus.PENDING)
        self.assertEqual(state.current_step, 0)

        # 注册并执行第一步
        def step1(s):
            return {"counter": s.variables.get("counter", 0) + 1}
        self.engine.register_step_handler("STEP1", step1)
        self.engine.run_step(task_id, "STEP1", "递增计数器")

        # 验证步骤持久化
        state = self.store.load_task(task_id)
        self.assertEqual(state.status, TaskStatus.RUNNING)
        self.assertEqual(state.current_step, 1)
        self.assertEqual(state.variables["counter"], 1)

        # 验证挂起与恢复
        self.engine.pause_task(task_id, reason="测试挂起")
        state = self.store.load_task(task_id)
        self.assertEqual(state.status, TaskStatus.PAUSED)

        self.engine.resume_task(task_id)
        state = self.store.load_task(task_id)
        self.assertEqual(state.status, TaskStatus.RUNNING)

        # 验证历史检查点数量
        ckpts = self.store.list_checkpoints(task_id)
        self.assertGreaterEqual(len(ckpts), 4)

if __name__ == "__main__":
    unittest.main()
