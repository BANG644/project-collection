# 📈 Kronos — 金融市场「语言」的基础模型

> **仓库**: [shiyu-coder/Kronos](https://github.com/shiyu-coder/Kronos)
> **Stars**: 32,536⭐ | **Forks**: 5,591 | **今日新增**: 数据不可用（Trending 当日上榜）
> **语言**: Python | **许可证**: MIT
> **论文**: arXiv:2508.02739 (AAAI 2026 接收) | **Demo**: [BTC/USDT 24h 预测](https://shiyu-coder.github.io/Kronos-demo/)

## 一、项目全景

Kronos 是**首个开源的金融 K 线（Candlestick）基础模型**——把金融市场的「K 线序列」视为一种自然语言，用训练大语言模型的离散 token + 自回归范式来做金融时序预测。预训练数据覆盖 **45+ 全球交易所**（股票、加密、外汇、期货），论文被 AAAI 2026 接收。

**项目亮点**：
- 🚩 首个开源金融 K 线 foundation model，把「K 线即语言」的方法论工程化落地
- 🪜 模型族覆盖 4.1M → 499.2M 参数，mini 仅 24.7M 即可在笔记本跑推理
- 🔓 全开源：模型权重（HuggingFace NeoQuasar）+ 微调脚本 + 在线 Demo + MIT 协议
- 🧪 两阶段架构（专用 tokenizer 量化 + 自回归 Transformer）天然处理金融数据高噪声

## 二、核心架构

Kronos 采用 **decoder-only 基础模型系列** + 新颖的两阶段框架：

```
连续 OHLCV 多维序列
       │
       ▼
[阶段1] Kronos-Tokenizer：Binary Spherical Quantization (BSQ)
       将连续数值 → 分层离散 token（coarse/fine subtoken）
       │
       ▼
[阶段2] 自回归 Transformer (decoder-only, causal mask)
       在 token 序列上预训练，统一服务多种量化任务
       │
       ▼
采样生成 → 反量化 → 预测 OHLCV 序列
```

**模型族（HuggingFace NeoQuasar）**：

| 模型 | Tokenizer | 上下文 | 参数量 | 开源 |
|------|-----------|--------|--------|------|
| Kronos-mini | Kronos-Tokenizer-2k | 2048 | 4.1M | ✅ |
| Kronos-small | Kronos-Tokenizer-base | 512 | 24.7M | ✅ |
| Kronos-base | Kronos-Tokenizer-base | 512 | 102.3M | ✅ |
| Kronos-large | Kronos-Tokenizer-base | 512 | 499.2M | ❌ 未公开 |

关键设计：tokenizer 量化把「具体价格数值」转为「K 线形态语义」，使模型学到的是形态而非数值，泛化能力显著强于直接回归；论文实验报告 **22% 合成 K 线保真度提升**。

## 三、源码深度解读

仓库结构清晰，核心推理 + 微调 + 示例分层：

**1. 模型定义（`model/kronos.py`）**
暴露三个核心类，是用户唯一需要 import 的入口：
```python
from model import Kronos, KronosTokenizer, KronosPredictor
tokenizer = KronosTokenizer.from_pretrained("NeoQuasar/Kronos-Tokenizer-base")
model = Kronos.from_pretrained("NeoQuasar/Kronos-small")
predictor = KronosPredictor(model, tokenizer, max_context=512)
```
`KronosPredictor` 封装了数据预处理 → 归一化 → 预测 → 反归一化的完整闭环；`small/base` 的 `max_context=512`，预测器会自动截断超长 lookback。

**2. 预测 API（`KronosPredictor.predict`）**
输入要求 pandas DataFrame 含 `['open','high','low','close']`（必填），`volume/amount` 可选，外加 `x_timestamp`/`y_timestamp` 两个 Series：
```python
pred_df = predictor.predict(
    df=x_df, x_timestamp=x_timestamp, y_timestamp=y_timestamp,
    pred_len=pred_len, T=1.0, top_p=0.9, sample_count=1)
```
`T` / `top_p` / `sample_count` 支持**概率预测 + 多路径采样取平均**，是金融不确定性量化的重要能力；`predict_batch` 则对多条序列做 GPU 并行独立归一化推理。

**3. 微调管线（`finetune/`）**
依赖 `qlib`，四步：配置 `config.py` → `qlib_data_preprocess.py` 数据准备 → `torchrun` 多卡训练 `train_tokenizer.py` + `train_predictor.py` → `qlib_test.py` 回测。README 自陈多数注释由 Gemini 2.5 Pro 生成、可能不准——属诚实标注。另有 `finetune_csv/` 提供 A 股 5min K 线 CSV 直训范例。

## 四、社区口碑

- **学术背书**：AAAI 2026 接收，arXiv 论文 + 代码 + 权重 + Demo + 多语言文档齐全，被 quant/AI 圈视为「金融 foundation model 方向可复现基线」。
- **增长迅速**：GitHub 30K 量级星标（多个第三方盘点 23K–32K 区间），4.1K forks，18+ 贡献者；GitHub Daily、掘金、网易号、explainx.ai 等均有深度解析。
- **社区共识**：最被津津乐道的是「K 线即语言」的范式迁移 + 24.7M 小模型可在 MacBook Air 跑推理的低门槛。
- **普遍警示**：社区与作者均明确强调——**论文/Demo ≠ 实盘，预测的是 K 线形态而非价格本身**，实盘需自行加风控、组合优化与合规，盈亏自负。中文社区调研文章直接点名「是真突破还是量化圈新玩具」的边界争议。

## 五、竞品对比

| 维度 | Kronos | 通用 TSFM (TimesFM/MOIRAI) | FinGPT / 金融 LLM | BloombergGPT |
|------|--------|---------------------------|-------------------|--------------|
| 数据范式 | K 线专用离散 token | 连续数值直接回归 | 文本/新闻情感 | 金融语料 LLM |
| 金融噪声处理 | ✅ 分层量化专攻高噪声 | ⚠️ 通用、弱 | ⚠️ 非价格序列 | ⚠️ 非 K 线序列 |
| 开源 | ✅ MIT + 权重 | 部分开源 | 部分 | ❌ 闭源 |
| 微调链路 | ✅ Qlib 集成 | 各异 | 各异 | ❌ |
| 定位 | K 线预测/形态识别 backbone | 通用时序预测 | 金融 NLP | 金融分析 LLM |

核心差异（README 原文）：*"Unlike general-purpose TSFMs, Kronos is designed to handle the unique, high-noise characteristics of financial data."* 它不与 FinGPT/BloombergGPT 直接竞争（后者偏 NLP/分析），而是补齐「K 线序列基础模型」这一被通用 TSFM 忽略的细分。

## 六、核心研判

**优势**
- 方法论文雅且可复现：把 LLM 离散 token 自回归范式搬到金融 K 线，提供统一 backbone 与多任务建模能力。
- 工程友好：三行 import 即可预测、完整 Qlib 微调回测、Demo 即时可玩，开源诚意足。

**风险**
- 预测 K 线形态而非价格，金融预测本质高度不确定，缺乏实盘盈利验证；large 模型未开源，能力上限待补。
- 数据治理/风控/监控需自行补齐，离真实交易系统接入尚远；微调脚本注释质量作者已自陈存疑。

**趋势**
- 「金融 foundation model」是明确热点方向，Kronos 作为开源基线可能催生一系列下游微调与对比实验；与 Agent 化量化（如已入库 virattt/dexter、ai-hedge-fund）结合是自然的下一步。

**启发**
- 对同类「非自然语言序列」建模需求（行情、能耗、传感器），Kronos 证明了「专用 tokenizer 量化 + 自回归 Transformer」是比直接数值回归更鲁棒的可迁移范式。

## 七、关键文件速查

| 路径 | 作用 |
|------|------|
| `model/kronos.py` | 核心入口：`Kronos` / `KronosTokenizer` / `KronosPredictor` |
| `model/module.py` | 模型内部模块定义 |
| `examples/prediction_example.py` | 单条预测完整脚本（含绘图） |
| `examples/prediction_batch_example.py` | 批量预测 |
| `examples/prediction_cn_markets_day.py` | A 股日线预测示例 |
| `finetune/train_tokenizer.py` / `train_predictor.py` | 双阶段微调（torchrun 多卡） |
| `finetune/qlib_test.py` | Qlib 回测 |
| `finetune_csv/finetune_base_model.py` | A 股 5min CSV 直训 |
| `webui/app.py` | Gradio Web UI |
| `tests/test_kronos_regression.py` | 回归测试 |

## 八、应用场景与启发

- **量化研究**：作为 K 线趋势/价格预测、形态识别、下游回归/分类任务的预训练基底。
- **可复现基线**：金融 foundation model 方向的对照实验、消融研究与教学案例。
- **组合启发**：与 AI 投研 Agent（dexter / ai-hedge-fund）对接，用 Kronos 生成概率化 K 线预测作为 Agent 的决策信号源，再用风控层过滤——符合「模型即信号、Agent 即执行」的现代量化架构。
