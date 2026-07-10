# addyosmani/agent-skills — 把整个软件生命周期编码成 Agent 技能

> **调研日期**: 2026-07-11 | **Stars**: 76,686⭐ (当日 +1,114) | **Forks**: 8,235
> **语言**: JavaScript | **许可**: MIT | **创建**: 2026-02-15 | **最近推送**: 2026-07-10
> **作者**: Addy Osmani (Google Chrome 团队著名工程师) | **仓库**: https://github.com/addyosmani/agent-skills

---

## 项目亮点（差异化）

- **全生命周期覆盖（Define→Plan→Build→Verify→Review→Ship）**：24 个技能覆盖从想法打磨、API/UI 设计、安全、性能、CI/CD、可观测性到上线，是三个主流"Agent 技能集"中覆盖面最广的。
- **反合理化（Anti-rationalization）机制**：每个技能内置"Agent 用来跳过步骤的借口表 + 逐条反驳"和 Red Flags，对抗"我稍后补测试"这类偷懒。
- **并行审查 Persona**：`/ship` 把 `code-reviewer`/`security-auditor`/`test-engineer`/`web-performance-auditor` 四个角色并行扇出，合并成 go/no-go。
- **三层 eval 框架（repo 内置）**：结构检查 / 路由与描述词汇检查（CI 可跑）/ 真实执行轨迹评分——这是三个框架中唯一在仓库内做全量技能度量的。
- **8 个 slash 命令 1:1 映射阶段** + `/build auto` 一次审批跑完整计划（保留验证、移除任务间人工卡点）。

## 项目全景

agent-skills 由 Addy Osmani 维护，把 Google 工程文化（《Software Engineering at Google》、eng-practices）里"资深工程师写生产代码时的纪律"编码成 Agent 可一致执行的技能。核心理念：AI 编码 Agent 默认走最短路径，会跳过 spec、测试、安全审查——技能用带步骤、检查点、出口标准的"工作流"而非"参考文档"来强制这些纪律。

它不是一个 runtime，而是纯 Markdown 技能包，通过 `npx skills add`（vercel-labs/skills CLI，覆盖 70+ Agent）或各工具原生插件机制安装。社区治理上接受并合并社区贡献，且每个技能都带 eval。

## 核心架构

```
agent-skills/
├── skills/                         # 24 技能 (23 生命周期 + 1 meta)
│   ├── interview-me/ idea-refine/ spec-driven-development/   # Define
│   ├── planning-and-task-breakdown/                          # Plan
│   ├── incremental-implementation/ test-driven-development/ context-engineering/
│   │   source-driven-development/ doubt-driven-development/
│   │   frontend-ui-engineering/ api-and-interface-design/   # Build
│   ├── browser-testing-with-devtools/ debugging-and-error-recovery/  # Verify
│   ├── code-review-and-quality/ code-simplification/ security-and-hardening/
│   │   performance-optimization/                             # Review
│   ├── git-workflow-and-versioning/ ci-cd-and-automation/ deprecation-and-migration/
│   │   documentation-and-adrs/ observability-and-instrumentation/ shipping-and-launch/  # Ship
│   └── using-agent-skills/        # Meta: 任务→技能 路由器
├── agents/                         # 4 个专家 persona (code-reviewer/test-engineer/security-auditor/web-perf)
├── references/                     # 7 份补充 checklist (Definition of Done 等)
├── hooks/                          # 会话生命周期钩子
├── .claude/commands/ .gemini/commands/ commands/  # 8 个 slash 命令 (多工具)
├── plugin.json                     # Antigravity 插件清单
└── docs/                           # 各工具安装指南 + comparison.md
```

**技能解剖（统一结构）**：每个 `SKILL.md` = Frontmatter(name/description/Use when) + Overview + When to Use + Process(步骤) + Rationalizations(借口+反驳) + Red Flags + Verification(证据要求)。设计原则：Process not prose；Verification 不可协商；Progressive disclosure（SKILL.md 入口，references 按需加载，控 token）。

## 源码深度解读

**1. 生命周期相位作为一等公民**
与 Superpowers 的"单线 pipeline"、Pocock 的"工具箱"不同，agent-skills 以 SDLC 相位组织：8 个 slash 命令（`/spec` `/plan` `/build` `/test` `/review` `/code-simplify` `/ship` `/webperf`）一一对应相位，外加 `/build auto` 把"批准计划→自主实现全部任务"压缩成一次通过（仍逐任务 TDD、逐任务提交、失败/风险步骤暂停）。这让"feature 从 spec 到上线、每相位有人工卡点"成为默认形态。

**2. using-agent-skills 元技能路由**
`skills/using-agent-skills/SKILL.md` 是 meta 路由器：把进入的工作映射到正确技能，并定义共享操作规则。技能也按"正在做什么"自动触发（设计 API → `api-and-interface-design`，写 UI → `frontend-ui-engineering`），无需手动点名。

**3. eval 框架是真实差异点**
`docs/skill-anatomy.md` 规范 + `evals/`：Tier1 查结构；Tier2 确定性检查每个技能 description 是否含用户真实说法的词汇、是否存在路由冲突（可在 CI 跑）；Tier3 把 Agent 真实执行轨迹按每技能期望评分。这是三个框架里唯一"技能本身是否工作"可被测的——描述或路由回归会 fail CI，而非日后神秘地"技能没触发"。

## 社区口碑

- **正向**：作者背书强（Addy Osmani 的工程师方法论可信度高）；覆盖面与"团队统一词汇/看护栏"定位清晰；反合理化表被社区视为对抗 Agent 偷懒的实用创新；Trendshift 榜单在列。
- **定位语**：README 直言"不是通用 prompt，而是把生产级与原型级工作区分开的观点鲜明的流程化工作流"。
- **时机**：2026-07-10 当日 Trending +1,114，稳居头部。

## 竞品对比（基于官方 docs/comparison.md 三方对照）

| | **agent-skills** | **Superpowers** (obra) | **Matt Pocock's skills** |
|---|---|---|---|
| 核心思想 | 把完整资深工程生命周期编码成技能 | 建立在可组合技能上的完整方法论 | 一位专家日常 Claude Code 工作流开源 |
| 组织原则 | SDLC 相位（Define→Ship） | 单一纪律循环：brainstorm→plan→execute→review | 聚焦、可组合的指令工具箱 |
| 目录规模 | 24 技能（全周期） | ~14 技能（内循环深） | ~30 技能（含 in-progress/deprecated） |
| 入口 | 相位 slash 命令 + `/build auto` | 技能链式 pipeline | slash 命令（/grill-me /tdd /to-prd） |
| 标志机制 | 反合理化表 + Red Flags + 并行 persona + 三层 eval | 子 Agent 驱动开发 + 任务审查 + worktree 隔离 | grilling 质询循环 + user/model-invoked 拆分 |
| 质量度量 | repo 内置目录级 eval（CI） | 方法论压力测试为核心；eval 独立 repo | 无 repo 内置 eval |
| 工具覆盖 | 最广（Claude/Cursor/Gemini/Antigravity/OpenCode/Windsurf/Copilot/Kiro/Codex） | 极广（含 Kimi/Factory Droid/Pi） | Claude Code 优先 |
| 最佳场景 | 整 feature 端到端带每相位卡点 | 大块模糊任务放手长跑 | 快速聚焦日常循环、尤其需求澄清 |

**真实对照实验（Om Mishra, 同模型同仓库同 prompt）**：agent-skills 更快进入代码（~8min vs ~12）且跑更多验证（7 vs 5，含全测试套件，额外抓到一个 feature 外兼容问题）；Superpowers 投入更多前瞻架构推理。结论：广度纪律验证 vs 重前瞻推理，按任务选。

## 核心研判

**优势**
- 唯一覆盖"安全→性能→CI/CD→可观测性→上线"全周期，团队若要统一 Agent 使用标准，相位命令+persona+checklist+eval 让它最契合。
- 反合理化 + eval 框架把"Agent 是否守纪律、技能是否真触发"变成可检查项，而非玄学。

**局限 / 风险**
- 相对 Superpowers 缺少单一的"放手长跑"强叙事；相对 Pocock 在需求质询上不如 grilling 锐利。
- 三框架均未解决"跨会话持久记忆"这一共同前沿。
- 不要把它和另一个框架同时作为 active router（meta 技能抢 `/tdd` 命令名、路由逻辑冲突）。

**定位**：团队/工程组织落地"Agent 按生产纪律写代码"的首选；个人若偏好轻量，可从 Pocock 起步、按需 cherry-pick 单个技能。

## 关键文件速查

| 路径 | 功能 |
|------|------|
| `skills/using-agent-skills/SKILL.md` | Meta 路由器 + 共享操作规则 |
| `skills/spec-driven-development/SKILL.md` | PRD 编写（目标/结构/风格/测试/边界） |
| `skills/test-driven-development/SKILL.md` | RED-GREEN-REFACTOR + 测试金字塔 + Beyonce Rule |
| `skills/code-review-and-quality/SKILL.md` | 五轴审查 + 变更尺寸 + 严重度标签 |
| `skills/doubt-driven-development/SKILL.md` | CLAIM→EXTRACT→DOUBT→RECONCILE→STOP 对抗性审查 |
| `agents/code-reviewer.md` 等 4 个 | 专家 persona（Staff Engineer 视角） |
| `references/definition-of-done.md` 等 7 份 | 补充 checklist |
| `docs/comparison.md` | 与 Superpowers / Pocock 的诚实三方对照 |
| `docs/skill-anatomy.md` | 技能格式规范 + eval 框架说明 |
| `plugin.json` | Antigravity 插件清单 |
