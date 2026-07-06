# affaan-m/ECC 深度调研报告

> **项目定位**: The agent harness performance optimization system — 智能体调度性能优化系统
> **仓库**: github.com/affaan-m/ECC | **Star**: 226,635 | **Fork**: 34,657 | **License**: MIT
> **主语言**: JavaScript | **版本**: v2.0.0 | **贡献者**: 230+

---

## 一、项目亮点

### 1.1 从黑客松项目到 226K Stars 的现象级增长

ECC（Everything Claude Code）最初是 Anthropic 黑客松获奖项目，作者 Affaan Mustafa 从 2025 年 5 月开始每日实战打磨，历时 10+ 个月成长为 AI Agent 领域最受关注的开源项目之一。项目月增 Star 最高曾达 5 万+（2026 年 3 月），增速在其品类中极为罕见。

### 1.2 它不是"配置包"，是"Agent 操作系统"

这是本文的**核心判断**——ECC 与其他同类项目的本质差异在于：

- **不是 prompt 集合**，而是完整的六大组件系统（Agents + Skills + Commands + Hooks + Rules + Scripts）
- **不是单工具插件**，而是跨 7 个 harness 的适配层（Claude Code、Codex、Cursor、OpenCode、Gemini、Zed、GitHub Copilot）
- **不是一次性安装**，而是有状态管理、健康检查、修复机制的工程系统
- **不是静态工具**，而是具备持续学习（Continuous Learning v2）的进化型系统

### 1.3 商业化与开源并行的模式

ECC 走了一条"开源核心 + 付费增值"路线：
- **MIT 许可开源**：核心代码永久免费
- **ECC Pro**（$19/seat/月）：私有仓库支持、GitHub App PR 审计
- **npm 包**：`ecc-universal` 周下载量可观，`ecc-agentshield` 独立安全工具
- **GitHub App**：ECC Tools 在 GitHub Marketplace 上架，有免费/Pro/企业三级

这种模式取得了商业赞助（CodeRabbit、Greptile、Atlas Cloud），保障了单一维护者能每周跨 7 个 harness 推送更新。

### 1.4 关键数字一览

| 维度 | 数据 |
|------|------|
| 总 Star | 226,635 |
| Fork | 34,657 |
| Agent 数量 | 67 |
| Skill 数量 | 277 (v2.0.0) |
| 遗留命令 | 93 |
| 内部测试 | 997+ |
| 语言生态 | 12 种 |
| 支持 Harness | 7 种 (Claude Code/Codex/Cursor/OpenCode/Gemini/Zed/Copilot) |
| 社区贡献者 | 230+ |
| 翻译语言 | 12 种 |

---

## 二、架构全景

### 2.1 六大组件柱

ECC 的架构是其最显著的特征。每个组件类型在 AI 辅助开发生命周期中扮演不同角色：

```
ECC = Agents + Skills + Commands + Hooks + Rules + Scripts
```

**Agents（67个）**— 专用子 Agent，用于任务委派。包括 `planner`、各语言 Reviewer、`security-reviewer`、`build-error-resolver` 等。每个 Agent 定义了角色、允许工具、最大 Token 等元数据。

**Skills（277个）**— 工作流定义和领域知识。从 TDD、E2E 测试到 Django 模式、SwiftUI 模式、PyTorch 深度学习。采用 SKILL.md 标准格式，每个 Skill 有 YAML frontmatter 定义元数据。

**Commands（93个遗留）**— 用户触发的斜杠/命名空间命令，如 `/plan`、`/tdd`、`/code-review`。v2.0.0 正在迁移到 Skills-first 模式。

**Hooks（30+）**— 生命周期事件触发的自动化。支持 PreToolUse、PostToolUse、UserPromptSubmit、Stop、PreCompact 等事件类型。

**Rules（12语言）**— 始终生效的治理规则，按语言和框架组织：`common/` + `typescript/` + `python/` + `golang/` + 更多。

**Scripts（50+）**— Node.js 基础设施：安装、卸载、状态管理、CI 集成。

### 2.2 五档安装档案

ECC 设计了清晰的安装策略，避免"一刀切"：

- **core** — 最小框架基线（6 个模块）
- **developer** — 默认工程配置（9 个模块）
- **security** — 安全重型配置（8 个模块）
- **research** — 研究和内容工作流（9 个模块）
- **full** — 完整安装（18 个模块）

配合 `npx ecc consult` 顾问式查询，用户可以先查再装、按需选配。

### 2.3 跨 Harness 适配层

这是 ECC 最独到的工程决策之一。它不是为某个编辑器写死配置，而是通过适配器模式统一不同 harness 的操作面：

```
┌─────────────────────────────────────────────┐
│   Skills/Agents/Commands (业务逻辑层)        │
├─────────────────────────────────────────────┤
│   Harness Adapter Layer (适配层)             │
├──────┬──────┬──────┬──────┬──────┬──────────┤
│Claude│Codex │Cursor│OpenCd│Gemini│ Zed ...  │
│ Code │      │      │      │      │          │
└──────┴──────┴──────┴──────┴──────┴──────────┘
```

每个 harness 有自己的配置目录（`.claude/`、`.codex/`、`.cursor/`、`.opencode/` 等），但共享同一套 Skills/Agents 核心内容。

### 2.4 状态管理与健康检查

ECC 引入了工程化的系统管理思维：

- **SQLite 状态存储** — 追踪安装了哪些组件、版本号、安装时间
- **`ecc doctor`** — 诊断当前安装的健康状态
- **`ecc repair`** — 自动修复损坏的安装
- **`ecc status --markdown --write status.md`** — 输出结构化状态快照，可用于团队交接
- **`ecc uninstall --dry-run`** — 预览卸载影响再执行

### 2.5 ECC 2.0 的 Rust 控制平面（Alpha）

v2.0.0 新增了 Rust 原型 `ecc2/`，采用三层架构：
- **Daemon Layer** — 驻留进程，管理 PTY、Git 操作、Agent 进程
- **Runtime Layer** — Workspace 运行时、Agent 注册表、SQLite 持久化
- **TUI Layer (ratatui)** — 终端仪表板，支持热键操作

目前是 Alpha 状态，但方向明确：从 JS 配置框架演进为 Rust 原生控制平台。

---

## 三、应用场景与启发

### 3.1 谁适合使用 ECC

根据对全网用户反馈的归纳，以下三类用户受益最大：

**第一类：跨工具切换的开发者**
> "你需要的不是更多 prompt，而是同一套工作标准可以跟着你走。" — AI-Chain 评测

如果你同时使用 Claude Code 写代码、Cursor 做重构、Codex CLI 做批量任务，ECC 的价值在于——只用学一次工作方式，所有 harness 行为一致。

**第二类：关注 AI 安全的团队**
ECC 的 AgentShield 安全扫描器是同类项目中独一无二的：
- 密钥检测（14 种模式）
- 权限审计
- Hook 注入分析
- MCP 服务器风险画像
- Agent 配置审查
- `--opus` 标志启动三个 Claude Opus 进行红蓝对抗审计

**第三类：Token 成本敏感的用户**
ECC 内置了精细的 Token 优化策略：
- Sonnet 作为默认模型（成本降低约 60%）
- 限制思考 Token 数量（隐藏思考成本降低约 70%）
- Opus 仅用于深度架构推理
- 环境变量 `MAX_THINKING_TOKENS`、`CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` 运行时控制

### 3.2 最具启发性的设计模式

**模式一：选择性安装架构（v1.9.0）**
```
install-plan.js (计算计划) → install-apply.js (执行安装) → state-store (记录状态)
```
这是 Manifest 驱动的安装管道，避免了"全量安装膨胀"。用户只安装需要的组件，且支持增量更新。

**模式二：Hook 运行时控制**
```javascript
export ECC_HOOK_PROFILE=minimal    // minimal | standard | strict
export ECC_DISABLED_HOOKS="pre:bash:reminder"
```
无需修改任何 hook 文件，通过环境变量即可控制钩子的行为和禁用特定钩子。

**模式三：包管理器自动检测**
检测优先级链：环境变量 → 项目配置 → package.json → 锁文件 → 全局配置 → 回退到首个可用。这种"约定优于配置 + 渐进式降级"的设计值得所有 CLI 工具借鉴。

**模式四：连续学习 v2 的 Instinct 系统**
这是 ECC 最具创新性的功能——从开发会话中自动提取模式：
- `/instinct-status` — 查看已学习的直觉及其置信度
- `/instinct-import/export` — 在团队间共享学习成果
- `/evolve` — 将相关直觉聚类为技能

### 3.3 局限性警示

**学习曲线陡峭**：六大组件 + 多种安装选项 + 大量配置，新手容易迷失。知乎用户反馈"上手需要 2-3 天才能熟悉全貌"。

**Cursor/Codex 是阉割版**：非 Claude Code 的 harness 无法享受完整 Agent 调度和命令能力，仅保留规则和上下文优化功能。

**不能与其他框架叠加**：官方明确警告不要叠加安装方法（Plugin + 手动 + full installer），社区也反映 ECC + Superpowers 同时使用可能导致流程冲突。

**部分 Pro 功能付费**：私有仓库支持、高级 PR 审计需要 $19/seat/月。

**MCP 消耗上下文**：官方警告全开 MCP 会严重压缩上下文窗口，建议活跃工具 < 80。

---

## 四、核心源码精读

此处不贴大段代码，只抽取最具借鉴价值的架构片段。

### 4.1 Skill 的标准格式（SKILL.md）

```yaml
---
name: continuous-learning-v2
description: 从会话中自动提取模式并沉淀为可复用技能
type: skill
version: 2.0.0
triggers:
  - session-end
requires:
  - node >= 18
---
```

Skill 通过 YAML frontmatter + Markdown body 定义。这种格式比 JSON Schema 更可读、更容易被 LLM 直接理解，是 ECC 生态的"协议层"。

### 4.2 安装规划引擎（scripts/install-plan.js）

```javascript
// 核心逻辑：Manifest 驱动的安装计算
function computeInstallPlan(profile, target, options) {
  const manifest = loadManifest(target);
  const profileConfig = PROFILES[profile];
  
  return profileConfig.modules
    .map(m => resolveModule(m, manifest))
    .filter(m => options.without ? !options.without.includes(m.id) : true)
    .map(m => applyOverrides(m, options));
}
```

这段代码揭示了 ECC 安装系统的核心：Manifest 是事实来源，Profile 是安装模板，`--without` 标志是运行时过滤，三者组合实现精细控制。

### 4.3 Hook 运行时控制机制

```javascript
// scripts/hooks/ 中的核心模式
const profile = process.env.ECC_HOOK_PROFILE || 'standard';
const disabledHooks = (process.env.ECC_DISABLED_HOOKS || '').split(',');

function shouldExecute(hookName) {
  if (disabledHooks.includes(hookName)) return false;
  if (profile === 'minimal' && !CORE_HOOKS.includes(hookName)) return false;
  if (profile === 'strict' && !isHookHealthy(hookName)) return false;
  return true;
}
```

三层守卫：全局禁用列表 → Profile 级别过滤 → 健康状态检查。这种设计让运行时控制零成本（不开功能时没有额外加载）。

### 4.4 跨 Harness 适配器（scripts/harness-adapter-compliance.js）

```javascript
const HARNESS_ADAPTERS = {
  'claude':   { installDir: '.claude',   pluginSystem: true  },
  'codex':    { installDir: '.codex',    pluginSystem: false },
  'cursor':   { installDir: '.cursor',   pluginSystem: false },
  'opencode': { installDir: '.opencode', pluginSystem: true  },
  'gemini':   { installDir: '.gemini',   pluginSystem: false },
  'zed':      { installDir: '.zed',      pluginSystem: false },
  'kiro':     { installDir: '.kiro',     pluginSystem: false },
};
```

适配器模式的具体实践：统一的 API 表面，不同的安装目标和能力集。PluginSystem 标志区分了哪些 harness 支持完整的插件生命周期管理。

---

## 五、口碑画像

### 5.1 综合评分（来自全网用户反馈）

| 维度 | 评分 | 说明 |
|------|------|------|
| 功能全面性 | ★★★★★ | "功能最全面" — 几乎覆盖所有场景 |
| 安全审计 | ★★★★★ | AgentShield 是独有优势 |
| 跨平台兼容 | ★★★★★ | Windows/macOS/Linux 全支持 |
| 学习曲线 | ★★☆☆☆ | "上手需要2-3天" — 最普遍的抱怨 |
| 安装复杂度 | ★★★☆☆ | 容易叠加安装导致冲突 |
| Token 优化 | ★★★★☆ | 有实践成果但需手动配置 |
| 社区活跃度 | ★★★★★ | 230+ 贡献者，Discord 活跃 |
| 文档质量 | ★★★★☆ | 有 Shorthand/Longform/Security 三本指南 |

### 5.2 真实用户反馈（来自中英文社区）

**反馈 1：知乎深度解析**
> "ECC 不是配置文件，是完整系统。解决了 AI Agent 时代的真实痛点：如何让 AI 助手更高效、更安全、更可预测地工作。" — 知乎 chenph-dev

**反馈 2：ECC vs Superpowers 对比文章**
> "ECC 是一把瑞士军刀——功能全面，模块化，可定制。适合需要精细控制和全面覆盖的团队。它的连续学习系统让工具随时间进化。" — theaiera.cn

**反馈 3：AI-Chain 技术博客**
> "它不是在卖一套更花哨的提示词，而是在回答一个更底层的问题：我们能不能把 AI 代理变成可持续运作的工程系统？" — ai-chain.tw

**反馈 4：技术栈分析网站**
> "解决了 AI 编码智能体三大痛点——上下文溢出、工具调用混乱、安全权限失控。长会话 Token 消耗平均降低 40%~70%。" — jishuzhan.net

**反馈 5：GitHub Issue 中的负面声音**
> Issue #2398 (2026-06-30): "congratulations on making this an overly complex harness." — 用户抱怨系统过于复杂，该 Issue 被迅速关闭。

### 5.3 关键 Issue 洞察

**Open Issues 揭示的痛点**（截至 2026-07-06）：
- **#2463**: Skill-Health 仪表板一直显示 0 次运行 — 生产环境功能不完整
- **#2452**: continuous-learning-v2 observer 在 Windows/Git Bash 上崩溃 — 跨平台兼容性问题
- **#2431**: install-modules.json 缺失 79 个 curated skills — Manifest 与实际不一致
- **#2428**: ESET 杀毒软件报 GenAISkill.IC 木马 — 安全误报（owner 已回应为误报）
- **#2074**: OpenCode 频繁出现 "bun: command not found" — Windows 环境配置问题

**Closed Issues 揭示的改进速度**：
- Issue 从报告到关闭通常 2-3 天（如 #2417 macOS mktemp 模板问题，7月1日报告 → 7月4日修复）
- Owner 深度参与技术讨论，回复详细（如 #2073 关于 Codex TOML 格式的讨论长达 3 轮）
- 社区 PR 活跃（30+ 社区贡献者合并）

---

## 六、竞品对比

### 6.1 核心竞争对手

| 维度 | ECC (affaan-m) | Superpowers (obra) | OpenClaude (openclaw) |
|------|----------------|-------------------|----------------------|
| **Stars** | 226K | ~247K | ~381K |
| **核心定位** | Agent 性能优化系统 | 可组合技能工作流 | Agent 通用平台 |
| **技术栈** | JavaScript/Node.js | Markdown 纯文本 | Go/Python |
| **模块规模** | 277 Skills, 67 Agents | ~20 核心 Skills | 完整 Agent 平台 |
| **安装方式** | Plugin + 5档 Profile | 一键自动激活 | 多样化部署 |
| **跨平台** | 7 harnesses | 6 harnesses | Claude + 自有 Agent |
| **状态管理** | SQLite + ECC CLI | 无额外状态 | Agent 状态机 |
| **安全性** | AgentShield 专有 | 无独立安全模块 | 内置安全机制 |
| **学习曲线** | 陡峭 | 平缓 | 中等 |
| **商业模式** | MIT + Pro $19/seat | MIT 开源 | MIT 开源 |
| **核心创新** | 连续学习 v2 / Instincts | TDD 铁律 / 子Agent | Agent 生态平台 |

### 6.2 五维对比分析

#### 核心定位
- **ECC**："Agent Harness 性能优化系统" — 解决 Agent 行为的遗忘、不一致、不安全三大系统性问题。**提供全面工具箱，按需选用。**
- **Superpowers**："可组合技能方法论" — 强调流程纪律（TDD、验证、头脑风暴）。**流程驱动，强制执行。**
- **OpenClaude**："Agent 通用平台" — 更偏向 Agent 开发和生态建设。**平台化思维。**

#### 技术栈
- **ECC**：纯 JavaScript/Node.js，好处是跨平台兼容性最好（Win/Mac/Linux 一致），但运行时性能受限于 Node。
- **Superpowers**：纯 Markdown 技能文件，零依赖、无供应链风险，但功能边界受限于无代码架构。
- **OpenClaude**：Go + Python，性能和并发有优势，但引入编译依赖。

#### 生态成熟度
- **ECC**：277 Skills、67 Agents、230+ 贡献者、12 种语言规则集。Discord 社区 + GitHub Discussions + Twitter 生态完善。有 ECC Pro 商业版和 GitHub App。
- **Superpowers**：~20 核心 Skills，精炼但有限。社区不如 ECC 活跃。
- **OpenClaude**：381K Stars 规模最大，Agent 生态最丰富。

#### 学习曲线
- **ECC**：最陡峭。六大组件 + 多种安装 Profile + 大量配置。用户反馈"新手容易迷失"。
- **Superpowers**：最平缓。安装后自动运行，用户更多扮演审批者角色。
- **OpenClaude**：中等。文档完善但功能复杂度导致学习时间较长。

#### 活跃度
- **ECC**：极其活跃。Owner 单人周更 7 harness，Issues 2-3 天关闭周期，30+ 社区 PR。
- **Superpowers**：活跃但节奏慢于 ECC，可能与精炼的 Skill 集有关。
- **OpenClaude**：Star 数最高，社区规模大，但更新频率不如 ECC 密集。

### 6.3 选择建议

| 适合场景 | 推荐方案 |
|----------|----------|
| 需要全面工具箱 + 安全审计 | ECC |
| 需要强制执行 TDD + 流程纪律 | Superpowers |
| 需要 Agent 生态平台 | OpenClaude |
| 新手入门 AI 编程 | Superpowers（平缓曲线） |
| 跨团队协作 + 成本控制 | ECC |
| 想系统学习 Agent 开发 | OpenClaude |

---

## 七、核心研判

### 7.1 ECC 的可持续性优势

**单点可持续性**：项目由 Affaan Mustafa 单人主导，但通过三方面降低了"单点故障"风险：
1. **230+ 贡献者** — 社区 PR 活跃，Issue 响应快
2. **商业赞助** — CodeRabbit、Greptile、Atlas Cloud 等赞助商保障了经济可持续性
3. **ECC Pro 收入** — $19/seat/月提供稳定现金流

**技术可持续性**：ECC 2.0 的 Rust 控制平面（Alpha）表明项目在从"配置框架"向"原生控制平台"演进，而非停留在 JS 配置层面。

### 7.2 最大隐患

**复杂性膨胀风险**：277 Skills + 67 Agents + 93 命令 = 400+ 组件。随着版本增长，维护负担和用户认知负担都在增加。Issue #2431（79个Skill未录入Manifest）就是膨胀的信号。

**跨 harness 维护负担**：维护 7 个 harness 的适配层，每个 harness 升级都可能引入兼容性问题（如 Issue #2074 的 OpenCode bun 问题）。

**单一维护者风险**：尽管有社区贡献，核心架构决策仍集中在 Owner 一人。如果 Owner 暂停维护，项目可能快速失速。

### 7.3 与 Superpowers 本质差异的判断

市场上常有人问"ECC 和 Superpowers 选哪个"，但笔者认为这个问题的前提错了——**它们不是竞争对手，而是互补物**：

- ECC 解决的是**底层基础设施**：规则立得住、记忆能持久、安全有保障、行为可预测
- Superpowers 解决的是**方法论流程**：拆解任务、强制执行 TDD、双阶段审查

最佳实践可能是：ECC 做底层 + Superpowers 做流程 + GSD 做上下文管理。三者分工清晰、互不冲突。

### 7.4 对国内开发者生态的启示

ECC 的崛起给国内开发者生态带来了几点启示：

1. **AI Agent 基础设施是蓝海** — 工具链本身比 AI 模型更稀缺
2. **跨平台一致性是刚需** — 不分中美开发者，多工具切换是普遍痛点
3. **"开源核心 + 付费增值"模式可行** — ECC Pro 验证了开发者愿意为 AI 工具链付费
4. **文档驱动增长** — ECC 的三本指南（Shorthand/Longform/Security）是其重要的增长引擎

### 7.5 综合评分

| 评估维度 | 评级 | 说明 |
|----------|------|------|
| 代码质量 | ★★★★☆ | JS 工程化良好，有 997+ 测试 |
| 架构设计 | ★★★★★ | 六大组件柱设计高效 |
| 文档完善度 | ★★★★☆ | 多语言 + 三本指南，但部分细节缺失 |
| 社区健康度 | ★★★★★ | 230+ 贡献者，Issue 响应快 |
| 商业可持续 | ★★★★☆ | Pro 版 + 赞助模式较健康 |
| 技术前瞻性 | ★★★★☆ | Rust 2.0 方向正确但尚 Alpha |
| 上手体验 | ★★☆☆☆ | 组件过多，新手友好度低 |

---

## 八、文件速查

### 8.1 根级关键文件

| 文件 | 作用 |
|------|------|
| `package.json` | npm 包 `ecc-universal` 定义，版本 2.0.0 |
| `AGENTS.md` | 根级 Agent 配置文件（Claude Code 自动检测） |
| `VERSION` | 版本号文件 |
| `install.sh` / `install.ps1` | 跨平台安装脚本 |
| `ecc_dashboard.py` | Tkinter 桌面仪表板 |
| `.mcp.json` | MCP 协议配置 |

### 8.2 核心目录速查

| 目录 | 内容 |
|------|------|
| `skills/` | 277 个 Skill 定义（核心工作流） |
| `agents/` | 67 个 Agent 定义（角色/工具/限制） |
| `commands/` | 93 个遗留斜杠命令 |
| `hooks/` | 30+ 生命周期钩子 |
| `rules/` | 12 种语言规则（common + 各语言） |
| `scripts/` | 50+ Node.js 基础设施脚本 |
| `manifests/` | 安装 Manifest 定义 |
| `mcp-configs/` | MCP 服务器配置 |
| `schemas/` | 配置 Schema 定义 |
| `plugins/` | 插件打包目录 |
| `ecc2/` | Rust 控制平面原型（Alpha） |
| `.claude/` | Claude Code 适配配置 |
| `.codex/` | Codex 适配配置 |
| `.cursor/` | Cursor 适配配置 |
| `.opencode/` | OpenCode 适配配置 |
| `.gemini/` | Gemini 适配配置 |
| `.zed/` | Zed 适配配置 |
| `.kiro/` | Kiro 适配配置 |
| `.hermes/` | Hermes Operator 配置 |
| `.codebuddy/` | CodeBuddy 适配配置 |
| `docs/` | 多语言翻译 + 架构文档 |
| `assets/` | 图片/Logo 资源 |
| `tests/` | 内部测试（997+） |

### 8.3 核心脚本速查

| 脚本路径 | 功能 |
|----------|------|
| `scripts/ecc.js` | 主 CLI 入口（list-installed/doctor/repair/status） |
| `scripts/install-plan.js` | 安装计划计算引擎 |
| `scripts/install-apply.js` | 安装执行器 |
| `scripts/uninstall.js` | 卸载工具（支持 dry-run） |
| `scripts/consult.js` | 顾问式安装查询 |
| `scripts/catalog.js` | 组件目录清单 |
| `scripts/doctor.js` | 安装健康检查 |
| `scripts/repair.js` | 自动修复 |
| `scripts/status.js` | 状态快照生成 |
| `scripts/harness-audit.js` | Harness 兼容性审计 |
| `scripts/control-pane.js` | 控制面板入口 |
| `scripts/sessions-cli.js` | 会话管理 CLI |
| `scripts/orchestrate-worktrees.js` | Git worktree 编排 |
| `scripts/loop-status.js` | 自动循环状态查看 |

---

> **报告生成日期**: 2026-07-06
> **数据来源**: GitHub API、Web 搜索、中英文社区文章
> **声明**: 本报告基于公开信息撰写，项目数据以实际仓库为准。评测观点综合自多源社区反馈，不代表作者立场。
