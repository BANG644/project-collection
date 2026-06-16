# 📊 microsoft/graphrag — 全方位深度调研报告

> **调研日期：** 2026-06-16
> **GitHub：** https://github.com/microsoft/graphrag
> **Stars：** ⭐ 33,787 | **Forks：** 3,584
> **语言：** Python | **许可证：** MIT
> **最新版本：** v3.1.0 (2026-05-28)

---

## 1. 🏗️ 项目架构全景

### 1.1 定位与价值主张

GraphRAG 是微软研究院推出的**模块化图结构检索增强生成（RAG）系统**，核心创新在于用**知识图谱**替代传统向量检索作为 RAG 的中间表示层。它不是简单的工具，而是一套从「非结构化文本 → 知识图谱 → 层次化社区摘要 → 多种查询策略」的完整数据流水线。

### 1.2 核心架构图（逻辑分层）

```
┌────────────────────────────────────────────────────────┐
│                   用户接口层 (CLI / API)                 │
│    graphrag query --method local/global/drift/basic    │
├────────────────────────────────────────────────────────┤
│                   查询策略层 (Search)                    │
│   LocalSearch    GlobalSearch    DRIFTSearch   BasicSearch
├────────────────────────────────────────────────────────┤
│                   上下文构建层 (Context Builder)         │
│    LocalContextBuilder   GlobalContextBuilder           │
│    DynamicCommunitySelection                            │
├────────────────────────────────────────────────────────┤
│                   索引流水线 (Index Pipeline)            │
│  TextSplit → GraphExtract → Summarize → Cluster →     │
│  CommunityReport → EmbedText                           │
├────────────────────────────────────────────────────────┤
│                   存储抽象层 (Storage)                   │
│   TableProvider (Parquet)   VectorStore (LanceDB)      │
│   Cache (LRU/Disk)   Blob Storage                     │
├────────────────────────────────────────────────────────┤
│                   模型适配层 (LLM)                       │
│   CompletionModel   EmbeddingModel   Tokenizer         │
│   支持 OpenAI / Azure / Ollama / 自定义                │
└────────────────────────────────────────────────────────┘
```

### 1.3 索引流水线（Pipeline）详解

GraphRAG 定义了多种预置 Pipeline，核心是 **Standard** 和 **Fast** 两种索引策略：

| 阶段 | 工作流名称 | 功能 | Standard | Fast |
|------|-----------|------|----------|------|
| 1 | load_input_documents | 加载输入文档 | ✅ | ✅ |
| 2 | create_base_text_units | 文本分块 | ✅ | ✅ |
| 3 | create_final_documents | 文档元数据最终化 | ✅ | ✅ |
| 4 | extract_graph | LLM 抽取实体+关系+总结 | ✅ | ❌ |
| 5 | extract_graph_nlp | NLP 方式抽取（更快） | ❌ | ✅ |
| 6 | finalize_graph | 图最终化（去重+融合） | ✅ | ✅ |
| 7 | extract_covariates | 提取声明/协变量 | ✅ | ❌ |
| 8 | prune_graph | 图剪枝 | ❌ | ✅ |
| 9 | create_communities | 社区检测（Leiden） | ✅ | ✅ |
| 10 | create_final_text_units | 文本单元最终化 | ✅ | ✅ |
| 11 | create_community_reports | LLM 生成社区报告 | ✅ | ❌ |
| 12 | create_community_reports_text | 文本版社区报告 | ❌ | ✅ |
| 13 | generate_text_embeddings | 生成向量嵌入 | ✅ | ✅ |

**独家发现**：v3.0+ 的最大架构变化是**将存储抽象为独立包**（`graphrag_storage`、`graphrag_cache`），使索引可以跑在 Azure、本地文件、Cosmos DB 等多种后端上，且支持增量索引（`update_*` 工作流系列）。

### 1.4 四种查询策略对比

| 策略 | 适用问题类型 | 核心机制 | 成本 |
|------|------------|---------|------|
| **Local Search** | 具体实体/局部问题 | 从关联实体+社区+协变量构建上下文，单轮 LLM 回答 | 低 |
| **Global Search** | 全局性/主题性问题 | Map-Reduce：多路并行生成社区答案→排序→归约 | 高 |
| **DRIFT Search** | 复杂多跳推理 | 动态社区选择+条件搜索，先粗略再精细 | 中 |
| **Basic Search** | 简单事实查询 | 纯向量相似度检索+LLM 回答 | 最低 |

---

## 2. 🔍 核心源码深度解读

### 2.1 `__main__.py` — 入口点

```python
"""The GraphRAG package."""
from graphrag.cli.main import app
app(prog_name="graphrag")
```

极简入口，所有 CLI 路由由 Typer 框架自动生成，实际逻辑在 `cli/main.py`。

### 2.2 `PipelineFactory` — 流水线工厂（核心架构决策）

**文件：** `packages/graphrag/graphrag/index/workflows/factory.py`

这是 GraphRAG v3 最关键的架构设计——**可插拔工作流注册表**：

```python
class PipelineFactory:
    workflows: ClassVar[dict[str, WorkflowFunction]] = {}
    pipelines: ClassVar[dict[str, list[str]]] = {}
```

- **`register()`** — 允许用户注册自定义工作流函数
- **`register_pipeline()`** — 允许用户定义全新的 Pipeline（工作流组合）
- 默认注册 4 种 Pipeline：Standard、Fast、StandardUpdate、FastUpdate

**设计模式分析：**
- 采用**注册表模式 + 策略模式**的组合
- 工作流是**独立的异步函数**，通过名称解耦
- Pipeline 是工作流名称的有序列表，运行时按序执行
- 支持自定义覆盖：`config.workflows` 可以完全替换内置定义

**代码骨架：**
```python
# 注册流程
PipelineFactory.register_pipeline(IndexingMethod.Standard, [
    "load_input_documents", *standard_workflows
])

# 执行流程
for name, workflow_function in pipeline.run():
    result = await workflow_function(config, context)
```

### 2.3 `GraphRagConfig` — 配置模型（Pydantic 深度嵌套）

**文件：** `packages/graphrag/graphrag/config/models/graph_rag_config.py`

这是项目中最复杂的类，包含 **20+ 嵌套子配置模型**：

| 子配置 | 类型 | 作用 |
|--------|------|------|
| `completion_models` | `dict[str, ModelConfig]` | 多模型配置（支持不同任务用不同模型） |
| `embedding_models` | `dict[str, ModelConfig]` | 嵌入模型配置 |
| `input / input_storage` | `InputConfig / StorageConfig` | 输入源配置（文件/Azure Blob 等） |
| `chunking` | `ChunkingConfig` | 文本分块参数 |
| `extract_graph` | `ExtractGraphConfig` | 图抽取参数（实体类型、最大 gleanings） |
| `summarize_descriptions` | `SummarizeDescriptionsConfig` | 描述总结参数 |
| `community_reports` | `CommunityReportsConfig` | 社区报告生成参数 |
| `local_search / global_search` | `SearchConfig` | 各搜索策略参数 |
| `vector_store` | `VectorStoreConfig` | 向量存储（默认 LanceDB） |
| `table_provider` | `TableProviderConfig` | 表格存储（Parquet/Cosmos） |

**独家发现**：通过 `get_completion_model_config()` 和 `get_embedding_model_config()` 方法，GraphRAG 支持**任务级模型隔离**——图抽取、总结、社区报告生成可以使用不同的 LLM 配置（如抽取用 GPT-4o，总结用 GPT-4o-mini 省钱）。

### 2.4 `run_pipeline` — 流水线执行器

**文件：** `packages/graphrag/graphrag/index/run/run_pipeline.py`

核心执行逻辑，关键设计：
1. **状态持久化**：每次执行会 dump `context.json` 和 `stats.json` 到 output_storage，支持断点恢复
2. **增量索引**：`is_update_run=True` 时走增量路径，复制旧索引到 `previous/` 子目录，新数据写入 `delta/`，最后合并
3. **流式输出**：使用 `AsyncIterable[PipelineRunResult]` 实现流式结果返回

```python
async for table in _run_pipeline(pipeline, config, context):
    yield table  # 每个工作流结果实时流出
```

### 2.5 `LocalSearch.search()` — 本地搜索实现

**模式分析：**
1. 调用 `context_builder.build_context()` 获取关联实体+社区报告+协变量
2. 拼装 system prompt（含上下文数据）
3. 单次 LLM 调用（流式）生成回答
4. 返回完整 SearchResult（含 tokens 统计、耗时、上下文数据）

**设计亮点**：所有指标（llm_calls、prompt_tokens、output_tokens）按阶段（`build_context` / `response`）分类统计，方便成本追踪。

### 2.6 `GlobalSearch.search()` — 全局搜索实现

**Map-Reduce 双阶段模式：**

```
Phase 1 — Map:
  ┌─ Community Report Batch 0 → LLM → {answer, score}
  ┌─ Community Report Batch 1 → LLM → {answer, score}
  ┌─ Community Report Batch N → LLM → {answer, score}
  (使用 asyncio.gather + Semaphore 控制并发)

Phase 2 — Reduce:
  收集所有 answers → 按 score 排序 → 截断到 max_data_tokens →
  拼装成 reduce prompt → LLM 流式生成最终回答
```

**独家发现**：Reduce 阶段的排序+截断逻辑是性能关键。如果所有 map 响应 score 都为 0（无相关信息），系统返回 `NO_DATA_ANSWER` 而非试图编造，这是负责任 AI 的设计体现。

### 2.7 `extract_graph` — 图抽取工作流

**工作流模式：**
1. 从 parquet 读取 text_units
2. 创建两个 LLM 实例（抽取用 + 总结用，可不同模型）
3. `extract_graph()` 对每个 text_unit 执行 LLM 抽取 → 实体+关系
4. 如果无实体或无关系 → **抛出 ValueError**（硬失败，防止空图）
5. `summarize_descriptions()` 对抽取结果进行 LLM 总结
6. 保留 raw 版本（用于 debug）+ 写回 parquet

---

## 3. 🌐 全网口碑画像

### 3.1 正面评价（综合中英文社区）

| 来源 | 观点 | 链接 |
|------|------|------|
| 知乎 zhuanlan | 有效解决传统 RAG「无法串点成线」的全局性问题 | [链接](https://zhuanlan.zhihu.com/p/707882203) |
| 微软官方博客 | 动态社区选择降低 77% tokens 成本 | [链接](https://www.microsoft.com/en-us/research/blog/) |
| CSDN 社区 | 「GraphRAG 为 RAG 全局摘要设定了新标准」 | [链接](https://blog.csdn.net/) |
| Filipe Calegario | 「在需要跨文档推理的场景下 GraphRAG 优于 naive RAG」 | [链接](https://www.sohu.com/a/) |

### 3.2 批评与局限

| 问题 | 严重程度 | 详情 |
|------|---------|------|
| **成本极高** | 🔴 严重 | 全文索引时 token 消耗巨大，尤其 Standard 模式的 LLM 图抽取 |
| **速度慢** | 🟡 中等 | 索引流程长，社区报告生成是大头 |
| **评估困难** | 🟡 中等 | 缺乏公认的 GraphRAG 质量评估指标 |
| **本地模型兼容性差** | 🟡 中等 | Ollama 本地模型常出现 JSON 解析错误（issue #575） |
| **配置复杂** | 🟢 较轻 | 20+ 嵌套配置项，新手容易配错 |
| **不适用简单场景** | 🟢 较轻 | 对简单事实查询，GraphRag 与 naive RAG 差异不大 |

### 3.3 version history 体现的演进方向

从 `.semversioner/` 目录中的版本记录（v0.1.0 → v3.1.0，共 46 个版本），关键里程碑：

| 版本 | 日期 | 关键变化 |
|------|------|---------|
| v0.1.0 | - | 初始开源 |
| v0.4.0 | 2024-11 | 增量索引 + DRIFT 搜索 |
| v1.0.0 | - | 首个稳定版本 |
| v2.0.0 | - | 大重构，抽象存储层 |
| v2.3.0 | - | 增量索引增强 |
| v2.4.0 | - | embedding 调优 |
| v2.5.0 | - | 速度优化 |
| v2.6.0 | - | data model 简化 |
| v2.7.0 | - | CosmosDB 支持 |
| v3.0.0 | 2026-01 | 主架构重构，包拆分（graphrag_storage 等独立包） |
| v3.1.0 | 2026-05 | 当前最新版 |

---

## 4. ⚔️ 竞品对比

### 4.1 核心竞品矩阵

| 维度 | **Microsoft GraphRAG** | **LightRAG** | **Nano-GraphRAG** | **Naive RAG (LlamaIndex)** | **Dify** |
|------|----------------------|-------------|-------------------|---------------------------|---------|
| Stars | 33K ⭐ | 20K+ ⭐ | ~2K ⭐ | 40K+ ⭐ | 70K+ ⭐ |
| 核心定位 | 企业级图 RAG 平台 | 轻量级图 RAG | 极简 GraphRAG 复现 | 通用 RAG 框架 | 低代码 AI 应用 |
| 索引成本 | 高（LLM 抽取+社区报告） | 低（增量图更新） | 中 | 低（纯向量） | 低 |
| 全局推理 | ✅ 最强（层次社区 + Map-Reduce） | ✅ 社区级 | ✅ 简化版 | ❌ 无 | ❌ 无 |
| 局部推理 | ✅ | ✅ | ✅ | ✅ | ✅ |
| DRIFT 搜索 | ✅ v0.4+ | ❌ | ❌ | ❌ | ❌ |
| 增量索引 | ✅ | ✅ | ❌ | ✅ | ✅ |
| 配置复杂度 | 🔴 很高 | 🟢 低 | 🟢 低 | 🟡 中 | 🟢 很低 |
| 多模型支持 | ✅（任务级隔离） | ✅ | ✅ | ✅ | ✅ |
| 微软生态集成 | ✅ Azure/Cosmos | ❌ | ❌ | ❌ | ❌ |
| 学习曲线 | 陡峭 | 平缓 | 平缓 | 适中 | 平缓 |

### 4.2 选择建议

| 场景 | 推荐方案 | 理由 |
|------|---------|------|
| 企业级文档理解（复杂推理+全局摘要） | **GraphRAG** | 层次社区+Map-Reduce 无替代 |
| 中小团队快速构建 QA 系统 | **LightRAG** | 成本低、效果好、部署简单 |
| 研究 GraphRAG 原理 | **Nano-GraphRAG** | 代码极简，适合学习 |
| 通用问答+工作流编排 | **Dify** | 低代码、生态丰富 |
| 需要微软 Azure 深度集成 | **GraphRAG** | 原生支持 Cosmos/LanceDB |

---

## 5. 🎯 核心研判

### 5.1 优势（Moats）

1. **社区层次结构是核心护城河**：Leiden 算法 + 社区报告生成的链式处理是同类项目中做得最深的，LightRAG 等竞品在此维度上尚无法匹敌
2. **微软背书 + 持续迭代**：从 v0.1.0 到 v3.1.0 的 46 个版本证明了微软的长期投入，不是「发论文就跑路」项目
3. **架构可扩展性**：v3.0 的包拆分（`graphrag_storage`、`graphrag_cache`、`graphrag_llm`、`graphrag_chunking` 等独立包）为插件化生态奠定了基础
4. **DRIFT 搜索是黑马**：动态社区选择是 GraphRAG 独有的能力，在复杂多跳推理场景有独特优势

### 5.2 风险

1. **成本问题是最大的采用障碍**：即使有 LazyGraphRAG 改进，完整索引的 token 消耗仍然惊人
2. **生态威胁**：LightRAG 等轻量方案在开源社区增长迅猛，如果 GraphRAG 不在成本优化上取得突破，可能被「农村包围城市」
3. **配置复杂度过高**：20+ 嵌套配置项让新手望而却步，和 Dify 这类低代码方案形成鲜明对比
4. **本地模型兼容性**：社区反馈 Ollama 等本地模型跑 GraphRAG 问题较多，限制了个人开发者使用

### 5.3 适用场景

| 最适合 | 不太适合 |
|--------|---------|
| 企业级知识库（跨文档全局摘要） | 简单 FAQ 问答 |
| 研究/情报分析（需要发现隐含关联） | 实时对话（延迟高） |
| 合规/审计场景（需要可解释的推理链路） | 移动/边缘端部署 |
| 微软 Azure 技术栈用户 | 个人/小团队成本敏感场景 |

### 5.4 趋势判断

GraphRAG 从 2024 年开源到现在，走过了从「论文概念验证」到「企业级产品」的演进。v3.0 的包拆分 + 增量索引 + DRIFT 搜索的组合，标志着微软正将其定位为**企业级知识图谱 RAG 平台**而非简单工具。

未来值得关注的方向：
- **LazyGraphRAG**（成本优化 1000 倍）的正式集成
- **对中文和大语言模型的深度优化**
- **与 Azure AI Studio 的深度整合**
- **开源社区对 LightRAG 方案的选择性压力**

---

## 6. 📁 文件速查

| 文件路径 | 核心功能 | 设计模式 |
|---------|---------|---------|
| `__main__.py` | CLI 入口 | Typer App |
| `cli/main.py` | CLI 命令路由 | Click/Typer |
| `config/models/graph_rag_config.py` | 全局配置模型 | Pydantic 深度嵌套 |
| `index/workflows/factory.py` | 流水线工厂 | **注册表+策略模式** |
| `index/run/run_pipeline.py` | 流水线执行器 | Async 流式 |
| `index/workflows/extract_graph.py` | 图抽取工作流 | 两阶段 LLM（抽取+总结） |
| `graphs/hierarchical_leiden.py` | 社区检测 | Leiden 算法 |
| `query/structured_search/local_search/search.py` | 局部搜索 | 单轮上下文注入 |
| `query/structured_search/global_search/search.py` | 全局搜索 | **Map-Reduce** |
| `query/structured_search/drift_search/search.py` | DRIFT 搜索 | 动态社区选择 |
| `query/context_builder/builders.py` | 上下文构建器 | Builder 模式 |
| `prompts/` | 所有 LLM 提示词 | 模板模式 |
| `data_model/` | 数据模型定义 | Dataclass + Pandas |
| `index/update/incremental_index.py` | 增量索引 | 时间戳分区+合并 |

---

> **本报告核心发现：**
> 1. GraphRAG 的 Map-Reduce 全局搜索和层次化社区报告生成是**目前开源社区独一无二**的组合能力
> 2. v3.0 架构重构（包拆分）是项目从「实验」走向「平台」的关键转折
> 3. 成本问题仍然是最大敌人，LazyGraphRAG 的正式集成可能是下一个里程碑
> 4. 对于需要「全局洞察」而非「局部检索」的场景，GraphRAG 目前无真正竞品
