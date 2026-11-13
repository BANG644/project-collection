# 🔬 tradermonty/claude-trading-skills — 全方位深度调研

> 调研日期：2026-11-14 ｜ Stars：4,054 ｜ 语言：Python（3.11–3.13，打包 floor 3.9）｜ 许可：MIT ｜ 编号：#593

## 📌 一句话定位
面向**时间受限个人投资者**的 Claude Skills 交易工作流工具箱：不替你下单、不卖信号，而是把市场复盘、风险管理、交易规划、日记化、持续改进**结构化**——「first for self, open for others」的个人项目，共享的是纪律与方法而非买卖建议。

## ⭐ 项目亮点
- **人始终在回路**：每个工作流都有人类决策闸（exposure ceiling、pre-trade discipline gate），明确「不外包买卖决策，只结构化决策过程」——与自动交易信号服务划清界限。
- **单一权威索引**：`skills-index.yaml` 是全量技能（id/分类/集成/工作流回溯）的 canonical 源，`workflows/*.yaml` 是工作流清单（技能顺序 + 决策闸 + 产物），二者皆被 validator 强制校验（`--strict-workflows`）。
- **无付费 API 也能跑**：5 技能启动路径（market-breadth-analyzer / uptrend-analyzer / position-sizer / trader-memory-core / signal-postmortem）只需公开 CSV、图表截图、本地文件，不强制订阅行情 API。
- **工程纪律罕见**：issue 用 [P2]/[P3] 优先级 + documentation/enhancement/bug + roadmap 标签管理；`scripts/` 含 schema validator 与打包脚本，CI 强制兼容矩阵。
- **覆盖 8 大技能域**：市场研判 / 核心组合 / 分红收入 / 波段机会 / 交易规划 / 交易记忆 / 策略研究 / 高级卫星，含 VCP/CANSLIM/IBD 分布日/FTD 等成熟方法论的技能化实现。

## 🏗️ 项目架构全景
仓库扁平清晰：`skills/<skill>/`（每技能含 SKILL.md + 参考材料 + 辅助脚本）、`skills-index.yaml`（权威元数据）、`workflows/`（运营清单 YAML，canonical）、`skill-packages/`（预构建 .skill 供 Claude Web 上传）、`skillsets/`（6 个目标导向安装包：market-regime/core-portfolio/dividend-income/swing-opportunity/trade-memory/strategy-research）、`docs/`（文档站 + schema spec）、`scripts/`（validator + bootstrap + 目录生成器）。

接入双通道：Claude Web App 上传 `.skill` 包；Claude Code 把技能目录拷进 `~/.claude/skills/`。配套 `hermes-trading-research-agent-work-package` 把技能打包成 Hermes 的 slash-command 例程（`/pre-market-routine`、`/after-close-review`、`/trade-journal` 等），明确「研究/日记/风险复盘助手，非自动交易系统」。

## 💡 应用场景与启发
- **典型场景**：① 15 分钟日盘检查（market-regime-daily → Exposure Coach 给仓位姿态，人类审而非下单）；② 每周长期组合复盘（core-portfolio-weekly，需 Alpaca，手动 CSV 可降级）；③ 仅当风险允许才找波段候选（swing-opportunity-daily，含 drawdown 断路器 + 纪律闸）；④ 每笔平仓记录学习（trade-memory-loop）。
- **可借鉴模式**：「**用 YAML 清单定义可复现工作流 + 人类决策闸 + 本地 YAML 日记**」是把专家流程工程化的通用范式，可迁移到任何「需要纪律但不想外包判断」的领域（医疗复盘、合规检查、研究 SOP）。
- **同类需求思路**：若你做垂直领域 Skill 集合，学它的「单一索引 + 校验器 + 预构建包 + 多 skillset 分发包」四件套——既保一致性又便于分发。
- **边界**：项目自陈「不为全自动化交易、信号外包、短线 scalping 设计」，ETA API 仍属可选增强。

## 🧠 核心源码解读（克制代码量）
`skills-index.yaml` 的 frontmatter 把每个技能声明为机器可读实体，并强制「README/CLAUDE.md/文档若与索引冲突，以索引为准」——这是防止文档漂移的硬规则：

```
# Canonical source: skills-index.yaml is the authoritative index of all skills.
# If this README, CLAUDE.md, or docs disagree with the index, the index is correct.
# workflows/*.yaml is canonical for multi-skill workflows.
```

工作流清单 `workflows/market-regime-daily.yaml` 以「anchor skills + API profile + 决策闸」组织，末尾明确 Exposure Coach 产出**供人审的姿态**而非订单。技能的 `integrations:` 字段声明输入要求（如 `fmp required` / `local_calculation` / `chart_image required`），validator 据此校验收发一致性——把「这个技能到底要什么数据」变成可机器校验的契约。

## 📐 架构决策与设计哲学
- **纪律优先于信号**：核心叙事是「结构化过程 > 预测对错」，免责声明反复强调 AS IS、非财务建议。
- **无 API 降级路径**：明确「no API 不意味 no external data」——公开 CSV/截图/本地文件仍必要，但刻意给零付费起步路径。
- **质量内建**：`scripts/validate_metadata_and_workflows` + `--strict-workflows` 把结构正确性变成 CI 关卡；兼容矩阵由 CI 实测而非声明。
- **透明边界**：Changelog + 发布兼容与迁移政策（`docs/dev/release-compatibility.md`）先于升级，体现「个人项目但按产品纪律维护」。

## 🌐 全网口碑画像
- **社区信号**：open issue ~76，标注专业（[P2]/[P3]、roadmap-2026-07、documentation），议题多为技能索引补全、测试隔离、路线图（#715 短侧卫星策略、#709 晨间决策 diff）。典型工程化自驱项目。
- **正面口碑**：投资者社区认可「把交易纪律工程化、且人始终在回路」的定位；5 技能零付费起步路径降低门槛；文档站（tradermonty.github.io）+ 日语 README 显诚意。
- **差评 / 摩擦**：① **免费层承诺过时**：#707 多个技能在新 Basic key 上吃 FMP 的 402/403，文档未同步——真实采用摩擦；② #705 ibd-distribution-day-monitor 缺 FMP key 抛未捕获 traceback，错误提示不友好；③ #731 测试里某技能 fmp_client 经 sys.modules 泄漏到 UGS 测试，隔离待修。
- **外部评测**：数据不可用（未检索到独立深度评测；声量主要在 GitHub 与文档站）。

## ⚔️ 竞品对比
| 维度 | Claude Trading Skills | virattt/ai-hedge-fund | Portfolioum/手动表格 | 券商研报 |
|------|----------------------|----------------------|---------------------|---------|
| 决策归属 | 人（决策闸） | 偏自动 | 人 | 人 |
| 信号外包 | ❌ 明确拒绝 | ✅ 偏信号 | ❌ | ✅ 外部 |
| 数据依赖 | 公开 CSV 可起步 | 需 API | 手动 | 付费 |
| 形式 | Claude Skills + 工作流 | 代码/代理 | 表格 | 文档 |
| 护城河 | 纪律 SOP 工程化 + 校验 | 策略实现 | 灵活 | 研究深度 |

**选择建议**：要「结构化自己的交易过程、不把判断外包」选本项目；要自动化信号/组合管理选 ai-hedge-fund 类；纯记录用表格即可。

## 🎯 核心研判
- **优势**：把交易纪律做成可复现、可校验、可分发的能力包；人类决策闸 + 无 API 降级路径是稀缺正确定位；工程纪律（索引/校验/兼容矩阵）远超普通个人项目。
- **风险**：① 免费层文档与实测 API 行为脱节（#707/#705），新手易踩；② 偏长线+波段卫星的定位，不适合想全自动/短线者；③ 依赖外部行情 API 的技能在 key 分级变动时脆弱。
- **适用**：时间受限、以长线/ETF/分红为核心、纪律化复盘的个人投资者。**不适用**：全自动交易、信号外包、短线 scalping。
- **趋势**：稳定成长期，路线图清晰（短侧卫星、决策案例共享、双周规则实验），属「方法论工程化」细分里的标杆实践。

## 📂 关键文件路径速查
- `skills-index.yaml` — 全量技能权威元数据（canonical）
- `workflows/` — 运营工作流清单 YAML（canonical，validator 校验）
- `skills/<skill>/SKILL.md` — 各技能主文件（如 market-breadth-analyzer / exposure-coach / position-sizer / trader-memory-core）
- `skillsets/` — 6 个目标导向安装包（market-regime/core-portfolio/...）
- `scripts/validate_metadata_and_workflows.py` — schema + 工作流校验器
- `docs/dev/metadata-and-workflow-schema.md` — schema 规范
- 文档站：https://tradermonty.github.io/claude-trading-skills/ ｜ 配套：hermes-trading-research-agent-work-package
