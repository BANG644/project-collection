# mattpocock/skills — 一位顶级工程师的"真实工程"技能工具箱

> **调研日期**: 2026-07-11 | **Stars**: 164,409⭐ (当日 +1,728) | **Forks**: 14,146
> **语言**: Shell | **许可**: MIT | **创建**: 2026-02-03 | **最近推送**: 2026-07-10
> **作者**: Matt Pocock (TypeScript 教育家, Total TypeScript) | **仓库**: https://github.com/mattpocock/skills

---

## 项目亮点（差异化）

- **Grilling 质询原语**：签名能力是"一次问一个问题、走完决策树每个分支"的质询循环（`/grill-me` `/grill-with-docs`），先把人和 Agent 对齐再动手——三个框架里需求澄清最强。
- **user-invoked vs model-invoked 显式拆分**：把 Agent 上下文当稀缺预算，用户唤起的技能负责编排，模型可自唤的技能持有可复用纪律，且前者绝不调用另一个前者。
- **共享语言 / CONTEXT.md + ADR**：`grill-with-docs` 边质询边构建项目领域模型，沉淀到 `CONTEXT.md` 与架构决策记录，跨会话降 token、提可导航性。
- **小、可改、可组合**：作者明言反对 GSD/BMAD/Spec-Kit 这类"接管流程"的框架，技能小而适配、跨模型通用、基于数十年工程经验。
- **公开演进纪律**：仓库带可见的 `in-progress/` 与 `deprecated/` 目录，把"技能自身的生命周期"也建模出来。

## 项目全景

Matt Pocock 把自己每天在 Claude Code 里真正用的技能开源，发展成一套 broad、观点鲜明、公开演进的工具箱（"Skills for Real Engineers, not vibe coding"）。它要修的四类失败模式：Agent 没做你想要的事（对齐缺口）、太啰嗦（缺共享语言）、代码不工作（反馈环缺失）、建成一坨泥球（不关心设计）。

与另外两者不同，它不是"方法论"也不是"全周期框架"，而是一位极好工程师的日常工具箱。分发走 `npx skills add mattpocock/skills`（vercel-labs/skills CLI），再跑 `/setup-matt-pocock-skills` 配置 issue tracker / triage labels / 文档落点。

## 核心架构

```
skills/
├── engineering/                   # 日常代码工作
│   ├── user-invoked: ask-matt, grill-with-docs, triage, improve-codebase-architecture,
│   │                 setup-matt-pocock-skills, to-spec, to-tickets, implement, wayfinder
│   └── model-invoked: prototype, diagnosing-bugs, research, tdd, domain-modeling,
│                     codebase-design, code-review
├── productivity/                  # 通用工作流
│   ├── user-invoked: grill-me, handoff, teach, writing-great-skills
│   └── model-invoked: grilling
├── personal/  misc/  in-progress/  deprecated/   # 其他 / 演进中 / 废弃
├── .claude-plugin/plugin.json     # 暴露 ~21 个技能给 Claude Code
├── CL AUDE.md  CONTEXT.md  CHANGELOG.md
└── docs/  scripts/  package.json   # 文档 + 发布脚本 (changeset)
```

**技能调用二分法**：User-invoked（你打字才触达，负责编排）vs Model-invoked（你或 Agent 按任务自动触达，持有可复用纪律）。一个 user-invoked 技能可调用 model-invoked 技能，但绝不调用另一个 user-invoked——保持编排层级干净。

## 源码深度解读

**1. grilling 是灵魂循环**
`skills/productivity/grilling/SKILL.md` 是可复用质询循环：`grill-me`（非代码）与 `grill-with-docs`（同上加共享语言/ADR）都是它的薄包装。它一次问一个问题、按依赖顺序走完设计树每个分支、每问给推荐答案、优先读代码而非追问、未确认共享理解前拒绝推进。`grill-with-docs` 顺带把术语沉淀进 `CONTEXT.md`——README 称这"可能是本仓库最酷的单一技术"：BEFORE 用 20 个词描述、AFTER 用"materialization cascade"一个词，会话间持续省 token。

**2. 深度模块设计纪律**
`codebase-design` 与 `improve-codebase-architecture` 把 Ousterhout《A Philosophy of Software Design》"深模块"思想操作化：大量行为藏在简单接口后、放在干净接缝、通过该接口可测。`improve-codebase-architecture` 扫描代码库找"加深"机会，呈现为可视化 HTML 报告，再就你选的那一个做 grilling——推荐每隔几天对代码库跑一次，对抗 Agent 加速的软件熵增。

**3. TDD 的"异端"取舍**
`skills/engineering/tdd/SKILL.md` 明确"重构不属于循环，它属于 code-review"——与 Addy 的 RED-GREEN-REFACTOR 同框但口径不同。这正体现 Pocock 工具的"一个真实工程师怎么 ship"而非委员会框架，也解释了为什么它 lifecycle 覆盖在 Build 之后偏薄（无安全/性能/上线技能）。

**4. 多会话编排在演进中**
`in-progress/wayfinder` 把大块超过单会话容量的工作规划成 issue tracker 上的"调查工单共享地图"，逐个解析直到目的地清晰——这是它在"跨会话记忆"共同前沿上的探索方向。

## 社区口碑

- **正向**：authenticity + sharpness 是最大卖点——这是"一个很厉害的工程师怎么 ship"，不是框架的设想；grilling 循环被社区公认为三方里需求质询的参考实现；newsletter 6 万+ 订阅者，生态号召力强。
- **时机**：2026-07-10 当日 Trending +1,728（全榜第一），164k stars 体量巨大。
- **吐槽点（来自官方 comparison 自评）**：Claude Code first（其他 Agent 可靠性有毛刺）；无 repo 内置 eval 抓回归；Build 之后生命周期覆盖薄；部分技能耦合个人 setup 向导与 tracker 约定。

## 竞品对比（详见 addyosmani/agent-skills 的 docs/comparison.md 三方表）

- **vs agent-skills**：Pocock 轻量、需求质询最强、Claude Code 最顺；agent-skills 覆盖全周期、带 eval、团队统一标准更强。
- **vs Superpowers**：Pocock 是小而锋利的日常循环；Superpowers 是重前瞻推理、可放手长跑的方法论。
- **三方共识**：不要同时把两个框架当 active router（抢 `/tdd` 命令名、路由冲突）；可 a la carte 摘单个技能（如摘 Pocock 的 `grill-me` + Superpowers 的隔离模式）。

## 核心研判

**优势**
- grilling 质询是"需求对齐"这一最常被忽略环节的标杆实现，单这一条就值得装。
- 技能小、可改、可组合、跨模型——不会被框架"接管流程"反噬，契合"agent 应保留控制权"的立场。
- 公开 `in-progress/deprecated`，把技能自身的演进纪律也示范出来，学习价值高。

**局限 / 风险**
- 单人 solo 维护、self-merge，规模化团队治理弱于 agent-skills。
- 无内置 eval，技能描述/行为回归只能靠人工发现。
- lifecycle 覆盖偏 Define/Build，缺 Security/Perf/Ship 类技能。

**定位**：个人/小队追求"轻量、锋利、Claude Code 优先"日常循环的首选；需求澄清环节几乎是必装。团队级统一标准则补 agent-skills。

## 关键文件速查

| 路径 | 功能 |
|------|------|
| `skills/productivity/grilling/SKILL.md` | 质询循环核心（grill-me/grill-with-docs 的底座） |
| `skills/productivity/grill-me/SKILL.md` | 非代码场景的对齐质询 |
| `skills/engineering/grill-with-docs/SKILL.md` | 质询 + 构建 CONTEXT.md/ADR 共享语言 |
| `skills/engineering/tdd/SKILL.md` | 红绿循环（重构归 code-review） |
| `skills/engineering/improve-codebase-architecture/SKILL.md` | 扫描并可视化"加深模块"机会 |
| `skills/engineering/code-review/SKILL.md` | 双轴审查（Standards + Spec，并行子 Agent） |
| `skills/engineering/wayfinder/SKILL.md` | in-progress：多会话调查地图编排 |
| `.claude-plugin/plugin.json` | 暴露 ~21 个技能给 Claude Code |
| `CLAUDE.md` `CONTEXT.md` | Agent 入口指令 + 共享语言示例 |
