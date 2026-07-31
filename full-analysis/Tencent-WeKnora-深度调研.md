# Tencent/WeKnora 深度调研

> 调研日期：2026-08-01 ｜ Stars：19,206 ｜ 语言：Go ｜ 协议：MIT ｜ 版本：v0.7.1 ｜ 默认分支：main

## 一、项目定位

腾讯开源的「RAG + ReAct Agent + 自动 Wiki」一体化企业级知识框架。它把分散在飞书 / Notion / 语雀 / RSS / 网页 / 本地文件里的文档，经过解析、混合检索、Agent 推理，沉淀成「可查询、可推理、可持续演进」的专属知识资产，并能以对话、IM 机器人、网站嵌入 Widget、REST API、CLI 等多种形式对外服务。微信对话开放平台（chatbot.weixin.qq.com）的底层技术框架即 WeKnora。

## 二、项目亮点

1. **三引擎合一**：RAG 快速问答 + ReAct Agent 自主多步推理 + Wiki 模式（Agent 从原始文档自治生成相互链接的 Markdown 知识库与可视化图谱），单一框架覆盖"查得到 / 想得通 / 写得出来"三层需求。
2. **微信生态原生**：作为微信对话开放平台核心技术，零代码即可把知识库部署到公众号 / 小程序；另含 Chrome 插件、微信小程序、网站嵌入 Widget、ClawHub Skill 四种轻量入口。
3. **混合检索 + 知识图谱**：BM25 稀疏召回 / Dense 稠密召回 / GraphRAG 图谱增强三路融合，多向量库扇出（pgvector HNSW 1024 维、Milvus、Weaviate、Qdrant、Doris、腾讯云 VectorDB 等）。
4. **企业级权限与可观测**：空间 RBAC 四级角色矩阵（Owner/Admin/Contributor/Viewer）+ 资源归属 + 空间审计日志；权限范围 API Key（能力级授权 + 按 KB 限制 + 节流）；Langfuse 全链路追踪 ReAct 循环 / Token / 工具调用；运行时任务队列面板与 Worker 池治理。
5. **全私有化 + 模块化**：Docker / K8s(Helm) 部署，大模型 / 向量库 / 存储后端均可替换；凭据与 MCP 密钥 AES-256-GCM 静态加密、防 SSRF、gRPC TLS。

## 三、核心架构

```
docs/网页/RSS(源) → docreader(解析/VLM/ASR) → Embedding 向量化 → 向量库(pgvector等)
                                                              ↓
                                          检索层(BM25 + Dense + GraphRAG 混合, 多库扇出)
                                                              ↓
                  ┌──────────────── ReAct Agent(internal/agent) ───────────────┐
                  │ think → act(tools/MCP/搜索) → observe → finalize → 循环    │
                  └──────────────────────────────────────────────────────────┘
                                                              ↓
                 RAG 问答 / Wiki 自动生成 / 对话策略   对外：WebUI · API · CLI · IM · Widget · 小程序
```

顶层模块：`cli/ client/ cmd/ config/ docreader/ frontend/ internal/ mcp-server/ migrations/ miniprogram/ deploy/ docker/ helm/`。`internal/agent/` 是推理内核，`tools/` 提供知识检索 / 代码执行 / 数据分析等内置工具，`skills/` 是可插拔技能沙箱。

## 四、应用场景与启发

- **企业知识中枢**：把飞书 / 语雀 / RSS 自动同步进库，给员工一个"问即答"的合规知识助手（金融 / 制造 / 法务等强合规场景尤其适合，因支持私有化与审计）。
- **文档自动维基化（Wiki 模式启发）**：与其人工维护 Confluence，不如让 Agent 周期性读原始文档、生成带链接的 Markdown Wiki + 知识图谱——这是"文档即代码 / 知识自演化"的可借鉴范式。
- **给同类需求的思路**：想做"带 Agent 的 RAG 产品"时，WeKnora 的「ReAct 循环 + 混合检索 + 任务队列 Worker 池 + 权限范围 API Key」组合是现成架构范本；其 `token/compress.go` 式上下文压缩也值得参考。

## 五、源码深度解读

### 1) ReAct 推理循环（internal/agent/）

经典 Think-Act-Observe 编排，目录即契约：`engine.go` 驱动主循环，`think.go` 生成推理，`act.go` 调度工具，`observe.go` 回收观测，`finalize.go` 产出最终答案；`memory/consolidator.go` 做对话记忆整合，`token/compress.go` 做上下文压缩。骨架（基于真实文件名，非逐行源码）：

```
engine.run():
  while not done and steps < max:
    thought  = think(context)            # think.go
    action   = plan(thought)             # act.go 选择 tools/MCP/搜索
    obs      = execute(action)           # observe.go 回收工具结果
    context  = compress(context, obs)     # token/compress.go 上下文裁剪
  return finalize(context)               # finalize.go
```

### 2) 内置工具集（internal/agent/tools/）

`knowledge_search.go`（混合检索入口）、`grep_chunks.go`（库内片段检索）、`data_analysis.go`（数据分析）、`faq_snippet.go`（FAQ 片段召回）等，统一以 `@Skill / @MCP` 提及方式在运行时按轮次范围化加载，避免全量工具塞满上下文。

### 3) 多源接入与解析（docreader/ + config/）

`docreader` 通过 gRPC（TLS + Token）对接解析服务，支持 PDF/Word/图片/Excel/PPT/EPUB 等十余种格式与 VLM/ASR 多模态；`process_config` 支持按批次覆盖解析引擎、分块、图谱抽取配置，并可对存量文档 `reparse`。

## 六、社区口碑

- 发行节奏极快：CHANGELOG 显示从 v0.2.0 到 v0.7.1 几乎每月多版，v0.7.x 持续加入云之家 IM、火山 Rerank、平台级 API Key、Worker 池治理等，迭代活跃度可信。
- 微信生态背书（微信对话开放平台官方框架）是其最强信任状；Trendshift 已收录。
- 具体 Issue / Discussion 情感分布「数据不可用」（本轮未做逐条抓取）；但"全私有化 + 企业 RBAC + 审计"定位明显瞄准对数据合规敏感的 B 端用户。

## 七、竞品对比 + 核心研判

| 维度 | WeKnora | Dify | FastGPT/MaxKB | microsoft/graphrag | RAGFlow |
|------|---------|------|--------------|-------------------|---------|
| 定位 | 知识框架(RAG+Agent+Wiki) | Agent 编排平台 | 知识库问答 | GraphRAG 算法库 | 深度文档解析 RAG |
| Wiki 自动生成 | 是 | 否 | 否 | 部分(仅图谱) | 否 |
| 微信/IM 生态 | 是(微信对话开放平台原生) | 部分(插件) | 部分 | 否 | 否 |
| 企业 RBAC/审计 | 是(四级+空间审计) | 是 | 部分 | 否 | 部分 |
| 部署 | Docker/K8s 私有化 | Docker/K8s | Docker | 库(需自搭) | Docker |

**核心研判**：
- 优势：三引擎一体 + 微信生态 + 企业级权限/可观测，是国产企业知识库赛道的强力选项；私有化与合规卖点清晰。
- 风险：技术栈偏重（Go 微服务 + pgvector/对象存储/Redis/Langfuse 等一堆中间件），运维门槛高；「数据不可用」——未核实其大规模生产案例与社区真实踩坑。
- 启发：若自研"带 Agent 的知识库"，直接借鉴其 ReAct + 混合检索 + Worker 池 + 权限范围 Key 的组合；若只是想用，WeKnora 比 graphrag（纯库）开箱即用，比 Dify 更聚焦知识而非通用编排。

## 八、关键文件路径速查

| 模块 | 路径 |
|------|------|
| ReAct 主循环 | `internal/agent/engine.go` / `think.go` / `act.go` / `observe.go` / `finalize.go` |
| 记忆/上下文压缩 | `internal/agent/memory/consolidator.go` · `internal/agent/token/compress.go` |
| 内置工具 | `internal/agent/tools/knowledge_search.go` · `grep_chunks.go` · `data_analysis.go` · `faq_snippet.go` |
| 解析服务 | `docreader/` · `config/`（process_config） |
| 权限/审计 | `internal/` RBAC（v0.6.0+）· `docs/RBAC说明.md` |
| 部署 | `docker-compose.yml` · `helm/` · `deploy/` |
| MCP / 小程序 / 插件 | `mcp-server/MCP_CONFIG.md` · `miniprogram/` · Chrome 扩展 |
