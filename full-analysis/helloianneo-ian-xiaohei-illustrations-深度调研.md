# helloianneo/ian-xiaohei-illustrations 深度调研

> 调研日期：2026-10-07 | 原始仓库：https://github.com/helloianneo/ian-xiaohei-illustrations
> 语言：Markdown / Skill 定义（无编译代码，纯 prompt + 资产） | 许可：MIT | Stars：≈12,376 | 最近活跃：2026-09-24

## 一、项目定位（一句话）

一个 **Codex Skill**：指导 AI Agent 把中文文章里的「判断、流程、状态、隐喻」变成一张张白底、手绘、怪诞但清爽的 16:9 正文配图，核心是让一个叫「小黑」的黑色线条 IP 承担画面里的核心动作。

## 二、项目亮点（差异化）

- **不是通用插画 prompt，是「认知锚点」引擎**：先消化正文、提炼认知转折，再决定哪几处值得配图——「不平均配图，优先认知锚点」。
- **强 IP 一致性**：默认视觉人格「小黑」（黑实心、白点眼、细腿、空表情），且**必须参与核心动作**，不能是角落装饰——这是它区别于普通 prompt 合集的关键。
- **渐进披露（Progressive Disclosure）的 skill 结构**：`references/` 下拆 5 个文档（风格 DNA / IP 设定 / 构图模式 / 提示词模板 / QA 清单），按需读取，避免一次性塞满上下文。
- **反模板化纪律**：明确要求「每次从当前文章重新发明一个怪诞但成立的隐喻」，禁止复刻已有案例构图（传送带断点 / 小黑拉线等）。
- **可交付闭环**：从 shot list 规划 → 单张生成（`image_gen`）→ QA 检查 → 落盘 `assets/<slug>-illustrations/`。

## 三、核心架构

```
ian-xiaohei-illustrations/
├── SKILL.md                      # 入口：定位 + 参考索引 + 5 步工作流 + 输出口径
├── agents/openai.yaml           # harness 注册（openai 适配）
├── assets/examples/             # 仅低频视觉校准，不进默认生成路径
└── references/                  # 渐进披露：按需读取
    ├── style-dna.md             # 风格 DNA、颜色、文字、禁忌
    ├── xiaohei-ip.md            # 小黑 IP 形象 / 性格 / 动作库 / 禁忌
    ├── composition-patterns.md  # 结构类型 + 原创隐喻方法 + 反复刻规则
    ├── prompt-template.md        # 单张生图提示词模板
    └── qa-checklist.md          # 生成后检查与迭代规则
```

真正的「代码」是 `SKILL.md` 的 YAML frontmatter 与结构化指令；运行时靠 Agent 的 `image_gen` 能力出图。设计重心在**指令工程 + 资产组织**，而非传统程序。

## 四、应用场景与启发

- **给同类需求的解决思路**：当你要做一个「风格稳定、可复用的内容生产 Skill」时，把**风格 DNA / IP 设定 / 质检清单**拆成独立 `references/` 文件、用 SKILL.md 做索引与按需加载，是比「把一切写进一个 giant prompt」更可维护的范式——这与用户 WorkBuddy 的 skill 体系（`.workbuddy/skills/`）同构。
- **隐喻优先而非装饰优先**：「小黑必须承担核心动作，去掉小黑画面仍成立说明它太装饰」这条约束，是把「角色一致性」从口号落到可执行规则的范例，对任何需要稳定视觉人格的生成型 Skill 都有借鉴意义。
- **反 PPT / 反说明书**：它明确划清「正文配图 ≠ 信息图 ≠ 流程图」，这种**范围自律**值得在自建 Skill 时借鉴——先定义「不做什么」比「能做什么」更能保证产出质量。

## 五、源码深度解读

### 1) SKILL.md 入口的「参考索引 + 渐进披露」

```yaml
---
name: ian-xiaohei-illustrations
description: 生成 Ian 风格的中文正文配图。用于用户要求为中文文章、帖子、博客…生成
  “怪诞”“小黑”“手绘”“正文配图”…等任务；默认使用小黑 IP、纯白手绘、少量红橙蓝批注…
---
## 先读这些参考        # 关键：按需读取，不一次塞满上下文
- `references/style-dna.md`：风格 DNA、颜色、文字、禁忌。
- `references/xiaohei-ip.md`：小黑 IP 的形象、性格、动作库和禁忌。
- `references/composition-patterns.md`：结构类型、原创隐喻方法和反复刻规则。
- `references/prompt-template.md`：单张生图提示词模板。
- `references/qa-checklist.md`：生成后检查和迭代规则。
```

这段 frontmatter 的 `description` 用「否定枚举 + 默认定位」双写法（既说清楚做什么，也用「不做 PPT/商业插画/可爱卡通」划边界），是高质量 Skill 元数据的范本。

### 2) 5 步工作流（核心调度逻辑）

```text
1. 消化正文        # 提炼核心观点 / 认知转折 / 适合视觉化的段落
2. 先出配图策略    # shot list：每张图写清 段落位置/主题/核心意思/结构类型/小黑动作/标注词
                   # 默认 4-8 张；短文 1-3，长文不超 9
3. 单张生成        # 用户明确要图才生成；每张单独 image_gen，不拼多图
4. 检查与迭代      # 对照 qa-checklist：小黑是否装饰化 / 太满 / 太像 PPT / 错字
5. 保存交付        # assets/<article-slug>-illustrations/01-topic-name.png 顺序命名
```

「先出 shot list 再生成」的「规划—执行分离」、以及「默认 4–8 张、够用就好」的克制，都是降低失控生图成本的实用设计。

## 六、全网口碑

- GitHub ≈12.4k stars，作者 Ian（伊恩，产品设计师 / 一人公司实践者 / AI Builder），README 自述定位为「用 AI 团队打造个人生产系统里的一个小工具」。
- 配套生态：同作者 `ian-handdrawn-ppt`（手绘技术 PPT）、`awesome-claude-code-skills`（Claude Code Skills 精选合集）、`obsidian-ai-second-brain`。
- 内容社区向强（微信 / X / 个人站 www.ianneo.xyz），工程化程度中等但**产品设计叙事清晰**，适合内容创作者与 AI 工作流设计者借鉴。

## 七、竞品对比 + 核心研判

| 维度 | ian-xiaohei-illustrations | 通用插画 prompt / 图片生成 | PPT 信息图模板 |
|---|---|---|---|
| 产出性质 | 正文认知解释图（隐喻） | 通用配图 | 结构化信息图 |
| 风格一致性 | 强（小黑 IP 人格） | 弱（每次重新描述） | 模板固定 |
| 适用场景 | 文章/博客/方法论配图 | 任意 | 汇报/课件 |
| 工程化 | Skill + 渐进披露 | 单条 prompt | 静态模板 |

**核心研判**：它本质上是「**把一位产品设计师的视觉方法论，固化成一个可被 Agent 复用的 Skill**」——价值不在代码量，而在**指令结构 + IP 纪律 + 范围自律**。对想做「风格化内容生成 Skill」的开发者，其 `references/` 拆分、QA 清单、反模板化约束是最值得抄的三处。局限：依赖底层 `image_gen` 能力，中文错字/风格漂移仍需人工 QA；且定位垂直（不适合商业 KV / 矢量源文件需求）。

## 八、关键文件路径速查

- 入口与调度：`ian-xiaohei-illustrations/SKILL.md`
- harness 注册：`ian-xiaohei-illustrations/agents/openai.yaml`
- 风格与 IP 设定（按需读）：`references/style-dna.md`、`references/xiaohei-ip.md`
- 构图与提示词：`references/composition-patterns.md`、`references/prompt-template.md`
- 质检：`references/qa-checklist.md`
- 低频校准样例（不进默认路径）：`assets/examples/`、`examples/prompts.md`
- 安装说明：`README.md`（复制到 `${CODEX_HOME:-$HOME/.codex}/skills/`）
