# 🔬 different-ai/openwork - 全方位深度调研

- GitHub: https://github.com/different-ai/openwork
- 调研时间: 2026-07-30
- 仓库规模: ⭐ 17.7K / Fork 1.8K / 语言 TypeScript / 协议 自定义(NOASSERTION, 桌面端免费开源) / 3,904 commits
- 官方定位: The open-source alternative to Claude Cowork (powered by opencode)
- 一句话: OpenWork 把「AI 工作流的可复用资产（skills / MCPs / 插件 / 配置）」做成可一键分享的链接，让 Claude Code / Codex / Cursor 等任意 Agent 都能复用同一套能力——开源版 Claude Cowork + 跨 Agent 能力总线。

## 🌟 项目亮点（差异化）

1. **跨 Agent 能力总线**：核心交付物不是桌面 App，而是一个**远程 MCP 服务器**（`https://api.openworklabs.com/mcp/agent`）。往 Codex/Claude Code/OpenCode/ChatGPT 里加一个 MCP，就把 skills、MCP 连接、Google Workspace、Microsoft 365 能力注入进去。
2. **「可弹出」设计（Ejectable）**：桌面 App 是可选的；你完全可以从自己已有的 Agent 直接用 OpenWork，无需安装 UI。
3. **一次性打包分享**：把 skills + MCPs + 插件 + 配置打包成一条链接，队友一键导入即用（无需终端/教程），借鉴 GitHub fork 文化做「能力分叉」。
4. **本地优先 + 50+ LLM**：基于 OpenCode，文件留在本地，支持 OpenAI/Anthropic/Google/本地等 50+ 提供商，而非锁定单一厂商。
5. **OpenWork Den 控制面**：团队/企业级管理——发布能力、按组织/团队/人分配、模型供给与策略管控、导入 Anthropic 兼容插件。

## 🏗️ 核心架构

- **桌面端**：Electron + Vite + pnpm + Turborepo monorepo（`apps/`、`packages/`、`ee/` 企业版、`evals/`、`prds/`）。
- **OpenWork MCP（核心）**：Streamable HTTP + OAuth 的远程 MCP server，仅暴露两个工具：
  - `search_capabilities`：发现当前可用能力
  - `execute_capability`：执行指定能力
  - 接入后客户端打开浏览器登录，按组织成员/角色/策略/暴露白名单做访问控制。
- **OpenWork Den（控制面）**：团队编排层，负责能力发布、席位/模型供给、桌面策略与版本管控。
- **分享模型**：Workspace Template → 生成单链接 → 队友 import 即落地（3 skills + 3 MCPs + 2 plugins 的 SDR 模板即开箱示例）。
- **商业模式**：桌面端免费开源（BYO LLM key）；Team Starter 前 5 席位免费、之后 $10/席位/月，含 API 与插件市场；Enterprise 定制（SSO、BYO 推理）。

## 🧠 源码深度解读

### 1. MCP 即「能力总线」的最小接口（README）
```text
The OpenWork MCP ... exposes two tools:
  search_capabilities  - finds what you can use
  execute_capability   - runs it
```
只暴露两个工具，却把「发现 + 执行」做成通用协议——这是把 Agent 能力从「写死在 prompt/配置里」升级为「可治理、可发现、可共享的服务」。比每个 Agent 各配一套 MCP 更上一层：OpenWork 自己是 MCP 的 MCP。

### 2. 桌面端是可选项，而非必需品（README 关键句）
> The desktop app is there when you want a dedicated workspace, but it is not required. You can use OpenWork from the agent you already have.

架构上把「用户界面」与「能力供给」解耦：核心价值在远程 MCP server，桌面 App 只是其中一个消费端。这让 OpenWork 能无缝嵌入既有 Agent 工作流，降低采用摩擦。

### 3. 企业侧 OAuth 收敛（提交历史）
```text
feat(connect): harden external MCP OAuth conformance (#2771)
fix(den): standardize external MCP OAuth on enterprise client (#2810)
```
external MCP 的 OAuth 合规被反复加固，说明它在认真做「把第三方 MCP/插件安全地接进组织」这件事，而非玩具。

## 💡 应用场景与启发

- **团队能力复用**：公司把内部 skills/MCP 打包成模板，新人一条链接拉起整套工作环境。
- **跨工具一致性**：在 Claude Code、Codex、Cursor 之间共享同一套 MCP 连接与 Google/365 能力，避免重复配置。
- **Agent 工作台开源化**：Claude Cowork 闭源商业，OpenWork 给「本地优先 + 多厂商 + 可分享」一个开源答案。
- **对同类需求的启发**：做 Agent 平台时，**先把「能力」做成可治理的远程 MCP，再谈 UI**；「分享链接 + 一键导入」比文档教程更能驱动团队 adoption；OAuth 收敛是企业落地的硬门槛，值得早做。

## 🌐 全网口碑

- **早期高热度**：登上 toolhunt、dev.to/juejin「一天一个开源项目」专题（第 18 篇），被称为「开源版 Claude Cowork / 本地 AI 代理工作台」。
- **活跃度极高**：3,904 commits，2026-07 仍在密集提交（evals typed runner、MCP OAuth 加固、bump 0.18.0），工程成熟度远超一般新项目。
- **定位清晰**：社区共识是「本地优先、数据自持、50+ LLM、跨平台（macOS/Win/Linux）」的开源 Cowork 替代。
- **反馈面**：桌面端到底是 Electron 还是 Tauri 有第三方文章误传（官方 README 显示 Electron+Vite）；企业版 `ee/` 闭源，免费与商业边界需看清；作为新项目生态（插件市场）仍在早期。

## ⚔️ 竞品对比 + 核心研判

| 维度 | OpenWork | Claude Cowork | Durable/Stack-AI | Composio |
|---|---|---|---|---|
| 开源 | ✅ 桌面端 | ❌ 闭源商业 | ❌ | ❌(SaaS) |
| 跨 Agent 复用 | ✅ 远程 MCP | 限自家 | 限自家 | ✅ 连接器 |
| 本地优先 | ✅ | ❌ | ❌ | ❌ |
| 能力分享 | ✅ 链接一键导入 | 部分 | 部分 | API |
| 企业控制面 | ✅ Den | ✅ | ✅ | ✅ |

**核心研判**：
- **最强**：把「Agent 能力」抽象成可治理、可分享、跨工具的远程 MCP，切口精准；本地优先 + 多厂商避开 Cowork 最大槽点。
- **风险**：商业可持续靠 Team/Enterprise 订阅，`ee/` 闭源；生态（插件市场、模板库）尚早，网络效应未成。
- **趋势**：Agent 工具正从「单 Agent 增强」走向「团队能力总线」，OpenWork 站在这个方向，且开源先发卡位好。
- **启发**：若做内部 Agent 平台，优先建设「能力即 MCP + 分享链接 + OAuth 治理」三层，比先做花哨 UI 更值钱。

## 📂 关键文件速查

- `README.md`（定位、MCP 接入、Den 控制面、本地开发）
- `package.json` / `pnpm-workspace.yaml` / `turbo.json`（monorepo 与构建编排）
- `apps/`（桌面端应用）、`packages/`（核心库）、`ee/`（企业版）
- `evals/`（能力评测）、`prds/scim`（产品需求/SCIM）
- `AGENTS.md` / `SECURITY.md` / `LICENSE`
- 远程 MCP：`https://api.openworklabs.com/mcp/agent`
