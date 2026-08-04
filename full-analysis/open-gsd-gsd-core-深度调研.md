# 🚢 open-gsd/gsd-core — 深度调研报告

> **仓库**: [open-gsd/gsd-core](https://github.com/open-gsd/gsd-core)
> **调研日期**: 2026-08-05 | **数据来源**: GitHub API + 完整文件树（3,136 项）+ 官方设计文档 + issue 列表
> **数据**: ⭐ 7,702 | 🍴 535 | **语言**: JavaScript（CommonJS `.cts`）| **许可**: MIT | **最后推送**: 2026-08-04
> **npm**: `@opengsd/gsd-core` | **当前版本**: 1.7.0 | **社区**: Discord
> **关系**: 本仓库是已归档的 [`gsd-build/get-shit-done`](gsd-build-get-shit-done-深度调研.md)（64,778⭐）的**官方继承者**

---

## 一、项目定位

**GSD Core 是一套「上下文工程 + 规格驱动开发」框架，用来驱动 AI 编码 Agent 按纪律化的阶段循环干活。**

它要解决的问题被官方文档明确命名为 **context rot（上下文腐坏）**——不是模型不行，而是随着会话变长，早期约定的约束、架构、边界条件被淹没在后续 token 里，模型开始"不报错地变笨"。

解法一句话：**主会话只当瘦编排器，所有重活派给全新上下文的子 Agent，用磁盘上的结构化产物（STATE.md / CONTEXT.md / PLAN.md）跨会话续命。**

支持运行时覆盖 Claude Code、OpenCode、Antigravity CLI、Kimi CLI、Kilo、Codex、Copilot、Cursor、Windsurf 等。

---

## 二、项目亮点（差异化）

1. **把 context rot 讲透了，而不是当口号**。`docs/explanation/context-engineering.md` 用四条可观测症状定义它（模型开始自相矛盾 / 代码风格漂移 / 计划忽略早期需求 / 幻觉出二十条消息前还记得的函数签名），并明确指出这**不是 bug 而是 transformer 注意力在长序列上的固有性质**——所以不能靠"提醒模型"修，只能靠结构。
2. **编排器永不碰源文件**。这是最硬的架构约束："The orchestrator — your main session — never touches source files."。它只做四件事：spawn agent、收结果、更新共享状态、路由下一步。因此主会话上下文增长**缓慢且可预测**。
3. **34 个专职 Agent + 72 个斜杠命令**的完整名册，不是"三个角色演戏"的玩具多 Agent。
4. **`.out-of-scope/` 目录**：显式记录"我们决定不做什么"（8 项，如 `omp-runtime-in-core.md`、`temporal-context.md`、`plan-md-human-rendering.md`）。这是极少见的**负向决策留档**实践。
5. **安装器强制、禁止手抄文件**。README 原文："The installer is required for cross-runtime compatibility — do not copy files from `agents/` or `commands/` directly." 因为同一套 Agent 定义要渲染成九种运行时各自的格式。
6. **五语 README**（英 / 葡 / 简中 / 日 / 韩），国际化程度罕见。

---

## 三、核心架构

### 3.1 五步阶段循环（每个 milestone 重复，一次一个 phase）

```
1. Discuss  — 在任何规划之前先固化实现决策 → CONTEXT.md
2. Plan     — 研究、分解、并验证计划能塞进一个全新上下文窗口 → RESEARCH.md / PLAN.md
3. Execute  — 并行波次执行；每个 executor 从干净的 200k token 上下文起步
4. Verify   — 走查已构建的东西；先诊断修复，再宣布完成
5. Ship     — 建 PR、归档 phase、进入下一个
```

关键在第 2 步的"**验证计划能塞进一个全新上下文窗口**"——这是把上下文预算当成一等约束，计划本身要通过 `gsd-plan-checker` 的容量审查才能进执行。

### 3.2 `/gsd-plan-phase` 的实际编排（官方文档原文拆解）

```
编排器（主会话）:
  1. 加载紧凑 JSON 上下文载荷（项目摘要 + phase 目标 + 相关配置）
  2. spawn researcher agent  ← 200k token 干净窗口
  3. spawn planner agent     ← 输入 = 研究输出 + phase 需求
  4. spawn plan-checker agent ← 执行前验证计划
  → planner 把 PLAN.md 写到 .planning/phases/，成为持久产物而非共享窗口里的脆弱记忆
```

**"durable artefact, not a fragile memory in a shared context window"** —— 这句话是整个框架的设计哲学浓缩。

### 3.3 三重纪律的组合逻辑

官方文档明确这三者是**故意的组合**，缺一不可：

| 纪律 | 解决什么 | 载体 |
|------|---------|------|
| **Fresh-context subagents** | 保证每个 Agent 推理**清晰** | 每次 spawn 全新 200k 窗口 |
| **Spec-driven development** | 保证每个 Agent 推理**正确的东西** | `CONTEXT.md` / `RESEARCH.md` / `PLAN.md`（含依赖序 + 显式验收标准） |
| **Meta-prompting** | 保证每个 Agent **知道怎么推理得好** | `gsd-core/workflows/` 与 `agents/` 里工程化过的 prompt |

原文："Fresh context ensures each agent reasons clearly. Spec-driven artefacts ensure each agent reasons about the *right* thing. Meta-prompting ensures each agent knows *how* to reason about it well."

### 3.4 仓库结构

```
agents/          34 个 Agent 定义（.md，meta-prompt）
commands/gsd/    72 个斜杠命令
gsd-core/        核心 workflows
capabilities/    能力包（有完整生命周期：loader/lock/trust/consent/ledger/state/writer）
skills/          技能
hooks/           运行时钩子
src/             ~400 个 .cts 模块（CommonJS TypeScript）
pi/              提示注入相关
eslint-rules/    自定义 lint 规则
.claude-plugin/  marketplace.json + plugin.json
.opencode/plugins/ .kilo/plugins/   ← 各运行时适配层
.out-of-scope/   8 份"明确不做"的决策记录
.changeset/      变更集（含 archived/，数百条，每条对应一个编号 issue）
```

### 3.5 34 个 Agent 名册（全量）

**研究类（7）**：`advisor-researcher` `ai-researcher` `domain-researcher` `phase-researcher` `project-researcher` `ui-researcher` `research-synthesizer`

**规划类（5）**：`planner` `plan-checker` `roadmapper` `assumptions-analyzer` `framework-selector`

**执行类（3）**：`executor` `code-fixer` `integration-checker`

**审查/审计类（8）**：`code-reviewer` `security-auditor` `ui-auditor` `ui-checker` `eval-auditor` `eval-planner` `nyquist-auditor` `verifier`

**文档类（4）**：`doc-classifier` `doc-synthesizer` `doc-verifier` `doc-writer`

**调试类（2）**：`debugger` `debug-session-manager`

**知识/记忆类（5）**：`codebase-mapper` `pattern-mapper` `mempalace-curator` `intel-updater` `user-profiler`

注意 `gsd-nyquist-auditor` 这个命名——奈奎斯特采样定理的隐喻，大概率是检查"验证采样密度是否足够覆盖变更面"，是本项目里最有想象力的一个 Agent 名。

### 3.6 命令体系（72 条，按语义分组）

| 组 | 命令 |
|----|------|
| 生命周期 | `new-project` `onboard` `new-milestone` `complete-milestone` `next` `phase` `ship` |
| 五步循环 | `discuss-phase` `plan-phase` `execute-phase` `verify-work` `pr-branch` |
| 专项 phase | `mvp-phase` `ui-phase` `spec-phase` `secure-phase` `validate-phase` `ai-integration-phase` `ultraplan-phase` |
| 审计 | `audit-fix` `audit-milestone` `audit-uat` `code-review` `eval-review` `ui-review` `review` `review-backlog` |
| 记忆宫殿 | `mempalace-capture` `mempalace-recall` `extract-learnings` `capture` `inbox` |
| 上下文/图谱 | `map-codebase` `graphify` `ingest-docs` `ns-context` `surface` `explore` |
| 快通道 | `fast` `quick` `sketch` `spike` `autonomous` |
| 运维 | `health` `stats` `progress` `config` `settings` `update` `cleanup` `undo` `pause-work` `resume-work` `forensics` |

`fast` / `quick` / `sketch` / `spike` 四个"快通道"命令的存在说明作者清楚：**完整五步循环对小改动是过度工程**，需要逃生舱。

---

## 四、应用场景与启发

### 4.1 直接可用的场景

| 场景 | 适配度 |
|------|-------|
| **中大型项目的长周期 AI 辅助开发** | ⭐⭐⭐⭐⭐ 正是设计目标，milestone/phase 结构天然对齐迭代节奏 |
| **接手遗留代码库** | ⭐⭐⭐⭐ `/gsd-onboard` + `gsd-codebase-mapper` 专为 brownfield 设计 |
| **多人协作 + AI 混合团队** | ⭐⭐⭐⭐ 磁盘产物（PLAN.md/STATE.md）天然可 code review、可进 git |
| **需要审计留痕的开发** | ⭐⭐⭐⭐ 每个 phase 有 CONTEXT/RESEARCH/PLAN/验证记录，链路完整 |
| **一次性脚本 / 小 bug fix** | ⭐⭐ 用 `/gsd-quick` `/gsd-fast`，否则五步循环太重 |

### 4.2 方法论启发（即使不用这个框架也值得抄的四条）

1. **"编排器永不碰源文件"是可以直接搬走的架构约束**。不管你用什么 Agent 框架，把主会话降级为纯路由器 + 让所有文件操作发生在一次性子 Agent 里，就能显著延缓上下文腐坏。这条不需要装 GSD 也能实践。
2. **产物落盘 > 上下文记忆**。凡是需要跨会话存活的信息，写成磁盘上的结构化 Markdown，而不是指望"模型还记得"。GSD 的 `STATE.md` / `CONTEXT.md` 是最小可行实现。
3. **计划必须通过"能否塞进一个干净窗口"的容量检查**。这是个很妙的验收标准——如果一个 phase 的计划本身就撑爆上下文，那它就该被拆分。这个规则可以直接写进任何团队的 AI 协作规范。
4. **`.out-of-scope/` 是被严重低估的实践**。显式记录"我们考虑过 X，决定不做，原因是 Y"，能防止半年后有人（或某个 Agent）重新提起同一个已否决方案。8 份文件覆盖了 agent 模板渲染、通用 Agent prompt skills、核心内嵌 OMP 运行时、时间上下文等——每一条都是有人认真提过的。

### 4.3 遇到什么问题该回来看这个仓库

- 「AI 写着写着就忘了我们一开始定的架构」→ 看 `docs/explanation/context-engineering.md`，这是目前对 context rot 讲得最系统的一篇
- 「想搭多 Agent 编码流水线，不知道该分几个角色」→ 直接抄 `agents/` 的 34 个角色划分，尤其是"研究/规划/执行/审查/文档/调试/记忆"这七大类的切分方式
- 「跨 Claude Code / Codex / Cursor 部署同一套工作流」→ 看安装器如何把同一份 Agent 定义渲染成九种运行时格式（`.claude-plugin/` `.opencode/plugins/` `.kilo/plugins/`）
- 「团队 AI 协作缺规范」→ 抄五步循环 + 产物清单

---

## 五、源码与工程实践深度解读

### 5.1 `src/` 里的能力（capability）生命周期系统

`src/` 下约 400 个 `.cts` 模块，其中 **capability-* 系列有 10 个文件**，构成一个完整的能力包生命周期：

```
capability-source.cts      ← 来源解析
capability-trust.cts       ← 信任评估
capability-consent.cts     ← 用户授权
capability-loader.cts      ← 加载
capability-lock.cts        ← 锁定版本
capability-activation.cts  ← 激活
capability-state.cts       ← 状态
capability-ledger.cts      ← 账本（审计留痕）
capability-writer.cts      ← 写入
capability-lifecycle.cts   ← 生命周期总控
```

**这个拆分密度说明作者把"第三方能力包"当成安全边界在处理**——trust → consent → lock → ledger 这条链路，本质是在做供应链治理。对比大多数 Agent 框架把插件加载写成一个 `loadPlugin()` 函数，这里的严谨度是数量级差异。

### 5.2 命令路由的多层适配

```
agent-command-router.cts
audit-command-router.cts
check-command-router.cts
claude-orchestration-command-router.cts
cjs-command-router-adapter.cts
command-routing-hub.cts
command-aliases.cts
command-arg-projection.cts
command-roster.cts
```

九个路由相关模块 + `adapter-declarative.cts` / `adapter-imperative.cts` 两种适配范式。这是"一套命令跑九种运行时"的成本——**跨运行时兼容不是免费的**，README 那句"不要手抄 agents/ 文件"背后就是这一堆。

### 5.3 `.changeset/` 的工程纪律

`.changeset/` 与 `.changeset/archived/` 下有数百条变更集，命名格式是 `<issue编号>-<简述>.md`：

```
2255-write-guard-catastrophic-shrink.md
2544-shared-hooks-package-json-clobber.md
2645-verification-deletion-ledger.md
2999-capability-eos-takeover-process.md
166-windows-claude-sh-hook-command.md
1452-long-workflows-should-checkpoint-before-context-exhaustion（对应 issue #1452）
```

从编号跨度（14 → 3409）可以读出：**这个项目的 issue 已经开到 3000+**，且每个修复都有对应 changeset。`write-guard-catastrophic-shrink`（写入守卫：灾难性缩水）这类命名，说明踩过"Agent 把文件写空了"的坑并做了防护。

### 5.4 从 issue 看真实痛点

| Issue | 信号 |
|-------|------|
| `#922` plan-phase aborts at planner spawn on a false-negative Agent-availability check | Agent 可用性探测误判导致流程中断——多运行时适配的典型脆弱点 |
| `#1817` gsd-tools state rebuild — STATE.md structural rebuilder / drift repair + ADR | **STATE.md 会漂移**，需要专门的重建器。产物落盘方案的固有代价 |
| `#1452` Long workflows should checkpoint before context exhaustion | 即便有全套上下文工程，长流程仍会撞上下文上限，需要检查点 |
| `#2773` spec-phase edge probe: shape cues are English-only — 非英文需求全落进 `unclassified` | ⚠️ **国际化陷阱**：README 有五种语言，但 spec-phase 的形状线索是硬编码英文的，中文需求会被判为未分类。五语 README 是门面，核心逻辑仍是英语中心 |
| `#277` bug(codex): global install does not materialize SDK payload for CJS bridge | 跨运行时安装的边界 bug |
| `#744` Add Kimi CLI runtime support | 运行时支持靠社区推动逐个加 |

---

## 六、社区口碑

- **⭐ 7,702 / 🍴 535**，相对前身 `gsd-build/get-shit-done` 的 64,778⭐ 差距悬殊——**继承者的星标只有前身的 12%**。这是典型的"归档重定向后星标不迁移"现象，新用户搜索 GSD 仍会先撞到已冻结的旧仓。
- **issue 编号已到 2773+，changeset 编号到 3409**，与 7.7k 星标对比，说明这是个**issue 密度极高的高强度迭代项目**，不是躺平仓。
- **高赞 issue 反应数普遍只有 1-2**，说明社区参与是**长尾式的高频小反馈**，而非集中式的大争议。健康但小众。
- **Discord 社区 + 五语 README + `gsd-opencode` 社区移植版**（rokicool），生态在往外扩。
- **CI 完备**：`.githooks/pre-commit` `.githooks/pre-push`、`.coderabbit.yaml`（AI code review）、自定义 `eslint-rules/`、`TESTING-STANDARDS.md`、`TEST-EXAMPLES.md`、`VERSIONING.md`、`SECURITY.md`。工程规范度远超同星级项目。

---

## 七、竞品对比

| 方案 | 定位 | 相对 GSD Core |
|------|------|--------------|
| **gsd-build/get-shit-done**（前身，64,778⭐，已归档） | 同源 | ⚠️ 已冻结。星标高但是化石，**新项目应直接用 gsd-core** |
| **BMAD-METHOD** | 敏捷 AI 开发方法论 | 角色扮演更重（PM/架构师/开发），GSD 更偏"上下文预算工程"；GSD 有跨九种运行时的安装器，BMAD 主要绑 IDE |
| **Anthropic Skills / Claude Plugins** | 官方能力包 | 粒度更细（单技能），GSD 是整套开发流程；GSD 的 capability 系统可视为在其上加了 trust/consent/ledger 治理层 |
| **spec-kit（GitHub）** | 规格驱动开发 | 更轻，聚焦 spec 生成；GSD 把 spec 嵌进完整五步循环并配 34 个 Agent |
| **OpenAI Codex / Claude Code 原生** | 单体 Agent | 无阶段纪律、无跨会话产物、无子 Agent 隔离——GSD 正是补这三块 |
| **Aider / Cline / Continue** | 编码助手 | 交互式单会话，遇长任务必然 context rot；GSD 是它们的上层编排 |

**GSD Core 的独特生态位**：它不与编码 Agent 竞争，而是**骑在它们之上做流程治理**。这也是它能同时支持九种运行时的原因。

---

## 八、核心研判

### ✅ 优势
1. **对 context rot 的问题定义和解法是目前最系统的**，`docs/explanation/context-engineering.md` 值得单独读一遍，即便不用这个框架。
2. **"编排器永不碰源文件"是可移植的硬架构约束**，含金量最高的一条。
3. **capability 十模块生命周期**把第三方能力当供应链风险治理，安全意识超出同类。
4. **`.out-of-scope/` 负向决策留档**，防止重复讨论已否决方案。
5. **工程规范完备**：pre-commit/pre-push hooks、自定义 eslint 规则、CodeRabbit AI review、测试标准文档、版本策略文档。

### ⚠️ 风险与代价
1. **重**。34 Agent + 72 命令 + 五步循环，学习曲线陡。小项目、小改动用它是负收益（作者也知道，所以给了 `fast`/`quick`/`sketch`/`spike` 逃生舱）。
2. **STATE.md 会漂移**（issue #1817 专门做重建器）。产物落盘方案不是银弹——磁盘状态与实际代码状态需要额外的同步机制维护。
3. **仍会撞上下文上限**（issue #1452）。上下文工程延缓而非消除问题。
4. **⚠️ 非英语需求可能被静默降级**（issue #2773 仍 open）。spec-phase 的形状识别线索硬编码英文，中文/日文需求会全部落进 `unclassified`。**中文用户使用前必须知道这一点**——五语 README 不代表核心逻辑支持多语。
5. **跨运行时适配是脆弱点**。issue #922（Agent 可用性误判）、#277（Codex 全局安装 SDK 载荷缺失）都是这类。九种运行时意味着九倍的边界情况。
6. **星标继承断层**。7.7k vs 前身 64.8k，新用户容易被旧仓误导。

### 🎯 一句话研判
**GSD Core 是把"AI 编码会随会话变笨"这件事当成架构问题而非提示词问题来解决的少数派**——它的价值不在 34 个 Agent 有多全，而在于"编排器永不碰源文件 + 产物落盘 + 计划需通过上下文容量审查"这三条可独立移植的原则。适合中大型长周期项目；小项目请用 `/gsd-quick` 或干脆别用。**中文用户上手前先确认 issue #2773 的 i18n 问题是否已修**。

---

## 九、关键文件路径速查

| 路径 | 说明 |
|------|------|
| `docs/explanation/context-engineering.md` | ⭐⭐ 全库最值得读的一篇：context rot 定义 + fresh-context subagents 解法 + 三重纪律组合逻辑 |
| `docs/explanation/the-phase-loop.md` | 五步循环设计说明 |
| `docs/ARCHITECTURE.md` | 架构总览 |
| `agents/` | ⭐ 34 个 Agent 定义（meta-prompt 本体），角色划分可直接借鉴 |
| `commands/gsd/` | 72 个斜杠命令 |
| `gsd-core/workflows/` | 核心工作流 meta-prompt |
| `src/capability-*.cts` | ⭐ 10 个模块的能力包生命周期（source→trust→consent→lock→ledger） |
| `src/*command-router*.cts` | 9 个命令路由模块，跨运行时适配的成本所在 |
| `.out-of-scope/` | ⭐ 8 份"明确不做"的负向决策记录 |
| `.changeset/` + `.changeset/archived/` | 数百条变更集，`<issue编号>-<简述>.md` 格式，项目演进史 |
| `.claude-plugin/marketplace.json` | Claude Code 插件市场清单 |
| `.opencode/plugins/` `.kilo/plugins/` | 其他运行时适配层 |
| `CONTEXT.md` | 项目自身的上下文文件（吃自己的狗粮） |
| `TESTING-STANDARDS.md` / `TEST-EXAMPLES.md` | 测试规范 |
| `docs/whats-new-1.7.0.md` | 当前版本变更说明 |
| `README.zh-CN.md` | 简体中文 README（注意：核心 spec 逻辑仍是英语中心，见 issue #2773） |

---

> **调研方法**：GitHub API 拉取仓库元数据 / 完整文件树（3,136 项）/ README / `docs/explanation/context-engineering.md` 全文 / agents 与 commands 目录清单 / 按 reactions 排序的 issue 列表。所有结论均基于仓库内实际文件，`.out-of-scope/`、capability 模块群、changeset 编号跨度等发现均为文件树实证。
