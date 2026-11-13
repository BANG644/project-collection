# 🔬 backnotprop/plannotator — 全方位深度调研

> 调研日期：2026-11-14 ｜ Stars：10,371 ｜ 语言：TypeScript（Bun 工作区）｜ 许可：MIT OR Apache-2.0 ｜ 编号：#592

## 📌 一句话定位
**本地优先的浏览器评审层**，插进你的 AI 编码 Agent（Claude Code / Codex / Copilot CLI / Gemini / OpenCode / Kiro / Droid / Amp / Pi 等）：agent 一提出方案/计划/HTML/收工，就在浏览器里打开可标注界面，你画重点、写评论、一键回传反馈让它接着干——补上「多 Agent 工作和你之间缺的那层 review」。

## ⭐ 项目亮点
- **接入面极广**：通过 plugins / hooks / commands 直插 10+ 编码 Agent 与个人助理，覆盖 Claude Code、Codex、Copilot CLI、Gemini CLI、OpenCode、Kiro、Droid、Amp、DeepSeek Harness、Pi，外加 VSCode / Cline / OpenClaw / DSH / PI 等插件。
- **Plannotator Inbox**：把多个 agent 的留言、提问、文件、引导式评审汇总到一个本地窗口，按「谁在等什么」分组，回答不阻塞任何 agent 会话，回复精准回到原会话——多 Agent 协作的「收件箱」。
- **三块评审面**：Inbox Surface（决策/原型/变体汇总）· Artifacts（标注 HTML/markdown 渲染件）· Code Review（本地 diff / 远程 PR / GitLab MR / GitButler / jj / Perforce / GitHub / GitLab）。
- **本地优先 + 零遥测**：计划、diff、标注、草稿、历史、配置默认全留本地；无使用遥测/分析；URL 标注可走 Jina Reader 或直连。
- **Herdr Annotate**：把同款评审带进终端（Herdr TUI），标注存同一数据目录，与 App 评审叠加复利。

## 🏗️ 项目架构全景
Bun 多包 monorepo（`package.json` workspaces：`apps/*` + `packages/*`）。`apps/` 下按接入端拆分：hook（agent hook 注入）、portal（评审门户）、review（浏览器评审 UI）、marketing、vscode-extension、cline-plugin、openclaw-plugin、dsh-plugin、pi-extension、opencode-plugin、guides-show、relay（relay 服务）、feedback-service、inbox。核心包：`packages/core`、`packages/server`、`packages/ui`、`packages/ai`、`packages/acp-client`、`packages/shared`、`packages/references`、`packages/system`、`packages/inbox`、`packages/t3-code`、`packages/guide-viewer`。

关键依赖揭示能力边界：`@anthropic-ai/claude-agent-sdk`、`@opencode-ai/sdk`、`@agentclientprotocol/sdk`（ACP）、`@modelcontextprotocol/client`（MCP）——即同时吃 Claude Agent SDK、OpenCode SDK、ACP、MCP 四类协议，靠 `plannotator inbox mcp` 让任何 agent 经 MCP 进收件箱。

## 💡 应用场景与启发
- **典型场景**：① agent 起草计划 → 浏览器打开 markdown 评审面，标注后回传；② 审本地改动或 GitHub PR，评论直接回给 agent；③ 多 agent 并行，Inbox 把各 agent 的提问/文件按「等什么」分组，你点开一条、标完、Send。
- **可借鉴模式**：「**把 agent 的输出先过一道人类标注闸再回流**」是降低多 Agent 失控的低成本结构——尤其适合「agent 自己觉得对、人没看就跑偏」的场景。
- **同类需求思路**：自研 Agent 工具链时，与其做重 PM 系统，不如做「轻量标注 + 精准回传 + 不阻塞会话」的收件箱层；plannotator 的 MCP/ACP 双协议接入值得抄。
- **边界**：本质是「human-in-the-loop 的评审 UI」，不是评测/审批自动化；大量接入靠插件与 hook，新 harness 需自行接。

## 🧠 核心源码解读（克制代码量）
`package.json` 的 scripts 暴露了运行模型：每个接入端是独立 `apps/*` 构建目标，共享 `packages/*`；typecheck 串联 20+ 个 `tsconfig` 做全仓严格类型。依赖层直接表明多协议并行接入：

```
"dependencies": {
  "@anthropic-ai/claude-agent-sdk": "^0.3.303",
  "@opencode-ai/sdk": "1.19.3",
  "@pierre/diffs": "1.6.4",          // diff 渲染
  "dockview-react": "^5.2.0",        // 多面板评审布局
  "marked": "^17.0.6", "dompurify": "^3.4.17"  // markdown 渲染 + 净化
},
"devDependencies": {
  "@agentclientprotocol/sdk": "1.9.0",
  "@modelcontextprotocol/client": "2.3.1"
}
```

评论回传路径：`/plannotator-review <pr-url>` 经 `packages/server` 调用已认证的 CLI/git remote 拉 PR/MR 数据；Inbox 的「回复回到原会话」依赖各 harness 的 plugin（Claude Code/Pi/OpenCode）或 `plannotator inbox mcp`（其余 agent）。`patchedDependencies` 里有对 `@opencode-ai/sdk` 与 `@pierre/diffs` 的补丁，说明它为了适配上游 SDK 做了局部 monkey-patch——接入层成本的真实信号。

## 📐 架构决策与设计哲学
- **本地优先、隐私默认**：明确「内容离开本地工作流仅当网络功能需要」，且给出关闭远程检查的开关（`--no-git-remote-check` / `PLANNOTATOR_GIT_REMOTE_CHECK=0`）。
- **不收集遥测**：计划/diff/标注默认留本地，与多数 SaaS 评审工具形成对比。
- **插件而非平台**：以 hook/plugin/command 嵌入既有 Agent，不要求迁移工具链。
- **诚实边界**：Release 检查会请求 GitHub 最新版（发往 GitHub 而非项目方），目前无 opt-out——唯一已知的网络副作用。

## 🌐 全网口碑画像
- **社区信号**：open issue ~200，高度集中在 Inbox 新功能（#3309 同一 Claude Code 会话显示为多个匿名 agent 参与者、#3303 区分「哪个 agent 在哪跑」、#3299 允许把 Inbox 嵌进受信宿主的 frame-ancestors、#3264 显示每个 agent 上下文窗口占用），说明产品重心在「多 Agent 收件箱」打磨，迭代极活跃。
- **正面口碑**：开发者普遍认可「终于有了 agent 和人类之间的 review 层」，对多 Agent 并行时「不被任何会话阻塞、回复精准回原会话」评价高。
- **风险 / 摩擦**：① 新 harness 需自行接插件，接入面虽广但非零成本；② Inbox 多会话身份识别仍是 open 痛点（#3309/#3303）；③ Release 检查的隐私开关缺失被社区点名。
- **外部评测**：数据不可用（未检索到独立深度评测文章，主要声量在 GitHub issue 与官网文档）。

## ⚔️ 竞品对比
| 维度 | Plannotator | Bloop/Greptile(代码评审) | Graphite | 传统 PR 评审 |
|------|-----------|------------------------|----------|------------|
| 接入 Agent | ✅ 10+ harness + MCP/ACP | ❌ | ❌ | ❌ |
| 多 Agent 收件箱 | ✅ Inbox | ❌ | ❌ | ❌ |
| 本地优先/零遥测 | ✅ | 视产品 | 否(SaaS) | — |
| 标注 HTML 制品 | ✅ | 部分 | 否 | 否 |
| 护城河 | 广接入 + human-in-loop 层 | 评审模型 | 堆叠/合并 | — |

**选择建议**：已在用编码 Agent 且想加「人审闸 + 多 Agent 收件箱」选 Plannotator；只要 PR 自动评审用 Greptile/Bloop；要分支堆叠工作流用 Graphite。

## 🎯 核心研判
- **优势**：精准补上「agent 产出 → 人审 → 回流」的缺失层；接入面业界最广；本地优先+零遥测契合隐私敏感团队；Inbox 是多 Agent 协作的稀缺正确抽象。
- **风险**：① 接入层靠多插件/hook，维护面大（含对上游 SDK 的 patch）；② 多会话身份识别仍不稳；③ 偏前端 UI 工具，无评测/审批自动化，单 Agent 小任务收益有限。
- **适用**：多 Agent 并行、需要人审把关、重视隐私_local 的团队/个人。**不适用**：只要全自动 PR 评审、或不用编码 Agent 的纯人团队。
- **趋势**：上升期，产品从「plan 标注」演进到「Inbox 多 Agent 收件箱」，方向贴合 Agent 协作刚需。

## 📂 关键文件路径速查
- `package.json` — workspaces + 多协议依赖（claude-agent-sdk / opencode-sdk / ACP / MCP）
- `apps/hook` — Agent hook 注入（计划/收工触发评审面）
- `apps/inbox` — Plannotator Inbox 收件箱
- `apps/review` — 浏览器评审 UI（markdown/HTML/diff）
- `packages/server` `packages/core` `packages/ui` — 评审服务/核心/UI
- `apps/vscode-extension` `apps/cline-plugin` `apps/openclaw-plugin` `apps/dsh-plugin` `apps/pi-extension` `apps/opencode-plugin` — 各 harness 接入
- 官网：https://plannotator.ai/ ｜ 文档：https://docs.plannotator.ai/
