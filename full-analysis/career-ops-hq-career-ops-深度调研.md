# 🔬 career-ops-hq/career-ops - 全方位深度调研

## 📌 一句话定位
`career-ops-hq/career-ops` 是一个跑在 **AI 编码 CLI（Claude Code / Codex / OpenCode / Antigravity / Cursor / Copilot）里的「AI 求职指挥中心」agent skill**——粘贴 JD 或 URL 即可自动评估岗位、生成 ATS 优化简历/PDF、追踪投递、模拟面试、起草外联邮件，全过程本地运行、隐私可控。

## ⭐ 项目亮点
- **爆发式增长 + 极高参与度**：72.6k⭐ / 13.7k fork（2026-04-04 创建，截至 2026-09-24 仍每日提交），fork 数比同类 skill 高一个量级，说明大量用户把它当"可改的私人求职系统"在用。
- **30+ 模式一站式**：`scan`（扫 portal 发现岗位）/ `discover`（解析公司列表）/ `deep`（公司深研）/ `pdf`/`text`/`latex`（多格式简历）/ `cover`/`email`（求职信+邮件）/ `tracker`（投递看板）/ `interview`/`interview-prep`/`interview/practice`（面试准备与陪练）/ `offer-prep`（合同逐条过）/ `patterns`（拒信规律）/ `upskill`（技能缺口）等。
- **多 harness 同构分发**：同一份 `SKILL.md` 同时铺到 `.claude/`、`.cursor/`、`.codex/`、`.agents/`、`.antigravitycli/`、`.github/`（Copilot instructions），并配套 `.claude-plugin` / `.codex-plugin` / `.cursor` 插件清单——这正是"框架厂商/社区发 Skill"的标准姿势。
- **auto-pipeline 零配置**：识别到 JD 文本或 URL 即自动跑「评估→报告(A-H 评分+全球 1-5 分)→PDF→tracker」，并输出本地化语言。
- **区域化市场逻辑**：内置 `eu-swe` / `eu-fintech` 等区域模式（如扫描 21 个欧盟 fintech portal、零 token 成本），靠 `config/profile.yml` 的 `language.modes_dir` 切换市场词汇与评估规则。

## 🏗️ 项目架构全景
### 仓库结构（main 树，关键部分）
- `.claude/skills/career-ops/SKILL.md` 等：各 harness 入口（router），内容一致。
- `modes/`：**核心逻辑目录**——`_shared.md`（共享指令）、`_profile.md`（候选人画像）、`_custom.md`（用户 house rules）、`{mode}.md`（每个模式的具体步骤）。
- `config/profile.yml`：候选人画像与输出语言、市场模式配置。
- `data/`：`pipeline.md`（待处理 URL 收件箱）、`agent-inbox.md`（跨会话排队）、tracker 等本地状态。
- `.github/`：成熟工程化——`copilot-instructions.md`、`agents/*.agent.md`（address-review / adopt-pr / docs-drift / i18n-sync / pr-brief / repro）、`scripts/ci-approve.mjs`、`direction-gate.mjs`（方向闸门）、`gfi-handoff.mjs`，以及含 `i-got-hired.yml`（社区成功案例驱动）的 issue 模板。

### 运行模型
- **PROJECT_ROOT 哨兵解析**：从 SKILL.md 位置向上回溯，直到找到同时含 `AGENTS.md` 与 `modes/` 的目录，所有路径都相对它解析——支持嵌套 checkout（如 `Development\career-ops`）。
- **Context Loading by Mode**：多数模式加载 `_shared + _profile + _custom + {mode}` 四件套；`scan` / `apply`（Playwright）/ `pipeline`（≥3 URL）会被委派给 `Agent(subagent_type="general-purpose")` 子代理，主会话只注入上述四件套内容。

## 💡 应用场景与启发
- **对在校生（推免 / 校招）极实用**：本地评估 JD（A-H 报告 + 全球 1-5 分）、生成 ATS 友好简历、准备技术/行为面试、追踪几十个投递——相当于一个不泄露隐私的私人求职 OS。
- **「Skill 即可改系统」范式**：它没有后端、不联网请求第三方，全靠 LLM + 本地 Markdown 状态文件驱动，降低了对 SaaS 的依赖；把"求职方法论"沉淀成可版本化、可 fork 的指令。
- **对自研 agent 的启发**：`modes/` 分层（shared/profile/custom/mode）+ 子代理委派 + 方向闸门 CI，是"把一套复杂工作流做成可审计 skill"的高质量范本，可借鉴到 paper-companion、灵感闪记等专家。

## 🧠 核心源码解读
### 1. Mode Routing 表（SKILL.md 节选）
```text
| Input | Mode |
| (empty) | discovery -- Show command menu |
| JD text or URL (no sub-command) | auto-pipeline |
| pdf | pdf |  text | latex | cover | email | tracker | interview | ...
```
auto-pipeline 检测逻辑：若 `$mode` 不是已知子命令且含 JD 关键词（"responsibilities"/"requirements"/"about the role" 等）或 JD URL，则执行 auto-pipeline；否则展示 discovery 菜单。

### 2. PROJECT_ROOT 解析（防路径错乱）
```text
start at the skill file's directory and walk upward until the nearest directory
containing both AGENTS.md and modes/. Resolve every path against PROJECT_ROOT,
never against the process's current working directory.
```
这避免了"命令从子目录启动导致读写错文件"的常见 skill bug。

### 3. 子代理委派（scan/apply/pipeline）
```python
Agent(
  subagent_type="general-purpose",
  prompt="[output language directive]\n\n[content of modes/_shared.md]\n\
[content of modes/_profile.md if exists]\n[content of modes/_custom.md if exists]\n\
[content of modes/{mode}.md]\n\n[invocation-specific data]",
  description="career-ops {mode}"
)
```

## 🌐 全网口碑画像
- **社区信号**：13.7k fork + `.all-contributorsrc` 多贡献者 + issue 模板含「i-got-hired」成功故事，说明社区以"真实拿到 offer"为飞轮自传播；`direction-gate.mjs` 等 CI 体现强工程纪律。
- **定位共识**：被视作"本地优先、agent 原生的求职操作系统"，区别于 Teal/Simplify 等闭源 SaaS。
- **注意点**：项目极新（2026-04 起），API/模式仍在快速演进；默认输出语言为英文（`language.output` 默认 `en`），国内校招需改 `config/profile.yml` 并准备中文市场词表。

## ⚔️ 竞品对比
| 维度 | career-ops | Teal / Simplify（SaaS） | 传统 LaTeX 简历 |
|------|-----------|------------------------|----------------|
| 运行位置 | 本地 CLI（隐私） | 云端（需上传简历） | 本地 |
| 能力面 | 评估+简历+面试+追踪+外联 一站式 | 偏简历优化/投递 | 仅排版 |
| 可定制 | fork 即改（全 Markdown） | 受限 | 高但手工 |
| 依赖 | 需 LLM CLI 环境 | 订阅 | 编译链 |

## 🎯 核心研判
- **优势**：本地优先 + 全链路 + 可 fork 改造，是把"求职方法论"产品化的优质样本；对正在准备推免/校招的用户价值很高（JD 评估、ATS 简历、面试陪练）。
- **风险**：强依赖 LLM CLI（Claude Code/OpenCode 等）环境与英文默认输出；模式多但文档散落各 `modes/*.md`，新手上手成本不低；极新项目、接口可能变动。
- **趋势**：与"agent 原生技能"浪潮同频（vercel-labs/skills、greensock/gsap-skills 同源趋势），是「框架/社区发 Skill」的代表作之一。

## 📂 关键文件路径速查
- `.claude/skills/career-ops/SKILL.md` — router（模式路由 + PROJECT_ROOT 解析 + 子代理委派）
- `modes/` — `_shared.md` / `_profile.md` / `_custom.md` / `{mode}.md`（核心逻辑）
- `config/profile.yml` — 画像、输出语言、市场模式
- `data/pipeline.md` / `data/agent-inbox.md` — 本地状态
- `.github/plugin/plugin.json`、`.claude-plugin/marketplace.json` — 插件分发清单
- 仓库：`https://github.com/career-ops-hq/career-ops`
