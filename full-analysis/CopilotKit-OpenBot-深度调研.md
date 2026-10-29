# CopilotKit/OpenBot 深度调研

> 调研日期：2026-10-30 ｜ 数据来源：GitHub API（README / `docs/architecture.md` / `server/src/computer/gateway.ts` / `server/src/computer/policy.ts` 真实源码）+ 当日 GitHub Trending 日榜
> 许可证：**MIT** ｜ 形态：自托管的「公司自有 AI 同事」平台（AG-UI 协议 / Docker Compose / React+Vite+Hono 单体仓）

## 项目亮点（差异化）

- **「公司真正拥有的 AI 助手」**：形态与 ChatGPT/Claude 类似，但跑在你自己的基础设施上、可任意改造；每个 coworker 拥有**独立的真实浏览器（带自己的登录态）、独立的文件、且仅被授予你许可的工具**。
- **AG-UI 协议解耦框架**：任何说 [AG-UI](https://github.com/ag-ui-protocol/ag-ui) 的端点都是「Bot」——LangGraph / Mastra / CrewAI / Pydantic AI / Google ADK 或手写 agent 同等待遇，治理随协议走而非随框架走。
- **网关即唯一通路（fail-closed）**：agent 对浏览器/文件/MCP/组件的任何动作都只经一个网关——**解析真实元素→问策略→写审计行→才执行**；deny 优先、缺策略即拒、坏规则即拒。
- **CEL 策略语言 + dry-run**：用 Google CEL 表达式写边界（而非列规则表），支持 `dry-run`（只决策+记录不拦截）先观测真实流量再切 `enforce`；`deny` 列表保证「禁止」不可被更广的 allow 反噬。
- **可审计、可接管、密钥不出转录**：`/admin/audit` 列出每条允许/拒绝/失败及对应规则；agent 遇登录墙可「请求接管」，人驾驶期间 Bot 动作被拒而非排队；密钥只记「请求了多久」不记内容。

## 项目定位（一句话）

OpenBot 是一个**自托管的 agent 平台**——把任意 AG-UI agent 变成「有自己浏览器、文件与工具、且每个动作都先被策略判定并记录」的公司同事，本质是在「agent 能用你的工具」和「你能放心让它靠近工具」之间架一道网关。

> 注：官方明言 **OpenBot 是模板而非产品**——clone 后替换 `examples/` 下的租户包、自建 coworkers/channels/skills；无托管版、无发布包依赖。当前 **Beta、活跃开发中**（最近推送 2026-10-29）。

## 核心架构

| 服务 | 端口 | 职责 |
|------|------|------|
| `app` | 3010 | React/Vite UI（频道、Bot 页、管理台） |
| `server` | 3001 | Hono API：CopilotKit runtime、auth、策略、审计、插件、组件、coworkers、channels |
| `agent-computer` | 4100 | 每个 Bot 一台 Chromium + `/workspace` + 浏览器档案 |
| `agent-bot` | 4200 | 概念验证 AG-UI Bot |
| `agent-langgraph` | 4201 | LangGraph AG-UI Bot |
| `supervisor` | 4500(host)/4300(container) | 给每人/每个 Isolated Bot 创建并管理一台 computer |
| `worker` | — | 触发到期 routine，交给 server 执行 |
| PostgreSQL + pgvector | 5432 | 产品数据、策略、审计、凭证、授权、频道、组件元数据 |
| CopilotKit Intelligence | 外部 | 持久化 thread 与记忆 |

- **数据自持**：Docker Compose 拉起全栈，数据落你自己的 PostgreSQL；模型密钥由管理员提供、**静态加密、从不记录**。
- **每人数一台 machine**：supervisor 给每人/每个 Isolated Bot 一台 container（各带 Chromium、登录态、workspace）；`COMPUTER_RUNTIME=runsc` 可跑在 gVisor 下。
- **组件而非散文**：编译后的 React 组件（`app/src/components/gallery/`）经 `/admin/playground` 沙箱创作、免部署发布；每次调用前 server 校验「组件存在/已发布/未被对该 Bot  withholding」。

## 源码深度解读（核心模块：`server/src/computer/` 网关与策略）

**1. 网关是动作到达 computer 的唯一通路（`gateway.ts` 文件头注释）**

```ts
// The only way an action reaches a Bot's computer.
//   1. Resolve the ref the caller sent into the element it actually points at,
//      from the snapshot this server fetched. Never from what the caller said.
//   2. Ask the policy. Deny beats allow, an absent policy denies, and a broken rule denies.
//   3. Write the row, whichever way the decision went, and only then act.
```

三段式铁律：**① 用 server 自己抓取的快照把调用方给的 ref 解析成真实元素（绝不信任模型自报的 label）**；② 问策略（deny 优先、缺策略拒、坏规则拒）；③ **先写审计行再执行**——「没被记录的动作 = 没发生」，因为没有绕过写行就能执行的路径。第①步是「never click Submit」不会被 `{name:"Continue"}` 绕过的根本。

**2. 用 CEL 而非规则表写边界（`policy.ts`）**

```ts
export type ActionPolicy = {
  mode: "dry-run" | "enforce";   // dry-run 只决策+记录不拦截
  deny: string[];                // 先评估，任一为真即拒，无关 allow
  allow: string[];               // 任一为真即许；空=什么都不许
};
// PolicyContext 可写的维度：
//   tool.name / bot.id / page.{url,host} / actor.id /
//   element.* / key / intent(activate|type|navigate|read|write_file|run_command…) /
//   file.* / mcp.* / initiator.*
```

设计要点：`intent`（`activate`/`type`/`navigate`/`run_command`…）表达的是**效果**而非机制——「不要激活任何叫 submit 的东西」一条规则就能覆盖 click/Enter/Space 三种激活路径，避免 agent 用按 Enter 绕过「禁止点击 Submit」。`element` 由网关从 server 快照解析，**攻击者自报的 label 无效**。

## 应用场景与启发

- **企业自托管「AI 同事」**：需要把 agent 接进公司浏览器/SaaS/文件，又必须满足合规审计、最小权限、可接管——OpenBot 的网关+CEL+审计三件套是可直接借鉴的治理骨架。
- **「策略即代码」的 agent 治理范式**：CEL 表达式 + dry-run 先观测后拦截 + deny 优先，比「allow 列表」更能表达真实业务边界；任何要「让 agent 操作敏感工具」的系统都该学这套。
- **AG-UI 解耦思路**：把「agent 框架」与「运行/治理平台」通过开放协议解耦，避免被单一框架锁定——对自建 agent 中台的团队是高价值参考。
- **边界可迁移**：其「解析真实元素、不信任 caller 自报、先记录后执行」三原则，适用于任何「LLM 驱动 UI 操作」的安全中间件。

## 社区口碑

- **7,993⭐**（2026-10-30 抓取），MIT，TypeScript；**2026-10-29 推送、Beta 活跃**，登 Trendshift「Repository Of The Day #3」。
- 出自 **CopilotKit**（AG-UI 协议发起方，企业级 agent 基础设施厂商），背后有商业公司与开发者生态背书，非个人玩具项目。
- **早期项目数据**：创建时间短、文档详尽但实战用户基数小；精确用户满意度/第三方深度评测**数据不可用**。采用前建议本地 `docker compose` 跑通再评估。
- 风险点：依赖 CopilotKit Intelligence（免费 Developer 计划可本地跑 Mac，30 天预览许可）；`OPENBOT_SINGLE_USER=true` 默认单管理员无登录，**任何生产部署必须先关掉并配置 OAuth/OIDC**。

## 竞品对比

| 维度 | OpenBot | CopilotKit 主框架 | LangGraph Platform / CrewAI | 终端 harness（claude-code） |
|------|---------|-------------------|------------------------------|------------------------------|
| 定位 | 自托管「AI 同事」平台+治理网关 | Agent UI/协议基础设施 | agent 编排框架/平台 | 命令行单 agent |
| 治理 | CEL 策略+审计+接管+密钥加密 | 组件/协议层，治理较弱 | 依赖自建 | 基本无 |
| 自托管 | 强（Docker Compose 全栈） | 中 | 中/强 | 强 |
| 多框架 | AG-UI 统一接入 | 原生 | 各自生态 | 原生 |
| 成熟度 | Beta（极早期） | 较成熟 | 成熟 | 成熟 |

## 核心研判

- **价值鲜明**：把「agent 能操作工具」升级为「操作前先判定、操作后全审计、危险时可接管、密钥不出转录」，是企业 agent 落地最缺的**治理层**；AG-UI 解耦与 CEL 策略是可复用亮点。
- **风险偏高**：Beta、生态极早期；强依赖 CopilotKit Intelligence 商业/本地运行时；安全模型高度依赖正确配置（漏配 `OPENBOT_SINGLE_USER` 即全员管理员）。
- **采用建议**：作为「企业 agent 治理网关」的参考架构重点学其 `gateway.ts`/`policy.ts` 设计；若真要生产，先本地跑通、严格按 README 关单用户模式并接 SSO，再等生态与许可条款进一步成熟。

## 关键文件路径速查

- `server/src/computer/gateway.ts` — 动作唯一通路（解析真实元素→策略→审计→执行）
- `server/src/computer/policy.ts` — CEL 策略引擎（deny 优先、缺策拒、坏规拒、dry-run）
- `server/src/computer/{client,computer-key,provider,sandbox}.ts` — computer 连接/密钥/提供方/沙箱
- `server/src/audit.ts` / `server/src/audit-retention.ts` — 审计事件与留存
- `supervisor/` — 每人数一台 computer 的创建与管理
- `agent-computer/` — Chromium + workspace + 浏览器档案
- `docs/architecture.md` · `docs/configuration.md` · `docs/coworkers.md` — 架构/配置/同事详解
- `examples/fintech/` — 租户包（coworkers/channels/skills 模板）
