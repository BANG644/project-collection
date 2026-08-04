# 🤝 accomplish-ai/coworker — 本地优先的开源 AI 同事

> **仓库:** [accomplish-ai/coworker](https://github.com/accomplish-ai/coworker)
> **Stars:** 10,938 ⭐（2026-06-19 入库时仅标 "Trending" → 本轮校正真实星标）
> **最后推送:** 2026-07-15 ｜ **语言:** TypeScript ｜ **许可:** MIT
> **版本:** `0.1.0`（早期）｜ **运行时:** Node >=24 ｜ **包管理:** pnpm monorepo
> **定位:** 活在用户桌面上的开源 AI 同事——本地运行、文件不出机器、用户自带 API Key

---

## 项目亮点（差异化）

- 🏗️ **真正的三进程架构**：`daemon`（常驻本地服务）+ `desktop`（Electron 壳）+ `web`（React 客户端）三者解耦，不是单壳 App。
- 🧠 **daemon = 有状态的 Agent 大脑**：任务/密钥/调度/技能/工作区/连接器的状态全在一个常驻本地服务里，多客户端可共享。
- 🌐 **多入口 + 多通道**：Web UI、Electron 桌面壳、甚至 **WhatsApp 连接器**（`whatsapp-service`）都能驱动同一个 daemon。
- 🔧 **MCP 即能力层**：浏览器、日历、complete-task 等能力都是独立 MCP server（`packages/agent-core/mcp-tools/`），可组合可插拔。
- 🔓 **OpenCode 集成**：代码类任务直接接 OpenCode 开源编码运行时，而非自己造执行引擎。

---

## 项目全景

旧报告把 coworker 当成"又一个桌面助手"是低估了它。它实质是一个 **local-first agent orchestration platform**：一个常驻本地的 daemon 负责所有状态与执行，Electron 负责原生壳与窗口，React Web 客户端负责交互。用户自带 API Key（OpenAI / Anthropic / Google / xAI / DeepSeek / Kimi / GLM / MiniMax / OpenRouter / Bedrock / Ollama 等 15+），文件留在本地。

注意 **版本仅 0.1.0**——早期、API 可能变动、Node 24 门槛偏高，但架构设计已经显出"平台"野心而非"玩具"。

---

## 核心架构（三进程 + 共享核心）

```
┌─────────────────────────────────────────────────────────────┐
│  apps/desktop  (Electron 主进程)                              │
│   app-startup / app-shutdown / app-window / connectors-auth   │
│   analytics(mixpanel)  ── 启动并托管下面两者                    │
└───────────────┬───────────────────────────┬─────────────────┘
                │ 渲染                       │ HTTP 调用
                ▼                            ▼
┌──────────────────────────┐   ┌──────────────────────────────────┐
│  apps/web (React 客户端)  │   │  apps/daemon (Node HTTP 服务)     │
│  App.tsx / TaskLauncher / │   │  task-service / scheduler-service │
│  BrowserPreview / Todo   │◄─►│  secrets / storage / settings /    │
│                          │   │  skills / workspace / connector /  │
│                          │   │  google-account / whatsapp /       │
│                          │   │  rate-limiter  (常驻大脑)           │
└──────────────────────────┘   └───────────────┬──────────────────┘
                                                │ 调用
                                                ▼
                              ┌──────────────────────────────────────┐
                              │  packages/agent-core (共享核心库)      │
                              │  src/browser/   浏览器自动化引擎        │
                              │  src/opencode/  接 OpenCode 编码运行时 │
                              │  src/common/types/  daemon/gateway/    │
                              │                    permission/sandbox/  │
                              │                    skills/task/...     │
                              │  mcp-tools/  calendar / complete-task / │
                              │              dev-browser-mcp           │
                              └──────────────────────────────────────┘
```

**为什么这样分**：把"无状态 UI"和"有状态 Agent 后端"切开，daemon 成为唯一真相源——即使桌面壳崩溃或用户用 Web/远程（`dev:remote`）访问，任务进度、密钥、调度都不丢。这是比"Electron 里直接跑 Agent"更稳的工程选择。

---

## 源码深度解读

### 1. daemon 服务清单（`apps/daemon/src/`）
常驻 Node 服务，每个职责一个 service：
- `task-service*.ts` / `task-callbacks.ts` / `task-event-forwarding.ts` —— 任务生命周期与事件
- `scheduler-service.ts` / `rate-limiter.ts` —— 定时与限流
- `secrets-service.ts` / `storage-service.ts` / `settings-service.ts` —— 凭证/持久化/配置
- `skills-service.ts` / `workspace-service.ts` —— 技能与工作区
- `connector-service.ts` / `google-account-service.ts` / `whatsapp-service.ts` —— 外部通道
- `http-server-factory.ts` / `daemon-routes.ts` / `health.ts` —— HTTP 暴露面

### 2. 浏览器自动化核心（`packages/agent-core/src/browser/`）
`browser-session.ts` / `browser-spawn.ts` / `server.ts` / `detection.ts` 构成无头浏览器引擎；`mcp-tools/dev-browser-mcp/` 再把它包成 MCP（`browser-manager.ts`、`click-change-detection.ts`、`coordinate-click.ts`、`emulation-aware-input.ts`）——即"让 Agent 能点网页"的能力层。

### 3. 类型系统是骨架（`packages/agent-core/src/common/types/`）
`daemon` / `gateway` / `permission` / `provider` / `sandbox` / `skills` / `task` / `todo` / `workspace` / `messaging` / `connector` / `google-account` 一整套类型，说明它从一开始就把"多客户端 + 权限 + 沙箱 + 连接器"当一等公民设计，而非事后补丁。

### 4. 权限模型
`permission-request-builders.ts` + `common/types/permission.ts` 实现"每个操作用户审批"——与 README 宣传的"完全控制"一致，是本地 Agent 的安全底线。

---

## 应用场景与启发

- **想做本地优先 Agent 产品**：直接抄这套三分层——React 无状态 UI + Electron 壳 + 常驻 daemon。UI 与 Agent 后端解耦后，桌面/Web/远程/IM 都能复用同一大脑。
- **能力用 MCP 拼装**：把每个能力（浏览器、日历、完成任务）做成独立 MCP server，比把功能硬编码进主程序更易扩展与测试。
- **代码执行别自己造**：接 OpenCode 这类开源编码运行时，专注编排与 UX。
- **多通道入口**：同一 daemon 同时服务 Web 与 WhatsApp，证明"Agent 后端"思路天然支持多渠道，不必为每个入口重写逻辑。

---

## 社区口碑

- Trending 出圈，多语言 README（ar/es/hi/id/ja/ko/ru/ta/tr/zh-CN）覆盖广，Discord 活跃。
- MIT + 本地优先，隐私叙事对企业和注重数据的用户有吸引力。
- 短板：0.1.0 极早期，Node 24 硬门槛劝退部分环境；功能成熟度与长期维护力尚未经大规模验证；Electron 体积与资源占用天然偏高。

---

## 竞品对比

| | Coworker | Open-Interpreter | Screenpipe | Manus/通用 Web Agent |
|---|---|---|---|---|
| 运行方式 | 本地 daemon + 桌面 + Web | CLI（本地） | 桌面守护进程 | 云端 |
| 多通道 | ✅ Web/桌面/WhatsApp | ❌ | ❌ | ❌ |
| 浏览器自动化 | ✅ 内置 | ❌ | ✅ 仅采集 | ✅ |
| 代码执行 | ✅ OpenCode 集成 | ✅ | ❌ | ✅ |
| 技能/MCP 能力层 | ✅ MCP 即插拔 | ❌ | ❌ | 视产品 |
| 用户审批 | ✅ 每步 | 可配 | ❌ | 视产品 |
| 许可 | MIT | MIT | MIT | 闭源 |

**结论**：coworker 的差异化在"本地优先 + 多通道 + daemon 状态化 + MCP 组合"，与纯 CLI 的 OI、纯采集的 Screenpipe、纯云端的 Manus 都不直接撞车。

---

## 核心研判

| 维度 | 评价 |
|------|------|
| 架构设计 | ⭐⭐⭐⭐⭐ 三进程 + 共享核心 + MCP 能力层，平台级思路 |
| 实用性 | ⭐⭐⭐⭐ 隐私优先、模型广、多通道 |
| 成熟度风险 | ⚠️ 0.1.0 早期，Node24 门槛，Electron 重 |
| 生态前景 | ⭐⭐⭐⭐ 本地 Agent + 多入口是清晰趋势 |

**研判**：coworker 不是"又一个桌面助手"，而是把 Agent 后端做成可本地托管、多渠道驱动的平台雏形。值得架构借鉴，但**现在入场当生产依赖偏早**——建议作为"本地 Agent 平台怎么分层"的参考实现来读，等 0.3+ 或 1.0 再评估上生产。

---

## 关键文件路径速查

| 文件 | 说明 |
|------|------|
| `apps/daemon/src/` | 常驻本地服务：任务/密钥/调度/连接器 |
| `apps/desktop/src/main/` | Electron 主进程：窗口/启动/连接器鉴权 |
| `apps/web/src/client/` | React 客户端：任务启动器/浏览器预览/待办 |
| `packages/agent-core/src/browser/` | 浏览器自动化引擎 |
| `packages/agent-core/src/opencode/` | OpenCode 编码运行时集成 |
| `packages/agent-core/mcp-tools/` | MCP 能力层（日历/完成任务/浏览器） |
| `packages/agent-core/src/common/types/` | 全系统类型骨架 |
| `package.json` / `pnpm-workspace.yaml` | pnpm monorepo + Node>=24 |

---

*调研日期: 2026-08-05 ｜ 数据来源：GitHub API + 仓库文件树 + README + 根 package.json*
