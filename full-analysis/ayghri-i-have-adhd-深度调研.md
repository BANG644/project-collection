# ayghri/i-have-adhd — 深度调研

> 调研日期：2026-10-08 ｜ 来源：GitHub Trending（当日新增，未入库）
> ⚠️ star 数 55k 短期激增，疑似 viral，引用时建议打折看待。

## 1. 项目定位（一句话）
i-have-adhd 是一个**给编程 Agent 安装的"输出纪律"技能/插件**——用 10 条规则强制 LLM "先给动作、别铺垫、不埋答案"，把啰嗦的"Great question! Let me think…"变成可直接执行的步骤清单。

## 2. 项目亮点（差异化，开篇呈现）
- **反直觉痛点精准**：直击 Agent 输出"铺垫长、答案埋、无下一步"的普遍病灶，用 ADHD 隐喻（行动优先、可见胜利、具体时间）反推 LLM 应怎样回复。
- **10 条可机械执行的规则**：lead with next action / number steps / end with one concrete next step / suppress tangents / restate state / specific time estimates / make wins visible / matter-of-fact errors / cap lists to 5 / no preamble-recap-closers。
- **多 harness 原生分发**：同时带 `.claude-plugin/`、`.codex-plugin/`、`.cursor/`、`.opencode/`、`.agents/`、`gemini-extension.json`、`kimi.plugin.json`、`qwen-extension.json`、`plugin.json`——一份 SKILL 覆盖几乎所有主流 agent。
- **零依赖、可 fork 调参**：核心就是 `skills/i-have-adhd/SKILL.md` 一份 Markdown，用户 fork 改规则即可。
- **多语种 README**（zh-CN/es/pt-BR/ja/vi/ko/fa/th/ar），传播力极强。

## 3. 核心架构
本质是**单文件技能 + 多平台适配清单**，无运行时：
```
i-have-adhd/
 ├─ skills/i-have-adhd/SKILL.md   ← 唯一真源（10 规则全文）
 ├─ .claude-plugin/  .codex-plugin/  .cursor/  .opencode/  .agents/   ← harness 接入
 ├─ plugin.json  gemini-extension.json  kimi.plugin.json  qwen-extension.json
 ├─ hooks/  extensions/  evals/  tests/  scripts/
 └─ AGENTS.md  GEMINI.md  INSTALL.md  CONTRIBUTING.md
```
"Before/After"对照即核心卖点：Before 是 4 行铺垫+模糊建议；After 是 `Edit src/auth.ts:42` + 编号步骤 + `npm test -- auth.spec.ts` + "下一步"。

## 4. 应用场景与启发
- **给同类需求的解法**：任何"想约束 Agent 输出格式"的场景，最轻量做法是**一份 SKILL.md + 多 harness 适配文件**，而非写代码。可复用到日报/工单/代码评审等一切"要动作不要散文"的生成。
- 与本项目高度同源：用户自己的专家系统/技能体系正是这种"用 SKILL.md 编码行为纪律"的范式；i-have-adhd 证明"输出风格治理"是独立可分发的能力层。
- 团队落地：把它作为 agent 默认插件，能显著降低"读 Agent 回复的时间成本"。

## 5. 源码深度解读
**① 唯一真源 SKILL.md（skills/i-have-adhd/SKILL.md）**
全仓库 10 条规则都在此。设计要点是**每条都是可机检的动作指令**而非原则，例如"Cap lists to 5 items""Specific time estimates (minutes, not 'a bit')"——便于 agent 在生成时直接对齐，也便于用户 fork 增删。

**② 多 harness 适配（plugin.json 族）**
`plugin.json` + `gemini-extension.json` + `kimi.plugin.json` + `qwen-extension.json` 是同一份技能对不同平台的"安装描述符"。`hooks/` 与 `extensions/` 提供可选的预置钩子。`evals/` 目录说明作者用评测驱动规则迭代——这比纯经验式调参更可信。

**③ 安装即分发（INSTALL.md + 各 plugin 目录）**
README 给的切换命令 `claude plugin uninstall/marketplace remove/add/install` 表明它走各平台原生 plugin 市场，零侵入。用户换自己 fork 只需改 marketplace 源。

## 6. 社区口碑
- 病毒式传播（55k⭐、3.1k forks、73 open issues），Kacper Rutkiewicz「AI Made Simple」已做拆解视频；评论普遍"终于有人治 Agent 的废话"。
- 理念来源透明标注：改编自 Ramsay & Rostain《The Adult ADHD Tool Kit》，"adapted for how an LLM should respond, not how a human should organize"——避免被误读为医疗建议。
- 争议：对"需要解释性上下文"的任务（复杂架构讨论）可能过于简略；属风格偏好，非缺陷。

## 7. 竞品对比 + 核心研判
| 维度 | i-have-adhd | general "be concise" prompt | agent-specific style skill |
|------|-------------|------------------------------|----------------------------|
| 规则可机检 | ✅ 10 条动作级 | ❌ 模糊 | 部分 |
| 多 harness 覆盖 | ✅ 9+ 平台 | ❌ | 少数 |
| 可 fork 调参 | ✅ 单文件 | ❌ | 视实现 |
| 有 evals 驱动 | ✅ | ❌ | 少见 |

**研判**：它是"agent 输出治理"这一细分需求的最小可行产品，胜在**轻、准、可分发**。真正的价值不在代码（几乎没有），而在把"大家都烦的废话"提炼成一套可复用的行为契约。风险：① viral star 含水分，实际留存待观察；② 规则过苛会损害需要推理过程的任务。对想做"专家行为规范"的用户，这是最佳范本——把 SOUL/AGENTS 里的风格要求压成一份可插拔 SKILL。

## 8. 关键文件路径速查
- 真源：`skills/i-have-adhd/SKILL.md`
- 平台接入：`plugin.json`、`gemini-extension.json`、`kimi.plugin.json`、`qwen-extension.json`、`.claude-plugin/`、`.codex-plugin/`、`.cursor/`、`.opencode/`、`.agents/`
- 质量保障：`evals/`、`tests/`、`hooks/`、`extensions/`、`scripts/`
- 说明：`README.md`（9 语种）、`AGENTS.md`、`GEMINI.md`、`INSTALL.md`、`CONTRIBUTING.md`
