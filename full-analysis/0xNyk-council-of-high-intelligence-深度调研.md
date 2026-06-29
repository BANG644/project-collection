# 🔬 0xNyk/council-of-high-intelligence — 全方位深度调研

## 📌 一句话定位

**18 个 AI 历史名人群组辩论系统** — 在编码 Agent 中通过 `/council` 命令召集亚里士多德、费曼、卡尼曼等 18 位"历史人物"进行多轮结构化辩论，支持跨模型提供商自动路由（Claude/OpenAI/Gemini/Ollama/NVIDIA/Cursor），以真模型多样性防止单一推理路径的"看似自信的错误"。

## ⭐ 项目亮点

1. **不是提示词角色扮演，是真模型多样性** — 辩论成员不光角色不同，其底层模型也通过 provider auto-routing 跨 Claude/OpenAI/Gemini/Ollama/NVIDIA/Cursor 等多提供商路由，极性对（Polarity Pairs）强制安排到不同模型，杜绝"同一模型的换装表演"
2. **7 步充分仪式化的辩论协议** — 问题重述门→盲审独立分析→实名交叉质询→强制异议/新颖性/反从众审查→终结结晶→加权投票→主席合成裁决，每一步都内置 anti-groupthink 机制
3. **加权投票避开了伪共识** — 不是简单的多数决：领域席位权重 1.5×，2/3 超级多数门槛，"悬而未决"可以报告为"分歧"，不强制捏造共识。投票前每个成员输出结构化 `STANCE:` 行
4. **三方生态覆盖** — 同时支持 Claude Code（SKILL.md）、Codex（SKILL.codex.md）和 Gemini CLI（SKILL.gemini.md），`install.sh --codex` 或 `install.sh --gemini` 一键安装
5. **20+ 预定义 Triad 领域面板** — architecture/strategy/debugging/risk/shipping/ai-safety/systems 等，每个 triad 的 3 位成员是其知识传统的最佳碰撞组合

## 🏗️ 项目架构全景

### 文件结构

```
council-of-high-intelligence/
├── SKILL.md              # Claude Code 协调器协议（核心）
├── SKILL.codex.md        # Codex 版协调器协议
├── SKILL.gemini.md       # Gemini CLI 版协调器协议
├── CLAUDE.md             # 开发者指南（不是配置文件，是README的元指南）
├── install.sh            # 安装脚本（78KB，覆盖三平台）
├── agents/
│   └── council-*.md ×18  # 每位成员的 agent 定义（YAML frontmatter + 身份提示词）
├── configs/
│   ├── auto-route-defaults.yaml
│   ├── provider-model-slots.example.yaml
│   └── provider-model-slots.cursor.example.yaml
├── demos/
│   ├── session-pack.md
│   └── verdict-template.md
└── scripts/
    └── detect-providers.sh   # 自动检测本地安装的LLM提供商
```

### 设计哲学

这里的架构决策跟普通项目很不一样——**它不是让开发者读的，是让 LLM Agent 读的**。CLAUDE.md 的这段说明揭示了核心设计：

> "Keep agent prompts tight — no filler sentences. Grounding protocols use specific constraints ('maximum 2 analogies', '3-level depth limit'), not vague guidance."

项目的"代码"由 18 份 agent 定义文件（`agents/council-*.md`）和一份 SKILL.md 执行协议组成。关键结构：

| 组件 | 文件数 | 角色 |
|------|--------|------|
| **协调器协议** | 3（SKILL.md / SKILL.codex.md / SKILL.gemini.md）| 辩论编排、流程控制、裁决合成 |
| **成员定义** | 18 | 每人的身份提示词、分析方法、输出格式、provider_affinity |
| **安装脚本** | 1（78KB shell）| 三平台跨运行时安装 |

### 支持的 Provider 自动检测

```
detect-providers.sh:
├── Claude Code        → native subagent（始终可用）
├── Codex (OpenAI)     → codex exec
├── Gemini CLI         → gemini -p
├── Ollama (local)     → ollama run
├── NVIDIA NIM         → openai_compatible_api（130+ 开源模型）
├── Cursor CLI         → cursor-agent -p（聚合 GPT/Claude/Gemini/Grok）
```

### Provider 路由约束（硬约束）

```
1. 极性对成员必须在不同 provider 上（硬约束）
2. 成员均匀分布到可用 provider
3. 成员 frontmatter 的 provider_affinity 做二级偏好
4. 任一 provider 失败 → 自动回退到 Claude
```

## 💡 应用场景与启发

### 典型使用场景

- **重大架构决策**：用 `/council --triad architecture` 对 monorepo vs polyrepo、微服务 vs 单体等做多维度评估
- **战略选择**：定价策略、开源决策、市场进入时机——`/council --triad strategy` 集成了孙武+马基雅维利+奥勒留
- **AI 安全审计**：`/council --triad ai-safety`（Sutskever+Aurelius+Socrates）对 AI 产品做安全悖论推演
- **产品设计评审**：`/council --triad design`（Rams+Torvalds+Watts）从用户体验、可维护性和问题重构三角度审视
- **创投尽调**：`/council --triad founder` 或 `economics` 用芒格的多模型推理+塔勒布的尾部风险审视

### 可借鉴的解决方案模式

1. **匿名化交叉审查（Anti-conformity）** — Round 2 的匿名化设计来自学术研究（Choi et al., arXiv:2510.07517; Free-MAD, arXiv:2509.11035），强制成员凭论据质量而非来源做判断。这对任何多 Agent 协作系统的防从众设计都是教科书级参考。
2. **协商式投票（Deliberative Vote）** — 不是每人一票的直选，而是领域专家 1.5 倍权 + 2/3 超级多数门槛 + 结构化 `STANCE:` 硬格式。避免"情绪共识"的伪装。
3. **与问题对话（Problem Restate Gate）** — 每个成员必须在分析前用自己的知识框架重构问题。3 个成员得出 3 种不同的重构 → 说明原始问题本身有歧义。

### 同类需求的可参考思路

如果你也想在自己的 Agent 中实现"多 Agent 辩论"：

- 不要只做角色提示词的变化——确实要路由到不同模型提供商，否则就是"同一个演员换角色"
- 明确设计"反一致"机制：异议配额（dissent quota）、新颖性门（novelty gate）、反事实提示（counterfactual prompt）
- 结构化投票 > 自然语言总结：`STANCE:` 行让统计可审计，避免"我看到大家好像都同意"的模糊性
- 让协调器不做判断——设一个独立"主席"角色做裁决合成，隔离流程控制与内容判断

## 🧠 核心源码解读（克制代码量）

这是一个特殊的仓库——它的"源码"主要是 Markdown 提示词文件。以下是最具借鉴价值的 3 个模块：

### 模块 1：SKILL.md — 协调器 7 步协议（核心）

SKILL.md 是一份 ~20KB 的"可执行提示词"，定义了协调器从接收到 `/council` 到输出裁决的全程。关键不是内容量，而是**执行序列设计**：

```markdown
# SKILL.md 核心骨架（高度提炼）

## STEP 0: 选择 Panel
1. `--triad` → 20 个预定义域
2. `--profile` → 3 个预设面板（classic/exploration-orthogonal/execution-lean）
3. `--members` → 手动指定 2-11 人
4. 默认 → 通过问题内容自动匹配最佳 triad

## STEP 1: Provider 检测与路由（~50 行逻辑）
- 运行 detect-providers.sh → 获取可用 provider JSON
- 将极性对成员分配到不同 provider
- 选主席（最高 tier 非 panel 成员）

## STEP 2-4: 三轮辩论（核心创新）
Round 1: 盲审独立分析（并行，400 words max）
Round 2: 实名交叉质询 + 匿名化（并行，300 words，必须挑战 2+ 人）
→ Post-Round 强制审查：异议配额、新颖性门、超 70% 一致触发反事实提示
Round 3: 终结结晶（并行，100 words + STANCE: 行）
```

**为什么 Round 2 要匿名化？** 防止"身份权威偏差"——如果知道某个意见来自"卡尼曼"（系统 1/2 偏见权威），其他人可能不敢反驳。而如果所有成员都凭论据质量评价，更能暴露真正的分歧。

### 模块 2：输出格式设计（裁决模板）

裁决输出模板是这份 SKILL.md 的另一个设计亮点。看看它要求主席输出什么：

```
## Council Verdict（模板必填字段详解）

### Acceptable Compromises
{这个裁决放弃了什么。如果"什么都没放弃"——说明为什么。}

### Kill Criteria
{可验证的证伪条件：如果 X 在 日期 前发生，裁决无效，应 Y。}

### Concrete Next Step
{唯一一个行动。<动词> <对象> by <日期>。不允许"考虑""探索"。}

### Unresolved Questions
{议会无法回答的问题。引导语是什么议会不知道的。}

### Vote Tally（结构化可审计）
monorepo — 2.5 (Ada [1.5×, domain], Feynman) ✅ cleared 2.333 threshold
polyrepo — 1.0 (Torvalds)
W_total 3.5 · threshold 2.333 · monorepo carries
```

**关键洞察**：裁决模板的设计强制了"知道我们不知道什么"——Kill Criteria 和 Unresolved Questions 放在 Concrete Next Step 之前，且 Minority Report 即使被多数否决也必须显示。这是决策科学中的"事前验尸"（premortem）原则在结构化 prompt 中的实现。

### 模块 3：成员定义格式（agents/council-*.md）

每个成员文件遵循严格的章节顺序，前端有 YAML 元信息：

```yaml
# agents/council-feynman.md（简化）
---
name: council-feynman
model: sonnet
provider_affinity: openai
polarity_pair: socrates
domain: first-principles
---

# Identity → Grounding Protocol → Analytical Method → ...
```

LLM 在进入任务前先读 CLAUDE.md，确保知道安装和测试流程后再工作。这种 "meta-prompt → skill → agents" 的三层结构本身就是一种行业最佳实践。

## 📐 架构决策与设计哲学

### 核心设计红线

1. **不分拆到独立 repo** — 所有 18 个 agent 文件放在同一个 repo 下，不单独维护。CLAUDE.md 说明了意图："每个人都应该独立可读，但一起发布"
2. **LLM 不宜做最终裁决** — 主席角色是独立合成者，不是参与者。且主席本身可以是一个不同的模型（`--chairman gemini`）
3. **"多于 5 个成员时并行 + Batch B"** — 7+ 成员时拆分两个批次保证审查质量。说明作者意识到并行通信的"带宽问题"

### Out-of-Scope（从 Issue 推断）

- Issue #34 提议支持模块化 Python Agent 框架（Agno/LangGraph）——这是仓库**不做**的。它定位是纯提示词项目，不走代码集成路线
- 没有 benchmark 数据。作者在 README 中引用了学术论文（Choi et al.）但没有自己出具体数字

## 🌐 全网口碑画像

### 好评共识

| 来源 | 评价 |
|------|------|
| OpenAgentSkill 平台 | "These scores combine public repository metadata, OpenAgentSkill review signals" — 平台活跃评分良好 |
| 技术博客评测 | 被多个 Agent Skills 目录收录（agentskillshub.top、clawhub.md），作为多 Agent 辩论的标杆参考 |
| GitHub 社区 | 1,823 Star / 196 Fork，Issue 仅 3 个 open，说明项目成熟度高 |

### 差评共识 & 争议焦点

- **无定量 benchmark** — README 引用了学术论文但没有自己的实验数据。用户最需要的问题是"辩论模式比单模型到底好多少？"目前只能从学术文献找答案
- **代码量近乎零** — 全部是提示词。某些使用者可能期望看到可编译的代码库
- **安装依赖多** — Claire Code + Codex + Gemini + Ollama + Cursor + NVIDIA，全套配置对非专业用户有门控

### 学术背景（关键）

来自 arXiv 2601.08835（DeliberationBench: When Do More Voices Hurt?）的研究发现，**并非所有多 Agent 辩论都能提升质量**——简单的 response-selection 方法在实验中实际优于复杂辩论协议。这给 CoHI 带来了一个需要正视的挑战：它的 7 步协议是否真的比"直接问 3 个不同模型然后选最好的"更优？

## ⚔️ 竞品对比

| 维度 | Council of High Intelligence | ChatDev (OpenBMB) | AutoGen (Microsoft) |
|------|---------------------------|-------------------|-------------------|
| **核心定位** | 决策辩论（历史人物群组） | 软件开发 | 通用多 Agent 对话 |
| **安装方式** | `install.sh`（提示词搬运） | pip install | pip install |
| **模型多样性** | ✅ 跨 6+ provider 自动路由 | ❌ 单一模型 | ✅ 支持多模型 |
| **辩论协议** | 7 步严密仪式（含匿名化+投票） | 角色分工流水线 | 自由对话模式 |
| **应用场景** | 决策支持/战略咨询 | 代码生成 | 通用任务编排 |
| **可审计性** | ✅ `STANCE:` 行 + 加权投票表 | ❌ | ❌ |
| **学术支撑** | 引用了多项研究 | 有论文 | 有论文+benchmark |

**选择建议**：要决策质量（特别是高风险的架构/战略/安全决策）→ CoHI。要代码生成 → ChatDev。要通用任务编排 → AutoGen。

## 🎯 核心研判

### 项目优势
- **决策质量设计最精致**— 目前开源社区最系统的"防群体思维"辩论协议
- **真模型多样性** — 跨 6+ provider 路由是硬约束，不是选项
- **裁决可审计** — 每一场辩论都留下结构化投票记录，可比对、可复盘

### 项目风险
- **无自有 benchmark** — 无法量化"好多少"。作为"决策辅助工具"，缺乏性能数据的支撑
- **纯提示词项目** — 受益于 LLM 进步的同时也完全依赖 LLM 质量（模型变笨了 → 辩论也变差了）
- **易用性门控** — 需要分别安装 Claude Code、Codex、Gemini CLI 等多个运行时

### 趋势判断
- **上升期**。多 Agent 协作是 2026 年 AI 最热的方向之一，CoHI 在"高质量决策辩论"细分领域的定位几乎没有竞品
- 但如果 DeliberationBench 的结论（简单方法优于复杂协议）被广泛验证，CoHI 可能需要简化协议或增加 benchmark 自证

## 📂 关键文件路径速查

| 文件 | 说明 |
|------|------|
| `SKILL.md` | 核心协调器协议（执行序列 + 裁决模板）|
| `SKILL.codex.md` | Codex 版协调器协议 |
| `SKILL.gemini.md` | Gemini CLI 版协调器协议 |
| `CLAUDE.md` | 开发者指南（架构+约定+测试）|
| `install.sh` | 多平台安装入口 |
| `agents/council-feynman.md` | 成员定义模板（18 份类似）|
| `configs/provider-model-slots.example.yaml` | 手动路由配置模板 |
| `scripts/detect-providers.sh` | Provider 自动检测脚本 |
| `demos/session-pack.md` | 完整使用示例 |
