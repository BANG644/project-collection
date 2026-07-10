# obra/superpowers — 建立在可组合技能上的完整软件开发方法论

> **调研日期**: 2026-07-11 | **Stars**: 251,668⭐ (当日 +1,096) | **Forks**: 22,456
> **语言**: Shell | **许可**: MIT | **创建**: 2025-10-09 | **最近推送**: 2026-07-10
> **作者**: Jesse Vincent (obra, RT/Perl 生态著名黑客, Prime Radiant) | **仓库**: https://github.com/obra/superpowers

---

## 项目亮点（差异化）

- **子 Agent 驱动开发（Subagent-Driven Development）**：每个任务派发一个全新上下文的子 Agent 实现，随后做"规格合规 + 代码质量"两阶段审查，最后用最强模型做整分支审查——长任务可自主跑数小时不偏离计划。
- **Git Worktree 隔离**：并行工作落在独立分支/worktree，互不污染上下文。
- **严格单线 pipeline**：brainstorming → writing-plans → subagent-driven-development/executing-plans → TDD → requesting-code-review → finishing-a-development-branch，技能"强制触发"而非建议。
- **写作技能本身的 TDD**：`writing-skills` 把 TDD 应用到文档——没有先写失败测试，技能不许 ship。
- **极广 harness 覆盖**：Claude Code / Codex / Cursor / Copilot CLI / OpenCode / Kimi / Factory Droid / Antigravity / Pi，几乎全覆盖。

## 项目全景

Superpowers 是"建立在可组合技能上的完整软件开发方法论"，由 obra（Jesse Vincent）与 Prime Radiant 团队打造。它赌注在**自主性与前置推理**：会话启动即退回问你"到底想做什么"，榨出 spec 分块给你读，批准后产出"一个热情但品位差、无判断力、无上下文、讨厌测试的初级工程师也能跟"的实现计划，强调真 RED/GREEN TDD、YAGNI、DRY；说"go"后启动 subagent 驱动开发，Agent 常自主跑几小时不偏离。

它不是 runtime，而是纯 Markdown 技能 + 初始指令（session-start hook 注入 `using-superpowers`）。官方称"技能自动触发，你什么都不用做，你的编码 Agent 就拥有了 Superpowers"。商业上提供企业支持/托管花费（sales@primeradiant.com）。

## 核心架构

```
superpowers/
├── skills/                         # 14 技能
│   ├── brainstorming/              # Socratic 设计细化, 写 dated spec
│   ├── writing-plans/              # 2-5 分钟/任务 的细计划 (精确路径+完整代码+验证)
│   ├── subagent-driven-development/  # 每任务派 fresh subagent + 两阶段审查 + 整支审查
│   ├── executing-plans/            # 批量执行 + 人工检查点
│   ├── test-driven-development/    # RED-GREEN-REFACTOR (含测试反模式参考)
│   ├── systematic-debugging/       # 4 阶段根因 (root-cause-tracing/defense-in-depth)
│   ├── verification-before-completion/  # 确认真修好
│   ├── requesting-code-review/ receiving-code-review/  # 预审查清单 / 回应反馈
│   ├── using-git-worktrees/        # 并行开发分支隔离
│   ├── dispatching-parallel-agents/ # 并发子 Agent 工作流
│   ├── finishing-a-development-branch/  # merge/PR 决策
│   └── writing-skills/ using-superpowers/  # 元: 写技能 / 技能系统导论
├── .claude-plugin/ .codex-plugin/ .cursor-plugin/ .kimi-plugin/ .opencode/ .pi/ .gemini/
├── hooks/  scripts/  tests/  docs/ (plans/ specs/ windows/ porting-to-a-new-harness)
├── AGENTS.md  CL AUDE.md  GEMINI.md  gemini-extension.json  package.json
└── RELEASE-NOTES.md  CODE_OF_CONDUCT.md
```

**基础工作流（6 步强制）**：brainstorming(写 spec) → using-git-worktrees(建隔离工作区) → writing-plans(拆 2-5 分钟任务, 含精确文件路径/完整代码/验证) → subagent-driven-development 或 executing-plans → test-driven-development(RED-GREEN) → requesting-code-review(按严重度报问题, Critical 阻塞) → finishing-a-development-branch(验证测试, 给 merge/PR/keep/discard 选项)。Agent 在任何任务前先查相关技能——是强制工作流，非建议。

## 源码深度解读

**1. subagent-driven-development 的"Fresh subagent per task"哲学**
`skills/subagent-driven-development/SKILL.md` 核心：为每个任务派发一个**全新上下文**的实现子 Agent，你精确构造它的指令与上下文，确保它专注且成功；它**绝不继承你的会话上下文或历史**——你只构造它所需。每个任务后做"规格合规 + 代码质量"两阶段 task review，末尾对整分支做 broad review。用 dot graph 决策树表达"何时用本技能 vs executing-plans（并行会话）"。Narration 规则：工具调用间最多一句短述，ledger 与工具结果即记录——刻意压低主 Agent 上下文占用，把协调工作留在主 Agent。

**2. 连续执行、减少人工卡点**
明确"不要在任务间暂停问人类"——除非 BLOCKED/真正歧义/全完成。"Should I continue?" 类提示与进度摘要浪费人类时间。这是它与 agent-skills"每相位人工卡点"最根本的分歧：Superpowers 刻意最小化运行中检查。近期方向是合并为单一 task reviewer（约 2x 速度、½ token），在为"重流程"付代价。

**3. writing-skills 把 TDD 应用到文档**
`skills/writing-skills/SKILL.md` 要求新/改技能先写失败测试再 ship——技能本身的"生产质量"由方法论自身保证。eval 套件现独立在 `prime-radiant-inc/superpowers-evals`（drill harness），plugin 基础设施测试在 `tests/`。

**4. 多 harness 通过目录分身**
`.claude-plugin/` `.codex-plugin/` `.cursor-plugin/` `.kimi-plugin/` `.opencode/` `.pi/` `.gemini/` 各放对应插件清单/安装指令，`Pi` 包还注入 session-start 与 compaction 后的 `using-superpowers` 引导。设计上"每个 harness 单独安装"，保证跨工具一致行为。

## 社区口碑

- **正向**：放手长跑 + 强护栏（防 Agent 把过程合理化跳过）是真实优势；251k stars 体量与极广 harness 覆盖说明采用度高；`writing-skills` 的"技能也 TDD"被视为方法论自洽的典范。
- **时机**：2026-07-10 当日 Trending +1,096，稳居前三。
- **社区呼声（来自官方 comparison 自评）**：最被要求却尚未内置的是"多 Agent 团队执行"；覆盖偏窄（内循环构建方法论，非安全→上线全周期）；单 pipeline 对小改动偏重。
- **治理**：largely solo-authored，大量未合并社区 PR 积压——贡献门槛高（更新须跨所有支持 Agent 工作）。

## 竞品对比（详见 addyosmani/agent-skills 的 docs/comparison.md 三方表）

- **vs agent-skills**：Superpowers 重自主/前置推理、长模糊任务放手长跑；agent-skills 重全周期广度+每相位卡点+eval。
- **vs Pocock**：Superpowers 是重方法论；Pocock 是轻量锋利日常循环。
- **真实实验（Om Mishra）**：同模型同仓库，Superpowers 投入更多前瞻架构推理，作者仍偏好它做"演进生产系统/无既定模式的探索工作"；agent-skills 更快进代码、验证更宽。
- **共识**：跨会话持久记忆三方都未解决；不要两个框架同时当 active router。

## 核心研判

**优势**
- "派发 fresh subagent + 两阶段审查 + worktree 隔离"是长任务自主执行最成熟的模式之一，护栏强、偏离低。
- 方法论自洽（连技能都 TDD），理念一致性高，适合"交一大块、早上看审查结果"的工作方式。
- harness 覆盖最广、最活跃 churn，跨工具一致体验好。

**局限 / 风险**
- 覆盖窄（内循环构建，无安全/性能/上线技能）；小改动上单 pipeline 偏重。
- 单人维护 + 社区 PR 积压，团队想改技能/贡献摩擦大。
- 多 Agent 团队执行尚未内置——社区最大呼声未满足。

**定位**：大块、模糊、可放手长跑的探索性/演进性工作的首选方法；小改动或团队统一标准则 agent-skills 更合适。

## 关键文件速查

| 路径 | 功能 |
|------|------|
| `skills/subagent-driven-development/SKILL.md` | 旗舰：fresh subagent/任务 + 两阶段审查 + 整支审查 |
| `skills/brainstorming/SKILL.md` | Socratic 设计细化, 写 dated spec |
| `skills/writing-plans/SKILL.md` | 2-5 分钟/任务的细计划 (路径+代码+验证) |
| `skills/using-git-worktrees/SKILL.md` | 并行开发分支隔离 |
| `skills/test-driven-development/SKILL.md` | RED-GREEN-REFACTOR (含测试反模式) |
| `skills/writing-skills/SKILL.md` | 元: 用 TDD 写技能本身 |
| `skills/using-superpowers/SKILL.md` | 技能系统导论 (session-start 注入) |
| `.claude-plugin/` `.codex-plugin/` `.cursor-plugin/` 等 | 多 harness 插件清单 |
| `docs/porting-to-a-new-harness.md` | 移植到新 harness 指南 |
| `tests/` `evals/`(外部 superpowers-evals) | 插件基础设施测试 / 技能行为 eval |
