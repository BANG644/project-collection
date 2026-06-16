# sapientinc-HRM-Text - 全方位深度调研

## 项目全景
- **仓库**：`sapientinc/HRM-Text`
- **一句话定位**：HRM-Text is a 1B text generation model based on the HRM architecture, strengthened by task completion and latent space reasoning.
- **解决的问题**：该项目试图把 README 中描述的能力产品化/脚本化，降低特定任务的搭建或执行门槛。
- **基础指标**：Stars=1142 / Forks=104 / 默认分支=`main`
- **Topics**：large-language-models, pretraining, hierarchical-reasoning-model, hrm
- **Homepage**：数据不可用

## 核心架构
### 目录结构判断
- 顶层目录分布（递归树抽样汇总）：config(15), models(12), evaluation(7), assets(2), docker(2), scripts(2), .dockerignore(1), .github(1), .gitignore(1), LICENSE(1)
- 关键文件候选：requirements.txt, README.md

### 设计亮点研判
- 存在 Python 入口，通常意味着 CLI、服务端或研究型流水线由 Python 主导。
- 仓库包含 .github 自动化配置，通常代表 CI 或 issue 模板已被纳入工程流程。

## 源码深度解读
### README / 说明文档要点
![](./assets/banner.png)

# HRM-Text: Efficient Pretraining Beyond Scaling

<p align="center">
  <a href="https://arxiv.org/pdf/2605.20613"><img src="https://img.shields.io/badge/Paper-arXiv-red?logo=arxiv&logoColor=white" alt="arXiv Paper"></a>
  <a href="https://huggingface.co/sapientinc/HRM-Text-1B"><img src="https://img.shields.io/badge/Model-HuggingFace-yellow" alt="Model"></a>
</p>

<p align="center"><strong>🌟 Pretrain a foundation model from scratch with ~$1000. 🌠</strong></p>

HRM-Text is a 1B text generation model based on the HRM architecture, strengthened by task completion and latent space reasoning. It offers a full pretraining framework, making foundation model pretraining accessible with 130-600x less compute and 150-900x less data. It is built upon a hierarchical recurrent architecture, PrefixLM sequence packing, FlashAttention 3 kernels, PyTorch FSDP2 training, evaluation, and checkpoint conversion tooling.

**Join 1200+ HRM Developers on Our Discord Community: [https://discord.gg/sapient](https://discord.gg/sapient)**

![](./assets/benchmark_scatter.png)

## Launch the Pretraining 🚀

### Required Resources

Choose a target size and prepare the corresponding GPU nodes.

- **L, 0.6B parameters:** 8 H100s, single node, about 50 hours (~$800).
- **XL, 1B parameters:** 16 H100s, two nodes, about 46 hours (~$1472).

*Price estimation based on $2/H100 hour.*

The following are benchmark results from the reference runs.

| Size | GPUs | Time | GSM8k | MATH | DROP | MMLU | ARC-C | HellaSwag | Winogrande | BoolQ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **L (0.6B)** | 8 | 50 hrs | 77.6% | 51.2% | 78.6% | 56.6% | 75.9% | 52.7% | 67.6% | 85.0% |
| **XL (1B)** | 16 | 46 hrs | 84.7% | 56.5% | 82.3% | 60.7% | 81.9% | 63.4% | 72.4% | 86.2% |

> Hopper-class GPUs are the expected training target because the attention path depends on FlashAttention 3.

### 1. Prepare Data

HRM-Text trains from sampled, tokenized data produced by the companion `data_io` pipeline. Use `data_io` to clean, tokenize, and stratified-sample the pretraining corpus, then point HRM-Text at the sampled output.

<p align="center">
  <a href="https://g
...[truncated]

### 关键文件精读
### `requirements.txt`
```
coolname
datasets
einops
flash_attn_3
hydra-core
lm-eval[hf,vllm]
math-verify
numba
numpy
omegaconf
pydantic
PyYAML
safetensors
sympy
torch
tqdm
transformers
vllm
wandb
```

### `README.md`
```
![](./assets/banner.png)

# HRM-Text: Efficient Pretraining Beyond Scaling

<p align="center">
  <a href="https://arxiv.org/pdf/2605.20613"><img src="https://img.shields.io/badge/Paper-arXiv-red?logo=arxiv&logoColor=white" alt="arXiv Paper"></a>
  <a href="https://huggingface.co/sapientinc/HRM-Text-1B"><img src="https://img.shields.io/badge/Model-HuggingFace-yellow" alt="Model"></a>
</p>

<p align="center"><strong>🌟 Pretrain a foundation model from scratch with ~$1000. 🌠</strong></p>

HRM-Text is a 1B text generation model based on the HRM architecture, strengthened by task completion and latent space reasoning. It offers a full pretraining framework, making foundation model pretraining accessible with 130-600x less compute and 150-900x less data. It is built upon a hierarchical recurrent architecture, PrefixLM sequence packing, FlashAttention 3 kernels, PyTorch FSDP2 training, evaluatio
...[truncated]
```

### 关键逻辑总结
- 从关键文件组合看，项目更像是**围绕单一目标组织的任务流水线/工具链**，而不是超重平台。
- 入口文件决定外部交互界面（CLI / API / UI），配置文件决定运行时依赖，测试文件则暴露作者真正关心的行为边界。
- 如果用户只读 README，通常只能知道“能做什么”；而从目录与入口文件能看出“怎么做、扩展点在哪、维护成本高不高”。

## 社区口碑
### GitHub Issues 抽样
- #16 [OPEN] Feature Request: Release checkpoints for HRM-Text 0.6B（comments=[] labels=无）
- #15 [OPEN] Discussion: optional sparse MoE FFN support for HRM-Text（comments=[] labels=无）
- #12 [OPEN] Can we try the model without training it?（comments=[{'id': 'IC_kwDOSgdGLM8AAAABD4Ytnw', 'author': {'login': 'Zane12518'}, 'authorAssociation': 'CONTRIBUTOR', 'body': '@Tylersuard \nYes, a pretrained 1B checkpoint is available on Hugging Face: https://huggingface.co/sapientinc/HRM-Text-1B\n\n\n', 'createdAt': '2026-05-27T14:23:41Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [], 'url': 'https://github.com/sapientinc/HRM-Text/issues/12#issuecomment-4555419039', 'viewerDidAuthor': False}] labels=无）
- #8 [OPEN] Is there a plan to submit HRM-Text to public LLM leaderboards?（comments=[] labels=无）
- #7 [CLOSED] Package installation versions are unclear and not specified（comments=[{'id': 'IC_kwDOSgdGLM8AAAABDk1kOQ', 'author': {'login': 'mannyjl16'}, 'authorAssociation': 'NONE', 'body': 'Closed because its probably due to me being on a T4 and not H100', 'createdAt': '2026-05-25T14:13:12Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [], 'url': 'https://github.com/sapientinc/HRM-Text/issues/7#issuecomment-4534920249', 'viewerDidAuthor': False}] labels=无）
- #6 [OPEN] Train question（comments=[] labels=无）

### Pull Requests 抽样
- PR #14 [OPEN] Add optional sparse MoE FFN support with 64x8 validation
- PR #13 [OPEN] Handle zero-causal PrefixLM FA3 pass as no-op
- PR #11 [MERGED] Drop empty-response samples in SFT data prep
- PR #10 [MERGED] Revert "Fix PrefixLM FA3 zero-causal segment crash"
- PR #9 [MERGED] Fix PrefixLM FA3 zero-causal segment crash

### Releases 抽样
暂无 release 或数据不可用

### 真实反馈与维护信号研判
- 抽样 issue 中 open/closed 约为 7/1，可作为维护者响应速度的弱信号。
- 近期 PR 抽样里可见已合并项 3 个，说明项目并非完全冻结。
- 由于本批处理以 GitHub 官方数据为主，若外部搜索结果缺失，应把 GitHub issue/PR 视为最可信的一手社区反馈源。
- 高频问题通常比 README 更能暴露真实落地难点：安装、兼容性、性能边界、文档歧义、平台限制。

## 竞品对比
| 维度 | HRM-Text | 竞品/替代 |
|---|---|---|
| 定位 | 面向仓库作者设定的具体场景，通常更垂直 | Mem0 / Graphiti / LangMem 往往更通用或生态更大 |
| 学习曲线 | 依赖其内部脚本/配置约定 | 通用方案学习成本更高，但生态更成熟 |
| 差异化 | 仓库通常以“快上手、场景专用、意见化实现”为卖点 | 通用方案强调可扩展、稳定性、跨场景能力 |
| 风险 | 作者驱动、文档深度可能不足、接口稳定性不确定 | 大项目更稳定，但改造成本更高 |

## 核心研判
### 优势
- 对目标问题有强意见化实现，落地路径通常比“从零搭建通用栈”更短。
- 如果核心文件少而清晰，二次阅读和定制成本较低。
- GitHub 原生 issue / release / PR 能直接帮助判断项目是否仍在演进。

### 风险
- 若 stars、forks、release 或 PR 活跃度偏低，意味着长期维护能力要谨慎评估。
- 如果关键逻辑过于集中在单文件脚本中，后续扩展会受到可维护性约束。
- 若缺少测试/CI/配置 schema，生产环境采用前应先做自测和边界验证。

### 适用场景
- 需要快速验证该仓库所解决的问题是否值得投入。
- 团队愿意接受一定的作者意见化设计，以换取更快交付。
- 适合作为参考实现、内部 PoC、垂直任务工具，而非默认直接替代成熟平台。

### 不适用场景
- 对 SLA、兼容矩阵、长期 LTS 有强要求的核心生产系统。
- 需要极高社区冗余、插件生态或企业级支持的场景。

## 关键文件路径速查
- `requirements.txt`
- `README.md`

## 3 条关键发现
- 代码入口/骨架集中在：requirements.txt, README.md
- 近期开源反馈以 issue 为主，典型议题包括：Feature Request: Release checkpoints for HRM-Text 0.6B；Discussion: optional sparse MoE FFN support for HRM-Text

## 研究方法与数据来源
- GitHub Repo API / README / 默认分支递归文件树
- 关键源码文件抽样精读
- Issues / PRs / Releases 社区活动抽样
- 说明：若外部搜索数据不可用，则明确标注并不伪造口碑结论
