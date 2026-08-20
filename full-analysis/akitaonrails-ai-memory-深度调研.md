# akitaonrails/ai-memory — 深度调研

> 调研日期：2026-08-21 ｜ 星标：3,507 ⭐ ｜ 协议：MIT（代码）/ 资产非商业 ｜ 语言：Rust ｜ 趋势：GitHub Trending 日榜 ｜ 作者：Fabio Akita(akitaonrails)

## 一、项目定位（一句话）

ai-memory 是一个 **跨 Agent 编码 CLI 的长期记忆服务器**（Rust 实现），把不同厂商的编码 Agent（Claude Code / Codex / OpenCode / Cursor / …）的观察编译成一份持久化、git 版本化的 Markdown wiki，让"退出 Claude Code、几小时后用 Codex 同目录继续"无需重述架构与失败尝试。

## 二、项目亮点（差异化）

- **跨 harness 记忆接力**：唯一把"跨厂商 Agent 记忆互操作"作为核心卖点的项目——同一份 wiki 被 20+ 客户端共享，天然解决"换工具就失忆"痛点。
- **Markdown-in-git，而非向量库**：wiki 是纯 Markdown 存 git 仓库，`grep` 友好、可 Obsidian 打开、可 `rsync` 备份，**没有向量库要运维**，也没有 `write_note` 仪式感。
- **极广客户端矩阵**：Claude Code / Codex / OpenCode / Cursor / Gemini CLI / Kiro / Antigravity / Grok / Kimi / OpenClaw / Devin / Pi / 甚至 Zero / Swival，覆盖主流与新锐 harness。
- **严格去污染设计**：authority-aware recall 区分"决策页（`_rules/decisions/procedures/gotchas`）"与"会话证据页"，检索文本始终作为**不可信历史证据**，永不因命名空间/层级/排名获得指令权威——从设计上防止记忆被污染成 prompt injection。
- **零摩擦捕获 + 可选 LLM**：lifecycle hooks 有界、消毒地捕获；LLM 完全 opt-in，零-LLM 模式仍提供 FTS5 + 实体 + 图邻居检索。

## 三、核心架构（克制呈现）

```
<wiki_root>/<workspace_id>/<project_id>/…   # 按稳定 UUID 隔离，同 repo 多 worktree 共享一 project
_global/                                    # 全局偏好 scope（技术选型/代码风格），注入每个项目
_rules/ decisions/ procedures/ gotchas/     # 权威页（召回时加权，但不具指令权威）
docs/ARCHITECTURE.md                        # 完整设计文档
```

- **后端**：Rust（axum）服务 + SQLite(FTS5) + git 版本化 markdown wiki；MCP over stdio/HTTP。Server 为单一真相源，所有 CLI 子命令都是其 HTTP 客户端，绝不直接碰 SQLite/wiki 文件。
- **捕获**：lifecycle hooks 写入有界、消毒的观察（prompt/工具生命周期/会话边界）；per-repo `.ai-memory.toml` 的 `[capture] ignore_paths` 在到达 spool 前丢弃匹配事件。
- **召回**：FTS5 + 实体匹配 RRF + 图邻居 RRF + 可选向量 RRF 四路融合；authority-aware 调权在截断前偏向权威页，但仅影响检索来源、不改文本可信度。

## 四、应用场景与启发（重点）

- **场景 1 — 多 Agent 协作的"记忆总线"**：个人或团队在 Claude Code / Codex / OpenCode 间切换时，记忆无缝接力，避免重复探索。
- **场景 2 — 团队知识沉淀**：`memory_write_page` 写下的决策/约定/坑是 git 版本化、可 code review 的，比散落的 `CLAUDE.md` 更可治理。
- **启发**：① "**Markdown-in-git 而非向量库**"大幅降低记忆层运维成本，且天然获得版本历史/可审计/可备份；② "**跨 harness 标准化 hook 接入**"是可复用的记忆层范式，任何做 Agent 记忆的项目都该支持多 CLI 而非绑定单一厂商；③ "**authority-aware recall 区分决策与证据**"是对抗记忆污染（prompt injection via memory）的关键设计，值得所有长期记忆系统借鉴。

## 五、源码解读（核心模块）

来自 README 明确引用的机制与文件（细节见 `docs/ARCHITECTURE.md`）：

- `rust-toolchain.toml` 锁定 Rust 1.95+，发布 linux/amd64+arm64 Docker 镜像与 macOS/Windows 原生二进制——体现其"服务器优先 + 多平台原生"的交付策略。
- `.ai-memory.toml` marker 文件：放在任意祖先目录即可覆盖 workspace/project 字段，支持 mono-repo、work/personal 拆分、多客户咨询公司——这是"per-project 隔离 by construction"的落地方式。
- lifecycle hooks 注入：每种 harness 有专门的 `install-hooks` 包（如 `install-hooks --agent kiro-cli`），在 SessionStart 注入 handoff、在 Stop/PostToolUse 捕获——客户端矩阵膨胀的本质是"为每种 harness 写一套 hook 适配"。

## 六、全网口碑

- 赞誉：由巴西知名 Ruby/Rails 布道者 Fabio Akita(akitaonrails) 出品，在 Agent 记忆赛道因"严谨的去污染设计 + 跨工具互操作"受关注；2026-05 创建后快速迭代，文档极其详尽。
- 观察：项目极早期，客户端矩阵虽广但每种 harness 的 hook 适配都是维护负担；设计上对"记忆被污染"的防御意识领先同类。

## 七、竞品对比 + 核心研判

| 维度 | ai-memory | Mem0 | LangGraph 记忆 | Claude Code 原生 memory | OpenClaw 记忆 |
|------|-----------|------|----------------|------------------------|---------------|
| 跨 harness 互操作 | ✅ 20+ | ⚠️ | ❌(绑定 LangChain) | ❌ | ⚠️ |
| 向量库依赖 | ❌(纯 MD+git) | ✅ | ✅ | ❌ | ✅ |
| 去污染设计 | ✅ authority-aware | ⚠️ | ⚠️ | ⚠️ | ⚠️ |
| 实现语言 | Rust | Python | Python | — | — |

**核心研判**：ai-memory 击中了"多 Agent 工具切换即失忆"的真实痛点，其 **Markdown-in-git + 跨 harness hook 接入 + 严格去污染** 三件套是记忆层的优秀范式，强烈推荐多 Agent 工作流用户自托管试用。**风险点**：客户端矩阵膨胀带来的长期维护复杂度；早期项目 API/设计仍可能变动。作为"Agent 记忆层刚需赛道"的有力玩家，值得持续跟踪。

> 关键文件速查：`docs/ARCHITECTURE.md`、`docs/marker-file.md`、`rust-toolchain.toml`、`.ai-memory.toml`、`docs/managed-workstreams.md`、`docs/ARCHITECTURE.md` 中的 FTS5/实体/图/向量 RRF 召回设计
