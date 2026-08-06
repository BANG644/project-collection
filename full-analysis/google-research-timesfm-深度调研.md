# 🔬 google-research/timesfm — 全方位深度调研

> 调研日期：2026-08-07 ｜ 仓库：https://github.com/google-research/timesfm
> 本次为**重写升级**（原报告文件名异常 `github.com-google-research-深度调研.md`，星标严重失真「7.5K+」→ 实测 **27,248**，缺口碑/研判/源码三大维度）

---

## 📌 一句话定位

**Google Research 的时序预测基础模型：一个 200M 参数的 decoder-only Transformer，零样本吃任意时间序列，直接吐点预测 + 分位数区间，不用再为每条序列单独训一个 Prophet/ARIMA/LightGBM。**

---

## ⭐ 项目亮点（README 之外的判断）

1. **⚠️ 星标数据必须校正**：旧报告写「7.5K+」，实测 **27,248⭐ / 2,642 forks**。第三方评测（dev.to，2026 年）记录其「25.4K stars，本周 +4.4K，GitHub 趋势榜首」——这是一次爆发式增长，旧数据落后了一个数量级级别的认知。
2. **2.5 版是「反规模化」的**：参数 **500M → 200M（砍 60%）**，上下文 **2,048 → 16,384（涨 8 倍）**，还**删掉了 frequency indicator**（用户不再需要手工声明数据粒度）。小模型 + 长上下文 + 免配置，三件事同时做到。
3. **仓库自带 Agent Skill**：`timesfm-forecasting/SKILL.md` + `AGENTS.md`，让 Claude Code / Codex / OpenClaw 可以把 TimesFM 当工具直接调用。这是**由社区贡献者 @borealBytes 推动**（issue #369，2026-03），Google 官方合并——罕见的「大厂模型仓库主动 Agent 化」案例。
4. **⚠️ 榜单地位已被反超（README 不会告诉你）**：2.5 发布时在 GIFT-Eval 零样本基础模型类别排名第一（MASE 0.705 / CRPS 0.49，同期 Moirai 2.0 为 0.728、IBM FlowState 0.726）。但 **Amazon Chronos-2（120M）随后在 GIFT-Eval 和 FEV Bench 上双双超越**；截至 2026 年初 tsfm.ai 榜单显示 TimesFM 系列 Average Rank ≈ **8.70（约第 9 位）**。
5. **核心架构是「框架无关配置 + 双后端实现」**：`configs.py` 用 frozen dataclass 定义与框架无关的层配置，`flax/` 和 `torch/` 各自实现同一套 dense/normalization/transformer——这是想同时吃 JAX/TPU 和 PyTorch/GPU 生态的工程解法。

---

## 🏗️ 项目全景

| 维度 | 数据（2026-08-07 实时核验） |
|------|------|
| 仓库 | google-research/timesfm |
| Stars | **27,248** ⭐（旧报告 7.5K+，严重失真） |
| Forks | 2,642 |
| 主语言 | Python |
| 许可证 | **Apache-2.0** |
| 创建 | 2024-04-29 |
| 最近推送 | 2026-07-14 |
| Open Issues | 220 |
| 默认分支 | **`master`**（非 main，clone 时注意） |
| 仓库文件数 | 103 个 blob（**极精简**，与 27k 星标形成反差） |
| 最新 PyPI | `timesfm==2.0.2`（2026-07-02） |
| 最新模型 | **TimesFM 2.5**（200M，2025-09 发布） |
| 论文 | arXiv:2310.10688，ICML 2024 |

> **重要免责**：README 明确写着 *"This open version is not an officially supported Google product."* —— 生产上线不要指望 Google 支持 SLA。

### 目录结构（全仓库仅 103 文件，一眼看完）

```
src/timesfm/
├── configs.py                    ← 框架无关的配置（本仓库的架构枢纽）
├── flax/     {dense,normalization,transformer,util}.py
├── torch/    {dense,normalization,transformer,util}.py
├── timesfm_2p5/  {base, flax, torch}.py     ← 2.5 模型三件套
└── utils/xreg_lib.py             ← 协变量（外生回归）支持

timesfm-forecasting/              ← Agent Skill（第一方）
├── SKILL.md
├── references/{api_reference, data_preparation, system_requirements}.md
├── scripts/{check_system.py, forecast_csv.py}
└── examples/{anomaly-detection, covariates-forecasting, finetuning, global-temperature}/

v1/                               ← 1.0/2.0 归档代码（pip install timesfm==1.3.0）
tests/  AGENTS.md  pyproject.toml
```

---

## 🧠 核心架构

### 设计枢纽：`src/timesfm/configs.py`

整个仓库最值得读的一个文件。它用 **frozen dataclass** 把「模型结构」与「实现框架」彻底解耦：

```python
@dataclasses.dataclass(frozen=True)
class TransformerConfig:
  model_dims: int
  hidden_dims: int
  num_heads: int
  attention_norm: Literal["rms"]
  feedforward_norm: Literal["rms"]
  qk_norm: Literal["rms", "none"]
  use_bias: bool
  use_rotary_position_embeddings: bool
```

`flax/transformer.py` 和 `torch/transformer.py` 各自消费同一个 config。**结论：想加一个新后端（比如 MLX），只需实现一层，不碰配置与调用侧。**

### 真正体现产品思考的是 `ForecastConfig`

```python
@dataclasses.dataclass(frozen=True)
class ForecastConfig:
  max_context: int = 0
  max_horizon: int = 0
  normalize_inputs: bool = False
  per_core_batch_size: int = 1
  use_continuous_quantile_head: bool = False
  force_flip_invariance: bool = True      # 默认开
  infer_is_positive: bool = True          # 默认开
  fix_quantile_crossing: bool = False
  return_backcast: bool = False
```

这几个 flag 是**对真实业务痛点的直接回应**，源码 docstring 写得很清楚：

| flag | 解决什么现实问题 |
|---|---|
| `force_flip_invariance` | 模型默认保证 `TimesFM(aX+b) = a·TimesFM(x)+b`（a≥0）；此 flag **把不变性扩展到 a<0**，即对翻转序列也稳定 |
| `infer_is_positive` | 输入非负则**保证输出非负**——避免「预测销量出现负数」这类经典事故 |
| `fix_quantile_crossing` | 修分位数交叉（P90 < P50 的荒谬输出） |
| `use_continuous_quantile_head` | 用独立连续分位数头，**避免 quantile collapsing** |
| `normalize_inputs` | 输入量级极大/极小时的数值稳定性 |

**这是本仓库最值得抄的东西**：不是模型结构，而是「把预测的常见病做成可开关的 flag」这个产品化思路。任何自研预测服务都该有一层这样的后处理开关，而不是让调用方自己 monkey-patch 输出。

### 20 行完成一次零样本预测

```python
import timesfm
model = timesfm.TimesFM_2p5_200M_torch.from_pretrained("google/timesfm-2.5-200m-pytorch")
model.compile(timesfm.ForecastConfig(
    max_context=1024, max_horizon=256,
    normalize_inputs=True, use_continuous_quantile_head=True,
    force_flip_invariance=True, infer_is_positive=True, fix_quantile_crossing=True))
point, quantiles = model.forecast(horizon=12, inputs=[series_a, series_b])
# point: (2, 12)   quantiles: (2, 12, 10)  ← mean + P10~P90
```

无训练、无拟合、无每序列建模。

---

## 💡 应用场景与启发

### 什么时候该来翻这个仓库

| 你的处境 | 来这里找什么 |
|---|---|
| 「每来一个新业务线就要重训一套预测模型」 | 零样本能力本身——这正是它要终结的循环 |
| 「预测结果偶尔出现负数 / 分位数交叉，被业务方投诉」 | `ForecastConfig` 那几个 flag 的设计思路（可直接照抄进自研服务） |
| 「要给 AI Agent 加时序预测能力」 | `timesfm-forecasting/SKILL.md` —— 现成的第一方 Agent Skill |
| 「要在 SQL 里做预测，不想搭 Python 服务」 | BigQuery ML `AI.FORECAST`、Connected Sheets、Vertex Model Garden 三个 Google 1P 落地面 |
| 「需要加价格/天气/促销等外部变量」 | `utils/xreg_lib.py` + `examples/covariates-forecasting/` |
| 「要做异常检测而非纯预测」 | `examples/anomaly-detection/detect_anomalies.py`（用预测残差做异常判定） |
| 「想在自己领域微调」 | `examples/finetuning/finetune_lora.py`（HF Transformers + PEFT LoRA） |
| 「要设计一个支持多后端的模型库」 | `configs.py` 的 frozen dataclass 解耦范式 |

### 三条可迁移的方法论

1. **「配置与实现解耦」**：frozen dataclass 描述结构，各框架实现层各自消费。这个模式适用于任何要同时支持多个运行时的库。
2. **「把领域坑做成默认开的 flag」**：`infer_is_positive` 默认 `True`。好的库替用户挡掉常识性错误，而不是写在文档里让用户自己注意。
3. **「大厂模型仓库主动 Agent 化」**：加一个 `AGENTS.md` + `SKILL.md`，模型立刻从「库」变成「Agent 可调用的能力」。成本极低，分发收益极大——这是所有模型/工具类仓库都该抄的动作。

---

## 🔍 源码解读补充：`timesfm-forecasting/` 这个 Skill 值得单独说

它不是敷衍的一个 md，而是完整的 Skill 工程：

```
SKILL.md
references/api_reference.md          ← 给 Agent 看的 API 手册
references/data_preparation.md       ← 数据准备规范
references/system_requirements.md    ← 环境前置检查说明
scripts/check_system.py              ← Agent 可先跑环境自检
scripts/forecast_csv.py              ← 一条命令预测 CSV
examples/global-temperature/         ← 完整端到端 demo：
    run_forecast.py → visualize_forecast.py → generate_gif.py / generate_html.py
    output/{forecast_output.csv, forecast_animation.gif, interactive_forecast.html}
```

**设计亮点**：`scripts/check_system.py` 让 Agent 在动手前先验环境——这是对「Agent 遇到依赖问题会瞎试」这一现实缺陷的针对性防御。`references/` 三件套则把「Agent 需要知道但不该塞进主 SKILL.md」的内容外置，控制上下文膨胀。**任何要写 Agent Skill 的人都该照这个结构抄。**

---

## 🌐 全网口碑

| 来源 | 观点 |
|------|------|
| **Issue #1「Installation conflict (praxis / lingvo)」，48 条评论** | 全仓库讨论最热的 issue，且**至今 open**。早期版本依赖 praxis/lingvo 导致装不上是历史第一大痛点；2.5 已重写不再依赖，但 issue 仍挂着，成为该项目安装体验的历史注脚 |
| Issue #404（open，10 评论） | 社区 PR：修 `torch.compile`、`strip_leading_nans`、`linear_interpolation` bug，向量化 running stats，补测试与 CI —— **说明 2.5 的 PyTorch 路径仍有真实 bug 在被社区修** |
| Issue #369（closed，10 评论） | 社区提议并交付第一方 Agent Skill；README 专门致谢 @borealBytes |
| Issue #104 / #143 / #13 | LoRA/DoRA PEFT 微调、torch 迁移、`patched_decoder` ImportError —— 早期版本迁移阵痛集中营 |
| dev.to 评测（andrew.ooo） | 「如果你还在为每个预测问题手搓 Prophet / ARIMA / per-series LightGBM，TimesFM 就是终结这个循环的东西」；记录 25.4K⭐、周涨 4.4K、GitHub 趋势榜首 |
| chooseai 中文报道 | **点破 README 的水分**：Google 官方博客称零样本「接近或超越」监督模型，但**该说法主要基于 v1.0 论文实验，v2.5 并未发布新论文提供对比数据** |
| paperswithbacktest（金融向对比） | 明确场景化推荐：单只股票日频 → TimesFM 2.5（快、有 BigQuery 集成）；多资产相关组合 → MOIRAI-2（any-variate attention）；概率风险区间 → Chronos-2；CPU-only → Chronos-Bolt。并引 Marconi et al.(2025)：预训练模型少用 3–10 年数据即可达到同等精度，**但三项金融任务中传统专用模型仍在两项持平或胜出** |
| GIFT-Eval 基准分析（emergentmind） | 基础模型在**低频、单变量、强季节性**场景全面胜出；但**高频、噪声大、多变量**场景下 PatchTST / iTransformer 等专用深度模型或统计集成仍更强 |

**口碑综合判断**：技术认可度极高，但**「零样本 SOTA」的光环已在 2026 年褪色**。它的真实定位是「最容易上手、有 Google 全家桶集成加持的强基线」，而非「当前最准」。

---

## ⚔️ 竞品对比

| 维度 | **TimesFM 2.5** | Amazon Chronos-2 | Salesforce MOIRAI-2 | IBM Granite TS / FlowState | 传统（Prophet/ARIMA/LightGBM） |
|---|---|---|---|---|---|
| 参数量 | 200M | 120M（另有 9M–710M 系列） | MoE 架构 | 小 | — |
| 架构 | decoder-only + **连续 patch embedding** | **tokenize 量化 + encoder-only(T5 系)** | decoder-only + **MoE + any-variate attention** | — | — |
| 上下文 | **16k（最长）** | — | — | — | — |
| 多变量 | ✗（本质单变量，靠 XReg 加协变量） | ✅ 原生多变量 + 未来协变量 | ✅ 任意变量数 | — | 需手工 |
| 概率预测 | 可选 30M 分位数头 | **原生（token 分布）** | 分位数回归 + 多 token 预测 | — | 部分 |
| GIFT-Eval | 发布时零样本第一（MASE 0.705）；**2026 初 Avg Rank ≈8.70（~第9）** | **开源榜第一，总榜第四** | 强于相关多资产 | 竞争者 | 基线 |
| 预训练规模 | 1000 亿时间点（Google Trends + Wikipedia + 合成） | — | 270 亿观测（LOTSA，9 领域） | — | — |
| 企业集成 | **BigQuery ML / Connected Sheets / Vertex Model Garden** | AWS 生态 | — | IBM 生态 | 无 |
| Agent Skill | ✅ 第一方 SKILL.md + AGENTS.md | ✗ | ✗ | ✗ | ✗ |
| 许可证 | Apache-2.0 | Apache-2.0 | — | — | 各异 |

**决策速查**：
- 已在 GCP / BigQuery 上 → **TimesFM**（SQL 一行 `AI.FORECAST`，集成成本最低）
- 要多变量 + 未来已知协变量（促销日历、定价计划）→ **Chronos-2**
- 多资产相关性建模 → **MOIRAI-2**
- CPU-only、要吞吐 → **Chronos-Bolt (9M)**
- 高频噪声数据、且有充足历史 → **别用基础模型**，PatchTST / 统计集成更稳

---

## 🎯 核心研判

### 优势
- **上手成本极低**：`pip install timesfm[torch]` + 20 行代码 = 可用预测。无训练、无调参。
- **16k 上下文是实打实的差异化**：可以直接喂几年的小时级数据，让模型自己挑相关部分。
- **产品化 flag 设计成熟**：负值/分位数交叉/量级异常等常见事故被默认挡掉。
- **Google 1P 三面落地**：BigQuery ML、Connected Sheets、Vertex Model Garden——对已在 GCP 的团队，这是最短路径。
- **仓库精简（103 文件）**：源码可通读，不是黑箱。
- **主动 Agent 化**：第一方 SKILL.md 让它能直接进 Agent 工具箱。

### 风险 / 局限
1. **「SOTA」标签已过期**：Chronos-2 已在 GIFT-Eval / FEV Bench 双双反超；tsfm.ai Avg Rank 约第 9。引用「零样本第一」时务必标注是 2025-09 发布时的快照。
2. **README 存在有利化表述**：「接近或超越监督模型」的依据来自 v1.0 论文，**2.5 未发新论文提供对比数据**。
3. **本质单变量**：多变量只能靠 XReg 外挂，原生多变量能力弱于 Chronos-2 / MOIRAI-2。
4. **无官方支持**：README 白纸黑字 *"not an officially supported Google product"*。220 个 open issue 也印证响应有限。
5. **金融等噪声领域慎用**：多项研究表明现成 TSFM 在金融数据上跑不赢领域内预训练/专用模型。
6. **默认分支是 `master`**：自动化脚本里写死 `main` 会直接失败（本次调研即踩到）。

### 适用 / 不适用
- ✅ **适用**：需要覆盖大量异构序列且不想逐条建模的场景（运维监控、多品类销量、能源负荷）；已在 GCP/BigQuery 的团队；需要快速拿到一条强基线来对比自研模型；给 Agent 加预测能力。
- ❌ **不适用**：高频金融交易预测（专用模型更优）；强多变量耦合场景（选 Chronos-2/MOIRAI-2）；需要厂商 SLA 支持的生产核心链路；数据量小且领域特殊（不如小模型精调）。

### 一句话结论
**它不再是「最准的那个」，但仍是「最省事的那个」——把它当作零成本的强基线和 GCP 生态的默认选项，而不是终局方案；真要压精度，先花半天把 Chronos-2 也跑一遍再决定。**

---

## 📂 关键文件路径速查

| 想看什么 | 路径 |
|---------|------|
| **架构枢纽**（框架无关配置） | `src/timesfm/configs.py` |
| 预测行为开关（最值得抄） | `src/timesfm/configs.py::ForecastConfig` |
| 2.5 模型实现 | `src/timesfm/timesfm_2p5/{timesfm_2p5_base, _flax, _torch}.py` |
| Flax/JAX 后端 | `src/timesfm/flax/{dense,normalization,transformer,util}.py` |
| PyTorch 后端 | `src/timesfm/torch/{dense,normalization,transformer,util}.py` |
| 协变量（外生变量）支持 | `src/timesfm/utils/xreg_lib.py` |
| **Agent Skill 主文件** | `timesfm-forecasting/SKILL.md` |
| Agent 环境自检脚本 | `timesfm-forecasting/scripts/check_system.py` |
| CSV 一键预测 | `timesfm-forecasting/scripts/forecast_csv.py` |
| Agent 参考文档三件套 | `timesfm-forecasting/references/{api_reference,data_preparation,system_requirements}.md` |
| LoRA 微调示例 | `timesfm-forecasting/examples/finetuning/finetune_lora.py` |
| 异常检测示例 | `timesfm-forecasting/examples/anomaly-detection/detect_anomalies.py` |
| 协变量预测示例 | `timesfm-forecasting/examples/covariates-forecasting/demo_covariates.py` |
| 端到端完整 demo | `timesfm-forecasting/examples/global-temperature/` |
| Agent 入口约定 | `AGENTS.md` |
| 1.0/2.0 归档代码 | `v1/`（`pip install timesfm==1.3.0`） |
| 单元测试 | `tests/` |

---

## 🔗 参考

- 仓库：https://github.com/google-research/timesfm （默认分支 `master`）
- 论文：https://arxiv.org/abs/2310.10688 （ICML 2024）
- 权重集合：https://huggingface.co/collections/google/timesfm-release-66e4be5fdb56e960c1e482a6
- Google Research 博客：https://research.google/blog/a-decoder-only-foundation-model-for-time-series-forecasting/
- BigQuery ML 集成：https://cloud.google.com/bigquery/docs/timesfm-model
- 第三方评测：https://dev.to/andrew-ooo/timesfm-25-review-googles-time-series-foundation-model-14kp
- 榜单反超报道：https://www.chooseai.net/news/3258
- 金融向三模型对比：https://paperswithbacktest.com/wiki/timesfm-vs-chronos-vs-moirai
- GIFT-Eval 基准：https://www.emergentmind.com/topics/gift-eval
