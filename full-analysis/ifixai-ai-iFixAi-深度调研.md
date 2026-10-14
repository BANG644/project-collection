# ifixai-ai/iFixAi — 深度调研

> 调研日期：2026-10-15 ｜ 星标：27,103 ⭐ ｜ 语言：Python（3.10+）｜ 协议：Apache-2.0 ｜ 默认分支：main ｜ 创建：2026-04-27 ｜ 主页：ifixai.ai ｜ 包：PyPI `ifixai`

## 1. 项目定位（一句话）
**AI Agent 的独立审计（Independent Auditing）工具**：在 agent 出事之前，抓住它的失误与盲区——把"AI 红队（Red-Teaming）"与"运营保障（Operational Assurance）"做平衡，用 <120 秒回答最要命的问题：**这个 agent 到底有没有按业务 KPI 和组织结构干它该干的事？**

> 差异化锚点：市面上的 Eval / 红队 / 可观测工具大多只评"技术能力"（token 效率、延迟、prompt injection 抗性），iFixAi 评的是**业务对齐度与组织约束遵守度**。

## 2. 项目亮点（差异化，开篇呈现）
- **60 项检查（Inspections）**：32 项核心检查横跨 5 大支柱（Fabrication / Manipulation / Deception / Containment / Alignment），28 项 premium-preview 仅报告不计入评分；全部 Apache-2.0。
- **强制最低线（Mandatory Minimum）**：`B01`（工具调用治理）、`B08`（权限提升检测）、`P01`（某关键项）任一失败，整体评级封顶 **60%**——把"安全底线"做成硬约束而非软建议。
- **三种运行形态同源**：①CLI 引导向导（`ifixai setup`→`ifixai run`，配置落 `ifixai.yaml`）；②显式 flag（CI/自动化）；③Plugin/Skill（Claude Code、Codex 原生安装，agent 自驱）。底层跑同一套诊断引擎。
- **多评审裁判（Multi-judge Ensemble）**：自评 + 独立厂商评审 + 多裁判集成，评分可溯源；`ifixai.yaml` 只存环境变量名、**绝不存密钥本身**。
- **真实落地证据**：`case_studies/` 含 AISI cyber-range containment、Meta Instagram support、OpenAI HuggingFace containment、Pizza Hut Dragontail 四份真实 SCORECARD；ProductHunt + Trendshift「本周 #1 Python 仓库」；9 语言 README（含简体中文）。

## 3. 核心架构
```
ifixai/
├── core/            # 编排与治理内核
│   ├── runner.py          # EvaluationPipeline 驱动，并发治理
│   ├── concurrency.py     # ConcurrencyGovernor（并发闸门）
│   ├── governance_synthesis.py  # 治理综合
│   ├── grounding.py / refusal.py / context.py
│   ├── fixture_loader.py  # 测试夹具加载
│   └── training_specification_screening.py
├── evaluation/      # 评测管线与裁判
│   ├── pipeline.py        # EvaluationPipeline
│   └── analytic_judge.py  # AnalyticRubricJudge / EnsembleAnalyticRubricJudge
├── harness/         # 运行宿主与套件
│   ├── suites.py          # 套件（smoke/strategic/essential/core/extended/all）
│   ├── registry.py        # ALL_SPECS / INSPECTION_REGISTRY
│   └── consistency.py     # CrossHookValidator（跨钩子一致性）
├── judge/           # 裁判配置与执行
│   ├── config.py / evaluator.py   # JudgeEvaluator / EnsembleJudgeEvaluator
├── providers/       # LLM 提供商抽象（base.py ChatProvider + detect_capabilities）
├── reporting/       # 评分卡 / 缺口分析 / 评级
│   ├── grading.py (score_to_grade) / scorecard.py / gap_analysis.py
├── scoring/         # 评分引擎
│   ├── category_weights.py  # DEFAULT / GRADED / STRATEGIC_TEST_IDS
│   └── engine.py           # compute_category_score
└── inspections/     # 60 项检查，每项一个目录
    └── b01_tool_governance/  # definition.yaml + runner.py (+ references.yaml/rubric.yaml)
        b02_non_llm_layer/ b03_auditability/ … b30_malicious_deployer_rules/
```
检查项以「`definition.yaml` + `runner.py` +（可选 `references.yaml`/`rubric.yaml`）」三元组声明，注册进 `INSPECTION_REGISTRY`，由 `harness/suites.py` 按套件组合调度——**插件化检查是可扩展架构的关键**。

## 4. 应用场景与启发
- **Agent 上线前的"安全/合规体检"**：对用户这种重度依赖多 agent 工作流（paper-companion、错题归因、灵感闪记等）的人，iFixAi 是现成的「agent QA 闸门」——在 agent 接真实业务前，先用 60 项检查卡一遍权限越界/幻觉/静默失败。
- **Policy Lab 的"最短有害动作链"思路可借鉴**：`docs/business-policy-lab.md` 自动找出"被允许动作"构成的最短有害序列，并对权限修复做合法性校验——这套"组合动作越权检测"范式，正好可补到错题归因链路的「归因结果可信度」一道闸。
- **可迁移的评分卡范式**：A–F 评级 + 强制最低线封顶 + 多裁判集成 + 不存密钥只存变量名——是一套可直接抄的"AI 治理评测"工程样板。

## 5. 源码深度解读
`ifixai/core/runner.py` 的 import 揭示了评测主链路：

```python
from ifixai.evaluation.pipeline import EvaluationPipeline
from ifixai.evaluation.analytic_judge import (
    AnalyticRubricJudge, EnsembleAnalyticRubricJudge)
from ifixai.harness.consistency import CrossHookValidator
from ifixai.harness.registry import ALL_SPECS, INSPECTION_REGISTRY
from ifixai.judge.evaluator import EnsembleJudgeEvaluator, JudgeEvaluator
from ifixai.reporting.grading import score_to_grade
from ifixai.scoring.engine import compute_category_score
```
即：**注册表拉全量检查 → EvaluationPipeline 并发执行 → AnalyticRubricJudge 逐条打分 → Ensemble 多裁判集成 → compute_category_score 加权 → score_to_grade 出 A–F**。

`docs/inspections.md` 把 60 项检查按 5 支柱分表，每项四字段（测什么 / 怎么测 / 为何重要 / 强制最低线），结果只有 `pass / fail / inconclusive / error` 四态——**把"agent 是否守规矩"做成可审计、可分级的清单**，而非模糊的"感觉它不可靠"。

## 6. 社区口碑
- 2026-04 创建，2026-10 冲上 GitHub Trending 日榜（日增 2,143⭐），Trendshift「本周 #1 Python 仓库」、ProductHunt 上榜；PyPI 已发布、9 语言文档、含 4 份真实 SCORECARD 案例——**增长快但项目仍年轻**，生态（第三方检查插件）尚未规模化。
- 缺点：需指向被测对象（SUT）并自备 API key；评分为启发式（非形式化证明）；28 项 premium 检查需 `--suite extended/all` 才跑。

## 7. 竞品对比 + 核心研判
| 维度 | iFixAi | LangSmith/Helicone（可观测） | PyRIT/Garak（红队） | AgentOps（可观测） |
|---|---|---|---|---|
| 评测焦点 | 业务 KPI / 组织约束对齐 | trace / token / 延迟 | prompt injection / 安全隐患 | agent 行为追踪 |
| 评分产出 | A–F + 强制最低线 | 指标面板 | 漏洞报告 | 会话回放 |
| 多裁判 | ✅ Ensemble | ❌ | 部分 | ❌ |
| 自托管 | ❌(SaaS/PyPI) | ❌ | ✅ | ❌ |

**研判**：iFixAi 卡位"**agent 治理层**"而非"能力评测层"，在 agent 大量进入生产的当下是清晰刚需。对用户的价值是「上线前体检 + 组合动作越权检测范式」。注意它只是启发式审计、不是安全保证，且商业/私有部署需看其 Pro 层条款。

## 8. 关键文件路径速查
- `ifixai/core/runner.py` — 评测主链路编排（必读）
- `ifixai/harness/registry.py` — 检查注册表（`ALL_SPECS` / `INSPECTION_REGISTRY`）
- `ifixai/inspections/` — 60 项检查（每项 `definition.yaml` + `runner.py`）
- `ifixai/scoring/engine.py` · `category_weights.py` — 评分引擎与权重
- `docs/inspections.md` · `docs/trajectory-assurance.md` · `docs/business-policy-lab.md` — 检查目录 / 轨迹审计 / 策略实验
- `case_studies/*/SCORECARD.md` — 4 份真实审计样例
- `pyproject.toml` · `ifixai.yaml`（运行配置，只存变量名不存密钥）
