# 🔬 hanshuaikang/nezha - 全方位深度调研

## 📌 一句话定位

**Nezha（哪吒）是一个「AI Agent 工作台」** — 在 Tauri 桌面应用里同时运行多个 Claude Code / Codex 会话，管理多项目的任务生命周期，让你不用在十几个终端窗口间来回切换。

> — 不是 IDE，不是聊天壳，而是 **AI 编码时代的多 Agent 控制台**

---

## 🏗️ 项目架构全景

### 📊 核心指标

| 指标 | 值 |
|------|------|
| 创建时间 | 2026-03-22（3 个月） |
| ⭐ Stars | 1,583（增长中） |
| 🍴 Forks | 156 |
| 📝 语言 | Rust (后端) + TypeScript (前端) |
| 📜 许可 | GPL-3.0 |
| 🔄 最后更新 | 2026-06-16（今日有更新） |
| 📦 版本 | v0.4.2 |
| 📏 安装包大小 | 仅 7MB |

### 架构分层

```
┌──────────────────────────────────────────────────┐
│                React 前端 (TypeScript)             │
│  CodeMirror 编辑器 · xterm 终端 · 文件树 · Git UI │
│  Shiki 语法高亮 · Markdown 渲染 · Skill Hub      │
├──────────────────────────────────────────────────┤
│            Tauri 桥接层 (@tauri-apps/api)          │
├──────────────────────────────────────────────────┤
│            Rust 后端 (src-tauri/src/)              │
│  TaskManager · session.rs (75KB) ·  pty.rs        │
│  git.rs · hooks.rs · fs.rs · storage.rs          │
│  portable-pty 终端模拟 · notify 文件监听           │
│  codex-rpc 用量查询 · notification 原生通知        │
└──────────────────────────────────────────────────┘
         ↓                    ↓                    ↓
   Claude Code CLI      Codex CLI            Git Worktree
```

### 核心 Rust 模块详解

| 模块 | 大小 | 职责 |
|------|------|------|
| `lib.rs` | 8.9KB | TaskManager 核心：PTY 生命周期、会话管理、macOS 窗口管理 |
| `session.rs` | **75KB** (最大文件) | Claude/Codex 会话发现、jsonl 日志流式读取、任务状态机 |
| `pty.rs` | 中等 | `portable-pty` 终端主从管理 |
| `git.rs` | 中等 | Git 操作：diff、commit、worktree、AI commit message |
| `hooks.rs` | 中等 | Agent Hook 系统：生命周期事件监听 |
| `event_watcher.rs` | 中等 | 文件系统变更监听（notify 库） |
| `subprocess.rs` | 605B | 跨平台子进程配置（Windows 无窗口标志） |
| `storage.rs` | 中等 | 本地持久化存储 |
| `usage.rs` | 中等 | Codex RPC 用量查询客户端 |

### 前端架构细节

前端基于 React 19 + TypeScript 6.0 + Vite 8，UI 组件库采用：
- `@radix-ui/react-popover/select` — 无样式 UI 基座
- `@xterm/xterm` — 终端模拟器
- `@uiw/react-codemirror` — CotEditor 集成
- `shiki` — 代码高亮
- `lucide-react` — 图标
- `marked` + `dompurify` — Markdown 渲染

---

## 🧠 独家发现

### 发现 1：Session 自动发现机制

Nezha 最内核的能力是**自动发现**正在运行的 Claude Code / Codex 会话文件（jsonl 格式），无需用户手动注册。

- **Codex**：自动扫 `~/.codex/sessions/` 目录
- **Claude Code**：自动识别 `~/.claude/sessions/` 目录

`session.rs` (75KB) 实现了完整的流式读取引擎：用 `read_session_lines_since()` 函数按偏移量增量读取 jsonl 日志，支持任务恢复和会话回放。

### 发现 2：「三头六臂」的并发模型

项目名哪吒寓意"三头六臂"，核心是**并发 Agent 调度**：

```
TaskManager
  ├─ pty_masters: HashMap<id, MasterPty>   — 终端主设备
  ├─ pty_writers: HashMap<id, Write>       — 终端写入通道
  ├─ child_handles: HashMap<id, Child>     — 子进程句柄
  ├─ codex_sessions: HashMap<id, Info>     — Codex 会话跟踪
  └─ claude_sessions: HashMap<id, Info>    — Claude 会话跟踪
```

每个 Agent 实例是一个独立的 PTY（伪终端），通过 `portable-pty` 库实现跨平台（macOS/Linux/Windows）。`remove_pty_handles()` 用固定锁顺序防止死锁。

### 发现 3：macOS 全屏隐藏的工程细节

`lib.rs` 中有一段精心设计的 macOS 全屏窗口隐藏逻辑：
- 原生全屏窗口独占一个 Space，直接 `hide()` 会留下黑屏
- 先退出全屏 → 轮询等待退出完成（100 次 × 50ms = 5s 兜底） → 8 次 × 120ms 间隔 hide
- 这在 Tauri 生态里属于**边缘 bug 的真实解决案例**

### 发现 4：Skill Hub 系统

Nezha 内置了 Skill 管理功能，支持：
- 软链方式集中管理本地的 Skill 文件
- Skill 冲突检测 (`SkillConflictDialog`)
- GUI 安装/卸载管理

### 发现 5：Git Worktree 原生集成

除了基本的 Git diff/commit 功能外，Nezha 原生支持 **Git Worktree** 工作流——这恰好和 Claude Code 2026-02 发布的 Worktree 特性互补，让用户可以并行运行多个完全独立的 Agent 工作区。

---

## 🌐 全网口碑画像

### 正面评价

| 来源 | 关键观点 |
|------|----------|
| AI 绘画教程网 | "直接把 Claude Code 和 Codex 当成工作台里的常驻工人" |
| 同上 | "终端多到烦的人的最爱" |
| Product Hunt 推荐 | 已上线 Product Hunt（featured badge） |
| HelloGithub 推荐 | 被列入 HelloGithub 推荐 |
| 社区 | "安装包只有 7MB，简洁轻量" |

### 主要批评 / 待修复

| 问题 | 说明 |
|------|------|
| macOS 未签名 | 需要手动执行 `xattr -rd` |
| Linux 支持未完善 | Roadmap 中 |
| 依赖外部 Agent | 必须先装好 Claude Code / Codex |
| 成熟度 | v0.4.2，仍在快速迭代中 |

---

## ⚔️ 竞品对比

| 维度 | Nezha | Cursor IDE | Windsurf | 传统终端复用 (tmux) |
|------|-------|------------|----------|---------------------|
| **定位** | Agent 工作台 | AI 原生 IDE | AI 原生 IDE | 终端多路复用 |
| **多 Agent 并发** | ✅ 核心能力 | ❌ 单会话 | ❌ 单会话 | ❌ 需手动 |
| **安装包大小** | 7MB | ~200MB+ | ~200MB+ | 原生 CLI 工具 |
| **技术栈** | Rust+Tauri | Electron | Electron | C 语言 |
| **会话持久化** | ✅ 自动发现 | ✅ | ✅ | ❌ |
| **Git 集成** | ✅ 原生 | ✅ | ✅ | ❌ |
| **Skill 管理** | ✅ | ❌ | ❌ | ❌ |
| **开源** | ✅ GPL-3.0 | ❌ 闭源 | ❌ 闭源 | ✅ BSD |
| **平台** | macOS/Windows/Linux | macOS/Windows | macOS/Windows | 全平台 |

### 差异化

- **独特定位**：Nezha 不做 AI 原生 IDE（不与 Cursor/Windsurf 竞争），而是做 **AI Agent 的调度面板**
- **轻量极致**：7MB vs 200MB+，Tauri 的技术选择带来明显优势
- **Skill 管理**：唯一一个内置 Skill 管理的 AI 编程桌面工具

---

## 🎯 核心研判

### 🟢 项目优势

1. **精准的生态位** — 不重复造 IDE，而是解决 Claude Code/Codex 用户"多个终端窗口"的真实痛点
2. **极轻量部署** — 7MB + Tauri 原生性能，启动速度和内存占用显著优于 Electron 竞品
3. **优秀的技术选型** — Rust 后端 (Tauri 2.x) + React 19，并发模型优雅
4. **活跃迭代** — 3 个月 168 次 commit，近乎每日更新
5. **任务生命周期视图** — session 自动发现 + 回放 + 恢复，比 bare CLI 体验大幅提升

### 🔴 项目风险

1. **极度依赖外部工具** — Nezha 本身不做任何 AI 编码，完全依赖 Claude Code / Codex，生态绑定风险高
2. **成熟度尚浅** — v0.4.2，Linux 支持未完善，macOS 签名问题未解决
3. **差异化脆弱** — 如果 Cursor/Windsurf/VS Code 内置类似的多 Agent 管理功能，Nezha 的独特价值会减弱
4. **单人项目** — 仅作者 hanshuaikang 主要维护，项目健康度依赖单一个体

### 适用场景 ✅

- 同时维护多个项目，每个项目跑独立 Agent 的开发者
- Claude Code + Codex 双工具用户
- 追求轻量桌面工具的 Vibe Coding 开发者
- 需要可视化会话管理的团队

### 不适用场景 ❌

- 需要完整 IDE 功能的场景（调试、重构、类浏览）
- 不使用 Claude Code / Codex 的开发者
- 对 macOS 签名有严格要求的封闭环境

### 趋势判断

**有潜力的新兴工具。** 3 个月 1.5K Stars + Product Hunt 推荐 + HelloGithub 认可，叠加 AI Agent 并行编程的大趋势，走势良好。但需要在 Claude Code/Codex 之外拓展更多 Agent 支持，才能避免单点绑定风险。如果作者能快速补齐 Linux 支持和扩展 Agent 类型，有望成为 AI Agent 工作台的标配。

---

## 📂 关键文件路径速查

| 文件 | 用途 |
|------|------|
| `src-tauri/src/lib.rs` | Rust 入口 — TaskManager 核心 |
| `src-tauri/src/session.rs` | 核心 — Claude/Codex 会话管理 (75KB) |
| `src-tauri/src/pty.rs` | 终端 PTY 管理 |
| `src-tauri/src/git.rs` | Git 操作封装 |
| `src-tauri/src/hooks.rs` | Agent Hook 系统 |
| `src-tauri/src/event_watcher.rs` | 文件系统监听 |
| `src-tauri/src/subprocess.rs` | 子进程跨平台配置 |
| `src-tauri/src/notification.rs` | 原生通知 |
| `src-tauri/src/storage.rs` | 本地持久化 |
| `src-tauri/src/usage.rs` | Codex RPC 用量查询 |
| `src/App.tsx` | React 入口 |
| `src/components/` | 前端组件 (40+ 组件) |
| `src/components/skill-hub/` | Skill 管理 UI |
| `src/components/git-diff/` | Git Diff 可视化 |
| `src/components/NewTaskView.tsx` | 新任务创建 |
| `src/components/TerminalView.tsx` | 终端渲染 |
| `knowledge/references/agent-hooks-support.md` | Hooks 文档 |
| `CLAUDE.md` | Claude Code 项目指令 |
| `AGENTS.md` | Agent work instructions |

## 🔗 参考链接

- GitHub: https://github.com/hanshuaikang/nezha
- ProductHunt: https://www.producthunt.com/products/nezha-2
- HelloGithub: Recommended badge
- 评测文章: Nezha：把 Claude Code 和 Codex 都塞进一个桌面工作台
