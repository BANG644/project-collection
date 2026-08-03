# vercel-labs/agent-browser 深度调研

> 调研日期：2026-08-04 | 调研方式：gh API 元数据 + 真实源码树（`cli/src/main.rs`、`cli/src/connection.rs`、`cli/src/mcp.rs`、`cli/src/native/daemon.rs`）+ README | 报告类型：修旧账（重写 4.7KB 占位报告为完整 7 维）

## 一、项目定位（一句话）

agent-browser 是 Vercel 出品的**原生 Rust 浏览器自动化 CLI**——专给 AI Agent 用的「浏览器手」，通过快照（accessibility tree + `@eN` 引用）+ 持久守护进程 + CDP 驱动 Chrome，并提供 MCP server 让任意 MCP 客户端直接操控浏览器。

## 二、项目亮点（差异化）

1. **原生 Rust + 持久守护进程架构**：CLI 本身只是薄壳，真正干活的是常驻 daemon（Unix 域套接字 / Windows 用 TCP）。一次 `open` 拉起浏览器，后续 `snapshot/click/fill` 走本地 socket 复用同一会话——比每命令起一个 Playwright 进程轻得多、快得多。
2. **`@eN` 引用寻址**：快照返回带编号的元素引用（`@e2`、`@e3`），Agent 用 `click @e2` / `fill @e3 "..."` 而非脆弱的 CSS/XPath。还能 `screenshot --annotate` 产出编号标注图，把视觉与交互对齐。
3. **MCP 与 CLI 同源（MCP-via-CLI）**：MCP server 把工具调用**委托给同一个二进制在 `--json` 模式下的命令解析器**，所以 MCP 行为与 CLI 永远对齐，不会出现「MCP 能做的 CLI 做不了」的漂移（见源码解读）。
4. **多引擎后端**：默认 CDP 驱动 Chrome（含 Lightpanda 无头内核），同时内置 WebDriver 后端覆盖 **Appium / Safari / iOS**，一套命令跨桌面与移动端。
5. **为 AI Agent 而生的工程细节**：`AGENTS.md` 明确要求「新增 CLI 命令必须同步更新 MCP server、README、skill 三处」，并把 `cli/src/mcp.rs` 的 CLI/MCP 对齐列为硬约束——这是把「Agent 可消费性」写进贡献规范里，而非事后补。

## 三、核心架构

```
┌──────────────┐   stdio JSON-RPC    ┌─────────────────────┐
│ MCP Client   │ ───────────────────▶│ cli/src/mcp.rs       │
│ (Claude等)   │                      │ (委托给 CLI --json)  │
└──────────────┘                      └──────────┬──────────┘
                                                    │
┌──────────────┐   命令/JSON         ┌──────────────▼──────────┐
│ Agent CLI    │ ───────────────────▶│ cli/src/main.rs          │
│ (agent-browser …)│                  │ 解析 → connection 发送    │
└──────────────┘                      └──────────┬──────────┘
                                                  │ socket (Unix/TCP)
                                                  ▼
                                        ┌─────────────────────┐
                                        │  daemon (tokio async) │
                                        │  cli/src/native/daemon│
                                        │  CdpClient / StreamSrv │
                                        └──────────┬──────────┘
                                                   │ CDP
                                        ┌──────────▼──────────┐
                                        │ Chrome (CfT) / Lightpanda │
                                        │ WebDriver: Appium/Safari/iOS │
                                        └─────────────────────┘
```

- **`cli/src/main.rs`**：入口与模块装配。`mod connection` 负责 `ensure_daemon` / `send_command` / `get_socket_dir` / `is_pid_alive` / `walk_daemons`；所有命令最终序列化为 JSON 经 socket 发给 daemon。
- **`cli/src/native/daemon.rs`**：tokio 异步守护进程。Unix 监听 `.sock`、Windows 写 `.port` 走 TCP；管理 pid/version 文件、StreamServer（实时流）、IdleActivity（空闲超时）、`AGENT_BROWSER_STATE_EXPIRE_DAYS` 状态清理。
- **`cli/src/native/cdp/`**：Chrome DevTools Protocol 封装（chrome.rs / lightpanda.rs / discovery / types）。
- **`cli/src/native/webdriver/`**：跨引擎后端（appium / safari / ios / backend / client）。
- **`cli/src/mcp.rs`**：stdio MCP server，保持 stdout 只输出换行分隔的 JSON-RPC，工具调用转发给 CLI 的 `--json` 模式。
- **`cli/src/snapshot.rs` + `native/element.rs` + `native/screenshot.rs`**：快照树、元素定位、截图/标注。
- **`cli/src/doctor/`**：自检模块（chrome/config/daemon/environment/network/security/webgpu…），`agent-browser doctor` 一键排查环境。
- **`benchmarks/`**：自带 `bench.ts` + `scenarios.ts` 性能基线，强调「fast native」是可量化的承诺。

**语言/许可**：Rust（CLI）+ TypeScript（docs/dashboard）；Apache-2.0。安装覆盖 npm（`npm i -g agent-browser`）、Homebrew、Cargo，且 daemon 不依赖 Node/Playwright。

## 四、应用场景与启发

- **给任意 Agent 接上「浏览器能力」**：Claude Code / Codex / Cursor 等只要支持 MCP，加载 agent-browser 的 MCP server 即可让其「打开网页、填表、截图、读 DOM」——比让模型自己写 Playwright 脚本稳得多。
- **E2E 测试与网页巡检**：`read <url>` 取 agent-readable 文本、`snapshot` 取可交互树、`wait_for_*` 系列做同步等待，可组成零代码维护成本的自动化巡检。
- **架构借鉴——「薄 CLI + 厚 daemon + MCP 同源」**：
  - 把有状态的部分（浏览器会话）放进常驻 daemon，CLI 保持无状态、可随时重启，避免每命令重建浏览上下文的开销。
  - **MCP 不要另写一套工具实现**，而是把 MCP 调用转回 CLI 的 `--json` 解析器——单一事实来源，CLI 与 MCP 永不漂移。这是做「CLI 工具 + MCP 暴露」的最佳实践样板。
- **多引擎后端抽象**：用统一命令面屏蔽 Chrome / Safari / iOS 的差异，Agent 侧无需感知底层引擎。

## 五、源码深度解读（2 个最具借鉴价值的模块）

### 1. `cli/src/connection.rs` — CLI 与 daemon 的解耦（节选）

CLI 不直连浏览器，而是 `ensure_daemon` 后通过 socket 发命令。关键设计是**命名空间隔离 + 空闲生命周期**：

```rust
// 命名空间隔离 daemon 的 socket 与 restore-state 目录
fn get_socket_dir() -> PathBuf {
    let ns = env::var("AGENT_BROWSER_NAMESPACE")
        .unwrap_or_else(|_| "default".into());
    ...
}
// ensure_daemon: 若 daemon 不在（is_pid_alive 为假）则拉起；向 socket 发送命令并读 Response
fn send_command(opts: &DaemonOptions, payload: Value) -> Result<Response, ...> { ... }
```

`AGENT_BROWSER_NAMESPACE` 让多个项目/会话的浏览器 daemon 互不干扰；`IdleActivity` + 空闲超时让无人用的 daemon 自动退场，不占资源。

### 2. `cli/src/mcp.rs` — MCP 委托给 CLI（节选）

```rust
//! The server keeps stdout exclusively for newline-delimited JSON-RPC
//! messages. Tool calls are delegated to the current binary in `--json` mode
//! so MCP behavior stays aligned with the normal CLI command surface.
const PROTOCOL_VERSION: &str = "2025-11-25";
const TOOL_LIST_PAGE_SIZE: usize = 64;   // 工具多时分页，避免一次列全
const TOOL_SNAPSHOT: &str = "agent_browser_snapshot";
const TOOL_CLICK:    &str = "agent_browser_click";
// ... 80+ agent_browser_* 工具，命名与 CLI 子命令一一对应
```

> 借鉴点：**MCP server 不重复实现业务，只做「协议适配层」**——把 JSON-RPC 工具调用翻译成对同一个二进制 `--json` 模式的调用。这样 CLI 加一个命令，MCP 同步获得一个工具，且语义一致。`TOOL_LIST_PAGE_SIZE=64` 也提示：当工具面很大时，MCP `tools/list` 要分页。

## 六、社区口碑

- 数据不可用（本次 gh Web/Trending 不可达，未抓取 HN/Reddit 等外部讨论；仓库 631 open issues、2,611 forks，CI 含 `benchmarks` 性能门禁，工程成熟度_signal 强）。
- `skills.sh` 已收录（`skills.sh/b/vercel-labs/agent-browser`），且仓库自带 `skill-data/core/SKILL.md` + `references/`，说明 Vercel 把「让 Agent 一键学会用本工具」当作一等公民在运营——这是 AI-native 工具的典型口碑建设手法。

## 七、竞品对比 + 核心研判

| 维度 | agent-browser | Playwright | Puppeteer | browser-use（AI agent） |
|------|---------------|-----------|-----------|------------------------|
| 实现 | 原生 Rust CLI + daemon | Node 库 | Node 库 | Python Agent 框架 |
| 寻址 | `@eN` 引用 + a11y 树 | selector | selector | 视觉/LLM 定位 |
| MCP | ✅ 原生 server | 需额外封装 | 需额外封装 | ✅（自身即 Agent） |
| 多引擎 | CDP + WebDriver(Safari/iOS) | 多引擎 | 仅 Chromium | 依赖 Playwright |
| 轻量 | ✅ 常驻 daemon 复用会话 | 每进程起浏览器 | 每进程起浏览器 | 重（LLM 推理） |

**核心研判：**
- **优势**：Rust 原生 + daemon 复用会话带来真实的速度/资源优势；MCP-via-CLI 的「单一事实来源」设计是同类工具里最干净的；多引擎后端（含 iOS/Safari）覆盖广；`AGENTS.md` 把「Agent 可消费性」写进贡献规范，长期利于生态。
- **风险**：① 强绑定 Chrome for Testing，非 Chromium 内核（Firefox/WebKit 桌面）支持弱；② Rust CLI 对纯 Node 团队是额外工具链；③ 与 Vercel 其他产品（如 v0 / AI SDK）的耦合度未来可能加深。
- **趋势/启发**：**「给 Agent 的浏览器工具」正在从 Python Agent 框架（browser-use）与 Node 库（Playwright）两条老路，收敛到「原生 CLI + MCP」这条新路**——agent-browser 是这条路的标杆。做同类工具时，优先保证「MCP 暴露 + 引用寻址 + 会话复用」三件事。

## 八、关键文件速查

| 路径 | 作用 |
|------|------|
| `cli/src/main.rs` | 入口与模块装配，命令解析后转 JSON 经 socket 发 daemon |
| `cli/src/connection.rs` | CLI↔daemon 解耦：`ensure_daemon` / `send_command` / namespace 隔离 |
| `cli/src/native/daemon.rs` | tokio 异步守护进程：Unix socket / TCP、状态清理、空闲超时 |
| `cli/src/mcp.rs` | stdio MCP server，委托给 CLI `--json` 模式（单一事实来源） |
| `cli/src/native/cdp/` | CDP 封装（chrome / lightpanda / discovery / types） |
| `cli/src/native/webdriver/` | 跨引擎后端（appium / safari / ios） |
| `cli/src/snapshot.rs` `native/element.rs` | 快照树、元素定位、@eN 引用 |
| `cli/src/doctor/` | 环境自检（chrome/config/network/security/webgpu） |
| `benchmarks/` | `bench.ts` + `scenarios.ts` 性能基线 |
| `AGENTS.md` | 贡献规范：CLI/MCP 对齐硬约束、AI 可消费性 |
| `agent-browser.schema.json` | 配置文件 schema（headed/json/session/restore/namespace…） |

---
*本地归档：`full-analysis/vercel-labs-agent-browser-深度调研.md` ｜ GitHub 远端：`github-project-research-20260614`*
