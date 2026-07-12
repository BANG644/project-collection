# 🔬 gastownhall/beads — 深度调研报告

> **仓库**: [gastownhall/beads](https://github.com/gastownhall/beads)  
> **调研日期**: 2026-07-13  
> **数据**: ⭐ 25,249 | 🍴 1,689 | 🐞 455 open issues | 📅 创建 2025-10-12，活跃推送至 2026-07-12  
> **语言**: Go | **协议**: MIT  
> **定位**: 面向 AI 编码 Agent 的分布式图谱化 issue 追踪器（Dolt 驱动）

---

## 一、项目定位

**Beads（bd）是给 AI 编码 Agent 用的"结构化记忆 + 任务图谱"**——它用 [Dolt](https://github.com/dolthub/dolt)（版本可控的 SQL 数据库）替代杂乱的 Markdown TODO 列表，把任务建模成带依赖关系的图谱，让 Agent 在处理长周期任务时不丢失上下文。一句话：**它是 Agent 的"issue tracker + 长期记忆"，且天然支持多 Agent / 多分支零冲突协作**。

## 二、项目亮点（差异化）

1. **Dolt 驱动 = 版本可控的记忆**：底层是 SQL 数据库，具备 cell-level merge、原生 branching、通过 Dolt remote 同步——记忆本身可 git 式分支合并。
2. **零冲突多 Agent 协作**：hash-based ID（`bd-a1b2`）避免 merge 碰撞，多 Agent / 多分支并发写不冲突。
3. **语义压缩（memory decay）**：自动把已关闭的旧任务摘要成精简记忆，省 context window。
4. **图谱链接**：`relates_to` / `duplicates` / `supersedes` / `replies_to` 关系，构建知识图谱而非扁平列表。
5. **双存储模式 + Git-Free**：Embedded（进程内 Dolt，默认）与 Server（dolt sql-server，多写者）两种模式；也可完全脱离 git 运行（`BEADS_DIR` + `--stealth`）。

## 三、核心架构

**存储引擎：Dolt**（MySQL-compatible 的版本化数据库）。两个模式：

- **Embedded（默认）**：`bd init` → Dolt 进程内运行，数据在 `.beads/embeddeddolt/`，单写者（文件锁）。
- **Server**：`bd init --server` → 连外部 `dolt sql-server`，数据在 `.beads/dolt/`，支持多并发写者，可用 TCP 或 Unix socket。

**Agent 集成（bd setup）**：`bd init` 默认写/更新 `AGENTS.md` 让 Agent 发现工作流；`bd setup codex|claude|factory|mux|cursor` 安装对应 hooks/settings/skills。

**角色路由**：
- Contributors（fork）：`bd init --contributor` 把规划 issue 路由到独立 repo（`~/.beads-planning`），不污染 PR。
- Maintainers（有写权限）：自动检测，规划直接进入主仓库。

**核心命令**：
`bd init` / `ready` / `create "Title" -p 0` / `update <id> --claim` / `dep add <child> <parent>` / `show <id>` / `prime`（注入上下文）/ `remember "insight"` / `prune` / `purge` / `dolt push|pull`

**层级 ID**：`bd-a3f8`(Epic) → `bd-a3f8.1`(Task) → `bd-a3f8.1.1`(Sub-task)。

## 四、应用场景与启发

- **长周期 Agent 任务**：让 Claude Code / Codex 用 `bd` 维护任务图谱，避免"上下文丢了重来"。
- **多 Agent 并行**：多个子 Agent 各自 claim 任务、写记忆，hash ID + Dolt merge 保证不冲突——解决多 Agent 协作的记忆一致性难题。
- **给同类需求的解法**：给 Agent 做"持久记忆"时，**别用 Markdown 文件（易冲突、难合并、难查询），改用版本化数据库（Dolt）**。它的三件套值得抄：① hash ID 防冲突 ② 依赖图谱取代 TODO 列表 ③ 语义压缩省 token。这是 Agent memory 工程化的一条清晰路线。

## 五、源码深度解读

**1) 入口与构建（Go）**

```
beads.go          # 主命令分发
beads_cgo.go      # CGO 启用时的构建标签文件
beads_nocgo.go    # 无 CGO 构建标签文件
cmd/              # 子命令实现（init/ready/create/update/dep/prime/remember/prune/dolt...）
```

用 build tags（`beads_cgo.go` / `beads_nocgo.go`）切换 CGO，兼顾静态分发与本地 Dolt 集成，是 Go 多后端编译的经典手法。

**2) 存储后端抽象（Dolt 默认，可换 Postgres/MySQL/SQLite）**

```bash
bd init                      # Embedded 模式（进程内 Dolt）
bd init --server            # 接外部 dolt sql-server
# 文档 STORAGE-BACKENDS.md 覆盖 Postgres / MySQL / SQLite 迁移
```
`.beads/issues.jsonl` 只是导出视图（供查看/互通），**不是真相源**；真相在 Dolt。跨机同步走 `bd dolt push` / `bd dolt pull`（refs/dolt/data）。这个"导出 ≠ 真相"的区分，避免了把 JSONL 当数据库导致的历史/分支丢失。

**3) 语义压缩与引用保护**

```bash
bd prune --older-than 30d --force   # 删 >30天 已关闭 bead
bd prune --older-than 90d --ignore-references --force
```
`bd prune` 自动跳过 ID 仍被任意 open/in-progress bead 的 description/notes/comments 引用的已关闭 bead（reference-aware protection），防止误删被下游引用的 ADR / 决策 / 验证类 bead。这是"自动清理"与"不破坏知识链路"的平衡设计。

## 六、全网口碑

- GitHub 25.2k⭐、1.7k fork，是 Agent memory / issue-tracker 赛道新锐，被 DeepWiki 收录并有多篇社区文章（ARTICLES.md）。
- 开发者欣赏"Dolt 版本化记忆"的新颖度与多 Agent 零冲突特性；455 open issues 多围绕 schema 迁移、server 模式、跨机同步边界——属快速演进期。
- 与 Claude Code / Codex / Cursor / Factory 均有官方 `bd setup` 集成，生态接入顺畅。

## 七、竞品对比 + 核心研判

| 维度 | beads | TaskMaster AI | Linear / GitHub Issues | Markdown TODO |
|------|-------|--------------|----------------------|--------------|
| 存储 | Dolt(版本化SQL) | 文件/DB | 云端SaaS | 纯文本 |
| 多Agent零冲突 | ✅ hash ID+Dolt merge | 部分 | ❌ | ❌ |
| 语义压缩 | ✅ memory decay | 部分 | ❌ | ❌ |
| 依赖图谱 | ✅ | 有限 | ✅(Linear) | ❌ |
| 离线/Git-Free | ✅ | ✅ | ❌ | ✅ |

**核心研判**：
- ✅ **记忆工程化方向正确**：Agent 长期记忆用"版本化数据库"而非"Markdown 文件"，是多 Agent 协作的客观刚需，beads 卡位早。
- ⚠️ **Dolt 依赖是双刃剑**：带来 merge/branch 超能力，但也引入 DB 运维复杂度（schema 迁移、server 模式、备份），小白上手成本高于纯文件方案。
- 💡 **可插拔存储是护城河**：支持 Postgres/MySQL/SQLite 后端（`STORAGE-BACKENDS.md`），降低被 Dolt 单一技术绑定的风险。
- 🔧 **风险**：455 open issues 显示跨机同步/迁移仍是硬骨头；若 Agent 框架（Claude Code 等）原生内置记忆，中间层价值或被吸收。

## 关键文件路径速查

- `beads.go` / `beads_cgo.go` / `beads_nocgo.go` — 主入口 + 构建标签
- `cmd/` — 子命令实现（init/ready/create/update/dep/prime/remember/prune/dolt…）
- `AGENTS.md` / `AGENT_INSTRUCTIONS.md` — Agent 工作流指引
- `docs/SETUP.md` — Agent / IDE 集成（bd setup）
- `docs/DOLT.md` — Dolt 后端与迁移
- `docs/STORAGE-BACKENDS.md` — Postgres/MySQL/SQLite 后端
- `docs/SYNC_CONCEPTS.md` / `PROTECTED_BRANCHES.md` — 同步与分支模式
- `.claude-plugin/` — 作为 Claude Code 插件自举
