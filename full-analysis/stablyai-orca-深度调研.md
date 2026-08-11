# stablyai/orca 深度调研报告

> 调研日期：2026-08-12 ｜ 星标：42,566 ⭐ ｜ 协议：MIT ｜ 语言：TypeScript(主) ｜ 默认分支：main ｜ 创建：2026-03-17

## 一、项目定位

**Orca 是"为百倍开发者准备的 AI 编排器（ADE）"**——把 Codex、Claude Code、OpenCode、Pi 等任意 CLI 编码 Agent 并排运行，每个 Agent 跑在**各自的 git worktree** 里，在一个桌面/移动/VPS 统一的界面里集中追踪、对比与合并，是 Agent 并行化工作流的新兴基础设施。

## 二、项目亮点

1. **并行 Worktree 编排**：一条 prompt 扇出 5 个 Agent，各自隔离在独立 git worktree，结果可对比、优胜者一键合并——把"多 Agent 试错"工程化。
2. **任意 CLI Agent 即插即用**：官方列出 30+ 兼容 Agent（Claude Code/Codex/Cursor/Grok/OpenCode/Pi/Devin/Goose…），"能在终端跑就能进 Orca"，BYOK（用自己的订阅）。
3. **桌面 + 移动 + VPS 三位一体**：桌面 App（macOS/Win/Linux）、手机 companion（iOS/Android，远程监控与追加指令）、headless Linux Server（`orca serve`）。
4. **Design Mode / Computer Use**：点击真实 Chromium 窗口的 UI 元素，把 HTML/CSS/截图直送 Agent prompt；内置 Computer Use 让 Agent 操作桌面应用。
5. **Agent 原生集成 GitHub & Linear**：应用内浏览 PR/Issue/看板，从任务直接开 worktree 评审，零上下文切换；并自带 8 个内建 Agent 技能。

## 三、核心架构

```
orca/
├── src/
│   ├── main/         # Electron 主进程：窗口/生命周期/系统托盘
│   ├── renderer/      # 前端 UI（React + Vite + Tailwind，components.json 提示 shadcn）
│   ├── cli/           # orca CLI：worktree create / snapshot / click / fill（Agent 可驱动 Orca）
│   ├── preload/       # Electron preload 桥
│   ├── relay/         # 代理/中继层（连接 Agent 进程与 UI）
│   ├── shared/        # 跨进程共享类型与工具
│   └── types/         # 全局 TS 类型
├── skills/            # 8 个内建 Agent 技能（computer-use / linear-tickets / orca-cli /
│   │                    orca-emulator / orca-emulator-android / orca-linear /
│   │                    orca-per-workspace-env / orchestration）
├── native/            # OS 原生模块：computer-use-{linux,macos,windows} / notification-status-macos / windows-cli-launcher
├── mobile/            # 移动端 companion（Swift/Kotlin）
├── docs/              # 多语言文档（含中文/日/韩/西/法/葡）
├── orca.yaml          # 配置文件
└── package.json       # pnpm monorepo（pnpm-workspace.yaml）
```

**核心抽象**：Orca 不是又一个 Agent，而是**Agent 的"驾驶舱"**——它用 Electron 承载多终端（Ghostty 级 WebGL 渲染、无限分屏、重启保留滚动缓冲），把每个 Agent 进程包进独立 worktree，通过 `relay/` 层在 UI 与 Agent 之间传递上下文（含 Design Mode 抓取的 DOM 截图）。`skills/` 目录则让 Orca 自身也能被 Agent 脚本化（`orca worktree create` 等 CLI）。

## 四、应用场景与启发

- **并行试错降本**：同一需求扇出多个 Agent 各自实现，人只做"选最优合并"，把单线程编码变批处理。
- **移动端远程驾驭**：手机 companion 让开发者通勤中也能监控/追加 Agent 指令，契合"异步 Agent 工作流"。
- **对 Agent 基础设施的启发**：Orca 印证了"**Agent 编排层 = 终端复用 + worktree 隔离 + 上下文富化（DOM/截图/GitHub/Linear）**"这一新兴范式。我们仓库中 `farion1231/cc-switch`（统管 7 款 Coding Agent）、`accomplish-ai/coworker`（本地优先 Agent 编排）是同一赛道的不同切面。
- **风险点**：worktree 并行会放大磁盘/分支管理复杂度；多 Agent 并发消耗大量 token 与 API 配额；移动端 companion 与桌面状态同步是工程难点。

## 五、源码深度解读

### 5.1 内建技能目录（skills/）
```text
skills/
├── computer-use/        # 让 Agent 操作桌面 UI（调用 native/computer-use-*）
├── linear-tickets/      # 从 Linear 任务拉上下文开 worktree
├── orca-cli/            # Orca 自身 CLI 技能（worktree/snapshot/click/fill）
├── orca-emulator/       # 本地 Android/iOS 模拟器驱动
├── orca-emulator-android/
├── orca-linear/         # GitHub/Linear 双向同步
├── orca-per-workspace-env/  # 每 worktree 独立环境变量
└── orchestration/       # 多 Agent 编排原语
```
洞察：`skills/` 与 `native/` 分离，使"Agent 能做什么"与"OS 如何执行"解耦——这是 Orca 可跨 macOS/Win/Linux 落地 Computer Use 的关键（各平台实现在 `native/`）。

### 5.2 src/ 分层（relay + main + renderer）
```text
src/main/    # Electron 主进程：窗口管理、生命周期、Native 模块加载
src/renderer/# React UI：worktree 看板、终端分屏、diff 标注
src/relay/   # 中继：把 Agent stdout、Design Mode 截图、GitHub/Linear 事件汇入 UI
src/cli/     # orca 命令：让外部 Agent 脚本化操控 Orca 自身
```
洞察：`relay/` 是"上下文富化中枢"——它把分散的信号（终端、截图、工单）归一后喂给 Agent，正是 Orca 区别于纯终端复用器的地方。

### 5.3 配置即 `orca.yaml`
仓库根 `orca.yaml` + `pnpm-workspace.yaml` 表明 Orca 以 pnpm monorepo 组织，配置驱动行为，便于团队按 workspace 注入环境变量（`orca-per-workspace-env` 技能）。

## 六、社区口碑

- **地位**：42k+ ⭐、2.9k forks，2026-03 才创建即飙红，是"Agent 编排/IDE"赛道增长最快的新星之一（topic 含 `yc-backed`，Stably AI YC 背景）。
- **评价基调**：正面为主——"终于有人把多 Agent 并行做成了产品""移动端远程驾驭很香"。吐槽集中在早期版本稳定性、移动端 APK 仍 0.0.x 早期、部分 Agent 适配需打磨。
- **工程信号**：MIT、Electron + pnpm monorepo、多语言文档、每日 ship（`changelog` 即功能列表）、`orca serve` headless 支持服务器部署，迭代极其活跃（最新 `v1.4.180`）。

## 七、竞品对比 + 核心研判

| 维度 | Orca | Claude Code (原生) | OpenCode | Devin |
|---|---|---|---|---|
| 并行 Agent | ✅ worktree 扇出 | 单线(可 worktree 手搓) | 单线 | 多 Agent |
| 桌面/移动 | ✅ 桌+移+VPS | CLI/桌 | CLI/桌 | 云 |
| 任意 Agent | ✅ 30+ | 仅自身 | 自身+插件 | 自有 |
| 定位 | Agent 编排舱 | 单 Agent | 开源 Agent | 自主工程师 |

**核心研判**：
- **优势**：把"多 Agent 并行 + 跨端监控 + 富上下文"做成开箱产品，BYOK 模式零锁定，兼容最广。
- **风险**：与上游 Agent（Claude Code/Codex）强耦合，随其 CLI 变更需持续适配；并行 token 成本高；产品仍早期。
- **趋势**：Agent 基础设施正从"单个更强"转向"编排更多"——Orca 站在这条曲线的早期红利位。
- **启发**：做 Agent 工具时，"**不造 Agent、只造 Agent 的驾驶舱**"是低风险高杠杆的切入点；worktree 隔离 + 上下文富化是可复用的核心范式。

## 八、关键文件速查

- `src/main/` — Electron 主进程（窗口/生命周期）
- `src/renderer/` — React UI（worktree 看板/终端分屏）
- `src/relay/` — 上下文富化中继层
- `src/cli/` — `orca` CLI（Agent 可驱动 Orca）
- `skills/` — 8 个内建 Agent 技能
- `native/` — OS 原生 Computer Use 实现（linux/macos/windows）
- `orca.yaml` / `pnpm-workspace.yaml` — 配置与 monorepo 定义
- `mobile/` — 移动端 companion（iOS/Android）
