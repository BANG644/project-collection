# 🧠 MemTensor/MemOS — 深度调研报告

> **仓库**: [MemTensor/MemOS](https://github.com/MemTensor/MemOS)
> **调研日期**: 2026-08-05 | **数据来源**: GitHub API + 完整文件树（2,320 项）+ README + issue 列表
> **数据**: ⭐ 10,587 | 🍴 976 | **语言**: Python（+ TS 插件）| **许可**: Apache-2.0 | **最后推送**: 2026-08-04
> **版本**: MemOS 2.0 "Stardust（星尘）" | **论文**: [arXiv:2507.03724](https://arxiv.org/abs/2507.03724)
> **背景**: MemTensor（记忆张量）出品，与 IAAR-Shanghai 的 Awesome-AI-Memory 同生态

---

## 一、项目定位

**MemOS 是给 LLM 和 AI Agent 用的「记忆操作系统」**——把长期记忆的 **存 / 取 / 管（store / retrieve / manage）** 统一到一套 API 下。

它跟绝大多数"AI 记忆"项目最本质的区别在于：**记忆不是一个黑盒 embedding store，而是一张可检视、可编辑的图**。README 原话："structured as a graph, inspectable and editable by design, not a black-box embedding store."

---

## 二、项目亮点（差异化）

1. **三种记忆类型并存，而不只是文本**。源码 `src/memos/memories/` 下明确分为三类：
   - `textual/` — 文本记忆（naive / general / tree / preference 多种实现）
   - `activation/` — **激活记忆：直接操作 KV cache**（`kv.py`、`vllmkv.py`）
   - `parametric/` — **参数记忆：LoRA**（`lora.py`）

   这是 MemOS 论文 MemCube 设计的落地。**同类项目（mem0、Zep 等）基本只做第一类**。把 KV cache 和 LoRA 也纳入"记忆"范畴，是学术出身项目才会有的野心。

2. **MemScheduler：异步摄入 + 毫秒级延迟**。记忆写入不阻塞主链路，专为高并发生产环境设计。`mem_scheduler/` 下有独立的 queue_ops / memory_ops / web_log_ops mixin 与 activation memory manager。

3. **多 Cube 知识库管理**。记忆按 "memory cube" 组织，支持跨用户/项目/Agent 的隔离、受控共享与动态组合。

4. **自然语言反馈修正记忆**（`mem_feedback/`）。不是只能增删，而是能用自然语言"更正/补充/替换"已有记忆。

5. **OmniMemEval 统一评测**：官方声称在 14 个商业记忆产品、十个数据集的统一评测中领先。且给了具体数字：LoCoMo 88.83 / LongMemEval 89.20。

6. **对 OpenClaw 的实测提升有公开数字**：五项 Agent 任务平均完成率 **36.63% → 50.87%**。这是少见的"接入记忆后端到端任务成功率"数据，而非仅仅检索指标。

---

## 三、核心架构

### 3.1 源码结构（`src/memos/`，443 个文件）

```
memories/                ← ⭐ 三类记忆的核心抽象
  ├── textual/           文本记忆：base / naive / general / tree / simple_tree
  │     ├── preference.py, simple_preference.py     ← 偏好记忆
  │     └── prefer_text_memory/
  ├── activation/        ⭐ 激活记忆（KV cache）：base / item / kv.py / vllmkv.py
  └── parametric/        ⭐ 参数记忆（LoRA）：base / item / lora.py

mem_scheduler/           ← 异步调度器
  ├── base_scheduler.py, general_scheduler.py
  ├── base_mixins/       queue_ops / memory_ops / web_log_ops
  ├── memory_manage_modules/  activation_memory_manager.py
  ├── general_modules/   task_threads / scheduler_logger / init_components
  └── analyzer/          api_analyzer / eval_analyzer / scheduler_for_eval

mem_cube/                ← 记忆立方（单 cube）
multi_mem_cube/          ← 多 cube 编排
mem_os/                  ← MOS 顶层门面
mem_agent/               ← Agent 侧集成
mem_chat/                ← 对话集成
mem_reader/              ← 记忆读取
mem_feedback/            ← 自然语言反馈修正
mem_user/                ← 用户维度
dream/                   ← ⭐ 命名有意思：疑似离线记忆整合/巩固（类比睡眠巩固）
search/ + reranker/      ← 混合检索 + 重排
graph_dbs/ + vec_dbs/    ← 图库（Neo4j）+ 向量库（Qdrant）双后端
embedders/ + llms/ + chunkers/ + parsers/
plugins/ + memos_tools/
api/ + cli.py + context/ + configs/
```

### 3.2 四种接入形态（README 官方对照表）

|  | Cloud API | Self-Host | OpenClaw Cloud Plugin | Local Plugin |
|--|-----------|-----------|----------------------|--------------|
| 适合 | 你的 App，全托管 | 团队自有基建 | OpenClaw 用户，零运维 | Hermes/OpenClaw，100% 本地 |
| 安装 | 拿 API key | `docker compose up` | `openclaw plugins install` | `npm install` + 配置 |
| 依赖 | 无（托管） | **Neo4j + Qdrant** | 无 | 无（本地 SQLite） |
| 数据落在 | MemOS Cloud | 你的服务器 | MemOS Cloud | 你的机器 |

**注意自托管的真实门槛：Neo4j + Qdrant 两套中间件**。这不是 `pip install` 就能跑的轻量方案。

### 3.3 `apps/` 下的四个下游集成（1,222 个文件，占仓库过半）

```
apps/MemOS-Cloud-OpenClaw-Plugin/   云端 OpenClaw 插件
apps/memos-local-openclaw/          本地 OpenClaw 插件
apps/memos-local-plugin/            本地插件核心（Hermes Agent + OpenClaw 共用）
apps/openwork-memos-integration/    openwork 集成
```

**`apps/` 占了整个仓库 53% 的文件量**——这说明 MemOS 的重心已经从"记忆库"转向"记忆插件分发"。它在打的是**接入位之战**：谁能成为主流 Agent 客户端的默认记忆后端。

### 3.4 本地插件的分层记忆模型（README 2026-05-09 更新）

```
L1 traces      ← 执行轨迹
L2 policies    ← 策略
L3 world models ← 世界模型
   ↓ 结晶化
crystallized Skills  ← 沉淀成技能
```

"self-evolving memory across L1 traces, L2 policies, L3 world models, and crystallized Skills" —— **从原始轨迹逐层抽象到可复用技能**，这是比"存对话+检索"高一个维度的记忆设计。

---

## 四、应用场景与启发

### 4.1 直接可用的场景

| 场景 | 匹配度 |
|------|-------|
| **给现有 Agent 加长期记忆** | ⭐⭐⭐⭐⭐ 四种接入形态覆盖从零运维到全自托管 |
| **OpenClaw / Hermes Agent 用户** | ⭐⭐⭐⭐⭐ 有官方插件，`openclaw plugins install` 即可 |
| **企业级、需数据不出境** | ⭐⭐⭐⭐ Self-Host 完整可用，但要自备 Neo4j + Qdrant |
| **多 Agent 共享/隔离记忆** | ⭐⭐⭐⭐ Multi-Cube 就是为此设计 |
| **客服/助理类需回溯历史工单** | ⭐⭐⭐⭐ README 明列此场景 |
| **研究 KV cache / LoRA 作为记忆载体** | ⭐⭐⭐⭐⭐ 全网少有的开源实现，`activation/vllmkv.py` + `parametric/lora.py` |
| **轻量个人项目** | ⭐⭐ 自托管太重；用 Local Plugin 或 Cloud API |

### 4.2 方法论启发

1. **"记忆"不该只有文本一种载体**。MemOS 把记忆切成 textual / activation(KV) / parametric(LoRA) 三层，对应"我记得这件事" / "我此刻脑子里装着这段上下文" / "这已经变成我的本能了"。这个三分法是**目前 AI 记忆领域最有解释力的抽象**，即便你不用 MemOS，设计自己的记忆系统时也该问：我的方案只做了哪一层？

2. **L1 traces → L2 policies → L3 world models → crystallized Skills 的结晶化路径**。这是"记忆如何变成能力"的可操作模型。大多数记忆系统止步于 L1（存日志）+ 检索，MemOS 明确了向上抽象的阶梯。

3. **图结构 + 可检视可编辑 > 黑盒向量库**。当记忆出错时，向量库你只能删了重建；图结构你能定位到具体节点改。这是**可运维性**的根本差异。

4. **`dream/` 模块的命名值得玩味**。类比睡眠期记忆巩固——离线做记忆整理/去重/抽象，而不是全在在线路径上做。这是把认知科学隐喻真正落成代码模块的罕见案例。

5. **异步摄入是生产化的分水岭**。MemScheduler 的存在意味着作者踩过"同步写记忆拖垮 QPS"的坑。任何要上生产的记忆系统都必须回答这个问题。

### 4.3 遇到什么问题该回来看这个仓库

- 「Agent 每次对话都失忆」→ 先看四种接入形态选一个
- 「想做 AI 记忆系统，不知道怎么分层」→ 看 `memories/` 的三分法 + L1→Skills 结晶路径
- 「记忆库越存越脏，检索质量下降」→ 看 `mem_feedback/`（自然语言纠错）和 `dream/`（离线巩固）
- 「KV cache 能不能当记忆用」→ `activation/kv.py`、`activation/vllmkv.py` 是可读的开源实现
- 「多 Agent 怎么共享记忆又不互相污染」→ `multi_mem_cube/`

---

## 五、官方性能数据（README 实录）

| Benchmark | Score |
|-----------|-------|
| LoCoMo | 88.83 |
| LongMemEval | 89.20 |
| PersonaMem v2 | 40.58 |
| HaluMem | 80.91 |
| BEAM-10M | 56.75 |
| GDPVal | 62.07 |
| LiveCodeBench | 64.96 |
| OmniMath | 61.00 |
| SWE-Bench | 38.46 |
| BrowseComp-Plus | 23.85 |

评测通过官方自建的 [OmniMemEval](https://github.com/MemTensor/OmniMemEval) 进行。

⚠️ **判读提示**：LoCoMo / LongMemEval 是**记忆专项**基准，88+ 分含金量高；但 LiveCodeBench / SWE-Bench / OmniMath 这些是**通用能力**基准，MemOS 作为记忆层的贡献比例难以从单个数字剥离——这些分数更多反映"底座模型 + MemOS"的组合表现。另外评测方 = 项目方（OmniMemEval 也是 MemTensor 出品），**自建 benchmark 自报 SOTA 需要打折看**，建议以第三方复现为准。

**相对可信的一条**：OpenClaw 五项 Agent 任务平均完成率 36.63% → 50.87%。这是端到端任务指标，比检索指标更难灌水。

---

## 六、社区口碑

- **⭐ 10,587 / 🍴 976**，Fork/Star 比 9.2% 偏高，说明**实际动手接入的人多**（记忆系统需要改配置、跑自托管，天然产生 fork）。
- **issue 编号已到 1667+**，活跃度高。
- **高赞 issue 揭示的真实坑**：
  - `#1298 fix: 系统注入的 boot / auto-recall prompt 和 NO_REPLY 会被写进记忆库` — ⚠️ **记忆污染的经典 bug**：系统自己注入的 prompt 反过来被当成用户记忆存了。任何做记忆系统的人都会撞上这个，值得专门看修复方案。
  - `#1199 memos-local-openclaw on Windows: better-sqlite3 path detection fails and viewer may not auto-start` — ⚠️ **Windows 支持薄弱**，better-sqlite3 原生模块路径检测失败。Windows 用户注意。
  - `#1667 fix(memos-local-plugin): harden hermes bridge lifecycle` — Hermes 桥接生命周期需加固。
  - `#1433 feat: 希望 openclaw 插件新增对自托管部署的 MemOS 的 api 支持` — ⚠️ 说明**OpenClaw 插件曾只支持云端，自托管用户被卡住**，是社区推动补上的。
  - `#30 How do you do the OpenAI LoCoMo evaluation?` — 早期就有人追问评测复现方法。
- **中文 issue 占比可观**（#1298、#1433 均为中文），说明中文社区是主力用户群之一。README 有 `README_ZH.md`。
- **仓库内有 `CLAUDE.md` / `AGENTS.md` / `.claude/` / `.codex/`** — 项目自身也在用 AI 编码 Agent 开发。

---

## 七、竞品对比

| 方案 | 定位 | 相对 MemOS |
|------|------|-----------|
| **mem0** | 最流行的 AI 记忆层 | 更轻、更易上手、生态更广；但**只做文本记忆**，无 KV/LoRA 层，记忆结构不如 MemOS 可检视 |
| **Zep / Graphiti** | 时序知识图谱记忆 | 图结构思路相近，时序建模更强；MemOS 胜在多模态 + 三类记忆 + 插件分发 |
| **Letta（原 MemGPT）** | 有状态 Agent + 记忆分层 | 概念先驱（虚拟上下文管理），MemOS 的工程完备度和 benchmark 覆盖更全 |
| **LangMem / LlamaIndex Memory** | 框架内置记忆模块 | 绑定框架，能力较基础；MemOS 是独立可插拔的记忆后端 |
| **Cognee** | 记忆 + 知识图谱 | 定位接近，社区规模小于 MemOS |
| **VictorTaelin/OptMem**（[已入库](VictorTaelin-OptMem-深度调研.md)） | 极简只追加记忆 | 单文件零依赖 vs MemOS 的重型系统——**光谱两端**。小项目选 OptMem，企业选 MemOS |
| **各家原生 memory**（ChatGPT/Claude 记忆） | 闭源托管 | 不可自托管、不可检视；MemOS 主打开放可控 |

**MemOS 的独特位**：唯一同时覆盖**文本 + KV cache + LoRA** 三类记忆载体的开源项目，且已经把插件铺到 OpenClaw / Hermes 两个主流 Agent 客户端。

---

## 八、核心研判

### ✅ 优势
1. **三类记忆的抽象（textual/activation/parametric）是当前 AI 记忆领域最完整的**，有论文（arXiv:2507.03724）背书，不是拍脑袋。
2. **图结构可检视可编辑**，比黑盒向量库在运维层面强一个量级。
3. **MemScheduler 异步摄入**说明经过生产化打磨。
4. **`apps/` 占 53% 文件量** = 已经在打接入位之战，四种形态覆盖全谱系用户。
5. **L1→L2→L3→Skills 的结晶化路径**是"记忆如何变成能力"的可操作模型。
6. **OpenClaw 任务完成率 36.63%→50.87%** 是端到端硬指标。

### ⚠️ 风险与保留
1. **⚠️ 自建 benchmark 自报 SOTA**。OmniMemEval 由 MemTensor 自己出品，"领先 14 个商业记忆产品"的结论缺乏第三方复现。**采信前应自行在业务数据上评测**。
2. **自托管门槛高**：Neo4j + Qdrant 两套中间件，不是轻量方案。团队要评估运维成本。
3. **⚠️ 记忆污染 bug 有前科**（#1298：系统 prompt 和 `NO_REPLY` 被写进记忆库）。虽已修复，但说明"什么该记什么不该记"的边界判定是这类系统的固有难点，接入后需自行监控记忆库质量。
4. **Windows 支持薄弱**（#1199：better-sqlite3 路径检测失败、viewer 不自启）。Windows 本地插件用户需有心理准备。
5. **云端优先的产品倾向**。OpenClaw 插件最初只支持 MemOS Cloud，自托管 API 支持是社区提 issue（#1433）推动的。**注意开源版与云服务的能力差**——这是"开源引流 + 云端变现"的典型结构，长期需关注开源版是否被有意弱化。
6. **仓库巨大**（2,320 文件，`apps/` 占 1,222），初次阅读成本高。想读核心只需看 `src/memos/memories/` 和 `mem_scheduler/`。

### 🎯 一句话研判
**MemOS 是目前对"AI 记忆"这件事想得最全的开源项目**——文本 / KV cache / LoRA 三层抽象加上 L1→Skills 结晶路径，把记忆从"存对话再检索"提升到了系统设计层面。但它同时也是**最重的**：自托管要 Neo4j + Qdrant，benchmark 是自家的，云端产品化倾向明显。**建议路径**：先用 Local Plugin 或 Cloud API 试水验证收益，确认有效再评估自托管；采信性能数字前务必自测。想学思路的话，`src/memos/memories/` 的三分法值得每个做记忆系统的人读一遍。

---

## 九、关键文件路径速查

| 路径 | 说明 |
|------|------|
| `src/memos/memories/` | ⭐⭐ 三类记忆抽象总入口，全库最值得读的目录 |
| `src/memos/memories/textual/tree.py` / `simple_tree.py` | 树形文本记忆实现 |
| `src/memos/memories/textual/preference.py` | 偏好记忆 |
| `src/memos/memories/activation/kv.py` / `vllmkv.py` | ⭐ **KV cache 作为记忆**的开源实现（vLLM 对接） |
| `src/memos/memories/parametric/lora.py` | ⭐ **LoRA 作为参数记忆** |
| `src/memos/mem_scheduler/base_scheduler.py` | 异步调度器基类 |
| `src/memos/mem_scheduler/memory_manage_modules/activation_memory_manager.py` | 激活记忆管理 |
| `src/memos/mem_cube/` / `multi_mem_cube/` | 记忆立方与多 cube 编排 |
| `src/memos/dream/` | ⭐ 疑似离线记忆巩固（睡眠隐喻） |
| `src/memos/mem_feedback/` | 自然语言反馈修正记忆 |
| `src/memos/search/` + `reranker/` | 混合检索 + 重排 |
| `src/memos/graph_dbs/` + `vec_dbs/` | Neo4j / Qdrant 双后端 |
| `apps/memos-local-plugin/` | ⭐ 本地插件核心（Hermes + OpenClaw 共用，L1-L3+Skills 分层实现处） |
| `apps/MemOS-Cloud-OpenClaw-Plugin/` | 云端 OpenClaw 插件 |
| `evaluation/` | 评测脚本（61 文件） |
| `deploy/` + `docker/` + `Dockerfile` | 自托管部署（含 Neo4j + Qdrant compose） |
| `README_ZH.md` | 中文 README |
| `CLAUDE.md` / `AGENTS.md` | 项目自身的 AI 编码规范（吃狗粮证据） |

---

> **调研方法**：GitHub API 拉取仓库元数据 / 完整文件树（2,320 项）/ README（15.4KB）/ 按 reactions 排序的 issue 列表。三类记忆分层、`dream/` 模块、`apps/` 占比 53% 等发现均为文件树实证；性能数字引自 README 官方表格并附判读警示。
