# NVIDIA/auto-ontology 深度调研

> 调研日期：2026-11-05 ｜ 定位：给 agent 用的企业数据「语义上下文层」，把不可靠的 Text-to-SQL 变成可验证的认证查询
> 仓库：https://github.com/NVIDIA/auto-ontology ｜ Stars：≈4.5k（2026-11-04，仍在快速上涨，HN 当日登榜）｜ 语言：Python ｜ 许可：Apache-2.0
> 关键词：semantic-layer / text-to-sql / mcp / agentic-analytics / rag / enterprise-data / nvidia-nim

## 一、项目定位（一句话）

auto-ontology 是 NVIDIA 开源的**「语义上下文层」**：它不从零训练模型，而是把你数据仓库的元数据**编译成一份 ontology（业务术语→字段、已审核的 SQL 度量、表间关系）**，再通过一个**只读 MCP Server（9 个工具）+ CLI + REST API** 把这份「带含义的地图」交给任意 agent harness——目标是解决 agentic analytics 最大的痛点：**「算得快但算错了」比算得慢更糟**。

## 二、项目亮点（差异化，开篇先看）

1. **把「可靠性」当成一等公民**：它不承诺「自动写 SQL」，而是承诺「在查询前先回答——数据在哪、它什么意思、该不该用、怎么用、从哪来」。README 原话：「a revenue figure delivered faster is worth nothing if it's wrong」。
2. **「schema 塞进上下文窗口」的反模式替代**：传统做法把整库 schema 塞给模型，token 随表/列线性膨胀、join 和度量靠模型临场发挥、答非所问还答得理直气壮；auto-ontology 只下发「问题真正触及的术语与表」，并预解析关系与已审核 SQL。
3. **MCP 只读、写走治理面**：MCP 故意只暴露 9 个只读工具（没有「浏览原始 schema」的工具），强制 agent 经由语义层取数；写操作（编辑/认证/发布）必须走 Next.js `/api/...` 治理面，权限、血缘、provenance 可控。
4. **与既有语义层共存而非取代**：它**读取并调和**你已有的 dbt semantic layer / Databricks metric view / 现有 ontology，定位是「complement」，不是把 Palantir、Snowflake Horizon、Databricks Genie 掀翻。
5. **自带确定性评测 harness**：`auto-ontology-eval` 用控制组（纯 schema）vs 实验组（ontology-grounded agent）双臂对照，靠**执行结果匹配**打分（无 LLM judge），数据集含 BIRD Dev、Mini-Dev、FDABench-Lite、BEAVER。

## 三、核心架构（克制呈现）

四件套服务 + 单一存储，是它最干净的设计决策：

| 组件 | 技术 | 端口 | 职责 |
|------|------|------|------|
| Frontend | Next.js 16 / React 19 / TS / Tailwind 4 / Better Auth / Prisma | 3000 | Web UI、SSO 登录、API 网关 |
| Backend | FastAPI（Python 3.12+）/ LangChain | 3001 | chat、NL-to-SQL、catalog、datasource API |
| Ingestion worker | FastAPI | 3002 | 摄入表数据、写 embedding |
| 存储 | Postgres + pgvector | 5432 | catalog / ontology / 向量，**三者在同一个库** |

**关键决策：语义目录就住在「它所描述的 catalog 旁边的 Postgres 里」**——不引入独立的图数据库（Neo4j 等）。向量、术语、元数据共享一个 store，部署面只有一套 Postgres。可选 HashiCorp Vault 存连接凭证。

支撑这一层的代码在 `auto_ontology/` 下分域组织：`catalog/`（元数据抽取 `extract.py`、SQL 解析 `sql_parse.py`、`normalize.py`、`write.py`、`parsers/`、`store/`）、`semantic/`（**编译器** `compile.py`、`term_extractor.py` 术语抽取、`semantic_fk.py` / `fk_suggester.py` 外键推断、`sql_attribute_suggester.py` 度量建议、`deterministic.py` 确定性查询生成、`prompts/`、`embed.py`）、`retrieval/text_to_sql/`（问答 agent）、`server/`（含 `semantic_compilation/`、`pql_analyses/`、`datasources/`、`ingestion/`、`rules/`）、`pii_detection/`（PII 处理）、`vdb/`（向量）、`connectors/`（Databricks/Postgres/Snowflake/DuckDB）。

## 四、应用场景与启发

- **企业 agentic BI 的「防错底座」**：任何让 LLM 直接对数据仓库发 SQL 的 agent（ChatBI、NL-to-SQL 助手）都该在前面垫一层「已认证定义」，避免「活跃用户」三个口径算出三个数。
- **可借鉴的模式**：① **「上下文层而非上下文窗口」**——把数据含义固化成可查询的 ontology，按需下发，而不是一次性塞 prompt；② **只读取数 + 治理写回**的职责切分（MCP 只读、API 写），天然支持权限与审计；③ **单一 Postgres 承载 catalog+向量+元数据**，用 pgvector 省掉一套独立向量库运维。
- **给同类需求的思路**：如果你要做内部知识库/指标平台的「AI 取数」能力，与其训练专用模型，不如先把「业务术语 ↔ 物理字段 ↔ 已审核 SQL」这张映射做扎实，再让 agent 走这张地图。

## 五、源码深度解读

**1) 语义编译器——`auto_ontology/semantic/compile.py` + `term_extractor.py`**
`term_extractor` 用 LLM 从 schema/文档/指标目录中**归纳**出候选实体、关系、度量定义（这一步是**概率性**的，不是推导）；`compile.py` 把它们编译成可供 agent 查询的语义层。注意：输出被官方定位为「starter ontology」，仍需业务专家在 UI 里测试、精炼、认证。

**2) 外键/关系推断——`semantic/semantic_fk.py` + `fk_suggester.py`**
自动建议表间 join 路径并写入 ontology（alembic 迁移里有 `add_semantic_fk_join_path_default`），让 agent 不必每次临场猜 join——这是相对「纯 schema prompt」最实在的收益之一。

**3) 确定性查询生成——`semantic/deterministic.py` + `retrieval/text_to_sql/`**
问答 agent 通过 MCP 的 `ask_question` 取数，返回**答案 / SQL / 原始行**三个分离字段（行数上限 100），并在回答时附上 SQL 与 agent 的推理步骤；`Validate` 阶段在查询前先做「可答性检查」，答不了就显式要求澄清，而不是瞎答。

> ⚠️ 说明：以上为基于 `AGENTS.md`、README 与目录结构的模块职责梳理；具体实现细节以仓库源码为准（本报告未逐行贴代码，避免臆造）。

## 六、社区口碑（全网口碑）

- **强正面、集中爆发**：2026-11-03 早晨登上 Hacker News（当时约 1,100 stars），ExplainX、MarkTechPost、DigestAI 等同步发文，普遍认可其「把可靠性放在速度前面」的定位，以及 MCP-ready、可接任意 OpenAI 兼容端点的工程完成度。
- **关键批评（最值得看）**：BestHub 的拆解《Generates Catalogs, Not Ontologies》指出——它**没有 RDF/OWL 推理机、没有 SWRL 规则、没有前向/后向链**；所谓「reasoning」只是配置里的 `REASONING_MODEL` 环境变量（指向 chat/NL-to-SQL 模型），**不是逻辑引擎**。即：它是「用 LLM 从 schema 归纳语义」的**概率性**系统，同一 schema 两次运行可能产出不同实体划分；而真正的 ontology 平台应能从公理**确定性推导**新事实。结论：它是「认证指标共享」的好加速器，但不是能做自动推理的完整 ontology 平台。
- **证据短板（多方共识）**：NVIDIA 自报「ontology 创建时间降 90%」，但**至今未公开任何 Text-to-SQL 准确率分数**；eval 仓库只发 harness 不发结果，且双侧臂都走 NVIDIA 网关上的 Claude，外加只给实验组喂 few-shot/value anchors——**要信它，得自己跑 benchmark**。
- **治理信号**：项目目前**不接受外部贡献（outside contributions not accepted at this time）**，对想参与或 fork 后改动的团队是个门槛。

## 七、竞品对比

| 维度 | auto-ontology | dbt Semantic Layer | Databricks Genie / Unity Catalog | Palantir Ontology | 纯 NL-to-SQL agent |
|------|--------------|-------------------|--------------------------------|-------------------|--------------------|
| 核心定位 | agent 的语义上下文层（开源、可嵌入） | 指标定义即代码 | 数据仓库原生 BI/治理 | 企业级本体+推理 | 直接生成 SQL |
| 推理能力 | 无（概率性归纳） | 无 | 无 | 有（确定性推导） | 无 |
| 与现有栈关系 | 读取并调和既有语义层 | 定义语义层本身 | 数据平台内置 | 平台内置 | 独立 |
| 开放程度 | Apache-2.0（暂不接受外部 PR） | 部分开源 | 闭源/商业 | 闭源 | 多为开源 |
| 取数接口 | MCP（只读）+ API（写） | SQL/dbt | UI/API | API | prompt |

选型：已有 dbt/Databricks 语义层的团队，把它当「agent 取数前面的认证网关」最顺；追求确定性推导与跨系统自动推理的企业，应看 Palantir 或自建规则引擎。

## 八、核心研判

- **价值判断**：把「数据含义」从 prompt 里抽出来做成可查询、可认证、可治理的层，方向正确，且工程完成度高（四服务+单 Postgres+pgvector、MCP 只读治理写回）。对任何要做 ChatBI/agentic analytics 的团队都有借鉴价值。
- **风险点**：① 概率性归纳≠确定性推理，金融/政务等「同问必同答、可审计」场景天然不满足；② 零公开准确率、eval 设计有偏，宣传可信度需自测；③ 暂不接受外部 PR，社区共建与定制化受限；④ 默认依赖 NVIDIA NIM（需 `nvapi-` key），虽可换端点但有心智与供应商绑定。
- **适用 / 不适用**：✅ 企业内「让 agent 安全地基于认证指标取数」；❌ 需要自动逻辑推导、强合规可审计、或完全离线无 NVIDIA key 的场景。
- **趋势判断**：上升期（HN 当日登榜、NVIDIA 官方背书、技能已同步进 `nvidia/skills` 生态）。但能否从「加速器」成长为「平台」，取决于它是否补上确定性推理与公开基准。

## 九、关键文件路径速查

- `auto_ontology/semantic/compile.py` — 语义层编译器（元数据→ontology）
- `auto_ontology/semantic/term_extractor.py` — LLM 归纳实体/关系/度量
- `auto_ontology/semantic/semantic_fk.py` / `fk_suggester.py` — 外键/关系推断
- `auto_ontology/semantic/deterministic.py` — 确定性查询生成
- `auto_ontology/catalog/sql_parse.py` / `extract.py` / `write.py` — 元数据抽取与 SQL 解析
- `auto_ontology/retrieval/text_to_sql/` — 问答 agent（背后即 README 提到的 Chat agent）
- `auto_ontology/server/semantic_compilation/` / `pql_analyses/` / `rules/` — 编译与查询执行面
- `auto_ontology/pii_detection/` — PII 处理
- `mcp/auto_ontology_mcp/tools.py` — 9 个只读 MCP 工具的握手清单（read-only by design）
- `AGENTS.md` / `CLAUDE.md` / `DEPLOYMENT.md` — 接入/治理/部署规约；`skills/nvidia-ontology-{setup,management,query}/` 为 agent 技能包
