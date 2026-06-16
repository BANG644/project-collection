# 🔬 rohitg00/agentmemory - 全方位深度调研

## 📌 一句话定位

**AgentMemory 是 AI 编码 Agent 的「海马体」** — 一套生产级持久记忆引擎，让 Claude Code、Cursor、Gemini CLI、Codex CLI、OpenClaw 等 15+ 主流 AI 编码工具**跨会话共享记忆**，自动记录架构决策、Bug 修复、技术选型，新会话无需重复解释。

> 不是 MEMORY.md 的升级版，不是 RAG 管道，而是**基于 iii 引擎的三层抽象记忆系统**。

---

## 🏗️ 项目架构全景

### 📊 核心指标

| 指标 | 值 |
|------|-----|
| 创建时间 | 2026-02-25（仅 4 个月） |
| ⭐ Stars | 23,053 |
| 🍴 Forks | 1,901 |
| 📝 语言 | TypeScript (ESM) |
| 📜 许可 | Apache-2.0 |
| 🔄 最后更新 | 2026-06-15（非常活跃） |
| 📦 包名 | `@agentmemory/agentmemory` |
| 📏 核心 LOC | ~21,800 |
| 📐 测试框架 | Vitest |

### 架构层级

```
┌─────────────────────────────────────────┐
│            上层：Agent 适配层              │
│  Claude Code / Cursor / Codex / OpenClaw  │
│  Gemini CLI / Hermes / Cline / Copilot   │
│  …… 共 15+ 种工具适配                     │
│         ├─ MCP 协议 (51 个工具)            │
│         ├─ Hook 系统 (12 个生命周期)        │
│         └─ REST API (124 个端点)           │
├─────────────────────────────────────────┤
│            中层：记忆管理引擎               │
│  │ 原始事件→去重→隐私过滤→存储→压缩→向量化  │
│  │ → BM25索引 + 向量索引 + 知识图谱        │
│  │ → 4层记忆巩固 + 留存策略                │
├─────────────────────────────────────────┤
│         底层：iii 引擎 (Rust 运行时)        │
│  │ 函数原语 / 状态管理 / 流式通信           │
│  │ 123 个预置函数 + WebSocket + OpenTelemetry│
└─────────────────────────────────────────┘
```

### 核心模块解读

#### src/index.ts — 工程化的模块注册中心

通过 `registerWorker()` 接入 iii-sdk，将 40+ 函数模块依次注册。每个模块都是一个独立 `registerXxxFunction(sdk, kv)` 调用。采用依赖注入模式——sdk 负责函数注册和调度，kv 负责数据库状态管理。

关键设计决策：**Builder 模式**的 TypeScript 实现，函数模块化注册而非全部塞在一个文件里。

#### src/types.ts — 类型系统设计的精妙之处

- **`RawObservation`** 到 **`CompressedObservation`** 的转换是系统核心数据流
- `Memory` 接口包含 6 种类型（pattern/preference/architecture/bug/workflow/fact），是最高层级的「可记忆」抽象
- `HookType` 枚举覆盖 16+ 个生命周期阶段，从 `session_start` 到 `session_end`，细粒度到 `subagent_start`/`subagent_stop`

#### src/functions/ 模块 — 功能分解

| 模块 | 行数 | 功能 |
|------|------|------|
| `remember.ts` | ~250 | 核心记忆写入，验证类型+TTL+重复检测 |
| `search.ts` | ~550 | 搜索索引管理，VectorIndex/SearchIndex/Persistence 三大组件 |
| `compress.ts` | ~220 | LLM 驱动的事件压缩，XML 解析 + 质量评分 + 自修正 |
| `lessons.ts` | ~200 | 教训重复检测 + 置信度强化机制 |
| `quality.ts` (eval) | ~50 | 确定性质量评分：压缩质量 / 摘要质量 / 上下文相关性 |
| `hybrid-search.ts` | ~250 | 三重检索融合引擎 |
| `crystallize.ts` | — | 原始事件→结构化知识 |
| `reflect.ts` | — | 事后回顾自省 |

#### 核心数据流：记忆生命周期

```
AI 工具调用触发 Hook
        ↓
RawObservation (原始事件)
        ↓  [去重: SHA-256, 5分钟窗口]
        ↓  [隐私过滤: API Key/Token/<private>]
  KV 存储 (保留完整上下文)
        ↓  [LLM 压缩]
  CompressedObservation (结构化: 事实+概念+叙事)
        ↓  [向量化: 6种 Embedding Provider]
  索引构建 (BM25 + 向量 + 知识图谱)
        ↓  [4层巩固]
  Memory (长期记忆: 类型/标题/内容/置信度/版本/关联)
```

### 检测引擎 (`eval/`)

| 模块 | 功能 |
|------|------|
| `quality.ts` | 确定性质量评分：压缩质量(100分制)、摘要质量、上下文相关性 |
| `schemas.ts` | Zod 模式定义：CompressOutputSchema 用于验证 LLM 输出 |
| `validator.ts` | LLM 输出校验器，解析 XML 并检查必填字段 |
| `self-correct.ts` | 失败自动修正管道：校验失败→重新提交 LLM→指数退避 |
| `metrics-store.ts` | 性能指标存储（召回率、准确率等） |

### 搜索系统：三重信号融合

BM25（关键词）: `search-index.ts`
- 自定义词干提取（支持多语言：希腊语、西里尔字母、阿拉伯语）
- 中文/日文/韩文可选分词器（jieba/tiny-segmenter）
- 精确匹配专业术语、文件名、错误码

向量搜索（语义）: `vector-index.ts`
- 支持 6 种 Embedding Provider（OpenAI/Gemini/Cohere/Voyage/CLIP/本地 all-MiniLM-L6-v2）
- 本地嵌入模型离线运行，+8% 召回率提升
- 完全本地可选，无需网络

知识图谱（推理）: `graph-retrieval.ts`
- BFS 遍历：发现实体之间的间接关联
- 查询展开（`query-expansion.ts`）：自动生成同义改写+时间维度具体化+实体抽取

**融合策略 (RRF)**:
- BM25 权重 0.4，向量 0.6，图谱 0.3（可调）
- RRF k=60 的 Reciprocal Rank Fusion
- 会话多样性过滤：同一会话最多返回 3 条结果
- **LongMemEval-S 基准 R@5 = 95.2%**

### CLI 核心 (`cli.ts`, 98KB)

- 自包含 CLI：安装引导 → 环境检测 → Agent 选择 → 配置生成
- 支持 15+ 工具的自动适配，自动检测工具是否已安装
- `doctor-diagnostics.ts`: 自动诊断环境问题并修复
- `remove-plan.ts`: 安全移除计划，包括文件清理、配置还原
- `onboarding.ts`: 首次运行引导，全交互式

### MCP Server (`mcp/`)

- `server.ts`: MCP 协议实现的主服务器
- `standalone.ts`: 轻量级独立模式（无需完整运行 iii 引擎）
- `tools-registry.ts`: 51 个 MCP 工具注册表
- `in-memory-kv.ts`: 内存 KV 存储（用于 MCP 上下文）
- `rest-proxy.ts`: REST→MCP 桥接层

### Hooks 系统 (`hooks/`)

16 个生命周期钩子，覆盖 AI 工具的完整会话周期：
- `session-start` / `session-end`：会话生命周期管理
- `pre-tool-use` / `post-tool-use` / `post-tool-failure`：工具调用级捕获
- `pre-compact`：压缩前的钩子，确保数据完整性
- `subagent-start` / `subagent-stop`：子代理级隔离（多 Agent 场景）
- `prompt-submit`：用户输入时的上下文注入

---

## 🧠 独家发现（READEME 之外的深度洞察）

### 发现 1：iii 引擎——命运的赌<EFBFBD>

AgentMemory 的核心依赖性选择 **iii 引擎**（iii.dev），一个 Rust 编写的事件驱动运行时。这是一个聪明但高风险的选择：
- ✅ **优势**：21,800 LOC 实现 123 个预置函数 + 存储 + 流式通信，代码极度精简
- ✅ **性能**：Rust 级性能，SQLite 持久化无需外挂数据库
- ⚠️ **风险**：项目绑定了 `"iii-sdk": "0.11.2"`（明确 pinned），iii 本身仍在快速迭代，版本锁定可能拖累升级

### 发现 2：四层记忆巩固——类人脑机制

项目受认知科学启发，设计了 4 层分级记忆：

| 层级 | 类比 | 存储内容 | 保留策略 |
|------|------|----------|----------|
| Working | 短期记忆 | 原始工具调用记录 | 会话级，自动清理 |
| Episodic | 情景记忆 | 会话摘要（"做了什么"） | 30 天衰减，高频访问强化 |
| Semantic | 语义记忆 | 核心事实与模式（"知道什么"） | 永久存储，矛盾检测自动合并 |
| Procedural | 程序性记忆 | 工作流与决策模式（"如何做"） | 项目级共享，团队协同优化 |

这是当前 AI 记忆方案中最完整的分层模型。

### 发现 3：自修正压缩管道

`compress.ts` + `self-correct.ts` 构成了一个有趣的管道：
1. LLM 压缩原始观察为 XML 格式
2. `validateOutput()` 校验 XML 结构和必填字段
3. `scoreCompression()` 确定性评分（0-100 分）
4. 失败时 `compressWithRetry()` 自动重试（指数退避）
5. 质量低于阈值时重新提交 LLM

这是一个 **「LLM+规则」的混合模式**，而非纯 LLM 依赖。

### 发现 4：中文/日文/韩文的全面支持

大多数同类项目只关注英文，但 AgentMemory 在以下方面做了 CJK 适配：
- `cjk-segmenter.ts`：CJK 分词器
- `@node-rs/jieba` 作为可选依赖
- 中文搜索的 BM25 词干提取支持
- 中文 UTF-8 处理的显式 Bug 修复（Issue #readBody corrupts multi-byte UTF-8）

### 发现 5：超过 120+ 的 API 端点

项目提供 51 个 MCP 工具 + 124 个 REST API 端点，覆盖：
- 记忆操作（read/write/search/delete/verify）
- 会话管理（start/stop/list/analyze）
- 系统管理（health/metrics/audit/export/import）
- 团队功能（share/team/control/access_log）
- 反馈与通知（lessons/signals/routines/sentinels）

这种 API 覆盖度使得 AgentMemory 几乎可以嵌入任何工具链。

---

## 🌐 全网口碑画像

### 好评共识

| 好评点 | 来源 | 关键数据/原话 |
|--------|------|---------------|
| **解决核心痛点** | SegmentFault 深度分析 | "每次会话都要重新解释架构"的根本矛盾被解决 |
| **检索精度惊人** | LongMemEval-S 基准 | R@5 = 95.2%（BM25-only 仅 86.2%） |
| **Token 成本大幅降低** | 官方基准 | 单会话 22,000+ tokens → 1,900 tokens，年成本 $500+ → $10 |
| **安装极简** | CSDN 实测 | "npx @agentmemory/agentmemory" 一条命令启动 |
| **多工具共享记忆** | 多名用户证实 | Claude Code 和 Cursor 共享同一记忆服务器 |
| **零手动维护** | CSDN 用户 | 不用写 MEMORY.md，不用更新 .cursorrules，后台自动工作 |
| **CJK 友好** | 中文社区 | 支持中文分词和搜索 |

### 差评共识 & 踩坑高发区

| 差评点 | 具体 | 严重程度 |
|--------|------|---------|
| **Embedding 检测问题** | Issue: v0.9.27 本地 embedding 未自动检测，smart-search 返回 0 语义命中 | 🔴 关键 Bug |
| **UTF-8 多字节编码 Bug** | Issue: readBody 对 >1 chunk 的多字节 UTF-8 乱码，影响中文/日文 | 🔴 关键 Bug |
| **搜索索引不同步** | Issue: import "replace" 清除 KV 但搜索索引未清理，造成幽灵结果 | 🟡 中等 |
| **MCP 连接问题** | Issue: OpenCode 无法连接到 agentmemory 的 MCP Server | 🟡 中等 |
| **小型项目效果有限** | CSDN 实测反馈：短小的脚本项目没什么效果 | 🟢 预期内 |
| **iii 引擎依赖风险** | 底层引擎在快速变化，版本锁定可能拖累升级 | 🟡 潜伏 |

### 维护者响应风格

项目由 Rohit Ghumare（rohitg00）主导。开源 4 个月已有 461 次提交，版本号从 v0.1.x 到 v0.9.27。社区贡献活跃：#415 PR（文档刷新）由 CodeRabbitAI 自动处理合并。版本发布密集（v0.9.23 → v0.9.27 仅 9 天），Bug 报告通常会在 48 小时内得到回应。

---

## ⚔️ 竞品对比

### 对比矩阵

| 维度 | AgentMemory | Mem0 | Letta | Claude Code MEMORY.md |
|------|------------|------|-------|---------------------|
| **定位** | 本地/私有记忆引擎 | 云端托管 API | 云端托管 | 静态文本文件 |
| **安装** | npx 一行命令 | 需注册/API Key | 需注册 | 零安装（配置文件） |
| **离线可用** | ✅ 完全离线 | ❌ 云端 | ❌ 云端 | ✅ |
| **多Agent协调** | ✅ 团队模式/共享 | ❌ 单 Agent | ❌ 单 Agent | ❌ |
| **检索类型** | BM25+向量+图谱(RRF) | 向量检索 | 向量检索 | grep 关键词 |
| **LongMemEval R@5** | 95.2% | ~80% | ~83% | < 50% |
| **Token 节省** | 92% / 会话 | 未公布 | 未公布 | 0% |
| **Hook 数量** | 16+ | 0（API only） | 几项 | 0（纯静态） |
| **工具适配** | 15+ 工具 | Claude only | 自定义 Agent | Claude Code only |
| **存储** | 本地 SQLite | 云端 | 云端 | 文件系统 |
| **成本** | 仅 LLM API 费用 | 按调用计费 | 按调用计费 | 无额外费用 |
| **社区 Stars** | 23K | ~5K | ~3K | N/A |
| **语言** | TypeScript | Python | Python | Markdown |

### 定位差异化

- **AgentMemory** ≈ 本地优先、跨工具、生产级：适合认真用 AI 编码的团队
- **Mem0** ≈ 云优先、单 Agent、试验级：适合快速实验
- **Letta** ≈ 托管服务、可定制 Agent：适合企业托管方案
- **CLAUDE.md** ≈ 零配置、极简：适合个人

---

## 🎯 核心研判

### 🟢 项目优势（不可替代的价值点）

1. **本地优先 + 零外部依赖** — 所有组件（嵌入模型、检索、存储）都在本地运行，无需 API Key 即可使用语义搜索，对隐私敏感团队极有价值
2. **跨工具记忆共享** — 15+ 工具的适配层是目前同类项目中最广的，**Claude Code↔Cursor↔Codex 共享同一记忆** 是独有卖点
3. **三层检索 RRF 融合** — BM25+向量+知识图谱的组合是目前开源方案中最完整的搜索架构，R@5=95.2% 有真实基准背书
4. **四层记忆巩固** — 类人脑机制的记忆分层在同类项目中独一无二
5. **Token 成本控制** — 92% 的 token 节省 + 年成本 $500→$10 有可验证数据

### 🔴 项目风险

1. **iii 引擎依赖风险** — 项目构建在一个快速迭代的外部引擎上。iii 本身的稳定性直接影响 AgentMemory。如果 iii 发生重大变更或消亡，整个项目需要重写底层
2. **GitHub 多字符 UTF-8 Bug 尚未完全修复** — 这对于中文/日文/韩文用户是严重问题
3. **快速迭代带来的稳定性问题** — 0.9.x 系列的每个小版本都在修复上一个版本的 Bug，说明质量门禁不够完善
4. **跨工具适配层的维护成本** — 15+ 工具每个都可能变更 API，维护成本持续增长
5. **概念验证到生产就绪的距离** — 0.9.x 意味着尚未 1.0，API 稳定性未承诺

### 适用场景 ✅

- 日常使用多个 AI 编码工具的开发者（Claude Code + Cursor 最典型）
- 团队协作需要共享 Agent 经验的小团队
- 大中型项目（6 个月以上，架构知识积累需求强烈）
- 隐私敏感的团队（完全本地，数据不出域）
- 注重开发效率和成本控制的工程团队

### 不适用场景 ❌

- 单次会话完成的脚本/工具类项目
- 使用小众/内部 AI 工具（没有适配层）
- 需要高度定制化记忆策略的场景

### 趋势判断 📈

**爆发增长期 — 高速上升。** 4 个月从 0 到 23K Stars，日增 400+，说明「AI Agent 记忆」是 2026 年的核心刚需。类比 RAG 在 2024 年的爆发。关键转型节点是 v1.0 发布，届时 API 稳定性承诺将决定企业级采用率。

**最大的外部威胁**：AI 编码工具厂商可能直接在工具层内建持久记忆能力。如果 Cursor 或 Claude Code 原生支持跨会话记忆，AgentMemory 会被边缘化。但短期内（6-12 个月），AgentMemory 在本地化和多工具协调上的优势仍然成立。

---

## 📂 关键文件路径速查

| 文件 | 用途 |
|------|------|
| `src/index.ts` | 主入口，40+ 函数模块注册 |
| `src/types.ts` | 核心类型定义（RawObservation/CompressedObservation/Memory/等） |
| `src/config.ts` | 配置系统（环境变量 + .env 文件 + 多 Provider 检测） |
| `src/cli.ts` | CLI 主流程（98KB，含安装引导 + Agent 适配 + 诊断） |
| `src/functions/remember.ts` | 核心记忆写入逻辑 |
| `src/functions/search.ts` | 搜索索引管理 |
| `src/functions/compress.ts` | LLM 压缩管道 |
| `src/functions/lessons.ts` | 教训系统（去重+强化） |
| `src/functions/consolidation-pipeline.ts` | 记忆巩固流水线 |
| `src/functions/graph-retrieval.ts` | 知识图谱检索（BFS） |
| `src/functions/hybrid-search.ts` | 三重检索融合引擎 |
| `src/functions/reflect.ts` | 事后回顾自省 |
| `src/functions/cascade.ts` | 级联删除/更新 |
| `src/state/hybrid-search.ts` | 混合搜索类（RRF 融合） |
| `src/state/vector-index.ts` | 向量索引（支持 6 种嵌入） |
| `src/state/search-index.ts` | BM25 关键词索引 |
| `src/state/kv.ts` | KV 存储实现 |
| `src/eval/quality.ts` | 质量评分（压缩/摘要/上下文） |
| `src/eval/self-correct.ts` | 自我修正（失败重试+退避） |
| `src/mcp/server.ts` | MCP 协议服务器实现 |
| `src/hooks/` | 16 个生命周期钩子 |
| `src/providers/embedding/` | 6 种嵌入 Provider 实现 |
| `package.json` | v0.9.27，iii-sdk 0.11.2 |

---

## 🔗 参考链接

- GitHub: https://github.com/rohitg00/agentmemory
- LongMemEval: 官方基准测试，R@5=95.2%
- iii Engine: https://iii.dev
