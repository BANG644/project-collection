# xerj-org/xerj 深度调研

> 调研日期：2026-10-16 ｜ 星标：5,447 ⭐（GitHub Trending 日榜，当日 +725）｜ 语言：Rust ｜ 许可：Apache-2.0（LICENSE 文件，GitHub API 标 NOASSERTION）｜ 默认分支：main ｜ 定位：本地优先的 AI 原生搜索引擎 / 索引引擎（Elasticsearch API 兼容），让 coding agent 用"查"替代"读文件"省 token

## 一、项目亮点（差异化）

- **Elasticsearch 线协议兼容**：实现 ES REST API（indices/documents/bulk/search/aggs/kNN/scroll/reindex/`_cat`），现有 Kibana、官方客户端库直连；兼容套件 **1366/1369** 用例通过，且把未实现的 3 例公开列出而非隐藏。
- **`autoindex` 零配置**：一条命令索引任意文件夹——代码经 **tree-sitter** 做 AST 感知索引（带符号名 + 行号，不是平面文本），PDF/DOCX/XLSX/PPTX/EPUB/Jupyter/邮件/日志/Unity 场景等几十种格式自动识别，无 schema、无 pipeline。
- **实测省 token 硬数据**：在 8 任务 × 4 语言 × 16 次/组的受控研究里，coding agent 用 XERJ 比 grep 驱动**少 2.7× output token**、比纯记忆少 **26×**，且 solve rate 相同（16/16）；日常用户报告端到端约 5×。
- **原生 MCP + Agent Memory + Second Brain**：同一二进制即 MCP server（13 个工具），`/_memory/{ns}` 做 agent 长期记忆，`/_graph` 做证据支撑的关系图（8 类检测器 + 两跳上限）。
- **单静态二进制、无 JVM、默认离线**：默认词法 embedder 离线（feature-hashing），神经 embedder 可选（需 ~90MB 模型文件）；预编译 Linux/macOS/Windows 的 x86-64/arm64。

## 二、核心架构（克制）

仓库是 Rust workspace，真正引擎在 `engine/`，MCP/CLI 是同一二进制的子命令：

```
engine/
└── crates/
    ├── xerj-server/       # HTTP + ES REST API 入口（cargo build -p xerj-server）
    ├── xerj-autoindex/    # tree-sitter 解析 + 符号级索引 + 增量 re-index
    ├── xerj-query/        # 查询 DSL 执行（BM25 + kNN + hybrid/RRF）
    ├── xerj-vector/ xerj-fts/ xerj-storage/  # 向量 / 全文 / 存储层
    ├── xerj-mcp/          # MCP stdio server（13 工具，代理到 node）
    ├── xerj-rerank/ xerj-ai/ xerj-hub/ ...   # 重排 / AI / 索引中心
tools/xerj-code/           # reference-coding 管线（hub/swebench/SKILL.md）
engine/tests/es-compat-yaml/  # ES 兼容套件（CI 每提交跑）
```

**信任边界模型**：`--insecure` 启动 = 无 TLS、无鉴权、绑定 `127.0.0.1` 且拒绝跨网卡明文监听（除非显式允许）；任何非回环绑定会拒绝启动。auth-on 模式密钥写在 `<data_dir>/admin.key`。MCP server 不做额外鉴权，节点的边界说了算。见 `docs/SECURITY_MODEL.md`。

## 三、应用场景与启发

- **Reference coding（主场景）**：把开源 repo 索引后，agent 在写代码前先"检索同类项目怎么解决"，让更小更便宜的模型在私有/长尾/post-cutoff 代码上反超记忆型大模型——直接对抗"模型没见过的 API 就 retry 循环"。
- **Agent 长期记忆后端**：`/_memory` 把"agent 学到的东西"按语义存、按语义取，下次会话直接召回——对任意 agent 工作流（如用户的 paper-companion / 错题归因）都是现成的"可查询记忆层"。
- **轻量 ES 替代 + 安全审计**：一个二进制同时做全文/向量/混合检索与聚合；索引整棵代码树后查 sink 模式 / 密钥 / 危险调用，WordPress 核心审计仅 ~26k token。
- **给"agent 上下文管理"的范式启发**：把 grep/逐文件读换成"语义检索 + file:line 段落"——这是降低 agent token 消耗最实在的工程手段之一。

## 四、源码深度解读（选 3 个核心模块）

**1. 索引器 `engine/crates/xerj-autoindex`**
tree-sitter 逐个文件解析，代码以"符号 + 全文"入库；**增量 re-index**：内容与上次索引逐字节相同的文件跳过解析、沿用旧结果，编辑少量文件时工作量仅正比于变更（通常 >95% 不变）。复现基准：`XERJ_EXTRACT_BENCH=... cargo test -p xerj-autoindex --release extract_bench`。

**2. MCP 桥 `engine/crates/xerj-mcp`**
暴露 13 工具，11 个是端点薄代理（`xerj_search`/`xerj_semantic_search`/`xerj_vector_search`/`xerj_hybrid_search`/`xerj_memory_*`/`xerj_brain_*`/`xerj_plan`）；2 个非代理：`xerj_map`（返回 autoindex 目录的字段图）与 `xerj_code_search`（跑 reference-coding 管线）。工具 schema 由 `tools/list` 实时生成并 CI 校验，杜绝文档漂移。

**3. 兼容层 `engine/tests/es-compat-yaml`**
把 ES 官方 YAML 兼容用例搬进仓库逐条跑，公开 1366/1369 通过率——这是它"敢说兼容 ES"的底气，也是评估"能否平替现有 ES 工具链"的依据。

## 五、全网口碑

- **势头**：GitHub Trending 日榜常客、Trendshift 上榜；README 用"field report"（一线使用反馈 PR，免 CLA）驱动社区，透明且低门槛。
- **可信度做法加分**：安全模型明写 `--insecure` 边界、`rerank` 是唯一会把文本发往第三方的搜索阶段并默认禁用、基准把 4 个失败（读 p99 在高频写时）也写成报告而非藏起——整体"可复现、不吹水"调性。
- **争议点**：价值高度依赖"模型是否记住这段代码"——对模型已烂熟的热门库收益中性甚至负；ES 官版在混合读写读 p99 上仍领先（项目自己承认）。

## 六、竞品对比 + 核心研判

| 维度 | XERJ | Elasticsearch | Meilisearch | Qdrant/向量库 |
|------|------|---------------|-------------|---------------|
| 定位 | agent 数据接口 | 通用搜索引擎 | 即时搜索 | 向量检索 |
| 索引配置 | 零配置 autoindex | 需 mapping | 自动 | 需 schema |
| ES 兼容 | 是（1366/1369） | 自身 | 否 | 否 |
| Agent 原生 | MCP + memory + graph | 否 | 否 | 部分 |

**核心研判**：XERJ 不是"重造 ES"，而是把检索重新定义为 **agent 的输入接口**——真正差异化在 autoindex 零配置 + agent memory + MCP 原生 + 透明基准。它的价值曲线是"越私有/越冷门/越 post-cutoff 的代码越赚，越热门的公开库越不赚"。**给同类需求（给 coding agent 配可查询记忆）的启发**：优先评估"这套代码模型记不记得"，再决定上不上检索层；若上，XERJ 的 ES 兼容 + 单二进制 + 本地优先让它成为比搭一套 ES+向量库更轻的选型。

## 七、关键文件速查

- 引擎 workspace：`engine/crates/`（xerj-server / xerj-autoindex / xerj-query / xerj-mcp / xerj-vector / xerj-fts / xerj-storage / xerj-rerank）
- reference-coding：`tools/xerj-code/`（SKILL.md / hub / swebench）
- 文档与边界：`docs/SECURITY_MODEL.md`、`docs/SECOND_BRAIN.md`、`docs/RERANK.md`、`docs/XERJ_VS_LUCENE.md`
- 兼容套件：`engine/tests/es-compat-yaml/`
- 一站入口：`https://xerj.org/llms.txt`（agent 可直接读的 setup 步骤）
