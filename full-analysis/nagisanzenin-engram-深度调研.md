# 🧠 nagisanzenin/engram — 基于证据的学习引擎（Claude Code / Codex 插件）

> **仓库**: [nagisanzenin/engram](https://github.com/nagisanzenin/engram)
> **Stars**: 472 | **Forks**: 58 | **语言**: Python（stdlib only）| **License**: MIT
> **创建**: 2026-07-05 | **最后推送**: 2026-07-09 | **版本**: v0.4.4 | **Open Issues**: 1
> **Topics**: claude-code, claude-code-plugin, fsrs, learning-science, spaced-repetition, education
> **调研日期**: 2026-07-10 | **数据来源**: GitHub API + README + docs/03-architecture + engram.py 源码

---

## 一、项目定位

Engram 是一个**证据驱动的学习引擎**，以 Claude Code / Codex 插件形态存在。它解决一个具体痛点：*Claude 能把任何东西讲得明明白白，你点头觉得自己懂了，十天后面一试全忘了*——因为聊天没有你的记忆、没有"你真懂没懂"的检验、也没有对抗遗忘的复习计划。

Engram 补上这三块缺失：**让你先产出答案的导师 + 盲审你真实掌握度的考官 + 在你要忘之前把你拉回来的调度器**。三个 slash 命令：`/learn`（学）、`/review`（复习）、`/coach`（仪表盘/策略）。100% 本地、无账号、无云服务。

---

## 二、项目亮点

1. **"检索即证据"的 Oracle 哲学** — 掌握度**只**由"在测试条件下被评分的自由回忆/应用/迁移"确立，绝不靠"我懂了"的自我感觉（也不靠导师说"懂了"）。把学习验证做成可执行的 oracle，而非 LLM 主观判断。
2. **FSRS-4.5 调度 + Receipt 强制** — 用开源间隔重复算法 FSRS-4.5 排复习；每次评分都落一条 receipt `(item, production, confidence, grade, misconceptions)`，状态转移**必须**有 receipt，否则不发生。
3. **确定性核心与 LLM 严格分工** — 所有日期/稳定性计算都在 `scripts/engram.py`（纯 stdlib CLI）里跑，LLM **从不**算日期；只有"评分"需要干净上下文隔离（独立 assessor agent）。
4. **omni-repo 跨 harness** — 同一套 skills + 引擎在 Claude Code 和 OpenAI Codex 都能跑（`.claude-plugin/` + `.codex-plugin/`），安装命令对称。
5. **工程完成度反差感** — 极早期（v0.4.4，5 天）却已 **70/70 selftest 通过**，状态全 human-readable JSON，且 `session-start` hook 只在有到期复习时才轻推、其余时间静默。

---

## 三、核心架构

设计 DNA 继承自 `claude-code-production-grade-plugin`，但把"软件验证"转置成"学习验证"：

```
engram/
├── skills/
│   ├── learn/SKILL.md        # /learn — 获取（诊断→推导→验证→排程）
│   ├── review/SKILL.md       # /review — 到期检索，2 分钟零摩擦
│   ├── coach/SKILL.md        # /coach — 仪表盘/策略/实验/排程
│   └── _shared/              # 对话语法、rubric、FSRS 参考、契约
├── agents/
│   ├── engram-curriculum-architect.md  # 主题→第一性原理 DAG（带类型边）
│   ├── engram-assessor.md              # 独立考官，受 rubric 约束，产出 receipt
│   └── engram-artifact-smith.md        # 按 Explorable Contract 生成可探索工件
├── hooks/
│   ├── hooks.json
│   └── session-start.sh      # 重新锚定：到期数轻推；无事则静默
└── scripts/
    └── engram.py             # 确定性核心：FSRS-4.5 + 状态 + receipt + 统计 + selftest
```

**关键设计决策**（来自 docs）：
- **导师就是主对话本身**（受 `_shared/dialogue-grammar.md` 治理），只有**评分**需要 fresh-context 隔离（assessor agent）——刻意反转父项目的"菜单用于知识"，这里"导航用方向键、检索永远开放式产出"。
- **状态全部落在 `~/.claude/learning/`**，human-readable、schema 版本化、与生态约定共存：

```
~/.claude/learning/
├── learner-model.json     # 开放学习者模型（可读）
├── graphs/<topic>.json    # 概念 DAG：每节点 mastery + FSRS 状态
├── receipts/<topic>.jsonl # 仅追加的评分证据
├── misconceptions.json    # 个人错误目录，挂到节点
├── sessions.jsonl         # 遥测：模式/时长/结果
├── experiments.json       # n-of-1 策略试验
└── artifacts/<topic>/<node>.html
```

---

## 四、应用场景与启发

**适用场景**
- 用 Claude Code 学任何东西（Kalman 滤波、音乐理论、Rust 生命周期…）并**真正记住**——尤其适合需要"第一性原理推导"的技术主题。
- 构建个人"开放学习者模型"：兴趣、目标、策略权重、节奏全在你机器上，可随时读、可迁移。
- 把"学习科学"（间隔重复、自由回忆、提取练习）直接嵌进日常 coding agent 工作流。

**给同类需求的解决思路（启发）**
- **把"可信状态"和"LLM 推理"彻底分开** —— 凡是可确定性计算的（排程、校验、迁移）一律用代码做 oracle，LLM 只做需要语言理解的部分。这是任何"Agent + 持久状态"系统的铁律。
- **receipt/enforcement 模式** —— 关键状态变更必须附带可审计证据（这里是一条 JSONL receipt），比"让 Agent 自己记住"可靠得多。可直接套用到任何需要"防 Agent 瞎改状态"的场景。
- **第一性原理概念图 > 章节顺序** —— curriculum-architect 按"什么必须先懂什么"建 DAG 并标记 THRESHOLD 概念，比顺着书的目录学更有效。
- **SessionStart re-anchor** —— 每次会话开始从磁盘重载学习者模型 + 到期队列，让 Agent 永不信任自己对话里的"记忆"。这是对抗 Agent 上下文漂移的轻量范式。

---

## 五、源码深度解读（engram.py 确定性核心）

### 1. FSRS-4.5 参数与评级映射

```python
W = [0.4872, 1.4003, 3.7145, 13.8206, 5.1618, 1.2298, 0.8975, 0.031,
     1.6474, 0.1367, 1.0461, 2.1072, 0.0793, 0.3246, 1.587, 0.2272, 2.8755]
DECAY = -0.5
FACTOR = 19.0 / 81.0          # 使 R(t=S)=0.9
RATINGS = {"again": 1, "hard": 2, "good": 3, "easy": 4}
GRADE_OF_RATING = {"again": "lapsed", "hard": "partial",
                   "good": "recalled", "easy": "recalled"}
OUTCOME_OF_GRADE = {"recalled": 1.0, "partial": 0.5, "lapsed": 0.0}
RETENTION_DEFAULT = 0.90      # 目标留存
```

`W` 即 FSRS-4.5 的 17 维权重；`RATINGS`/`GRADE_OF_RATING` 是"评级↔掌握度"的双射，用于校准回退与不一致告警。日期与稳定性**全部在此 CLI 内算**，LLM 只传评级。

### 2. 不可信输入防护（untrusted-input guards）

```python
_SLUG_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
# 所有外部 topic/文件名先过 slug 校验；ENGRAM_TODAY 冻结"今天"便于测试
```

状态文件名、topic key 都先过 slug 正则；`ENGRAM_TODAY=YYYY-MM-DD` 与 `selftest` 在临时目录跑，保证确定性可测——这正是它 **70/70 selftest** 的底气。

### 3. 状态契约（learner-model.json 节选）

```json
{
  "schema": 1,
  "memory": { "desired_retention": 0.90, "interval_multiplier": 1.0, "last_refit": null },
  "challenge_band": { "target_success": 0.85, "hint_budget": 2 },
  "interests": ["distributed systems", "woodworking", "Vietnamese history"],
  "strategy_weights": { "derivation_first": 0.6, "example_first": 0.4 }
}
```

开放学习者模型把"你想保持多高留存、给多少提示预算、偏好推导优先还是例子优先"全变成可读可调的参数——学习策略因此是**可解释、可实验**的，而非黑箱。

---

## 六、全网口碑

项目极新（创建 2026-07-05，调研时 5 天，472⭐ / 58 forks，v0.4.4）。**第三方评测/社区长文数据不可用（尚在早期）**。可观测信号：
- **工程信号强**：70/70 selftest、100% 本地、状态 human-readable、`session-start` 静默 hook，显示作者有"生产级插件"方法论底子（明确继承自 `claude-code-production-grade-plugin`）；
- **话题精准卡位** learning-science + spaced-repetition + claude-code，正是 2026 年 Agent 生态高热度交叉点；
- **omni-repo** 同时支持 Claude Code 与 Codex，分发面更广。

---

## 七、竞品对比 + 核心研判

| 维度 | **Engram** | Anki / 间隔重复 App | 让 LLM "教我" | 笔记类（Obsidian 等） |
|------|-----------|---------------------|---------------|----------------------|
| 提取练习 | ✅ 强制自由回忆 | ✅（卡片） | ❌ 只讲解 | ❌ |
| 盲审评分 | ✅ 独立 assessor + receipt | ⚠️ 自评 | ❌ | ❌ |
| 第一性原理编排 | ✅ 概念 DAG | ❌ 平铺卡片 | ❌ | ⚠️ 靠人工 |
| 本地/隐私 | ✅ 100% 本地 JSON | ⚠️ 多需云同步 | ❌ 发给模型 | ✅ |
| 嵌入 coding agent | ✅ /learn /review | ❌ | ✅ 但无验证 | ⚠️ 需手动 |

**核心研判**
- **优势**：把"学习科学"做成了**可验证、可审计、可本地拥有**的 Agent 基础设施；确定性核心 + receipt 强制的设计极其扎实，远超多数"提示词学习助手"。
- **风险**：极早期、单一作者、API 会变；依赖用户真的去 `/review`（习惯门槛）；FSRS 参数 `refit` 需积累足够证据才生效。
- **趋势**：在"Agent 不该只回答、该帮你真正掌握"这一方向上，Engram 是当前工程完成度最高的实现之一。若保持节奏，有望成为 Claude Code 学习类插件的标杆。

**一句话结论**：不是又一个"让 AI 教你"的玩具，而是把间隔重复和提取练习**焊进了 Agent 的工作流里**，并用确定性代码守住了"你到底懂没懂"的底线——想用 Claude 学硬东西并记住的人，值得 `claude plugin marketplace add` 一试。

---

## 八、关键文件路径速查

| 路径 | 说明 |
|------|------|
| `scripts/engram.py` | 确定性核心：FSRS-4.5 调度 + 状态 + receipt + 统计 + selftest |
| `skills/learn/SKILL.md` | `/learn` 获取流程（诊断→推导→验证→排程） |
| `skills/review/SKILL.md` | `/review` 到期检索 |
| `skills/coach/SKILL.md` | `/coach` 仪表盘/策略/实验 |
| `agents/engram-curriculum-architect.md` | 主题→第一性原理概念 DAG |
| `agents/engram-assessor.md` | 独立考官，产出 receipt |
| `agents/engram-artifact-smith.md` | 可探索工件生成（Explorable Contract） |
| `hooks/session-start.sh` | 到期复习轻推（无事静默） |
| `docs/03-architecture.md` | 插件设计 DNA 与状态布局详解 |
| `~/.claude/learning/` | 运行时状态（learner-model / graphs / receipts / …） |
