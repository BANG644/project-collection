# nature-skills 深度调研

> 调研日期：2026-11-09 ｜ Stars：52,759 ｜ 语言：Python ｜ 协议：Apache-2.0 ｜ 主分支：main ｜ 创建：2026-04-24

## 一、项目全景

`Yuan1z0825/nature-skills` 是一套面向 AI 学者的**可复用科研技能集合**，核心理念是"把一篇 Nature 论文的诞生过程拆成可安装的 Agent Skill"。它不卖模型、不卖算力，而是把科研工作流（检索、阅读、写作、绘图、引用、审稿回复、转 PPT/专利）**工程化为 23+ 个可插拔技能**，让 Claude Code / Codex / Chatbox / OpenClaw / OpenCode / Hermes 等 Agent 直接调用。

关键事实（仓库元数据 + 社区实测）：
- **23+ Skills**，覆盖科研全链路：`nature-academic-search`（含 `mcp-server/`）、`nature-citation`、`nature-data`、`nature-downloader`、`nature-experiment-log`、`nature-figure`、`nature-image2ppt`、`nature-literature-pipeline`、`nature-paper-card`、`nature-paper-to-patent`、`nature-paper-trans`、`nature-paper-xray`、`nature-paper2ppt`、`nature-paper2word`、`nature-polishing`、`nature-proposal-writer`、`nature-reader`、`nature-ref-verifier`、`nature-response`、`nature-reviewer`、`nature-shared`、`nature-social-science`、`nature-statistics`、`nature-writing`。
- 每个 Skill 自带 `SKILL.md` + `README.md` + `README_EN.md`，部分带 `scripts/`、`references/`、`manifest.yaml`、`mcp-server/`。
- 安装方式：`npx skills`、Claude Code、Codex、Chatbox 等；Apache-2.0。
- 创始人为上海交大（医疗 AI 方向）博士生 Yizhe Yuan，配套"知识星球"付费社区与 API 代充渠道（商业侧）。

**项目亮点**
1. **"投稿规范"写成 Agent 可执行技能，而非又一份提示词合集**——这是它区别于普通 prompt 仓库的核心。
2. **共享资源层 + 三级质量体系**：`nature-shared` 提供跨技能公共契约；明确区分**第一手来源 / 用户材料 / 模型推断**三类信息，降低幻觉污染。
3. **Paper X-Ray 范式**：`nature-paper-xray` 强调"读懂作者到底怎么想出来的"，明确 NOT a summary / translation / peer review——直击"读论文只看摘要"的痛点。
4. **可只装所需部分**：模块化粒度细，用户不必一次性把整套流程塞给 Agent。

## 二、核心架构

nature-skills 的架构是 **"技能市场（skills/）+ 共享契约层（nature-shared）+ 路由协议（SKILL.md frontmatter）+ Agent 宿主"**：

- **技能层 `skills/<name>/`**：每个技能是独立目录，由 YAML frontmatter（`name` + `description` 路由词）驱动 Agent 选择；内含 `SKILL.md`（主流程）、`references/`（领域知识）、`scripts/`（可复现脚本）、`manifest.yaml`（后端/资源声明）。
- **共享层 `nature-shared/`**：跨技能复用核心，如 `core/paper-type-taxonomy.md`（论文类型分类）、`core/contract.md`（产出契约）。
- **路由协议**：`SKILL.md` 顶部 `description` 用中英双语描述触发场景（如"精读论文 / 讲透这篇论文 / paper x-ray"），Agent 据此决定加载哪个技能、加载哪些 `always_load` 文件。
- **宿主无关**：通过标准 SKILL.md 规范对接多种 Agent；部分技能（如 academic-search）额外提供 `mcp-server/` 以 MCP 协议暴露能力。

数据流：用户自然语言需求 → Agent 按 SKILL.md 路由词匹配技能 → 读取 `manifest.yaml` + `always_load` 核心 → 调用 `scripts/` 或 `references/` → 产出结构化科研工件（图、审稿回复、PPT、Word）。

## 三、源码深度解读

### 1. 图形摘要路由（`skills/nature-figure/SKILL.md`）
`nature-figure` 的 `SKILL.md` 用**路由协议**把"画科学图"拆成多条互斥路径，并强制人工科学审核边界：

```markdown
## Routing protocol
### 0. Check for graphical-abstract and AI-schematic routes
... read references/ai-graphical-abstract-workflow.md first. It owns the
message/audience brief, composition and palette workflow, policy gate,
human scientific review, disclosure boundary, and provenance requirements.
...
Treat output as a draft schematic / graphical abstract, not as a quantitative
data panel. Do not invent experimental values, author logos, institutional
marks, or unsupported mechanisms.
```
其 `manifest.yaml` 声明 `backend` 轴（python/r）及各值映射文件；`scripts/audit_svg_schematic.py` 在交付前对 SVG 做合规审计——把"AI 画图易造假"的风险用流程钉死。

### 2. 论文精读契约（`skills/nature-paper-xray/SKILL.md`）
`nature-paper-xray` 把"读懂一篇论文"定义为重建作者研究路径，而非复述摘要：

```markdown
## Default stance
- The method section is a teaching order, not the order the work happened in.
- Every figure was chosen. Ask what the authors want a reader to believe...
## Workflow
4. Ground the mathematics. ... follow each key formula with a micro-example
   using concrete numbers carried to the end.
6. Preserve hedging strength. "May" is not "does", "suggests" is not "shows".
   Where the paper does not report something the conclusion needs, write that
   it is not reported. Never substitute a plausible number...
```
这套"保真度"约束（不替作者补动机、不编数字、保留 hedging 强度）是它质量口碑的来源，也直接对应社区最在意的"引用幻觉/数据不一致"风险。

## 四、应用场景与启发

- **科研全链路提效**：初写者用 structure 组织、用 `nature-reviewer` 模拟审稿人预判质疑、用 `nature-response` 把返修信/cover letter/LaTeX 返修包流程化——社区实测"结构组织速度、审稿视角预判、语言密度控制"提升最明显。
- **"规范即技能"的范式**：把任何强规范、强流程的知识工作（法律、医学、咨询）拆成"路由词 + 共享契约 + 可审计脚本"，比提示词堆砌更稳、更可维护。本仓库已入库的 `addyosmani/agent-skills`（#16）、`anthropics/skills`、`agentskills/agentskills`（#19）同属此赛道，可对照研究。
- **幻觉防控的可借鉴点**：`nature-shared` 显式分离"第一手来源 / 用户材料 / 模型推断"，并强制"引用必须人工在 PubMed/Scholar 核实"——任何接 LLM 的知识工作都应建立类似的**来源分级 + 人工核验闸门**。

## 五、社区口碑

- **顶级机构背书信号**：aixq.cc 报道 Google DeepMind 以 nature-skills 为设计参考推出 Science-skills，"大厂实验室选择以开源社区项目为参考而非从零设计"，被视为赛道认可信号。
- **真实用户实测（lqnn.cn）**：最强增益在结构组织、审稿视角预判、语言密度控制；但踩坑清单明确——**引用幻觉**（AI 自动补的参考文献必须逐一在 PubMed/Scholar 核实）、方法过度简化、摘要与正文数值不一致、术语漂移、过度高级化掩盖论证漏洞（作者称"最危险的就是最后一条"）。
- **边界认知（zhichai.net / aixq.cc）**：共识是"Skill 解决的是表达问题，不是科学问题"——它放大优点也放大缺陷，"shaky science 包装漂亮是学术共同体最大敌人"；安装门槛（Claude Code / GitHub）天然筛掉非技术背景研究者。
- **成熟度提醒**：aixq.cc 指出 70%+ 技能处于 Draft/Beta，且路由逻辑围绕 Codex Agent 行为设计，换平台迁移成本不小；toutiao 测评将其列为"科研 Skills 顶级档第一名"（当时约 2.85 万 Star），但提醒"不是 Nature 官方项目，各模块成熟度不一，当瑞士军刀而非录用保证书"。

> 口碑研判：工程严谨度、覆盖广度、来源分级获高度认可，DeepMind 参考是强信任信号；主要风险是引用幻觉与过度润色掩盖弱论证，需人工把关。

## 六、竞品对比

| 维度 | nature-skills | addyosmani/agent-skills(#16) | anthropics/skills | Elicit/Consensus(Web) |
|------|--------------|------------------------------|-------------------|----------------------|
| 聚焦领域 | 科研全生命周期 | 软件工程全生命周期 | 通用 Agent 能力 | 文献检索/综述(SaaS) |
| 技能数 | 23+ | 24 | 海量 | N/A(平台) |
| 来源分级 | ✅ 显式三级 | 部分 | 依技能 | 平台内 |
| 本地可跑 | ✅ Agent 宿主 | ✅ | ✅ | ❌ 云端 |
| 协议 | Apache-2.0 | 未明示 | MIT 类 | 闭源 SaaS |

结论：在"科研写作/绘图/审稿"垂直赛道，nature-skills 是覆盖最完整、契约最严的一套；通用型（anthropics/skills、addyosmani/agent-skills）侧重工程，不直接解决投稿规范。它真正的对手是**"研究者手工调 matplotlib 到凌晨 + 逐条手排参考文献"**这种原始工作流。

## 七、核心研判

1. **方向价值高**：把"投稿规范"工程化为可执行技能，重新定义了学术工作的基本假设，已被顶级实验室参考，范式成立。
2. **不能替代科学训练**：它放大 science 的优点也放大缺陷——核心 insight、好问题、好证据仍属人；应作"放大镜"而非"魔法棒"（导师视角）。
3. **落地三道闸**：引用必须人工核实、方法以原始记录为准、保留 AI 改动差异高亮逐条确认——这三条不执行，风险远大于收益。
4. **数据不可用**：各模块成熟度不一、Draft/Beta 占比高，无统一第三方基准；"DeepMind 参考"来自科技媒体转述，未找到 DeepMind 官方声明原文。

## 八、关键文件路径速查

- `skills/nature-figure/SKILL.md` — 科学绘图技能（含 AI 图形摘要路由 + `scripts/audit_svg_schematic.py`）
- `skills/nature-figure/manifest.yaml` — 后端轴（python/r）声明与资源映射
- `skills/nature-paper-xray/SKILL.md` — 论文精读（Paper X-Ray，保真度约束）
- `skills/nature-polishing/SKILL.md` — 学术英文润色 + 术语一致性扫描
- `skills/nature-reviewer/` `skills/nature-response/` — 模拟审稿人 / 返修信·cover letter·LaTeX 返修包
- `skills/nature-shared/core/` — 跨技能共享契约（paper-type-taxonomy.md / contract.md）
- `skills/nature-academic-search/mcp-server/` — 以 MCP 协议暴露检索能力
- `README_EN.md` — 技能索引 + 安装指南（Claude Code / Codex / Chatbox / npx skills）
