# BloopAI/vibe-kanban 全方位深度调研报告

> 调研时间：2026-06-29 | 仓库：BloopAI/vibe-kanban
> 数据基准：Stars 27,211 | Forks 2,874 | v0.1.44 | 2,070+ commits

---

## 1. 一句话定位

**Vibe Kanban 是 AI 编程时代的"元工具"——一个位于 Claude Code、Codex、Gemini CLI 等编码 Agent 之上的编排层（Orchestration Layer），通过看板界面 + Git Worktree 隔离机制，把"与 AI 聊天写代码"升级为"像管理工程师团队一样管理 AI Agent 工单"。**

它不是又一个 AI 编程助手，而是"管理 AI 编程助手的助手"。

---

## 2. 项目亮点（5 条）

### 2.1 精准卡位"人机协作瓶颈"

Vibe Kanban 的洞察非常精准：当 AI 编码 Agent 变得足够强时，瓶颈不再是**代码生成速度**，而是**人类的规划和审查带宽**。开发者花在看终端输出、切换上下文、合并代码上的时间，远多于 Agent 执行时间。Vibe Kanban 把人类从"盯着光标闪烁"中解放出来，让开发者专注于"给什么任务、如何验收"。

### 2.2 Git Worktree 隔离 —— 比 Docker 更轻量的安全执行环境

Vibe Kanban 的核心技术决策是使用 **Git Worktree** 而非 Docker 来隔离 Agent 执行。每个任务在基于 main 分支的独立 Worktree 中运行，互不干扰。相比于 Docker 容器（需要容器化、镜像管理、性能损耗），Git Worktree 零额外开销、不改变运行环境、不拖慢笔记本性能（M3 Mac 上可流畅运行多个 Worktree）。这是整个项目的"地基级"设计决策。

### 2.3 多 Agent 统一编排 —— provider-agnostic 的抽象层

通过 `StandardCodingAgentExecutor` trait，Vibe Kanban 统一了 10+ 种 AI 编码 Agent 的调用接口（Claude Code、Codex、Gemini CLI、GitHub Copilot、Amp、Cursor、OpenCode、Droid、CCR、Qwen Code）。开发者可以在不同任务中选用不同 Agent，也能在项目层面做 A/B 比较。这种"对所有 Agent 一视同仁"的姿态，在供应商锁定的 AI 工具市场中独树一帜。

### 2.4 从规划到合并的端到端闭环

Vibe Kanban 覆盖了完整的开发流程：Issue 规划（看板）→ Agent 执行（Worktree 隔离）→ Diff 审查（内联评论）→ Dev Server 预览（内置浏览器 + DevTools）→ 合并/PR（AI 生成描述 + 一键合并）。每一步都在同一个 UI 中完成，不打断开发节奏。尤其值得注意的是"内联评论 + Follow-up 指令"功能——审查者可以直接在 Diff 上给 Agent 反馈，Agent 在上下文中继续修改。

### 2.5 激进简洁的分发方式

`npx vibe-kanban` 一键安装，零配置启动。NPM 包自动提取 Rust 编译的 Server 二进制 + React 前端，自动分配端口、自动打开浏览器。这种"跟安装一个 NPM 依赖包一样简单"的分发哲学，极大降低了使用门槛，是项目能在 1 年内积累 27k Stars 的重要推动力。

---

## 3. 项目架构全景

### 3.1 四层架构总览

```
┌────────────────────────────────────────┐
│          表现层 (React SPA)             │
│  local-web / remote-web / web-core     │
│  看板视图 · Diff 审查 · Dev Server      │
│  内置浏览器 · 实时终端输出               │
├────────────────────────────────────────┤
│          应用层 (Rust/Axum)             │
│  LocalContainerService                  │
│  EventService · ExecutorService        │
│  GitService · ConfigService            │
│  PrMonitorService · ImageService       │
├────────────────────────────────────────┤
│          执行器层 (Executor)            │
│  StandardCodingAgentExecutor trait     │
│  Claude / Codex / Gemini / Cursor ...  │
│  command-group 子进程管理               │
├────────────────────────────────────────┤
│          数据层                         │
│  SQLite (本地) / PostgreSQL (远程)      │
│  SQLx · ts-rs 类型同步                  │
│  MsgStore + WebSocket 实时推送          │
└────────────────────────────────────────┘
```

### 3.2 Rust 多 Crate 架构（Monorepo）

| Crate | 类型 | 职责 |
|-------|------|------|
| `server` | 二进制 | Axum 主服务入口，路由注册 |
| `local-deployment` | 库 | 本地部署生命周期管理 |
| `deployment` | 库 | `Deployment` trait，部署抽象 |
| `services` | 库 | 业务逻辑（Container、Git、Executor、Event、PR Monitor 等） |
| `executors` | 库 | AI Agent 执行器工厂 & StandardCodingAgentExecutor trait |
| `db` | 库 | SQLx 模型、数据库迁移、MsgStore |
| `api-types` | 库 | 共享类型定义，`#[derive(TS)]` 自动生成 TypeScript 类型 |
| `git` | 库 | Git 操作封装（git2 crate） |
| `utils` | 库 | 工具函数、错误类型、配置文件 |
| `tauri-app` | 应用 | Tauri v2 桌面应用（自动更新、系统托盘、原生通知） |
| `npx-cli` | 应用 | NPM 分发入口（NPM 包提取二进制） |

### 3.3 多 Agent 编排机制

Vibe Kanban 的编排并非传统意义上的"多 Agent 协作协议"，而是一种**任务队列 + Worktree 隔离**的工作流引擎：

1. **任务创建**：用户在 Kanban 看板上创建 Issue，编写描述和验收标准
2. **Executor 选择**：为每个任务指定 AI Agent（Claude Code / Codex / 等）
3. **Worktree 创建**：`GitWorktreeManager` 在独立目录创建新 Worktree，自动关联新分支
4. **命令构建**：`CommandBuilder` 根据 Executor 类型构造 CLI 命令
5. **进程管理**：使用 `command-group` 生成子进程，异步读取 stdout/stderr
6. **实时推送**：WebSocket 将 Agent 执行的每一步发送到前端
7. **结果归集**：执行完成后提取 Git Diff，构建 `ExecutorResponse`
8. **审查合并**：Diff 审查后合并回主分支，清理 Worktree

### 3.4 桌面应用（Tauri v2）

Tauri 桌面应用提供了本地部署的最佳体验：
- **自动更新**：通过 Tauri updater 无缝升级
- **系统托盘**：后台运行，不阻塞终端
- **原生通知**：任务完成、合并冲突等事件通知
- **代码签名**：macOS/Windows 签名认证
- **终端 vs 浏览器模式**：默认启动桌面应用，`--browser` 参数切换 Web 模式

### 3.5 远程部署架构

Vibe Kanban 支持通过 Docker 部署云实例：
- **数据库**：PostgreSQL（替代本地 SQLite）
- **OAuth**：GitHub / Google 登录
- **Relay Tunnel**：中继隧道支持远程访问本地编辑器
- **Caddy**：反向代理 + HTTPS
- **多租户**：支持团队协作

---

## 4. 应用场景与启发（重点）

### 4.1 三个典型场景

**场景一：遗留代码现代化改造**
> 将大量 Cobalt 代码转换为 Java，或升级老旧框架。这类任务重复性高、隔离性好，适合批量并发。开发者可以在看板上创建 10 个任务，分给 3 个 Claude Code 实例并行执行，每 5 分钟审查一轮 Diff。

**场景二：多方案并行探索（Prototyping）**
> 同时尝试 3 种不同的算法实现，分发给 3 个 Agent（Claude Code / Codex / Gemini），然后人类选择最好的一个合并。这是在传统开发中几乎不可能的操作——因为开发者的时间是串行的。

**场景三：深度代码库分析**
> 让 Agent 对代码库进行深度扫描和分析，生成报告或 To-Do List，而不直接修改代码。Vibe Kanban 将这种"只读分析"任务也纳入管理。

### 4.2 对 AI Agent 工作流管理的五大启示

**启示一：人类瓶颈是 AI 编程时代真正的"最后一公里"**

当 Agent 生成代码的速度远超人类审查能力的上限时，效率的瓶颈不在于 Agent 本身，而在于人类如何组织、分发和验收工作。Vibe Kanban 本质上是一个**人类注意力管理工具**——它把开发者从"盯着 Agent 干活"解放为"批量审查 Agent 的产出"。这个认知对任何构建 AI 开发工具的人都有启发意义：提升开发者效率的最佳方式，不是让 Agent 更快，而是让人类更能驾驭 Agent。

**启示二：Git Worktree 是最适合 Agent 任务的隔离方案**

与 Docker 容器化方案相比，Git Worktree 有四个不可替代的优势：
- **零性能损耗**：不引入虚拟化层
- **环境一致性**：Agent 在真实开发环境中运行，不会遇到"容器内能跑、容器外不行"的问题
- **天然版本追踪**：每次 Agent 执行的结果本身就是 Git 分支，审查、合并、回滚都是原生 Git 操作
- **零配置成本**：不需要写 Dockerfile，不需要管理镜像

这是一个"少即是多"的经典案例——不是所有问题都需要容器来解决。

**启示三：看板范式完美匹配 AI 任务的生命周期**

Kanban 的 Todo → In Progress → In Review → Done 状态流转，与 AI 编码 Agent 的任务生命周期天然对齐：
- **Todo**：编写 Issue、设定验收标准（Spec）
- **In Progress**：Agent 在执行窗口中工作
- **In Review**：人类审查 Diff，提供反馈
- **Done**：合并完成，Worktree 清理

看板本身就是一个"工作流可视化系统"，而 Vibe Kanban 把 Agent 的执行状态直接映射到看板列上，这是"范式匹配"的完美体现。

**启示四："标准化执行器抽象"是 Agent 编排的基础设施**

Vibe Kanban 的 `StandardCodingAgentExecutor` trait 背后是一套完整的"Agent 标准化理论"：无论底层 Agent 是什么，只要暴露统一的 CLI 接口和输出格式，就可以被编排。这在 Agent 生态快速演变的当下尤其重要——今天用 Claude Code，明天可能换成更好的模型，有了抽象层，切换成本接近于零。

**启示五：产品已停运，但代码资产依然有价值**

"Vibe Kanban is sunsetting" 的实际含义是：BloopAI 公司未能找到可持续的商业模式（Apache 2.0 开源 + 云服务订阅这条路没有走通），但源代码社区可以 fork 和继续维护。这个事实带来的启发是：**AI 工具类开源项目的商业化路径依然不清晰**，尤其是当你构建的是一个"编排层"（其他 Agent 的上层）时，价值捕获非常困难——因为 Agent 提供商（Anthropic、OpenAI、Google）随时可以在自己的产品中内置类似功能。

### 4.3 与自身工作的关联思考

如果要将 Vibe Kanban 的思路应用到实际工作中，以下几点最值得关注：

1. **Agent 工作流不应与具体 Agent 绑定**：任何 Agent 编排系统都应该采用 provider-agnostic 的设计，减少供应商锁定风险
2. **隔离 + 可见性是 Agent 代码管理的一体两面**：Git Worktree（隔离）+ 实时流输出（可见性）是最小可行组合
3. **审查流程是 Agent 产出质量的唯一把关机制**：Vibe Kanban 的 Diff 审查 + 内联反馈 + Follow-up 修改 ≈ 代码审查的 Agent 原生版
4. **MCP 配置中心化是降低维护成本的关键**：一个项目级 MCP 配置文件，所有 Agent 自动继承，避免重复配置

---

## 5. 核心源码解读

### 5.1 Container 编排（`crates/services/src/container.rs` 思路）

Vibe Kanban 的 Container 不是 Docker 容器，而是"逻辑容器"——一个由 Worktree 目录 + 进程组 + 配置项构成的工作单元。

核心执行流程：

```
main_execute_task()
├── validate_task_input()           # 输入校验
├── create_git_worktree()           # 创建隔离工作树
├── prepare_executor_config()       # 按 Agent 类型注入配置
├── spawn_ai_process()              # 异步启动 Agent 子进程
│   ├── build_cli_command()         # 构建 CLI 命令
│   ├── setup_environment()         # 注入环境变量
│   └── start_streaming()           # 启动 stdout/stderr 流
├── monitor_execution()             # 监控进程生命周期
│   ├── parse_stdout()              # 逐行解析
│   ├── handle_stderr()             # 错误处理
│   └── update_task_status()        # 推送状态更新
└── finalize_execution()            # 收尾
    ├── commit_changes()            # Git 提交变更
    ├── cleanup_worktree()          # 清理工作树
    └── send_notifications()        # 通知
```

### 5.2 任务调度与状态机

前端 TypeScript 定义了严格的状态转换规则：

```typescript
// packages/web-core/src/types.ts (逻辑示意)
export type TaskStatus =
  | "todo"        // 待处理
  | "inprogress"  // 进行中（Agent 正在执行）
  | "inreview"    // 审查中（等待人类审查）
  | "done"        // 已完成
  | "cancelled";  // 已取消

// 状态转换矩阵
const allowedTransitions: Record<TaskStatus, TaskStatus[]> = {
  todo: ["inprogress", "cancelled"],
  inprogress: ["inreview", "cancelled"],
  inreview: ["todo", "done", "cancelled"],
  done: ["todo"],
  cancelled: ["todo"],
};
```

状态转换不仅是 UI 更新，还附带副作用：`inprogress → 创建 Worktree`、`inreview → 提取 Git Diff`、`done → 合并代码`。

### 5.3 数据库设计（`crates/db/`）

数据库层使用 SQLx，本地 SQLite / 远程 PostgreSQL 双模式。关键表设计：

- **projects**：项目信息，关联 Git 仓库路径
- **tasks**：任务卡片、状态、关联项目
- **task_attempts**：每次 Agent 执行的独立记录（一个任务可以多次尝试）
- **workspaces**：Git Worktree 映射表，追踪分支、状态
- **executor_profiles**：Agent 配置（CLI 命令、环境变量等）
- **events**：事件溯源（WebSocket 推送的事件日志）

### 5.4 执行器抽象（`crates/executors/src/lib.rs`）

```rust
#[async_trait]
pub trait Executor: Send + Sync {
    async fn execute(&self, request: ExecutorRequest)
        -> anyhow::Result<ExecutorResponse>;
    fn validate_config(&self) -> anyhow::Result<()>;
    fn capabilities(&self) -> Vec<BaseAgentCapability>;
    async fn check_availability(&self) -> AvailabilityInfo;
}
```

每种 Agent 实现该 trait，差异主要体现在：
- CLI 命令参数不同（`claude code` vs `codex` vs `gemini`）
- 环境变量注入不同
- 输出解析（`NormalizedEntry`）逻辑不同

### 5.5 前端看板 UI（`packages/web-core/`）

React 前端使用 TypeScript，架构分层清晰：
- **web-core**：共享业务逻辑（状态管理、API 客户端、类型定义）
- **local-web**：本地部署 UI
- **remote-web**：云部署 UI

实时通信采用 WebSocket，支持的消息类型：
- `LOG_ENTRY`：Agent 的实时终端输出
- `TASK_STATUS_UPDATE`：任务状态变更
- `GIT_DIFF`：代码变更对比信息
- `EXECUTION_PROGRESS`：执行进度
- `APPROVAL_REQUEST`：Agent 请求人类确认

### 5.6 类型安全（`crates/api-types/`）

通过 `#[derive(TS)]` 标注 Rust 结构体，利用 `ts-rs` crate 自动生成 TypeScript 类型定义，确保前后端类型一致性。这是一种比 OpenAPI/Swagger 更轻量的"Rust → TypeScript"类型同步方案——没有 YAML 中间表示，直接从 Rust 源码生成 TS 类型。

---

## 6. 全网口碑画像

### 6.1 正面评价

- **定位精准**：多个评测一致认为 Vibe Kanban 切中了 AI 编程时代"人机协作"的核心痛点（知乎、掘金、CSDN）
- **执行力强**：从概念到产品落地速度极快，2025-06 创建，不到一年 27k Stars
- **实用性强**："不是概念炒作，是能用起来的产品"是用户最常给出的评价
- **设计优雅**：Rust + React 的技术选型被认为"适合此类问题领域"
- **Git Worktree 隔离**被广泛称赞为"比 Docker 更聪明的方案"

### 6.2 负面/争议点

- **公司停运（最重要）**：README 已明确标注 "Vibe Kanban is sunsetting"，BloopAI 公司关闭，项目转为社区维护。这是所有潜在用户最应该关注的风险
- **BSL/Apache 2.0 争议**：[注：实际许可证为 Apache 2.0，早期有 BSL 1.1 的传言] 许可证不明确曾引发社区疑虑
- **小任务过重**：单次 Agent 调用（如"修复拼写错误"）也需要创建卡片、写描述、分配 Agent，流程繁琐
- **并行任务管理门槛高**：同时追踪 3-4 个并行任务的上下文对认知要求很高，部分用户反馈"不知道自己到底在 Review 什么"
- **Bug 稳定性**：Mac 上 Merge 按钮偶尔失效、Open in IDE 功能偶尔无响应
- **依赖底层 Agent**：如果 Claude Code 陷入死循环，Vibe Kanban 只能"看"不能"修"
- **缺少国产 Agent 集成**：CSDN 用户指出缺少对 Trae、Baidu Comate、CodeBuddy 等国内工具的支持

### 6.3 社区热度

- **GitHub Discussions**：活跃，多数为功能请求和使用答疑
- **Discord**：官方社区，核心团队参与
- **Show HN**：获大量关注，成为 HN 首页项目
- **知乎/掘金/CSDN**：均有深度评测文章，传播范围广
- **VibeCodingHub**：v0.1.44 版本仍被推荐，社区 Fork 关注度高

### 6.4 关键结论

Vibe Kanban 是一个"产品理念获得广泛认同，但商业化未能走通"的经典案例。它的开源性确保代码将长期可用，但未来迭代依赖于社区 Fork 和维护。

---

## 7. 竞品对比

### 7.1 对比矩阵

| 维度 | Vibe Kanban | Claude Code Task | Codex Auto-run | OpenCode 任务 | Linear/Jira | Plane |
|------|-------------|-----------------|---------------|-------------|------------|-------|
| **定位** | Agent 编排层 | Agent 内建任务 | Agent 内建任务 | Agent 内建任务 | 项目管理 | 项目管理 |
| **Agent 支持** | 10+ 种 | 仅 Claude | 仅 Codex | 仅 OpenCode | 不适用 | 不适用 |
| **隔离机制** | Git Worktree | 无 | 无 | 无 | 不适用 | 不适用 |
| **并发执行** | 多 Agent 并行 | 单任务 | 单任务 | 单任务 | 人工跟踪 | 人工跟踪 |
| **Diff 审查** | 内嵌 + 评论 | 终端 | 终端 | 终端 | 不适用 | 不适用 |
| **Dev Server** | 内置 Browser | 手动 | 手动 | 手动 | 不适用 | 不适用 |
| **部署方式** | 本地/Tauri | CLI | CLI | CLI | SaaS | 自托管 |
| **许可证** | Apache 2.0 | 专有 | 专有 | 专有 | 专有 | Apache 2.0 |
| **公司状态** | **停运** | 活跃（Anthropic） | 活跃（OpenAI） | 活跃 | 活跃 | 活跃 |

### 7.2 核心差异解读

**vs Claude Code / Codex / OpenCode 的内建任务管理**

最直接的竞品其实是各 Agent 自身的任务管理功能（Claude Code 的 Project / Task、Codex 的 Auto-run 模式）。Vibe Kanban 的优势在于：
- **Agent 无关**：不绑定任何 Agent 供应商
- **可视化**：看板 + Diff + Dev Server 一体化
- **并发编排**：真正的多 Agent 并行

劣势在于：
- **额外的抽象层摩擦**：Agent 自身的 CLI 更直接
- **供应商内置集成更好**：Claude Code 对自己的 MCP 配置天然支持更好
- **Agent 厂商可能"绞杀"**：Anthropic/OpenAI/Google 完全可以在自己的产品中内置看板编排功能

**vs Linear / Jira**

Vibe Kanban 和传统项目管理工具**不是替代关系，而是互补关系**：
- Linear/Jira 管"人与人"的任务分配，Vibe Kanban 管"人与 AI Agent"的工作流
- 传统看板没有"执行"语义——卡片状态变化需要人手动拖拽；Vibe Kanban 的状态变化由 Agent 执行触发
- 但 Vibe Kanban 缺乏传统项目管理所需的 Sprint 规划、工时追踪、报表等功能

**vs Plane**

Plane 是目前最成功的开源项目管理工具（Apache 2.0），但与 Vibe Kanban 完全不在同一赛道：
- Plane 是"开源版 Linear"，解决的是团队项目管理问题
- Vibe Kanban 解决的是"AI Agent 工作流管理"问题
- 两者在未来可能的结合点：Plane 作为项目层管理，Vibe Kanban 作为 Agent 执行层

### 7.3 竞品格局展望

Vibe Kanban 停运后，市场上出现了若干类似项目：
- **Claude Squad**：开源的 Claude Code / Codex / OpenCode 多 Agent 管理终端
- **Paseo**：跨设备控制层，支持更多 Agent 类型，AGPL-3.0 开源
- **Parallel Code**：桌面应用，Git Worktree 并行执行

这些项目正在接棒 "Agent Orchestration Layer" 这个赛道，但普遍还处于早期阶段（Stars < 1k），尚未达到 Vibe Kanban 的成熟度。

---

## 8. 核心研判

### 8.1 产品价值判断

**Vibe Kanban 提出了一个正确的命题，但可能过早地来到了市场。**

"AI Agent 需要编排层"这个判断在逻辑上是成立的——当开发者同时使用多个 Agent 时，确实需要一个统一的管理界面。但问题是：
- **当前 Agent 的使用密度**：大多数开发者目前只使用 1-2 个 Agent，编排层的需求尚未形成刚需
- **Agent 的自主性不足**：当前 Agent 还需要频繁的人工确认和介入，"编排"的实际收益被 Agent 自身的低自主性抵消
- **Agent 厂商的挤压**：Claude Code / Cursor 等产品正在快速内建任务管理功能，留给第三方的空间正在收窄

### 8.2 停运原因分析

BloopAI 公司关闭的核心原因应该包括：
1. **商业化困难**：Apache 2.0 开源 + 云服务订阅的混合模式未能找到 Product-Market Fit
2. **市场时机问题**：Agent 编排层的需求尚未成为市场刚需
3. **竞争压力**：Agent 厂商的内建功能会持续侵蚀第三方编排层的价值
4. **融资环境**：AI 工具赛道的融资在 2025-2026 年趋于理性

### 8.3 未来走向预测

**短期（6-12 个月）**：
- 社区 Fork 活跃，2-3 个主要的 Fork 分支可能出现
- 部分功能被 Agent 厂商（尤其是 Claude Code 和 Cursor）吸收
- "Agent Orchestration Layer" 被证明为过渡性品类

**中期（1-2 年）**：
- 随着 Agent 的自主性提升（One-shot 成功率 > 90%），编排层的需求反而会降低——因为 Agent 不再需要频繁的人类介入
- 看板 + Agent 深度整合可能被 IDE（VS Code / Cursor / JetBrains）原生吸收

**长期（3 年+）**：
- 编排层作为独立品类存在的价值存疑
- 更可能演变为 IDE 插件、CI/CD 集成组件等嵌入形态
- Vibe Kanban 的"Git Worktree 隔离 + 并发编排 + 内联审查"设计模式将成为行业标准，但以组件形式存在于其他产品中

### 8.4 对从业者的建议

- **学习思路而非代码**：Vibe Kanban 的最大价值不是可直接运行的代码，而是"Agent 编排层"的设计思路
- **关注 Git Worktree 隔离方案**：这是最值得复用的工程实践
- **不要轻视人机交互设计**：Vibe Kanban 在"如何让人类高效审查 Agent 输出"上的设计（Diff + 内联评论 + Follow-up）比大多数 Agent 工具做得好
- **商业化需谨慎**：在 Agent 编排层这个品类上直接 SaaS 商业化的风险很高

---

## 9. 关键文件路径速查

| 路径 | 说明 |
|------|------|
| `Cargo.toml` | Rust 工作空间配置，定义所有 crate |
| `crates/server/src/main.rs` | Axum 服务入口 |
| `crates/server/src/routes/tasks.rs` | 任务路由（创建、执行、状态查询） |
| `crates/services/src/container.rs` | Container 编排逻辑（Worktree 创建/清理） |
| `crates/services/src/git_worktree.rs` | Git Worktree 管理器 |
| `crates/executors/src/lib.rs` | `Executor` trait 定义（Agent 抽象层核心） |
| `crates/executors/src/executors/claude.rs` | Claude Code 执行器实现 |
| `crates/db/src/models.rs` | 数据库模型定义（projects, tasks, workspaces 等） |
| `crates/db/src/msg_store.rs` | WebSocket 实时消息存储 |
| `crates/api-types/src/lib.rs` | 共享类型定义（`#[derive(TS)]`） |
| `crates/git/src/service.rs` | Git 操作封装（git2） |
| `crates/local-deployment/src/lib.rs` | 本地部署生命周期管理 |
| `crates/tauri-app/src/main.rs` | Tauri v2 桌面应用入口 |
| `npx-cli/bin/cli.js` | NPM 分发入口，提取并启动二进制 |
| `packages/web-core/src/types.ts` | 前端类型定义（TaskStatus 等） |
| `packages/web-core/src/hooks/useWebSocket.ts` | WebSocket 连接管理 |
| `packages/local-web/src/App.tsx` | 本地 Web UI 入口 |
| `AGENTS.md` | AI Agent 配置文件 |
| `CLAUDE.md` | Claude Code 配置（Workbuddy 类似） |
| `LICENSE` | Apache 2.0 许可证 |
| `docker-compose.yml` | Docker 部署（远程/云模式） |

---

*报告结束 - 调研日期：2026-06-29*
*重要提示：报告调研时，BloopAI 公司已关闭，Vibe Kanban 项目状态为 "sunsetting"，请读者自行评估使用风险。*
