# RAGFlow 深度调研

> 调研日期：2026-08-13 | 星标：87,476（2026-08-12）| 协议：Apache-2.0 | 语言：Go + Python | 出品：InfiniFlow

## 一、项目定位

RAGFlow 是领先的开源 **RAG（检索增强生成）引擎**，融合前沿 RAG 与 Agent 能力，为企业提供"上下文引擎（context engine）"+ 预置 Agent 模板，把复杂数据转化为高保真、生产可用的 AI 系统。它不是简单的"向量检索+LLM"，而是把**文档理解质量**作为一等公民。架构上是 Python 后端 + React 前端 + 自研 `deepdoc` 文档理解库的组合。

## 二、项目亮点（差异化）

1. **深度文档理解（deepdoc）**：从格式复杂的非结构化数据（PDF/扫描件/表格/图片）抽取"高质量"知识——真·"quality in, quality out"。
2. **模板化、可解释的智能分块（chunking）**：多种模板，可视化分块让人可干预，避免黑盒切分。
3. **接地引用（grounded citations）**：可追溯引用降低幻觉，关键参考可视化。
4. **异构数据源兼容**：Word/Slides/Excel/TXT/图片/扫描件/结构化数据/网页。
5. **自动化 Agent 工作流**：可编排的 agentic workflow + MCP + 多通道（飞书/Discord/Telegram/Line）+ Memory。
6. **自研上下文引擎**：可切换 Elasticsearch / Infinity（InfiniFlow 自家向量库）。

## 三、核心架构

- **分层**：前端 `web`（React）→ 后端 API（Python，`ragflow_server.py` / `task_executor.py`）→ 依赖服务（MinIO 对象存储、Elasticsearch/Infinity 全文+向量、Redis、MySQL）。
- **文档理解层 `deepdoc/`**：版面分析 + 表格结构识别 + 文本/OCR 抽取。
- **Agent 层 `agent/`**：基于 DSL 的画布（`canvas.py` 的 `Graph` 类），组件化（Begin/Retrieval/Generate/...），支持 code executor（沙箱，依赖 gVisor）。
- **自研向量库 Infinity**（`infiniflow/infinity`）作为 ES 替代，通过 `docker/service_conf.yaml.template` 的 `DOC_ENGINE` 切换。
- **Agent 沙箱 `agent/sandbox/`**：多 provider（local/e2b/aliyun/ssh/self_managed），带 seccomp 安全边界。

## 四、应用场景与启发

- **场景**：企业知识库、客服问答、文档智能、合规检索。
- **启发 1**：RAG 的质量瓶颈在**文档解析与分块**，而非检索；把解析/分块做成可视、可干预的一等公民，是工程胜负手。
- **启发 2**："上下文引擎"作为 LLM 的**独立价值层**——它不绑定某个应用，可被任意上层消费，这是 InfiniFlow 把 RAGFlow 与 Infinity 拆成两层产品的原因。
- **启发 3**：沙箱化 code executor 让 Agent 能跑真实 Python/Node 代码，是 agentic RAG 从"问答"走向"执行"的关键。

## 五、源码深度解读

### 1. `agent/canvas.py` — Agent 工作流的执行图
`class Graph` 是 Agent 画布的核心数据结构。DSL 用 `components` 字典描述每个节点（`component_name` + `params` + `upstream`/`downstream`），Graph 负责拓扑与执行顺序：

```python
class Graph:
    dsl = {
        "components": {
            "begin":     {"obj": {"component_name": "Begin", "params": {}}, "downstream": ["answer_0"], "upstream": []},
            "retrieval_0": {"obj": {"component_name": "Retrieval", "params": {}}, "downstream": ["generate_0"], "upstream": ["answer_0"]},
            "generate_0": {"obj": {"component_name": "Generate", "params": {}}, "downstream": ["answer_0"], "upstream": ["retrieval_0"]},
        }
    }
```

这印证了 RAGFlow Agent 是**"声明式图 + 组件化执行"**而非硬编码链——每个 `component` 都继承自 `agent/component/base.py` 的 `ComponentBase`，由 `component_class` 注册。

### 2. `deepdoc/` + `rag/`
`deepdoc/` 负责版面/表格/OCR 抽取；`rag/` 负责 chunk、embedding、retrieval、rerank。关键抽象：`rag/prompts/generator.py` 的 `chunks_format`（prompt 拼接）、`common/token_utils.py`（token 计量 sink）。

### 3. `agent/sandbox/`
多 provider 沙箱 + `seccomp-profile-default.json` + `security.py`：把"不可信代码执行"做成**可插拔、带安全边界**的能力，fail-closed 思路（限制系统调用 + 资源限额）。

## 六、社区口碑

- 87k⭐，GitHub Octoverse 常客，Discord 活跃，13 种语言 README，DeepWiki 支持；商业云 cloud.ragflow.io。
- 1,879 open issues（规模大、迭代快，部分为功能请求）。
- 口碑：被公认为 Dify/Verba 之外"**文档理解最强**"的开源 RAG；对企业私有部署友好。部署依赖重（ES/Infinity/MySQL/Redis/MinIO）是被诟病的点。

## 七、竞品对比 + 核心研判

| 维度 | RAGFlow | Dify（已入库） | LangChain/LlamaIndex | GraphRAG（已入库） |
|------|---------|--------------|----------------------|-------------------|
| 定位 | 文档理解+RAG 引擎 | 通用 Agent/工作流平台 | 开发框架/库 | 知识图谱全局摘要 |
| 文档解析 | 自研 deepdoc，强 | 依赖上游 | 依赖上游 | 不强调 |
| 开箱即用 | 高 | 高 | 低（胶水多） | 中 |

- **核心护城河**：`deepdoc` 文档理解 + 模板化可解释分块 + 自研向量库 **Infinity**，三者构成"高质量上下文"闭环。
- **风险**：组件多、依赖重、部署复杂；企业版与开源版边界需注意；与 Dify 常互补（RAGFlow 做知识层、Dify 做编排）。
- **研判**：最适合"重文档、重精度"的知识问答场景；若只需轻量检索，LlamaIndex 更轻。

## 八、关键文件速查

- `agent/canvas.py` — Agent 图执行引擎
- `deepdoc/README.md` — 文档理解说明
- `rag/` — chunk / embedding / retrieval
- `agent/sandbox/` — 代码执行沙箱
- `docker/service_conf.yaml.template` — `DOC_ENGINE` 切换 ES↔Infinity
- `Dockerfile` / `docker/docker-compose.yml` — 部署
