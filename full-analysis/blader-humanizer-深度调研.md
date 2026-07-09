# 🪄 blader/humanizer — 去除 AI 写作痕迹的跨 Agent 技能

> **仓库**: [blader/humanizer](https://github.com/blader/humanizer)
> **Stars**: 28,427 | **Forks**: 2,624 | **语言**: Markdown（纯 skill，无代码）| **License**: MIT
> **创建**: 2026-01-18 | **最后推送**: 2026-06-29 | **版本**: SKILL.md v2.8.2 | **贡献者**: 9
> **调研日期**: 2026-07-10 | **数据来源**: GitHub API + SKILL.md 源码逐行解读

---

## 一、项目定位

`humanizer` 是一个**纯 Markdown 的 Agent 技能（skill）**，作用是把文本里"AI 生成感"的痕迹抹掉，让文字读起来更像人写的。它不依赖任何运行时代码——整个仓库就是一份 `SKILL.md`（加上插件元数据），因此能在任何支持 skill 式指令的 Agent harness（Claude Code、Codex、Cursor、OpenClaw 等）里直接跑。

它的方法论不是作者拍脑袋，而是**直接基于 Wikipedia 的「Signs of AI writing」指南**（由 WikiProject AI Cleanup 维护，来自对上千条 Wikipedia AI 文本的观测）。Skills CLI 一行 `npx skills add blader/humanizer` 即可跨 harness 安装。

---

## 二、项目亮点

1. **权威的方法论底座** — 33 类可检测模式，全部映射到 Wikipedia 的实证清单，而非"感觉像 AI"的玄学判断。从"过度强调意义/legacy"到" aphorism 公式（X is the Y of Z）"都给了 Before/After 对照。
2. **跨 Agent 原生兼容** — frontmatter 里 `compatibility: any-agent`，运行时产物就是 `SKILL.md` 本身。同一份文件即可通过 Claude Code 插件、`npx skills`、Git clone 三种方式装入不同 harness。
3. **双循环 + 声纹校准** — 不是"润色一遍完事"，而是 `draft → audit → final`：先改，再自问"这段话哪里还明显是 AI 写的"，再定稿。可选 **Voice Calibration**：喂一段你自己的旧文，它先解析你的句长/用词/标点习惯，再把 AI 模式替换成"你的"模式。
4. **硬约束 + 误报防护** — em dash（—）被定为**硬性零容忍约束**（不只是"少用"）；同时单列一整节「What NOT to flag」，明确"完美语法≠AI""单个 em dash 不算数""混合语域是真人信号"，防止把好好的人话改坏。
5. **规模信号极强** — 约 6 个月冲到 28K⭐ / 2.6K forks，是同类"AI 去痕"技能里星标最高的之一；已有社区中文翻译版（见下「竞品对比」）。

---

## 三、核心架构

整份技能是一个**结构化的提示词工程文档**，没有代码执行层。骨架如下：

```
humanizer/
├── SKILL.md              # 核心：技能指令全文（v2.8.2）
├── README.md             # 安装与多 harness 入口说明
├── LICENSE               # MIT
├── AGENTS.md             # Agent 上下文
└── .claude-plugin/       # Claude Code 插件元数据（marketplace.json / plugin.json）
```

`SKILL.md` 内部由这些区块构成：

| 区块 | 作用 |
|------|------|
| **frontmatter** | `name/version/description/license/compatibility/allowed-tools` —— 声明技能元数据与可用工具（Read/Write/Edit/Grep/Glob/AskUserQuestion） |
| **Your Task** | 三原则：识别模式 → **改写而非删除** → 保留原意 → 匹配声纹 |
| **Voice Calibration（可选）** | 解析用户样本的句子长度/用词/标点习惯，按样本而非默认风格重写 |
| **PERSONALITY AND SOUL** | 反向约束：只去 AI 痕迹不够， sterile 无灵魂的文字同样"显假"；给出"怎么加人味"（有观点、节奏变化、放点乱） |
| **CONTENT / STYLE / COMMUNICATION / FILLER 模式（共 33 条）** | 每条含"信号词 + 问题 + Before/After"，分内容、风格、沟通、填充四类 |
| **DETECTION GUIDANCE** | 误报清单 + "什么是人写信号"（具体细节、矛盾情绪、年代梗、自我纠正…） |
| **Process and Output** | 固定产出格式：draft + 「still-AI」要点 + final + 变更摘要 |
| **Full Example** | 一整篇 Lisbon 游记的 AI 版→草稿→定稿对照，演示所有原则落地 |

---

## 四、应用场景与启发

**适用场景**
- 把 Agent 生成的邮件、文档、博客、报告"解码"成不像机器写的版本
- 作为写作 Agent 的**后置过滤器**，嵌进任何内容生产流水线
- 个人写作训练：用它当"AI 痕迹镜子"，反向学习什么是 AI 腔

**给同类需求的解决思路（启发）**
- **把"检测规则"沉淀成可审计的清单，而不是黑箱模型** —— 33 条模式每条都带 Before/After，任何人都能对照校验，远比一个"AI 检测器"打分可信。下次要做"风格约束"类技能，先写模式库 + 反例。
- **"重写而非删除" + "保留段落数"** 是一条极实用的指令工程技巧：约束输出结构（5 段进 5 段出），避免 Agent 偷偷把内容砍短。
- **硬约束要用"扫描校验"兜底** —— 它要求定稿前扫一遍 `—` 和 `–`，任何命中都算没改完。这种"生成后自检"模式可复用到任何有禁止词的场景。
- **声纹校准 = 用样本做 few-shot 风格锚定**，比在 prompt 里写"写得自然点"有效得多。

---

## 五、源码深度解读（SKILL.md 即源码）

### 1. frontmatter 的工具边界

```yaml
name: humanizer
version: 2.8.2
description: |
  Remove signs of AI-generated writing from text...
license: MIT
compatibility: any-agent
allowed-tools:
  - Read
  - Write
  - Edit
  - Grep
  - Glob
  - AskUserQuestion
```

`allowed-tools` 只放行读写/搜索/提问，**不放 Bash** —— 刻意把 humanizer 限制成"纯文本编辑"角色，防止它被诱导去执行命令。这是 skill 安全设计的范本。

### 2. 模式组织方式（节选）

```markdown
### 14. Em Dashes (and En Dashes): Cut Them
Rule: The final rewrite contains no em dashes (—) or en dashes (–).
      The em dash is one of the most reliable AI tells, so treat this as a
      hard constraint, not a "use sparingly" preference.
Before: The term is primarily promoted by Dutch institutions—not by the people themselves.
After:  The term is primarily promoted by Dutch institutions, not by the people themselves.
```

每条模式统一为「信号词 → 问题 → Before → After」四段式，可被 Agent 逐条比对。33 条覆盖内容（意义膨胀、虚假排比）、风格（标题大写、emoji、弯引号）、沟通（协同套话、知识截止免责）、填充（ filler、过度 hedging）四大类。

### 3. 处理循环（Process and Output）

固定三步产出：**draft 改写 → 自问"What makes the below so obviously AI generated?"并列出残留 tell → final 定稿（无 em/en dash）→ 变更摘要**。把"自我审查"显式写进流程，是这个技能质量稳定的关键。

---

## 六、全网口碑

仓库本身即"口碑"：约 6 个月 28.4K⭐ / 2.6K forks，9 名贡献者，MIT，被 `npx skills` 跨 Agent 技能市场收录，说明它已是该赛道的**事实上标准实现**之一。

- **生态扩散**：存在社区中文翻译版 `op7418/Humanizer-zh`（本仓库已单独调研入库），反向证明原版影响力外溢。
- **采用信号**：README 给出 Claude Code 插件、`npx skills add --agent '*'`、Git clone 三种安装路径，跨 harness 分发成熟度高于多数个人 skill。
- **局限**：作为"提示词技能"，其效果高度依赖底层模型遵循指令的能力；em dash 硬约束在部分模型上可能被执行得过于机械。社区讨论分散在各大 Agent 论坛/HN，无集中评测数据（**具体第三方评测数据不可用**）。

---

## 七、竞品对比 + 核心研判

| 维度 | **blader/humanizer** | 通用「AI 检测器」(GPTZero 等) | 其他 humanize 提示词 |
|------|----------------------|-------------------------------|----------------------|
| 形态 | 可执行的 Agent skill（改写） | SaaS 打分工具（只检测） | 单条 prompt |
| 方法论 | Wikipedia 实证 33 模式 | 黑箱 perplexity/burstiness | 作者经验 |
| 跨 harness | ✅ any-agent | ❌ 需粘贴文本 | ⚠️ 多半绑定单一工具 |
| 声纹校准 | ✅ 样本驱动 | ❌ | 极少 |
| 误报防护 | ✅ 整节「NOT to flag」 | ❌ 常误伤人话 | ❌ |
| 开源/本地 | ✅ MIT 纯本地 | ❌ 云端付费 | ✅ 但质量参差 |

**核心研判**
- **优势**：方法论权威且可审计、跨 harness 零摩擦、工程化程度（版本号、硬约束自检、声纹校准）在"提示词技能"里罕见地高；星标规模已建立网络效应。
- **风险**：纯提示词方案，质量天花板由宿主模型决定；"去 AI 感"在学术/出版场景可能涉及诚信边界，使用者需自担场景合规责任。
- **趋势**：随着 AI 写作泛滥，"去痕/风格约束"会从零散 prompt 收敛成少数标准化 skill。humanizer 凭借先发星标 + 跨市场分发，大概率守住头部位置。

**一句话结论**：如果你想让 Agent 产出的文字"不像机器写的"，这是当前最值得直接 `npx skills add` 的那个；它真正的价值不在"魔法"，而在把一条经验规则变成了**可审计、可校准、可自检**的工程资产。

---

## 八、关键文件路径速查

| 路径 | 说明 |
|------|------|
| `SKILL.md` | 技能全文（v2.8.2），33 模式 + 处理循环，即"源码" |
| `README.md` | 多 harness 安装入口（Claude Code 插件 / npx skills / Git clone） |
| `AGENTS.md` | Agent 上下文 |
| `.claude-plugin/marketplace.json` | Claude Code 插件市场元数据 |
| `LICENSE` | MIT |
