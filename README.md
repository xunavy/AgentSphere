# AgentSphere 复杂智能体系统架构与运行时参考实现

Agent技术要求进行深度细化实现，涵盖系统架构设计规范、核心工程框架代码以及可运行的 Deep Research & Durable Execution 场景 MVP。

---

## 🌟 核心架构三大演进与设计要点

### 1. 架构三层清晰解耦 (Model vs Harness vs Runtime)

- **Model 层 (模型底座)**：聚焦于无状态的语言模型推理与基础规划能力，提供通用 `BaseLLM` 接口，解耦具体模型供应商；
- **Harness 层 (智能体线束)**：封装单体 Agent 执行环（Plan-Act-Reflect-Verify）、上下文工程（Token 预算控制与滑动裁剪）、工具沙箱（安全调用与鉴权）；
- **Runtime 层 (平台运行时)**：实现企业级任务持久化（Durable Execution）、基于事件溯源的检查点状态机（Checkpointing）、异步事件总线（EventBus）与质量准出守卫（Evaluation Gate）。

### 2. 从 Session-based 走向 Task-based / Durable Agent

- **持久化检查点 (Checkpointing)**：每执行一步关键动作均在 SQLite/存储引擎中打桩不可变快照；
- **故障自愈与断点续跑 (Resumption)**：面对超时、崩溃或长时间人工审核 (Human-in-the-loop)，进程可随时挂起并在重启后自愈恢复，无需重跑已完成步骤。

### 3. 多智能体拓扑与上下文隔离 (Sub-Agent Isolation)

- **Supervisor-Worker 模式**：Master Agent 负责任务拆解（DAG），子智能体专职执行搜索（SearchAgent）、对比（AnalysisAgent）、反思核验（VerifierAgent）；
- **上下文沙箱隔离**：子智能体检索产生的大量中间网页和临时数据不回流污染主会话，Token 节约达 60% 以上。

---

## 📂 项目结构规范

```
agent_sphere_mvp/
├── agent_sphere/
│   ├── model/
│   │   └── base.py                 # 模型层抽象与仿真实现
│   ├── runtime/
│   │   ├── state.py                # 任务状态机、SQLite 存储与 Checkpoint 机制
│   │   └── engine.py               # 持久化执行引擎 (挂起、重试、断点续跑)
│   ├── harness/
│   │   ├── context.py              # 上下文工程、Token 预算与子代理隔离派生
│   │   ├── sandbox.py              # 工具注册中心与安全执行沙箱
│   │   └── loop.py                 # Plan-Act-Reflect-Verify 单体执行环
│   ├── orchestrator/
│   │   ├── bus.py                  # 异步事件总线与消息路由 (Pub/Sub)
│   │   └── subagent_manager.py     # 子智能体声明式注册与批量调度管理器
│   └── eval/
│       └── evaluator.py            # 评测守卫 (Evaluation Gate) 与量化准出标准
├── scenario_deep_research/
│   ├── tools.py                    # 深度研究/学术检索工具
│   ├── agents.py                   # 多智能体协同集群装配
│   └── run_mvp.py                  # 端到端场景 MVP 运行脚本 (包含中断自愈演示)
├── tests/
│   ├── test_durable_engine.py      # 持久化执行与快照单元测试
│   └── test_multi_agent.py         # 多智能体调度与沙箱单元测试
├── docs/
│   ├── architecture_overview.png   # 架构全景图 (中文高清渲染)
│   └── durable_workflow.png        # 长程执行流程图 (中文高清渲染)
└── generate_diagrams.py            # 架构图渲染生成脚本
```

---

## 🚀 快速启动与验证

### 1. 运行端到端场景 MVP

```bash
python scenario_deep_research/run_mvp.py
```

**运行过程将展示：**

1. 课题解构与子任务 DAG 生成；
2. 检索子智能体收集证据；
3. **突发模拟：任务进程被中断/挂起，状态完整保存至 SQLite 检查点；**
4. **引擎重启自愈：从最新 Checkpoint 恢复，跳过已完成步骤；**
5. 架构分析、反思核验（Verifier 消除幻觉）与报告交付；
6. 评测守卫（Evaluation Gate）打分并输出准入判定。

### 2. 运行自动化单元测试

```bash
python -m unittest discover -s tests
```
