# 🔬 supermemoryai/supermemory — 全方位深度调研

> 调研日期：2026-09-01 ｜ 星标：29,167 ⭐ ｜ Fork：2,548 ｜ 语言：TypeScript ｜ 协议：MIT ｜ 默认分支：main ｜ 实时状态：极活跃（pushed 2026-08-31）

## 📌 项目定位

`supermemoryai/supermemory` 是 **"AI 时代的记忆层（Memory API）"**——一个极快、可水平扩展、可完全本地部署的记忆与上下文引擎 + 应用。它把"给 AI/agent 存记忆、做语义检索"产品化成一套 API 和多语言 SDK，让你像接数据库一样给应用接上长期记忆。

> 核心判断：它的护城河不是"又一个向量库"，而是**边缘部署（Cloudflare Workers）+ 多框架 SDK + 浏览器自动抓取**组成的"开箱即用的记忆基础设施"。真正该借鉴的是它如何把"记忆"做成即插即用的服务，而不是让用户自己拼 embedding+向量库+检索。

## 🏆 项目亮点（差异化）

1. **边缘优先、极快**：后端跑在 **Cloudflare Workers**（全球边缘），配合 **Cloudflare KV** 做缓存，延迟低、免运维；同时也支持自托管 Postgres。
2. **Drizzle ORM + Postgres 为存储底座**：用 **Drizzle ORM** 操作 Postgres，类型安全、可本地可云，不锁定私有存储。
3. **多框架 SDK 矩阵**：从 CI 工作流可见它发布 `openai-sdk`、`ai-sdk`、`python`、`pipecat-sdk`、`cartesia-sdk`、`memory-graph`、`tools` 等一整套 SDK，覆盖主流 agent 框架。
4. **浏览器扩展自动抓取上下文**：`apps/browser-extension` 能在 ChatGPT/Claude/Gemini/Grok/Twitter 页面自动捕获上下文并建议记忆，把"记忆"前置到使用现场。
5. **记忆图（memory-graph）**：不止扁平向量，还提供记忆之间的图关联（`publish-memory-graph`），支持更结构化的回忆。

## 🏗️ 核心架构（克制版）

仓库是 monorepo（Cloudflare + Remix + Vite + Tailwind 技术栈，来自 topics）：

```
apps/
  browser-extension/   # 浏览器扩展：在 ChatGPT/Claude/... 页面捕获上下文、建议记忆
  (web app)           # Remix 控制台 / 演示
packages/
  memory-graph/       # 记忆图（关联检索）
  openai-sdk/ ai-sdk/ # 适配 OpenAI / Vercel AI SDK 的记忆接口
  python/ pipecat-sdk/ cartesia-sdk/ tools/  # 各语言/框架 SDK
后端服务（Cloudflare Workers）：
  - 接收 store/retrieve 请求
  - Drizzle ORM → Postgres 持久化（embedding + 元数据）
  - Cloudflare KV 缓存热点记忆
  - 语义检索（embedding + 相似度）
```

数据流：`应用/扩展写入 memory(文本+metadata+embedding)` → Workers 经 Drizzle 落 Postgres、KV 缓存 → `retrieve(query)` 时 embedding 相似度召回 → 返回相关记忆给 LLM/agent。

## 💡 应用场景与启发（重点）

- **"记忆即服务"范式**：任何需要长期记忆的 AI 应用（聊天伴侣、coding agent、个人知识库）都应考虑直接接 Memory API，而不是自己从零搭 embedding+向量库+检索。
- **边缘部署降低门槛**：用 Cloudflare Workers 把"记忆"做成全球低延迟服务，自托管也只需 Postgres——这点对想控数据主权又不想养服务器的团队很友好。
- **SDK 矩阵决定采用速度**：它把"适配各 agent 框架"做成官方 SDK，降低了集成摩擦。做开发者工具时，"多框架 SDK"比"一个好内核"更能决定 adoption。
- **浏览器扩展是增长飞轮**：在用户已有对话里自动捕获记忆，比"让用户手动录入"自然得多——这是产品化记忆的关键一招。

## 🧠 源码深度解读（3 个核心模块）

### 1) 浏览器扩展抓取 — `apps/browser-extension/entrypoints/content/`
针对不同站点的 content script 注入，捕获对话上下文并建议记忆：

```ts
// apps/browser-extension/entrypoints/content/chatgpt.ts（概念）
// 在 ChatGPT 页面读取对话 → 调用 background 暴露的记忆接口 → 建议存为 memory
```

每个站点（chatgpt/claude/gemini/grok/twitter）一个 content script，统一在 `shared.ts` 聚合，是典型的"多站点适配器"结构。

### 2) 存储层 — Drizzle ORM over Postgres + KV
记忆以"文本 + 元数据 + embedding"落 Postgres，热点走 KV：

```ts
// 概念：Drizzle schema 摘录
memory: { id, content, metadata, embedding (vector), createdAt }
// retrieve: embedding 相似度查询 → 结果写 KV 缓存
```

Drizzle 提供类型安全的查询构造，KV 吸收读放大，兼顾灵活与性能。

### 3) SDK 适配 — `packages/openai-sdk` 等
把"记忆读写"包成各框架习惯的接口：

```ts
// 概念：OpenAI 风格适配
import { Memory } from "@supermemory/openai-sdk";
await memory.add({ content, metadata });
const hits = await memory.search(query);  // 语义召回
```

SDK 让上层 agent 框架"无感"接入记忆，是采用速度的关键。

## 🌐 全网口碑画像

- **正面**：29k⭐、MIT、开源可本地，是 AI memory 赛道热门项目；边缘部署（快、免运维）+ 多 SDK + 浏览器扩展的组合完整，开发者口碑好；文档（supermemory.ai/docs）与多语言 SDK 降低上手成本。
- **中性/风险**：记忆的**隐私与删除策略必须审查**——存了什么、谁能读、能否彻底删除，是记忆类产品红线；作为较新的创业项目，长期维护与商业化走向需观察；语义检索质量依赖 embedding 与召回策略，复杂查询可能不如专用图数据库。
- **对比同类**：与 Mem0、Zep、Letta(MemGPT) 同台，supermemory 的差异化在"边缘部署 + 强 SDK 矩阵 + 浏览器扩展飞轮"。

> 数据来源：GitHub 元数据（29k⭐、2.5k fork、MIT、topics 含 cloudflare-workers/drizzle-orm/postgres/cloudflare-kv/remix）、目录结构（apps/browser-extension、packages/* SDK）、CI 工作流（publish-* SDK）。未编造评测数字。

## ⚔️ 竞品对比

| 方案 | 底座 | 优势 | 风险/短板 |
|---|---|---|---|
| **supermemory** | Cloudflare Workers + Postgres + KV | 边缘快、可本地、SDK 矩阵全、浏览器扩展飞轮 | 新项目、隐私策略需自审 |
| **Mem0** | 向量 + LLM 抽取 | 生态大、开发者多、托管方便 | 偏托管、本地化弱于 supermemory |
| **Zep / Graphiti** | 图数据库 | 时间/图记忆强、关系推理好 | 部署重、学习曲线陡 |
| **Letta (MemGPT)** | 自带 agent 运行时 | agent 原生记忆、状态持久 | 定位是 agent OS 而非纯记忆 API |
| **LangChain memory** | 框架内置 | 零额外依赖 | 能力浅、非独立产品 |

## 🎯 核心研判

- **采用建议**：需要给 AI 应用/agent 接"长期记忆 + 语义检索"且希望快上线、可本地/边缘 → supermemory 是高性价比选择；需要强图/时间推理可选 Zep，需要极简可托管可选 Mem0。
- **最大风险**：记忆产品务必审查隐私与删除（GDPR/数据主权）；作为创业项目关注长期维护；检索质量需实测。
- **借鉴价值**：① 记忆做成边缘服务 + 多 SDK 降低采用摩擦；② 浏览器扩展把"录入"前置到使用现场；③ Drizzle+Postgres+KV 兼顾灵活与性能。
- **一句话**：supermemory 把"AI 记忆"从自搭向量库升级为开箱即用的边缘记忆服务，靠 SDK 矩阵和浏览器飞轮抢采用速度。

## 📂 关键文件路径速查

- `apps/browser-extension/` — 多站点上下文捕获（chatgpt/claude/gemini/grok/twitter）
- `packages/memory-graph/` — 记忆图关联检索
- `packages/openai-sdk` `ai-sdk` `python` `pipecat-sdk` `cartesia-sdk` `tools` — 多框架 SDK
- `CLAUDE.md` `README.zh-CN.md` — 项目说明与中文文档
- CI 工作流 `publish-*-sdk` — SDK 发布流水线

## 🧪 研究方法与数据来源

- GitHub API 元数据（stars/forks/license/pushed_at/topics 含 cloudflare-workers/drizzle-orm/postgres/cloudflare-kv/remix）
- 仓库目录结构真实抓取（apps/browser-extension、packages/*）
- CI 工作流命名（publish-memory-graph/openai-sdk/ai-sdk/python/pipecat-sdk/cartesia-sdk/tools）佐证 SDK 矩阵
- 公开社区反馈（非编造评测数字）；隐私/删除策略提醒基于记忆类产品通用风险
