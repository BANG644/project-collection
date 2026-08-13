# holaOS 深度调研（holaboss-ai/holaOS）

> 调研日期：2026-08-14 ｜ 星标：6,447 ⭐ ｜ 语言：TypeScript ｜ 协议：Modified Apache 2.0（附加商业分发/品牌限制）｜ 默认分支：main ｜ 创建：2026-03-22 ｜ 官网：holaos.ai

## 一、项目定位（一句话）

holaOS 是一个**开源一体化 AI Agent 工作区**：把 Claude Code、Codex、以及自带 holaOS Agent 跑在**同一个本地优先工作区**里，共享记忆、工具、技能与应用，主张「无厂商锁定 + 本地优先」。

## 二、项目亮点（差异化，开篇呈现）

- 🔀 **任意 Agent 同工作区，无锁定**：Claude Code / Codex / 自带 Agent 并排运行，共用同一记忆、工具、技能；切换驱动不重建环境。
- 🧠 **本地优先的共享记忆**：上下文/偏好/项目历史存为**本地纯文件**（可读可改），跨会话、跨 Agent 持久化，不锁死在他人云端。
- 💸 **模型随你选**：内置前沿模型（Kimi K3、GLM 5.2 日常量；GPT 5.6、Claude Opus 5、Fable 5 攻坚），或 **BYOK**（自带 OpenAI / Anthropic / 兼容端点密钥）。
- 🪟 **HolaApps：应用与 Agent 并排的真实 UI**：从内置市场装应用，作为**真实可交互界面**紧邻 Agent 打开（Notion、浏览器、你的自有 app），Agent 在其中操作，结果就地落盘（`.xlsx`/`.pptx`/`.docx`）。
- 🧩 **100+ 集成 + MCP + 技能 + HolaApps 市场**：Gmail/Notion/Slack/GitHub/Linear 等一键 OAuth；任意 MCP server 即插即用；技能打包一次、任意 Agent 复用。

## 三、核心架构

TypeScript monorepo（Turbo 编排）：`apps/desktop`（Electron 桌面壳）+ `apps/docs`；`packages/`（核心运行时：记忆、集成、MCP 桥接、技能执行）；`runtime/`（Agent 执行运行时，把 Claude Code / Codex 作为「驱动」接入）；`shared/`（跨包共享）；`patches/`（依赖补丁）。根级 `AGENTS.md` / `CLAUDE.md` 是给编码 Agent 的提示工程文件。协议为 **Modified Apache 2.0**（在 Apache 2.0 基础上附加商业分发与品牌使用限制，自建分发需注意）。要求 Node 24。

## 四、应用场景与启发

- **个人 / 团队 Agent 工作台**：统一调度多个编码 / 通用 Agent，避免每个 Agent 各建一套环境。
- **多 Agent 统一本地记忆**：把记忆做成可读文件，天然可移植、可审计、可备份。
- **「应用即 UI 表面，Agent 来驱动」范式**：HolaApps 让 Agent 操作真实 App（而非只吐聊天文本），人随时接管——是「Agent 操作系统」的早期实现样本。
- 💡 **启发**：① Agent OS 化的关键是「共享记忆 + 无锁定 + 真实 UI 并排」；② 本地优先记忆文件化，是兼顾隐私与可移植的最佳折中；③ 对重视数据主权 / 多 Agent 协同的用户，这类「Agent 工作台」比单一聊天壳更有长期价值。

## 五、源码深度解读

### 1. `packages/` —— 核心运行时
拆分记忆（本地文件 + 向量嵌入）、集成（50+ OAuth 连接）、MCP 桥接、技能运行时。记忆层是「本地纯文件 + 结构化 + 嵌入」的混合，保证跨 Agent 召回。

### 2. `apps/desktop` —— Electron 壳
启动 Agent 运行时并渲染 HolaApps 并排 UI；`desktop:install` → `prepare-runtime:local` → `typecheck` → `dev` 的脚本链在 `package.json` 中编排。

### 3. `runtime/` —— Agent 驱动接入
把外部 Agent（Claude Code / Codex）作为「driver」接入统一工作区，使其共享同一记忆 / 工具 / 应用上下文，是「无锁定」的技术支点。

## 六、全网口碑

- 2026-03 新建，趋势榜新星（6.4k⭐，2026-08），Trendshift 上榜；定位对标「Agent 操作系统」。
- 数据有限（open issues 仅 8 个），属**极早期项目**；社区与生态尚未规模化，口碑积累中。
- 因「本地优先 + 多 Agent 无锁定 + 真实 App 并排」的清晰定位，在 Agent 工作台赛道获得关注。

## 七、竞品对比 + 核心研判

| 维度 | holaOS | stablyai/orca | Flowise/Dify | AgentOps |
|---|---|---|---|---|
| 定位 | Agent 工作台/OS | worktree Agent 编排 | 编排 UI | 可观测 |
| 本地优先 | ✅ 纯文件记忆 | ✅ | 部分 | ❌ |
| 多 Agent 无锁定 | ✅ | 部分 | ❌ | ❌ |
| 真实 App 并排 | ✅ HolaApps | ❌ | 部分 | ❌ |

- **核心研判**：
  - ✅ 优势：无锁定 + 本地优先 + 多 Agent 统一 + 真实 UI 并排 + HolaApps 市场，概念完整。
  - ⚠️ 风险：**极早期**（Node 24 门槛、Modified Apache 2.0 商业限制）、生态未成熟、与 Dify/Flowise 等重叠且暂无先发优势。
  - 🔮 趋势：Agent OS 化 / 工作台化是明确方向，但胜出者未定。
  - 💡 启发：若你重视数据主权与多 Agent 协同，可把它作为「Agent 工作台」候选持续观察；生产采用需等生态与许可条款更清晰。

## 八、关键文件路径速查

- `apps/desktop/`（Electron 桌面应用，`.env.example` 为配置模板）
- `packages/`（核心运行时：记忆 / 集成 / MCP / 技能）
- `runtime/`（Agent 驱动接入层）
- `shared/` · `patches/`（依赖补丁）
- `AGENTS.md` · `CLAUDE.md` · `INSTALL.md` · `LICENSE`（Modified Apache 2.0）
