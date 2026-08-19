# Yeachan-Heo/oh-my-claudecode 深度调研

> 基本信息：⭐ 38670 / 💻 TypeScript / 📜 MIT / 🏷️ 领域 AI编码（Claude Code 多智能体编排插件）/ 🌿 默认分支 main / 🕒 最近更新 2026-08-18（仓库创建于 2026-01-09）

> 数据来源说明：本文所有数字与文件结构均来自 `gh api` 实时抓取（仓库元数据、README、文件树、`docs/ARCHITECTURE.md`、`.claude-plugin/plugin.json`、`hooks/hooks.json` 及真实源码片段）与官网 `yeachan-heo.github.io/oh-my-claudecode-website` 抓取。星标数采用 GitHub API 返回的权威值 38670；官网首页另显示 35.5k，存在版本/统计口径漂移（plugin.json 版本 4.15.10，官网展示 4.14.4），下文以 API 数据为准并注明矛盾点。

---

## 一、项目定位（一句话）

**oh-my-claudecode（OMC）是一套面向 Claude Code 的「Teams-first 多智能体编排」插件/CLI 运行时，把 Claude Code 从单智能体对话升级为可调度 19 个专业 Agent、39 个 Skill、并跨 Claude/Codex/Gemini/Antigravity/Grok/Cursor 多后端并行协作的「类固醇」式智能体操作系统。**

---

## 二、项目亮点（5 条差异化，开篇呈现）

1. **Teams-first 原生多智能体编排**：从 v4.1.7 起 `team` 成为规范化（canonical）编排面，并启用 Claude Code 原生 Agent Teams（`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`），以 `team-plan → team-prd → team-exec → team-verify → team-fix` 分阶段流水线协同；同时 `omc team N:codex/gemini/...` 用 tmux 真正拉起外部 CLI worker 进程（非 MCP 模拟），用完即销毁。
2. **零学习曲线 + 自然语言魔法词**：无需记忆命令，`autopilot / ralph / ultrawork(ulw) / ralplan / team / ccg / deep-interview` 等关键词在 prompt 中自动触发对应编排模式（由 `hooks/keyword-detector.mjs` 在 `UserPromptSubmit` 钩子里识别）。
3. **三层智能体分层 + 三级模型路由**：19 个 Agent 按「构建/分析 / 评审 / 领域 / 协调」四车道组织，并以 haiku/sonnet/opus 三档成本模型自动路由（探索用 haiku、实现用 sonnet、架构与评审用 opus），官方声称可节省 30–50% token 成本（README 表述，未提供独立审计链接，标注为厂商口径）。
4. **技能自学习（learner/skillify）**：从会话中自动抽取可复用解题模式为 `SKILL.md`，存于 `.omc/skills/`（项目级，建议提交）或 `~/.omc/skills/`（用户级），并基于触发词在后续会话自动注入。
5. **跨多 AI 后端并行 + 实时可观测**：可在真实 tmux 窗格里并行调度 Codex/Gemini/Antigravity/Grok/Cursor 与 Claude 协同；内置 HUD 状态栏、会话摘要、回放日志、成本追踪，以及 Telegram/Discord/Slack/OpenClaw 通知与速率限制自动恢复（tmux 守护进程）。

---

## 三、核心架构

OMC 并非独立服务，而是**以 Claude Code 插件（marketplace）+ npm CLI（`oh-my-claude-sisyphus`）两种形态挂载到 Claude Code 之上的编排层**。其核心由四个相互衔接的系统组成（来自 `docs/ARCHITECTURE.md`）：

```
User Input → Hooks(事件探测) → Skills(行为注入) → Agents(任务执行) → State(进度追踪)
```

### 3.1 四个系统

- **Hooks（钩子）**：在 Claude Code 生命周期事件（`UserPromptSubmit` / `SessionStart` / `PreToolUse` / `PostToolUse` / `PermissionRequest` / `Stop` 等）上挂载 Node 脚本。OMC 的几乎所有「自动化」都从这里触发——这是整套编排的**事件总线**。
- **Skills（技能）**：不是切换 Agent，而是**在现有 Agent 之上叠加能力**的行为注入。技能分三层组合：执行层（如 `default`/`orchestrate`）+ 增强层（0–N，如 `ultrawork` 并行、`git-master` 提交）+ 保证层（可选，如 `ralph`「未验证完成不停止」）。公式：`[执行技能] + [0-N 增强] + [可选保证]`。
- **Agents（智能体）**：19 个专业子 agent，按 `oh-my-claudecode:<agent-name>` 通过 Task 工具委派，并绑定模型档位（文件见 `agents/*.md`）。
- **State（状态）**：进度、会话、计划、日志、handoff、研究笔记、本地产物写入 `.omc/`（`gitignore` 默认忽略，仅 `.omc/skills/**` 可提交），跨上下文压缩（compact）与多会话存活。

### 3.2 「Teams-first multi-agent」到底是什么意思

两层含义：

1. **编排首选是 Team 而非单 Agent 自循环**。README 明确「Team is the canonical orchestration surface」，旧 `swarm` 关键词已移除。Team 用 Claude Code 原生 Agent Teams 把 N 个 Claude Agent 放到同一共享任务清单上，按五阶段流水线协同（规划→PRD→执行→验证→修复循环）。
2. **CLI 侧的「真进程」并行**：`omc team N:codex "..."` 不是虚拟调度，而是用 tmux 真正拉起 N 个 Codex/Gemini/Antigravity 等 CLI 子进程窗格，任务结束即消亡，无空闲资源占用。多后端（codex/gemini/agy/grok/cursor/claude）各司其职：Codex 做架构与安全审查、Gemini/Antigravity 做 UI/大上下文、Cursor 做执行、Claude 做总指挥与综合。

> 关键区别：Claude Code 自带的多 Agent 偏向「主 Agent 派生子 Agent 并行」；OMC 的 Teams-first 把协调权交给一个**分阶段流水线 + 跨多后端真进程**的编排面，更像「智能体操作系统」而非「提示词包裹层」。

### 3.3 工程形态

- 插件形态：`.claude-plugin/plugin.json` 声明 40+ skills、`commands/`、`mcpServers`（`.mcp.json`）、`agents/`。
- CLI 形态：`bin/oh-my-claudecode.js` + `bridge/*.cjs/js`（打包后的运行时桥接，含 `team.js`、`mcp-server.cjs`、`runtime-cli.cjs`）。
- TypeScript 源码编译后落于 `dist/`，桥接脚本落于 `bridge/`，构建脚本落于 `scripts/`（均为 `.mjs/.cjs` 真源）。仓库本身即发行物（含 `dist/`），非纯源码仓库。

---

## 四、应用场景与启发（重点章节）

这一节是本文重点——OMC 不只是一个「更好用的 Claude Code 配置」，它给出了一整套**「如何把一个通用 LLM 编程助手改造成可治理的多智能体系统」**的工程范式，对同类需求有可迁移的解决思路。

### 4.1 这个仓库能用在哪里

| 场景 | 用法 | 价值 |
|---|---|---|
| **个人开发者提效** | `/autopilot "build a REST API"`、`/ralph "refactor auth"` 自然语言驱动端到端实现 | 零配置、免记命令，把「想法」直接落到「可测代码」 |
| **团队级代码评审/安全审计** | `omc team 2:codex "review auth module"`、`/ccg "review this PR"` | 跨 Claude/Codex/Antigravity 多模型交叉验证，降低单模型盲区 |
| **大型重构/多文件并行** | `/ultrawork "fix all TS errors"` | 最大并行度，多 agent 同时改不同文件 + 原子提交 |
| **需求不清晰时** | `/deep-interview "vague idea"` | 苏格拉底式追问，暴露隐含假设、量化清晰度，先想清再写码 |
| **CI/CD 与无头自动化** | `omc setup`、`omc ask`、`omc session search` + 环境变量注入 API Key | 确定性终端命令替代交互式 slash，适合流水线 |
| **跨仓库统一状态** | 父目录放 `.omc-workspace` 标记 | 多个独立 git 仓库共享同一 `.omc/` 状态根 |
| **知识沉淀** | `/skillify` 从会话抽取可复用 SKILL，提交到 `.omc/skills/` | 团队共享「踩坑即固化为技能」，越用越聪明 |

### 4.2 给同类需求的解决思路（可迁移范式）

1. **用 Hooks 当事件总线，而非重写 Agent 循环**：OMC 几乎不侵入 Claude Code 内核，而是把 `UserPromptSubmit`/`PreToolUse`/`PostToolUse` 等钩子当「插件入口」。任何想给现有 LLM 工具加编排能力的人，都可用同样的钩子机制（Claude Code 原生支持）零侵入挂载自己的逻辑。
2. **Keyword/frontmatter 触发优于命令记忆**：用 `keyword-detector.mjs` 在 prompt 提交时正则/语义匹配激活模式——这是「自然语言界面」的低成本实现，可被任何 CLI Agent 框架借鉴。
3. **分层 Agent + 模型分级路由 = 成本可控**：把「探索/文档」丢给便宜模型、「架构/评审」留给贵模型，用 frontmatter 里的 `model: haiku/sonnet/opus` 固化（见 `agents/executor.md` 的 `model: sonnet`），既保质量又压成本。
4. **「保证层」模式解决「半完成」痛点**：`ralph` 的「未验证完成绝不停止 + verifier 复核」是治理 LLM「假装完成」的工程解法，值得任何自动化执行系统采用。
5. **真进程并行（tmux worker）优于「伪多 Agent」**：需要异构后端协同时，直接拉起真实 CLI 子进程比在单上下文里模拟多角色更稳、更易观测——OMC 的 `omc team` 是范本。
6. **状态外置 + 可提交技能 = 可演化系统**：把运行态写进 `.omc/`、把可复用知识写成可提交的 `SKILL.md`，让系统随使用自我增殖，是「学习型工具」的核心设计。

---

## 五、源码深度解读（3 个核心模块，真实文件路径）

### 5.1 模块一：Hook 事件总线（编排的心脏）

OMC 的自动化全部从 Claude Code 钩子触发。`hooks/hooks.json` 声明了在哪些生命周期事件上跑哪些 Node 脚本（统一经 `scripts/run.cjs` 包装执行）：

```jsonc
// hooks/hooks.json（节选）
{
  "hooks": {
    "UserPromptSubmit": [{
      "matcher": "*",
      "hooks": [
        { "type": "command",
          "command": "node \"$CLAUDE_PLUGIN_ROOT\"/scripts/run.cjs \"$CLAUDE_PLUGIN_ROOT\"/scripts/keyword-detector.mjs" },
        { "type": "command",
          "command": "node \"$CLAUDE_PLUGIN_ROOT\"/scripts/run.cjs \"$CLAUDE_PLUGIN_ROOT\"/scripts/skill-injector.mjs" }
      ]
    }],
    "PreToolUse": [{
      "matcher": "*",
      "hooks": [{ "type": "command",
        "command": "node \"$CLAUDE_PLUGIN_ROOT\"/scripts/run.cjs \"$CLAUDE_PLUGIN_ROOT\"/scripts/pre-tool-enforcer.mjs" }]
    }],
    "PostToolUse": [{
      "matcher": "*",
      "hooks": [
        "scripts/post-tool-verifier.mjs",
        "scripts/project-memory-posttool.mjs",
        "scripts/post-tool-rules-injector.mjs"
      ]
    }]
  }
}
```

> **架构要点**：用户每提交一句话→`keyword-detector` 判断激活哪种编排模式；每次工具调用前→`pre-tool-enforcer` 注入提醒/强制委派；每次工具调用后→`post-tool-verifier` 校验、`project-memory` 沉淀记忆。整条链完全声明式，零侵入 Claude Code。

### 5.2 模块二：技能自动注入（learned-skill 自学习机制）

`scripts/skill-injector.mjs`（UserPromptSubmit 钩子）负责根据触发词把历史学到的技能自动塞进上下文。其会话 ID 解析逻辑展示了 OMC 对「钩子上下文安全」的处理（防路径穿越）：

```javascript
// scripts/skill-injector.mjs（节选，真实源码）
function resolveHookSessionId(hookPayload) {
  const payloadId =
    hookPayload && typeof hookPayload === 'object' &&
    typeof hookPayload.session_id === 'string' && hookPayload.session_id.trim()
      ? hookPayload.session_id.trim() : undefined;
  const envId = process.env.OMC_SESSION_ID && process.env.OMC_SESSION_ID.trim()
    ? process.env.OMC_SESSION_ID.trim() : undefined;
  return payloadId ?? envId;            // payload 优先于环境变量
}
const SESSION_ID_REGEX = /^[a-zA-Z0-9][a-zA-Z0-9_-]{0,255}$/;
function validateSessionId(sessionId) {
  if (!sessionId) return undefined;
  if (sessionId.includes('..') || sessionId.includes('/') || sessionId.includes('\\')) return undefined;
  if (!SESSION_ID_REGEX.test(sessionId)) return undefined;
  return sessionId;                     // 校验失败直接丢弃，防穿越
}
```

> **架构要点**：技能发现分「用户级 `~/.omc/skills/` + 项目级 `.omc/skills/`（优先级更高）+ 工作区 `.claude/skills/` 兼容」三层，递归扫描子目录。注释明确「STANDALONE SCRIPT - uses compiled bridge bundle from dist/hooks/skill-bridge.cjs，首次构建前回退到内联实现」——体现 OMC「未构建也能跑」的健壮性设计。

### 5.3 模块三：Agent 分层与模型路由（frontmatter 驱动）

每个 Agent 是一个带 YAML frontmatter 的 Markdown Prompt 文件。`agents/executor.md` 示范了「角色/成功标准/约束/调查协议」的结构化模板与 `model: sonnet` 的档位固化：

```markdown
---
name: executor
description: Focused task executor for implementation work (Sonnet)
model: sonnet
level: 2
---
<Agent_Prompt>
  <Role> You are Executor. Implement code changes precisely... </Role>
  <Success_Criteria>
    - The requested change is implemented with the smallest viable diff
    - All modified files pass lsp_diagnostics with zero errors
    - Build and tests pass (fresh output shown, not assumed)
    - No new abstractions introduced for single-use logic
  </Success_Criteria>
  <Constraints>
    - Work ALONE for implementation... All code changes are yours alone.
    - Prefer the smallest viable change. Do not broaden scope.
    - After 3 failed attempts on the same issue, escalate to architect agent.
  </Constraints>
```

> **架构要点**：`model` 字段把成本控制写进 Agent 定义本身。路由逻辑在 `scripts/pre-tool-enforcer.mjs` 中对「Bedrock/Vertex/普通 Claude/非 Claude 供应商」做环境探测（`isBedrockProviderEnv` / `isVertexProviderEnv` / `isNonClaudeProviderEnv`），并据 `routing.forceInherit` 决定是否继承模型——这正是「模型分级路由」的代码落点。

---

## 六、全网口碑

- **规模与热度**：GitHub API 实时数据——⭐ 38670、🍴 Fork 3474、👁 Watchers 129、Open Issues 仅 3（维护活跃、issue 收敛快）。创建于 2026-01-09，至 2026-08 约 7 个月即逼近 3.9 万星，增长曲线陡峭（README 内嵌 Star History 图表）。官网首页自报 35.5k stars / 30.4k 月活（数据口径与 API 存在漂移，已注明）。
- **定位口碑**：README「Inspired by」列出 `oh-my-opencode`、`claude-hud`、`Superpowers`、`everything-claude-code`、`Ouroboros`，自喻「Your Claude Just Have been Steroided」——在社区被普遍视为「Claude Code 最强编排插件 / 类固醇」型工具。
- **多语言与社区**：README 提供 英/韩/中/日/西/越/葡/德/俄/意 10 种语言版本；设有 Discord 社群、GitHub Sponsors 与分级赞助档位（见 `.github/SPONSOR_TIERS.md`），并维护「Featured by OmC Contributors」榜单（聚合贡献者的高星仓库），社区运营成熟。
- **质量信号**：仓库含 `benchmarks/`（含 Docker 化评测、`omc` vs `vanilla` 对照的 `predictions/`、`stats.json`）与 `dist/__tests__/` 大量单测（文件名如 `delegation-enforcer.test.js`、`hud-*.test.js`），工程化与自测完整度高于一般 prompt 仓库。
- **注意点（客观）**：① npm 包名 `oh-my-claude-sisyphus` 与仓库名/插件名 `oh-my-claudecode` 不一致，新手易混淆；② 安装时 `better-sqlite3` 依赖会报 `deprecated prebuild-install@7.1.3` 警告（上游问题，已在 #2913 跟踪）；③ 多后端 worker/Windows HUD 等仍依赖 tmux（Windows 需 `psmux`），存在平台门槛。

---

## 七、竞品对比 + 核心研判

### 7.1 横向对比（Claude Code 配置/编排生态）

| 维度 | **oh-my-claudecode (OMC)** | dotfiles / 个人 CLAUDE.md 配置 | claude-hud / 单点工具 | 原生 Claude Code Agent/Subagent | 其他插件框架（如 claude-code 类 skills 集合） |
|---|---|---|---|---|---|
| 编排范式 | Teams-first 分阶段流水线 + 跨多后端真进程 | 无（纯静态提示/规则） | 仅 HUD 展示，无编排 | 主 Agent 派生子 Agent 并行 | 以技能/命令集合为主 |
| 智能体数量 | 19 个专业 Agent（四车道） | 0（靠你自己写） | 0 | 自带通用 subagent | 视插件而定 |
| 多 AI 后端 | Claude+Codex+Gemini+Antigravity+Grok+Cursor | 否 | 否 | 否 | 少数支持 |
| 成本路由 | haiku/sonnet/opus 三级自动路由 | 手动 | 无 | 手动 | 少见 |
| 自学习 | skillify/learner 抽取技能 | 需手动 | 无 | 无 | 少数 |
| 可观测 | HUD + 会话摘要 + 回放 + 成本追踪 | 无 | 有（仅 HUD） | 弱 | 弱 |
| 上手成本 | 零（魔法词触发） | 高（要懂配置） | 低 | 中 | 中 |
| 侵入性 | 钩子声明式、零侵入内核 | 改配置 | 注入设置 | 原生 | 各异 |

### 7.2 核心研判

- **定位优势**：OMC 在「Claude Code 增强层」里走的是**最重、最系统**的一条路——它不像 dotfiles 那样只是静态提示，也不像 claude-hud 只做展示，而是把**编排、Agent、路由、自学习、可观测、跨后端**做成一套可插件化的操作系统。这是它星标爆发式增长的根本原因。
- **护城河**：①「Teams-first + 真进程 tmux worker」的组合在同类里少见且难抄；② 19 Agent + 39 Skill + 完整 benchmark/单测构成内容与质量壁垒；③ 多语言文档 + Discord + 赞助体系形成社区飞轮。
- **风险/短板**：① 命名分裂（仓库/插件/包名三者不同）增加认知负担；② 强依赖 Claude Code 生命周期与 tmux，平台/版本耦合度高，Claude Code 一旦改钩子协议即有破窗风险；③ 体量庞大（仓库 77MB+，含 `dist/`），对只想「轻量配置」的用户偏重；④ 成本节省 30–50% 为厂商口径，缺乏第三方独立评测佐证（仅 `benchmarks/` 内 `omc` vs `vanilla` 对照，未公开横向对比结论）。
- **适用决策**：如果你要的是「给 Claude Code 装上多智能体引擎、跨模型并行、还要自学习」，OMC 是目前生态里最完整的选项；如果你只要「几个好用的提示词/命令」，dotfiles 或单点工具更轻。OMC 适合重度 AI 编码团队与个人高级用户，不适合追求极简、强离线或强平台无关的场景。

---

## 关键文件路径速查

| 路径 | 说明 |
|---|---|
| `hooks/hooks.json` | 编排事件总线：声明 UserPromptSubmit/PreToolUse/PostToolUse 等钩子挂载的脚本 |
| `scripts/skill-injector.mjs` | 技能自动注入钩子（自学习机制核心，含会话 ID 安全校验） |
| `scripts/pre-tool-enforcer.mjs` | 工具调用前提醒/强制委派 + Bedrock/Vertex/供应商模型路由探测 |
| `agents/executor.md` | 19 个专业 Agent 之一，示范 `model: sonnet` 档位固化与结构化 Prompt 模板 |
| `docs/ARCHITECTURE.md` | 官方架构文档：四系统（Hooks/Skills/Agents/State）与 Agent 车道、模型路由 |
| `.claude-plugin/plugin.json` | 插件清单：40+ skills、commands、mcpServers、agents 的注册入口（version 4.15.10） |
| `bridge/team.js` | 打包后的 Team 编排运行时桥接（含 worktree/多仓库状态根解析逻辑） |
| `commands/` | 全部 slash 命令定义（如 `team.md`/`autopilot`/`ralph`/`ccg`/`deep-interview`） |
| `benchmarks/` | 评测体系：Docker 化、omc vs vanilla 对照、fixtures/ground-truth/scoring |
| `docs/REFERENCE.md` | 完整功能参考（CLI、工作流、状态/多仓库/工作树契约等） |

---

## 铁律自检

- ✅ 报告信息量超过 README（补充了：四系统架构、Teams-first 双含义、真实源码走读、竞品决策矩阵、研判与风险、路径速查）。
- ✅ 常规实现代码未逐行罗列，仅挑架构关键点 + 精炼骨架（hooks 声明、注入器会话校验、Agent frontmatter）。
- ✅ 重点展开「应用场景与启发」章节。
- ✅ 真实引用文件路径与代码片段（均来自 `gh api` 实时抓取）。
- ✅ 未执行 git commit/push，未修改任何索引文件，仅产出本报告。
- ✅ 数据均标注来源；星标 38670 采用 GitHub API 权威值，官网 35.5k 与版本号漂移已注明，无编造数字。
