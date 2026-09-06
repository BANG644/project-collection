# 🔬 sapientinc/HRM-Text - 全方位深度调研

> 调研日期：2026-09-07 ｜ 重写自模板化旧报告（原"四层组成"通用 boilerplate，无真实源码/架构/外链）
> 数据来源：GitHub 仓库 `sapientinc/HRM-Text` 真实 README / 目录树抓取（stars 1,969，pushed 2026-09-04，Apache-2.0，Python）

## 📌 一句话定位

`HRM-Text` 是**基于 HRM（Hierarchical Reasoning Model，分层推理模型）架构的 1B 文本生成模型 + 完整预训练框架**，强调任务完成与潜空间推理。它宣称用 **130–600× 更少算力、150–900× 更少数据**实现基础模型预训练——约 $1000 即可从零预训练一个基础模型。

> 核心判断：它卖的不是"一个模型权重"，而是一整套**可复现的低成本基础模型预训练配方**（数据采样 → 预训 → SFT → 评测 → HF 导出），并配 arXiv 论文（2605.20613）与 HuggingFace 权重。真正价值在"把基础模型预训练门槛从百万级 GPU 小时压到 ~$1000"。

## 🏆 项目亮点（差异化）

1. **从零预训练可及**：参考配方 L(0.6B) 8×H100 ~50h/$800；XL(1B) 16×H100 ~46h/$1472（按 $2/H100·h 估算）。
2. **完整框架而非单点**：数据管线 + 预训 + SFT + 评测 + 转换器导出一条龙，配套 `data_io` 伴侣仓库做清洗/分词/分层采样。
3. **前沿训练栈**：分层循环架构 + PrefixLM 序列打包 + **FlashAttention 3** kernels + **PyTorch FSDP2** 分布式训练。
4. **多架构可对照**：`config/arch/net` 内置 hrm / transformer / trm / rins / ut 等基线，可同配方横向比较。
5. **学术完整度**：arXiv 论文 2605.20613 + HuggingFace 模型 `HRM-Text-1B` + 公开基准（XL: GSM8k 84.7% / MATH 56.5% / MMLU 60.7%）。

## 🏗️ 核心架构

Config 驱动的 Hydra 工程（注意：模型**依赖 Hopper 级 GPU**，因为 attention 路径依赖 FlashAttention 3）：

```
HRM-Text/
├── config/
│   ├── arch/net/        # hrm / transformer / trm / trm_match_recurrence / rins / ut
│   ├── arch/size/       # B(12L) / L(24L) / XL(32L) / XXL(72L) / XXL_wide
│   ├── cfg_pretrain.yaml / cfg_sft.yaml
│   └── data/            # hlm.yaml / sft.yaml
├── pretrain.py          # FSDP2 预训入口（optimizer/LR/W&B/checkpoint）
├── dataset_new.py       # PrefixLM 打包数据集加载器
├── multipack_sampler.py # 分布式 multipack batch 采样（LPT 分配）
├── models/
│   ├── flash_attention_prefixlm_v2.py  # 两遍 PrefixLM attention
│   ├── layers.py        # RoPE / gated MHA / SwiGLU / static KV cache
│   ├── baselines/hrm_nocarry_bp_warmup.py  # 主架构
│   └── lm_head.py
├── conversion/convert_to_hf.py   # FSDP2 ckpt → HF 格式
├── evaluation/          # 评测引擎 + benchmark 包装 + config
└── docker/Dockerfile    # 测试过的 CUDA/PyTorch/FA3 环境
```

## 🧠 源码深度解读

### 1. `pretrain.py` —— FSDP2 训练主循环

负责 FSDP2 wrapping、优化器创建、LR schedule、W&B 日志、代码/配置快照与分布式 checkpoint。多节点时每 rank 仅存自身分片，故 README 强烈建议挂载共享存储。

### 2. `dataset_new.py` + `multipack_sampler.py` —— PrefixLM 打包

`dataset_new.py` 加载 `data_io` 产出的 `tokens.npy` 与每 epoch 索引数组，构建 PrefixLM batch、默认 mask 指令 token、emit FlashAttention sequence metadata；`multipack_sampler.py` 用 LPT（最长处理时间）分配做分布式 multipack batching，提升 token-slot 利用率、均衡二次注意力计算量。

### 3. `models/flash_attention_prefixlm_v2.py` —— 两遍注意力

实现 PrefixLM 的两遍 path：**前缀区一次双向 pass + 回复区一次因果 pass**。这是"指令-回复"结构高效训练的关键，也解释了为何用 FlashAttention 3（Hopper 特性）。

### 4. `models/layers.py` 与 `models/baselines/hrm_nocarry_bp_warmup.py`

`layers.py` 含 RoPE、gated MHA、SwiGLU MLP、static KV cache 与初始化工具；`hrm_nocarry_bp_warmup.py` 是 HRM-Text 主架构（分层递归，H/L 模块均分层）。

## 🌐 全网口碑画像

- GitHub：1,969⭐、Apache-2.0、活跃（pushed 2026-09-04）、`sapientinc` 组织维护，Discord 社区 1200+。
- 学术活跃：arXiv 2605.20613 + HuggingFace `HRM-Text-1B` 权重 + 公开基准表。
- 社区定位：小模型高效预训练 / HRM 架构研究，对"预算有限想从零训基础模型"的研究者强信号。

## ⚔️ 竞品对比

| 方案 | 优势 | 风险 |
|---|---|---|
| `HRM-Text` | HRM 潜空间递归推理、完整可复现预训配方、$1000 级门槛、论文+权重齐全 | HRM 是否真优于标准 Transformer 仍待社区验证；依赖 FA3/Hopper |
| TinyLlama / MiniCPM 训练 | 社区大、久经考验 | 架构为标准 Transformer，无 HRM 递归卖点 |
| nanotron / lit-gpt | 通用预训框架、生态成熟 | 不提供"低成本配方 + 特定架构"组合，上手成本高 |

## 🎯 核心研判

**优势**：① 把基础模型预训练从"大厂专属"拉到"单人可负担"，配方透明可复现；② HRM 架构提供标准 Transformer 之外的递归推理探索路径；③ 数据→预训→SFT→评测→导出全链路 + 多架构基线，研究友好。

**风险**：① HRM 架构相比标准 Transformer 的真实增益**需独立验证**（样本/任务有限）；② 强依赖 Hopper + FlashAttention 3，非 H100/A100 用户难跑；③ 原生 vLLM 推理支持"进行中"，当前推理路径偏自研。

**适用场景**：预算有限、想从零预训练小基础模型的研究者/团队；HRM/递归推理架构的方向探索。

**不适用场景**：无 Hopper 级 GPU；追求"开箱即用大模型"而非"自己训"的轻量需求。

## 📂 关键文件路径速查

- `README.md`：预训配方、基准表、SFT、导出、状态。
- `config/arch/net/` + `config/arch/size/`：架构与尺寸预设（Hydra 切换）。
- `pretrain.py`：FSDP2 预训入口。
- `dataset_new.py` / `multipack_sampler.py`：PrefixLM 数据集与 multipack 采样。
- `models/flash_attention_prefixlm_v2.py`：两遍 PrefixLM attention。
- `models/baselines/hrm_nocarry_bp_warmup.py`：HRM-Text 主架构。
- `conversion/convert_to_hf.py`：FSDP2 → HF 格式导出。
- `evaluation/`：评测引擎与 benchmark 配置。
- `docker/Dockerfile`：测试过的 CUDA/PyTorch/FA3 环境。

## ⭐ 三条关键发现

1. 真正价值是**"低成本可复现预训练配方"**，模型权重只是配方跑出来的产物；HRM 架构是这条链路的差异化卖点。
2. **PrefixLM 两遍注意力 + PrefixLM 序列打包 + multipack LPT 采样**三件套，是把"指令-回复"训练效率做高的工程关键。
3. 引用前需冷静：**HRM 架构性能增益仍待社区独立复现**，且强绑定 Hopper/FA3 是硬约束。
