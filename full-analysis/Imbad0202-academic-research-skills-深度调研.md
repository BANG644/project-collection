# Imbad0202/academic-research-skills — 深度调研

> 调研日期：2026-09-28 ｜ 星标：49,638 ｜ 许可：CC BY-NC 4.0（**非开源，仅非商用**）｜ 版本：v3.22.2 ｜ 语言：Markdown 提示词驱动 + Python 护栏 ｜ 维护者：Cheng-I Wu

## 1. 项目定位（一句话）
面向 Claude Code 的**学术科研副驾驶框架**：覆盖"研究→写作→评审→修改→定稿"全链路，以"人在环内（human-in-the-loop）"为铁律，拒绝全自动写论文。

## 2. 项目亮点
- **27 个模式 / 4 大技能 / 39 个提示词角色**：deep-research(8)、academic-paper(11)、academic-paper-reviewer(6)、academic-pipeline(编排+resume)，单一真相源在 `MODE_REGISTRY.md`。
- **诚信闸门（integrity gates）**：Stage 2.5 / 4.5 跑 7 模式阻断式检查清单；v3.8 引入 **L3 claim-faithfulness gate**——每个引用带定位锚点，可开启 `ARS_CLAIM_AUDIT=1` 逐条核对其是否真支持所提主张（claim-not-supported / fabricated-reference 等 5 类 HIGH-WARN 拒产出）。
- **跨模型验证 + 物料护照**：`ARS_CROSS_MODEL` 交叉审查；每篇稿子生成 Material Passport 记录引用/实验溯源；Experiment Provenance Intake(#260) 强制在 Stage 1 声明"是否跑了实验"，关闭"编造实验被静默绕过"的漏洞。
- **边界明确且被记录**：`POSITIONING.md` 显式拒绝 7 类"自主科研反模式"（端到端自动管线、自主选题 agent、Paper2X 自动生成、自主跑实验、湿实验室 API、模拟 IRB、把产量当成果）。
- **学术可信度高**：有 Zenodo DOI、arXiv 引用（Zhao 2026 1.47 亿参考文献语料审计、Ren 2026 综述、Gartenberg 2026 等 5 个学术锚点作为设计依据），多语言 README，已发真实 pipeline 产出样例（含 Stage 2.5 抓出 15 处问题文献的诚信报告）。

## 3. 核心架构
- **插件分发**：`.claude-plugin/marketplace.json` + `plugin.json`（v3.7.0+ 走 `/plugin marketplace add` → `/plugin install`）；也提供 Codex 兄弟分发、Claude Science 导入、Pi 包装。
- **分层契约**：每个 skill 声明 `data_access_level`(raw/redacted/verified_only) 与 `task_type`(open-ended/outcome-gradable)，由 `scripts/check_data_access_level.py` 强制；Benchmark Report Schema 约束诚实对比。
- **管线编排**：academic-pipeline 10 阶段，自适应检查点 + 中期强化 + 逐标准回归检查；`resume_from_passport=<hash>` 可从护照重置边界恢复。

## 4. 应用场景与启发
- **对科研新手的护栏价值极高**：用户正处于科研入门期（OCR/大模型方向），ARS 的"Socratic 引导定题 + 强制每阶段确认 + 引用/主张对齐核查"正好是方法论补课工具。
- **可迁移的质量门禁范式**：其"L3 主张-证据对齐闸门""实验溯源 Intake""跨模型 handoff 信封(`scripts/cross_model_handoff.py`)"可直接借鉴到用户的**错题归因链路**——给归因结果加"主张-证据对齐"与"跨模型复核"两道闸。
- **注意边界**：CC BY-NC 禁止商用 SaaS/托管/咨询打包；定位是 copilot 不是 pilot，不替你做实验也不声称作者身份。

## 5. 源码深度解读
`POSITIONING.md` 把"谁控制下一次研究状态迁移"作为唯一判据来区分 copilot vs auto-research：
> Rejected: the scholar would become a reviewer of AI output, not the author. The pipeline's mandatory checkpoints exist precisely to prevent this.

`MODE_REGISTRY.md` 的 27 模式矩阵用 `Spectrum`(Fidelity/Balanced/Originality) 与 `Oversight`(Very High→Low) 双轴约束每个模式的人为介入强度，例如 `socratic` 模式 Oversight=Very High、`format-convert`=Low——把"自动化程度"做成可审计的元数据而非暗箱。

`docs/` 下 `ARCHITECTURE.md` / `DATA_FLOWS.md` / `RISK_REGISTER.md` / `STAGE_CAPABILITY_MATRIX.md` 把"数据流出了什么、缓存了什么、哪些风险已知"全部写成可审查文档，是开源科研工具罕见的工程纪律。

## 6. 社区口碑
- 49.6k⭐、v3.22 成熟度高（2026-09-25 仍更新）；Zenodo 长期归档；被多篇 2026 Nature/arXiv 论文引用为设计依据。
- 缺点：体量庞大、提示词工程复杂，新手需读 `docs/SETUP.md` 六种安装法；纯提示词驱动，对"真正跑实验"环节需配合兄弟项目 `Imbad0202/experiment-agent`。

## 7. 竞品对比 + 核心研判
| 项目 | 定位 | 差异 |
|---|---|---|
| ARS | 人在环内科研副驾驶 | 诚信闸门 + 非商用护栏，最严谨 |
| Google PaperOrchestra (2604.05018) | 自动科研 | ARS 借鉴其 VLM 图验证/修订轨迹 |
| The AI Scientist | 全自主写论文 | ARS 明确拒绝此路线 |
| experiment-agent | 实验执行 | ARS 的上游互补件 |

**研判**：这是目前最"克制且诚实"的 AI 科研助手，价值在**过程质量**而非**产出数量**；作为用户科研方法论的"外部评审+引用核查"层非常合适，但不要用它替代你自己的实验与判断。

## 8. 关键文件路径速查
- `.claude-plugin/plugin.json` — 插件清单（4 skills/27 modes/39 roles 总述）
- `POSITIONING.md` — 定位与 7 类拒绝机制（必读边界）
- `MODE_REGISTRY.md` — 27 模式矩阵（单一真相源）
- `docs/ARCHITECTURE.md` / `DATA_FLOWS.md` / `RISK_REGISTER.md` — 架构与数据流
- `academic-pipeline/references/ai_research_failure_modes.md` — 7 模式失败清单
- `shared/ground_truth_isolation_pattern.md` — 真值隔离模式
- `scripts/check_data_access_level.py` / `scripts/cross_model_handoff.py` — 护栏脚本
