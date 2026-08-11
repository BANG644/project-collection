# 🔍 深度调研报告：amElnagdy/guard-skills

> **仓库**: [amElnagdy/guard-skills](https://github.com/amElnagdy/guard-skills)
> **Stars**: 1,154 ⭐ | **Forks**: 136 | **Open Issues**: 4
> **语言**: 纯 Markdown（无可执行代码） | **License**: MIT | **默认分支**: `master`
> **创建**: 2026-06-06 | **最后推送**: 2026-07-04
> **调研日期**: 2026-08-11（本次为 2026-06-18 版本的**重写升级**，补齐架构/源码/口碑/竞品/研判五个缺失维度）

---

## 一、项目定位（一句话）

**一组"防守型" Agent Skill，专门在 AI 写完代码之后做二次质量关卡——拦截的不是 lint 能查的格式问题，而是 LLM 系统性会犯的 15 类"AI 特有病"。**

---

## 二、项目亮点（差异化，开篇必读）

1. **把"AI 代码病理学"编成了可执行清单** — `references/ai-failure-modes.md` 列了 15 条 LLM 系统性失败模式，**每条都带研究出处 + Bad/Good 对照 + 自检 imperative**。这不是"写代码要清晰"这种废话，而是"LLM 因为训练奖励信号惩罚抛异常，所以学会了吞掉异常"这种根因级归因。
2. **"守卫"而非"生成"的角色反转** — 绝大多数 Skill 是让 Agent 更能干（生成、重构、搭脚手架）；这个仓库反过来，是给 Agent 装刹车。设计上明确写着：先干活，再让另一个专门关卡审 diff。
3. **零依赖的可移植性宣言** — SKILL.md 里专门有 `## Compatibility` 段落，白纸黑字承诺：不需要 MCP server、不需要网络、不需要 API key、不需要 shell、不需要本地可执行文件、不需要打包脚本。任何支持 `SKILL.md` + 相对链接引用的运行时都能跑。
4. **三模式状态机（guard-pass / live / review）** — 同一套规则体，按调用时机切换行为语义。尤其 review 模式明确规定"**不要改代码，只出结构化发现报告**"，避免审查者顺手把代码改烂。
5. **"技能加载后不许退化"的显式约束** — SKILL.md 里有一句很少见的自我约束：一旦本技能激活，**同一 session 内后续每次代码修改都要重跑自检**，不能因为"技能是早先加载的"就退回无守卫输出。这是对 LLM 长上下文衰减的直接对抗。
6. **给 AI 读者的优先级指令** — 引用文件清单里对 `ai-failure-modes.md` 特别标注："**Read this one first if you are an AI agent reading this skill. It is the highest-leverage file in the skill.**" 明确区分人类读者与 AI 读者的阅读路径。

---

## 三、核心架构

### 3.1 真实文件树（37 个 blob，`master` 分支）

```
guard-skills/
├── LICENSE  README.md  .gitignore
└── skills/
    ├── clean-code-guard/          # 通用代码质量关卡（核心）
    │   ├── SKILL.md
    │   ├── agents/openai.yaml     # 轻量展示元数据
    │   └── references/
    │       ├── ai-failure-modes.md        ← 全仓最高杠杆文件
    │       ├── naming-and-functions.md
    │       ├── comments-and-formatting.md
    │       ├── solid.md
    │       ├── dry-kiss-yagni.md
    │       ├── review-checklist.md
    │       └── sources.md                 ← 中央参考文献库
    ├── test-guard/                # 测试关卡
    │   └── references/{jest,pytest,phpunit,llm-app-testing}.md
    ├── docs-guard/                # 文档关卡
    │   └── references/{docstrings,code-samples,verification,review-checklist}.md
    ├── wp-guard/                  # WordPress 专用
    │   └── references/{security,performance,i18n,review-checklist}.md
    └── woo-guard/                 # WooCommerce 专用
        └── references/{checkout-and-money,hpos-and-crud}.md
```

### 3.2 架构模式：三层「渐进披露」

这个仓库的架构价值不在代码（它一行代码都没有），而在**上下文预算的组织方式**：

| 层 | 文件 | 何时读 | 目的 |
|---|---|---|---|
| L1 触发层 | SKILL.md 的 YAML `description` | 每次都在上下文里 | 决定"要不要激活" |
| L2 规则层 | SKILL.md 正文 | 激活时 | Always-applied imperatives + 自检清单 |
| L3 论据层 | `references/*.md` | **按需**，命中特定原则才读 | 完整规则体 + 引用出处 |

SKILL.md 明确写了 L3 的四个触发条件：① 规则理由记不清了 ② 用户对规则提出反驳、需要引用出处 ③ 处于 review 模式需要完整清单 ④ 被审代码触及特定原则（如涉及继承 → 读 `solid.md`）。

**这是 Agent Skill 设计里"引用文件不是附录，而是惰性加载的知识分片"的教科书实现。**

### 3.3 `description` 字段：一个 200+ 词的路由器

最值得抄的是 YAML frontmatter 里的 `description`——它不是简介，是**路由决策表**：

```yaml
description: Review generated or changed production code before it ships, using Clean Code,
  SOLID, DRY, KISS, YAGNI, and LLM-specific failure-mode checks in any programming language.
  Best used reactively after an agent writes, edits, refactors, or fixes code, before presenting,
  committing, or merging the result. Use when the user asks "review this PR", "is this safe to
  merge?", "make this cleaner", "audit this code", "refactor this", "fix this bug", or after a
  coding agent produced implementation code. ...
  Invoke it on your own initiative the moment you finish writing, editing, or refactoring
  non-trivial production code, before presenting or committing — don't wait to be asked.
  DO NOT USE for factual/conceptual questions, CI/tooling config, git workflow,
  running/debugging tests, pure architecture discussion, prose writing, data analysis,
  or test-code review (use test-guard).
```

三段式结构值得直接复用：**做什么 → 什么话术触发（含原话引号）+ 主动触发时机 → DO NOT USE 负向清单（并指向兄弟 skill）**。负向清单尤其关键，它是防止 Skill 过度触发、污染无关会话的唯一手段。

---

## 四、应用场景与启发 ⭐

### 4.1 什么时候该想起这个仓库

| 你的问题 | 这个仓库给的答案 |
|---|---|
| "AI 写的代码怎么老是 try/catch 吞异常？" | `ai-failure-modes.md` #1，带 Karpathy 的根因归因（训练奖励信号惩罚抛异常） |
| "我想写个 Skill，但不知道 description 该怎么写才不误触发" | 抄它的三段式 description，特别是 DO NOT USE 负向清单 |
| "Skill 内容太多，塞进上下文就爆了" | 抄它的 L1/L2/L3 渐进披露 + 四条按需加载触发条件 |
| "怎么让 Agent 在长会话里不忘记质量约束？" | 抄它那句"技能加载后每次修改都要重跑自检，不许退化" |
| "同一套规则，写代码时用和审代码时用行为该不该一样？" | 三模式状态机：guard-pass / live / review，review 模式明令禁止改代码 |
| "我要做领域专用质量守卫（金融/医疗/嵌入式）" | 抄它的 `wp-guard`/`woo-guard` 分层：通用 guard + 领域 guard 并列，共享同一骨架 |

### 4.2 可迁移的三个设计模式

**① "生成器 / 守卫者"角色分离。** 让同一个模型在两个不同的 prompt 语境下分别扮演作者和审稿人，比在一个 prompt 里要求"写得又快又好"有效得多。这个模式不限于代码——文案、SQL、配置、IaC 都能套。

**② 失败模式目录化（Failure Mode Catalog）。** 与其写"要写好代码"，不如穷举"具体会怎么写坏"。每条带 Pattern / Source / Bad / Good / Rule 五要素。**任何你要让 AI 稳定输出的领域，都值得先建一份自己的失败模式目录**——这是本仓库最值得抄走的东西。

**③ 明确区分"AI 读者"与"人类读者"的文档。** 在文档里直接写"如果你是 AI，先读这个文件"——这在 Agent 时代会越来越常见，而大部分 README 还没意识到自己的第一读者已经变成了模型。

### 4.3 局限提醒

它是**判断层**不是**验证层**。SKILL.md 自己也承认：不替代项目的 linter / formatter / type checker / test runner。机械校验用项目自己的工具，这个技能只负责"人类才做得了的判断"。所以别指望它拦住类型错误。

---

## 五、源码深度解读（克制版）

由于是纯 Markdown 仓库，"源码"即规则文本。挑两段最有信息密度的。

### 5.1 失败模式 #1：吞异常（根因归因是全文精华）

```markdown
## 1. Catch-all error handling that swallows failures

**Pattern.** Wrapping operations in broad catch-all handlers or returning
null/empty success on any caught error, hiding real bugs.

**Source.** Karpathy directly observed that LLMs are unusually afraid of
exceptions. ... Root cause is the reward signal during training —
propagating exceptions penalizes the model, so the model learns to suppress them.

**Bad:**
  getEmail(userId):
    attempt:  user = userStore.get(userId); return user.email
    catch anyError:  return null
Looks safe. In practice, a database outage is now indistinguishable
from "user has no email."

**Good:**
  getEmail(userId):
    user = userStore.get(userId)  // storage errors propagate
    return user.email             // null only means the user has no email
```

**为什么这段值得单独拎出来**：它不止说"别吞异常"，而是给出了**为什么 LLM 特别爱吞异常**的机制解释——RLHF 训练中抛异常被惩罚。这种"根因级"写法让规则从"教条"变成"可推理的约束"，模型更容易内化，也更容易在边界情况下自己判断。

**15 条失败模式全清单**（较 2026-06 版本的 14 条新增 1 条）：
① 吞异常 ② 为不可能情况加防御 ③ 过早抽象 ④ 注释污染 ⑤ 复制粘贴代替复用 ⑥ **幻觉 API / 包** ⑦ 无意图的通用命名 ⑧ 长函数一把抓 ⑨ 参数爆炸 ⑩ 与周边代码风格不一致 ⑪ 死代码 / 未用 import / 半成品 ⑫ **用 mock fallback 宣告成功** ⑬ 貌似正确实则错误 ⑭ 投机性可配置化（YAGNI）⑮ 为琐事引入新依赖。

其中 ⑥⑫⑬ 是纯 AI 独有的——传统 clean code 书里根本不会讨论"模型会编造一个不存在的库"。

### 5.2 `agents/openai.yaml`：跨运行时适配只用了 4 行

```yaml
interface:
  display_name: "Clean Code Guard"
  short_description: "Clean-code guardrails for AI agents"
  default_prompt: "Use $clean-code-guard after code is written or changed to review
                   it for clean-code and LLM-failure issues."
```

**克制的典范**：作者没有为 OpenAI 运行时复制一整套规则，只加了一个 4 行的展示层适配文件，规则体依然单一来源。这是"一套内容、多个宿主"的最低成本做法——想让自己的 Skill 同时上架 Claude Code 和 Codex 的人可以直接照抄这个模式。

---

## 六、社区口碑

- **增长曲线**：2026-06-09 上 Trending 时 467 ⭐ → 2026-08-11 达 1,154 ⭐，两个月 **2.47 倍**。在 Agent Skill 这个高度同质化的赛道里属于稳健增长（非爆冲后熄火型）。
- **Fork/Star 比 11.8%（136/1154）**：偏高，符合"配置类仓库"特征——用户倾向 fork 后按自己团队规范改，而非直接安装。可作为**实际使用深度的正向信号**（相比纯收藏型仓库的 2-3%）。
- **Issue 数仅 4 个（开放）**：纯文档仓库的自然结果，无运行时故障面。也说明社区讨论主要发生在别处（作者的推文/博客），仓库本身不是讨论中心。
- **维护节奏**：2026-06-06 创建 → 2026-07-04 最后推送。**近 5 周（截至 2026-08-11）无更新**。对纯规则库来说不算致命（规则不会腐烂），但需注意：失败模式清单理应随模型迭代而更新，长期停更会导致清单滞后于新一代模型的行为特征。
- **可信度加分项**：`references/sources.md` 作为中央参考文献库存在，规则可追溯到 Karpathy 观察、Sandi Metz 的 re-inline 规则、Fowler 的 YAGNI 成本分类、McCabe 复杂度等公开出处，**不是作者拍脑袋**。

---

## 七、竞品对比

| 项目 | 定位 | 与 guard-skills 的关系 |
|---|---|---|
| **addyosmani/agent-skills**（85,658 ⭐，本库已收录） | 生产级工程技能全家桶 | 体量碾压，覆盖面更广；但它是"让 Agent 更能干"，guard-skills 是"给 Agent 装刹车"，**互补而非替代** |
| **thananon/9arm-skills**（3,089 ⭐，本库已收录） | 个人工程师工作流合集 | 同为纪律型 Skill，但 9arm 偏**流程纪律**（调试四步法），guard-skills 偏**产物质量**。可同装 |
| **mukul975/Anthropic-Cybersecurity-Skills**（本库已收录） | 安全领域 Skill | 同属"领域守卫"思路，guard-skills 的 wp-guard/woo-guard 是同一模式在 WordPress 生态的落地 |
| **传统 linter（ESLint / Pylint / SonarQube）** | 机械规则检查 | **不重叠**。SKILL.md 明确划界：机械校验交给项目工具，本技能只做判断层。SonarQube 查不出"这个抽象是不是过早" |
| **CodeRabbit / Greptile 等 AI PR Reviewer** | SaaS 化 AI 代码审查 | 功能重叠度最高的真竞品。差异：guard-skills **零成本、零依赖、可完全自定义、在本地 Agent 内联执行**；SaaS 方案有更好的 PR 集成和历史上下文，但要钱且规则不透明 |

**竞争位置判断**：它不在"最强代码审查工具"这条赛道上竞争，而是占据了一个更窄但更清晰的生态位——**给已经在用 Coding Agent 的人，提供一个零成本、可读、可改的质量兜底层**。护城河不是技术，是那份 15 条失败模式清单的**研究出处质量**。

---

## 八、核心研判

**值得抄的（★★★★★）**
`references/ai-failure-modes.md` 这一个文件的价值 ≈ 整个仓库。它是目前公开资料里对"LLM 写代码系统性犯什么错"最结构化的整理，而且每条带出处。**即使你完全不用这个 Skill，也应该把这 15 条读一遍并内化进自己的 code review 直觉。**

**值得装的（★★★★☆）**
如果你日常用 Claude Code / Codex 写生产代码，`clean-code-guard` 值得常驻。零依赖意味着零风险——它不能执行任何东西，最坏情况只是多占点上下文。`wp-guard`/`woo-guard` 仅对 WordPress 生态有意义，其他人可以只装前三个。

**要清醒的（⚠️）**
1. **它是判断层，不是验证层**——别拿它当 linter 用，机械错误照样漏。
2. **近 5 周未更新**——失败模式清单是"随模型演进的活文档"，停更会滞后。用之前建议自己 diff 一遍，看有没有你在新模型上观察到的新病症需要补。
3. **上下文成本真实存在**——五个 guard 全装 + references 按需加载，在长会话里会挤占预算。建议按项目栈只装用得到的。
4. **1,154 ⭐ 的量级意味着它还不是"事实标准"**——同赛道有 8.5 万星的 addyosmani/agent-skills，如果你只装一套，先装那个；guard-skills 是补充位。

**一句话结论**
> 一个只有 Markdown、没有一行代码的仓库，靠一份带研究出处的"AI 代码病理学清单"站住了脚。**最大价值不是让你装上它，而是让你意识到 AI 写代码有 15 种系统性犯错方式——读完这份清单，你自己 review AI 代码的水平就上了一个台阶。**

---

## 九、关键文件路径速查

| 路径 | 为什么重要 |
|---|---|
| `skills/clean-code-guard/references/ai-failure-modes.md` | **全仓最高杠杆文件**，15 条 LLM 失败模式带出处 |
| `skills/clean-code-guard/SKILL.md` | 三模式状态机 + 三段式 description 模板 + Compatibility 零依赖声明 |
| `skills/clean-code-guard/references/sources.md` | 中央参考文献库，规则可追溯性的来源 |
| `skills/clean-code-guard/references/review-checklist.md` | review 模式的结构化走查清单 |
| `skills/*/agents/openai.yaml` | 4 行搞定跨运行时适配的最小成本模板 |
| `skills/test-guard/references/llm-app-testing.md` | 少见的"如何测试 LLM 应用"专题 |
| `skills/wp-guard/` `skills/woo-guard/` | 领域专用 guard 的分层范例（通用 + 领域并列） |

---

*调研方法：GitHub API 实时元数据 + `git/trees` 全量文件树 + raw.githubusercontent 源文件直读；星标/Fork/Issue 数为 2026-08-11 实时值。*
