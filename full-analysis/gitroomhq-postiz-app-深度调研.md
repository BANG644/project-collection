# gitroomhq/postiz-app 深度调研

> 调研日期：2026-10-27 ｜ 数据来源：GitHub API（README / 源码树 / 关键源文件）+ 当日 GitHub Trending 日榜
> 许可证：**AGPL-3.0**（云版与自托管同功能、不锁特性；修改并分发需开源）

## 项目亮点（差异化）

- **开源可自托管的社媒调度平台**，对标 Buffer / Hootsuite / Later，支持 16+ 平台（X / Instagram / YouTube / TikTok / LinkedIn / Reddit / Threads / Bluesky / Mastodon / Discord / Slack / Pinterest / Dribbble / Facebook …）。
- **真正的 agentic 表面**：自带 **MCP Server（基于 Mastra）** + CLI + 一连串连接器（Claude / ChatGPT / Codex / OpenClaw / Cursor / Hermes / Grok / MCP / AI Agents CLI），把"社媒发布"封装成 agent 可调用的工具面。
- **技术栈成熟**：pnpm monorepo + NextJS（前端）+ NestJS（后端）+ Prisma/PostgreSQL + Temporal（长任务编排）+ Resend（邮件）。
- **合规清晰**：只用官方 OAuth、不抓取平台、不收集/代理用户 token，降低封号风险。
- **云版与自托管完全同功能**，不做特性阉割（AGPL 下卖托管服务）。

## 项目定位（一句话）

Postiz 是一个**开源、可自托管的社媒管理与调度平台**，并把"发帖 / 分析 / 协作"能力以 MCP + CLI + 多 harness 连接器的形式暴露给 AI agent。

## 核心架构

- **`apps/backend`**（NestJS）：REST API、调度引擎、渠道 OAuth、与 Temporal 衔接；`api/routes/*.controller.ts` 是 HTTP 入口。
- **`apps/commands`**（NestJS commands）：`run:agent` 等 CLI 任务入口。
- **`apps/orchestrator`**：Temporal `workflows/`（如 `clipping.workflow.ts`）与 `activities/`（如 `clipping.activity.ts`），负责长任务编排。
- **`libraries/nestjs-libraries`**：共享核心——`agent/`（AgentGraphService 等）、`chat/`（MCP relay、tools、Mastra 封装）、`database/prisma`。
- **`libraries/react-shared-libraries`**：前端共享组件与 i18n。

## 源码深度解读（2 个核心模块）

**1. MCP Server 引导 —— `libraries/nestjs-libraries/src/chat/start.mcp.ts`**

`startMcp(app)` 从 Nest 容器取出 Mastra / Organization / OAuth / LoadTools 服务，启动 `@mastra/mcp` 的 `MCPServer`：

```ts
const mastra = await mastraService.mastra();
const agent = mastra.getAgent('postiz');
const agentTools = await agent.listTools();
const tools = { ...agentTools, ...(await loadToolsService.loadTools(true)) };
```

鉴权区分三种 token：`pos_`（OAuth token，经 `oauthService.getOrgByOAuthToken`）、普通 API key（`organizationService.getOrgByApiKey`）、`psh_`（指向另一个自托管 Postiz 的 relay，由 `McpRelayService` 处理）。还处理 `subscriptions/listen` 长连接的 10s 优雅结束、OAuth 中间件，以及"Claude connector 目录不接受 AI 媒体生成工具"时隐藏对应工具——说明它对**不同 MCP host 有差异化工具暴露**。

**2. agent 执行入口 —— `apps/commands/src/tasks/agent.run.ts`**

```ts
@Command({ command: 'run:agent', describe: 'Run the agent' })
async agentRun() {
  console.log(await this._agentGraphService.createGraph('hello', true));
}
```

`@nestjs-command` 的 `run:agent` 实际调用 `AgentGraphService.createGraph(...)`——即 agent 图（graph）的执行编排，位于 `libraries/nestjs-libraries/src/agent/agent.graph.service.ts` 与 `agent.module.ts`。

## 应用场景与启发

- **社媒运营团队 / 个人创作者**的开源替代：调度、分析、团队协作、RSS 自动发、AI Copilot 一站式。
- **agentic 接入范式值得借鉴**：把"社媒操作"封装成 MCP 工具 + 多 harness 连接器 + CLI，让任意 agent 直接发布/查询——与 WorkBuddy 的 skill/agent 生态同构。
- **Temporal 做长任务编排**（如视频剪辑 workflow）是可靠范式，适合任何"步骤多、需可恢复"的异步 pipeline。

## 社区口碑

- **38,284⭐**，AGPL-3.0，2023-07 创建，最近推送 2026-10-24（持续活跃）；README 自述 7M+ 下载。社媒运营圈知名度高，是开源社媒调度赛道头部。
- 2026-10-27 登上 GitHub Trending 日榜。
- 合规声明清晰（官方 OAuth、不抓取、不收 token），降低封号与被平台限制风险。

## 竞品对比

| 维度 | Postiz | Buffer/Hootsuite/Later | 通用自动化（N8N/Make） |
|------|--------|----------------------|----------------------|
| 许可证 | AGPL-3.0 开源自托管 | 闭源 SaaS | 开源/商业 |
| 特性 | 调度+分析+协作+RSS+AI | 类似 | 通用，无社媒垂直能力 |
| agentic | 原生 MCP/CLI/连接器 | 弱/无 | 需自建 |
| 采用成本 | 自托管需过各平台 OAuth 审核 | 开箱即用 | 需搭流程 |

## 核心研判

- **价值**：最成熟的开源社媒调度 + 原生 agentic 接入；想把"社媒操作"变成 agent 工具面，Postiz 是现成参考与脚手架。
- **采用**：自托管需自行过 Meta/YouTube/TikTok 等 OAuth 审核（可能数周），云版开箱即用；AGPL-3.0 下纯内部使用无碍，修改分发需开源。
- **风险**：PostgreSQL/Redis/Temporal 全家桶，运维较重；多平台 OAuth 审批是主要落地摩擦。

## 关键文件路径速查

- `apps/backend/src/api/routes/*.controller.ts` — HTTP / 调度入口
- `libraries/nestjs-libraries/src/chat/start.mcp.ts` — MCP Server 引导（核心 agentic 接入）
- `libraries/nestjs-libraries/src/chat/mcp.relay.service.ts` — 自托管 relay
- `libraries/nestjs-libraries/src/chat/load.tools.service.ts` / `tools/clipping.tool.ts` — 工具装载
- `apps/commands/src/tasks/agent.run.ts` — `run:agent` CLI
- `libraries/nestjs-libraries/src/agent/agent.module.ts` / `agent.graph.service.ts` — agent 图编排
- `apps/orchestrator/src/workflows/clipping.workflow.ts` — Temporal 长任务
