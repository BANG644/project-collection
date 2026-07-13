# 🔍 github/spec-kit — 全方位深度调研

> **调研日期**: 2026-07-14 | **Stars**: 120,478 ⭐ | **Forks**: 10,681 | **Open Issues**: 363 | **License**: MIT
> **语言**: Python（CLI 用 `uv` 安装）| **官方**: GitHub 官方仓库（github org）
> **最新发布**: v0.12.13（2026-07-13，当日仍在发布，极高活跃度）

---

## 一、项目定位（一句话）

GitHub 官方出品的 **Spec-Driven Development（规范驱动开发）工具包**——用一套可执行的规范（constitution → spec → plan → tasks → implement）把"先写规范、再写代码"变成 AI 编码 Agent 的结构化工作流，让 Agent 聚焦于"产品场景与可预期结果"，而不是每次从零 vibe coding。

## 二、项目亮点（差异化）

1. **官方背书 + 30+ Agent 适配**：GitHub 官方仓库，原生支持 Claude Code / Copilot / Codex / Cursor / Gemini CLI 等 30+ 编码 Agent，既生成 slash command（`/speckit.*`），也支持 skills 模式（`$speckit-*`）。
2. **规范即可执行产物**：区别于传统"写完就丢"的 PRD，spec-kit 把规范沉淀为 `specs/` 下的 `spec.md / plan.md / tasks.md / research.md / data-model.md / contracts/`，且 `tasks.md` 带依赖顺序、`[P]` 并行标记、文件路径、TDD 结构、checkpoint——是直接喂给 `/speckit.implement` 的执行清单。
3. **运行时模板解析 + 三层可定制**：核心命令/模板在最底层，上面叠 Presets（改格式/术语/合规）、Extensions（加新命令/阶段）、Project-Local Overrides（一次性微调），按优先级栈自上而下解析，第一个匹配生效。
4. **Bundle 角色化打包**：用 `bundle.yml` 把一组 extensions+presets+steps 钉版本，一条命令给"产品经理/安全研究员/开发者"等完整角色配置，且 install 幂等、可离线、移除不破坏他人组件。
5. **基于真实研究**：README 明确标注深受 John Lam（@jflam）的工作影响，是把"规范驱动开发"从论文/方法论落成开源工具链的早期实践。

## 三、核心架构

整体是 **`specify` CLI（Python，经 `uv tool install specify-cli` 安装）+ Agent 侧 slash command/skill 文件** 的组合。CLI 只负责 bootstrap 与生命周期管理（`init` / `self upgrade` / `extension add` / `preset add` / `bundle install`），真正的"思考"发生在 Agent 里——命令文件通过模板引导 Agent 产出结构化 artifact。

模板解析优先级栈（运行时自上而下，第一个匹配生效）：

```
1. Project-Local Overrides   .specify/templates/overrides/   # 一次性微调，最高优先
2. Presets                   .specify/presets/templates/      # 改核心/扩展的格式
3. Extensions                .specify/extensions/templates/   # 加新能力
4. Spec Kit Core             .specify/templates/              # 内置 SDD 命令与模板
```

`specify init` 后项目里的典型结构（来自 README 的详细流程）：

```
.
├── .specify
│   ├── memory/constitution.md      # /speckit.constitution 产出：项目治理原则
│   ├── scripts/bash/               # check-prerequisites / setup-plan / setup-tasks ...
│   └── templates/                  # plan-template / spec-template / tasks-template
├── specs/001-create-taskify/
│   ├── spec.md                     # 需求 + 用户故事（what & why）
│   ├── plan.md                     # 技术栈 + 架构（how）
│   ├── tasks.md                    # 可执行任务清单
│   ├── research.md                 # 技术调研
│   ├── data-model.md
│   └── contracts/                  # api-spec.json / signalr-spec.md
└── CLAUDE.md                       # plan 阶段生成的项目入口
```

**核心开发阶段**：0-to-1 Greenfield（从零生成）、Creative Exploration（并行多实现探索）、Iterative Enhancement（Brownfield 现代化）。核心哲学是 intent-driven（先定义 what 再定义 how）、rich specification（用护栏+组织原则）、multi-step refinement（多步精炼而非一次生成）。

## 四、应用场景与启发

- **给"AI 编码 Agent 工作流"的借鉴**：spec-kit 证明了"约束 Agent 先写规范、再写代码"能显著降低返工。同类需求（你自己的 Agent harness）可直接复用其"constitution → specify → plan → tasks → implement → converge"的七段式骨架，尤其是 `converge`（对照 spec/plan/tasks 审计代码库、把剩余工作追加为新 task）这个收口命令——多数自建 harness 都缺"实现后回灌校验"这一步。
- **模板优先级栈是通用模式**：当你的工具需要"内置默认 + 用户可覆盖"时，spec-kit 的 overrides > presets > extensions > core 解析顺序是现成的设计范式，比硬编码开关清晰得多。
- **Bundle 解决"团队角色一键配置"**：如果你想给团队不同角色分发不同的 Agent 配置（而非每人手搓），`bundle.yml` + 目录优先栈（project > user > built-in）+ 幂等 install 是可直接搬用的实现。
- **与同类（如 obra/superpowers、addyosmani/agent-skills）的关系**：spec-kit 是"官方 + 重工具链（CLI + 模板系统 + bundle）"路线；superpowers 偏"子 Agent 心智方法论"；agent-skills 偏"把软件生命周期编码成技能"。选型时：要工程化、要管多 Agent、要合规门禁 → spec-kit；要轻量方法论注入 → 后两者。

## 五、源码解读（关键模块）

spec-kit 的代码主体是 Python CLI + 大量 Markdown 模板。CLI 负责解析参数、拉取/解析模板、写 Agent 命令文件。两个最值得看的入口：

**1. `specify init` 的集成探测（伪代码骨架）**
```python
# init 时按 --integration 选择目标 Agent，并探测其 CLI 是否安装
if integration.requires_cli and not shutil.which(integration.cli_bin):
    warn(f"{integration.cli_bin} 未安装，用 --ignore-agent-tools 跳过检测")
# 把核心模板 + 已安装的 extension/preset 命令文件写入 Agent 目录
# 如 .claude/commands/、.codex/skills/、AGENTS.md 等
write_commands(specify_templates, target_dir=integration.command_dir)
```
关键点：`requires_cli` 元信息 + 非交互默认 Copilot，是它"跨 30+ Agent 还能正确落位"的原因。

**2. 模板运行时解析**
命令文件本身不内嵌逻辑，而是引用 `.specify/templates/` 下的 Markdown 模板；运行时按优先级栈取第一个匹配。这意味用户改 `.specify/templates/overrides/` 就能在不 fork 仓库的前提下改掉所有命令行为——这是它"可定制但不分裂"的设计支点。

## 六、全网口碑

- **社区信号**：GitHub 官方仓库，120K⭐ / 10.7K forks / 363 open issues，发布极频繁（v0.12.13 当日发布），Discord/社区 extensions+presets+bundles 生态已成形，文档站（github.github.io/spec-kit）含完整 CLI reference 与社区贡献目录。
- **评价倾向**（综合 README 与生态）：正面集中在"终于有官方把 SDD 落成工具""跨 Agent 通用""模板可覆盖"；争议点主要是 SDD 对简单需求偏重（但提供了 `clarify` 可跳过 spike）、以及对 Agent 过度热情（over-eager）需要 constitution 约束——README 自己也坦诚写了"Agent 可能加你没要求的东西，要它解释理由"。
- **数据不可用**：具体 HN/Reddit 单帖评分、Twitter 讨论量未做抓取，以上基于仓库元数据 + README 自述推断。

## 七、竞品对比 + 核心研判

| 维度 | spec-kit（GitHub） | obra/superpowers | addyosmani/agent-skills | LangChain/手写 PRD |
|------|-------------------|------------------|------------------------|-------------------|
| 出身 | 官方、工程化 | 社区方法论 | 社区方法论 | — |
| 核心形态 | CLI + 模板系统 + Bundle | 子 Agent 心智 + git-worktree | 技能集合 + eval 框架 | 文档 |
| 跨 Agent | 30+ 原生 | 需适配 | 需适配 | 无 |
| 合规/门禁 | Preset 强制 + Bundle 钉版本 | 弱 | 三层 eval | 无 |
| 学习曲线 | 中（概念多） | 低 | 低 | — |

**核心研判**：
- **优势**：官方背书 + 频繁迭代 + 跨 Agent 通用 + 模板可覆盖，是企业/团队落地"规范驱动 AI 开发"目前最完整的开源选项；Bundle 的"角色化一键配置 + 幂等 + 离线"对团队协作尤其有价值。
- **风险**：SDD 流程对 trivial 任务有 overhead；强依赖 Agent 遵循模板（Agent 跑偏仍需人工 constitution 约束）；生态虽起量但 Extension/Preset 质量参差，README 明确提示"社区贡献自行 review 源码"。
- **趋势判断**：规范驱动开发是 2026 年 AI 编码的主流范式之一，GitHub 亲自下场意味着它会成为事实标准参照物。对想自建 Agent harness 的团队，spec-kit 的"七段式 + 模板优先级栈 + Bundle"值得直接借鉴，而非从零造轮子。

## 八、关键文件路径速查

- `spec-driven.md` — Spec-Driven Development 完整方法论（7 阶段详解）
- `spec-driven.md` 顶部 Table of Contents 列出的 `docs/install/`、`docs/upgrade.md` — 安装/升级指南
- `examples/bundles/` — 4 个角色化 bundle 清单（PM / 业务分析师 / 安全研究员 / 开发者）
- `extensions/EXTENSION-PUBLISHING-GUIDE.md`、`presets/PUBLISHING.md` — 扩展/预设发布指南
- `.specify/templates/`（运行时生成于项目内）— plan-template / spec-template / tasks-template 实际落位处
- 文档站：`https://github.github.io/spec-kit/`（reference / community / integrations 全量）
