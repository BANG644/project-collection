# 🔬 vitali87/code-graph-rag - 全方位深度调研

> 调研时间：2026-08-10 | Stars：⭐ 2,875 | 语言：Python | 协议：MIT | 默认分支：main（版本 v0.0.582）

## 📌 一句话定位
code-graph-rag 是一个**把多语言 monorepo 解析成统一知识图谱、再用自然语言查询/编辑代码**的 RAG 系统：Tree-sitter 抽结构 → Memgraph 存图 → LLM 把人话翻成 Cypher 并驱动 AST 级代码修改。CLI 叫 `cgr`，同时可作为 MCP server 接 Claude Code / Claude Desktop。

## ⭐ 项目亮点
- **统一图 Schema 跨语言**：Python/TS/JS/Rust/Go/Java/C/C++/C#/PHP/Lua/Dart 等 12+ 语言塞进**同一套语言无关图谱**，混合语言 monorepo 不用为每个语言单独建索引。
- **可插拔 ast-grep 语言层**：新增一门语言（如 Ruby）只需一个 YAML pattern 文件，就能 emit `Module/Function/Class` 节点 + import 边，**不必手写解析器**——扩展成本极低。
- **数据流污点边（FLOWS_TO）**：在 C#/Java/C/Go 上跟踪值流过赋值、调用、I/O sink，是普通"调用图"之上额外的语义边，对安全/影响分析有用。
- **不只是查，还能改**：AST 级"外科手术式"补丁 + diff 预览，把"让 AI 改代码"收敛成结构化编辑而非全文重写。

## 🏗️ 项目架构全景

### 目录结构 + 设计哲学
核心库在 `codebase_rag/`（35+ 模块），CLI 在 `cgr/`：

```
codebase_rag/
├── graph_loader.py      # 把解析结果装载进 Memgraph
├── graph_updater.py     # 增量更新图
├── schema_builder.py    # 统一图 Schema 定义
├── cypher_queries.py    # 预置 Cypher 模板
├── language_spec.py     # 每语言 Tree-sitter 配置
├── parser_loader.py     # ast-grep 可插拔语言层加载
├── embedder.py / vector_store.py  # 语义向量召回（Qdrant）
├── unixcoder.py         # 嵌入模型（UnixCoder）
├── flow_verdict.py      # FLOWS_TO 污点判定
├── dead_code.py         # 从入口遍历边找死代码
├── ast_cache.py / parser_fingerprint.py  # 解析缓存与指纹
├── cli.py / main.py     # 交互式 CLI
```

设计哲学是**"图谱为结构真相源 + 向量为模糊召回"双轨**：精确的结构问题（谁调用 X、Y 的路由是什么）走 Cypher 图遍历；不知道符号名的模糊问题走向量语义。二者互补。

### 技术栈 & 依赖图谱
- 解析：Tree-sitter（treesitter-full）+ ast-grep（结构搜索替换）；
- 图存储：**Memgraph**（需 Docker）；向量：**Qdrant**（需 Docker）；
- LLM 后端：Gemini / OpenAI / Ollama（Ollama 为本地兜底）；
- 框架：pydantic-ai、mcp、loguru；Python ≥ 3.12。

### 核心配置一览
`pyproject.toml` 声明 `cgr` 命令；`cgr` 经 PyPI 安装需 Docker（Memgraph+Qdrant）、cmake、ripgrep；`.env.example` 配 LLM key；语言支持矩阵见 `language_spec.py` + `parser_loader.py`。

## 💡 应用场景与启发（重点章节）

### 典型使用场景
- **新人 onboarding**：对着陌生 monorepo 用中文问"X 函数在哪、被谁调用、属于哪个模块"，直接拿到结构答案而非 grep 全文。
- **跨语言影响分析**：改一个共享库，沿 import/call 边看影响范围，跨 Python↔TS 边界也行。
- **AI 辅助重构**：AST 级补丁 + diff 预览，按你自己的编码规范优化代码。

### 可借鉴的解决方案模式
- **"ast-grep YAML 即语言插件"**：用声明式 pattern 文件新增语言支持，比"每语言写解析器"省一个数量级——任何"多格式解析"系统（日志、配置、AST）都可借鉴。
- **"图 + 向量双轨召回"**：把"精确结构"与"模糊语义"分开存储与查询，是 RAG 代码检索的成熟范式（CodeGraph 也走这条路，但用 SQLite 替代 Docker）。

### 同类需求的可参考思路
如果环境**不允许 Docker / 要纯本地零依赖**，code-graph-rag 的 Memgraph+Qdrant 组合反而是负担——此时应参考 CodeGraph（本地 SQLite、无 API key）。code-graph-rag 更适合"已有 Docker 基建、要最强图表达力"的团队。

## 🧠 核心源码解读（克制代码量）

### 入口与主流程（codebase_rag/main.py + cli.py）
两阶段流水线：① 多语言解析器读仓库，把函数/类/方法/模块及其关系摄入 Memgraph（`graph_loader` + `schema_builder`）；② RAG 系统把自然语言翻成 Cypher，检索代码并驱动编辑。

```text
Source Code → Tree-sitter Parser → AST Analysis → Memgraph Graph
User Query → LLM(Cypher Gen)    → Cypher Query → Graph Results → Response
```

### 关键模块：可插拔语言层（parser_loader.py + language_spec.py）
Ruby 支持就是典型案例——新增语言只写一个 YAML pattern 文件，emit `Module/Function/Class` 节点 + import 边，无需手写 parser。这是"配置即解析器"的极致。

### 关键模块：数据流边（flow_verdict.py）
`FLOWS_TO` 污点边跟踪值在赋值/调用/I-O sink 间的流动，覆盖 C#/Java/C/Go，让"改 X 会影响哪些数据路径"可查询——比纯调用图多一层语义。

### 隐藏功能 & 未文档化特性
- `dead_code.py` 从入口点遍历 call/reference 边自动找死代码；
- `graph_audit.py` / `graph_updater.py` 支持图审计与增量更新（非全量重建）；
- 既可作为 CLI 也可作为 MCP server（`mcp>=1.28.1`），直接进 Claude Code 工具链。

## 📐 架构决策与设计哲学
- **选 Memgraph 而非 Neo4j/SQLite**：图原生、Cypher 标准、性能好，但代价是必须 Docker——这是"表达力优先于部署简单"的取舍。
- **选 LLM 生成 Cypher 而非固定模板全覆盖**：灵活但依赖模型质量，且需 API key（Ollama 兜底缓解离线焦虑）。
- **版本号已到 v0.0.582**：高频迭代（几乎每日发布），但 0.0.x 仍暗示 API 不稳定、无向后兼容承诺。

## 🌐 全网口碑画像

### 好评共识
- MCP 市场与 mdskills.ai 评价其"多语言统一图 Schema + AST 级编辑"组合在 monorepo 导航上体验好；
- dev.co 评估"Maintenance: Active、License clarity: Clear"，认为中等置信度值得采用；
- 社区欣赏"图 + 向量"双轨与可插拔语言层的低扩展成本。

### 差评共识 & 踩坑高发区
- **Docker 依赖是部署门槛**：Memgraph + Qdrant + cmake + ripgrep 一堆前置，轻量环境劝退（dev.co 明确列为 Implementation consideration）；
- **大 monorepo 性能未文档**：>100k 文件的索引速度与表现未知；
- **0.0.x 稳定性无保证**：频繁更新但无 SLA、无向后兼容承诺；
- **非离线友好**：主用 Gemini/OpenAI，纯 air-gapped 环境需显式配 Ollama。

### 争议焦点
主要在"要不要 Docker"——这正是它与 CodeGraph（纯本地 SQLite）的分野。社区没有强烈反对，更多是"按需选型"。

### 维护者响应风格
仓库 CI 极全（claude-code-review / osv-scanner / scorecard / sonarcloud / codecov 全开），作者维护积极，安全与质量门禁到位。

## ⚔️ 竞品对比

| 维度 | code-graph-rag | Graphify-Labs/graphify | code-review-graph | codebase-memory-mcp | CodeGraph(colbymchenry) |
|------|----------------|------------------------|-------------------|---------------------|------------------------|
| 存储 | Memgraph(Docker) | 图+LLM提取 | SQLite | SQLite+LSP | 本地 SQLite |
| 多语言 | 12+ 统一Schema | 是 | Tree-sitter | Hybrid LSP | Tree-sitter |
| 部署复杂度 | 高(Docker) | 中 | 低 | 低 | **极低(无Docker)** |
| 能编辑代码 | AST补丁+diff | 浏览为主 | 审查为主 | 记忆为主 | 检索为主 |
| 离线/本地 | Ollama兜底 | 部分 | 是 | 是 | **完全本地** |
| 定位 | 查询+编辑RAG | 知识图谱浏览 | PR审查/风险 | 代码图后端 | 预索引符号图 |

**选择建议**：已有 Docker、要最强图表达力+AST 编辑 → code-graph-rag；要零依赖纯本地符号图 → CodeGraph；只要代码审查影响分析 → code-review-graph；本库已收录 Graphify/code-review-graph/codebase-memory-mcp，三者定位互补。

## 🎯 核心研判

### 项目优势（不可替代的价值点）
- 统一跨语言图 Schema + 可插拔语言层，monorepo 导航体验领先；
- "图+向量+AST编辑"三位一体，不止检索还能改。

### 项目风险（潜在隐患和局限性）
- Docker 强依赖抬高部署门槛，对轻量/离线场景不友好；
- 0.0.x 无稳定 API 承诺，生产集成需谨慎；
- 大仓库性能未验证，星标尚低（2.9k）生态未成网络效应。

### 适用场景 & 不适用场景
- ✅ 已有 Docker 基建、多语言 monorepo、要 AI 辅助理解与重构的团队；
- ❌ 纯离线/air-gapped、无 Docker、要生产级 SLA 的场景。

### 趋势判断
**早期上升期**。方向（代码图 RAG）正热，竞品 CodeGraph 7 天冲 31k 说明赛道需求真实；code-graph-rag 靠"表达力 + 可编辑"差异化，但需解决部署与稳定性才能吃到红利。

## 📂 关键文件路径速查
- 图装载/更新：`codebase_rag/graph_loader.py`、`graph_updater.py`
- 图 Schema/Cypher：`codebase_rag/schema_builder.py`、`cypher_queries.py`
- 语言层：`codebase_rag/language_spec.py`、`parser_loader.py`
- 语义召回：`codebase_rag/embedder.py`、`vector_store.py`、`unixcoder.py`
- 数据流/死代码：`codebase_rag/flow_verdict.py`、`dead_code.py`
- CLI/MCP：`codebase_rag/cli.py`、`main.py`（CLI 入口 `cgr/`）
- 发布：https://github.com/vitali87/code-graph-rag ｜ PyPI：`code-graph-rag`
