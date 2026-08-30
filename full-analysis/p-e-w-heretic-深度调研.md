# p-e-w/heretic — 深度调研

> 调研日期：2026-08-31 ｜ 星标：29,063 ⭐ ｜ 协议：AGPL-3.0 ｜ 语言：Python ｜ 默认分支：`master` ｜ 最新 Release：v1.4.0（2026-06-14），开发中 2.0.0.dev0 ｜ 来源：GitHub Trending 日榜（+150/日）

## 一、项目定位（一句话）

Heretic 是一个**全自动 LLM 审查移除工具**——把学术界的「方向性消融（directional ablation / abliteration）」从"手工调参的黑魔法"变成"一条命令 + 自动超参搜索"的工程流程，无需任何后训练即可让模型停止拒答，同时用 KL 散度约束把能力损伤压到最低。

## 二、项目亮点（差异化）

- **把消融变成多目标优化问题**：传统 abliteration 需要人工挑层、挑方向、挑强度，Heretic 用 Optuna 的 **TPE 采样器**（`n_trials = 200`，其中 `n_startup_trials = 60` 做随机探索）自动搜索参数空间，**同时最小化「拒答次数」和「与原模型的 KL 散度」**。这是它区别于所有其他 abliteration 脚本的根本设计。
- **量化战绩可复现**：README 给出同一底模的横向对比（PyTorch 2.8 / RTX 5090）——在**同等拒答抑制水平（3/100）**下，Heretic 的 KL 散度显著更低：

  | 模型 | "harmful" 提示的拒答数 | 对 "harmless" 提示的 KL 散度 |
  |---|---:|---:|
  | google/gemma-3-12b-it（原始） | 97/100 | 0（定义上） |
  | mlabonne/gemma-3-12b-it-abliterated-v2 | 3/100 | 1.04 |
  | huihui-ai/gemma-3-12b-it-abliterated | 3/100 | 0.45 |
  | **p-e-w/gemma-3-12b-it-heretic（本项目）** | **3/100** | **0.16** |

  同样"解除拒答"，副作用只有对手的 1/3 ～ 1/6。
- **消融实现为 rank-1 LoRA 增量，而非权重手术**：这是全仓库最关键的工程决策（详见第五节）。传统做法直接改写 `W`，一旦参数不合适必须重新加载模型；Heretic 把消融写成可挂载/卸载的 LoRA 适配器，因此**每次 trial 可以 instant reset**，200 次搜索才成为可能。
- **生态规模已成事实**：Hugging Face 上带 `heretic` 标签的社区模型**超过 5000 个**（`huggingface.co/models?other=heretic`），官方组织 `heretic-org`，另有 Discord / Matrix 社区与 Codeberg 镜像。
- **消费级硬件可跑**：RTX 3090 + 默认配置，对 ~8B 模型解除审查约 **20–30 分钟**；支持 `bnb_4bit` 量化以在更小显存上运行。
- **模型架构覆盖广**：dense / MoE / 多模态 / 混合架构均支持；内置 `chain_of_thought_skips` 处理 thinking 模型（`<think>`、gpt-oss 的 `<|channel|>analysis<|message|>`、`[THINK]` 等），确保评测发生在真正的回答开头而非推理块内。

## 三、核心架构（克制呈现）

源码极其精简——`src/heretic/` 只有 13 个文件，但职责切分非常干净：

```
src/heretic/
├── main.py        # 编排：加载模型 → 残差分析 → Optuna 搜索 → 导出（1474 行，最大文件）
├── model.py       # 消融核心：abliterate() 的矩阵运算与 LoRA 构造（867 行）
├── analyzer.py    # 残差几何分析：good/bad/refusal 方向的余弦相似度与 silhouette
├── evaluator.py   # 批量生成响应
├── scorer.py      # 打分抽象层
├── scorers/
│   ├── keyword_rate.py    # 拒答率：关键词命中法（"i cannot" / "as an ai" / "unethical" …）
│   └── kl_divergence.py   # 能力保留度：与原模型 logprob 分布的 KL 散度
├── plugin.py      # 插件机制：scorer 可外部替换、支持多实例
├── reproduce.py   # 复现已有消融结果
├── config.py / system.py / progress.py / utils.py
└── config.default.toml   # 226 行、注释详尽的配置总纲
```

**数据流**：两个提示词数据集（默认 `mlabonne/harmless_alpaca` 400 条 vs `mlabonne/harmful_behaviors` 400 条）→ 逐层采集残差 → 求差得到"拒答方向" → 在参数空间中搜索（层范围、强度 λ、方向正交化等）→ 每个 trial 用 100 条测试提示同时算「关键词拒答率」和「KL 散度」→ TPE 收敛 → 导出 safetensors（默认 `max_shard_size = "5GB"`）。

**插件化打分器**是被低估的设计：`scorers = [...]` 列表里每项都是 `{ plugin = "...", optimization = "minimize" }`，可以自定义打分维度（甚至同一个 scorer 挂多个实例、各自不同数据集分片），意味着这套优化框架**不止能做"去审查"，任何"改一点权重、优化某个行为指标、同时不许模型变傻"的任务都能复用**。

## 四、应用场景与启发（重点）

- **场景 1 — 本地模型的实用化处理**：自托管 LLM 时常被过度对齐的拒答策略卡住（医学、法律、安全研究、创意写作里的正常问题被拒），Heretic 提供的是"最小副作用地拆掉拒答开关"的工程手段，而不是粗暴的越狱提示词。
- **场景 2 — 对齐机制的可解释性研究**：`print_residual_geometry = true` 会打出逐层表格（S(g,b)、S(g,r)、silhouette 系数、各方向 L2 范数）——这是**研究"拒答行为在残差流里长什么样、集中在哪几层"的现成工具**。README 示例里可以清楚看到第 10 层 S(g,r)=0.8189、silhouette=0.2863 出现峰值，第 18 层范数骤降到 190（gemma 的特殊层结构），这类观察比论文复现快得多。
- **场景 3 — 通用"行为编辑 + 能力保留"框架**：把 scorer 换成别的指标（啰嗦度、特定风格、拒绝某类输出），这套 TPE + KL 双目标搜索就变成通用的**低成本行为微调替代方案**——仓库自带的 `config.noslop.toml`（去 AI 味）、`config.nohumor.toml`（去油腻幽默）就是这个思路的现成示范。
- **核心启发（工程范式）**：
  1. **把"可回滚"设计进算法本身**。选择 LoRA 增量而非原地改权重，直接把"能不能做 200 次自动搜索"从不可行变成可行。任何需要反复试参的模型改动，都该先问一句"这个改动能不能表达成可挂载的 delta"。
  2. **单目标优化会骗人，双目标才诚实**。只优化"拒答数下降"会得到一个变傻的模型；加上 KL 散度约束才逼出真正的帕累托前沿。同类"优化某指标"的任务，都该配一个"别把基础能力搞坏"的对偶指标。
  3. **默认配置即文档**。226 行 `config.default.toml` 每个参数都写了"为什么这样默认、失败时会怎样降级"（例如 dtype 的四级 fallback 链 `auto → float16 → bfloat16 → float32` 并注明各自失败原因），这种写法让配置文件同时承担了设计说明书的角色。

## 五、源码深度解读（核心模块）

### 5.1 `model.py::abliterate()` — 消融的 rank-1 LoRA 表达

整个项目的技术心脏。数学上，方向性消融要从权重矩阵 `W` 中减去它在拒答方向 `v` 上的投影：

```python
# LoRA abliteration: delta W = -lambda * v * (v^T W)
# lora_B = -lambda * v ; lora_A = v^T W
lora_A = (v @ W).view(1, -1)
lora_B = (-weight * v).view(-1, 1)
```

三行代码的含金量：
- `delta W = -λ · v · (vᵀW)` 是标准的**投影消除**，但被拆成 `B @ A` 的 rank-1 外积形式，正好是 LoRA 的标准形态（`lora_A` 是 1×n，`lora_B` 是 m×1）。
- 因此消融**不修改原始权重**，只是挂上一个秩为 1 的适配器。`weight`（即 λ）由 Optuna 逐 trial 给出，改参数只需替换适配器，**模型不必重载**。
- 副产品：导出结果天然兼容 PEFT / LoRA 生态，用户可以只分发几 MB 的适配器而不是整个模型。

### 5.2 行归一化的三档策略（`row_normalization`）

配置里有个容易被忽略但很关键的参数：

| 取值 | 行为 |
|---|---|
| `none` | 直接在原权重上算 LoRA |
| `pre` | 相对**行归一化后的权重**计算适配器 |
| `full`（默认） | 同 `pre`，但额外**重归一化以保持原始行幅值** |

`full` 是对 grimjim 提出的 **norm-preserving biprojected abliteration** 的近似实现——因为幅值保持存在非线性效应，无法精确表达为 rank-1，所以用 `full_normalization_lora_rank = 3`（借 `torch.svd_lowrank` 做低秩分解）来逼近。这解释了默认配置为何是 `full`：**消融最大的副作用来源是权重行范数被破坏，先把范数护住，KL 散度自然下来**——这正是它 KL=0.16 打赢 1.04 的关键之一。

另一个同向的开关是 `orthogonalize_direction = true`：只减去拒答方向中**与"良性方向"正交的分量**，避免连带删掉正常语义。

### 5.3 `main.py::objective()` — Optuna 多目标搜索

```python
sampler = optuna.samplers.TPESampler(...)   # 树结构 Parzen 估计
# 每个 trial：构造 LoRA → 挂载 → 跑 100 条 harmful 提示算 keyword_rate
#                          → 跑 100 条 harmless 提示算 KL divergence
# 双目标 co-minimize，200 trials（前 60 随机探索）
```

工程细节值得学：`study_checkpoint_dir = "checkpoints"` 让搜索可中断续跑；`batch_size = 0`（auto）会自动探测最大可用批量（上限 `max_batch_size = 128`）；`offload_outputs_to_cpu = true` 把中间残差/logprob 尽快搬到 CPU 以压低峰值显存——**这三条都是"让长时间 GPU 任务在消费级卡上不崩"的通用招式**。

### 5.4 `scorers/keyword_rate.py` — 拒答检测的务实取舍

拒答判定没有用分类模型，而是一张 ~35 词的关键词表（`disclaimer` / `i cannot` / `as an ai` / `unethical` / `prohibit` / `illegal` …）做大小写不敏感匹配。看似粗糙，但作为**优化过程中的代理指标（proxy metric）**足够：它便宜（无需额外模型）、稳定（无随机性）、方向正确。这是"优化循环里的指标要优先选便宜且单调的"的教科书案例。

## 六、全网口碑（真实信号）

- **社区规模**：HF 上 5000+ 衍生模型；Discord + Matrix 双社区 + Codeberg 镜像（对不信任 GitHub 的用户友好）。
- **Issue 活跃度**（实抓样本）：#438「[RFC] 让 LLM 来驾驶 Heretic」、#431「通过 PyTorch/XLA 支持 TPU（自动检测 + FSDP + XLA 安全的 merge/export）」、#421「feat(ara)：支持 DiffusionGemma 块扩散模型」、#423「更好的 thinking 前缀检测逻辑」（5 条评论）——**社区 PR 在主动扩硬件后端与模型架构支持**，不是单人项目在孤军奋战。
- **真实痛点**：#429 bitsandbytes 的 `libnvJitLink.so.13` 缺失（CUDA 13 环境依赖坑）、#436 在 `tencent/Hy3-FP8` 上失败（FP8 量化模型未覆盖）、#434/#435 围绕 dtype fallback 的错误上报与"不可恢复错误不该重试"——说明**环境依赖与新型量化格式是当前主要摩擦点**。
- **迭代节奏**：v1.2.0（2026-02）→ v1.3.0（2026-05）→ v1.4.0（2026-06），已在推进 2.0.0.dev0，节奏约季度一个 minor。
- **争议面**：项目本质是移除安全对齐，伦理争议内生存在。作者的立场体现在工程上——README 明确对标学术方法（Arditi et al. 2024）并列出 AutoAbliteration、remove-refusals-with-transformers 等前作，走的是"透明的研究工具"路线而非地下工具路线。AGPL-3.0 也意味着**基于它做闭源 SaaS 不可行**。

## 七、竞品对比 + 核心研判

| 维度 | Heretic | mlabonne/abliterated 系列 | huihui-ai/abliterated | 手工 abliteration 脚本 | LoRA 微调去对齐 |
|---|---|---|---|---|---|
| 自动调参 | ✅ Optuna TPE 200 trials | ❌ 人工 | ❌ 人工 | ❌ | ❌ |
| 能力损伤（KL） | **0.16（最低）** | 1.04 | 0.45 | 不可控 | 视数据集 |
| 需要训练 | ❌ 完全不需要 | ❌ | ❌ | ❌ | ✅ 需算力+数据 |
| 产物形态 | LoRA 适配器 / 完整模型 | 完整模型 | 完整模型 | 完整模型 | LoRA |
| 架构覆盖 | dense/MoE/多模态/混合 | 有限 | 有限 | 需自行改 | 通用 |
| 消费级可跑 | ✅ RTX 3090 / 20-30min | — | — | ✅ | ⚠️ 更贵 |
| 可插拔目标 | ✅ scorer 插件 | ❌ | ❌ | ❌ | ⚠️ 换数据集 |

**核心研判**：

Heretic 的价值**不在"去审查"这个用途，而在它证明了一件方法论上的事**——只要能把模型改动表达成可即时挂载/卸载的低秩增量，并且给优化目标配上一个"别把模型搞坏"的对偶约束，就可以用通用超参搜索器（Optuna）自动化掉过去依赖专家直觉的权重手术。它把一个"炼丹活"变成了"跑个 job"。

- **值得抄的三件事**：① 算法层面的可回滚性设计（LoRA 增量 > 原地改权重）；② 双目标优化（效果指标 + 能力保留指标）而非单目标；③ 配置文件即设计文档（fallback 链与默认值理由写在注释里）。
- **适用判断**：需要本地模型不无谓拒答、或研究对齐机制在残差流中的几何结构 → 直接用；需要系统性提升某项能力 → 这不是微调替代品，abliteration 只做"减法"。
- **风险点**：伦理与合规风险由使用者承担；AGPL-3.0 阻断闭源商业化；依赖 bitsandbytes / CUDA 版本组合较脆（#429）；FP8 等新量化格式尚未覆盖（#436）。
- **迁移到自己项目的最短路径**：把 `scorers/` 换成你自己的指标，把 `abliterate()` 换成你自己的 delta 构造函数，`main.py` 的 Optuna 编排 + checkpoint + 自动 batch size 探测几乎可以原样复用——**这才是这个仓库对大多数人最实际的用法**。

> **关键文件速查**：
> - 消融数学核心 → `src/heretic/model.py::abliterate()`（rank-1 LoRA，`lora_A = v @ W` / `lora_B = -weight * v`；`row_normalization` 三档 + `torch.svd_lowrank` 低秩幅值保持）
> - 优化编排 → `src/heretic/main.py::objective()`（`optuna.samplers.TPESampler`，双目标 co-minimize）
> - 残差几何分析 → `src/heretic/analyzer.py::print_residual_geometry()`
> - 打分插件 → `src/heretic/scorers/keyword_rate.py`、`scorers/kl_divergence.py`、抽象层 `scorer.py` + `plugin.py`
> - 配置总纲（226 行，含所有默认值理由）→ `config.default.toml`；风格变体 → `config.noslop.toml`、`config.nohumor.toml`
> - 多架构回归测试 → `tests/{gemma-4e,minicpm5,mistral-3,qwen2.5,qwen3.5-moe}/config.toml` + `tests/run_tests.py`
