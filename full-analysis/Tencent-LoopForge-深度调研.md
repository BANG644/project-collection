# 🔬 Tencent/LoopForge — 全方位深度调研

> 调研日期：2026-11-15 ｜ Stars：812 ｜ 语言：Go（1.26+） ｜ 许可：MIT ｜ 编号：#595

## 📌 一句话定位
**LoopForge** 是腾讯开源（MIT）的**自托管「AI 研发交付」平台**——用 **SOP（标准作业流程）** 把 CodeBuddy、Codex、Claude Code 等 **10 种 coding-agent CLI** 编排成可复用、带人工门禁、带运行证据的交付流程，解决「用 Agent 写代码容易，但团队级、可重复、质量可控地交付难」的痛点。

## ⭐ 项目亮点
- **双工作路径**：① 与 Main Bot 聊天（按需开 Docker 沙箱，可中途转向/接管）；② 跑 SOP（可视化画布，节点类型：Agent / Script / Human-gate / Sub-SOP / Preview build），把成功路径固化成可复用标准流程。
- **角色分离**：planner / implementer / reviewer / tester 各自拥有独立的 prompt、executor、model、rules、Skills、MCP 工具——直接消解「Agent 自己 review 自己 diff」的偏置。
- **人工在环（HITL）**：Human-gate 节点暂停运行，等待人审批或**退回上游**节点；失败检查可自动 rework 到更早步骤。
- **可观测、可恢复**：节点状态、工具调用 trace、worker 日志、每节点产物快照、workspace 预览；可暂停、重试、从任意节点重跑。
- **团队级交付闭环**：需求（Requirement）→ 交付（PR/MR）全链路追踪，PR/MR 状态与直接分支合并检测；工程指标 + 业务域报告 + token/成本按公开标价核算。
- **已在腾讯内部验证**：据官方披露已部署 **20+ 业务线**，月自动化 **200+ 需求/工单**；MIT + 纯自托管是其采用关键。

## 🏗️ 项目架构全景
Go monorepo，模块边界清晰（架构文档 `docs/architecture.md` 明确保留上游 Go module 名 `agentflow` 与 `AGENTFLOW_*` 环境变量以降低合并冲突）：
- `cmd/agentflow`：API / worker / 合并进程；`cmd/agentflow-runner`：个人与池化执行机；`cmd/agentflow-mcp` 与 `cmd/agentflow-gate-mcp`：公开 MCP 与结构化门禁结果。
- `internal/engine`：SOP 图、租约（lease）、调度、沙箱生命周期与交付——就绪分支在运行 workspace 内一起执行，取消后重跑某分支会恢复被取消的兄弟分支。
- `internal/domain`：WorkflowDefinition / Run / Node / SOP / Requirement 等核心领域模型。
- `internal/repo`：MySQL 持久化（每业务域一个 repository）；`internal/httpapi`：HTTP/MCP 处理器；`internal/runtime` 与 `internal/runner`：executor 协议、凭证、隔离与产物；`internal/tracker`：远端 Issue/PR 适配器；另有 `gatemcp` / `schedule` / `runeval` / `notification` / `observability` 等。
- 部署：`docker compose` 拉取 GHCR 镜像（无需本机 Go/Node），监听 `0.0.0.0:8090`；`local/` 提供 CLI 版（`npx loopforge-cli install claude`）。

## 💡 应用场景与启发
- **典型场景**：① 探索/小修用聊天；② 一旦某类需求跑通，沉淀成 SOP（角色+脚本+人工门禁），下次同类型复用；③ 内置 backend / frontend / bug-fix / product 四类 SOP 直接当蓝图。
- **可借鉴模式**：**把「工程交接」当一等公民**——跨角色、跨环境的 handoff（谁在什么沙箱、按什么顺序、带什么检查、谁签字）才是团队级 AI 研发的瓶颈，而非「写代码」本身。LoopForge 用「SOP 节点 + 独立 reviewer 角色 + 人工门禁 + 运行证据」把交接标准化。
- **同类需求思路**：若你要做团队级 AI 研发平台，其架构范式（角色分离 + DAG 化 SOP + 人工闸门 + 需求→交付追踪 + 成本可观测）值得直接参考；用 Docker 沙箱承载真实仓库、GitHub OAuth 做 PR 交付、把「agent 不应自评」用组织约束而非提示词解决。

## 🧠 核心源码解读（克制代码量）
SOP 的本质是一个 **DAG 调度器**。`internal/engine/workflow_graph.go` 的 `readyNodes()` 给出核心算法——节点就绪当且仅当它的所有依赖边源节点状态均为 `"succeeded"`：
```go
for _, n := range wf.Nodes {
    if r.Nodes[n.ID].Status != "pending" { continue }
    ready := true
    for _, d := range deps[n.ID] {
        if r.Nodes[d].Status != "succeeded" { ready = false }
    }
    if ready { out = append(out, n) }
}
```
同文件的 `ancestors()` / `descendants()` 用邻接表回溯计算「重跑范围」——这是「取消后重跑一个分支会恢复被取消的兄弟分支」的实现基础。

人工门禁是可机检的契约。`internal/engine/gate_submit.go` 中，门禁结果以 JSON 产物落盘到 `.agentflow/gate-results/<node>/attempt-N.json`，engine 读取并校验 `GateResult.Decision ∈ {pass, rework, fail, human}`，且 `rework`/`human` 必须带 `ActionRequired` 与 `Reason`——把「人是否批准、为什么、退回哪一步」变成结构化、可校验、可审计的事件，而非聊天里一句口头确认。

## 📊 社区口碑（外链）
- 2026-07 开源后趋势上升，11-14 约 **700+⭐、单日 +174**；explainx.ai、thenextgentechinsider、gatebase、agipath 等均有报道，普遍认可其「团队级 AI 研发交付」定位。
- **风险/争议**（来自 mrkeyoor 沙箱实测与 README 自陈）：① `go test` 实测 **23 passed / 5 failed**（测试未全绿），成熟度尚早；② 默认经 Docker socket 起沙箱，**仅适合信任团队**，非多租户隔离；③ 聊天工作台目前**仅中文**，英文团队需注意；④ 默认跨实例用户可读项目数据，须设 `AGENTFLOW_ALLOW_SIGNUP=false` + HTTPS 再对外。

## 🥊 竞品对比
| 维度 | LoopForge | Dify / n8n / Flowise | Plannotator | Agent Autoloop |
|------|-----------|----------------------|-------------|----------------|
| 定位 | 团队级软件交付（coding-agent 编排） | 通用 AI/自动化工作流 | 本地 Agent review 面 | 后台 Agent hub |
| 差异化 | 角色分离 + Docker 沙箱 + GitHub 交付 + 人工门禁 + 运行证据 + 成本报表 | 通用、非交付专用 | 单开发者审查面 | 后台运行 |
**研判**：LoopForge 不与通用工作流 builder 正面竞争，而是把「软件交付」做成专用层；其护城河是「SOP 复用 + 人工门禁 + 运行证据 + 自托管」的团队交付闭环。

## 🎯 核心研判
方向正确——瓶颈确实在「跨角色/跨环境的工程交接」，且已被腾讯内部 20+ 业务线验证。但成熟度仍早期（测试不全绿、中文 UI、隔离边界弱），**适合信任团队私有部署，不适合多租户 SaaS**。MIT + 自托管是采用关键；若团队已用多种 coding CLI 且交付质量失控，LoopForge 是当前最贴合的编排层。

## 📁 关键文件路径速查
- 架构：`docs/architecture.md`
- SOP 引擎：`internal/engine/engine.go`、`internal/engine/workflow_graph.go`、`internal/engine/node_execute.go`
- 人工门禁：`internal/engine/gate_submit.go`、`internal/engine/bot_control.go`
- 领域模型：`internal/domain/workflow.go`、`internal/domain/run.go`、`internal/domain/sop_lane.go`、`internal/domain/requirement.go`
- 入口：`cmd/agentflow`、`cmd/agentflow-runner`、`start.sh`
