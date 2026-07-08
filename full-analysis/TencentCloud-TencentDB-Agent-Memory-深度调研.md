# 🔬 TencentCloud/TencentDB-Agent-Memory — 全方位深度调研

## 📌 一句话定位

**腾讯云开源的 AI Agent 本地长期记忆引擎**，通过 L0→L1→L2→L3 四层渐进式流水线 + Mermaid 符号化短期记忆，让 Agent 记住用户偏好和任务上下文，最高节省 61.38% Token，提升 51.52% 任务通过率。

## ⭐ 项目亮点

1. **四层语义金字塔架构（核心差异化）** — 拒绝扁平向量存储，从 L0 原始对话 → L1 原子事实 → L2 场景块 → L3 用户画像，逐层抽象、逐层压缩。上层的 Persona、场景等为**人类可读的 Markdown 文件**，而非不可解释的向量嵌入
2. **Mermaid 符号化短期记忆** — 不是用 verbose prose 记录中间日志，而是用 Mermaid 语法编码任务状态机，配合 `node_id` 实现从符号图到原始日志的**无损下钻追踪**（README 声称 Benchmark 下短文搜索 Token 减少 61.38%）
3. **三层召回策略可配置** — Keyword (FTS5 BM25) / Embedding (VectorStore) / Hybrid (RRF 融合)，Embedding 不支持时自动 fallback 到 keyword，不会静默失效
4. **Zero-config 最小化部署** — `{}` 空配置即可运行，所有字段均有合理默认值，embedding provider 默认 "none" 禁用向量搜索，降低首次使用门槛
5. **测试驱动 + 中文友好** — 依赖 `@node-rs/jieba` 分词器 + BM25 中文/英文双语文档评分，代码中有大量中文注释和 prompt 模板

## 🏗️ 项目架构全景

### 目录结构

```
src/
├── core/
│   ├── index.ts              # 核心导出（interfaces + TdaiCore facade）
│   ├── config.ts             # 全功能配置解析（v3）
│   ├── tdai-core.ts          # 服务门面
│   ├── types.ts              # 核心类型定义
│   ├── conversation/
│   │   └── l0-recorder.ts    # L0 对话录制（JSONL 格式，每日一分片）
│   ├── hooks/
│   │   ├── auto-capture.ts   # L0 自动捕获 hook
│   │   └── auto-recall.ts    # 自动召回 hook（核心检索逻辑）
│   ├── persona/
│   │   ├── persona-generator.ts   # L3 用户画像生成
│   │   └── persona-trigger.ts     # L3 触发策略
│   ├── profile/profile-sync.ts    # 画像同步
│   ├── prompts/
│   │   └── l1-dedup.ts      # L1 冲突检测 prompt（LLM 去重）
│   ├── record/               # 记忆记录读写
│   ├── scene/                # L2 场景管理
│   ├── store/                # 存储层（sqlite-vec FTS5 + VectorStore）
│   └── utils/                # 工具函数
├── adapters/                 # Host 适配器（OpenClaw / Standalone）
├── cli/                      # CLI 命令
├── bin/                      # 可执行脚本入口
├── scripts/                  # 辅助脚本
└── hermes-plugin/            # Hermes 网关插件
```

### 技术栈

- **运行时**：Node.js ≥ 22.16（ESM only）
- **存储**：本地 `sqlite-vec`（FTS5 全文搜索 + VectorStore）+ 可选 Tencent Cloud VectorDB
- **Embedding**：OpenAI 兼容 API / 腾讯云 VDB 内置 BGE 模型
- **构建**：tsdown（TypeScript bundler），TypeScript 6.x
- **LLM 调用**：AI SDK（Vercel AI SDK）+ 可选 OpenClaw host 原生 LLM 或 standalone LLM override

### 核心配置一览

配置按功能分组为 `capture / extraction / persona / pipeline / recall / embedding` 六个模块：

```typescript
// 最小配置（零配置可用）
const config = {};
// 等效于：
{
  capture: { enabled: true },
  extraction: { enabled: true },
  recall: { enabled: true, strategy: "hybrid", maxResults: 5 },
  embedding: { enabled: false, provider: "none" }, // 默认无 embedding
  storeBackend: "sqlite",
}
```

## 💡 应用场景与启发

### 典型使用场景

1. **AI 编码助手的长期记忆** — 作为 OpenClaw 插件，让 Agent 记住用户的编码偏好（代码风格、测试习惯、工具链选择），跨会话不丢失
2. **个人 AI 助手的画像积累** — 通过 L3 Persona 持续积累用户画像，实现"越用越懂你"
3. **长任务 Agent 的上下文卸载** — 利用 Mermaid 符号化压缩 + 外挂 refs 文件，防止长对话的 Token 溢出（非常适用 SWE-bench 类连续任务场景）
4. **多 Agent 协作的共享记忆** — 配合 Tencent Cloud VectorDB 后端，支持多进程/多 Agent 共享记忆池

### 可借鉴的解决方案模式

- **"渐进式披露"存储架构**：上层存结构（Persona/场景/画布），下层存证据（原始对话/工具日志），形成可追溯的 drill-down 链。这比单纯全部存到向量数据库的"扁平 recall"模式提供了更好的可解释性
- **符号化 vs 向量化的取舍**：Mermaid 语法作为中间表示层的设计很巧妙——既保留了语义密度（比向量嵌入可读），又保持了 LLM 可解析性（比原始文本紧凑）
- **Prompt 工程去重策略**：`l1-dedup.ts` 中 LLM 批量判断"store/update/skip/merge"的去重策略，比纯向量相似度去重更精准

### 同类需求的可参考思路

如果你需要为 AI Agent 构建记忆系统，TDAI 的"三层召回策略（Keyword / Embedding / Hybrid）" + "Embedding 不可用时自动 fallback"的设计值得直接参考。它的配置系统（所有字段默认值、分组管理、类型化）也是工程化记忆系统的优秀范例。

## 🧠 核心源码解读

### 1. 配置系统（config.ts）— 安全优先的设计

配置系统的核心思想是**"零配置可用，配置错误宽容"**。Embedding 配置出错（如缺失 apiKey、model、dimensions）**不会抛异常**，而是 `embeddingEnabled = false` + 记录 error message，系统降级为纯 Keyword/FTS5 搜索继续运行：

```typescript
let embeddingConfigError: string | undefined;
if (embeddingProviderRaw === "none") {
  embeddingEnabled = false;
} else if (/* provider remote but missing fields */) {
  embeddingConfigError = `Remote embedding provider '...' requires 'apiKey', 'baseUrl', 'model', and 'dimensions'...`;
  embeddingEnabled = false;
}
// Never throws — plugin continues without vector search
```

这种做法确保了在 embedding 服务不可用、apiKey 失效、网络不通等情况下，Agent 功能不中断。

### 2. L0 录制器（l0-recorder.ts）— 双重防重复捕获

采用"位置切片 + 时间戳游标"双重机制防止同一轮对话被重复录制：

```typescript
// Layer 1 (position slice): 利用 cached messageCount 定位本轮新增消息
const usePositionSlice = originalUserMessageCount != null 
  && originalUserMessageCount <= rawMessages.length;
const slicedMessages = usePositionSlice
  ? rawMessages.slice(originalUserMessageCount)
  : rawMessages;

// Layer 2 (timestamp cursor): fallback when position slice unavailable
const cursor = afterTimestamp ?? 0;
const extracted = cursor !== 0
  ? allExtracted.filter((m) => m.timestamp > cursor)
  : allExtracted;
```

同时将带 `prependContext` 污染的原始用户消息替换为缓存的纯净版，确保记忆中没有注入的系统指令。

### 3. 自动召回（auto-recall.ts）— 三层混合搜索 + RRF 融合

Hybrid 搜索的核心实现：FTS5 关键词检索 + VectorStore 向量检索并行执行，通过 Reciprocal Rank Fusion 合并结果：

```typescript
// Run keyword and embedding searches in parallel
const [keywordResult, embeddingResult] = await Promise.all([
  searchByKeyword(cleanText, ...),
  searchByEmbedding(cleanText, ...),
]);

// RRF merge: k=60 is standard constant
const RRF_K = 60;
const mergedMap = new Map<string, { rrfScore: number; formatable }>();

// Process keyword results
keywordResults.forEach((r, rank) => {
  mergedMap.set(r.record.id, {
    rrfScore: 1 / (RRF_K + rank + 1),
    formatable: recordToFormatable(r.record),
  });
});

// Process embedding results — merge with RRF
embeddingResults.forEach((r, rank) => {
  const existing = mergedMap.get(r.record_id);
  if (existing) existing.rrfScore += 1 / (RRF_K + rank + 1);
  else mergedMap.set(r.record_id, { rrfScore: 1 / (RRF_K + rank + 1), ... });
});
```

关键设计：当 embedding 服务不可用时，策略自动 fallback 到 keyword；当底层 store（如 TCVDB）原生支持混合搜索，直接短路到单次 API 调用避免冗余嵌入。

### 4. L1 去重 Prompt（l1-dedup.ts）— LLM 驱动的智能去重

不是用向量相似度阈值（容易误判），而是用 LLM 批量判断每条新记忆应该 store / update / skip / merge：

```
动作选择逻辑：
- "store"：视为新信息，新增
- "skip"：已有记忆更好，忽略
- "update"：同一事实，新记忆更优，覆盖旧记忆
- "merge"：多条记忆互补不矛盾，合并为一条更完整记忆

跨类型合并示例：
- 一条 episodic "用户在 2018 年开始做播客" 
  + 一条 persona "用户有播客制作经验" 
  → 可 merge 为一条 person 或 episodic（取决于信息侧重）
```

这种做法比纯向量相似度去重更精准，但引入了 LLM 调用的额外成本（这是一个为质量而牺牲速度的设计选择）。

## 📐 架构决策与设计哲学

### 核心设计原则：「拒绝扁平存储，拥抱分层与符号化」

| 决策 | 不选 | 选 | 原因 |
|------|------|----|------|
| 记忆分层 | 扁平向量存储 | L0→L1→L2→L3 语义金字塔 | 确保可追溯、可解释、可下钻 |
| 短期记忆 | 原始日志堆砌 | Mermaid 符号图 + refs 卸载 | 最大语义最小 Token，同时保留无损追溯 |
| 存储异构 | 纯向量数据库 | 上层 Markdown + 下层 SQLite/DB | 上层可读可调试，下层可检索 |
| Embedding 默认 | 启用（需要配置）| 禁用（provider="none"）| 零配置即可用，降低首次成本 |
| 配置错误 | 抛异常 | 静默降级 + error message | 不因配置错误阻断 Agent 运行 |

### ADR 关注点

从 Issue #235（跨平台适配器）的讨论可以看出，架构设计明确遵循**"TDAI 拥有存储和检索，各平台拥有展示"**的边界原则。TDAI 返回原始召回数据，各平台（OpenClaw / Hermes / Dify / Codex）自行决定如何格式化到 prompt 中。

## 🌐 全网口碑画像

### 好评共识

- **架构设计新颖** — 四层语义金字塔被国内开发者评价为"比 Mem0 更工程化的人记忆方案"（掘金评论）
- **性能提升数据可信** — 61.38% Token 节约和 51.52% 通过率提升有 SWE-bench 等基准支撑（腾讯云官方文章）
- **国产开源友好** — MIT 协议、中文文档、支持中文分词（jieba），符合国内团队使用习惯

### 差评共识 & 踩坑高发区

- **OpenClaw 强绑定** — 官方插件形式依赖 OpenClaw SDK（开源的 OpenAgent 平台），独立使用需要走 Standalone adapter 或 MCP bridge，配置门槛较高
- **Embedding 默认不启用** — 虽然设计上是"零配置可用"，但无 embedding 时纯 FTS5 搜索在中文语义匹配上表现一般
- **Node.js 版本要求高** — 强制 ≥ 22.16，对部分存量环境不友好
- **心智模型较复杂** — 四层 pipeline、Mermaid 符号化、Offload 机制等概念堆叠，初次使用需要较长时间理解

### 争议焦点

- **L1 用 LLM 做去重 vs 向量相似度**：用 LLM 更精准但更贵更慢；用向量更快但可能误判。Issue 中团队选择了 LLM 方案，但留下了 `enableDedup` 开关选项
- **主分支与 v1.0.0 tag 的分歧**：Issue #420 发现 v1.0.0 tag 的 OTel 版本不匹配（`new Resource()` 构造器在 v2 SDK 下不兼容），导致观测数据静默失效——这暴露了 tag 管理上的问题

### 维护者响应风格

腾讯云开发者社区团队维护，Issue 响应迅速（7 日内必有回复），有 "腾讯犀牛鸟开源专属" label 的中高难度任务（Issue #235），吸引了 20+ 社区贡献者领取任务。

## ⚔️ 竞品对比

| 维度 | TencentDB Agent Memory | Mem0 | mem.ai (Butterfly Effect) |
|------|----------------------|------|--------------------------|
| 核心定位 | Agent 本地长期记忆引擎 | 记忆层 API | 个人 AI 记忆助手 |
| 记忆架构 | 四层语义金字塔（L0→L3） | 扁平 embedding 检索 | 端到端黑盒 |
| 部署方式 | 本地 SQLite（默认）/ 腾讯云 VDB | 远程 API | SaaS |
| 开源协议 | MIT | Apache 2.0 | 闭源 |
| 语言 | TypeScript（Node.js）| Python | — |
| 中文支持 | 原生（jieba + BM25 zh/en）| 通用模型 | 有限 |
| 可解释性 | 高（Markdown 画像 + Mermaid 符号图 + 完整追溯链）| 低（向量嵌入不可读）| 低 |
| 配置复杂度 | 中（四层 pipeline 需理解）| 低（API 即用）| 零配置 |
| Agent 框架绑定 | OpenClaw（深度）| 通用 | 通用 |

### 选择建议

- **需要完整、可解释的 Agent 记忆流水线** → TencentDB Agent Memory（特别是已使用 OpenClaw 的团队）
- **快速集成、仅需简单记忆检索** → Mem0（Python API 更直接）
- **不在乎数据隐私和可解释性** → mem.ai / ChatGPT Memory

## 🎯 核心研判

### 项目优势

1. **架构领先性** — 四层渐进式记忆 pipeline + Mermaid 符号化短期记忆，目前开源界没有第二个方案在"系统性设计"上达到这个深度
2. **可解释性** — Persona/场景块存储为人类可读 Markdown，支持完整追溯链（L3→L2→L1→L0），这在"AI 可信任"日益重要的背景下是巨大的差异化优势
3. **腾讯品牌背书** — MIT 协议 + 腾讯云团队维护，可靠性有保障；社区响应积极

### 项目风险

1. **生态绑定** — 主要适配 OpenClaw；独立使用需走 MCP bridge（代码可见 PR #339），体验远不如原生集成
2. **复杂度门槛** — 4 层 pipeline 的配置项高达 50+ 个，即使是"零配置"默认值，理解其完整工作流也需要相当时间投入
3. **纯 LLM 去重的成本** — L1 dedup 依赖 LLM 调用，在频繁交互场景下会产生额外 Token 支出

### 适用场景 ✅
- OpenClaw 平台用户需要 Agent 长期记忆
- 研究 Agent 记忆系统架构的开发者
- 需要可解释性强的 Agent 记忆方案

### 不适用场景 ❌
- 非 OpenClaw 平台的快速集成需求
- 对 Node.js 22 环境难以满足的团队
- 仅需简单 KV 记忆存储的轻量场景

### 趋势判断

**上升期**（2026年4月开源，3 个月达 7.5K+ Star，社区贡献活跃）。随着 OpenClaw 生态的发展和 Agent 记忆需求的爆发，该项目的关注度预计继续增长。但如果不能尽快降低独立使用的门槛（MCP bridge 成熟度），可能仅限于 OpenClaw 生态圈内。

## 📂 关键文件路径速查

| 功能 | 路径 |
|------|------|
| 入口/导出 | `index.ts`, `src/core/index.ts` |
| 配置解析 | `src/config.ts` |
| L0 对话录制 | `src/core/conversation/l0-recorder.ts` |
| L1 去重 Prompt | `src/core/prompts/l1-dedup.ts` |
| 自动召回 | `src/core/hooks/auto-recall.ts` |
| 用户画像 | `src/core/persona/persona-generator.ts` |
| 存储层 | `src/core/store/` |
| 适配器层 | `src/adapters/` |
| CLI 入口 | `src/cli/index.ts` |
| Hermes 插件 | `hermes-plugin/memory/memory_tencentdb/` |
