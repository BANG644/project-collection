# 🔬 withkynam/vibecode-pro-max-kit — 全方位深度调研

> 调研时间：2026-11-24（修旧账重写，原稿为 2026-06-19 抽样模板报告）
> 数据来源：`gh api` 实时抓取（元数据 / README 99KB / 文件树 205KB / Issues / Release / `CLAUDE.md` / `AGENTS.md` / `vc-manifest.json` / `context-builder.cjs`）+ 第三方评测（FollowAgents FARS / topairepos / repo-explainer / GitCode）

## 📌 一句话定位

一套「AI 编码操作系统」式的 harness 套件：把单次编码请求强制拆成 RIPER-5 七阶段（研究→规格→创新→计划→验证→执行→更新），每阶段用工具权限锁死（研究阶段只读、计划阶段只写 process/），由 15 个专职 sub-agent + 33 个 skill 分工，两条自修复质量循环（PVL 查计划、EVL 独立复测），状态落盘以扛住会话重置——主打「让 AI 像一支有纪律的工程团队工作，而不是一个飞快的自动补全」。

> 核心判断：它是目前「流程最重、约束最硬」的 AI 编码 harness——**用文件系统和 hook 当控制平面，用 sub-agent 权限隔离当纪律**。但第三方 FARS 评分仅 47/100，文档宣称（33 skills / 36 validators 数字不一）与自动化评测存在落差，"流程最严"既是卖点也是门槛。

**实时数据**：1,173⭐ / 232 forks / JavaScript / MIT / 23 open issues / 最后推送 2026-06-21 / manifest v3.2.5。

## ⭐ 项目亮点

1. **工具权限按阶段锁死（step-locked）**：RESEARCH 只读、INNOVATE 无 Write、PLAN/VALIDATE 只写 `process/`。这不是 prompt 建议，而是真实能力限制。repo-explainer 评价：这套 hook「像操作系统用 syscall 一样——不是激励行为，而是约束行为」，是全项目最核心的设计。
2. **主 Agent 永不碰代码**：协调者（orchestrator）只做 4 件事——技能发现、意图识别、路由、监控；每次编辑和测试都在专职 sub-agent 里完成（code → vc-execute-agent，test → vc-tester）。第三方称之为"structurally honest"（结构性诚实）——消灭隐藏执行。
3. **双质量循环 PVL + EVL**：PVL（Plan Validation Loop）让计划过 V1–V7 检查点产出 PASS/CONDITIONAL/BLOCKED；EVL（Execution Validation Loop）由独立测试 agent 复跑全部检查项。两个循环各自能_self-heal_，且共享一个 autoresearch 引擎。
4. **Autopilot 三通道 + /goal 授权令牌**：quick/fast/full 三档按风险匹配仪式感；hands-free 跑完整流程，只在三种"硬停"打断——不可逆外部操作、连续多阶段卡死、需真钱的外部调用。状态每阶段落盘，会话重置可精确续跑。
5. **跨 7 工具零适配**：靠 AGENTS.md + SKILL.md 两个开放标准支持 Claude Code / Codex / Cursor 等，`vc-manifest.json` 用 `symlinks` 把 `.agents/skills` 指向 `.claude/skills`，一处维护多处生效。

## 🏗️ 项目架构全景

### 目录骨架（文件树实证）

```text
vibecode-pro-max-kit/
  ├─ .claude/
  │   ├─ agents/    ← 15 个专职 agent（vc-research / vc-plan / vc-execute / vc-tester /
  │   │              vc-code-reviewer / vc-debugger / vc-ui-ux-designer ...）
  │   ├─ skills/    ← 33 个 skill（关键词自动发现匹配）
  │   ├─ hooks/     ← 控制平面：权限拦截 / 状态持久化 / 阶段推进
  │   │   └─ lib/   ← context-builder.cjs / session-state-manager.cjs / privacy-checker.cjs ...
  │   └─ settings.json
  ├─ .codex/        ← Codex 对应布局
  ├─ .agents/skills → symlink 到 .claude/skills
  ├─ process/       ← 落盘的项目记忆：features/ context/ general-plans/ development-protocols/
  ├─ CLAUDE.md (29KB) / AGENTS.md (38KB) / vc-manifest.json / install.sh
  └─ compute-sync-plan.mjs / resolve-manifest.mjs / e2e-kit-flows.test.mjs
```

**关键观察**：13 个 `vc-*-agent.md` 文件（research/plan/spec/execute/tester/validate/debugger/code-reviewer/code-simplifier/ui-ux-designer/git-manager/innovate/fast-mode/update-process/quick-fix）是"职责即文件"的设计——每个 agent 一个 markdown 定义，职责边界写进 system prompt。

### RIPER-5 七阶段流水线

```text
Step0 技能发现（扫 33 skills 关键词匹配）
  → Research（只读调研） → Spec（需求文档，用户签字）
  → Innovate（2-3 方案取舍，无 Write） → Plan（可执行清单，限定可碰文件）
  → Validate（PVL：V1-V7 检查点 → PASS/CONDITIONAL/BLOCKED）
  → Execute（EVL：独立 tester 复跑全部检查项）
  → Update Process（经验回写项目记忆，文档不腐化）
```

## 💡 应用场景与启发（重点章节）

### 典型使用场景（来自官方与第三方）

- **PM/创始人的"技术联合创始人"**：`Build me a SaaS with auth, billing, and landing page`——先出架构计划供审、实现带测试、每个决策可被审计。
- **设计还原**：给 Figma 截图，design-aware agent 逐组件实现并起视觉对比检查。
- **零停机重构**：研究现有鉴权 + 业界 RBAC 方案 → 写迁移计划标注影响文件 → 带回滚说明地实施。
- **大型多阶段项目**：umbrella plan + 每阶段内循环 + 回归检查，配合 phase program 自重塑。

### 可借鉴的解决方案模式

1. **"用 hook 做权限层，而非 prompt 做建议"**。这是全项目最值得抄的思想：想让 Agent"研究阶段别写代码"，与其在 prompt 里说"请不要写"，不如在 hook 层把 Write 工具拿掉。**约束要落在能力层，不能落在意愿层**。
2. **协调者/执行者分离 + 结构化状态码**。每个 sub-agent 必须以 `DONE / DONE_WITH_CONCERNS / BLOCKED / NEEDS_CONTEXT` 之一结束，协调者不忽略 BLOCKED、不重复同一阻塞路径三次。这套"状态契约"是让多 Agent 编排可诊断的关键。
3. **双循环分离"查计划"与"验执行"**。PVL 管计划质量、EVL 管实现正确性，各自独立 self-heal。做 Agent 质量体系时，把"计划评审"和"结果验证"分开是重要的架构决策。
4. **上下文预算的系统化监控**。`context-builder.cjs` 里 `WARN_THRESHOLD=70 / CRITICAL_THRESHOLD=90`、注入去重 TTL（5min/30s）、"每个 subagent 只有 200K tokens，聪明地委派"的显式提醒——把 token 治理做成运行时机制而非事后统计。

### 同类需求的可参考思路

如果要在自己的 Agent 体系里引入"强制流程"，本项目的 RIPER-5 + 权限锁 + 状态码是可参考的完整设计。但要清醒：**它假设你愿意为连续性牺牲速度和自由度**——repo-explainer 说得好，"most AI coding tools are optimized for speed, this one for continuity"。

### 门槛提醒（第三方一致指出）

Node.js ≥ 22 + bash（Windows 需 Git Bash/WSL，不支持 PowerShell）；安装创建大量文件可能吓到新手；autopilot 依赖状态文件完好（损坏则续跑失败）；智能模型策略用 opus 级模型写代码可能推高成本；缺详细排障文档。

## 🧠 核心源码解读

### 上下文构建器：注入治理（`context-builder.cjs`，31KB）

这是"控制平面"的具体实现，几个关键常量直接揭示设计：

```js
const RECENT_INJECTION_TTL_MS = 5 * 60 * 1000;   // 近期注入去重窗口
const PENDING_INJECTION_TTL_MS = 30 * 1000;      // 待处理注入窗口
const WARN_THRESHOLD = 70;                        // 上下文用量告警线
const CRITICAL_THRESHOLD = 90;                    // 严重线
```

`reserveInjectionScope()` / `hasRecentInjection()` / `pruneReminderScopes()` 一套函数实现**注入作用域去重**——防止同一提醒在多个 scope 重复塞进上下文。`buildSessionSection()` 里明确提示"each subagent only has 200K tokens... spawn and delegate intelligently"，把上下文预算意识灌输给模型。这是把"上下文工程"落成代码的范本。

### 分发清单：`vc-manifest.json`（2.7KB）

manifest 用 `include / exclude / symlinks / kitOnly / legacyDeletions` 五段精确控制"哪些文件进用户项目、哪些只留在 kit"：

```json
"symlinks": { ".agents/skills": "../.claude/skills" },
"kitOnly": ["README.md", "docs/**", "install.sh", "resolve-manifest.mjs", ...],
"legacyDeletions": [".claude/skills/vc-team", ...]  // 升级时清理旧版残留
```

**独家发现**：`legacyDeletions` 列出了 10+ 个被废弃的旧 skill 目录（vc-team / vc-chrome-devtools / vc-docs…）——说明这个项目经历过大规模重构，manifest 承担了"升级迁移"职责。这是 kit 类工具少见的工程细节，README 完全没提。

### code-reviewer agent：staff-engineer 级检查清单

`vc-code-reviewer.md` 定义了生产就绪审查——并发竞态、N+1 查询、信任边界、错误传播、数据泄漏等 checklist，并要求高风险工作产出 `review-decision.json`。这揭示了项目的野心：不只是"写代码"，而是"写能过生产审查的代码"。

## 📐 架构决策与设计哲学

- **连续性 > 速度**：明确对标"聪明的实习生"式 AI 编码，用流程约束换来长项目的连贯性。
- **能力约束 > 行为建议**：hook 层做权限拦截，prompt 层做职责描述——两层配合。
- **文件系统即记忆**：plans / reports / knowledge 全落盘，启动 hook 恢复审批门禁。
- **深度 > 广度**：GSD 支持 14 运行时，它只做 7 个但每个带完整 harness/hook——README 明说"breadth vs depth: your choice"。
- **自改进**：`Update Process` 阶段把经验回写主题分组的知识库，下次交付自动带上。

## 🌐 全网口碑画像（5+ 真实来源）

- **FollowAgents FARS-2.1 评分 47/100（Major gaps）**：Trust 12/29（least privilege 未明确、autopilot 可能绕过用户确认、数据流透明度不足）、Reliability 6/14（"33 skills vs 36 validators" 数字不一致）、Verifiability 仅 3/8。但也肯定"non-destructive install with backups"、README 与代码结构基本一致。来源：followagents.com/en/agents/vibecode-pro-max-kit
- **repo-explainer（正面深评）**："The hooks are the real control plane... using the filesystem and hook layer the way an operating system uses syscalls — not to inspire behavior, but to constrain it"；"most AI coding tools are optimized for speed, this repo is optimized for continuity"。来源：repo-explainer.com/withkynam/...
- **topairepos**：收录完整竞品对比表（vs Superpowers / GSD / gstack），确认 RIPER-5 七阶段、PVL+EVL 双循环、7 工具支持等核心宣称。来源：topairepos.com/repos/withkynam/vibecode-pro-max-kit
- **GitCode 中文评测**：定位"流程最严、记忆最长、无人值守最强"，详述七阶段门禁与 Autopilot 三通道；指出 GSD 运行时覆盖更广（14 vs 7）。来源：blog.gitcode.com（vibecode-pro-max-kit 对比 Superpowers 与 GSD）
- **claudewave 收录 code-reviewer agent**：将其作为独立可安装 agent 分发，说明其子 agent 设计有复用价值。来源：claudewave.com
- **GitHub 一手**：23 open issues；最后推送 2026-06-21——相对其他 agent 项目，近 5 个月更新停滞，是活跃度隐忧。star 从评测时的 1.2k 到现在 1.17k，关注度平稳。

> 口碑结论：**理念获深度好评（"编码界的操作系统"），但自动化评测给出"主要缺陷"评分**——落差集中在可验证性、最小权限、文档数字一致性。适合愿意折腾流程的工程团队，不适合追求开箱即用的用户。

**可核验来源**：[FollowAgents FARS 47/100](https://followagents.com/en/agents/vibecode-pro-max-kit) · [repo-explainer 深评](https://repo-explainer.com/withkynam/vibecode-pro-max-kit) · [topairepos 竞品对比](https://topairepos.com/repos/withkynam/vibecode-pro-max-kit) · [GitCode 中文评测](https://blog.gitcode.com/1eab6c96aa6b2a32c3a954af4b003520.html)

## ⚔️ 竞品对比

| 方案 | 流程约束 | 质量循环 | 工具支持 | 记忆 | 定位 |
|---|---|---|---|---|---|
| **vibecode-pro-max-kit** | RIPER-5 七阶段工具权限锁 ✅✅ | PVL+EVL 双循环 | 7（深度） | 落盘自改进 | 连续性/无人值守 |
| Superpowers | 强制工作流 + 86 skills | 按单 skill | 仅 Claude Code 插件 | 插件记忆 | 技能生态最丰富 |
| GSD | 部分（上下文修复） | 无自动循环 | 14 运行时（最广） | 磁盘状态 | 多工具切换 |
| gstack | 阶段分离弱 | 无 | 单工具 | — | 元提示词 + 23 角色 |

**选择建议**：大型长周期项目 + 要无人值守 + 愿付流程成本 → 本套件；要技能生态/轻量约束 → Superpowers；要跨最多运行时 → GSD。

## 🎯 核心研判

### 优势

1. **理念完整且独特**：把"工程纪律"系统化落地（权限锁 + 专职 agent + 双循环 + 状态码），理念层面领先多数"prompt 包"。
2. **跨工具零适配**：两个开放标准打天下，manifest 工程精细。
3. **对连续性问题的深刻回答**：_session reset 可精确续跑 + 知识自改进_击中了长项目的真实痛点。

### 风险

1. **第三方评测落差明显**：FARS 47/100、可验证性 3/8、数字不一致（33 skills vs 36 validators）——宣称与实际有差距。
2. **更新停滞**：最后推送 2026-06-21，近 5 个月无更新；年轻项目停滞是危险信号。
3. **重型流程的成本**：Node 22 门槛、大量文件、opus 级模型成本、Windows 不支持 PowerShell、无排障文档。
4. **autopilot 单点依赖**：状态文件损坏即续跑失败；最小权限未明确（FARS 指出）。

### 适用场景 & 不适用场景

- ✅ 大型多阶段项目、需要审计链的场景（PM/创始人要review架构）、无人值守长任务、愿为连续性投入流程成本。
- ❌ 快速原型、小修补、Windows PowerShell 环境、追求开箱即用、账号/成本敏感场景。

### 趋势判断

**理念领先但活跃度存疑**。若能恢复迭代并补齐 FARS 指出的可验证性/最小权限缺口，有成为"重型 AI 编码 harness"标杆的潜力；若持续停滞，会沦为理念先于工程的"概念验证"。

## 📂 关键文件路径速查

| 路径 | 用途 |
|---|---|
| `CLAUDE.md` / `AGENTS.md` | 29KB/38KB 的行为规约（理解 RIPER-5 与职责边界第一站） |
| `.claude/agents/vc-*.md` | 15 个专职 sub-agent 定义（research/plan/execute/tester/code-reviewer…） |
| `.claude/hooks/lib/context-builder.cjs` | 注入治理：TTL 去重、上下文阈值、200K 提醒（控制平面核心） |
| `.claude/hooks/lib/session-state-manager.cjs` | 会话状态落盘/恢复 |
| `vc-manifest.json` | 分发清单：include/exclude/symlinks/legacyDeletions |
| `process/development-protocols/` | 开发协议（RIPER-5 各阶段规则） |
| `install.sh` / `resolve-manifest.mjs` / `compute-sync-plan.mjs` | 安装与同步引擎 |
| `e2e-kit-flows.test.mjs` | 端到端流程测试 |
| `README.md` → RIPER-5 / Two Quality Loops / Autopilot | 官方核心概念权威说明 |
