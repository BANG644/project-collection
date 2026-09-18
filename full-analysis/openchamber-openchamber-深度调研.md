# 🔬 openchamber/openchamber - 全方位深度调研

## 📌 一句话定位
OpenChamber 是一个基于 **OpenCode AI agent SDK** 的开源"代理式开发环境"（MIT），把 AI 编码 agent 的**调用、追踪、评审、发布**串进同一工作区，并跨桌面/Web/PWA/VS Code/手机多端保持会话连续——作者是 Bohdan Triapitsyn，2025-09 首次公开，一年内冲到 ~1 万⭐。

## ⭐ 项目亮点
- **Session Goals（可验证终点）**：给 session 设一个完成条件，agent 每轮自动检查结果，达成/卡住/到上限才停；即使关掉 App 后台也继续跑——把"agent 跑偏"用"可验证目标"约束住。
- **Multi-run + Fusion（多模型并行融合）**：同一任务可同时丢给最多 5 个模型、各自独立 session/worktree；挑最优，或用 Fusion 把多个输出的强项重组为新 session（不是简单拼接，而是重排成可执行上下文）。
- **Changes Walkthrough + Preview**：大 diff 被 AI 拆成有序步骤讲解"改了什么、如何配合"；Preview 让你在运行应用里**点选元素**，把截图+DOM 路径+CSS+控制台报错一起发给 agent——前端调试不再靠手述"左边第二个按钮偏了"。
- **Private Relay（端到端加密远程）**：一次性二维码配对设备，经加密中继连接，**不开公网端口、不经第三方中转**，可随时撤销——满足"出门用手机连回家里工作站"的隐私诉求。

## 🏗️ 项目架构全景
### 仓库结构（来自 `package.json` + README）
- **Bun workspace monorepo**：`packages/web`（React+Vite 前端）、`packages/ui`（React 19 + Tailwind 4 + HeroUI + CodeMirror 多语言）、`packages/electron`（桌面壳）、`packages/mobile`、`packages/sdk`、`packages/vscode`、`packages/docs`。
- **关键技术**：React 19、`@codemirror/*`（多语言编辑器）、`zustand`（状态）、`zod`（校验）、`@opencode-ai/sdk`（agent 内核）、`node-pty`/`bun-pty`（终端）、`express` + `http-proxy-middleware`（Web 服务）、`@xenova/transformers`（本地 ML，如语音）。
- **运行模型**：桌面版自带 OpenCode CLI 二进制；Web/VS Code 版依赖 PATH 中的 OpenCode。CLI 用 `curl .../install.sh | bash` 安装，`openchamber --ui-password` 起本地服务（默认 localhost，公网访问需 `--lan` + 密码）。

### 核心能力链路
issue/PR → 启动 session（带上下文+评论+文件树）→ agent 执行+跑测试 → 失败检查回灌 agent 续修 → 更新/合并 PR；另有 cron 定时任务可配 Session Goals 做周期性维护。

## 💡 应用场景与启发
- **多 agent 并行 + 结果融合**：Multi-run/Fusion 是"不赌单模型一次出对"的工程解法，适合代码评审与方案对比——任何需要"多模型择优"的 pipeline 都可借鉴其 worktree 隔离 + 上下文重组思路。
- **"agent 产出是一等公民"的 IDE 范式**：把每次运行视为**可追踪/可回放/可合并的工作单元**，而非聊完即散的对话——对长时多轮 agent 任务（如本仓库的自动化调研）是重要产品启发。
- **本地优先 + 加密远程**：隐私模型写进代码（MIT 可见），比"默认上云"更契合敏感代码场景；Private Relay 的 QR 配对范式可复用到任何"设备间安全接力"。

## 🧠 核心源码解读
### 1. Monorepo 包划分（`package.json` workspaces）
```json
"workspaces": ["packages/*", "packages/sdk/examples/*"],
"packageManager": "bun@1.4.2",  // 非 npm/pnpm，用 bun 提速
```
`postinstall` 会自动 build SDK、build 内置扩展、确保 electron——把"装完即跑"做成默认体验。

### 2. 多端共享 UI（`packages/ui`）
UI 包被桌面（Electron）、Web（PWA）、VS Code 扩展共同复用，避免三端各写一遍；`settings-registry` 自动生成快照，主题可通过 `port-opencode-theme` 从 OpenCode 移植。

### 3. 与 OpenCode 的解耦
OpenChamber 不重造 agent 内核，只做"界面 + 监督 + 评审"层（`@opencode-ai/sdk` 调用），因此 OpenCode 升级即能力升级——"不重复造轮子，只补统一壳"。

## 📐 架构决策与设计哲学
- **基于 OpenCode 而非自研内核**：选 OpenCode 因"开源、API 稳、易扩展"（README "Why OpenCode?"）；明确与 OpenCode 团队无隶属。
- **本地优先 + 可自托管**：所有项目名/路径/prompt/代码/会话内容留在本地机器，隐私靠代码而非政策保证。
- **Bun 而非 npm**：构建/依赖用 bun，强调速度与 `bun-pty` 原生终端。

## 🌐 全网口碑画像
- **好评共识**：被称为"覆盖 90% 场景的锤子"（arceapps 对比）；分支可对话时间线（`/undo`/`/redo`/按轮 fork）被赞"每个 IDE GUI 都缺的能力"；GitHub issue→PR 闭环、VS Code 侧栏 Agent Manager 并行多模型体验获肯定；中文长测文章赞其"把代理运行当一等公民"。
- **差评共识**：远程访问依赖 Cloudflare 隧道，**企业代理/ISP 阻断 QUIC 时 quick 模式静默失败**；多窗口模式每窗拉独立 daemon，比标签页更重；500+ open issues 反映仍不稳定；文档与生态快速演进有"小坑"（中文实测文、reporank）。
- **争议焦点**：它本质是 OpenCode 的"漂亮壳"，价值在于界面/监督层而非内核；相对 OpenCode 原生 TUI（119k⭐）体量仍小。
- **增长信号**：2025-09 创建，半年 ~8000–10000⭐、800+ fork、活跃日更（everydev.ai / reporank / arceapps）。

## ⚔️ 竞品对比
| 维度 | OpenChamber | OpenCode(原生TUI) | CodeNomad | nomacode |
|------|-----------|------------------|-----------|----------|
| 形态 | 桌面/Web/VS Code/移动 | 终端 TUI | 原生 GUI | 轻量前端 |
| 多模型 | Multi-run+Fusion | 需自配 | 部分 | 部分 |
| 设备接力 | Private Relay E2E | LAN 共享 | — | — |
| 成熟度 | 新(500+ issues) | 高(119k⭐) | 中 | 中 |

## 🎯 核心研判
- **优势**：唯一把"多端连续 + 多模型融合 + issue→PR 闭环 + 加密远程"做全的开源壳；本地优先隐私模型清晰。
- **风险**：依赖 OpenCode 生态走向；新项目稳定性与文档成熟度不足；远程隧道对网络环境敏感。
- **适用**：需要 agent 连续工作、多任务并行、跨设备评审的开发者/小团队；**不适用**只偶尔让 AI 写几行代码的轻量用户。
- **趋势**：上升期，迭代快，是 OpenCode 生态最成熟的第三方前端之一。

## 📂 关键文件路径速查
- `package.json` — 根 monorepo 配置（workspaces/bun/依赖）
- `packages/ui/` — 共享 UI（React19+CodeMirror）
- `packages/electron/` — 桌面壳（内置 OpenCode）
- `packages/vscode/` — VS Code 扩展（Agent Manager）
- `packages/sdk/` — OpenCode SDK 封装
- `README.md` — 能力说明与 Quick start
- 文档 `packages/docs/content/docs/`（session-goals / multi-run / private-relay / walkthrough）
