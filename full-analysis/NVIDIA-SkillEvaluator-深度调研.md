# 🔬 NVIDIA/SkillEvaluator - 全方位深度调研

> 调研日期：2026-11-16 ｜ 数据源：GitHub API（仓库/Issue/Release/源码）+ NVIDIA 官方博客 + 全网口碑检索
> ⚠️ 本报告只写 README 之外的判断。安装与命令清单请直接看官方文档。

## 📌 一句话定位

NVIDIA 开源的 **Agent Skills 三层评测框架**——把「技能（SKILL.md）」当软件来测：Tier 1 静态安全/质量门禁、Tier 2 语义重叠去重、Tier 3 沙箱内的「装/不装技能」配对实测（Skill Lift），是 NVIDIA「Verified Skills」流水线的参考实现，也是 2026-08 一篇 arXiv 论文的配套工具。

一句话点破本质：**大多数工具检查「技能说了什么」，SkillEvaluator 测「技能到底有没有用」**——用同一任务、同模型、同评分器跑两遍（装/不装技能），差值就是贡献。这把它和所有静态 linter 区分开。

## ⭐ 项目亮点

1. **Tier 3「配对实测」直接回答因果问题**：每个 case 在隔离沙箱里跑两次（装技能 vs 不装），唯一变量是技能本身，差值即 **Skill Lift**。这解决了 Agent 领域长期存在的归因难题——「加了这个技能，行为变化到底来自谁」。
2. **三层完全独立可单跑**：Tier 1 无需 API key（quality-check / security-scan / pii-scan），Tier 2 用 embedding 查重（技能内 + 全目录重叠），Tier 3 才需要 LLM + 沙箱。渐进式门槛让团队从「零成本静态检查」起步。
3. **30+ 验证器构成的安全纵深**：validators/ 下有 security / secrets / pii_ownership / similarity / unicode_smuggle（防 Trojan Source CVE-2021-42574）/ url_policy / license / script_lint 等——把「技能供应链安全」做成体系化检查。
4. **NVIDIA 官方实证数据背书**：官方博客公布 300+ 技能 / 30+ 产品 / 2 种 harness 的基准：平均 Correctness +41 分、Effectiveness +39 分；且发现静态分与 LLM 评判相关性仅 Spearman 0.14——**用数据证明「必须跑 live tier，光看质量分没用」**。
5. **生产级工程化**：CI onboarding（GitHub Actions / GitLab CI 模板）、bundle 版本化（0.7.0→0.9.0 每版带 SHA256SUMS + 验证收据）、agent 版本 pin（Codex 0.161.0 / Claude Code 2.1.292）保可复现——把评测当基础设施做。

## 🏗️ 项目架构全景

### 三层架构（tier_workflows.py / tier_group.py 编排）

```
Tier 1  静态门禁    validators/（30+ 验证器）+ SkillSpector/Gitleaks/Semgrep → 结构/安全/质量分
Tier 2  去重         embedding/client + registry → 技能内重复 + 目录间重叠（Findings 四级严重度）
Tier 3  Live 评测    Harbor 框架 + 沙箱（Docker/Daytona/E2B/Modal/Runloop）+ 双 agent → Skill Lift
```

**设计哲学：每条结论都是结构化 Finding + 可复现实验**。Tier 1/2 输出带 severity 的 Finding 对象，Tier 3 输出受控对比的分数差——拒绝「感觉这个技能不错」式的主观评价。

### 目录结构 & 依赖图谱

```
src/skillevaluator/
├── validators/        # 30+ 验证器：security/pii/similarity/unicode_smuggle/... 
├── tier3/             # Harbor runner / native agents / secret_redaction / token_usage /
│                      #   nemo_gym backend / plugin_canary / trajectory_timing ...
├── embedding/         # client / extractor / registry / limits（Tier 2 核心）
├── config/            # license_config.yaml / pii_patterns.yaml
├── cli.py / cli_core.py / tier_group.py / tier_workflows.py   # CLI 与分层编排
ci/                    # 11+ workflow 模板、bundle 版本化、benchmark 发布
skills/skillevaluator/SKILL.md   # 元技能：让 Agent 自然语言就能跑评测
docs/                  # Fern 生成的完整文档站（tier1/2/3 + CI + 自定义 grader）
```

### 技术栈

- Python 3.12–3.14，PyPI 包 `skillevaluator`（extras: llm / security / tier2 / tier3 / all / dashboard）。
- Tier 3 依赖：Harbor（评测框架）+ agent（opencode / codex / claude-code）+ 沙箱后端；支持 NVIDIA Build 端点做免基建原型验证。
- 支持 GitHub Actions 与 GitLab CI（double CI），`ci init` 自动生成检查 changed skills 的 workflow。

## 💡 应用场景与启发（重点章节）

### 典型使用场景

- **技能发布方（DevRel / 平台团队）**：像 database 公司维护 25+ 公开 Claude Code/Codex 技能，用 CI 门禁阻止「结构坏掉 / 泄密」的技能合并，用 Tier 3 证明「这个技能真的提升 agent 表现」。
- **技能市场 / 目录运营**：用 Tier 2 查重，防止几十个近重复技能污染目录、挤占 agent 上下文预算。
- **学术研究**：配套的 arXiv 论文与 benchmark，用于研究「技能 vs agent」的评测方法。

### 可借鉴的解决方案模式（最具迁移价值）

1. **「配对实验」归因法**：`with-skill / without-skill` 双跑，控制其余所有变量，只留一个自变量。这个方法可以迁移到任何「评估某个组件/提示/工具是否真的有用」的场景——**包括你自己的 Agent 工作流迭代**：改了一个 skill，到底变好了没有？跑配对实验，别靠感觉。
2. **渐进式成本门槛**：Tier 1 免费快检 → Tier 2 中等成本查重 → Tier 3 昂贵实测。任何评测/质检体系都可以照此分层，让 80% 的问题在最便宜的层被拦住。
3. **「规范 → gate → CI」闭环**：把质量标准写成可机检的验证器，再自动注入 PR 流程。这是「文档驱动治理」升级为「代码驱动治理」的范本。
4. **安全默认值（secret redaction / 敏感 stdin）**：`tier3/harbor/secret_redaction.py`、`stream_redaction.py`、`sensitive_stdin.py` ——评测过程会碰到真实密钥，项目把它当头等公民处理。任何会接触凭证的工具链都该这么做。
5. **可复现性工程**：pin agent 版本、bundle 带 SHA256SUMS 和验证收据。评估类工具的信任完全建立在「别人能复现你的结果」上。

### 同类需求的可参考思路 / 可复用片段

- `validators/unicode_smuggle.py`：检测不可见 Unicode 字符（Unicode Tag 字符、BiDi override、零宽字符、变体选择器），防提示注入和 Trojan Source。这段代码可直接用于**任何处理外部 Markdown/提示词的管道**——你自己的 skill 加载器也该扫一遍。
- `validators/similarity.py` 的 embedding 查重 + 四级 severity 分类：可用于「重复需求/重复 bug/重复笔记」检测。
- `tier_group.py` 的 Click Group 设计：让 `skillevaluator tier1 <path>` 直接把路径当默认 workflow 参数，又保留 expert 子命令——**CLI 交互设计的巧思**，可做工具时参考。

## 🧠 核心源码解读（克制代码量）

### 关键模块一：TierGroup 的默认路径分发（`src/skillevaluator/tier_group.py`）

```python
def parse_args(self, ctx, args):
    if args and self.workflow is not None:
        first = args[0]
        is_path = first.startswith((".", "~")) or "/" in first or "\\" in first or Path(first).exists()
        if first.startswith("-") or is_path:
            ctx.meta["direct_tier_args"] = args   # 识别为"路径"→走默认 workflow
            return args
    return super().parse_args(ctx, args)
```
**设计解读**：`tier1 ./my-skill` 和 `tier1 --help` / `tier1 validate ./x` 能共存——靠识别「首参数是否为路径/选项」来分流到默认 workflow 还是子命令。这是让 CLI 既简洁又不牺牲扩展性的关键技巧。

### 关键模块二：相似度验证器（`validators/similarity.py`）

```python
class SimilarityValidator(ValidatorBase):
    """Detect duplicate content via embedding similarity.
    Supports all three content types (skill, rules, workflows).
    Produces structured Finding objects classified into four severity tiers."""
    def __init__(self, threshold=SIMILARITY_DEFAULT_THRESHOLD, model=None,
                 catalog_path=None, full_body=False, max_entries=..., ...):
        if not math.isfinite(threshold) or not 0.0 <= threshold <= 1.0:
            raise ValueError("Similarity threshold must be finite and within [0, 1]")
```
**设计解读**：阈值合法性、`--catalog`/废弃 `--cache` 互斥、条目数上限全部在构造期校验——**防御性编程贯穿始终**。查重结果用结构化 Finding + 四级严重度表达，而非简单布尔值，便于 CI 分级处理。

### 关键模块三：Unicode 走私检测（`validators/unicode_smuggle.py`）

```python
_TEXTUAL_MIME_TYPES = frozenset({"application/json", "application/x-sh",
    "application/x-yaml", "image/svg+xml", ...})
class UnicodeSmuggleValidator(ValidatorBase):
    """Detects Unicode Tag chars (U+E0020-U+E007E), BiDi overrides (CVE-2021-42574),
    zero-width steganography, variation selectors — configurable via yaml."""
```
**设计解读**：连「伪装成 svg 的文本」都要扫，说明威胁模型覆盖到「技能资源文件里藏不可见指令」。这是把 Agent Skills 当作**不可信输入**来防御的体现。

### 隐藏特性 & 未文档化细节

- **dual 后端**：Tier 3 除 Harbor 外还接了 `tier3/nemo_gym/backend.py`（NVIDIA NeMo Gym），说明内部有更深的 NVIDIA 生态集成。
- **plugin_canary / mcp_proof**：Tier 3 有插件 canary 与 MCP 证明相关模块——针对「技能声明的工具调用是否真实发生」的验证，是评测严谨性的体现。
- **元技能**：`skills/skillevaluator/SKILL.md` 让 Agent 用自然语言就能跑评测（"Is my skill any good?"），即「评测工具本身也做成了 skill」——自举设计。

## 📐 架构决策与设计哲学

- **support level = Experimental**：README 明确「community, best-effort, no SLA」——NVIDIA 不承诺企业级支持。这对采购决策是关键信息。
- **版本快、破坏性变更真实存在**：0.1.0（2026-08-05）到 0.9.0（2026-11-13）已第 11 版；0.9.0 的 grading 变更**明确声明与旧版分数不可比**。0.9.0 新增 token/judge-call/cost 预算，超时保留部分结果。
- **Issue 暴露的边界**：#603（open）指出文档里的 CI recipe 比仓库自身 workflow 弱（空摘要门禁可通过、action 未 pin、gitleaks 下载未校验）——**「文档示例 vs 自身实践」的差距**是快速迭代项目的典型债。

## 🌐 全网口碑画像

### 好评共识

- ReviewRamble 给 4.0/5：「问了大多数技能扫描器跳过的问题——技能到底有没有帮到 agent」，并认可 cheap path（Tier 1 无需 key/GPU/Docker）。
- NVIDIA 官方博客给出硬数据：300+ 技能、Correctness +41 / Effectiveness +39 平均提升；jetson-optimize-memory 技能省 76.9% token。
- explainx / dosa.dev 肯定「把技能当被测软件、三层 gate 可进 CI」的定位，称其为 ACES 研究结论（文档扫描与运行时提升弱相关）的**工具化落地**。

### 差评共识 & 踩坑高发区

- **论文数据比博客克制得多**：arXiv 论文覆盖 58/64 生产技能、947 个配对 case、4 种 harness，平均 composite lift 仅 **0.2134**，72.8% 的 case 为正——远没有博客「+41 分」那么惊艳。博客快照 85% 技能每任务只跑一次、无置信区间。
- **静态分几乎不能信**：论文发现静态评分与 LLM judge 评分 Spearman 仅 0.14——这是「必须跑 Tier 3」的最强论据，也是对项目自身 Tier 1 价值的诚实限定。
- **成本与门槛**：Tier 3 需要 Docker/托管沙箱 + agent 与 judge 双 provider key，成本按 case×agent×attempt×arm 增长；文档拒绝对美元报价。
- **版本 churn**：0.9.0 分数与旧版不可比；pin 的 agent 版本（Claude Code 2.1.292 等）不是你团队今天在用的 CLI——**可复现性 vs 时效性的张力**。
- **反向效果真实存在**：技能在不相关的任务上加载会让 agent 变差；cuopt-install 技能让 token 增加 120.3%。

### 争议焦点

- **「博客营销数字 vs 论文诚实数字」**的落差，被 ReviewRamble 等第三方明确点出——采用者应以论文和自己的配对实测为准。
- 定位边界：适合「发布技能给别人的团队」，对个人少量技能「Tier 1 或 SkillSpector 就够了」（ReviewRamble 判断）。

### 维护者响应风格

- Issue ~25 个（多为 CI/文档硬化类，如 #603），Release 平均每 1–2 周一版，节奏快。
- 最近的提交仍在换默认 judge 模型（#608，Claude Opus 5.5）——紧跟模型演进。

## ⚔️ 竞品对比

| 维度 | SkillEvaluator | SkillSpector（NVIDIA 内置扫描器） | 通用 LLM Eval（如promptfoo/DeepEval） | ACES 论文基准 |
|------|----------------|-----------------------------------|----------------------------------------|---------------|
| 定位 | 技能三层评测（含 live lift） | 静态安全扫描器 | 通用 LLM 应用评测 | 学术研究基准 |
| Live 配对实测 | **核心能力** | 无 | 部分 | 有（研究性质） |
| 查重 | Tier 2 embedding | 无 | 少见 | 无 |
| CI 集成 | GitHub/GitLab 模板 | 作为 Tier1 组件 | 各异 | 无 |
| 成熟度 | Experimental，快速迭代 | 更稳定 | 生态成熟 | 论文一次性 |

**选择建议**：发布/维护公开技能 → SkillEvaluator（Tier1 起步，重要技能上 Tier3）；只要静态安全扫描 → SkillSpector 更轻；评 LLM 应用整体质量 → 通用 eval 框架；做学术研究 → ACES/SkillEvaluator 论文。**注意 SkillSpector 是 SkillEvaluator Tier 1 的内置组件，二者是包含关系而非替代。**

## 🎯 核心研判

### 项目优势（不可替代的价值点）

- **唯一把「Skill Lift 配对实测」产品化并开源的方案**：从归因角度解决了「技能有没有用」这个根本问题，且有 NVIDIA 30+ 产品的真实基准支撑。
- **安全纵深 + 可复现工程**：30+ 验证器、secret redaction、版本 pin、bundle 校验收据——工程严谨度远超一般开源评测工具。
- **渐进式门槛 + CI 原生**：Tier1 零成本起步，能直接进 PR 门禁。

### 项目风险（潜在隐患和局限性）

- **Experimental / no SLA**：产品化承诺弱，版本 churn 快，分数跨版本不可比。
- **成本与复杂度**：Tier3 的沙箱 + 双 provider key + 矩阵式成本，对个人和小团队过重。
- **数字需折扣看待**：官方博客 +41 分与论文 0.2134 lift 的落差提醒——**不要拿营销数字做采购依据**。
- **自身债**：文档 CI recipe 弱于自身 workflow（#603）、grading 破坏性变更——快速迭代的代价。

### 适用场景 & 不适用场景

- ✅ 适用：维护公开技能目录的 DevRel/平台团队、技能进入生产前的门禁、技能效果归因研究。
- ❌ 不适用：通用 LLM 应用评测、需要厂商 SLA 的企业、个人少量技能的轻量检查（Tier1 或 SkillSpector 即可）。

### 趋势判断

**快速上升期**：11 月内连发 5 版、上 trending，踩中「Agent Skills 质量治理」刚需。真正的问题是它能否从「NVIDIA 内部工具开源」成长为「跨厂商的技能评测标准」——Partner pilot（OpenClaw/ClawHub、Nous Research/Hermes）是积极信号，但 Experimental 定位和激烈 churn 仍是障碍。**建议：把它当「技能评测方法论的参考实现」学习配对实验与分层门禁；团队采用时以论文数据为准、锁定版本、从 Tier1 渐进。**

## 📂 关键文件路径速查

| 文件 | 作用 |
|------|------|
| `skills/skillevaluator/SKILL.md` | 元技能：自然语言驱动评测，含 Tier 选择表与前置条件 |
| `src/skillevaluator/tier_group.py` | 路径/子命令分流的 CLI 编排技巧 |
| `src/skillevaluator/validators/similarity.py` | Tier2 embedding 查重 + 四级 Finding |
| `src/skillevaluator/validators/unicode_smuggle.py` | 不可见 Unicode / Trojan Source 检测 |
| `src/skillevaluator/tier3/harbor/secret_redaction.py` | Tier3 密钥脱敏（安全默认值样本） |
| `docs/tier3-live-evaluation.mdx` | 配对实测（Skill Lift）方法论文档 |
| `config/pii_patterns.yaml` / `license_config.yaml` | PII 与许可证检查规则 |
| `ci/bundles/0.9.0/` | 版本化 CI bundle（SHA256SUMS + 验证收据） |
