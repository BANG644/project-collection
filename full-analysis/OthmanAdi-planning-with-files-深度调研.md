# 🔬 OthmanAdi/planning-with-files — 全方位深度调研

> 调研时间：2026-11-24（修旧账重写，原稿为 2026-06-19 抽样模板报告）
> 数据来源：`gh api` 实时抓取（元数据 / README 117KB / 文件树 246KB / 60 Issues / Release / `AGENTS.md` / `scripts/check-complete.sh` / `SKILL.md`）+ 第三方评测（HighlightsX / ClaudeCodeMod / DiscoverGit / claudecodeagents）

## 📌 一句话定位

把 AI 编码 Agent 的「计划 + 发现 + 进度」写成磁盘上的三个 Markdown 文件（`task_plan.md` / `findings.md` / `progress.md`），用各平台的生命周期 hook 每轮重新注入上下文，让 Agent 在 `/clear`、compaction、崩溃后都能恢复任务——**用文件系统当 Agent 的"外部工作记忆"，直接对抗 context rot（上下文腐化）**。

> 核心判断：它解决的是一个真实且普遍的痛点（上下文重置后 Agent 重读仓库、让你重述目标、重做已完成的活）。它的聪明之处在于机制极简——三个文件 + 每轮注入 + 可选完成门禁——但** enforcement 依赖各宿主是否忠实执行 hook**，这是它能力边界的根源。

**实时数据**：28,207⭐ / 2,331 forks / Shell / MIT / 14 open issues / 最后推送 2026-11-23 / v3.29.1（2026-11-23，几乎日更）。

## ⭐ 项目亮点

1. **三文件职责分离，对抗"计划被改写以匹配结果"**：`task_plan.md`=意图、`findings.md`=过程学到的东西、`progress.md`=实际做了什么。第三方 HighlightsX 点破：合在一个文件里，计划会被悄悄重写成"已完成"的样子；分开存储就保住了真实性。
2. **确定性的完成门禁（completion gate），且有精细的 5 条件决策表**。从 `check-complete.sh` 源码挖到：门禁默认关闭，必须 ①`<plan-dir>/.mode` 含 "gate" ②存在 in_progress 阶段 ③Stop hook 输入非 `stop_hook_active=true` ④阻塞计数低于上限（默认 20）⑤自上次阻塞后 ledger 有推进——全满足才拦。这种"防止 Agent 说完成但没做完"的机械约束，是同类 skill 里少有的硬核实现。
3. **跨平台分发工程做到极致**：同一份 skill 通过 Agent Skills 开放标准铺到 60+ Agent（Claude Code / Codex / Cursor / Copilot / OpenCode / Hermes / Gemini / Kiro / Pi / CodeBuddy…），仓库里 `.claude/ .codex/ .cursor/ .agents/ .opencode/ ...` 一堆镜像目录并非冗余，而是 per-host 原生布局。自 v3.7.0 起从普通 git clone 即可被标准路径发现。
4. **hook 性能优化有据可查**：v3.6.0 把单次 hook 从 2.0–2.4 秒压到 **289ms**，且注入块是 KV-cache 稳定的（结构不变，可命中缓存）。ClaudeCodeMod 记录了这组数据。
5. **多 Agent 编排的"所有权"规约**：`AGENTS.md` 明确定义——orchestrator 拥有 `task_plan.md`，worker 通过自己的 ledger 汇报，不各自改写共享计划；Markdown on disk 是跨 Agent 共享状态，**无运行时内存状态**。

## 🏗️ 项目架构全景

### 仓库骨架（39 个顶层目录，文件树实证）

```text
planning-with-files/
  ├─ .agents/skills/planning-with-files/   ← Agent Skills 标准路径（cross-tool）
  │    ├─ SKILL.md (38KB!) / examples.md / plan-inventory.md / reference.md
  ├─ .claude/ .codex/ .cursor/ .opencode/ .hermes/ .gemini/ .kiro/ .pi/ ...
  │    └─ 各宿主原生 skill/plugin 布局（大多是同一 SKILL 的镜像）
  ├─ .claude-plugin/ (marketplace.json / plugin.json)  ← Claude 插件市场分发
  ├─ scripts/  ← init-session.sh / check-complete.sh / resolve-plan-dir.sh / attest-plan.sh / bump-version.py ...
  ├─ hooks/    ← 生命周期 hook（UserPromptSubmit / Stop / PreCompact ...）
  ├─ commands/ templates/ examples/ tests/ docs/
  └─ AGENTS.md / CHANGELOG.md / CITATION.cff / MIGRATION.md / SECURITY.md
```

**关键观察**：SKILL.md 高达 38KB（约 10k tokens）——这本身成了一个 Issue（"SKILL.md is about 10k tokens: Claude Code keeps the first 5,000 after compaction"）。项目大受欢迎后，文档膨胀开始反噬。

### 三文件模式与运行链路

```text
任务开始 → /plan 或 init-session.sh 建 plan（可 .planning/<id>/ 隔离）
  → 每轮 UserPromptSubmit hook：从磁盘重新注入"当前阶段/发现/进度"
  → Agent 执行，按规则写回三文件（每阶段更 plan、一有发现更 findings、全程更 progress）
  → /clear 或 compaction → PreCompact hook 提醒 + 打印 Plan-SHA256
  → 恢复时从选定目录读回三文件（自动恢复只读项目文件，不读历史 transcript）
  → 完成判定：check-complete.sh --gate 按 5 条件决定是否拦截 Stop
```

## 💡 应用场景与启发（重点章节）

### 典型使用场景（第三方评测给出的真实用法）

- **跨上下文重置的长任务**：需要 5+ 工具调用、会撞上 `/clear` 或 compaction 的多步任务——这是 skill description 自己写明的门槛。
- **多 Agent 并行工作流**：orchestrator + workers，各 worker 用独立 ledger，共享计划由 orchestrator 单一持有；`.planning/<id>/` slug 目录隔离并行任务。
- **Claude Code plan mode 的接续**：两者互补而非替代——先在 plan mode 设计批准方案，再让它写进 `task_plan.md` 进入执行。

### 可借鉴的解决方案模式

1. **"磁盘即共享状态"的多 Agent 协作范式**。当多个 Agent 需要协作，与其做复杂的消息总线，不如约定"文件是唯一真相来源"。AGENTS.md 里的所有权规约（谁写哪个文件、worker 不碰共享计划）是这套范式能跑起来的关键——**光有文件不够，必须有写入权限的显式约定**。
2. **"每轮重新注入"抵抗 context rot**。把关键状态从"对话开头"搬到"每轮开头"，是对抗大模型注意力衰减的直接手段。这一手可用于任何长会话 Agent：把目标/约束/当前阶段用 hook 每轮塞进上下文。
3. **可选 + 多条件的完成门禁**。它不强制开启，且开了也有 5 个条件 + 阻塞上限（防止无限拦） + stall 检测（停滞则放行）。这是"机械约束"设计的范本——**强约束必须有逃生阀**，否则 Agent 会卡死。
4. **SHA-256 plan attestation**（v2.37.0）：`attest-plan.sh` 把当前 plan 内容锁成哈希，hook 发现文件偏离哈希就拒绝注入。这解决了"计划被悄悄篡改"的信任问题——值得任何需要"人批准过的计划不可被 Agent 偷改"的场景借鉴。

### 同类需求的可参考思路

如果你要给自己做"Agent 长期记忆"，本项目的定位很清楚：**它管的是"当前任务的执行状态"（阶段/进度/完成判定），不是"跨任务的事实检索"**。后者该用 agentmemory 这类记忆层。二者互补。DiscoverGit 的对比也印证了这点。

### 成本/边界提醒

每轮重新注入三个文件要花 token；短任务上是纯开销（HighlightsX 明确指出）。文件只如实反映 Agent 写的内容——一个谎报进度的模型会产出"自信但错误"的 progress.md 并持久化。**它解决连续性，不解决诚实性**。

## 🧠 核心源码解读

### 完成门禁的决策表（`scripts/check-complete.sh`，13.9KB）

这是全仓库最值得读的代码。头部注释直接给出 gate 触发的 5 个条件（见亮点 2），并明确「默认 advisory 报告永远 exit 0，只有 opt-in gate 才可能拦」。几个 engineering 细节：

```bash
# stdin 处理：只在 fd 0 非 TTY 时读，避免交互挂起
[ -t 0 ] || read -r HOOK_JSON
# 显式选择器是绑定不是提示（issue #237）：解析失败就退出，绝不回退到 ROOT plan
echo "[planning-with-files] An explicit PLAN_ID ... did not resolve ..."; exit "$VALIDATE"
```

**独家发现 1**：`--validate` 与 gate 是两条独立路径——history Issue「check-complete: --validate 和 completion counter 读不同语法（合法 plan 可能被判无效）」说明两套 grammar 曾漂移，是维护中的真实技术债。

**独家发现 2**：计数逻辑刻意排除 fenced code block（`#377`），用 awk 状态机跟踪 fence 开合——因为 plan 文档里的示例代码也会被当作状态行误计。

### 计划选择器的歧义处理（issue #237 的修复）

`resolve-plan-dir.sh` 支持 `PLAN_ID` / `.planning/.active_plan` / 最新 mtime 三级解析。当显式 `PLAN_ID` 解析失败，脚本**拒绝回退**到根 plan——因为"用一个错误 plan 的完成状态回答，等于在决定一个 autonomous run 能否停止"，这是安全问题。这种"失败要显式、不静默降级"的取舍很值得学。

### 版本发布工程（`AGENTS.md`，4.7KB）

维护者规则里藏着大量实践智慧：contributor PR 必须 rebase/cherry-pick 保留 Author（曾因 squash 错误归属）；禁止 `--no-verify`；版本由 `bump-version.py` 统一管理（19 个跟踪文件 + parity 测试），**脚本和测试是真相来源而非 prose 清单**；发布后手工分发到 ClawHub / npm / skills.sh；公开文案必须过 `/humanizer`（禁 em-dash、禁客套）。这份文件本身就是"Agent 时代维护者 SOP"的优秀范本。

## 📐 架构决策与设计哲学

- **磁盘 > 上下文**：核心哲学一句话——"Markdown on disk is the shared state; no runtime-only state"（AGENTS.md）。
- **显式优于隐式**：选 plan 失败不回退、gate 需 opt-in、完成需 ledger 推进——处处避免"猜"。
- **维护者克制**：公开文案去 Em-dash、去客套；贡献者归属精确；供应链审计（新依赖/install script/bin shim）写进流程。
- **Delivery 手动但严谨**：ClawHub SSL 证书过期也要"proceed through warning"——真实运维细节，README 绝不会写。

## 🌐 全网口碑画像（5+ 真实来源）

- **HighlightsX**："Every coding agent loses its working memory when the context resets... the plan should not live in the context window at all"。给出弱点：短任务是纯开销；文件只如实于写它的 Agent（谎报会持久化）。数据点：v3.10.1 时期 26k⭐ 仅 7 open issues，"heavy use with a quiet tracker"。来源：highlightsx.github.io/planning-with-files
- **ClaudeCodeMod 市场页**：详述 UserPromptSubmit 每轮注入、v3.7.0 标准路径 clone 即发现、hook 289ms、KV-cache 稳定。来源：claudecodemod.com/marketplaces/othmanadi-planning-with-files
- **DiscoverGit 8/10**："simple and language-agnostic: markdown files on disk, no runtime server, no proprietary format"；列出 3 大风险——平台 hook API churn / benchmark 自报不可独立验证（96.7% pass、5.0 vs 13.3 turn recovery）/ 大规模重注入开销。来源：discovergit.app/repo/OthmanAdi/planning-with-files
- **claudecodeagents.com**：收录为 Claude Code 多 Agent 插件，28,193⭐，列入 awesome-claude-code-toolkit；引述用户评价"The planning skill your agent cannot ignore"。来源：claudecodeagents.com/mods/planning-with-files
- **SkillsLLM 安全扫描 PASSED**（2026-04-16）：npm audit + pip audit 无高危；但 semgrep 未运行。来源：skillsllm.com/skill/planning-with-files/
- **GitHub 一手**：14 open issues（对 28k⭐ 而言极低，说明成熟稳定），但内容揭示真实痛点——SKILL.md 10k tokens 超 compaction 保留窗、Python 3.8+ 静默失败、check-complete 语法漂移、Windows/PowerShell 支持缺口、Git Bash 上 plan 列表脚本 26 秒。

> 口碑结论：**"小功能做到极致"的典范**——高频好评是可靠、无依赖、跨 60+ Agent；主要质疑是 benchmark 自报、hook API 依赖平台、以及文档膨胀带来的上下文开销。

**可核验来源**：[HighlightsX 评测](https://highlightsx.github.io/planning-with-files) · [ClaudeCodeMod 市场页](https://claudecodemod.com/marketplaces/othmanadi-planning-with-files) · [DiscoverGit 8/10](https://discovergit.app/repo/OthmanAdi/planning-with-files) · [claudecodeagents.com](https://www.claudecodeagents.com/mods/planning-with-files) · [SkillsLLM 安全扫描](https://skillsllm.com/skill/planning-with-files/)

## ⚔️ 竞品对比

| 方案 | 核心差异 | 状态载体 | 完成门禁 | 多 Agent |
|---|---|---|---|---|
| **planning-with-files** | 磁盘三文件 + 每轮注入 | Markdown 文件 | ✅ 可选 5 条件门禁 | 所有权规约 |
| rohitg00/agentmemory | 运行层持久记忆（ richer retrieval） | 运行时记忆层 | ❌ | — |
| Claude Code plan mode | 执行前设计审批 | 上下文内 | ❌ | — |
| 手写 todo.md | 无 hook 自动注入 | 文件 | ❌ | ❌ |

**选择建议**：要"当前任务连续性 + 机械完成判定" → 本项目；要"跨任务事实检索" → agentmemory；要"执行前审批" → plan mode。三者互补。

## 🎯 核心研判

### 优势

1. **解决真痛点且机制极简**：三文件 + hook 注入，无服务器、无专有格式，7 个月做到 28k⭐。
2. **成熟度高**：14 open issues、日更 release、58 贡献者、跨平台分发工程完善。
3. **硬核的完成门禁与所有权规约**：从"说完成"到"证明完成"，从单 Agent 到多 Agent 共享状态，都有机械约束。

### 风险

1. **平台 API 依赖**：hook 机制相对新，宿主改 API 可能静默破坏注入。
2. **benchmark 自报不可验证**：96.7% pass / 5.0 vs 13.3 turn recovery 是作者内部评测，无独立复现。
3. **文档膨胀反噬**：SKILL.md 38KB / 10k tokens，compaction 后只保留前 5000，可能丢关键规则。
4. **解决连续性不解决诚实性**：谎报进度的 Agent 会持久化错误状态。

### 适用场景 & 不适用场景

- ✅ 5+ 工具调用的长任务、会撞 `/clear`/compaction 的会话、多 Agent 协作需共享计划。
- ❌ 短任务（纯开销）、需要语义检索历史事实、需要强隔离的团队 CI 流程（多 Agent 并行隔离仍在演进）。

### 趋势判断

**成熟稳定期**，仍在高频迭代（v3.29.x，几乎日更）。下一步关键在于 hook 稳定性与文档瘦身；护城河是"标准路径 + 跨平台分发 + 完成门禁"，而非机制本身（机制极易被复制）。

## 📂 关键文件路径速查

| 路径 | 用途 |
|---|---|
| `.agents/skills/planning-with-files/SKILL.md` | 权威 skill 定义（38KB，注意 compaction 截断问题） |
| `scripts/check-complete.sh` | 完成门禁 5 条件决策表 + awk 状态计数（核心源码） |
| `scripts/resolve-plan-dir.sh` / `.ps1` | plan 解析（PLAN_ID / active_plan / mtime），歧义不回退 |
| `scripts/attest-plan.sh` | SHA-256 计划锁定，防篡改（v2.37.0） |
| `scripts/init-session.sh` | 建计划（根 legacy 或 .planning/<id>/ 隔离） |
| `AGENTS.md` | 维护者 SOP + 多 Agent 所有权规约 + 发布流程 |
| `templates/{task_plan,findings,progress}.md` | 三文件模板 |
| `hooks/` | 生命周期 hook（UserPromptSubmit / Stop / PreCompact） |
| `.claude-plugin/marketplace.json` | Claude 插件市场分发配置 |
