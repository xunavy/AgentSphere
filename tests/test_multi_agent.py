"""单元测试：多智能体调度与工具沙箱 (Multi-Agent & Tool Sandbox)"""

import unittest
from agent_sphere.harness.sandbox import ToolSandbox
from agent_sphere.harness.loop import AgentHarness
from agent_sphere.model.base import MockLLM
from agent_sphere.orchestrator.bus import EventBus
from agent_sphere.orchestrator.subagent_manager import SubAgentManager, SubAgentSpec

class TestMultiAgent(unittest.TestCase):
    def test_sandbox_tool_registration_and_execution(self):
        sandbox = ToolSandbox()
        def add(a: int, b: int) -> int:
            return a + b
        
        sandbox.register_tool("add", "两数相加计算", add)
        schemas = sandbox.get_tool_definitions()
        self.assertEqual(len(schemas), 1)
        self.assertEqual(schemas[0]["function"]["name"], "add")

        res = sandbox.execute("add", {"a": 10, "b": 25})
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["result"], 35)

    def test_subagent_dispatch_and_event_bus(self):
        bus = EventBus()
        received_events = []
        bus.subscribe("subtask.completed", lambda msg: received_events.append(msg))

        mock_llm = MockLLM(responses={"子任务测试": '{"thought": "完成", "action": "complete", "findings": "测试成功"}'})
        harness = AgentHarness("TestWorker", "测试专用工人", mock_llm)
        
        manager = SubAgentManager(bus)
        manager.register_subagent(SubAgentSpec("TestWorker", "测试角色", harness))

        res = manager.dispatch("TestWorker", "子任务测试")
        self.assertEqual(res["status"], "completed")
        self.assertEqual(len(received_events), 1)
        self.assertEqual(received_events[0].sender, "TestWorker")

if __name__ == "__main__":
    unittest.main()
