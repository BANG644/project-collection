# chaitanyagiri/munder-difflin — 深度调研

> 调研日期：2026-08-21 ｜ 星标：3,066 ⭐ ｜ 协议：MIT（代码）/ 像素资产 LimeZu 非商业 ｜ 语言：TypeScript ｜ 趋势：GitHub Trending 日榜 ｜ 版本：v0.4.4（working prototype）

## 一、项目定位（一句话）

Munder Difflin 是一个 **桌面端多 Agent harness**（Electron），把你已经在用的终端编码 CLI（Claude Code / Codex / Grok / Kimi / Qwen / OpenCode / …）变成"你的克隆团队"，在一个 2D 办公室地板上可视化协作，由"你的克隆"Michael（GOD agent）统一编排。

## 二、项目亮点（差异化）

- **多 harness 统一包装**：一套 UI 编排 Claude Code / Antigravity(Gemini) / OpenAI Codex / xAI Grok / Kimi Code / Qwen / OpenCode / Crush / pi.dev / GitHub Copilot，全部 BYOK + 可接本地 LLM（Ollama/LM Studio/vLLM）。
- **GOD 自治编排**：Michael 读取每个请求、自行解决常规项保持系统全自治，仅把**关键项（花费 / 破坏操作 / 范围变更）升级到人工审批队列**。
- **Hive 共享层**：per-agent 记忆 + 原子文件邮箱（mailbox）+ 共享 blackboard + append-only 事件日志 + **single-committer git**（避免多 Agent 并发 `index.lock` 损坏）。
- **安全与可观测**：电路断路器（steer→constrain→stop 三级）、per-agent token 预算、真实成本账本、OTel 遥测、Tool Waterfall；Slack/Webhook 集成可让 Michael 派生临时 worker 回帖。
- **富可视化 UI**：Pixi.js 办公室地板（Agent 走动/信封飞递）、xterm.js 终端、内置 Monaco IDE（git rails + 差异对比）、Kanban 任务板；MIT（代码），像素资产来自 LimeZu 仅限非商业。

## 三、核心架构（克制呈现）

两条数据平面喂一个渲染器：

```
Electron Main (Node)
 ├─ pty.ts          # PtyManager：每个 agent 一个 node-pty 进程，按 id IPC 流式输出
 ├─ hive.ts         # 磁盘多 agent 层：memory / mailboxes / router
 ├─ hooks.ts        # hook server + 厂商桥（cth-hook for Claude Code, agy-hook for Antigravity）
 ├─ memory.ts       # 语义记忆层（CLI 包装，无索引时降级 no-op）
 ├─ breaker.ts / control.ts  # 成本/失控断路器 + HITL 闸门
 ├─ db.ts           # SQLite 持久化 + 成本账本
 └─ fs.ts / git.ts  # 沙箱化 fs/git 桥（经主进程，渲染器只走 window.cth）

Electron Renderer (React)
 ├─ OfficeFloor (Pixi.js)   # 办公室地板：角色/相机/寻路/状态
 └─ CommandBar / Terminal / Memory / Tasks / Triggers / Handbook 各面板
```

- **Terminal plane**：`PtyManager` 把每个 agent 衍生为真实 `node-pty` 进程，字节级真实（非模拟），用 xterm.js 渲染。
- **Hive / event plane**：`hive.ts` 是磁盘多 agent 层；`hooks.ts` 跑 hook server，厂商桥把生命周期 payload POST 进来；router 投递消息、GOD 裁决、idle/inbox 唤醒保持 worker  draining。
- **渲染边界**：渲染器只通过类型化 `window.cth` contextBridge 与主进程通信，所有 fs/git 访问经主进程 broker。

## 四、应用场景与启发（重点）

- **场景 1 — 把单 Agent CLI 升级为"并行办公室"**：用已有订阅（Claude/Codex/Grok…）的时薪额度跑一整队 Agent，人在旁监控而非逐个操作。
- **场景 2 — 多 Agent 协作可观测**：Avatar 走动 + 信封飞递 + 实时终端流，把"多 Agent 黑箱"变成可直观监控的办公室。
- **启发**：① "**single-committer git + 文件邮箱**"的 Agent 间通信范式（每个 agent 写自己 `outbox/`，router 投递到收件人 `inbox/`，单一提交者避免 `index.lock` 竞争）是分布式多 Agent 协调的稳健实践，比让所有 agent 直接碰 git 安全；② "**GOD 编排 + 人工闸门**"在保持自治的同时把花费/破坏操作升级人工，是安全的多 Agent 自治模板；③ Pixi 可视化显著降低多 Agent 系统的认知负荷，值得任何多 Agent 产品借鉴"把抽象协作具象化"。

## 五、源码解读（核心模块）

来自真实 `src/main/` 结构与 README 说明：

- `pty.ts`：`PtyManager` 用 `node-pty` 把每个 agent 起成独立 PTY，输出经 `pty:data:<id>` 按 id 流式推给渲染器——这是"Every terminal is a real agent"的落地核心。
- `hive.ts` + `hooks.ts`：磁盘多 agent 层与 hook server 配合，厂商桥（`cth-hook`/`agy-hook`）把生命周期事件喂给 hive；router 负责消息投递与 GOD 裁决。
- `breaker.ts` / `control.ts`：成本/失控断路器（steer/constrain/stop 三级）+ HITL 闸门，是"可安全自治"的关键护栏。

## 六、全网口碑

- 赞誉：创意与趣味性极强（The Office / Dunder Mifflin 梗、15 个办公室角色 Avatar），在多 Agent harness 赛道以"可视化办公室"形成清晰差异化；Discord 社区活跃。
- 观察：v0.4.4 仍 working prototype；本版本刚修掉 Windows agent 互信 bug（cmd.exe 按首个换行截断多行消息，导致 agent 互相无视）；资产许可非商业，商用需替换像素图。

## 七、竞品对比 + 核心研判

| 维度 | Munder Difflin | OpenCode/Claude Code(单 Agent) | coworker | oh-my-claudecode | stablyai/orca |
|------|---------------|-------------------------------|----------|------------------|---------------|
| 多 Agent 编排 | ✅ 可视化 | ❌ 单 | ✅ | ✅(Teams) | ✅(worktree) |
| 多厂商 CLI 统一 | ✅ | ❌ | ⚠️ | ⚠️ | ⚠️ |
| 可视化办公室 | ✅ Pixi | ❌ | ❌ | ❌ | ❌ |
| 成熟度 | ⚠️ prototype | ✅ | ⚠️ | ⚠️ | ⚠️ |

**核心研判**：Munder Difflin 在"多 Agent 编排的可观测性 + 趣味化"上做了有价值探索，其 single-committer git 协调与 GOD 自治+人工闸门是值得借鉴的工程范式。**适合个人/小团队体验并行 Agent、作为理念参考与玩具**；但 v0.4 早期、Electron 较重、资产许可非商业（商用需替换），**生产环境慎用**。对想做多 Agent 产品的团队，其"把协作具象成办公室"的 UX 思路值得吸收。

> 关键文件速查：`src/main/pty.ts`、`src/main/hive.ts`、`src/main/hooks.ts`、`src/main/memory.ts`、`src/main/breaker.ts`、`src/main/control.ts`、`src/main/db.ts`、`src/preload/index.ts`、`HIVE.md`、`SPEC.md`、`DESIGN.md`
