# nightly-labs/openbot 深度调研

> 调研日期：2026-10-27 ｜ 数据来源：GitHub API（README / 源码树 / 关键源文件）+ 当日 GitHub Trending 日榜
> 许可证：仓库含 LICENSE 但 GitHub 未识别为标准 SPDX（`NOASSERTION`），采用前需自行确认条款

## 项目亮点（差异化）

- **本地优先（local-first）的桌面工作区**：把 Codex / Claude / Grok / OpenCode / Gemini / Cursor / Cline 等 agent 变成"常驻同事"，每个 agent 拥有独立 workspace + 独立会话。
- **统一用 ACP 接入**：通过 **Agent Client Protocol（ACP）** 抽象各家 CLI，而不是为每一个 agent 写一套定制集成（也支持自定义 OpenAI 兼容端点与自定义 ACP agent，并自动探测本地 Ollama / LM Studio）。
- **崩溃安全的 FIFO 消息队列**：可暂停 / 恢复 / 取消，队列状态持久化，进程崩了不丢任务。
- **agent-to-agent 协作 + 文件传输 + 内嵌持久浏览器**：agent 之间能发消息、回贴、传图、托管文件；还能打开并操控一个嵌入式浏览器。
- **单体仓库跨端**：Electron 桌面 App + Expo 移动端 + Discord/Slack/Telegram 接入 + Cloudflare Workers/D1 账户后端，工程化完整。

## 项目定位（一句话）

OpenBot 是一个**本地优先的桌面工作台**，让你把多个 AI agent 当作有独立工作区、有记忆、能互相协作的"持久同事"来用——而不是每次在终端里一次性调用 CLI。

## 核心架构

- **桌面端**：Electron + SolidJS + Bun（`electron.vite.config.ts`、`electron-builder.yml` 驱动构建与签名）。
- **IPC 契约层**：`packages/contracts` 用 TypeScript 接口定义主进程↔渲染进程的桥接 API，preload 包裹作用域方法。
- **应用矩阵**（`apps/`）：`auth-api`（Cloudflare Workers + D1 账户后端，支持一次性邮箱码登录）、`mobile`（Expo）、`discord-app` / `slack-app` / `telegram-app`（IM 接入）、`site-router`、`status`。
- **agent 接入**：provider runtimes 适配各家 CLI，核心走 ACP；per-agent 上下文监控会在长线程耗尽模型窗口前自动 compaction（压缩）。

## 源码深度解读（2 个核心模块）

**1. IPC 分组 API 契约 —— `packages/contracts/src/ipc-desktop-apis.ts`**

该文件把每一个 agent 能力域拆成一组"分组 API"，统一用 `GroupApi<IpcEndpoints["xxx"]>` 模式生成类型安全的桥接接口：

```ts
export interface AgentDesktopApi extends PathApi<"agent"> {
  onAttachmentImport: (listener: (event: AttachmentImportEvent) => void) => () => void;
  onEvent: (listener: (event: AgentEvent) => void) => () => void;
}
export interface BrowserDesktopApi extends GroupApi<IpcEndpoints["browser"]> {
  sendLiveViewInput: (input: BrowserLiveViewInput) => Promise<void>;
}
export type ComputerUseDesktopApi = GroupApi<IpcEndpoints["computerUse"]>;
```

注释点出关键不变量：`onEvent` 是 `onScopedEvent` 过滤到"选中 server"后的视图；preload 会记录哪个 server 被选中；`ComputerUseDesktopApi` 只暴露给 cua 驱动，overlay 表面只听 `onHighlightPlacement`（推送而非拉取，避免被反向驱动）。这是一套**把 IPC 按能力分域、用类型约束边界**的干净设计。

**2. README「What works」声明的能力清单**

- Persistent agents backed by 独立 Codex/Claude/Grok/OpenCode/Gemini/Cursor/Cline 会话 + 本地 workspace；
- FIFO 队列（暂停 / 恢复 / 取消 / 崩溃安全持久化）；
- agent-to-agent 消息、回贴、反应、图片与托管文件传输；
- 持久嵌入式浏览器供 agent 打开 / 检查 / 控制；
- 可选 Computer Use（macOS/Win/Linux，由 `cua-driver` 二进制作为 OpenBot 的子进程启动并分发给各 provider）；
- 账户后端运行在 Cloudflare Workers + D1 上。

## 应用场景与启发

- **多 agent 持久协作工作台**：把"一次性 CLI 调用"升级为"有状态、有工作区、可排队的常驻同事"。对需要长会话 + 多 agent 协作的任务（例如需要边检索边归因、跨 agent 传递中间产物的科研项目）是值得借鉴的产品形态。
- **ACP 抽象值得复用**：用统一协议接入异构 agent CLI，避免 N×M 的定制集成爆炸——任何想"把多个 agent 编排进一个 GUI"的工具都可以参考。
- **崩溃安全队列 + per-agent compaction**：长任务不丢进度、上下文不爆窗，是 agent 工作台的基本功。

## 社区口碑

- 创建于 2026-08-12，最近推送 2026-10-26（当日仍在活跃开发）；**1,336⭐**，属于**很早期项目**。
- 2026-10-27 登上 GitHub Trending 日榜，增速快但基数小。
- **口碑数据不可用**：尚无大规模用户评测或第三方深度评测；作为 fresh project，能力以官方宣称为主，需谨慎采用。标注：早期项目，协议/功能仍可能大幅变动。

## 竞品对比

| 维度 | openbot | accomplish-ai/coworker | makecindy/cindy | 终端 harness（claude-code/codex） |
|------|---------|----------------------|----------------|-----------------------------------|
| 形态 | 桌面 GUI 工作台 | 本地优先 AI 同事（daemon+桌面+web） | 开箱即用 agent 客户端 | 命令行 |
| 多 agent | 持久 workspace + 队列 + 跨 IM | 有 | 多 harness 编排 | 单 agent |
| agent 接入 | ACP 统一协议 | MCP 能力层 | 多 harness×多模型 | 原生 CLI |
| 成熟度 | 极早期 | 早期 | 较新 | 成熟 |

## 核心研判

- **方向正确**：把 agent 从"一次性调用"升级为"常驻有状态同事"，契合 agent 协作趋势；ACP 抽象与崩溃安全队列是可复用亮点。
- **风险偏高**：极早期（许可 `NOASSERTION` 未明确），功能宣称多于验证；强依赖各家 CLI 的 ACP 稳定性。
- **采用建议**：作为"多 agent 工作台"的参考样本，重点学习其 workspace / queue / IPC 设计；生产采用需等生态成熟、许可澄清。

## 关键文件路径速查

- `packages/contracts/src/ipc-desktop-apis.ts` — IPC 分组 API 契约（核心集成边界）
- `packages/contracts/src/ipc-agent-events.ts` — agent 事件类型
- `packages/contracts/src/ipc-browser.ts` — 浏览器实时视图输入
- `apps/auth-api` — Cloudflare Workers + D1 账户后端
- `electron.vite.config.ts` / `electron-builder.yml` — 桌面构建与签名
- `docs/architecture/providers.md` — agent provider（ACP）设置说明
