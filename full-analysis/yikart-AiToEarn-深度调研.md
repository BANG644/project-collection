# AiToEarn（一人公司的 AI 内容营销智能体）深度调研

> 数据来源：GitHub API 抓取（stars / README / 目录树 / package.json / .mcp.json），抓取日期 2026-10-05。许可：MIT。语言：TypeScript（全栈 monorepo，含 Electron 桌面端）。

## 一、项目定位（一句话）
面向 **OPC（一人公司 / One-Person Company）** 的 AI 内容营销智能体平台：用 Agent 自动化覆盖「创作 → 发布 → 互动 → 变现」全链路，一键把内容分发到抖音 / 小红书 / B站 / TikTok / YouTube 等 14+ 主流平台。

## 二、项目亮点（差异化）
1. **四大 Agent 闭环**：`Create`（创意→成品，调用视频/图文模型批量铺量）、`Publish`（跨 14 平台统一分发 + 日历排期）、`Engage`（浏览器插件自动点赞/关注/AI 评论/高转化信号挖掘）、`Monetize`（商家推广任务结算，CPS/CPE/CPM 三种结果导向模式）。
2. **五种使用形态**：官网直用 / 龙虾 OpenClaw / Claude·Cursor 等 MCP / Docker 私有化 / 源码开发——同一个能力多入口触达。
3. **MCP 协议原生支持**：后端自带 MCP Server（`nx-mcp`，stdio），可在任意支持 MCP 的 Agent 或大模型中直接调用。
4. **矩阵账号运营**：批量下发创作任务、Agent 并行生成多条内容，面向规模化内容分发。
5. **真实大型全栈应用**：仓库 375 MB、3411 个文件，是经生产打磨的 TS 工程而非 demo。

## 三、核心架构
- **Nx + pnpm monorepo**（`pnpm@10.33`、`nx@22.7`），三大子项目：
  - `project/aitoearn-backend`：后端（NestJS 风格，经 `@nx/nest`），含 Dockerfile 与 `.mcp.json`。
  - `project/aitoearn-web`：前端（**Next.js + Ant Design + Lexical 富文本 + Radix UI + FullCalendar**），带 Dockerfile。
  - `project/aitoearn-electron`：桌面端（electron-builder，Tauri 非此仓）。
- **Agent-Native 开发范式**：后端仓库自带一整套 `.agents/skills/`（`caveman`、`diagnose` 含 HITL 循环、`grill-me`、`grill-with-docs`、`handoff`、`improve-codebase-architecture`、`prototype`、`tdd`、`setup-matt-pocock-skills`…），即**项目本身即用 AI Agent 工作流驱动开发与交接**，是研究「agent 化软件工程」的活样本。
- **发布/变现编排层**：把各平台授权（Server Relay）与平台 AI 模型（AI Relay）拆分，配合「内容交易市场」「开放平台」构成商业闭环。

## 四、应用场景与启发
- 「**内容工业化**」落地范式：把多平台授权、结算、Agent 编排组合成产品，技术护城河在「编排 + 合规授权 + 结算」而非底层模型。
- 多入口（Web / OpenClaw / MCP / Docker）的分发设计，对「同一能力如何适配不同用户形态」有参考价值。
- 仓库内 `.agents/skills` 体系（含 HITL 人审 loop）是「用 Agent 维护 Agent 产品」的可复用模板。

## 五、源码深度解读
**`project/aitoearn-backend/package.json`（工程基座）**：声明 `pnpm@10.33` + `nx@22.7` + `@nx/nest`，`@nx/eslint`、`@nx/vite`、`@nx/vitest` 全链路；`simple-git-hooks` 的 pre-commit 跑 `lint-staged`，规范即代码。
```json
"packageManager": "pnpm@10.33.0",
"scripts": { "ai:serve": "nx serve aitoearn-ai", "server:serve": "nx serve aitoearn-server" },
"devDependencies": { "nx": "22.7.1", "@nx/nest": "22.7.1", "@nx/vite": "22.7.1", "vitest": "4.1.5" }
```
**`project/aitoearn-backend/.mcp.json`（MCP 暴露）**：以 stdio 方式挂 `nx-mcp`，使外部 Agent 可直接驱动后端能力。
```json
{ "mcpServers": { "nx-mcp": { "type": "stdio", "command": "npx", "args": ["nx-mcp"] } } }
```
**`project/aitoearn-web/package.json`（前端栈）**：Next.js（`@ant-design/nextjs-registry`）+ Ant Design 6 + Lexical（`@lexical/*` 富文本）+ Radix UI 全系 + FullCalendar 排期 + `@microsoft/fetch-event-source` 流式——印证「日历排期 + 富文本创作 + 流式生成」的产品形态。

## 六、社区口碑
⭐**26,284**（Trendshift 榜单在列，多语言 README 中/英/日）。作为「AI 副业/出海」热门赛道代表，社区关注度高；但 README 含大量赞助商（秘塔 MiniMax、APIMart）导流，商业化气息浓，需区分「产品价值」与「营销内容」。

## 七、竞品对比
| 维度 | AiToEarn | Buffer/Hootsuite | MoneyPrinterTurbo/NarratoAI |
|---|---|---|---|
| 本质 | AI Agent 内容营销闭环 | 传统社媒排期管理 | AI 视频生成 |
| 变现 | 内置 CPS/CPE/CPM 结算 | 无 | 无 |
| Agent 化 | 创作/发布/互动全 Agent | 仅定时发布 | 仅生成 |
| 多平台发布 | 14+ 平台原生分发 | 支持但非 AI | 一般导出 |

差异：友商多在「单点」（生成或排期），本项目主打「创作→发布→互动→变现」**全闭环 + Agent 编排**。

## 八、核心研判
✅ 真实大型 TS 全栈 + 多端 + MCP 的生产级项目，架构清晰、Agent-Native 实践可借鉴，是「AI 内容工业化」的优秀样本。
⚠️ 技术护城河偏「编排 + 授权 + 结算」而非底层模型；核心能力是对各家视频/图文模型的调用与编排，须关注平台 API 变动与合规风险（自动互动涉及平台 ToS）。
📌 推荐场景：研究「一人公司如何用 Agent 做内容变现」「agent 化软件开发工作流」「多入口能力分发」。不推荐作为底层模型/算法学习样本。

## 九、关键文件路径速查
- `project/aitoearn-backend/package.json` — 工程基座（pnpm/nx/Nest）
- `project/aitoearn-web/package.json` — 前端栈（Next.js/AntD/Lexical）
- `project/aitoearn-electron/` — 桌面端（electron-builder）
- `project/aitoearn-backend/.mcp.json` — MCP Server 暴露
- `project/aitoearn-backend/.agents/skills/` — 内置 Agent 开发工作流（含 HITL）
- `nginx/`、`docker` 相关 — 私有化部署配置
