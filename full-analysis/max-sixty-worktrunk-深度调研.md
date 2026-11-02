# max-sixty/worktrunk 深度调研

> 调研日期：2026-11-03 ｜ 定位：面向「并行 AI Agent 工作流」的 Git worktree 管理 CLI
> 仓库：https://github.com/max-sixty/worktrunk ｜ Stars：≈9.9k ｜ 语言：Rust ｜ 许可：MIT OR Apache-2.0

## 一、项目定位（一句话）

Worktrunk 是一个 Rust 写的小型 CLI（`wt`），把 Git worktree 管理做得「像切分支一样简单」——专为「同时跑多个 AI 编程 agent（Claude Code / Codex 等），每个 agent 一个隔离工作目录」的场景而生，提供分支寻址、状态清单、生命周期 hooks 与写时复制（COW）构建缓存。

## 二、项目亮点（差异化，开篇先看）

1. **为并行 agent 而生**：核心假设是「你的开发者可能是一个模型，不是人」——fan-out 多个 agent 各占一个 worktree，互不改乱，diff 可独立 review 后合并。
2. **分支即地址**：worktree 用分支名寻址（`wt switch feat`），路径由可配置模板自动算出，不必再手敲 `git worktree add -b feat ../repo.feat && cd ...`。
3. **生命周期 Hooks**：在 worktree 创建 / 合并前 / 合并后等节点跑自定义命令（如自动装依赖、起 dev server），把环境准备自动化。
4. **COW 共享构建缓存**：在 APFS / btrfs / XFS 上跨 worktree 共享 `target/`、`node_modules/`，避免每个 worktree 重复构建。
5. **原生 agent 启动**：`-x` 标志切到 worktree 后直接拉起 agent（`wt switch -x claude -c feat -- 'Fix pagination'`），agent 无关（shell 里能启的都行）。

## 三、核心架构（克制呈现）

Rust 二制（`wt`，Windows 上为避免与终端 `wt` 冲突装为 `git-wt`），源码在 `src/`：

- **`commands/`**：核心命令实现——`switch`（创建/跳转）、`list`（状态清单：ahead/behind、暂存、提交信息）、`remove`、`merge`（squash/rebase/清理一条龙）、`step`（提交-推送生命周期 + LLM 生成提交信息）、`for_each`、`init`、`relocate`、`backup` 等。
- **`git/`**：git 底层交互——`reap.rs`（清理）、`recover.rs`、`ref_deletion.rs`、`fsmonitor.rs`、`ci_platform.rs`（拉 CI 状态）、`parse.rs`/`diff.rs`。
- **`git_wt.rs`**：worktree 自身的创建/寻址/模板解析。
- **`llm.rs`**：调用模型生成提交信息 / 分支摘要（需注意私有代码配置）。
- **`hooks.rs` / `priority.rs` / `cache.rs`**：钩子执行、优先级、缓存（COW）。
- **`cli/` + `shell/`**：CLI 解析与 shell 集成（切换 worktree 时自动 `cd`）。

## 四、应用场景与启发

- **多 agent 并行开发**：给 3+ 个 coding agent 各派一个任务、各占一个 worktree，从一个终端 fan-out，再独立 review/merge——典型用法 `wt switch -x claude -c feat-a -- '...'`。
- **无 stash 审 PR**：`wt switch pr:123` 把某个 PR 分支开到独立 worktree，当前工作不受扰。
- **多 dev server 同开**：`hash_port` 过滤让每个 worktree 跑在稳定唯一端口，可并排对比分支。
- **给同类需求的启发**：① 当「执行者」可能是 LLM 时，工具 ergonomics 要按**非人类操作者**重新设计（分支寻址、一键生命周期）；② **COW 构建缓存**把「隔离」与「不重复构建」调和，是并行 agent 落地的关键工程点；③ Hooks 把「环境准备」从人工步骤变成声明式生命周期事件。

## 五、源码深度解读

**1) 命令分层**（`src/commands/`）：每个 git 工作流动作是一个独立模块，`mod.rs` 汇总；`switch` 负责「按分支名解析路径→创建或跳转」，把原生 3–4 条 git 命令收敛成一条。合并类命令把 commit/rebase/merge/cleanup 串成单步：

```rust
// 设计意图：一条命令取代原生多条 git 操作
// wt switch --create feature-auth  => 建分支 + 建 worktree + cd 进去
// wt merge main                   => squash + rebase onto main + fast-forward + 清理
```

**2) LLM 提交信息**（`src/llm.rs` + `commands/step.rs`）：`wt step` 在提交阶段调用模型生成提交信息，并以可读方式呈现；源码与 `README.md`/`docs`/`src/cli/mod.rs` 等通过 `readme_sync` 集成测试保持同步，确保文档与实现不漂移。

## 六、全网口碑

- **正面共识**：评测普遍认为「只要你开始并行跑哪怕一个 AI agent，就值得装」。它把原生 git worktree 的啰嗦操作压缩到单命令，分支寻址 + 状态清单 + hooks + 合并自动化都「为 agent 场景写得很直白」。2026 年初发布后迅速成为最受欢迎的 git worktree 管理器；MIT/Apache-2.0 双许可，商用友好。
- **明确边界**：① **shell 集成（wt config shell install）几乎是完整体验的前提**，否则切目录不顺手；② **COW 缓存仅 APFS/btrfs/XFS 生效**，ext4 用户拿不到该收益；③ LLM 功能会读代码，私有仓启用前先确认模型配置；④ 项目年轻（2025-10 创建），维护者积极但仍在快速演进。

## 七、竞品对比与核心研判

| 维度 | worktrunk | 原生 git worktree | git-branchless | Graphite |
|---|---|---|---|---|
| 并行 agent 优化 | ✅ 核心 | ❌（通用） | 部分 | 部分 |
| 分支寻址 / 单命令 | ✅ | ❌ 啰嗦 | ✅(stack) | ✅(stack) |
| 生命周期 hooks | ✅ | ❌ | 部分 | 部分 |
| COW 构建缓存 | ✅(特定 FS) | ❌ | ❌ | ❌ |
| LLM 提交信息 | ✅ | ❌ | ❌ | ❌ |

**核心研判**：worktrunk 不是通用 Git GUI，而是**专为「agent 是主要操作者」这一新范式打磨的底层构建块**——它待在终端、agent 无关、把 worktree 当分支一样易用。最适合已经在并行开多个 Claude/Codex、或多开功能分支的 Git 用户；若你不在跑并行 agent，它仍是更友好的 worktree 封装，但核心价值在于「fan-out agent」工作流。注意 shell 集成与文件系统对 COW 的前提。

## 八、关键文件路径速查

- `src/commands/switch.rs` / `list.rs` / `merge.rs` / `step.rs` / `for_each.rs` — 核心命令
- `src/commands/hooks.rs` — 生命周期钩子
- `src/git/git_wt.rs` — worktree 创建/寻址/模板
- `src/git/reap.rs` / `recover.rs` / `ref_deletion.rs` / `fsmonitor.rs` / `ci_platform.rs` — git 底层交互
- `src/llm.rs` — LLM 提交信息/摘要
- `src/cache.rs` / `src/priority.rs` — COW 缓存与优先级
- `src/cli/` / `src/shell/` — CLI 与 shell 集成
- `Cargo.toml` / `hooks/` / `skills/` / `plugins/` — 依赖、钩子与 agent 技能
