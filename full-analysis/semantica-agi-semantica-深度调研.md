# 🔍 深度调研报告：semantica-agi/semantica

> **Stars**: 2,266 ⭐ | **Forks**: 299 | **语言**: Python | **License**: MIT | **创建**: 2025-06-25 | **默认分支**: main
> **定位**：Graph-Native 基础设施，为 AI Agent 提供「可解释、可追溯、可审计」的上下文与问责层（开源版 Palantir for AI Agents）
> **调研日期**：2026-08-08（GitHub Trending）

## 一、项目亮点（差异化）

- **「AI 问责层」而非「质量层」**：它补的是 accountability，不是 answer quality——解决「AI 为什么这么决策、用了哪些事实、推理路径是什么、能否审计」。
- **确定性推理，无需 LLM**：前向链、Rete 网络、Datalog、SPARQL 全部可解释；图构建 / 推理 / 溯源都不依赖 LLM，避免黑箱。
- **W3C PROV-O 全量溯源**：每个事实带 provenance，审计轨迹可导出 JSON / CSV / RDF；双时态图（BiTemporalFact）支持时间点快照。
- **多图存储可插拔（Polyglot）**：RDF（Oxigraph / Blazegraph / Jena / RDF4J via SPARQL）+ 标记属性图（Neo4j / FalkorDB / Apache AGE / Neptune via Cypher）+ 向量库，换存储不碰业务代码。
- **企业数仓原生 connector**：Databricks（Unity Catalog + Delta Lake）、Snowflake 直连，lakehouse 里的表直接变带溯源的图节点，不必先导出到第三方 SaaS。

## 二、项目全景

Semantica 自述「The Open Source Palantir for AI Agents」——坐在你的 LLM、向量库、Agent 框架**之下**，作为确定性基础设施层。核心理念：多数 Agent 存的是 embedding 不是 meaning，上下文无法解释、决策无法审计；在信贷等受监管场景，这缺口是合规暴露而非不便。

面向人群：AI/ML 平台团队、Databricks/Snowflake 数据平台团队、合规/风险/审计团队、受监管企业（金融/医疗/法律/政府/国防）、平台/基础设施工程师、数据与知识工程师。

工程成熟度：PyPI **0.6.0，Development Status 5 - Production/Stable**；**2,170 commits、21 contributors**；提供 REST API（100+ 端点）、MCP server（10+ 工具）、CLI（50+ 命令）、Knowledge Explorer 可视化工作台；原生 Agno 支持 + 多编辑器插件。

## 三、核心架构

完整数据流水线（`ARCHITECTURE.md` 的 mermaid 全景）：

```
Sources → Ingest → Parse → Normalize → Split
        → Extract(NER/Relation/Event/Triplet/Coref)
        → Conflict Detection → Deduplication
        → KG Construction(BiTemporalFact, TemporalGraphQuery)
        → [Ontology | Reasoning | Provenance | Context&Decisions]
        → [Vector Store | Graph Store]
        → [Export | Visualize | Services(REST/MCP/CLI/Explorer)]
```

Python 模块划分（`semantica.*`）：
- `ingest`（FileIngestor / WebIngestor / DBIngestor / ParquetIngestor / SnowflakeIngestor / StreamIngestor / RepoIngestor / EmailIngestor / MCPIngestor）
- `parse` / `normalize`（Text/Entity/Date/Number Normalizer）/ `split`（entity/relation/graph/ontology/hierarchical aware）
- `semantic_extract`（NamedEntityRecognizer / RelationExtractor / EventDetector / TripletExtractor / CoreferenceResolver）
- `conflicts`（ConflictDetector / Resolver / SourceTracker）
- `deduplication`（DuplicateDetector / EntityMerger）
- `kg`（GraphBuilder / EntityResolver / BiTemporalFact / TemporalGraphQuery）
- `ontology`（OntologyGenerator / Validator；OWL / SHACL / SKOS）
- `reasoning`（ReteEngine / DatalogReasoner / SPARQLReasoner / ExplanationGenerator）
- `provenance`（ProvenanceManager；W3C PROV-O）
- `context`（ContextGraph / AgentContext / DecisionRecorder / CausalChainAnalyzer / PolicyEngine）
- `vector_store`（FAISS / Qdrant / Weaviate / Milvus / Pinecone / PgVector；Hybrid + RRF）
- `graph_store`（Neo4j / FalkorDB / Apache AGE / Neptune）
- `export`（RDF Turtle / JSON-LD / N-Triples / OWL / SHACL / Parquet / Cypher / ArangoDB AQL / GraphML / CSV / HTML）
- `visualization`（KG / Ontology / Embedding / Temporal Visualizer）

决策智能生命周期：`record_decision()` → `add_causal_relationship()` → `find_similar_decisions()` / `trace_decision_chain()` / `analyze_decision_impact()` → Govern。

## 四、应用场景与启发

- **受监管决策的「为什么」**：信贷审批 Agent 的决定数月后要经得起监管追问——Semantica 把每次决策存为可查询、可溯源的一等对象。
- **lakehouse 直接变知识图谱**：Databricks/Snowflake 里现成的表，不必导出到第三方 SaaS 就能成带血缘的图节点。
- **多 Agent 共享智能层**：多个 Agent 需要共享知识/决策时，Semantica 的「单一共享智能层」是关键差异（vs Mem0/Zep 的单 Agent 私有记忆）。
- **给同类需求的解法**：做 Agent 可审计/可解释，优先组合「图构建 + 确定性推理 + PROV-O 溯源 + 实体消歧」，而不是堆向量检索。
- **架构借鉴**：把 reasoning / KG / provenance 做成**确定性、可换存储**的层，坐在现有 LLM 栈之下做补充而非替换——零厂商锁定。

## 五、源码深度解读

### 1. 决策即一等对象（`semantica/context`）

```python
from semantica.context import ContextGraph
graph = ContextGraph(advanced_analytics=True)
decision_id = graph.record_decision(
    category="vendor_selection",
    scenario="Choose cloud provider for HIPAA workload",
    reasoning="AWS offers BAA, mature HIPAA tooling, existing expertise",
    outcome="selected_aws", confidence=0.93,
)
```

每个 Agent 决策成为可查询、可审计的知识节点；`add_causal_relationship()` 串联触发/启用/导致/先于关系，`trace_decision_chain()` 取完整因果祖先——这是「问责层」的 API 内核。

### 2. 确定性推理引擎（`semantica/reasoning`）

`ReteEngine` / `DatalogReasoner` / `SPARQLReasoner` / `ExplanationGenerator` 提供前向链、Rete 网络、Datalog、SPARQL，**完全可解释路径，且无需 LLM**。这与「图构建/推理/溯源都是确定性」的设计原则一致——把不确定性留给上层 LLM，把问责留给下层确定性栈。

### 3. 双时态事实与冲突检测（`semantica/kg` + `semantica/conflicts`）

`BiTemporalFact` + `TemporalGraphQuery` 支持时间点图快照（time travel）；`ConflictDetector` / `ConflictResolver` / `SourceTracker` 在事实冲突时**标记而非静默覆盖**，配合 `deduplication` 的 `EntityMerger` 在噪声成灾前合并重复——这是「存 meaning 不存 embedding」的工程落点。

## 六、社区口碑

- **定位清晰、口碑分化**：x-cmd 等评测点明——「想用 Semantica 提升 Agent 答案质量的人方向错了，它补的是 accountability 不是 quality」；与 Neo4j/FalkorDB（只存+图算法，需自建 PROV-O/SHACL）相比，Semantica 把问责层内置。
- **发布节奏快**：PyPI 0.1.x（2025 Q4）→ 0.5.x（2026 Q2，SHACL 策略引擎、BiTemporalFact、实体消歧、MCP server 12 工具、Agno 集成、8 编辑器插件）→ 0.6.0 Production/Stable；v0.5.1 加 Apache Arrow/Feather  ingestion、一键部署（Docker/Railway/Render/Fly/GCP/Azure/K8s/Helm）、Neo4j bulk CSV、修 6 CVE。
- **社区规模**：2,170 commits、21 contributors、~1,200+ stars（早期帖）→ 2,266 stars；Discord / X / YouTube 演示齐备。
- **专业质疑**：LinkedIn 上图领域专家指其「reasoning」更接近信息链接（抽取+实体解析+图遍历）而非基于显式公理的逻辑推断；自动诱导的 OWL ontology 非策展领域治理本体；建议用于语料探索 / 概念发现 / KG 引导 / RAG，而非严格合规或专家系统。

## 七、竞品对比

| 维度 | Semantica | Mem0 / Zep | Neo4j / FalkorDB | Apache Jena / RDFLib |
|---|---|---|---|---|
| 定位 | Agent 问责层 | 单 Agent 私有记忆 | 存储+图算法 | W3C 标准工具 |
| 溯源 | W3C PROV-O 内置 | ❌ | 需自建 | 需自建 |
| 推理 | Rete/Datalog/SPARQL | ❌ | ❌ | 面向本体工程师 |
| 多 Agent 共享 | ✅ 单一共享智能层 | ❌ 私有 | 存储层 | 存储层 |
| 决策生命周期 | ✅ 内置 | ❌ | ❌ | ❌ |
| 高 Level API | record_decision() | memory API | Cypher | SPARQL |

### 核心研判

- **优势**：罕见地专攻「AI 合规 + 可解释性」，确定性推理 + PROV-O 溯源 + 双时态 + 实体消歧 + 决策生命周期全内置；多图存储可插拔、零厂商锁定；企业数仓原生 connector 击中受监管场景痛点。
- **风险**：0.x 阶段变化快，生产需 pin tag；专家质疑其「reasoning」偏信息链接而非逻辑推断、自动诱导本体非策展；在严格合规/专家系统场景说服力有限。
- **趋势**：「Agent 问责层」会从 nice-to-have 变受监管行业的必选项，Semantica 占得开源先机。
- **启发**：做金融/医疗/法律等强审计 Agent，优先评估 Semantica 作确定性问责底座；但别指望它提升答案质量，也别在严格合规场景把它当唯一真相源——配合策展本体使用。

## 八、关键文件速查

- `ARCHITECTURE.md` — 全量数据流水线 + 决策智能生命周期 mermaid 图
- `semantica/` — Python 包根（context / reasoning / provenance / kg / ontology / ingest / …）
- `mcp/` — 10+ 工具的 MCP server
- `plugins/` — 多编辑器插件
- `explorer/` — 交互式 Knowledge Explorer 工作台
- `integrations/` — Agno 等原生集成
- `cookbook/` / `docs/` — 用法食谱与文档
- `pyproject.toml` / `Dockerfile` / `docker-compose.yml` — 打包与部署
