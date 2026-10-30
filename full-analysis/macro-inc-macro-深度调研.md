# macro-inc/macro 深度调研

> 调研日期：2026-10-31 ｜ 数据来源：GitHub API（README / `AGENTS.md` / `.agents/` 规则树）
> 许可证：**AGPL-3.0** ｜ 形态：Rust 后端 + SolidJS 前端的「一体化团队工作空间」（含 Agents + 共享团队记忆）

## 项目亮点（差异化）

- **单一系统替代 Slack+Linear+Notion+HubSpot+Superhuman**：邮件/消息/文档/任务/Agents/CRM/通话/文件/PR 全部打通，跨引用（doc↔task、channel↔email）**原生存为双向图（bidirectional graph）**，而非靠 Zapier/MCP 胶带拼接。
- **共享团队级 AI 记忆**：Agents 块带「统一团队记忆」，能代表你行动；通话被录音转写并写入团队记忆供 Agent 检索——把「公司知识」变成 Agent 可达的计算对象。
- **@-linked 可计算工作区**：一切 @链接、可搜索，团队和 Agent「再也不用切换工具」；设计哲学是「公司本应是可计算的（computable），而不是靠 MCP+Zapier 勉强粘起来」。
- **模块化「积木（blocks）」**：每个面（邮件/文档/任务…）各自为战但共享同一后端；AGENTS.md 明确「每块研究最佳实践再做得更好」。
- **极重 Agent 工程化**：`.agents/` 下 rules/skills/agents 三层齐全，且 `.claude`/`.cursor`/`.pi` 仅做**符号链接**到 `.agents/`，单一真相源。

## 项目定位（一句话）

Macro 是一个**把团队所有工作软件重做成「单一可计算系统」的一体化工作空间**——用共享后端 + 双向图 + 团队级 AI 记忆，让邮件/消息/文档/任务/CRM/Agent 彼此原生关联，而非靠集成胶水拼接。

> **5.8k⭐**（2026-10-30 当日 Trending 上榜），AGPL-3.0，Rust + SolidJS，2025-11 创建、**2026-10-30 当天活跃**，538 fork / 291 open issues。

## 核心架构

- **仓库分层**：`apps/web/`（前端，自带 agent 指南：Bun/UI 模式/浏览器校验）、`apps/`、`packages/`（共享前端包）、`services/`（可部署服务与 worker，Rust crate 名取自各 `Cargo.toml`）、`crates/`（可复用后端库/领域服务/适配器）、`infra/`（部署定义）、`tooling/`（开发工具与 `just` 配方）、`docs/`（架构/设计/runbook）。
- **`.agents/` 单一真相源**：`rules/`（路径作用域约定，触碰匹配文件即加载）、`skills/`（任务工作流，如 `add-sdk-endpoint`/`audit`/`cloud-storage-hexagonal-architecture`）、`agents/`（子 Agent：`auditor`、`browser-verifier`）、`templates/`。`AGENTS.md` 明确「真实文件在 `.agents/`，工具目录只 symlink」。
- **`AGENTS.md` ↔ `CLAUDE.md` 符号链接**：编辑 `CLAUDE.md` 即改 `AGENTS.md`，杜绝双份。
- **数据层**：`crates/macro_db_client/migrations/` 是 MacroDB（PostgreSQL）迁移；协作 markdown 走 CRDT（`collab-surface-core` skill）。

## 源码深度解读（核心模块：Agent 引导与仓库地图）

**1. 仓库即「给 Agent 的操作系统」（`AGENTS.md`）**

```markdown
# Repository guide for coding agents
1. Read CODING.md.
2. Find the affected app/service/crate in the map below and read its AGENTS.md.
3. Read task-relevant guides, not every linked doc.
4. Explore the code you will change and its callers until you know how it works.
```
`AGENTS.md` 把「先读 CODING.md → 按地图找子树 AGENTS.md → 读相关 guide → 读懂调用链」固化为强制四步；`.agents/rules/` 做成**路径作用域**加载（碰 `rust/` 加载 rust 架构/代码/DB/guardrails 规则，碰 `web/` 加载 solid/设计系统/i18n 规则），避免巨型 prompt。这套「分层 agent 文档 + 路径作用域规则」是大型 Rust+前端 monorepo 的可复制范式。

**2. 单一真相源防漂移（symlink 策略）**

`AGENTS.md` 显式声明「Real files live in `.agents/`；tool-specific directories only symlink to it」——Cursor/Claude/π 的 `rules|skills|agents` 各自 symlink 回 `.agents/`。这意味着加一条规则只需改一处，所有 Agent 宿主自动一致，杜绝「Claude 版和 Cursor 版规则分叉」的常见坑。

## 应用场景与启发

- **小团队/初创的「操作系统」**：想用一套工具替代 Slack+Linear+Notion+HubSpot 的团队，Macro 提供统一后端 + 双向图 + 团队记忆，agent 可直接跨邮件/任务/CRM 行动。
- **「工作空间要可计算」的方法论**：把跨引用存成双向图、把通话/文档喂给团队记忆，是「让 Agent 真正理解公司上下文」的工程化样本。
- **大型 monorepo 的 Agent 文档范式**：`.agents/` 单一真相源 + 路径作用域规则 + symlink 到各宿主，强烈推荐任何多 Agent 协作的仓库照搬。
- **AGENTS.md 四步前置读**：任何「让 Agent 改代码前先读懂架构」的项目都应借鉴。

## 社区口碑

- **概念受认可但尚早期**：**5.8k⭐**、AGPL-3.0，由 ~15 人团队 dogfood 两年、NYC/Toronto 设计，Trending 上榜说明「一体化可计算工作空间」叙事有市场；Rust+SolidJS、键盘优先、Linear 风任务。
- **主要顾虑**：AGPL-3.0 商用传染；291 open issues 较多（早期项目常态）；自托管/云部署成熟度、与既有 Slack/Linear 数据迁移成本未知；「统一后端」在极端规模下的性能待验证。
- **主观满意度数据不可用**：精确 NPS 无第三方统计；上述基于 README 自述与 Trending 表现。

## 竞品对比

| 维度 | Macro | Slack+Linear+Notion（拼装） | Notion AI Workspace | Height / 类 Linear 全家桶 |
|------|-------|------------------------------|----------------------|---------------------------|
| 统一后端 | 是（单向数据模型） | 否（各自有库） | 部分 | 部分 |
| 跨引用 | 原生双向图 | 靠 Zapier/MCP | 有限 | 有限 |
| 团队 AI 记忆 | 内建（通话/文档入记忆） | 需外接 | 有（笔记级） | 有（任务级） |
| 许可 | AGPL-3.0 | 各 SaaS | 各 SaaS | 各 SaaS |

## 核心研判

- **价值清晰**：「把公司重做成可计算系统」的定位切中多工具割裂痛点，双向图 + 团队记忆 + 原生 Agent 行动是差异化；其 Agent 文档范式（`.agents/` 单一真相源）本身是高质量工程样本，值得单独借鉴。
- **边界明确**：**仍是早期产品**（open issues 多、规模待验证），AGPL 对闭源不友好；迁移既有工具链有成本。
- **采用建议**：小团队想统一协作栈时可评估；即便不采用 Macro，其 `.agents/` symlink + 路径作用域规则也该抄进自己的仓库；闭源产品注意 AGPL。

## 关键文件路径速查

- `AGENTS.md` · `CLAUDE.md`（symlink）→ 仓库地图与「改码前四步」
- `CODING.md` — 各语言编码规则（先读）
- `.agents/rules/` — 路径作用域约定（`rust/`、`web/`、`infra/`、`sdk.md`…）
- `.agents/skills/` — 任务工作流（`add-sdk-endpoint`/`audit`/`cloud-storage-hexagonal-architecture`）
- `.agents/agents/` — 子 Agent（`auditor`/`browser-verifier`）
- `apps/web/` · `services/` · `crates/` · `packages/` · `infra/` — 前端/服务/库/包/部署分层
- `crates/macro_db_client/migrations/` — MacroDB（PostgreSQL）迁移
