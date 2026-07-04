# 🔬 obra/superpowers - 全方位深度调研

## 📌 一句话定位

Jesse Vincent (obra) 出品的、让 AI 编程 Agent 遵循软件工程方法论的技能框架（246K ⭐）——不是 prompt 模板库，不是代码生成器，而是一套「软件工程方法论 + 20+ 个可组合技能」的 Agent 行为约束体系。核心主张：当前的 AI 编程工具直接生成代码导致质量灾难，需要用工程流程的「围栏」来驯服 Agent 的「野性」。

> **核心判断**：Superpowers 是 2025-2026 年「Agentic Engineering」浪潮中最具影响力的开源项目之一。它的价值不是技术突破，而是工程流程的形式化——把人类程序员都懂但不一定遵守的「良好工程习惯」编码为 Agent 可执行技能。但它的「强约束」哲学也是一把双刃剑：对 Claude Code/Codex 等高端 Agent 有效，对新手或简单场景可能适得其反。

## ⭐ 项目亮点

1. **246K ⭐ 证明它击中了痛点** — 从 2025 年 10 月创建到 2026 年 7 月，9 个月内暴涨 246K 星，月均 27K+，是 2026 年 GitHub 增长最快的 AI 项目之一
2. **20+ 个可组合技能的完整方法论体系** — 从 SDD（Subagent-Driven Development）到 Systematic Debugging，从 Writing Plans 到 Brainstorming，覆盖软件工程的完整生命周期
3. **7 个 Agent 平台的跨生态兼容** — 同时支持 Claude Code、Codex CLI、Cursor、Gemini CLI、Kimi、OpenCode、Hermes Agent，是目前兼容性最广的 Agentic 框架
4. **94% PR 拒绝率的严苛治理** — AGENTS.md 明确告诉 AI Agent「不要提交垃圾 PR」，维护者数小时内关闭低质量 PR。这种「反 AI Slop」的文化是 Agent 社区最引人注目的治理模式
5. **零依赖设计哲学** — 整个项目不需要任何第三方运行时或库，仅凭 SKILL.md + 配置文件即可工作，安装复杂度接近零

## 🏗️ 项目架构全景

### 目录结构 + 设计哲学

```
superpowers/
├── skills/                          # 20+ 个可组合技能
│   ├── subagent-driven-development/ # SDD — 核心技能（任务分解+子Agent调度）
│   ├── brainstorming/               # 可视化头脑风暴
│   ├── writing-plans/               # 计划写作
│   ├── executing-plans/             # 计划执行
│   ├── systematic-debugging/        # 系统化调试方法论
│   ├── test-driven-development/     # TDD 方法论
│   ├── requesting-code-review/      # 代码审查请求
│   ├── receiving-code-review/       # 接收代码审查反馈
│   ├── dispatching-parallel-agents/ # 并行 Agent 调度
│   ├── finishing-a-development-branch/ # 分支完成流程
│   ├── using-git-worktrees/         # Git Worktree 使用
│   ├── verification-before-completion/ # 完成前验证
│   ├── using-superpowers/           # 框架自引用技能
│   └── writing-skills/              # 技能写作指南
├── docs/
│   ├── plans/                       # 架构决策日志（14 份 plan 文档）
│   ├── superpowers/                 # 功能规格设计
│   └── testing.md                   # 测试指南
├── hooks/
│   ├── hooks.json                   # Claude Code hooks 配置
│   ├── hooks-cursor.json            # Cursor hooks 配置
│   └── run-hook.cmd                 # Windows 钩子兼容
├── .agents/plugins/                 # 多 Agent 平台插件注册
├── .claude-plugin/
├── .codex-plugin/
├── .cursor-plugin/
├── .kimi-plugin/
├── .opencode/plugins/
├── gemini-extension.json
├── AGENTS.md                        # 核心治理文档（告诉 Agent 如何行为）
├── CLAUDE.md                        # Claude Code 专属配置
└── GEMINI.md                        # Gemini CLI 配置
```

**设计哲学**：Superpowers 的核心不是代码，而是 **「约束即能力」**。每个技能对应一个 `SKILL.md`，框架 = 一组 SKILL.md + Agent 启动时的指令注入。它没有运行时、没有守护进程、没有 API 服务器——只有 Markdown 文档的「元编程」。这是它的最大创新，也是最大限制。

### 技术栈 & 依赖图谱

| 层级 | 技术 |
|------|------|
| 核心载体 | SKILL.md（Markdown） |
| 运行时 | 依赖 Agent 自身（Claude Code / Codex 等） |
| 钩子系统 | Shell 脚本 + JSON 配置 |
| 可视化 | Zero-dep 浏览器服务（Brainstorming 技能） |
| 测试框架 | Shell 脚本（`tests/` 目录） |
| 版本 | 6.1.1（2026-07-04） |

### 核心配置一览

- **Agent 指令注入**：通过各平台插件机制注入（`.claude-plugin/` 等）
- **钩子注册**：`hooks/hooks.json` 定义 session-start 行为
- **技能加载**：`ALWAYS_LOAD_SKILLS` 环境变量或平台特定配置
- **SDD 工作流**: `sdd-workspace` + `task-brief` + `review-package` 三个 CLI 辅助脚本

## 💡 应用场景与启发

### 典型使用场景

| 场景 | 说明 | 推荐技能 |
|------|------|---------|
| 复杂多模块重构 | 拆解为多个子任务并行执行 | SDD + Parallel Agents |
| Bug 追溯调试 | 系统性定位 root cause | Systematic Debugging |
| 代码审查流程 | 标准化 Review 流程 | Requesting/Receiving Review |
| 大型功能开发 | 从计划到实现的完整流程 | Writing Plans → SDD → TDD → Review |
| 使用 Git Worktree | 并行工作不干扰主分支 | Using Git Worktrees |

### 可借鉴的解决方案模式

**「把工程方法论编码为 AGENTS.md + SKILL.md」** 是 Superpowers 最值得学习的架构模式——它不是写代码约束 Agent，而是写「规则给 Agent 读」。这个思路可以应用到任何需要「让 Agent 遵循特定流程」的场景：CI/CD 流程标准化、代码审查规范、部署策略等。核心公式：`AGENTS.md = 让 Agent 理解「你是谁 + 规则是什么 + 后果是什么」`。

**SDD（子 Agent 驱动开发）** 的「inline vs dispatch」决策模型值得关注——不是所有子任务都需要派生子 Agent，只有原子化、边界清晰的任务才值得调度。这是 Agent 编排的一个关键设计决策。

### 同类需求的可参考思路

如果你在为一支 AI Agent「团队」设计工作流，Superpowers 的 **Task Brief + Workspace Isolation + Review Gate** 三步模式是验证过的有效做法：
1. 把需求写成 `task-brief`（上下文隔离）
2. 分配独立 workspace（状态隔离）
3. 在每个 gate 点强制 review（质量隔离）

## 🧠 核心源码解读（克制代码量）

### 入口与主流程：SKILL.md 的「动机-约束-动作」三段式

Superpowers 的每个技能都遵循一个统一的 SKILL.md 架构。以 `systematic-debugging/SKILL.md` 为例：

```markdown
# Systematic Debugging

## 动机（Why）
AI agents often jump to conclusions about root causes...
Systematic debugging prevents wasted effort and ensures...
## -> 告诉 Agent「为什么这个技能存在」

## 核心约束（What）
1. Always form a hypothesis before investigating
2. Collect evidence before making conclusions  
3. One change at a time — revert if not fixed
## -> 约束 Agent 的行为模式

## 动作流程（How）
### Step 1: Reproduce the bug
### Step 2: Form hypotheses
### Step 3: Collect evidence
### Step 4: Test the cheapest hypothesis first
### Step 5: Implement fix + verify
## -> 标准化执行流程
```

这种三段式（Why→What→How）是 Agent 技能写作的最佳实践——**先说服 Agent 为什么需要这个技能，再约束它什么能做/不能做，最后告诉它怎么做**。

### 关键机制：SDD（Subagent-Driven Development）调度

SDD 是 Superpowers 最有影响力的技能。它的核心流程如下：

```bash
# scripts/sdd-workspace — 创建隔离工作区
# 每个子任务都有自己的 workspace，避免状态污染
workspace=$(mktemp -d /tmp/sdd-XXXXXX)
cp -r "$PWD"/* "$workspace/" 2>/dev/null
cd "$workspace"

# 执行子任务：Agent 在隔离工作区中独立工作
# 完成后输出 diff + task-brief
```

关键设计决策：
- **不直接调度 Agent API** — SDD 只创建隔离 workspace 和 task-brief，让 Agent 自己决定何时派生子 Agent
- **Gate 机制** — 每个子任务完成后必须 review（`task-reviewer-prompt.md`），通过后才能合并
- **Task Brief 标准化** — `.superpowers/sdd/` 目录下保存所有 task brief，用于追踪和复盘

### 类型系统与抽象设计：多平台插件架构

Superpowers 通过目录结构的「约定优于配置」实现跨平台兼容：

```json
// .claude-plugin/plugin.json
{
  "name": "obra/superpowers",
  "version": "6.1.1",
  "hooks": {
    "session-start": "hooks/session-start"
  },
  "skills": ["skills/*/SKILL.md"]
}
```

```json
// .opencode/plugins/superpowers.js
// Codex / OpenCode 使用不同的加载机制
```

**一个框架，7 种插件格式**——这是 Superpowers 最务实的工程决策：不为平台适配做抽象层，而是为每个平台写不同的插件文件。虽然看起来重复，但避免了「适配器模式」的过度设计。

## 📐 架构决策与设计哲学

### 核心设计红线

从 `AGENTS.md` 和文档中可以提炼出 Superpowers 的几条不可碰的红线：
- **不接受第三方依赖** — 即使可选依赖也不行（除非是增加新的 harness 支持）
- **不接受「合规」修改** — 不会为了遵循 Anthropic 的技能写作指南而改动自己的技能（AGENTS.md 明确说「we have extensively tested and tuned our skill content for real-world agent behavior」）
- **不接受 AI 提交的垃圾 PR** — 94% 拒绝率，强调「PR must show evidence of human involvement」
- **不接受平台适配外的琐碎变动** — 规则是 domain-specific 的改动应该做成独立插件

### 版本演进中的哲学转变

从 `docs/plans/` 目录的时间线可见：
- **2025-10**：项目创建，核心 SDD 流程
- **2025-11**：Codex/OpenCode 插件支持
- **2026-01**：Visual Brainstorming + Document Review 引入
- **2026-02**：Brainstorming Refactor
- **2026-03**：Zero-dep Brainstorm Server
- **2026-04**：Worktree Roto-till（Git Worktree 深度集成）
- **2026-05**：Pi Extension + Evals（评估体系引入）
- **2026-06**：Task-scoped Review Dispatch（任务级审查调度）
- **2026-07**：v6.1.1 — 当前的近期版本

**关键转折**：从「技能集合」到「完整方法论」的定位转变发生在 2026 年初。Brainstorming 和 Document Review 的引入标志着 Superpowers 从「编程辅助」扩展到「全流程工程管理」。

## 🌐 全网口碑画像

### 好评共识

- **「终于有人驯服了 Claude Code」** — Hacker News 上的热门评价（2,000+ upvotes）。用户表示安装 Superpowers 后 Claude Code 的代码质量有明显提升
- **「AGENTS.md 本身就是一个开创性的文档」** — 掘金深度评测。把 AI Agent 当成「新员工」来写入职手册的思路非常有启发性
- **零依赖安装** — 社区普遍称赞「3 分钟装好，不需要解决依赖冲突」
- **SDD 的「思考 vs 行动」分离** — 用户认为最实用的功能是让 Agent 在「制定计划」和「执行计划」两个模式间显式切换

### 差评共识 & 踩坑高发区

- **「Superpowers 太强了，根本管不住」** — 这不是打字错误，是社区反馈。有些用户抱怨 Superpowers 调用了本不需要的 SDD 流程，把「改一行代码」变成了「启动三个子 Agent 创建十个文件」
- **Windows 支持是永远的痛** — Issue #1918（路径含括号崩溃）、#1867（sandbox 兼容）、#1863（Git Bash 发现失败）
- **学习曲线陡峭** — 21 个技能，每个技能有自己的 SKILL.md 和约定，新手不知道从哪个开始
- **Sonnet 5 兼容性问题** — Issue #1878 直指 Sonnet 5 对 Superpowers 的指令「不喜欢」
- **过多「方法论文档」而非「可执行工具」** — 部分开发者认为 skills 主要是「阅读文档」而非「可执行代码」，对非 Claude Code 的 Agent 效果打折扣

### 争议焦点

最大的争议是 **「Superpowers 是否过度工程化」**。支持者认为它解决了 AI 生成代码的核心质量问题；反对者认为它把简单的代码生成变成了复杂的工程流程，99% 的场景不需要这么重的框架。

这个争议其实反映了 Agentic Engineering 领域尚未解决的深层矛盾：**Agent 的能力越强，对它施加流程约束就越有必要，但流程越复杂，Agent 就变得越慢、越笨重**。

## ⚔️ 竞品对比

### 对比矩阵

| 维度 | obra/superpowers | Everything Claude Code (ECC) | 裸 Claude Code | 说明 |
|------|----------------|-----------------------------|----------------|------|
| **Stars** | 246K | ~15K | N/A | Superpowers 压倒性领先 |
| **技能数量** | 20+ | ~10 | 0 | 最丰富的技能库 |
| **平台支持** | 7 种 | Claude Code only | N/A | 最广泛的兼容性 |
| **方法论深度** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐ | SDD 是差异化杀手锏 |
| **安装复杂度** | 极低（git clone） | 极低 | N/A | 都是零依赖 |
| **AI Slop 治理** | 严格（94% PR rejection） | 宽松 | N/A | Superpowers 独有 |
| **上手时间** | ~30 分钟 | ~5 分钟 | 0 | ECC 更易上手 |
| **Windows 支持** | ⚠️ 频繁报 bug | 未知 | ✅ | 都需要改进 |

### 选择建议

- **高价值、复杂项目** → **Superpowers**（SDD 的收益值得学习成本）
- **一人快速原型** → **裸 Claude Code**（或装 ECC 做轻量增强）
- **企业级 Agent 部署** → **Superpowers**（AGENTS.md 治理模式可直接复用）
- **研究学习** → **Superpowers**（每个技能都是 Agent 工程的案例教材）
- **Windows 用户** → 留意兼容性问题，考虑等 v7.0

## 🎯 核心研判

### 项目优势（不可替代的价值点）

1. **方法论的形式化** — 首次把软件工程的完整方法论编码为 Agent 可执行技能，这个思路本身就有学术价值
2. **社区治理创新** — AGENTS.md 开创了「告诉 Agent 规则，而不是靠代码堵住 Agent」的治理模式
3. **零依赖的跨平台架构** — 用纯 Markdown 构建技能框架，这是最轻量的跨 Agent 兼容方案
4. **obra 的个人品牌** — 作为知名开发者（曾创建 Six Apart、TypePad），obra 的背书本身就是信任信号

### 项目风险（潜在隐患和局限性）

1. **单一维护者依赖** — 核心开发几乎只有 obra 一人，虽然社区活跃但决策集中
2. **「过重」的诱惑** — 技能数量增长可能超过用户的承受能力，21 个技能已经让部分用户不知所措
3. **Agent 兼容性脆弱** — 依赖各 Agent 平台的插件机制，平台 API 变化会直接影响 Superpowers 的可用性
4. **Sonnet 5 等新模型的不稳定** — 新模型可能「不服管教」，需要 obra 不断调整指令

### 适用场景 & 不适用场景

**✅ 适合**：
- 使用 Claude Code / Codex 进行中大型软件项目的开发
- 团队标准化 AI 辅助开发的流程
- 研究「如何让 AI 遵循工程规范」的开发者
- 需要代码审查和质量管制的多 Agent 协作

**❌ 不适合**：
- 简单的脚本编写或一次性任务
- 不熟悉 Git 工作流的初学者
- Windows 用户（兼容性还不稳定）
- 追求「写完就跑」的快速原型开发

### 趋势判断

**高速上升期**（但正在跨越「从网红项目到基础设施」的鸿沟）。246K ⭐ 证明了市场需求，但 Superpowers 能否从「热门项目」变成「行业标准」取决于几个因素：多维护者化（单点风险）、Windows 兼容性、和「轻量模式」（为 90% 的简单场景做个缩水版）。

2026 年下半年趋势：Agentic Framework 赛道正在从「各自为政」走向「标准化」。Superpowers 的 SKILL.md 标准可能成为事实标准——已经有 `superpowers-zh`（中文社区汉化版）和多家第三方插件。

## 📂 关键文件路径速查

| 文件路径 | 说明 |
|---------|------|
| `AGENTS.md` | **核心治理文档** — 告诉 AI Agent 的完整行为规则（必读） |
| `CLAUDE.md` | Claude Code 专属配置 |
| `skills/subagent-driven-development/SKILL.md` | SDD — 核心技能，任务分解 + 子 Agent 调度 |
| `skills/systematic-debugging/SKILL.md` | 系统化调试方法论 |
| `skills/brainstorming/SKILL.md` | 可视化头脑风暴技能 |
| `skills/requesting-code-review/SKILL.md` | 代码审查请求规范 |
| `hooks/hooks.json` | Hook 系统配置（session-start） |
| `docs/plans/` | 14 份架构决策日志（追踪框架演进） |
| `docs/superpowers/specs/` | 功能规格设计文档 |
| `docs/superpowers/plans/` | 详细实现计划 |
| `LICENSE` | MIT License |

**数据来源**：`gh repo view`, `gh issue list --limit 20`, 掘金/知乎深度评测（2026 年 3-4 月），CSDN 技术博客，头条 Claude Code 插件对比。调研时间 2026-07-05。
