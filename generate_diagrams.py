import os
from playwright.sync_api import sync_playwright

output_dir_docs = r"D:\AI-github\agent_sphere_mvp\docs"
output_dir_brain = r"C:\Users\navy\.gemini\antigravity-cli\brain\f56321f8-a1f6-4694-8384-6cbc7d670213\images"

html_content_arch = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: "Microsoft YaHei", "PingFang SC", "Segoe UI", sans-serif;
    background: #0d1117;
    color: #e6edf3;
    padding: 30px;
    width: 1200px;
    margin: 0 auto;
  }
  .header {
    text-align: center;
    margin-bottom: 25px;
  }
  .header h1 {
    font-size: 28px;
    font-weight: 700;
    color: #58a6ff;
    letter-spacing: 1px;
    margin-bottom: 8px;
  }
  .header p {
    font-size: 14px;
    color: #8b949e;
  }
  .layer {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 12px;
    padding: 18px 20px;
    margin-bottom: 18px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
  }
  .layer-title {
    font-size: 16px;
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 14px;
    padding-bottom: 8px;
    border-bottom: 1px solid #21262d;
  }
  .badge {
    font-size: 11px;
    padding: 2px 8px;
    border-radius: 20px;
    font-weight: 500;
    text-transform: uppercase;
  }
  .badge-blue { background: #1f6feb33; color: #58a6ff; border: 1px solid #1f6feb; }
  .badge-purple { background: #8957e533; color: #bc8cff; border: 1px solid #8957e5; }
  .badge-green { background: #23863633; color: #3fb950; border: 1px solid #238636; }
  .badge-orange { background: #d2992233; color: #d29922; border: 1px solid #bb8009; }
  .badge-red { background: #da363333; color: #f85149; border: 1px solid #da3633; }

  .grid {
    display: grid;
    gap: 14px;
  }
  .grid-4 { grid-template-columns: repeat(4, 1fr); }
  .grid-3 { grid-template-columns: repeat(3, 1fr); }
  .grid-2 { grid-template-columns: repeat(2, 1fr); }

  .card {
    background: #21262d;
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 12px 14px;
    transition: all 0.2s;
  }
  .card-title {
    font-size: 14px;
    font-weight: 600;
    color: #f0f6fc;
    margin-bottom: 6px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  .card-desc {
    font-size: 12px;
    color: #8b949e;
    line-height: 1.5;
  }
  .card-tags {
    margin-top: 8px;
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
  }
  .tag {
    font-size: 10px;
    background: #30363d;
    color: #c9d1d9;
    padding: 1px 6px;
    border-radius: 4px;
  }
  .connector {
    text-align: center;
    color: #58a6ff;
    font-size: 18px;
    margin: -10px 0 8px 0;
  }
</style>
</head>
<body>
  <div class="header">
    <h1>AgentSphere 复杂智能体系统参考架构 (Reference Architecture)</h1>
    <p>面向长程复杂任务 (Long-Horizon Tasks) · 持久化执行 (Durable Execution) · 多智能体协同 (Multi-Agent)</p>
  </div>

  <!-- 场景业务层 -->
  <div class="layer">
    <div class="layer-title" style="color: #bc8cff;">
      <span>业务场景与应用层 (Business Scenarios Layer)</span>
      <span class="badge badge-purple">业务输入端</span>
    </div>
    <div class="grid grid-3">
      <div class="card">
        <div class="card-title">深度检索与研究 (Deep Research)</div>
        <div class="card-desc">多信源检索、信息交叉比对、长文报告合成与事实溯源。</div>
        <div class="card-tags"><span class="tag">搜索召回</span><span class="tag">信息聚类</span><span class="tag">深度综合</span></div>
      </div>
      <div class="card">
        <div class="card-title">长周期任务 (Long-Horizon Tasks)</div>
        <div class="card-desc">跨分钟至小时级连续执行、中途人工审批、断点续传与自愈。</div>
        <div class="card-tags"><span class="tag">异步轮询</span><span class="tag">状态持久化</span><span class="tag">人工介入</span></div>
      </div>
      <div class="card">
        <div class="card-title">自主工程智能体 (Coding / Workflows)</div>
        <div class="card-desc">代码生成、环境沙箱验证、自动化测试、循环重试与自我修复。</div>
        <div class="card-tags"><span class="tag">代码沙箱</span><span class="tag">测试驱动</span><span class="tag">反思修复</span></div>
      </div>
    </div>
  </div>

  <div class="connector">▼ 任务协议解构与委派</div>

  <!-- 多智能体协同编排层 -->
  <div class="layer">
    <div class="layer-title" style="color: #58a6ff;">
      <span>多智能体协作与编排层 (Multi-Agent Orchestrator)</span>
      <span class="badge badge-blue">主控调度</span>
    </div>
    <div class="grid grid-4">
      <div class="card">
        <div class="card-title">目标拆解器 (Task Planner)</div>
        <div class="card-desc">宏观目标分解为可独立执行的子任务树 (DAG) 并维护依赖拓扑。</div>
        <div class="card-tags"><span class="tag">任务DAG</span><span class="tag">动态重规划</span></div>
      </div>
      <div class="card">
        <div class="card-title">子智能体调度器 (Dispatcher)</div>
        <div class="card-desc">按能力路由派发 Sub-Agent，控制并发度、生命周期与上下文隔离。</div>
        <div class="card-tags"><span class="tag">并发池化</span><span class="tag">隔离运行</span></div>
      </div>
      <div class="card">
        <div class="card-title">事件消息总线 (Event Bus)</div>
        <div class="card-desc">父子 Agent 结构化消息通信、异步事件流、心跳监听与广播。</div>
        <div class="card-tags"><span class="tag">事件驱动</span><span class="tag">消息分发</span></div>
      </div>
      <div class="card">
        <div class="card-title">成果合流与仲裁 (Arbitrator)</div>
        <div class="card-desc">收集子智能体交付物，仲裁冲突信息，组装结构化总产出。</div>
        <div class="card-tags"><span class="tag">结果汇聚</span><span class="tag">冲突消解</span></div>
      </div>
    </div>
  </div>

  <div class="connector">▼ 单体实例化与线束封装</div>

  <!-- Agent Harness 单体线束层 -->
  <div class="layer">
    <div class="layer-title" style="color: #3fb950;">
      <span>智能体线束与执行层 (Agent Harness & Loop)</span>
      <span class="badge badge-green">执行核心</span>
    </div>
    <div class="grid grid-4">
      <div class="card">
        <div class="card-title">核心循环 (Agent Loop)</div>
        <div class="card-desc">Plan-Act-Reflect-Verify 标准执行环，状态步进与中止条件判定。</div>
        <div class="card-tags"><span class="tag">ReAct++</span><span class="tag">状态机步进</span></div>
      </div>
      <div class="card">
        <div class="card-title">上下文工程 (Context Engine)</div>
        <div class="card-desc">Token 预算分配、动态记忆压缩、上下文滑窗裁剪与相关性检索。</div>
        <div class="card-tags"><span class="tag">Token预算</span><span class="tag">记忆萃取</span></div>
      </div>
      <div class="card">
        <div class="card-title">工具沙箱 (Tool Sandbox)</div>
        <div class="card-desc">权限鉴权、Schema 校验、网络/文件沙箱隔离与调用安全防护。</div>
        <div class="card-tags"><span class="tag">最小权限</span><span class="tag">安全调用</span></div>
      </div>
      <div class="card">
        <div class="card-title">反思与核验 (Reflection Gate)</div>
        <div class="card-desc">执行结果质量自查、幻觉过滤、格式结构化校验与容错重试。</div>
        <div class="card-tags"><span class="tag">自我核查</span><span class="tag">契约验证</span></div>
      </div>
    </div>
  </div>

  <div class="connector">▼ 基础设施与持久化支撑</div>

  <!-- 持久化运行时与平台层 -->
  <div class="layer">
    <div class="layer-title" style="color: #d29922;">
      <span>持久化运行时与平台底座 (Durable Runtime & Platform)</span>
      <span class="badge badge-orange">平台底座</span>
    </div>
    <div class="grid grid-4">
      <div class="card">
        <div class="card-title">持久化引擎 (Durable Engine)</div>
        <div class="card-desc">基于事件溯源 (Event Sourcing) 的 Checkpoint 机制，支持中断、重放与状态恢复。</div>
        <div class="card-tags"><span class="tag">检查点快照</span><span class="tag">断点续跑</span></div>
      </div>
      <div class="card">
        <div class="card-title">状态与任务仓储 (State Store)</div>
        <div class="card-desc">任务元数据、执行历史、中间产物强一致性持久化，全生命周期可溯源。</div>
        <div class="card-tags"><span class="tag">事务持久化</span><span class="tag">版本控制</span></div>
      </div>
      <div class="card">
        <div class="card-title">评测与守卫 (Evaluation Gate)</div>
        <div class="card-desc">离线 Benchmark、在线链路评测、完成率/成本/耗时量化监控与质量红线。</div>
        <div class="card-tags"><span class="tag">量化评测</span><span class="tag">质量准出</span></div>
      </div>
      <div class="card">
        <div class="card-title">可观测性 (Observability)</div>
        <div class="card-desc">全链路分布式 Tracing、Token 消耗统计、错误告警与实时可视化回放。</div>
        <div class="card-tags"><span class="tag">OpenTelemetry</span><span class="tag">轨迹回放</span></div>
      </div>
    </div>
  </div>

  <!-- 底层模型层 -->
  <div class="layer" style="margin-bottom: 0;">
    <div class="layer-title" style="color: #f85149;">
      <span>模型底座能力层 (Foundation Model Layer)</span>
      <span class="badge badge-red">智能驱动</span>
    </div>
    <div class="grid grid-3">
      <div class="card">
        <div class="card-title">基础推理模型 (Reasoning LLM)</div>
        <div class="card-desc">负责单步深思考、逻辑推理、意图理解与自然语言生成。</div>
      </div>
      <div class="card">
        <div class="card-title">结构化与工具调用 (Structured & Tool Use)</div>
        <div class="card-desc">严格 JSON Schema 输出、原生 Function Calling、长上下文窗口支持。</div>
      </div>
      <div class="card">
        <div class="card-title">多模态与外部适配 (Multimodal & APIs)</div>
        <div class="card-desc">图像/文档解析、Embedding 向量表征、异构模型路由与降级容灾。</div>
      </div>
    </div>
  </div>
</body>
</html>
"""

html_content_flow = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: "Microsoft YaHei", "PingFang SC", "Segoe UI", sans-serif;
    background: #0d1117;
    color: #e6edf3;
    padding: 30px;
    width: 1200px;
    margin: 0 auto;
  }
  .header {
    text-align: center;
    margin-bottom: 25px;
  }
  .header h1 {
    font-size: 26px;
    font-weight: 700;
    color: #3fb950;
    margin-bottom: 6px;
  }
  .header p {
    font-size: 13px;
    color: #8b949e;
  }
  .timeline {
    display: flex;
    flex-direction: column;
    gap: 16px;
    position: relative;
  }
  .stage {
    display: flex;
    align-items: stretch;
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 10px;
    overflow: hidden;
  }
  .stage-sidebar {
    width: 160px;
    background: #21262d;
    border-right: 1px solid #30363d;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    padding: 15px;
    text-align: center;
  }
  .stage-num {
    font-size: 20px;
    font-weight: bold;
    color: #58a6ff;
    margin-bottom: 4px;
  }
  .stage-name {
    font-size: 14px;
    font-weight: 600;
    color: #f0f6fc;
  }
  .stage-content {
    flex: 1;
    padding: 16px 20px;
    display: flex;
    gap: 14px;
  }
  .step-box {
    flex: 1;
    background: #0d1117;
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 12px 14px;
  }
  .step-title {
    font-size: 13px;
    font-weight: 600;
    color: #79c0ff;
    margin-bottom: 5px;
  }
  .step-desc {
    font-size: 12px;
    color: #8b949e;
    line-height: 1.5;
  }
  .highlight-box {
    border-color: #d29922;
    background: #272115;
  }
  .highlight-title {
    color: #e3b341;
  }
  .arrow-down {
    text-align: center;
    color: #3fb950;
    font-size: 16px;
    font-weight: bold;
    margin: -8px 0;
  }
</style>
</head>
<body>
  <div class="header">
    <h1>长程任务持久化执行与多智能体协同流水线 (Durable Pipeline)</h1>
    <p>任务接单 ➔ 拓扑规划 ➔ 子智能体隔离派发 ➔ 检查点断点续跑 ➔ 验证守卫 ➔ 成果交付</p>
  </div>

  <div class="timeline">
    <!-- 阶段 1 -->
    <div class="stage">
      <div class="stage-sidebar">
        <div class="stage-num">阶段 01</div>
        <div class="stage-name">任务初始化与意图理解</div>
      </div>
      <div class="stage-content">
        <div class="step-box">
          <div class="step-title">① 创建持久化任务实例</div>
          <div class="step-desc">分配全局唯一 TaskID，初始化状态机（PENDING），持久化初始输入至任务仓储。</div>
        </div>
        <div class="step-box">
          <div class="step-title">② 上下文预算分配</div>
          <div class="step-desc">评估任务规模，划分主 Agent 与 Sub-Agent 的 Token 上限及沙箱权限。</div>
        </div>
        <div class="step-box">
          <div class="step-title">③ 写入初始检查点 (Checkpoint)</div>
          <div class="step-desc">记录 Step 0 初始快照，确保整个执行生命周期随时具备故障回滚点。</div>
        </div>
      </div>
    </div>

    <div class="arrow-down">▼ 状态机流转: PENDING ➔ PLANNING</div>

    <!-- 阶段 2 -->
    <div class="stage">
      <div class="stage-sidebar">
        <div class="stage-num">阶段 02</div>
        <div class="stage-name">规划与任务拓扑解构</div>
      </div>
      <div class="stage-content">
        <div class="step-box">
          <div class="step-title">① Master Agent 宏观规划</div>
          <div class="step-desc">主控智能体分析复杂课题（如 Deep Research），分解为独立并行的子研究课题。</div>
        </div>
        <div class="step-box">
          <div class="step-title">② 构建任务 DAG 依赖图</div>
          <div class="step-desc">声明阶段产物输入输出协议，确定哪些子任务可并发运行，哪些需要等待前置依赖。</div>
        </div>
        <div class="step-box highlight-box">
          <div class="step-title highlight-title">③ 持久化 Plan 检查点</div>
          <div class="step-desc">将解构出的子任务清单持久化入库，任何崩溃均可直接加载规划，无需重复规划。</div>
        </div>
      </div>
    </div>

    <div class="arrow-down">▼ 状态机流转: PLANNING ➔ DISPATCHING</div>

    <!-- 阶段 3 -->
    <div class="stage">
      <div class="stage-sidebar">
        <div class="stage-num">阶段 03</div>
        <div class="stage-name">子智能体并发派发与执行</div>
      </div>
      <div class="stage-content">
        <div class="step-box">
          <div class="step-title">① 独立上下文沙箱派发</div>
          <div class="step-desc">为检索智能体、分析智能体各分配独立 Context 窗口，杜绝上下文互相污染与膨胀。</div>
        </div>
        <div class="step-box">
          <div class="step-title">② 工具调用与深度爬取</div>
          <div class="step-desc">Sub-Agent 调用 WebSearch / Tool API，收集多源事实数据，并执行单步自我过滤。</div>
        </div>
        <div class="step-box highlight-box">
          <div class="step-title highlight-title">③ 断点保存与中断恢复 (Durable)</div>
          <div class="step-desc">若网络超时或任务挂起，立即保存子状态。系统重启后由引擎自动加载断点恢复执行。</div>
        </div>
      </div>
    </div>

    <div class="arrow-down">▼ 状态机流转: RUNNING ➔ VERIFYING</div>

    <!-- 阶段 4 -->
    <div class="stage">
      <div class="stage-sidebar">
        <div class="stage-num">阶段 04</div>
        <div class="stage-name">评测守卫与反思核验</div>
      </div>
      <div class="stage-content">
        <div class="step-box">
          <div class="step-title">① 汇聚子智能体产物</div>
          <div class="step-desc">消息总线捕获各 Sub-Agent 交付的结构化成果，解除阻塞并转交综合智能体。</div>
        </div>
        <div class="step-box">
          <div class="step-title">② 独立核查员反思 (Verifier)</div>
          <div class="step-desc">调度 Verifier Sub-Agent 执行幻觉核验、数据矛盾检测与引用真实性核对。</div>
        </div>
        <div class="step-box">
          <div class="step-title">③ 质量准出评估 (Evaluation Gate)</div>
          <div class="step-desc">计算完成率、结构完整性与指标阈值；若未通过，则触发局部有针对性重试。</div>
        </div>
      </div>
    </div>

    <div class="arrow-down">▼ 状态机流转: VERIFYING ➔ COMPLETED</div>

    <!-- 阶段 5 -->
    <div class="stage">
      <div class="stage-sidebar">
        <div class="stage-num">阶段 05</div>
        <div class="stage-name">成果交付与平台资产沉淀</div>
      </div>
      <div class="stage-content">
        <div class="step-box">
          <div class="step-title">① 生成最终成果物</div>
          <div class="step-desc">输出包含执行链路、论证证据与结构化结论的完整报告并通知用户/上游系统。</div>
        </div>
        <div class="step-box">
          <div class="step-title">② 运行时审计与日志归档</div>
          <div class="step-desc">持久化全量 Event Log、Token 消耗统计、各环节耗时，供后续可观测性分析。</div>
        </div>
        <div class="step-box">
          <div class="step-title">③ 沉淀 Reference Architecture</div>
          <div class="step-desc">验证有效的 Prompt 模式、重试策略与子任务调度范式同步至 AgentSphere 平台。</div>
        </div>
      </div>
    </div>
  </div>
</body>
</html>
"""

def generate_images():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1260, "height": 960}, device_scale_factor=2)
        
        # 1. 架构全景图
        page.set_content(html_content_arch)
        img1_docs = os.path.join(output_dir_docs, "architecture_overview.png")
        img1_brain = os.path.join(output_dir_brain, "architecture_overview.png")
        page.screenshot(path=img1_docs, full_page=True)
        page.screenshot(path=img1_brain, full_page=True)
        print(f"Generated {img1_docs}")
        
        # 2. 流程图
        page.set_content(html_content_flow)
        img2_docs = os.path.join(output_dir_docs, "durable_workflow.png")
        img2_brain = os.path.join(output_dir_brain, "durable_workflow.png")
        page.screenshot(path=img2_docs, full_page=True)
        page.screenshot(path=img2_brain, full_page=True)
        print(f"Generated {img2_docs}")
        
        browser.close()

if __name__ == "__main__":
    generate_images()
