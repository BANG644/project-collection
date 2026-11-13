# 🔬 google/elephant-goldfish-model — 全方位深度调研

> 调研日期：2026-11-14 ｜ Stars：18,526 ｜ 语言：Python 68.7% / Astro 15.1% / JS 11.9% ｜ 许可：Apache-2.0 ｜ 编号：#589

## 📌 一句话定位
Google 开源的**设计与评审插件**：「大象（Elephant）」带着完整项目上下文起草规格，「金鱼（Goldfish）」用**零上下文的子 Agent** 从外部视角死磕草稿，人在批准前不写一行代码——专治「Agent 自己写方案、自己审方案、自己觉得牛」的上下文坍塌。

## ⭐ 项目亮点
- **上下文隔离是当前最便宜的质量控制**：起草者和评审者刻意拆成两套记忆，金鱼只看到文档与其引用的源码，看不到此前的对话，因此能抓出起草者「默认成立」却从未写下的假设。
- **五阶段强制评审流水线**：Zoom Out → Comprehension → Design Critique → 中间 Zoom Out → Implementation Readiness，且要求「先批评、再说好」。
- **反谄媚硬约束**：SKILL.md 直接 bans「great/brilliant/smart」等奉承词与道歉语，强制「Earn Your Agreement」，把挑剔写进协议而非靠模型自觉。
- **多 harness 一等公民**：Claude Code / Codex / Antigravity / ChatGPT Work 均原生支持，且若 harness 无法开干净子 Agent 就**直接停审**而非假装。
- **工件优先交付**：所有提案/评审必须落盘成文件再让人审，不在聊天框里甩大段文字。

## 🏗️ 项目架构全景
不是传统「代码库」，而是**一组 Agent Skill + 评审人 persona + 文档标准**的组合。核心角色分三层：
- **Elephant**：长会话，持有项目上下文与历史决策，产出 `concepts_brief.md` → `design_draft.md`。
- **Goldfish**：无历史的子 Agent（fresh-context subagent），按 `agents/<file>.md` 的 persona 读同一份文档挑刺。
- **You**：拍板取舍、批准规格。

7 个 skill：`egm-brainstorm`（方向共识）、`egm-draft`（分节起草）、`egm-review`（五阶段评审）、`egm-resolve`（处理评审意见）、`egm-bootstrap`（给存量代码库补文档）、`egm-review-loop`（自定义评审组）、`egm-drift-report`（文档 vs 当前代码漂移）。技术栈：Python 主体 + Astro 文档站（egm.dev）。

## 💡 应用场景与启发
- **典型场景**：特性需要设计决策时（如「给项目加 webhook 投递，失败重投/重复事件怎么办」），先 `/egm-brainstorm` 共识、再 `/egm-draft` 分节起草、最后 `/egm-review` 让金鱼审。
- **可借鉴模式**：「**把评审者从作者记忆里剥离**」是通用方法论——任何需要自审质量的环节（写 RFC、出技术方案、出 PR 计划），都可以复制「作者写 + 无上下文 reviewer 审」的双角色结构。
- **同类需求思路**：自研 Agent 时，与其堆叠更强模型，不如加一道「从没听过你说过什么的模型」做最后一道关。这是成本最低的质量杠杆。
- **已验证用法**：对**存量设计文档 / README / PR 计划**直接跑 `/egm:egm-review`，60 秒就能拿到新鲜视角评审，无需新写规格。

## 🧠 核心源码解读（克制代码量）
`skills/egm-review/SKILL.md` 是整个项目的灵魂，定义了五阶段与 11 条执行约束。最关键的「强制挑剔」写成硬规则而非建议：

```
## Execution Constraints (CRITICAL)
1. Artifact-First Delivery (MANDATORY): 严禁在聊天框直接甩大段提案/草稿，
   必须写入工作目录文件后告知路径并请求评审。
4. No Glazing: 禁止称想法 "great/brilliant/smart"，无实质的恭维即噪音。
5. Critique First: 即便想法很强，也先讲错在哪、缺什么、风险在哪。
8. Earn Your Agreement: 只有想法经严苛客观审视后才可认同。
```

五阶段在 SKILL.md frontmatter 写死：`Initial Zoom Out → Comprehension → Design Critique → Intermediate Zoom Out → Implementation Readiness`。Comprehension 阶段用「子 Agent 复述」检测歧义；Design Critique 分 design / structural / style 三类 reviewer；Implementation Readiness 校验文件路径、数据结构、签名。

`egm-draft` 的差异化在「**每写完一节就暂停等你反馈**」，而不是一次性吐完整篇——把人锁进 Loop 里。`egm-review` 要求 Goldfish「在独立上下文运行，无会话历史」，并明确：harness 不能嵌套子 Agent 就停审（「a review in the same context is not a Goldfish review」）。

## 📐 架构决策与设计哲学
- **不做「AI 写代码」的事**：EGM 明确「You make the trade-offs and approve」，且 README 自承「不替代测试或人的判断」。
- **插件而非平台**：装进用户已有 harness，不新造 IDE；通过 plugin marketplace 分发。
- **文档标准即契约**：`docs/designs/` 下的标准 + 各 reviewer persona，使评审可复现。
- **边界**：官方声明「not an officially supported Google product」，过度用于小而明确的 bug fix 是 overkill（README 自己说）。

## 🌐 全网口碑画像
- **好评共识**：Marktechpost / TheNextGenTechInsider 一致认为它精准命中「agentic coding 的上下文坍塌 / AI slop」痛点；AI Frontier Post 实测 Codex CLI 0.164.0-alpha.9 安装干净、7 个 skill 齐全、离线单测通过。
- **增长信号**：aifrontierpost 称 11 月 11 日前 5 天涨 4,738 ⭐（AI 仓库第 8 快），约 17,558 ⭐ / 1,314 fork；agentindex 测得 90 天 100+ commits、2 次 release（v0.1.1）。中文圈 Clauday 标题直给「大象写方案，金鱼来挑刺」，点出「上下文隔离是最便宜的质量控制」。
- **差评 / 风险共识**：① token 消耗高（Marktechpost 直言 high token consumption）；② 依赖能开 fresh subagent 的 harness，否则直接停审；③ 某些 host 存在 instruction leakage 风险提示；④ 非官方支持产品，长期维护承诺弱。
- **社区治理**：issue 偏工程化（#436 让实现对照已批准设计、#433 给每条评审发现打证据标签、#414 Web 兼容 Chat skill），讨论区开放，节奏健康。

## ⚔️ 竞品对比
| 维度 | EGM | MS Spec Kit | Amazon Kiro | 传统 PR 评审 |
|------|-----|------------|------------|------------|
| 评审上下文 | 零上下文子 Agent 隔离 | 单上下文 | 单上下文 + 自动 spec | 人审 |
| 角色拆分 | Elephant/Goldfish 双角色 | 弱 | 弱 | 无 |
| 反谄媚约束 | 写进 SKILL.md | 无 | 无 | 视人 |
| 接入成本 | 装插件即可 | 中 | 中 | — |
| 护城河 | 上下文隔离方法论 | 微软生态 | AWS 生态 | — |

**选择建议**：要「逼自己先想清楚再写」且已在用 Claude Code/Codex，选 EGM；已在 Azure/AWS 重度绑定可选 Spec Kit/Kiro。

## 🎯 核心研判
- **优势**：用「结构而非意志力」解决自审失效；多 harness 支持 + Apache-2.0 让它极易落地；反谄媚硬约束是稀缺设计。
- **风险**：token 成本高、对 harness 能力有硬门槛、非官方产品维护存疑、小修小补用它是杀鸡用牛刀。
- **适用**：中大型特性设计、跨团队 RFC、PR 计划预检。**不适用**：一行 bug fix、无子 Agent 能力的轻量 harness。
- **趋势**：上升期。上下文隔离正从「炫技」变「默认质量控制」，且 Google 把 Anthropic/OpenAI 的 Agent 当一等公民支持，信号明确。

## 📂 关键文件路径速查
- `skills/egm-review/SKILL.md` — 五阶段评审 + 11 条反谄媚硬约束（核心）
- `skills/egm-draft/SKILL.md` — 分节暂停式起草
- `skills/egm-brainstorm/SKILL.md` → `concepts_brief.md`
- `docs/designs/architecture.md` — skill 与 reviewer 如何拼装
- `TESTING.md` — 校验、执行记录与验证边界
- 灵感出处：Dave Rensin 原文 https://medium.com/@drensin/elephants-goldfish-and-the-new-golden-age-of-software-engineering-c33641a48874
