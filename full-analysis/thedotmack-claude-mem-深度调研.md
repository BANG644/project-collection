# thedotmack/claude-mem 深度调研

> 调研日期：2026-07-27 | 星标：88,631⭐ | 协议：Apache-2.0 | 语言：JavaScript / TypeScript
> 定位：跨 Agent 的「会话记忆压缩」系统 —— 捕获 Agent 行为、AI 压缩、向量+SQLite 存储、未来会话自动注入

## 项目亮点（差异化）

- 🧠 **跨 Agent 通用记忆层**：不止 Claude Code，还支持 OpenClaw / Codex / Gemini / Hermes / Copilot / OpenCode 等 —— 一个记忆引擎服务所有 Agent。
- 🗜️ **「捕获 → AI 压缩 → 向量+SQL 双存储 → 注入」** 的完整闭环：不是简单转录，而是用 LLM 把冗长会话压成高密度记忆。
- 🗄️ **SQLite + ChromaDB 双引擎**：结构化元数据走 SQLite，语义检索走 ChromaDB 向量库（topics 明确含 chromadb / sqlite / embeddings / rag）。
- 🪝 **Hook 驱动的零侵入接入**：通过 Agent 的 hook 机制捕获会话事件，对业务代码零侵入。
- 🔌 **SDK + 多集成 + 后台 Supervisor**：`sdk/` 供二次开发，`integrations/` 适配各 Agent，`supervisor/` 跑后台压缩 worker。

## 项目全景

claude-mem 解决的是 Agent 的「**金鱼记忆**」问题：每次新会话 Agent 都从零开始，丢失了昨天的决策上下文、踩过的坑、用户偏好。`claude-mem` 在会话中持续捕获 Agent 的每一步动作，用 AI 压缩成记忆，存入本地（SQLite 元数据 + ChromaDB 向量），在**未来的会话中自动检索并注入相关上下文**。

`package.json` 关键字段：`name: claude-mem`，`bin: { "claude-mem": "./dist/npx-cli/index.js" }`，`description: "Memory compression system for Claude Code - persist context across sessions"`。安装即用 `npx` 或插件形式（` .claude-plugin` / `.codex-plugin` / `openclaw/` 目录均存在）。

## 核心架构

`src/` 目录揭示了完整的能力分层：

```
src/
├─ hooks/        ← 会话事件捕获（Agent hook 注入点）
├─ core/         ← 记忆压缩 / 去重 / 摘要核心逻辑
├─ storage/      ← SQLite（结构化）+ ChromaDB（向量）双存储适配
├─ services/     ← 记忆检索 / 注入 / 生命周期管理
├─ sdk/          ← 供其他 Agent/应用接入的 SDK
├─ integrations/ ← 各 Agent 适配器（Claude/Codex/Gemini/...）
├─ server/ servers/ ← 记忆服务 / 潜在 MCP server
├─ supervisor/   ← 后台压缩 worker 调度
├─ cli/ npx-cli/ ← 命令行入口
├─ ui/           ← 记忆可视化
├─ shared/ types/ utils/ build/  ← 公共层
```

**数据流**：
```
Agent 会话 ──hook──► core 捕获原始事件
        │
        ▼
core 调用 LLM 压缩（摘要 / 提取决策 / 用户偏好）
        │
        ├─► storage: SQLite 存结构化元数据（who/what/when）
        └─► storage: ChromaDB 存 embedding 向量（语义检索）
        │
        ▼
未来会话 ──services 检索相关记忆──► 注入 system/context
```

`supervisor/` 表明压缩是**异步后台任务**，不阻塞主会话；`server/` + `servers/` 暗示它可独立成记忆服务（甚至 MCP server），供多个 Agent 共享同一记忆体。

## 源码深度解读

三个最值得借鉴的设计：

1. **Hook 零侵入捕获**（`src/hooks/`）：利用 Agent 原生的 PreToolUse/PostToolUse/Stop 等 hook 点挂接，捕获工具调用与输出，**业务代码完全无感**。这是它能「跨 Agent 通用」的前提 —— 每个 Agent 只需提供 hook 适配（见 `integrations/`）。

2. **双存储分层**（`src/storage/`）：SQLite 负责精确查询（按项目/时间/类型过滤），ChromaDB 负责语义召回（"上次那个 OAuth 报错怎么解决的"）。这种「结构化 + 向量」混合是记忆系统的标准最优解，与 `mem0` / `supermemory` 思路一致。

3. **异步 Supervisor 压缩**（`src/supervisor/`）：压缩（LLM 调用）成本高，放到后台 worker，会话结束后再压缩落库，避免拖慢交互。这是工程化上区别于「同步转录类」记忆工具的关键。

## 应用场景与启发

- **长周期项目的上下文延续**：多日开发一个大功能，每天 Agent 自动带上昨天的决策记忆。
- **团队共享记忆**：`server/` 形态下，多个 Agent / 多开发者可共享同一项目记忆体。
- **🔧 给同类需求的启发**：
  - 「**hook 捕获 + 异步压缩 + 双存储 + 注入**」是 Agent 记忆系统的成熟范式，直接可抄。
  - 记忆的粒度很重要：压缩摘要 > 全量转录，否则记忆库会迅速膨胀且噪声大。
  - 跨 Agent 通用性的关键在于**把接入做成 hook 适配层**，而非耦合某一 Agent 内部。

## 社区口碑

- 88k⭐、Apache-2.0，是「Agent 记忆」品类当前最热项目之一，活跃度极高（pushed 2026-07-23）。
- 用户普遍认可「跨 Agent 通用 + 本地优先」定位；常见对比对象是 `mem0`（框架更重）、`supermemory`（云端）。
- 仓库体积巨大（289MB，含 ChromaDB 依赖与测试 fixture），首次安装偏重。

## 竞品对比

| 项目 | 星标 | 差异 |
|------|------|------|
| **thedotmack/claude-mem（本品）** | 88k | 跨 Agent 通用 + 本地优先 + Hook 零侵入 + 双存储 |
| mem0ai/mem0 | 高 | 更重的记忆框架，云/自托管，开发者向 |
| supermemoryai/supermemory | 中 | 云端记忆服务，API 化 |
| ClaudioDrews/memory-os | — | 个人 OS 型记忆 |
| DeusData/codebase-memory-mcp | — | 聚焦代码库记忆的 MCP |
| TencentCloud/Agent-Memory | — | 企业级 Agent 记忆 |

> 本品的差异化是「**本地优先 + 跨 Agent hook 适配 + 异步压缩**」，在「个人开发者自用、不想把记忆传云端」场景下优于 mem0/supermemory 的云端路线。

## 核心研判

- **价值**：把「Agent 长期记忆」做成开箱即用的本地引擎，且架构（hook 捕获 / 双存储 / 异步压缩）是记忆系统的事实标准范式，极具复用与教学价值。
- **风险**：① 依赖 ChromaDB 使安装偏重；② 压缩质量依赖底层 LLM，可能丢失关键细节；③ 跨 Agent 适配器需随各 Agent 版本跟进维护。
- **趋势**：Agent 记忆将从「玩具」走向「基础设施」，本地优先 + 跨 Agent 共享是明确方向；MCP 化（server/ 已现雏形）会让记忆成为可插拔能力。
- **给开发者启发**：做记忆系统，**先定「捕获点（hook）→ 压缩策略 → 存储分层 → 注入时机」四件套**，再谈功能；本地优先能显著降低采用门槛。

## 关键文件速查

- `package.json` —— bin/claude-mem 入口、scripts（build/worker/sync-marketplace）
- `src/hooks/` —— 会话事件捕获（零侵入接入点）
- `src/core/` —— 记忆压缩 / 摘要核心
- `src/storage/` —— SQLite + ChromaDB 双存储适配
- `src/services/` —— 检索 / 注入 / 生命周期
- `src/supervisor/` —— 后台异步压缩 worker
- `src/sdk/` + `integrations/` —— 二次开发 SDK 与多 Agent 适配
- `plugin/` + `.claude-plugin/` / `.codex-plugin/` / `openclaw/` —— 各平台插件入口
