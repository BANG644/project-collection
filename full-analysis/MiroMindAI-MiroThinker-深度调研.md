# MiroMindAI/MiroThinker 深度调研

> 调研日期：2026-08-01 ｜ Stars：8,361 ｜ 语言：Python ｜ 协议：Apache-2.0 ｜ 默认分支：main
> 模型系列 MiroThinker-1.7（基于 Qwen3 训练：8B/30B/72B/235B）

## 一、项目定位

深度研究（Deep Research）Agent 开源实现，核心创新是 **interactive scaling（交互式扩展）**——让 Agent 在不确定时自主投入更多搜索 / 计算步数，而非固定预算。在 BrowseComp（英文 74.0 / 中文 75.3）等深度搜索基准上达到 SOTA。既是可跑的 Agent 框架，也是配套训练数据的产出管线（collect-trace 用于 SFT/DPO）。

## 二、项目亮点

1. **Interactive Scaling（交互式扩展）**：不同于"固定轮数"的常规 Agent，MiroThinker 根据问题难度动态分配工具调用预算，难任务自动多搜多想——这是其刷榜 BrowseComp 的关键机制。
2. **近因上下文保留（keep_tool_result）**：只保留最近 K 条工具结果、但完整保留"思考+动作"轨迹，在不掉性能的前提下腾出上下文空间，支撑 256K 长上下文与数百步轨迹。
3. **可复现的基准矩阵**：GAIA / HLE / BrowseComp(EN&ZH) / WebWalkerQA / XBench / FRAMES / SEAL-0 / FutureX / AIME2025 / DeepSearchQA 全套评测脚本开箱即用。
4. **工具链开放且可本地化**：默认 E2B(沙箱) + Serper(搜索) + Jina(抓取)，并提供 `tool-vqa-os` / `tool-transcribe-os` / `tool-reasoning-os` 等开源本地替代，避免全链路依赖商业 API。
5. **训练数据闭环**：`apps/collect-trace` 能从 Claude/Codex/Qwen 收集轨迹，反哺 SFT/DPO——不止是推理脚本，更是"造深度研究模型"的方法论。

## 三、核心架构

```
main.py ──→ orchestrator(ReAct 主循环)
              ├─ pipeline       # 单步: 思考→选工具→执行→观察
              ├─ tool_executor  # 调度 E2B/Serper/Jina/VQA/Reasoning...
              ├─ answer_generator# 基于保留的轨迹生成最终答案
              └─ stream_handler  # 流式输出
           上下文管理: keep_tool_result(K) 近因保留
配置: conf/agent/*.yaml (max_turns / keep_tool_result / tools)
```

Agent 与模型解耦：`llm=qwen-3|claude-3-7|gpt-5`，模型权重用 SGLang/vLLM 自托管，Agent 逻辑在 `apps/miroflow-agent`。

## 四、应用场景与启发

- **深度研究自动化**：市场/竞品/学术调研中需要"多轮搜索+交叉验证+长链条推理"的任务，可直接用 MiroThinker 跑（配 Qwen3-235B 或 Claude）。
- **造自己的深度研究模型**：`collect-trace` + SFT/DPO 流程，把强模型轨迹蒸馏到小模型，是"小模型也能做深搜"的可行路径。
- **给同类需求的思路**：
  - "interactive scaling + 近因上下文"组合解决了 ReAct Agent 的两大痛点（预算僵化、长轨迹爆上下文），比简单堆 max_turns 更优雅。
  - 工具用 YAML 声明式组合（`conf/agent/*.yaml`），方便团队按需插拔 MCP/本地工具。

## 五、源码深度解读

> 路径来自仓库真实 `apps/miroflow-agent/` 与 `libs/miroflow-tools/` 树；近因策略细节来自 README 配置说明。

### 1) 编排主循环（apps/miroflow-agent/src/core/orchestrator.py）

```
orchestrator.run(task):
  while step < max_turns:
    thought, action = pipeline.step(trace)      # 思考+选工具
    obs = tool_executor.run(action)             # 执行(搜索/代码/抓取)
    trace.append(thought, action, obs)
    trace = retain_recent(trace, K)             # keep_tool_result: 仅留最近 K 条 obs
  return answer_generator.generate(trace)
```

### 2) 近因上下文保留（keep_tool_result，README 明示机制）

```
keep_tool_result = K   # 只保留最近 K 条 tool 结果, 但完整保留 thought/action 序列
# 经验: Agent 后续动作更依赖近期观测而非远期; 该策略在不掉性能下释放上下文
```

这一设计让 256K 上下文能承载数百步轨迹，是 interactive scaling 能成立的前提。

### 3) 工具执行器（apps/miroflow-agent/src/core/tool_executor.py）

统一调度 `libs/miroflow-tools/` 下的搜索/抓取/沙箱/视觉/语音/推理工具；配置驱动（`conf/agent/*.yaml` 列出 `tool-python / search_and_scrape_webpage / jina_scrape_llm_summary / tool-vqa ...`），支持开源本地工具替代商业 API。

## 六、社区口碑

- 学术/工程信号强：BrowseComp SOTA 成绩、完整基准脚本、Qwen3 多尺寸权重开源，在深度研究 Agent 圈有口碑。
- 明确的推荐配置（`mirothinker_1.7_keep5_max200/300`）与详尽部署/评测文档，降低复现门槛。
- 具体 HN/Reddit/Issue 情感「数据不可用」（本轮未逐条抓取）。

## 七、竞品对比 + 核心研判

| 维度 | MiroThinker | OpenAI Deep Research(闭源) | Gemini DR(闭源) | opendeepresearch(开源) | langchain DeepAgents |
|------|------------|---------------------------|-----------------|------------------------|----------------------|
| 开源/权重 | 是(模型+代码) | 否 | 否 | 是(仅代码) | 是 |
| Interactive Scaling | 是(核心创新) | 是(内部) | 是(内部) | 否(固定) | 部分 |
| 长上下文管理 | keep_tool_result 近因 | 内部 | 内部 | 弱 | 弱 |
| 本地化工具 | 提供开源替代 | 否 | 否 | 部分 | 部分 |
| 训练数据闭环 | 是(collect-trace) | 否 | 否 | 否 | 否 |

**核心研判**：
- 优势：把"交互式扩展 + 近因上下文"做成开源可复现方案，且附带造模型的数据闭环，是深度学习 Agent 研究的优质基线。
- 风险：强结果依赖强基座模型（Qwen3-235B / Claude / GPT-5）与商业工具（E2B/Serper/Jina）默认组合，全开源本地化需自行替换且性能可能下降；小模型权重效果「数据不可用」未逐项核实。
- 启发：做深度研究 Agent 时，"动态预算 + 近因上下文"应作为默认设计；想自研深搜模型，其 collect-trace→SFT/DPO 流水线是直接可抄的方法论。

## 八、关键文件路径速查

| 模块 | 路径 |
|------|------|
| 编排主循环 | `apps/miroflow-agent/src/core/orchestrator.py` |
| 单步流水线 | `apps/miroflow-agent/src/core/pipeline.py` |
| 工具执行 | `apps/miroflow-agent/src/core/tool_executor.py` |
| 答案生成 | `apps/miroflow-agent/src/core/answer_generator.py` |
| 流式 | `apps/miroflow-agent/src/core/stream_handler.py` |
| 配置 | `apps/miroflow-agent/conf/agent/*.yaml`（`mirothinker_1.7_keep5_max200` 等） |
| 工具库 | `libs/miroflow-tools/`（含 `tool-vqa-os`/`tool-transcribe-os`/`tool-reasoning-os`） |
| 轨迹收集(训练) | `apps/collect-trace/`（`collect_trace_*.sh`） |
| 入口/部署 | `apps/miroflow-agent/main.py` · `apps/gradio-demo/` · `.env.example` |
