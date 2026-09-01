# 🔬 topoteretes/cognee — 全方位深度调研

> 调研日期：2026-09-02 ｜ 星标：30,395 ⭐ ｜ Fork：2,987 ｜ 开放 Issue：486 ｜ 语言：Python ｜ 协议：Apache-2.0 ｜ 默认分支：main ｜ 创建：2023-08-16 ｜ 最新版本：**v1.5.3（2026-08-23）** ｜ 状态：**高度活跃**（pushed 2026-09-01）

## 📌 项目定位

`topoteretes/cognee` 是**面向 AI Agent 的开源"记忆平台"**：把非结构化输入（文档、对话、代码、网页）经 ECL 管线（Extract → Cognify → Load）转成**知识图谱 + 向量索引的混合表示**，让 Agent 跨会话拥有可检索、可溯源、可修正的长期记忆。自托管，Apache-2.0。

> **核心判断**：cognee 与"又一个 RAG 库"的本质区别在于它把记忆当作**有生命周期的数据资产**来建模——不只有写入和检索，还有 `improve`（改进）、`forget`（遗忘）、`provenance`（溯源）、`session_distillation`（会话蒸馏）、`temporal_graph`（时序图）。它真正对标的不是 LangChain 的 retriever，而是 Mem0 / Zep(Graphiti) / Letta 这一层的记忆基础设施——**并且它内置了从这三家迁移数据的适配器**，这是极强的竞争意图信号。

## 🏆 项目亮点（差异化）

1. **V1 / V2 双 API 并行**：V1 是数据管线视角（`add` / `cognify` / `search`），V2 是记忆视角（`remember` / `recall` / `improve` / `forget`）。同一内核两套心智模型，老用户不断裂、新用户不用先学管线概念。
2. **内置竞品迁移适配器**：`cognee.migration` 明确提供 `Mem0Source` / `ZepSource`(GraphitiSource) / `LettaSource` / `COGXArchiveSource`——直接把"从竞品搬过来"做成一等公民能力。
3. **记忆溯源（provenance）是独立子系统**：`modules/provenance` + `infrastructure/databases/provenance` + `visualize_memory_provenance()`，可回答"这条记忆是从哪份文档、哪一步推理来的"。多数记忆库只给相似度分数，给不出来源链。
4. **`memify` 与自定义管线**：除标准 `cognify`，还提供 `memify` 与 `run_custom_pipeline` + `Drop` 原语，允许用户自定义记忆加工流程，而非被框架的固定流程锁死。
5. **数据库全栈可插拔**：`infrastructure/databases/` 下并列 `graph` / `vector` / `relational` / `hybrid` / `postgres` / `cache` / `unified` / `provenance`，图库支持含 Kuzu（仓库有独立 `kuzu/` 目录）。
6. **面向 Agent 的运行时装饰器**：`modules/agent_memory/{decorator.py, runtime.py, sanitization.py}`——把记忆能力以装饰器注入 Agent 函数，并内置**输入净化**（sanitization），说明作者意识到记忆写入是攻击面。
7. **评测体系内建**：仓库根目录有 `evals/`，包内有 `eval_framework/` 与 `metrics/`。记忆质量可量化，不靠 demo 截图说话。
8. **交付形态齐全**：`cognee-mcp`（MCP server）、`cognee-frontend`、`cognee-starter-kit`、`distributed/`、`deployment/`、`docker-compose.yml`、`notebooks/`——从 notebook 试用到分布式部署全覆盖。

## 🏗️ 核心架构（克制版）

```
输入：文档 / 对话 / 代码 / 网页
   │
   ▼  ── cognee.add() ──────────────────────────────────
┌──────────────────────────────────────────────────────┐
│ tasks/ingestion · tasks/documents · tasks/web_scraper │  Extract
│ infrastructure/loaders · files                        │
└───────────────┬──────────────────────────────────────┘
                ▼  ── cognee.cognify() / memify() ──────
┌──────────────────────────────────────────────────────┐
│ tasks/chunks   → 分块                                 │
│ tasks/graph    → 实体/关系抽取，建图                    │  Cognify
│ tasks/summarization · entity_completion                │
│ tasks/temporal_graph · temporal_awareness → 时序建模    │
│ modules/ontology → 本体约束      provenance → 溯源链    │
└───────────────┬──────────────────────────────────────┘
                ▼  ── Load ────────────────────────────
┌──────────────────────────────────────────────────────┐
│ infrastructure/databases/                             │
│   graph(含 Kuzu) │ vector │ relational │ hybrid       │
│   postgres │ cache │ provenance │ unified            │
└───────────────┬──────────────────────────────────────┘
                ▼  ── 检索 ────────────────────────────
┌──────────────────────────────────────────────────────┐
│ V1: search(SearchType)   modules/search + retrieval   │
│ V2: recall()             modules/recall               │
│ 生命周期: improve / forget / push / export             │
│ 会话: session_lifecycle · session_distillation         │
└───────────────┬──────────────────────────────────────┘
                ▼
   出口： Python SDK │ cognee-mcp (MCP) │ REST(api/v1) │ frontend UI
   横切： observability/trace_context · logging · sync · cloud
```

**架构要点**：`cognee/modules/` 有 30 个子模块，`cognee/tasks/` 有 18 类任务。这个"modules（能力域）× tasks（可编排步骤）"的二维切分，是它能同时支撑固定管线与自定义管线的结构原因。

## 💡 应用场景与启发（重点）

**什么时候该去翻这个仓库？**

- **要给 Agent 加长期记忆时**：这是最直接的场景。相比自己拿向量库 + 手写 prompt 拼接，cognee 提供了完整的记忆生命周期（写入/检索/改进/遗忘/溯源）。
- **要做知识图谱 + 向量的混合检索（GraphRAG）时**：`infrastructure/databases/hybrid` 与 `modules/retrieval` 是现成的工程实现，省掉自己缝合图库与向量库的脏活。
- **要回答"这个答案凭什么"时**：provenance 子系统是本仓库最值得单独学习的部分。任何需要**可审计 AI**（医疗、法务、金融、企业内知识）的系统都该参考它的溯源链建模。
- **要设计"可遗忘"的数据系统时**：`forget` 作为一等 API + `tasks/cleanup`，对应 GDPR/隐私删除需求。多数 RAG 系统的删除是"删向量条目"，而记忆图谱里删一个实体会牵连关系——cognee 被迫正面解决了这个问题。
- **要做会话压缩 / 上下文工程时**：`session_distillation` + `session_lifecycle` 提供了"长对话 → 精炼记忆"的落地实现，这正是当前 Agent 上下文窗口焦虑的核心解法。
- **要设计双 API 平滑演进时**：V1/V2 并存（而非破坏性重写）是很好的 API 演进范本——`__init__.py` 里用注释块清晰分区，老 API 不动、新 API 另起心智模型。
- **迁移场景**：已在用 Mem0 / Zep / Letta 但想自托管、想要图谱与溯源 → 直接看 `cognee.migration` 的四个 Source 适配器。

**启发式结论**：cognee 给同类需求带来的最大解决思路是——**把"记忆"从检索问题重构为数据生命周期问题**。一旦这样建模，improve / forget / provenance / distillation 就成了必然产物，而不是事后补丁。

## 🧠 源码深度解读（3 个核心模块）

### 1) 公共 API 的双轨分层 — `cognee/__init__.py`

真实抓取的文件本身就是最好的架构文档（作者用注释块显式分区）：

```python
"""Public Python API for Cognee.
...groups the stable V1 API, memory-oriented V2 API, visualization helpers,
tracing utilities, migration helpers, and session models behind a single
package-level entrypoint.
"""
# --- V1 API -------------------------------------------------
from .api.v1.add import add
from .api.v1.cognify import cognify
from .api.v1.search import SearchType, search
from .modules.memify import memify
from .modules.run_custom_pipeline import run_custom_pipeline
from .api.v1.visualize import (visualize_graph, get_memory_provenance_graph,
                               visualize_memory_provenance, get_schema_inventory)

# --- V2 memory-oriented API ---------------------------------
from .api.v1 import (remember, RememberResult, recall, improve, forget,
                     serve, disconnect, visualize, push, PushResult,
                     export, ExportResult)
from .memory import MemoryEntry, QAEntry, TraceEntry, FeedbackEntry

# 竞品迁移：Mem0Source, ZepSource/GraphitiSource, LettaSource, COGXArchiveSource
from . import migration
```

三处值得学的工程细节：
- **`__version__` 必须在文件最顶部**，作者留了注释说明原因（否则循环导入）——真实项目的踩坑记录直接写进代码。
- **`dotenv.load_dotenv(override=True)` 在 logging 初始化之前**，因为 `LOG_LEVEL` 要先就位。启动顺序被显式管理。
- **`MemoryEntry / QAEntry / TraceEntry / FeedbackEntry` 四种记忆类型**：说明记忆不是一坨文本，而是有类型的结构体（尤其 `FeedbackEntry` —— 反馈也是记忆，这是 `improve` 能工作的前提）。

### 2) 存储抽象层 — `cognee/infrastructure/databases/`

真实子目录清单：

```
graph/        vector/       relational/    hybrid/
postgres/     cache/        provenance/    unified/
dataset_database_handler/  dataset_queue/  exceptions/  utils/
```

关键研判：
- **`hybrid/` 与 `unified/` 并存**说明它经历过演进——先有图/向量各自适配，再有 hybrid 缝合，最后抽出 unified 统一门面。这是存储抽象的典型成熟路径。
- **`provenance/` 是独立数据库层**而非某张附属表 → 溯源被当作与主数据平级的关注点。
- **`dataset_queue/` + `dataset_database_handler/`** → 多数据集（多租户/多 Agent）隔离是内建的，不是靠命名前缀凑。
- 仓库根目录独立 `kuzu/` 目录 + `cognee_db_workers/`：嵌入式图库 Kuzu 被特殊对待，并有独立 worker 进程模型。

### 3) Agent 记忆注入与安全边界 — `cognee/modules/agent_memory/`

仅四个文件，但信息量极大：

```
decorator.py       # 以装饰器把记忆能力挂到 Agent 函数上
runtime.py         # 运行时上下文（会话、数据集、追踪）
sanitization.py    # ⚠️ 写入前净化
__init__.py
```

**`sanitization.py` 的存在是本次调研最有价值的发现之一**：记忆系统的写入路径是被长期忽视的攻击面——如果 Agent 把用户输入原样写进长期记忆，攻击者就能投毒（memory poisoning），后续所有会话都会读到被污染的"事实"。cognee 把净化放在 agent_memory 模块内、与装饰器同级，说明这是设计时就考虑的边界而非事后补丁。

配套横切能力：`modules/observability/trace_context.py` 提供 `enable_tracing`，`modules/recall/{config,methods,types}` 与 `modules/search/{methods,models,operations,types}` 结构对称——V1 search 与 V2 recall 是平行实现而非一个包另一个。

## 🌐 社区口碑与维护现状

| 信号 | 实测值 |
|---|---|
| 星标 / Fork | 30,395 ⭐ / 2,987 |
| 最新版本节奏 | v1.5.3（2026-08-23）、v1.5.2（08-22）、v1.5.1（08-21）、v1.5.0.dev5（08-20）、v1.5.3.dev1（08-26） |
| 最后推送 | 2026-09-01（调研当日） |
| 开放 Issue | 486 |
| 仓库体积 | 236.7 MB |
| 协作规范 | `CONTRIBUTING.md` / `CODE_OF_CONDUCT.md` / `DCO.md` / `SECURITY.md` 等治理文件齐全 |
| 工程化 | `.pre-commit-config.yaml`、`.coderabbit.yaml`(AI 代码审查)、`.mergify.yml`(自动合并)、`.gitguardian.yml`(密钥扫描)、`.devcontainer`、`mise.toml` |
| Topics | 含 `good-first-issue` / `good-first-pr` / `help-wanted` / `contributions-welcome` |
| AI 协作 | 根目录有 `AGENTS.md` + `CLAUDE.md`，包内有 `cognee/skill.md` |

**研判**：**发版节奏极快（三天内连发 v1.5.1/1.5.2/1.5.3）**，配合 dev 预发布通道，说明处于高速迭代期——好处是功能新，代价是 API 稳定性风险，生产环境务必锁定小版本。治理工具链（GitGuardian 密钥扫描 + Mergify + CodeRabbit + DCO）在同规模开源项目中属于上游水平，说明团队有商业化投入（官网 cognee.ai）。Topics 大量标注 `good-first-issue` / `help-wanted`，是主动经营外部贡献者的信号。

⚠️ 观察到的"施工中"痕迹：根目录存在 `RECALL_TOOL_CALLS_PLAN.md`、`SESSION_POSTGRES_CACHE_PLAN.md`、`pr_body.md`，以及 `logs/` 目录被提交进仓库——设计文档与临时文件混在根目录，是快速迭代的副作用。

## ⚔️ 竞品对比

| 项目 | 记忆范式 | 相对 cognee 优势 | 相对劣势 |
|---|---|---|---|
| **Mem0** | 向量 + LLM 抽取事实 | 上手极快、API 极简、托管服务成熟 | 图谱与溯源弱，复杂关系推理受限 |
| **Zep / Graphiti** | 时序知识图谱 | 时序建模成熟、企业级托管 | 自托管灵活度与可插拔存储不如 cognee |
| **Letta（原 MemGPT）** | Agent 操作系统 + 记忆分页 | Agent 状态机完整、记忆编辑范式清晰 | 更偏 Agent 框架，作为独立记忆层复用性弱 |
| **LlamaIndex / LangChain** | 通用 RAG 编排 | 生态与连接器最广 | 记忆是能力之一，无生命周期/溯源一等公民 |
| **Graphiti + 自建向量库** | 自行缝合 | 完全可控 | 全部工程量自负（cognee 已把这条路走完） |

**选型结论**：要最快接一个记忆能力 → Mem0；要企业托管 + 时序 → Zep；要 Agent OS → Letta；**要自托管 + 知识图谱 + 溯源可审计 + 存储可插拔 → cognee**。cognee 内置四个竞品迁移适配器，事实上把自己定位为"这一层的最终形态"。

## 🎯 核心研判

- **采用建议**：适合**需要自托管、需要溯源可审计、记忆关系复杂**的 Agent 系统（企业知识助手、法务/医疗/科研 Agent、代码库记忆）。若只需"记住用户偏好"这种轻量场景，cognee 的图谱管线属于过度工程，Mem0 更合适。
- **最大风险（三条）**：
  1. **API 稳定性**：三天连发三个 patch 版 + dev 通道并行，v1.5.x 仍在快速变形。生产必须锁版本并跟踪 breaking change。
  2. **运维复杂度**：图库 + 向量库 + 关系库 + 缓存四类存储，236MB 仓库、独立 `cognee_db_workers` 与 `distributed/`，自托管运维成本远高于单一向量库。先用 `docker-compose.yml` 或 `cognee-starter-kit` 验证再上生产。
  3. **记忆投毒攻击面**：虽有 `sanitization.py`，但记忆系统天生是持久化攻击面——被污染的记忆会跨会话反复生效。开放给终端用户写入前必须自建审计与回滚（好在 provenance 让回滚可定位）。
- **借鉴价值（可直接迁移）**：① 把记忆建模为生命周期（write/recall/improve/forget）而非仅检索；② provenance 作为平级子系统 + 可视化溯源图；③ V1/V2 双 API 并行的非破坏性演进；④ 记忆写入前 sanitization 的安全意识；⑤ modules（能力域）× tasks（可编排步骤）的二维代码切分；⑥ 内置竞品迁移适配器作为增长策略。
- **一句话**：cognee 把 AI 记忆从"向量检索"升级为"有溯源、可改进、可遗忘的数据生命周期"，是自托管 Agent 记忆基础设施里工程完成度最高的一个；代价是运维复杂度与高速迭代带来的 API 波动。

## 📂 关键文件路径速查

| 路径 | 作用 |
|---|---|
| `cognee/__init__.py` | **公共 API 全景**，V1/V2 分区、迁移入口、四种记忆类型 |
| `cognee/api/v1/` | REST + SDK 端点实现（add/cognify/search/remember/recall/…） |
| `cognee/modules/`（30 子模块） | 能力域：`recall` `search` `retrieval` `provenance` `ontology` `memify` `agent_memory` `session_distillation` `session_lifecycle` `observability` `sync` `cloud` 等 |
| `cognee/modules/agent_memory/{decorator,runtime,sanitization}.py` | Agent 记忆注入 + **写入净化（安全边界）** |
| `cognee/modules/provenance/` | 记忆溯源链核心 |
| `cognee/tasks/`（18 类） | 可编排步骤：`chunks` `graph` `ingestion` `summarization` `temporal_graph` `temporal_awareness` `entity_completion` `web_scraper` `code_graph` `codingagents` `cleanup` 等 |
| `cognee/infrastructure/databases/` | 存储抽象：`graph`/`vector`/`relational`/`hybrid`/`postgres`/`cache`/`provenance`/`unified` |
| `cognee/infrastructure/llm/` · `loaders/` · `locks/` | LLM 抽象、加载器、并发锁 |
| `cognee/modules/search/types/SearchType.py` | 检索类型枚举（决定 search 行为的关键） |
| `cognee/eval_framework/` · `evals/` · `cognee/modules/metrics/` | 记忆质量评测体系 |
| `cognee-mcp/` | MCP server（接入 Claude/IDE 等） |
| `cognee-frontend/` · `cognee/api/v1/ui` | Web UI |
| `cognee-starter-kit/` · `notebooks/` · `examples/` | 最小可跑起点（**建议从这里入门**） |
| `distributed/` · `deployment/` · `docker-compose.yml` · `Dockerfile` | 分布式与部署 |
| `kuzu/` · `cognee_db_workers/` | 嵌入式图库与 DB worker |
| `cognee/migration/` | Mem0 / Zep(Graphiti) / Letta / COGXArchive 迁移适配器 |
| `cognee/alembic/` · `run_migrations.py` | 数据库 schema 迁移 |
| `AGENTS.md` · `CLAUDE.md` · `cognee/skill.md` | AI 协作约定 |

## 🧪 研究方法与数据来源

- GitHub API 元数据：stars 30,395 / forks 2,987 / open issues 486 / Apache-2.0 / main / size 236,720KB / homepage cognee.ai / 19 个 topics
- `git/trees` + `contents` API 真实抓取：根目录、`cognee/`、`cognee/modules/`（30 项）、`cognee/tasks/`（18 项）、`cognee/infrastructure/`、`infrastructure/databases/`、`cognee/api/`、`modules/{recall,agent_memory,search}`、`cognee-mcp/`、`cognee/pipelines/`
- `cognee/__init__.py` 源码实抓（docstring、V1/V2 导入分区、migration、memory 类型、启动顺序注释）
- Releases API：v1.5.3 / v1.5.3.dev1 / v1.5.2 / v1.5.1 / v1.5.0.dev5 及发布日期
- 治理与工程化文件清单实抓（pre-commit / coderabbit / mergify / gitguardian / devcontainer / mise / DCO / SECURITY）
- 未引用任何无法核实的第三方评测数字；竞品对比基于公开定位与本仓库 `migration` 适配器所指向的对象
