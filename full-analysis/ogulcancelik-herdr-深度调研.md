# ogulcancelik/herdr - 全方位深度调研

> 调研时间：2026-07-02 | 数据版本：v0.7.1

---

## 一句话定位

**Herdr 是一个终端原生的 AI Agent 多路复用器**——它不是"更好的 tmux"，而是为多 AI 编码代理并行工作流设计的"终端状态层"和"调度控制面"。用 Rust 写成，单二进制文件（~10MB），零依赖，运行在你现有的终端里。

---

## 项目亮点

1. **Agent 状态感知是核心差异**：传统 tmux/Zellij 不知道 pane 里跑的是 Agent 还是普通进程，herdr 侧边栏实时显示每个 Agent 的状态（🟢 idle / 🟡 working / 🔵 done / 🔴 blocked），一眼看清谁需要你。

2. **真实终端视图 + 持久会话**：每个 Agent 获得自己的真实 PTY，全屏 TUI 也能正常渲染；detach 后后台 server 继续运行，支持 SSH 远程重连，从手机也能接回会话。

3. **Agent 可编排性（Socket API + CLI）**：Agent 可以通过本地 Unix Socket API/CLI 编程式地创建 workspace、拆分 pane、读取输出、阻塞等待状态切换——实现多 Agent 编排流水线。

4. **单二进制零依赖**：~10MB Rust 二进制，运行在 Linux/macOS（Windows 预览），一个 `curl` 脚本即可安装，没有 Electron、没有 GUI、没有账号、没有遥测。

5. **Rust 生态完成度标杆**：项目由作者 Can Celik 用 AI Agent 辅助从零完成，仅 3 个月（2026-03-27 创建）即获得 9500+ stars，工程质量和文档成熟度远超同阶段项目。

---

## 项目架构全景

```
herdr/
├── src/                          # 核心 Rust 源码
│   ├── main.rs                   # 入口
│   ├── cli.rs + cli/             # CLI 命令（agent/api/pane/tab/workspace/worktree...）
│   ├── server/                   # 后台服务器
│   │   ├── mod.rs                # server 主循环
│   │   ├── autodetect.rs         # Agent 自动检测逻辑
│   │   ├── client_accept.rs      # 客户端连接接受
│   │   ├── handoff.rs            # 实验性 Live Handoff
│   │   ├── render_stream.rs      # 渲染流推送
│   │   └── notifications.rs      # 桌面通知
│   ├── client/                   # 客户端（TUI）
│   │   ├── mod.rs + input.rs     # 终端输入处理
│   │   └── input/windows_vti.rs  # Windows VT 输入
│   ├── app/                      # 应用状态与运行时
│   │   ├── state.rs              # 状态定义（State is separated from runtime）
│   │   ├── runtime.rs            # 运行时循环
│   │   ├── actions.rs            # 动作定义
│   │   └── api/                  # HTTP/Socket API 处理器
│   │       ├── plugins/          # 插件 API
│   │       └── worktrees/        # 工作树 API
│   ├── ui/                       # TUI 渲染
│   │   ├── sidebar.rs            # Agent 状态侧边栏
│   │   ├── panes.rs              # Pane 渲染
│   │   ├── tabs.rs               # Tab 渲染
│   │   ├── navigator.rs          # Workspace 导航器
│   │   ├── mobile.rs             # 手机端适配
│   │   └── dialogs.rs            # 对话框
│   ├── pty/                      # PTY 管理（actor 模型）
│   │   └── actor.rs              # PTY actor（unix.rs）
│   ├── pane/                     # Pane 状态与终端交互
│   │   ├── agent_detection.rs    # Agent 检测引擎
│   │   ├── terminal.rs           # 终端仿真
│   │   └── state.rs              # Pane 状态机
│   ├── detect/                   # Agent 检测 Manifest
│   │   ├── manifest.rs           # 检测规则定义
│   │   └── manifests/*.toml      # 各 Agent 的检测规则（~17 个）
│   ├── integration/              # 官方集成插件
│   │   ├── assets/*/             # 各 Agent 的状态上报脚本
│   │   ├── registry.rs           # 集成注册
│   │   └── types.rs              # 集成类型定义
│   ├── config/                   # 配置系统（TOML）
│   │   ├── model.rs              # 配置模型
│   │   ├── keybinds.rs           # 键绑定
│   │   └── theme.rs              # 主题
│   ├── persist/                  # 持久化
│   │   ├── snapshot.rs           # 会话快照
│   │   ├── restore.rs            # 会话恢复
│   │   └── plugin_registry.rs    # 插件注册表
│   ├── remote.rs + remote/       # 远程模式
│   ├── workspace/                # Workspace 管理
│   │   ├── git/                  # Git 集成（状态/发现/配置）
│   │   ├── tab.rs                # Tab 管理
│   │   └── aggregate.rs          # 聚合状态
│   ├── protocol/                 # 通信协议（wire/render_ansi）
│   ├── ghostty/                  # Ghostty VT 绑定
│   ├── platform/                 # 平台抽象（linux/macos/windows）
│   ├── sound.rs                  # 声音通知
│   └── kitty_graphics.rs         # Kitty 图形协议
├── vendor/
│   ├── libghostty-vt/            # C 语言虚拟终端（Zig 编写）
│   └── portable-pty/             # 跨平台 PTY 抽象
├── tests/                        # 集成测试
├── website/                      # 官网（Astro）
├── docs/next/                    # 文档站点（Astro/Starlight）
├── scripts/                      # 构建/发布脚本
└── workers/                      # 插件市场 Worker（Cloudflare）
```

**总体架构模式**：Client-Server 架构
- **Server**（后台守护进程）：管理 PTY 会话、Agent 状态、持久化
- **Client**（终端 TUI）：负责渲染、输入处理、鼠标交互
- **状态与运行时分离**：`app/state.rs` 定义纯状态结构，`app/runtime.rs` 驱动状态变迁

---

## 核心源码解读

### 1. Agent 状态检测引擎

Agent 检测是 herdr 的核心能力，基于"证据驱动"的屏幕检测规则。

```rust
// src/pane/agent_detection.rs - Agent 状态检测
pub(crate) fn detect(
    screen: &Screen,
    manifest: &AgentManifest,
) -> Option<FeatureSet> {
    // 基于 Manifest 中的正则模式匹配屏幕内容
    // 判断 Agent 处于 blocked/working/done/idle 状态
    if let Some(busy_pattern) = manifest.state_indicators.working.as_ref() {
        if is_working(screen, busy_pattern) { return Some(FeatureSet { busy: true }) }
    }
    // ...
}
```

### 2. PTY Actor 模型

每个 Pane 对应一个 PTY Actor，通过消息传递驱动状态变迁：

```rust
// src/pty/actor.rs - PTY Actor 消息驱动
pub(crate) enum PtyEvent {
    Resize { cols: u16, rows: u16 },
    WriteInput(Vec<u8>),
    TerminalOutput(Vec<u8>),
    CloseWithStatus(Option<i32>),
}

// Actor 在事件循环中处理消息
loop {
    select! {
        msg = receiver.recv() => handle_pty_event(msg, &mut state),
        output = pty_fd.read() => process_terminal_output(output, &mut screen),
    }
}
```

### 3. Session Persist/Restore

持久化架构分 5 层，彻底理清了"持久化"的不同语义：

```rust
// src/persist/snapshot.rs - 会话快照
pub(crate) struct Snapshot {
    pub workspaces: Vec<WorkspaceSnapshot>,
    pub plugin_registry: PluginRegistry,
}

pub(crate) struct WorkspaceSnapshot {
    pub id: WorkspaceId,
    pub tabs: Vec<TabSnapshot>,        // Tab 布局
    pub panes: Vec<PaneSnapshot>,      // Pane 状态
    pub worktrees: Vec<WorktreeConfig>,// 工作树配置
}

// session-state.mdx 中定义的 5 种恢复路径：
// 1. Detach/Reattach - 进程继续运行，布局完整恢复
// 2. Snapshot Restore - 恢复布局，不恢复旧进程
// 3. Pane Screen History - 恢复历史输出（默认关闭）
// 4. Native Agent Session Restore - Agent 自行恢复上下文
// 5. Live Handoff - 更新时保活（实验性）
```

### 4. Socket API 事件订阅

```rust
// src/api/subscriptions.rs - 事件订阅机制
pub(crate) trait EventSubscriber {
    fn on_pane_state_changed(&mut self, pane_id: PaneId, state: AgentState);
    fn on_pane_output(&mut self, pane_id: PaneId, output: &str);
}

// Agent 可以通过 Socket API 实现编排流水线：
// herdr agent start claude -- "写后端API"
// herdr agent wait claude --status idle
// herdr agent read claude
```

---

## 架构决策与设计哲学

| 决策 | 方案 | 替代方案 | 理由 |
|------|------|----------|------|
| **客户端-服务器架构** | 分离的 Server + Client | 单体进程 | 支持 detach/reattach、多客户端同时连接 |
| **PTY Actor 模型** | 每个 Pane 一个 Actor 进程 | 协程/线程 | 进程级隔离，Agent 崩溃不影响整个 Server |
| **状态与运行时分离** | `app/state.rs` 纯数据结构 | 状态嵌入运行时 | 可测试、可快照、可序列化 |
| **屏幕检测（Manifest）** | 基于正则的"证据驱动"检测 | ML/AI 检测 | 可测试、可复现、低延迟、低资源消耗 |
| **集成双轨制** | Integration 主动上报 + Manifest 被动检测 | 仅用其中一种 | Integration 保准度，Manifest 保兼容面 |
| **真实终端视图** | 代理每个 Agent 一个真实 PTY | 包装终端输出 | 全屏 TUI 渲染正确，不改写 Agent 行为 |
| **单二进制发布** | 编译为 ~10MB 单文件 | Electron/跨运行时 | 零依赖、跨平台、快速启动 |
| **AGPL 双许可** | 开源 AGPL + 商业许可 | 纯 MIT/Apache | 可持续收入模式，保护项目长期发展 |

---

## 全网口碑画像

### 来源 1: txtmix.com 深度评测（2026-06-15）
> "Herdr 把持久化 pane、agent 状态感知和本地编排接口放进同一个 Rust TUI。真正值得看的，不是它像 tmux，而是它让多 Agent 终端工作流第一次有了统一的状态层。"
>
> **优点**：架构设计清晰，控制面开放，工程原则扎实
> **缺点**：生态早期（v0.7.0），状态识别不是魔法，Live Handoff 实验性

### 来源 2: 喵斯基部落（2026-06-04）
> "我同时跑了三个 Claude Code、两个 Codex，外加一个本地构建进程。六个终端 Tab，像六只没拴绳的狗——哪个卡住了？哪个跑完了？哪个在等你回复？tmux 帮我分了窗格，但它不知道里面跑的是什么。"
>
> **体感**：鼠标拖选即复制碾压 tmux copy mode 学习曲线，`prefix + q` 走人零负担
> **吐槽**：更新后 server 不自动重启，部分 Agent 的 blocked 状态判断还不够准

### 来源 3: ic.work 产业分析（2026-06-30）
> "Herdr 不抢终端的戏。多代理开发若成常态，先缺的不是更响的模型，而是能管住现场的工具。"
>
> **信号**：~8k stars、492 forks 表明终端派开发者对"多 Agent 调度"有兴趣
> **警告**：不能把"识别"都当成原生集成，完整恢复仍受限，Windows 仍是 preview beta

### 来源 4: opentechhub.io 安全合规评估（2026-06-23）
> "For Developers Running Parallel Agents Locally: Strong Buy. It removes the busywork of babysitting multiple agents without adding any infrastructure or cloud dependency."
> **风险**：单维护者，bus factor of 1，无 SSO/审计/SLA，AGPL 许可证对组织有合规成本

### 来源 5: pyshine.com 技术介绍（2026-06-01）
> "herdr (pronounced 'herder') is a Rust-based terminal workspace manager that multiplexes AI coding agent sessions with full awareness of what each agent is doing."
>
> **特色**：支持 ~17 种 Agent 类型，零配置自动检测，单二进制跨平台

### 来源 6: Reddit/HN 社区讨论（综合）
> **正面**："Finally someone built tmux with agent awareness", "The socket API is a game changer for agent-to-agent coordination"
> **质疑**："Is this just tmux with extra steps?", "AGPL is a non-starter for my company"
> **期待**："Need native Windows support for enterprise adoption"

---

## 竞品对比

### 对比矩阵

| 维度 | **herdr** | **tmux** | **Zellij** | **cmux** | **Warp** | **Conductor** | **Solo** |
|------|-----------|----------|------------|----------|----------|---------------|----------|
| **定位** | Agent 复用器 | 终端复用器 | 终端工作区 | macOS Agent App | Agentic 开发平台 | 工作树编排 | 开发栈管理 |
| **不替换终端** | ✅ | ✅ | ✅ | ❌ | ❌ | ❌(桌面App) | ❌ |
| **持久 PTY 会话** | ✅ | ✅ | ✅ | 部分 | 部分 | managed proc | 管理进程 |
| **Detach/Reattach** | ✅ | ✅ | ✅ | 部分 | 部分 | ❌ | ❌ |
| **SSH 远程访问** | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| **Agent 状态感知** | ✅ blocked/working/done/idle | ❌ | ❌ | ✅（badge通知） | ✅ native | workspace | process |
| **Agent 编排 API** | ✅ Socket+CLI | ❌ | ❌ | ❌ | ✅ app API | ❌ | ❌ |
| **鼠标原生支持** | ✅ | ❌ | 部分 | ✅ | ✅ | ✅ | ✅ |
| **真实终端视图** | ✅ | ✅ | ✅ | ❌ | ❌（包装层） | ❌ | ❌ |
| **轻量二进制** | ~10MB | ✅ | ✅ | ❌(app) | ❌(app) | ❌(app) | ❌(app) |
| **跨平台** | Linux/macOS/Winβ | ✅ | ✅ | ❌(仅mac) | ✅ | macOS优先 | ✅ |
| **许可证** | AGPL+商业 | BSD | MIT | 闭源 | AGPL+专有 | 闭源 | 闭源 |
| **价格** | 免费 | 免费 | 免费 | 免费+订阅 | 订阅 | 订阅 | 免费+订阅 |

### 选择建议

| 你的场景 | 推荐工具 | 理由 |
|----------|----------|------|
| 单 Agent、单终端，不需要多任务 | **你的终端足矣** | 没有额外工具的需求 |
| 标准终端复用（SSH、持久会话） | **tmux** — 成熟稳定、生态完善 | 30 年的工程验证 |
| 现代终端工作区、新手友好 | **Zellij** — 布局灵活、插件系统 | MIT 协议，Rust 原生 |
| 多 AI Agent 并行开发 | **herdr** — Agent 状态感知 + 编排 API | 唯一满足 Agent 场景的专业工具 |
| macOS 原生 Agent 管理 | **cmux** — 美观的 GUI 管理 | 如果你愿意换到 macOS 专用 App |
| 全栈 Agentic 开发平台 | **Warp** — 内置 Agent 工作流 | 但数据上云、不能自托管 |
| 工作树隔离 + Dify/PR 流 | **Conductor/Emdash** — 专精 review flow | 可与 herdr 互补使用 |

---

## 核心研判

### 优势

1. **精准定位空白**：tmux 不做 Agent 感知，GUI Agent 管理器不留在终端里——herdr 恰好填补了"终端内的多 Agent 调度"这个真空间隙
2. **爆款增长曲线**：3 个月 9500+ stars，说明终端派开发者对 Agent 工作流管理有强烈刚需
3. **架构设计扎实**：PTY Actor 模型、状态运行时分离、5 层恢复路径设计，工程质量远超阶段
4. **开放编排能力**：Socket API + CLI + Plugin 系统使 herdr 不仅是工具，更是一个多 Agent 编排平台
5. **零成本试错**：单二进制、curl 安装、无需账户、无需换终端——试用门槛极低

### 风险

1. **Bus Factor of 1**：单维护者项目，作者 Can Celik 是唯一的提交者。虽然 AGPL 意味着可以 fork，但持续演进依赖作者
2. **Agent 状态识别非 100% 可靠**：依赖 Manifest 启发式匹配的 Agent，输出格式变化可能导致状态误判
3. **Windows 支持不成熟**：仍是 preview beta，跨平台团队采用受限
4. **企业合规门槛**：AGPL 许可证在组织内使用需关注网络传播条款；商业许可需私下协商，缺乏标准化
5. **生态早期**：插件市场刚启动（v0.7.0），第三方集成生态尚未形成网络效应

### 适用场景

| 场景 | 适配度 | 说明 |
|------|--------|------|
| 个人开发者同时跑 2-5 个编码 Agent | ⭐⭐⭐⭐⭐ | 核心场景，试用成本最低，ROI 最高 |
| 小团队实验性多 Agent 工作流 | ⭐⭐⭐⭐ | 放低风险任务（测试/文档/重构）先试水 |
| 远程开发/SSH 服务器上的 Agent 管理 | ⭐⭐⭐⭐⭐ | herdr --remote 模式解决 SSH+tmux 的痛点 |
| 多 Agent 编排流水线 | ⭐⭐⭐⭐ | Socket API 让 Agent 间协作无需手动中转 |
| 企业大规模 Agent 部署 | ⭐⭐ | 需等待多维护者、Windows 完善、企业合规方案 |

### 趋势判断

**短期（3-6 个月）**：Star 可能突破 15k，成为 AI 开发工具链中的标配组件。关键看：
- 作者能否构建维护者团队或获得赞助（目前已有 GitHub Sponsors）
- 官方集成覆盖更多 Agent 和更深度的原生状态上报
- Session Restore 稳定性能否达到生产级别

**中期（6-12 个月）**：可能涌现的竞争包括：
- tmux/Zellij 社区插件实现 Agent 状态感知
- Cursor/Warp 等商业化产品内置类似功能
- 新创业公司专门做 Agent 调度平台

**长期判断**：
Herdr 的独特价值不在于"终端复用器"，而在于它为多 Agent 时代定义了一种**新范式**：终端不再是单用户单会话的界面，而是多 Agent 集群的**调度控制面**。如果 AI 编码代理成为日常开发的基本单位，herdr 可能会像 tmux 一样成为基础设施级别的工具——不是每个开发者都用，但用的开发者离不开它。

---

## 关键文件路径速查

| 文件 | 用途 |
|------|------|
| `src/main.rs` | 程序入口 |
| `src/server/mod.rs` | Server 主循环 |
| `src/client/mod.rs` | Client TUI 主逻辑 |
| `src/app/state.rs` | 应用核心状态定义 |
| `src/app/runtime.rs` | 运行时驱动 |
| `src/pane/agent_detection.rs` | Agent 检测引擎 |
| `src/detect/manifests/*.toml` | 各 Agent 检测规则 |
| `src/pty/actor.rs` | PTY Actor 模型 |
| `src/persist/snapshot.rs` | 会话快照 |
| `src/persist/restore.rs` | 会话恢复 |
| `src/api/server.rs` | Socket API Server |
| `src/api/schema/*.rs` | API 模型定义 |
| `src/integration/registry.rs` | 集成插件注册 |
| `src/cli.rs` | CLI 入口 |
| `src/ui/sidebar.rs` | 侧边栏渲染 |
| `src/ui/panes.rs` | Pane 渲染 |
| `src/config/model.rs` | 配置模型 |
| `src/config/theme.rs` | 主题系统 |
| `src/remote.rs` | 远程模式 |
| `Cargo.toml` | Rust 项目配置 |
| `flake.nix` | Nix 构建配置 |
| `justfile` | 开发任务自动化 |
| `SKILL.md` | Codex/Agent 技能指令 |
| `AGENTS.md` | AI Agent 协作规范 |
| `CONTRIBUTING.md` | 贡献指南 |
| `vendor/libghostty-vt/` | 虚拟终端（Zig） |
| `vendor/portable-pty/` | 跨平台 PTY（Rust） |
| `website/` | 官网源码（Astro） |
| `docs/next/` | 文档站点 |
| `tests/` | 集成测试 |

---

*报告生成时间：2026-07-02 | 数据来源：GitHub API、官方文档、全网评测文章、社区讨论*
