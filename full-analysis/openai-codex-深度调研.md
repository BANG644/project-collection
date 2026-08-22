# 🔬 openai/codex - 全方位深度调研

> 调研日期：2026-08-23 | Stars：⭐ 112,897 | 语言：Rust（核心）/ TypeScript（CLI 壳）| 协议：Apache-2.0 | 默认分支：main

## 📌 一句话定位
OpenAI 出品的终端编码 Agent（Codex CLI），以「**沙箱优先 + 长程无人值守自主执行**」为核心哲学——本地 Rust 运行时负责把每个工具调用关进 OS 级隔离沙箱，云端 Codex Web / Cloud Tasks 负责异步跑长任务并自动开 PR，同一套 Agent 逻辑在 CLI / IDE / 云三端复用，且代码完全开源可审计。

## ⭐ 项目亮点
- **沙箱优先（Sandbox-first）**：OS 级隔离是第一等公民。`sandboxing` / `linux-sandbox`（基于 Bubblewrap `bwrap`）/ `windows-sandbox-rs` / `execpolicy` 共同构成从 read-only 探查、workspace 写入到 full-access 的多级执行策略，**每个 shell 命令都可单独审批**——这是它和 Claude Code「approval-prompt 为主」最本质的架构差异。
- **长程自主（Goal mode）**：可无人值守跑数百到上千次工具调用（官方演示过 1000+ 顺序调用不中断），适合「丢一个任务、几小时后回来看 diff」的工作流。
- **三形态统一**：同一 agent 逻辑覆盖本地 CLI、IDE 扩展、云端 Codex Web / Cloud Tasks（异步开 PR），`cloud-tasks` / `cloud-tasks-client` 两个 crate 专门承载云端任务编排。
- **真开源、可自托管**：Apache-2.0，可用自己的 API key 跑，代码可审计——相比闭源的 Claude Code 是结构性优势。
- **ChatGPT 订阅即免费用**：Plus / Pro / Business / Edu / Enterprise 直接 `Sign in with ChatGPT`，无需另购；也支持 API key 按 token 计费。

## 🏗️ 项目架构全景
### 目录结构与设计哲学
仓库是「Rust 核心 + TS/JS CLI 壳 + SDK」三件套，最外层 `codex-cli`（CLI 壳）、`codex-rs`（Rust 核心 monorepo）、`sdk`（可嵌入 SDK）、`docs`。

`codex-rs` 是一个 **~90 crate 的 Cargo workspace**，按职责高度模块化。关键 crate 群：

```
codex-rs/
├── core/            # Agent 主循环（loop / turn / tool dispatch）
├── core-api/        # 与 OpenAI Responses API 的桥接契约
├── codex-api/       # endpoint/responses.rs, realtime_websocket/* 流式协议
├── sandboxing/      # 沙箱抽象层
├── linux-sandbox/   # Bubblewrap(bwrap) 实现
├── windows-sandbox-rs/  # Windows 沙箱实现
├── execpolicy/      # 执行策略（权限分级 + 逐命令审批）
├── codex-mcp/ + mcp-server/ + rmcp-client/  # MCP 集成（含 Rust MCP 客户端）
├── skills/          # 项目内 SKILL.md 技能加载
├── cloud-tasks/ + cloud-tasks-client/       # 云端任务编排（开 PR）
├── code-mode/ + code-mode-host/ + code-mode-runtime/  # 编码 Agent 模式
├── app-server/ + app-server-daemon/         # 桌面 App 守护进程
├── chatgpt/ + model-provider/ + login/     # 鉴权与后端选择
├── hooks/ + tui/ + apply-patch/ + exec/ + shell-command/  # 工具与交互层
└── secrets/ + keyring-store/                # 凭据管理
```

设计哲学：**沙箱是默认姿态，自主是可选开关**。Agent 循环（core）只负责「思考→调用工具→观察」，而「工具到底在什么隔离级别跑」由 `sandboxing` + `execpolicy` 决定——把安全边界从「靠用户每次点确认」升级为「靠 OS 隔离 + 策略矩阵」。

### 技术栈与依赖
- 核心：Rust（Cargo workspace，Bazel 辅助构建 `BUILD.bazel`），`bwrap` 作 Linux 沙箱后端。
- 后端：OpenAI Responses API（`codex-api/src/endpoint/responses.rs` 是主入口），支持 GPT-5.5 / o 系列推理模型；也支持 Ollama / LM Studio 本地模型（`ollama` / `lmstudio` crate）。
- 扩展：MCP（`codex-mcp`）、SKILL.md 技能（`skills` crate）、Hooks（`hooks` crate）。
- 鉴权：`chatgpt` crate 处理 `Sign in with ChatGPT`，`login` / `keyring-store` 管理本地 token。

## 💡 应用场景与启发（重点章节）
### 典型使用场景
- **OpenAI 技术栈团队跑无人值守长任务**：把「修这个 bug / 给模块补测试」丢给 Cloud Tasks，它跑完直接开 PR，你继续干别的。
- **安全敏感工作流**：需要让 Agent 跑不可信操作（如执行爬虫脚本、处理外部输入）时，OS 级沙箱比「信任 + 事后确认」更稳。
- **自建私有 Codex**：用自己企业的 OpenAI 兼容 endpoint，在隔离环境跑编码 Agent。

### 可借鉴的解决方案模式
1. **「沙箱即策略」而非「沙箱即提示」**：把执行边界做成 `execpolicy` 这样的结构化枚举（read-only → edit → full），而不是靠 system prompt 叮嘱 Agent「别乱动」——后者在长程自主里必然失效。
2. **云端/本地双运行时同源**：`cloud-tasks` 与本地 `core` 跑同一套 Agent 逻辑，只是执行后端不同。同类产品（编码 Agent、RPA、评测 harness）都可用「core 抽象 + 多 backend」避免维护两套代码。
3. **SKILL.md 跨 Agent 可移植**：Codex CLI 与 Claude Code / Gemini CLI / Cursor 共用 `SKILL.md` 开放标准——技能资产不再锁死在单一 harness。

### 同类需求的可参考思路
- 如果你在做「让 LLM 安全执行 shell」的产品，直接抄 `linux-sandbox`（bwrap 命名空间隔离）+ `execpolicy`（分级审批）的组合，比造轮子可靠。
- 长程 Agent 的「断点续跑 / 进度可见」可参考 `cloud-tasks` 的任务状态机设计。

## 🧠 核心源码解读（克制代码量）
### 1. 沙箱执行策略（`execpolicy` + `linux-sandbox`）
沙箱不是事后补丁，而是工具调用链的前置关卡。`execpolicy` 定义权限分级，`linux-sandbox` 用 bwrap 创建挂载/网络/进程命名空间：

```rust
// execpolicy: 权限分级（示意结构）
pub enum ExecPolicy {
    ReadOnly,          // 仅读，禁止任何写入
    WorkspaceWrite,    // 允许写工作区
    FullAccess,        // 完全访问（需显式开启）
}
// linux-sandbox: 用 bwrap 起隔离命名空间后执行命令
fn run_in_sandbox(cmd: &Command, policy: &ExecPolicy) -> Result<Output>
```

### 2. Agent 主循环（`core` crate）
`core` 只关心「思考 → 调工具 → 观察」的不变循环，工具执行被委托给 `tools` / `exec` / `apply-patch`，沙箱与策略在更底层拦截：

```rust
// core: 抽象的工具分发（示意）
loop {
    let resp = model.respond(ctx).await;          // codex-api → Responses API
    for item in resp.items {                       // 工具调用 / 文本
        match item { ToolCall(c) => {
            let out = execpolicy::guard(c, &policy).await?;  // 沙箱前置
            ctx.observe(out);
        }}
    }
}
```

### 3. 云端任务（`cloud-tasks`）
本地 `core` 与云端 `cloud-tasks` 共用 Agent 逻辑，差异只在「执行后端」——这是它「三形态统一」的关键。

> 注：以上为基于仓库真实 crate 结构与公开文档还原的架构骨架，具体实现以 `codex-rs/` 下源码为准。

## 🌐 全网口碑画像
来源：TechLogHub 三方横评（2026-08-17）、Agensi / laracopilot / toolsmadeeasy 对比文、LogRocket 2026-06 排行榜。

### 好评共识
- **开源可审计**是最大卖点，社区普遍认为「闭源 Claude Code 做不到这点」。
- **长程自主 + 云端开 PR**被频繁点赞：「丢任务、回来看 PR」的工作流在 Claude Code 上需要自己搭。
- **Token 效率高**：一篇被广泛转发的 Express 重构测试显示 Codex 约 $15、Claude Code 约 $155（API 费率），方向性一致。

### 差评共识 / 踩坑高发区
- **长程自主易漂移**：在模糊指令下，Goal mode 容易跑偏，需要用户自己设 guardrail。
- **OpenAI 模型绑定**：最佳效果依赖 GPT-5.5 / o 系列，作为「模型无关 harness」较弱。
- **Windows 沙箱配置有学习曲线**：bwrap 在 Windows 上需 `windows-sandbox-rs`，配置踩坑多。

### 基准与定位
- Terminal-Bench 2.0：Codex(GPT-5.5) 82.7%，长于长程 agentic 工作流与多步调试。
- SWE-bench Verified：Claude Code(Opus) 在复杂多文件重构更高；SWE-bench Pro（抗污染）Claude Opus 4.8 69.2% vs GPT-5.5 58.6%。
- 结论分化明确：**质量/多文件 → Claude Code；速度/沙箱安全/异步 → Codex**。

## ⚔️ 竞品对比
| 维度 | openai/codex | anthropics/claude-code | google/gemini-cli |
|------|-------------|----------------------|-------------------|
| 开源 | ✅ Apache-2.0 | ❌ 无 SPDX（闭源分发） | ✅ |
| 安全模型 | OS 级沙箱优先 | 审批提示 + allow/deny 规则 | 可选容器沙箱 |
| 自主模型 | Goal mode（长程无人值守） | approval-gated loop + subagents | 对话式 ReAct |
| 上下文 | 模型原生窗口 + repo 索引 | 选择性加载（高 context 效率） | 1M token 暴力加载 |
| 计费 | ChatGPT 订阅包含 / API | 订阅 $20 起 / API | 免费层慷慨 |
| MCP | ✅ | ✅ 最成熟 | ✅ |

**选择建议**：已标准化 OpenAI 模型、要跑沙箱内长程无人值守任务 → Codex；要最高代码质量与多文件重构、愿留在 loop 里 → Claude Code；超大 mono-repo 要整库上下文 → Gemini CLI。三者 SKILL.md 互通，切换成本低。

## 🎯 核心研判
### 优势（不可替代）
- 唯一「开源 + 沙箱优先 + 云端异步开 PR」三者兼具的主流编码 Agent。
- ChatGPT 订阅即免费用，入门成本为零。

### 风险
- **模型锁 OpenAI**：脱离 GPT-5.5/o 系列后能力打折。
- **长程漂移**：模糊任务需要用户设护栏，否则浪费 token。
- Windows 沙箱体验落后 Linux/macOS。

### 适用 / 不适用
- ✅ OpenAI 技术栈、要安全隔离跑不可信操作、要异步长任务。
- ❌ 追求最高多文件重构代码质量且不介意付费 → Claude Code 更稳；超大库整库上下文 → Gemini CLI。

### 趋势
上升期。开源 + 沙箱 + 多端统一是 2026 编码 Agent 的主流范式，Codex 在该象限占据先发开源位。

## 📂 关键文件路径速查
- `codex-rs/core/` — Agent 主循环
- `codex-rs/sandboxing/` + `codex-rs/linux-sandbox/` + `codex-rs/windows-sandbox-rs/` — OS 级沙箱
- `codex-rs/execpolicy/` — 执行权限分级
- `codex-rs/codex-api/src/endpoint/responses.rs` — Responses API 桥接
- `codex-rs/codex-mcp/` + `codex-rs/mcp-server/` — MCP 集成
- `codex-rs/cloud-tasks/` + `codex-rs/cloud-tasks-client/` — 云端任务编排
- `codex-rs/skills/` — SKILL.md 技能加载
- `codex-rs/hooks/` + `codex-rs/tui/` — 钩子与终端 UI
- `codex-cli/` — CLI 壳（TS/JS）
- `docs/` — 官方文档与贡献指南
