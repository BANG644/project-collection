# trycompai/crm 深度调研

> 一句话：**agentic-first 开源 CRM——"耐久研究 agent 是产品本身，数据库只是它记笔记的地方"**，用「API 零智能 + 租约式工作队列 + deny-all 沙箱 + 证据账本」把"不臆测客户"写成架构约束而非团队纪律。

🔗 https://github.com/trycompai/crm ｜ 许可 MIT ｜ 语言 TypeScript（Bun）｜ ⭐ 6,016（2026-07-31 创建，两周破 6k）｜ 主页 https://trycrm.ai

## 一、项目亮点（差异化）

1. **范式反转**：多数 CRM = 数据库 + 表单（AI 版再在旁边挂个聊天框）；本仓库反过来——agent 自主决定"看什么、何时跟进、花多少研究预算"，关停浏览器它仍在后台跑。README 原话："The agent is not a feature of the CRM; the CRM is where the agent keeps its notes."
2. **API 故意无智能**：NestJS 只负责"报告发生了什么"（写一行队列），语义判断全交给 agent。文档 `docs/api.md` 记载了一次真实故障——某 Nest 服务直接调富化 API 被定为 bug。这避免了"两套身份匹配逻辑漂移，其中一个把地球上所有雇主都匹配上"的惨剧。
3. **证据账本（evidence ledger）**：核心规则"绝不臆测一个人"——任何工具不接受 confidence 分数（模型自评分会朝"看起来有用"的方向错），工具只报告"观察到什么"（`crm.signature-block`、`github.account-identity`），强证据写入记录，弱证据变成待人工确认的 suggestion。
4. **deny-all 沙箱**：agent 的 shell 既无网络也无 `DATABASE_URL`，只能当文本处理器。这是"客户邮件正文唯一能外泄的路径"被结构性堵死的设计，而非靠审查。
5. **零密钥可运行**：没有任何外部 API key 时仍工作——`read_crm_history` 读你自己线程/会议/签名块（免费且是最强证据）。每个 key 只"多开一个可查的地方"，session 启动时打印可用源清单。

## 二、核心架构

Turborepo monorepo（Bun 运行，部署 Vercel），三层 apps + 共享 packages：

| 路径 | 职责 |
| --- | --- |
| `apps/agent` | 研究 agent（工具/技能/调度/沙箱），基于 **eve**（Vercel 文件系统优先的耐久 agent 框架） |
| `apps/app` | Next.js App Router 前端（shadcn/ui + nuqs URL 状态）· :3000 |
| `apps/api` | NestJS API（HTTP/auth/tRPC/Google 同步）· :3001 |
| `packages/db` | Prisma schema + 迁移 + Postgres 客户端 |
| `packages/auth` | Better Auth（仅 Google + 单 allow-list 环境变量） |
| `packages/ui` | shadcn/ui 组件 + Tailwind 主题（**全仓唯一 UI 源**） |
| `packages/env` | 加载根 `.env` |

**技术栈**：Model = Vercel AI Gateway（无 provider SDK，OIDC 免 key）；Sandbox = Vercel Sandbox（生产）/ Docker·microsandbox（本地）；Data = Prisma + Postgres(Neon) + 可选 Redis(Upstash)；Files = Vercel Blob。

**三条写进代码而非 style guide 的规矩**（`docs/api.md` / `docs/design.md`）：
- 智能永不驻留 API；
- `packages/ui` 是 UI 唯一来源（调用点不得覆写样式）；
- **没有 organization 概念**——单租户故意为之，一个恒定值的 `organizationId` 只是"看起来像真实权限检查的列、索引和开销"。

## 三、源码深度解读（agent 子系统，最有借鉴价值）

### 1. `apps/agent` 的 18 工具 / 4 技能 / 1 调度
- **18 authored tools**：`read_crm_history`、`search_crm`、`identify_contact`、`research_person`、`enrich_company`、`record_fact`、`schedule_recheck`…
- **4 skills**（markdown 散文，随代码版本化）：`evidence.md`、`identity-matching.md`、`data-boundaries.md`、`writing-a-brief.md`——agent 读的"操作手册"。
- **1 schedule** `dispatch.ts`：本身"什么都不决定"，只 lease 到期行、每行起一个 session。

### 2. 租约式工作队列（`lib/tasks.ts`）
```
claimDue → 行级 FOR UPDATE SKIP LOCKED 抢租
```
两个 dispatcher 拿到不相交的工作；某次运行崩溃时，行在租约到期后自动释放。**任何"每 N 分钟最老 10 个联系人"都写进 task 的 `dueAt`，而非 cron 表达式**——调度即数据。agent 想再看某人就调 `schedule_recheck` 并说明原因，该原因展示给销售（"14 天后再来却说不出理由 = 没有理由，只是默认值"）。

### 3. deny-all 沙箱（`deny-all` egress）
- 沙箱有 `bash`/`grep`/`glob` + `/workspace`，但**无网络、无 `DATABASE_URL`**。
- `web_fetch` 跑在 app runtime，`web_search` 跑在模型 provider——沙箱本身既无凭据也无出口，天然不可 exfiltrate。`deny-all` egress 零成本。
- 前端每个 contact/company/deal 都有 **Agent 标签页**：实时步骤、被丢弃的线索及原因、两难时原地问答。会话经签名 token 携带（`AGENT_BRIDGE_SECRET` 双进程一致即开启）。

## 四、应用场景与启发

- **"agent 优先"后端设计范式**：把"智能"从请求-响应 API 抽离，改为"事件入队 → 耐久 agent 租约消费 → 写回"。任何需要长时自主运行的内部系统（尽调、竞品监控、销售情报）都可照搬 `lib/tasks.ts` 的 `FOR UPDATE SKIP LOCKED` 租约模式。
- **防幻觉的工程化**：用"证据账本 + 禁 confidence 分数 + 弱证据降级为 suggestion"替代"提示词里写'不要编造'"。可复用于任何让 LLM 写结构化事实的系统。
- **沙箱即安全边界**：不靠审批流，靠"shell 里既没有网络也没有 DB 凭据"让外泄在物理上不可能——比 DLP 规则更可靠。
- **零密钥可降级**：外部集成做成"可插拔可选源"，离线也能跑核心功能，避免 SaaS 绑定。

## 五、社区口碑

- 2026-07-31 上线，两周 ⭐ 6,016、fork 618，增长曲线陡峭，说明"agent 是产品而非功能"的叙事击中痛点。
- 由 Context（context.dev，"Powered by Context"）团队出品，backed by 已知做 AI 基础设施的团队，可信度较高。
- README 设计感强、ADR（`adrs/`）与 `docs/` 齐备，工程透明度好；Hacker News / X 讨论「single-tenant 是否够用」「eve 框架成熟度」是主要争议点（数据不可用精确引用，未见大规模负面）。

## 六、竞品对比 + 核心研判

| 维度 | trycompai/crm | Attio / HubSpot / 传统 CRM | ChatGPT 式"AI CRM" |
| --- | --- | --- | --- |
| AI 定位 | agent = 产品本体，后台自主跑 | AI = 侧边聊天框 | 聊天 = 唯一界面 |
| 智能位置 | 全在 agent，API 零智能 | 散布在多处逻辑 | 黑盒 |
| 防幻觉 | 证据账本 + 禁自评分 | 基本无 | 靠 prompt |
| 部署 | 自托管（Vercel） | SaaS | SaaS |
| 租户 | 单租户（刻意） | 多租户 | 多租户 |

**研判**：
- ✅ 适合"小团队/个人销售情报 + 想完全自控数据 + 接受单租户"的场景，是 현재 가장 彻底践行 agentic 架构的开源 CRM。
- ⚠️ 单租户 + Google-only 鉴权 + 全量可见的授权模型，决定它**不是**给"多客户 SaaS 化"用的；企业化需自己加租户层。
- ⚠️ 强依赖 **eve**（Vercel 耐久 agent 框架）与 Vercel AI Gateway，生态绑定较重；自托管非 Vercel 时需评估 eve 的可移植性。
- 结论：当作"agentic 后端架构参考实现"价值最高，直接当生产 CRM 替换 Salesforce 尚早（成熟度、多租户、合规都未到）。

## 七、关键文件路径速查

- `apps/agent/lib/tasks.ts` — 租约式工作队列（`claimDue` / `FOR UPDATE SKIP LOCKED`）
- `apps/agent/dispatch.ts` — 唯一调度（只 lease 不决策）
- `apps/agent/.agents/skills/ai-elements/` — agent 工具/技能/参考实现
- `docs/api.md` — "智能永不驻留 API" 的故障由来与规则
- `docs/agent.md` — agent 全量写真
- `docs/design.md` — `packages/ui` 唯一 UI 源约束
- `SECURITY.md` — 单租户/全量可见授权模型，接真实数据前必读
- `packages/db/` — Prisma schema（无 organization 表，佐证单租户）
- `turbo.json` / `package.json` — Bun + Turborepo 编排（Node ≥22，bun@1.3.12）
