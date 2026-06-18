obra/superpowers — 深度调研报告⚡ 一句话定位：GitHub Star 第五多的项目（19.7 万⭐）——一个 Agent 技能框架 & 软件开发方法论，支持 Claude / Codex / Cursor / Gemini 等多平台，通过插件系统实现跨 Agent 的 Skill 复用。📋 基本档案字段值⭐ Stars197,310🗓️ 创建时间2025-10-09（非常新，仅 7 个月）🔄 最近提交2026-05-14🔖 默认分支main💻 主要语言Shell（框架本身）+ 各插件语言📦 插件生态Claude / Codex / Cursor / Gemini🏛️ 架构全景superpowers 是一个非常新的项目，但发展极快。从仓库结构看：superpowers/├── AGENTS.md              ← Agent 行为规范定义├── 
- `CLAUDE.md`              ← Claude 专用配置├── GEMINI.md              ← Gemini 专用配置├── 
- `README.md`              ← 项目主文档├── .claude-plugin/       ← Claude 插件定义│   └── marketplace.json   ← 插件市场├── .codex-plugin/         ← OpenAI Codex 插件├── .cursor-plugin/        ← Cursor 插件└── .opencode/            ← OpenCode 集成    └── plugins/superpowers.js核心洞察：superpowers 本身是一个「框架 + 方法论」，而不是一个具体的工具。它定义了 Agent 软件开发的工作流程，并将这个流程封装为各主流 AI 编码工具的插件。🔧 核心机制解析Skill 系统架构superpowers 的 Skill 是一种结构化的 Agent 任务模板，类似于：superpowers/├── skills/│   ├── writing-plans/     ← 计划写作技能│   ├── review-loop/       ← 审查循环技能│   └── ...               ← 更多技能├── workflows/│   └── subagent-driven/   ← 子 Agent 驱动开发流程└── docs/Subagent 驱动开发流程这是 superpowers 的核心方法论——用 Agent 驱动 Agent，形成开发流水线。一个典型的流程：主 Agent 接收任务调用 writing-plans Skill 制定计划调用 review-loop Skill 进行审查分配子 Agent 执行具体模块通过 finishing-a-development-branch 汇总结果插件化多平台支持插件平台状态.claude-pluginAnthropic Claude✅ 完整支持.codex-pluginOpenAI Codex✅ 完整支持.cursor-pluginCursor IDE✅ 完整支持.opencodeOpenCode✅ 集成🌐 全网口碑分析好评共识（从 Issue 推断）方法论价值高 — 将优秀的开发实践固化进工作流跨平台一致性好 — 在不同 Agent 间复用同一套方法论模块化设计 — Skill 可以独立使用、组合踩坑高发区（从最新 Issue 分析）Issue内容类型#1577review-loop rust edition 2015 默认问题bug#1576writing-plans 不强制 TDD，导致跳过测试bug#1574不遵守 plan-tune 问题偏好设置enhancement#1569Gemini CLI 模型路由偏向 Flash/Litebug#1561SessionStart hook 在 Windows 上报错bug#1566生命周期扩展系统需求enhancement观察：superpowers 是一个非常活跃的项目（7 个月，1577 个 issue），且对 Windows 的支持还有 bug 需要修复。🔍 竞品对比竞品定位vs superpowersLangChain AgentsAgent 应用开发框架更偏底层库，superpowers 偏方法论AutoGPT自主 Agent 任务执行superpowers 更结构化，有人工反馈环CrewAI多 Agent 协作框架CrewAI 侧重多 Agent 协作，superpowers 侧重开发流程Devin (Cognition)AI 软件工程师闭源，superpowers 开源可审计superpowers 的差异化：它不是一个具体的 Agent，而是一套「如何用 Agent 高效开发软件」的方法论 + 工具链。这个定位让它可以横跨多个 Agent 平台使用。

## 🎯 核心研判

核心

### 优势

方法论护城河 — 积累的是最佳实践，不是代码本身多平台插件生态 — 一个 Skill 定义，多个 Agent 平台复用社区快速跟进 — 7 个月 1577 issues，说明开发者高度关注与 OpenClaw 的协同 — 当前已在 .claude-plugin 中集成，OpenClaw 也可受益主要

### 风险

Windows 支持不完善 — SessionStart hook 报错是生产环境

### 风险

依赖上游 Agent 平台 — 如果 Claude/Codex 改变 API，插件需要同步更新TDD 执行不完整 — writing-plans Skill 目前不强制 TDD，导致测试可能被跳过非常新 — 7 个月的项目，API 和方法论尚未稳定趋势判断superpowers 的出现代表了 AI Agent 开发从「用 Agent 写代码」向「用 Agent 管理系统开发流程」的升级。它的 Skill 抽象层次比 LangChain 更高（偏方法论而非技术实现），这个定位在 2026 年的 Agent 生态中有独特的战略价值。数据来源：gh repo view / gh issue list / gh git trees，调研时间 2026-05-19
