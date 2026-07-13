# 🔍 Nutlope/hallmark — 全方位深度调研

> **调研日期**: 2026-07-14 | **Stars**: 4,963 ⭐ | **Forks**: 270 | **Open Issues**: 6 | **License**: MIT
> **语言**: Markdown（Agent Skill，CSS 产出）| **背景**: Together AI 出品
> **最新发布**: 无 tag（经 `npx skills add nutlope/hallmark` 分发）| **创建**: 2026-04-27 | **最后 push**: 2026-06-26

---

## 一、项目定位（一句话）

Hallmark 是一个给 Claude Code / Cursor / Codex 用的 **反 AI 味设计技能**——它给 Agent 一套"拒绝生成 AI slop"的硬规则：为每个需求挑不同宏观结构、套 20 套主题之一、跑 57 道 slop 测试门 + 发射前自批判，让两个不同 brief 出来的页面"像两个站，而不是同一模板换色"。

## 二、项目亮点（差异化）

1. **结构多样性 > 视觉多样性**：多数反 slop 技能只调色板，Hallmark 坚持**宏观结构也要变**——hero→3-feature→CTA→footer 这种"LLM 默认节奏"被显式打散，不同 brief 用不同 section 律动。
2. **57 道 slop-test 门 + 发射前自批判**：每次产出前在 6 个轴（Philosophy/Hierarchy/Execution/Specificity/Restraint/Variety）打 1–5 分，任一 <3 触发重做，并把六分戳在产物顶部（`/* Hallmark · pre-emit critique: P5 H4 E5 S4 R5 V5 */`）。
3. **锁定 token，禁止中途 improvisation**：选定主题后所有颜色/`font-family` 必须引用命名 token（`var(--color-accent)`），内联 OKLCH/hex 或绕过 token 的字体声明直接判违规——保证整页调性一致。
4. **四动词一体**：默认（新建）/ `audit`（按 anti-pattern 打分、不改）/ `redesign`（保留文案+IA+品牌、只换视觉结构）/ `study`（从截图/URL 抽"设计 DNA"，拒绝像素克隆与付费模板，可导出 `design.md`）。
5. **组件级 8 态纪律**：组件场景强制交付全部 8 态（default/hover/focus-visible/active/disabled/loading/error/success）+ 一个 8 态预览页，比页面级更严。

## 三、核心架构

本质是 **一个 SKILL.md（YAML frontmatter + 规则正文）+ `references/` 参考库 + `docs/` 配方**。分发靠 `npx skills add nutlope/hallmark`（或手动拷到 `~/.claude/skills/hallmark/`、`.cursor/rules/hallmark.mdc`、`.codex/skills/hallmark/`）。

技能内部有清晰的"流程 + 学科"双层结构：

```
默认 Design flow:
  Step 0  Pre-flight scan   读现有 tokens/字体/框架/微交互姿态
  Step 1  Genre detection    editorial / modern-minimal / atmospheric / playful
  Step 2  Macrostructure pick（20 主题轮转 + 静默 custom 分支）
  Step 2.6 Theme route      锁定 token，禁止内联值
  Step 4  Enrichment         hero 插画 / demo 视频 / 抽象背景
  Step 5  Multi-section preview
  发射前 → Pre-emit self-critique（6 轴 <3 重做）

跨动词的 6 大学科（audit/redesign/study/组件 都适用）：
  1 发射前自批判  2 诚实文案(不编指标)  3 锁定 token
  4 禁手绘假 chrome  5 移动端 320/375/414/768 四宽验证  6 排版纯净(标题不斜体)
```

**关键安全护栏**：Hallmark 是设计技能不是"推土机"——现有项目里默认就地改/增量加组件，删生产文件/路由树需用户显式确认；PDF/README/稿子当参考素材，不逐字抄。

**主题系统**：20 个命名主题（catalog）默轮换 + 一个安静的 custom 分支（仅在 brief 带创作意图信号——点名品牌色/多维 vibe/显式要 custom——才触发，从零造 OKLCH 调色 + 自由字体配对，仍过 57 门）。

## 四、应用场景与启发

- **给"AI 前端生成"直接可用的护栏**：如果你在做"AI 帮写 UI"的产品/技能，Hallmark 的"57 门 + 6 轴自批判 + 锁定 token + 8 态组件"是可整段搬用的质量门，比事后人工挑毛病省得多。
- **结构性反模板是可借鉴的切入点**：多数反 slop 只动视觉，Hallmark 证明"先打散宏观结构"才是去模板味的关键。你给任何生成式 UI 加约束时，应同时约束"section 律动"而非仅"配色"。
- **`study` 抽 DNA 的模式**：从参考设计提取"宏观结构+字形配对+色彩锚点"而非像素克隆，并导出可移植 `design.md`——这是"借鉴不抄袭"的干净实现，适合任何需要"从竞品学设计"的团队。
- **与 UI/UX 工作流结合**：本仓库的 `ui-ux-super-optimizer` 等技能可把 Hallmark 的 slop-test 门作为"发射前校验"一环，互补（Hallmark 偏规则硬约束，ui-ux 偏审美优化）。

## 五、源码解读（关键模块）

**1. 发射前自批判（SKILL.md 核心纪律）**
```markdown
## Disciplines (跨所有动词)
1. Pre-emit self-critique: 发射前在 6 轴打 1–5 分，任一 <3 触发重做，
   并把六分戳在产物顶部：/* Hallmark · pre-emit critique: P5 H4 E5 S4 R5 V5 */
2. Honest copy: 用户没给的指标绝不编造；"+47% 转化"等一旦虚构即 slop（gate 46）
3. Locked tokens: 选定主题后所有色/字体必须引用 var(--token)，内联值违规（gate 48）
```
要点：把"质量门"写成 Agent 必须执行并**自我公示分数**的步骤，比隐式建议有效得多。

**2. 组件级 8 态交付（component-scope）**
```text
组件场景强制：所有交互组件交付 8 态 default/hover/focus-visible/active/
disabled/loading/error/success + 一个 .preview.html 竖向堆叠 8 态、各标 label
（用 .is-hover 等 class 强制伪类，一次渲染全部态）
```
要点：把"状态完整性"变成可一键预览的交付物，而不是靠开发者记得补 loading/error。

## 六、全网口碑

- **社区信号**：4.96K⭐ / 270 forks / 仅 6 open issues（issue 极少，说明规则集稳定或用户量尚在早期），MIT，Together AI 背书，有 live demo（usehallmark.com）与 20+ 真实示例页。
- **口碑倾向**：正面集中在"出来的页面真的不像 AI 生成""结构会变""audit/study 动词实用"；顾虑主要是它是**规则堆**（67KB SKILL.md），Agent 遵循度依赖模型能力，且 last push 在 2026-06-26（相对其他三个不那么活跃）。
- **数据不可用**：具体 HN/Reddit 单帖评分、Twitter 讨论量未抓取；以上基于仓库元数据 + README/SKILL 自述推断。

## 七、竞品对比 + 核心研判

| 维度 | hallmark (Together AI) | Anthropic frontend-design skill | 通用 "美化 UI" 提示词 |
|------|------------------------|----------------------------------|----------------------|
| 反 slop 手段 | 57 门 + 6 轴自批判 + 结构多样 | 审美原则（较软） | 基本无 |
| 跨 Agent | Claude/Cursor/Codex | 主要 Claude | 任意 |
| 动词 | 建/审/重设/抽DNA | 建 | 建 |
| 组件 8 态 | ✅ 强制 | 视版本 | 无 |
| 可移植 design.md | ✅ study 导出 | ❌ | ❌ |

README 自述其规则源自"anti-AI-slop 设计领域共识（Anthropic 前端技能、Claude cookbook 前端美学、2026 tactile rebellion 运动）"——即站在已有共识肩上的工程化封装。

**核心研判**：
- **优势**：目前把"反 AI 味"落成**可执行硬规则 + 自批判公示**的最完整开源技能；结构多样性思路切中要害；四动词覆盖"建/审/改/学"全周期；MIT 可随意 fork。
- **风险**：规则集庞大（Agent 遵循度受模型能力影响）；仅 4.96K⭐、近期 push 不频繁，生态与迭代速度弱于前三个；偏 greenfield 页面，对已有大型项目的增量 redesign 依赖"用户显式确认"护栏，自动化空间有限。
- **趋势判断**：随着"AI 生成页面一眼假"成为痛点，反 slop 设计技能会成标配。Hallmark 的"硬门 + 自批判 + 结构多样"是值得直接借鉴（甚至集成进你自己的 UI 生成流程）的范式，尤其适合做"发射前质量闸门"。

## 八、关键文件路径速查

- `skills/hallmark/SKILL.md` — 技能主体（frontmatter + 流程 + 6 大学科 + 组件 8 态）
- `skills/hallmark/references/slop-test.md` — 57 道 slop 测试门（含 Pre-emit self-critique）
- `skills/hallmark/references/anti-patterns.md` — 反模式库（编造指标 / 中途 token  improvisation / 手绘假 chrome / 斜体标题 等）
- `skills/hallmark/references/structure.md` — 宏观结构（macrostructure）多样性协议
- `skills/hallmark/references/custom-theme.md` — custom 分支（创作意图信号 → 从零造主题）
- `skills/hallmark/references/study.md` — study 动词（抽设计 DNA + design.md 导出）
- `skills/hallmark/references/responsive.md` `interaction-and-states.md` — 移动端四宽 / 8 态交互纪律
- `docs/recipes.md` `docs/study-examples.md` — 实战配方与 study 示例
