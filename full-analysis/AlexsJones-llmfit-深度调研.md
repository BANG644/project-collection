# AlexsJones/llmfit — 把模型「量体裁衣」到你的硬件

> GitHub: [AlexsJones/llmfit](https://github.com/AlexsJones/llmfit)
> ⭐ 30,094 | 🍴 1,837 | 🦀 Rust | MIT
> 创建: 2026-02-15 · 更新: 2026-07-21
> 官网: 无（CLI/TUI 工具）· 姊妹项目: sympozium / llmserve / llama-panel

## 一、项目亮点

- **唯一以「硬件适配度」为核心卖点的本地 LLM 选型工具** — 不跑模型也能告诉你「哪几个模型在你的机器上跑得动、跑得快」
- **众包实测基准网络** — 用户在 TUI 内一键把真实 tok/s 测速结果 PR 回仓库，个人实测会覆盖内置估算值，形成网络效应护城河
- **106 个精选模型库 + 多运行时支持**（Ollama / llama.cpp / MLX / Docker Model Runner / LM Studio），含 MoE、动态量化、多 GPU
- **Rust 写的轻量 TUI/CLI**，无外部依赖，安装即单二进制

## 二、项目全景

一句话：**llmfit = 本地大模型「尺码推荐器」**。输入你的硬件（RAM/CPU/GPU），它扫描内置的 106 个 HuggingFace 模型库，按 **质量 / 速度 / 适配度 / 上下文** 四个维度打分，输出「哪些模型能在你机器上流畅跑」的排序清单。

核心工作流：
1. 自动探测本机硬件（内存、CPU、GPU 型号与显存）
2. 对每个候选模型计算内存占用（默认按 Q4_K_M 量化，0.5 bytes/param 估算）与预计速度
3. 交互式 TUI（默认）或 CLI 模式展示推荐结果
4. 可选「benchmark & share」：下载模型→本地 serve→测真实 tok/s→从 TUI 直接 PR 回社区库

姊妹生态：sympozium（K8s 上管理 Agent）、llmserve（本地模型 serve TUI）、llama-panel（macOS 原生管理端）。

## 三、核心架构

Rust workspace 三件套：

```
llmfit/                          (workspace root)
├── llmfit-core/                 # 核心逻辑 + 所有数据
│   ├── data/
│   │   ├── hf_models.json       # 106 个 HuggingFace 模型元数据
│   │   ├── docker_models.json   # Docker Model Runner 模型
│   │   ├── onnx_models.json     # ONNX / 音频模型
│   │   ├── baselines.json       # 内置「估算」基准（官方测速）
│   │   ├── benchmark_cache.json # 估算缓存
│   │   ├── benchmarks.yaml      # 基准定义
│   │   ├── schema.json
│   │   └── community/           # 🔑 众包「实测」结果（PR 贡献）
│   │       ├── nvidia-geforce-rtx-2080/*.json
│   │       ├── tesla-t4/*.json
│   │       └── intel-arc-graphics-130v-140v-integrated/*.json
│   └── build.rs
├── llmfit-tui/                  # 默认交互界面
└── llmfit-desktop/              # 桌面端
```

架构关键点：**「估算值（baselines.json）」与「实测值（community/*.json）」双层分离**。内置官方估算保证开箱即用；用户贡献的实测结果会覆盖估算，且「相同硬件的他人实测会被标记为 ✓ 已验证」。这是一个典型的「启发式先行 + 群体智慧校准」设计。

`weekly-model-update.yml` 工作流每周自动刷新模型库，`community-benchmarks.yml` 处理社区测速 PR。

## 四、源码深度解读

### 4.1 数据驱动的「适配度」引擎（`llmfit-core/data/`）

整个工具的「大脑」其实是这批 JSON/YAML 数据文件，而非复杂算法。每个模型记录参数规模、量化档、上下文长度、适用场景。**fit 评分 = f(硬件剩余内存, 模型量化后体积, 速度估算, 上下文需求)**。将「知识」外置为数据而非代码，使非 Rust 开发者也能通过 PR 贡献模型，极大降低了社区参与门槛。

### 4.2 众包实测闭环（TUI → PR）

`docs/benchmarking.md` 描述：用户在 TUI 内选模型→serve→测速，**每次运行先存本地，再可一键 PR 回仓库**。设计上的巧思是「先本地保存、零第三方账号、无需 gh CLI」——把贡献摩擦降到最低，这是社区基准库能滚雪球增长的关键。

```rust
// 概念骨架：fit 评分维度（非逐字源码）
struct FitScore {
    quality: f32,   // 模型能力档位
    speed: f32,     // 估算/实测 tok/s
    fit: f32,       // 内存是否装得下 + 余量
    context: f32,   // 上下文长度适配度
}
// 优先用 community/<hw>/*.json 的实测，回退 baselines.json 估算
```

## 五、社区口碑

- **活跃度高**：1,837 forks，每周自动更新模型库，社区基准 PR 流程成熟
- **定位精准**：本地 LLM 玩家苦于「参数→显存」换算久矣，llmfit 直击痛点，README 强调「right-size to your hardware」
- **生态协同**：作者围绕本地 LLM 组建了 sympozium/llmserve/llama-panel 工具矩阵，形成小生态
- 口碑数据多来自 GitHub Discussions 的基准分享，未做大规模社媒舆情统计（「数据不可用」）

## 六、竞品对比

| 维度 | llmfit | Ollama | llama.cpp | LM Studio | GPT4All |
|------|--------|--------|-----------|-----------|---------|
| 硬件适配推荐 | ✅ 四维打分 | ❌ 仅运行 | ⚠️ 探测但不评分 | ⚠️ 简单筛选 | ❌ |
| 众包实测库 | ✅ community/ | ❌ | ❌ | ❌ | ❌ |
| 多运行时 | ✅ 5 种 | ✅ | ✅ | ⚠️ | ✅ |
| 交互形态 | TUI+CLI | CLI | CLI/lib | GUI | GUI |
| 量化选择 | ✅ 动态 | ⚠️ | ✅ | ✅ | ⚠️ |

**差异化**：竞品要么「只负责跑」（Ollama/llama.cpp），要么「只给 GUI 选型」（LM Studio），没有把「你这机器到底能跑啥」做成可量化、可众包校准的一等公民。

## 七、核心研判

**优势**
1. 切中本地 LLM 最大的隐性痛点——「型号→硬件」换算，且做成可量化评分
2. 众包实测闭环构建数据护城河，越用越准（网络效应）
3. 数据外置 + 零摩擦 PR，社区贡献门槛极低
4. Rust 单二进制，轻量无依赖

**风险/局限**
1. 模型库需持续维护，依赖每周自动更新 + 社区贡献，新硬件/新量化格式可能滞后
2. 估算对未收录硬件/ novel 架构（如新型 NPU）可能失真
3. 本身不 serve 模型，依赖外部运行时（Ollama 等），是「选型层」非「推理层」

**启发（可复用思路）**
- **「估算先行 + 用户实测覆盖」是任何「推荐类工具」的黄金模板**：先以内置启发式保证开箱可用，再让真实用户贡献 ground truth 反哺。
- **把知识外置为数据文件而非代码**，能用 PR 撬动社区维护，比硬编码可持续得多。

## 八、应用场景与启发

- **本地 AI 玩家购机/选型**：「我这台笔记本能跑多大的 Qwen？」→ llmfit 直接答
- **边缘部署预检**：在往树莓派/笔记本塞模型前，先用它算内存账
- **对同类需求的解决思路**：做「推荐/适配」类工具时，不要追求一次性完美算法，而是设计「内置估算 + 众包校准」的双层数据架构——这正是 llmfit 三个月冲到 30K stars 的底层逻辑。

## 九、关键文件路径速查

```
llmfit-core/data/hf_models.json        # 106 个模型元数据（核心知识库）
llmfit-core/data/baselines.json        # 官方「估算」基准
llmfit-core/data/community/            # 🔑 众包「实测」结果（护城河）
llmfit-core/data/benchmarks.yaml       # 基准定义
MODELS.md                              # 模型支持清单（人读版）
docs/how-it-works.md                   # 工作原理详解
docs/benchmarking.md                   # 众包测速 PR 流程
Cargo.toml                             # workspace: llmfit-core/tui/desktop
```
