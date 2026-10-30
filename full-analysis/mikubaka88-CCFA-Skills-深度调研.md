# mikubaka88/CCFA-Skills 深度调研

> 调研日期：2026-10-31 ｜ 数据来源：GitHub API（README / `AGENT_GUIDE.md` / 路由与契约章节）
> 许可证：**MIT** ｜ 形态：给 Codex/Claude Code/Cursor/Gemini CLI 用的「CCF-A 论文研究故事线」技能家族（17 个 skill，TeX 脚手架 + YAML 路由）

## 项目亮点（差异化）

- **17 个分工明确的 skill 接力，而非一个万能长 prompt**：从 idea、文献、实验，到写作、绘图、评审、rebuttal、投稿，每个阶段由一个专精 skill 负责，handoff 时**研究问题/证据/结论的连贯性被保留**（任务连续性不丢失）。
- **「论文是一条需在反复修改中保持连贯的研究故事线」**：直击「idea 还在、轮廓丢了」的痛点——related work 淹没问题、方法描述与代码机制偏离、补实验让论证分叉。
- **强路由与契约**：`ccf-common/references/skill-trigger-registry.yaml` 做模糊路由，`handoff-modes.md` 规范证据传递/授权/集成；`artifact-contracts.md` 固定每个产物的规范路径与工作目录。
- **人文化（humanization）基线贯穿**：`ccf-humanization` 先做，通信直接、保留证据/不确定性/严格批评，review-only 不改写被评文本——对抗「AI 腔」与「虚构结论」。
- **多语言与自动更新**：README 含简/繁/英三语，支持 Codex/Claude/Cursor/Gemini 安装，带 AUTO_UPDATE 指南。

## 项目定位（一句话）

CCFA-Skills 是一个**为 CCF-A 论文量身打造的「研究故事线」技能家族**——用 17 个接力式 skill 把 idea→文献→实验→写作→绘图→评审→rebuttal→投稿串成一条连贯可审计的管线，让论文在长期推进中不丢失清晰轮廓。

> **3.4k⭐**（2026-06 创建、10-20 仍活跃，Trendshift 日/周榜在榜），MIT，TeX，140 fork / 8 open issues，v0.11.0。

## 核心架构

- **入口与引导**：`AGENT_GUIDE.md`（家族总引导）+ 路由章节；先激活 `ccf-humanization` → `ccf-common`，再按需调专精 skill。
- **家族成员（17 个，按职责）**：
  - 构思/评审：`ccf-idea-optimizer`（救 idea）、`ccf-idea-reviewer`（价值/新颖性/机制，不含分）、`ccf-paper-reviewer`（评估不改写）、`ccf-submission-checker`（venue/年/track 规则 + LaTeX/PDF 实检）。
  - 文献：`ccf-literature-monitor`（新论文/竞品跟踪）、`ccf-literature-searcher`（外部发现）、`ccf-integrity-auditor`（引用与论断支撑核查）。
  - 实验：`ccf-experiment-designer`（数据集/baseline/消融/指标 schema）。
  - 写作/绘图：`ccf-paper-writer`（草稿/修订/压缩/展示）、`ccf-visual-composer`（图/表/方法架构图/可编辑重建）、`ccf-paper-to-exemplar`（写作范式抽取）。
  - 收尾：`ccf-rebuttal-writer`（作者回复/修订台账/重投计划）、`ccf-pipeline-orchestrator`（规划/依赖协调）。
  - 基建：`ccf-common`（共享策略）、`ccf-project-scaffolder`（初始化项目状态）、`ccf-skill-forger`（家族与文档图维护）。
- **契约与状态**：`ccf-common/references/{artifact-contracts,continuity,routing,task-modes}.md` + `ccfa.yaml`（项目状态）；`preferences.md`（个人偏好，任务内解析一次）。
- **安装矩阵**：`.claude-plugin/`、` .codex-plugin/`（plugin.json）+ `npx skills add mikubaka88/CCFA-Skills --global --agent codex --skill '*' --copy`。

## 源码深度解读（核心模块：路由注册表与交接契约）

**1. 模糊路由靠 YAML 注册表（`ccf-common/references/skill-trigger-registry.yaml`）**

```yaml
# 抽象意图 → 具体 skill（AGENT_GUIDE 第 22 条引用）
- intent: "选题值不值得做 / 靠谱吗"
  route: ccf-idea-reviewer        # 只判价值/新颖性/机制，不打分
- intent: "最新相关工作和 baseline"
  route: ccf-literature-searcher
- intent: "画方法架构图并要可编辑 PPTX"
  route: ccf-visual-composer
```
`AGENT_GUIDE` 明确要求「先用 `skill-trigger-registry.yaml` 做模糊路由、用 `handoff-modes.md` 做证据转移」——把「该调哪个 skill」从模型临场猜测变成**可查表、可审计**的决策，避免重复检索/报告。

**2. 交接携带完整上下文（`handoff-modes.md` + `artifact-contracts.md`）**

handoff 必须带：**scope、前置状态、源版本/锚点、规范路径、具体问句/完成条件**；`artifact-contracts.md` 固定每类产物一个稳定工作目录（`ccfa-workfiles/<purpose>/<artifact-id>/`，如 `figures/method-overview`）。这意味着一个 skill 把任务交给下一个时，研究问题/证据/结论的链接被保留，长任务丢失上下文后也能从 `ccfa.yaml` 重建——**这正是「故事线不发散」的工程保障**。

## 应用场景与启发

- **CCF-A / 顶会论文全流程写作**：从选题评审到 rebuttal，用接力式 skill 保持论证连贯，特别适合「长期推进、易丢轮廓」的科研写作。
- **「长任务不丢上下文」的 skill 编排范式**：YAML 路由注册表 + 强制 handoff 契约 + 固定产物路径，可迁移到任何「多 Agent/多 skill 长链路」场景（如本工作区的错题归因、paper-companion）。
- **对抗 AI 腔与虚构**：humanization 基线 + review-only 不改写 + 不虚构实证结论，是「AI 辅助学术写作需可信」的范本。
- **对用户的直接价值**：用户正推进科研入门与论文写作，这套家族可直接复用其「idea→实验→写作→评审」链路与路由/契约设计。

## 社区口碑

- **定位精准、增长快**：**3.4k⭐**、MIT，针对 CCF-A 这一中文科研刚需人群，Trendshift 日/周榜在榜，v0.11.0 迭代活跃；三语文档 + 多 Agent 安装降低门槛。
- **主要风险**：极度垂直（CCF-A 特定），非该赛道研究者收益有限；17 skill 的路由/契约学习曲线不低；「不虚构结论」依赖宿主 agent 守纪律。
- **主观满意度数据不可用**：精确 NPS 无第三方统计；上述基于 README 自述与 Trendshift 榜单。

## 竞品对比

| 维度 | CCFA-Skills | 单一论文写作 prompt | PaperAgent / 通用学术 Agent | 人工润色/导师 |
|------|-------------|---------------------|------------------------------|---------------|
| 覆盖 | idea→投稿全链路 | 单点 | 部分 | 全靠人 |
| 连贯性保障 | 路由+契约+状态 yaml | 无 | 弱 | 人脑 |
| 防虚构 | humanization 基线 | 无 | 视实现 | 有 |
| 垂直度 | CCF-A 专精 | 通用 | 通用 | 领域专家 |

## 核心研判

- **价值清晰**：在「CCF-A 论文全链路、且要保持故事线连贯」这一垂直刚需上几乎没有对等物；其「YAML 路由 + handoff 契约 + 固定产物路径」的 skill 编排，是长链路多 Agent 协作的高质量范本，对本工作区的科研类 Agent 直接可借鉴。
- **边界明确**：**高度垂直**（CCF-A 特定），通用论文场景需改造；17 skill 体系有学习成本。
- **采用建议**：做 CCF-A/顶会写作时优先试，重点抄其「路由注册表 + 交接契约」设计到自己的多 Agent 流水线；非该赛道可取其编排思想、弃其具体技能。

## 关键文件路径速查

- `AGENT_GUIDE.md` — 家族总引导（路由/协作/契约总则）
- `ccf-common/references/skill-trigger-registry.yaml` — 模糊意图→skill 路由表
- `ccf-common/references/{handoff-modes,artifact-contracts,continuity,task-modes}.md` — 交接/产物/连续性/任务模式契约
- `AGENT_GUIDE`（第 1–15 条）— `ccf-humanization`→`ccf-common`→专精 skill 的激活顺序
- `ccf-{idea-optimizer,idea-reviewer,paper-writer,visual-composer,paper-reviewer,rebuttal-writer,submission-checker,...}` — 17 个技能
- `.claude-plugin/plugin.json` · `.codex-plugin/plugin.json` · `npx skills add ... --copy` — 多 Agent 安装
- `ccfa.yaml` — 项目状态（上下文重建锚点）
