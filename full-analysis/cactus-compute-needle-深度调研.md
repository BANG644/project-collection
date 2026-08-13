# Needle 深度调研（cactus-compute/needle）

> 调研日期：2026-08-14 ｜ 星标：4,830 ⭐ ｜ 语言：Python ｜ 协议：MIT ｜ 默认分支：main ｜ 创建：2026-02-24 ｜ 官网：cactuscompute.com

## 一、项目定位（一句话）

Needle（**Needle 2**，45M 参数）是一个**14MB 单文件基础模型**，专为**手机 / 穿戴 / 智能家居 / 机器人**等微型设备上的**工具调用、设备操控、结构化抽取**设计——整模型烘焙进单一 14MB 引擎，约 28MB RAM 即可跑完整会话。

## 二、项目亮点（差异化，开篇呈现）

- 📦 **极致小巧、自包含**：权重烘焙进单一 14MB 引擎，无独立模型文件；推理**完全离线无网络**，引擎首次从 HF 拉取一次后缓存。
- 🔒 **字节级语法约束解码**：从你的 schema 编译出字节级 grammar，**每个 token 都被约束**，JSON 永不会畸形（对比大模型「JSON mode」更稳定）。
- 🎯 **置信度门控**：每个响应带学习得到的 calibrated confidence，设阈值——高于则执行，低于则升级（escalate）给更大模型/人工。
- 🧰 **工具检索（Tool Retrieval）**：声明大工具目录，内置检索头每轮只渲染 top-5 工具，grammar 约束到该子集，支持大 catalogue 持久化索引。
- 🧠 **有界内存**：256 token 滑动窗口 + 工具作为 KV 锚点（sink），**无论对话多长，内存恒定 ~28MB**。
- 🏗️ **新架构 Simple Attention Network**：Hadamard MLP 替 FFN、GQA、engram KV 记忆、多 lane hyper-connections（arXiv:2607.18363），用 CQ2-bit Cactus Quants 极量量化。

## 三、核心架构

`needle/` 包：`model/`（Simple Attention Network 实现）、`agent/`（工具检索头与调用循环）、`cli.py`（CLI + `needle playground` 本地 Gradio 服务）、`playground/`（Web UI）。推理引擎从 HF 拉取并缓存；解码时由**从 schema 编译的字节级 grammar** 约束每一步。整模型以 CQ2-bit 量化烘焙进引擎，故「`pip install cactus-needle` + 描述工具」即可用。

## 四、应用场景与启发

- **离线设备端 Agent**：智能家居语音指令→工具调用（开灯/调温）、机器人指令解析，断网也可运行。
- **结构化抽取**：发票/收据/工单从文本抽取为 Pydantic 对象（抽取 = 单工具的调用，schema 一致性由 grammar 保证）。
- **小模型兜底 / 置信门控路由**：用 Needle 处理简单结构化任务，低置信时升级给大模型，降本增效。
- 💡 **架构启发**：① 极小型模型 + **语法约束解码** = 比大模型 JSON mode 更可靠、更省的结构化输出范式；② 「置信度门控 + 工具检索」是端侧 Agent 的黄金组合；③ 把模型**烘焙进引擎**免去模型文件分发/版本管理，是端侧部署的优雅方案；④ 有界内存（KV sink）让长会话不爆 RAM，是 tiny model 落地的关键。

## 五、源码深度解读

### 1. `needle/model/` —— Simple Attention Network
每个 block 携带自己的更新规则：`x̂` 是 4 条残差流的 RMS 归一化展开；`H` 是固定的 Walsh-Hadamard 变换（无权重，n log n 时间）；`(k,v)` 从哈希 n-gram 表取；`P` 是路由 logits 的 Sinkhorn 双向随机归一化；`a,b,g` 与 σ-gates 均可学且输入相关。注意力与 MLP 残差都做 sandwich-norm + gate，engram 记忆位点在前两层 firing。
```text
概念：x̂ = RMSNorm(flatten(4 residual streams))
       (k,v) = lookup(hashed n-gram tables)
       P = Sinkhorn(A)   # 双向随机归一化路由
       输出 = gated(attention) + gated(mlp)
```

### 2. `agent.py`（推断层）—— 工具调用循环
`complete()` 返回 grammar 约束的 `call`；你执行后把结果回灌为下一轮 `complete()`；离题输入返回空 call `[]`（无自由文本兜底）；`reasoning` 是模型对每个参数来源的自由文本推导（如 `'ten minutes' -> minutes 10`），可解释。
```json
{ "type":"call", "success":true, "function_calls":[{"name":"set_lights",
  "arguments":{"room":"living room","on":true,"brightness":30}}],
  "reasoning":"'living room'->room; 'dim'->on true, brightness 30",
  "confidence":0.94, "prefill_tps":4300.0, "decode_tps":850.0 }
```

### 3. `cli.py` —— `needle playground`
启动本地 Gradio（默认 `127.0.0.1:7860`），UI 内可微调并导出 `.cact` 权重；`Field`（gt/le/pattern/max_length…）编译进 decode grammar，模型只能吐合规值。

## 六、全网口碑

- 2026-02 新建，Cactus Compute 出品，趋势榜新星（4.8k⭐，2026-08）；配套论文 arXiv:2607.18363。
- 数据有限（早期项目），但在「tiny on-device model」赛道认知度快速上升：基准上以 **5x~70x 更小、2-bit vs f16**，与 FunctionGemma 270M / LFM2.5 230M / Apple FM 互有胜负。

## 七、竞品对比 + 核心研判

| 维度 | Needle 2 (45M/14MB) | FunctionGemma 270M | LFM2.5 230M | Apple FM | llama.cpp/Ollama |
|---|---|---|---|---|---|
| 体积 | 14MB | 270M | 230M | 大 | 引擎+模型 |
| 可靠结构化 | ⭐语法约束 | ⭐ | ⭐ | ⭐ | 依赖 prompt |
| 离线端侧 | ✅ | ✅ | ✅ | ✅ | ✅ |
| 置信门控 | ✅ | ❌ | ❌ | ❌ | ❌ |

- **核心研判**：
  - ✅ 优势：极致小 + 语法约束可靠结构化 + 离线 + 置信门控 + 工具检索内置，概念完整。
  - ⚠️ 风险：**极早期**（45M 参数能力上限有限）、生态/基准待验证、引擎仍依赖首次从 HF 拉取。
  - 🔮 趋势：端侧 tiny model + 语法约束解码会成设备端 Agent 标配。
  - 💡 启发：**设备端「可靠工具调用 / 结构化抽取」场景的首选探索对象**；其 grammar 约束解码与置信门控路由范式，值得任何「小模型干结构化活」的需求借鉴。

## 八、关键文件路径速查

- `needle/model/`（Simple Attention Network 实现）
- `needle/agent.py`（工具调用循环 / 检索头）
- `needle/cli.py` · `needle/playground/`（CLI 与本地 Gradio）
- `llms.txt` · `pyproject.toml` · `requirements.txt` · `LICENSE`（MIT）
- 权重：`huggingface.co/Cactus-Compute/needle2`
