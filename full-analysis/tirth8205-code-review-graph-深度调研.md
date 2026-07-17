# tirth8205/code-review-graph 深度调研报告

> 调研时间：2026-07-18 | Stars：19,684 | Forks：2,106 | License：MIT
> 主语言：Python（3.10+） | 定位：local-first 代码智能图谱，面向 MCP / CLI 的 AI 编码上下文压缩层

---

## 一、项目全景

### 一句话定位

**code-review-graph（CRG）是一个本地优先（local-first）的代码智能图谱：用 Tree-sitter 把仓库解析成「函数 / 类 / 导入」节点 +「调用 / 继承 / 测试覆盖」边的图，存在本地 SQLite，在 AI 编码工具做 code review / 架构分析时，只把「受影响的极小文件集」喂给模型，而不是让 Agent 重读整个仓库。**

### 核心指标

| 维度 | 数据 |
|------|------|
| GitHub Stars | 19,684（2026-07-18，创建于 2026-02，约 5 个月涨至近 2 万） |
| Forks | 2,106 |
| Open Issues | 115（社区活跃） |
| 许可证 | MIT |
| 主语言 | Python 3.10+ |
| 分发 | PyPI（`pip install code-review-graph`） |
| 集成平台 | 15+：Codex、Claude Code、Cursor、Windsurf、Zed、Continue、OpenCode、Gemini CLI、Qwen、Qoder、Kiro、GitHub Copilot 等 |
| MCP 工具 | 30 个 + 5 个 MCP Prompts 工作流模板 |

### 解决的真问题

AI 编码工具在 review / 理解大仓库时，往往会把大量源码重新塞进上下文。CRG 的核心主张是：**「别烧 token，聪明地 review」**——仓库解析成图后，每次只返回 blast radius（变更波及范围）内的文件，典型场景 token 削减中位数 **~82x**（fastapi 单仓最佳 528x）。

---

## 二、核心架构

### 2.1 处理管线（Pipeline）

```
Repository
   │  git ls-files（只索引 tracked 文件）
   ▼
Tree-sitter Parser（40+ 语言 + Jupyter）
   │  提取 function / class / import / call site / inheritance / test
   ▼
SQLite Graph（nodes + edges，存于 .code-review-graph/）
   │  edges 带三级置信：EXTRACTED / INFERRED / AMBIGUOUS
   ▼
Post-processing（flow detection / community detection-Leiden / FTS5 索引）
   ▼
Blast-radius 分析（变更 → 调用者/依赖/测试）
   ▼
Minimal Review Set（~2,000–3,500 tokens 的精准上下文）
   │
   └─► MCP Server（30 tools）► AI 编码工具按需查询
```

### 2.2 四大支柱能力

1. **Blast-radius（波及范围）分析**：文件变更时，图追溯每一个调用者、依赖、测试，算出变更的「爆炸半径」，AI 只读这些文件。
2. **增量更新 < 2 秒**：hook / watch 模式触发时，按 SHA-256 哈希找出变更文件的依赖，只重解析真正变了的（2,900 文件项目重索引 < 2 秒）。
3. **Monorepo 友好**：大仓 token 浪费最痛，CRG 把 27,700+ 文件排除在 review 上下文外，实际只读 ~15 个文件。
4. **本地优先 + 零遥测**：图存在本地 SQLite，无任何外部服务调用；语义搜索的向量 embedding 是可选的，且 base URL 指向 localhost 时自动跳过云外联警告。

### 2.3 30 个 MCP 工具（节选关键）

| 工具 | 作用 |
|------|------|
| `get_minimal_context_tool` | 超紧凑上下文（~100 tokens），**应第一个调用** |
| `get_impact_radius_tool` | 变更文件的爆炸半径 |
| `get_review_context_tool` | token 优化的 review 上下文 + 结构摘要 |
| `query_graph_tool` | 调用者 / 被调用者 / 测试 / 导入 / 继承查询 |
| `traverse_graph_tool` | 从任意节点 BFS/DFS 遍历（带 token 预算） |
| `detect_changes_tool` | 风险评分的变更影响分析 |
| `get_hub_nodes_tool` / `get_bridge_nodes_tool` | 架构热点 / 瓶颈节点 |
| `get_knowledge_gaps_tool` | 结构弱点、未测热点 |

并附带 5 个 MCP Prompts 工作流模板：`review_changes` / `architecture_map` / `debug_issue` / `onboard_developer` / `pre_merge_check`。

---

## 三、源码深度解读

> 基于 `code_review_graph/` 包实读，聚焦「图分析算法」与「解析/增量」两块。

### 3.1 图分析算法（`analysis.py`）

`analysis.py` 是 CRG 的「架构体检中心」，纯函数式、直接读 `GraphStore`。三个核心能力代码极其干净：

- **Hub 检测**（`find_hub_nodes`）：遍历所有 edge 统计 in/out degree，排除 File 节点后按总度排序取 Top-N——找「最被依赖」的架构热点。
- **Bridge 检测**（`find_bridge_nodes`）：用 networkx 的 `betweenness_centrality`（>5000 节点时采样近似）找「处在多对节点最短路径上的瓶颈」；这些节点一旦坏掉，多个社区失联。
- **Surprise 评分**（`find_surprising_connections`）：给跨社区(+0.3)、跨语言(+0.2)、外围→枢纽(+0.2)、跨测试边界(+0.15)、异常边类型(+0.15) 的耦合累加分数，揪出「不该有关联却有关联」的异味耦合。

```python
# analysis.py 节选：surprise 评分的累加逻辑（结构异味检测）
if src_cid != tgt_cid:           score += 0.3   # cross-community
if src_lang != tgt_lang:         score += 0.2   # cross-language
if (src_deg <= 2 and tgt_deg >= high_deg_threshold) or (...):
                                  score += 0.2   # peripheral-to-hub
if src.is_test != tgt.is_test and e.kind == "CALLS":
                                  score += 0.15  # cross-test-boundary
```

`generate_suggested_questions()` 则把上述分析自动转成 review 问题（bridge 是否充分测试？hub 是否缺测试？跨社区调用是否有意？），直接喂给 Agent。

### 3.2 解析与增量（`parser.py` / `incremental.py`）

- `parser.py`（约 388KB，最大模块）是 Tree-sitter 的统一 walker：把各语言的 node type（function/class/import/call）映射到统一图 schema。新增语言只需在 `code_review_graph/parser.py` 的 `EXTENSION_TO_LANGUAGE` 加映射，或在 `.code-review-graph/languages.toml` 放一份 TOML（**无需 fork、无需改代码**）。
- `incremental.py` 负责增量更新：用 SHA-256 哈希比对变更文件、找依赖、只重解析变化部分。这是「2,900 文件 < 2 秒」的支撑。

### 3.3 一句话源码研判

CRG 的工程水准高于多数「AI 工具」项目：**结构清晰、算法可解释、处处留可配置旋钮**（30+ 环境变量如 `CRG_MAX_IMPACT_DEPTH`、`CRG_TOOLS` 工具白名单）。它把「代码理解」做成了可查询的本地服务，而不是又一个黑盒 RAG。

---

## 四、应用场景与启发

### 4.1 最适合的场景

1. **大仓库 / Monorepo 的 AI code review**：让 Claude Code / Codex 在 review PR 时只读 blast radius，避免整仓重读。
2. **CI 风险门禁**：GitHub Action 在每次 PR 贴「风险评分 + 受影响执行流 + 测试缺口」的 sticky 评论，可选 `fail-on-risk` 做合并门。
3. **架构 onboarding**：新人不读全码，用 hub/bridge/knowledge-gap 快速理解热点与瓶颈。
4. **多仓检索**：`crg-daemon` 后台 watch 多个仓库，跨仓搜索。

### 4.2 不适合的场景（项目自己承认）

- 小仓库、单文件 trivial diff、一次性问题——图的结构元数据开销反而比直接读文件大。
- 需要精确符号级跳转时，LSP 仍更准（CRG 是跨语言持久图，LSP 是 per-language daemon）。

### 4.3 给同类需求的启发

- **「上下文压缩」正成为 AI 编码的刚需层**：CRG 证明「结构化图谱 + blast radius」比「grep + 全读」或「RAG chunk」在 multi-hop 问题上更省 token。
- **local-first + 零遥测** 是开发者工具建立信任的关键——尤其涉及源码结构这种敏感数据。
- **方法论诚实** 本身也是产品力：明确标注「recall 1.0 是图内循环上界」「MRR 0.35 搜索待改进」，反而比粉饰数字更可信。

---

## 五、社区口碑

> 说明：CRG 是 2026-02 创建、近期快速走红（GitHub Trending）的新项目，深度第三方长评测尚少。以下口碑信号均来自官方仓库可观测数据与项目公开声明，未做外部评论编造。

- **增长势能与分发**：约 5 个月涨至 19.6K⭐ / 2.1K fork，PyPI 分发 + 15+ 平台一键 `install` 自动注入 MCP 配置，降低了采用门槛。
- **工程诚实度（最强口碑信号）**：README 的 Benchmarks 章节罕见地**自曝短板**——impact「recall 1.0」是图内循环上界（circular by construction）、搜索 MRR 仅 0.35、flow detection 33% recall、小单文件改动图开销反而更大。这种「主动标注局限性」在 AI 工具里很少见，是高质量项目的标志。
- **文档完整度**：英文 + 简/日/韩/印地 5 语 README，独立 `docs/` 含 USAGE / COMMANDS / FAQ / TROUBLESHOOTING / REPRODUCING / ROADMAP，且有确定性可复现的 benchmark 配方。
- **活跃度**：115 open issues、Discord 社区、CI 与 eval 周跑，显示维护在正常运转。

---

## 六、竞品对比

### 6.1 与同类代码图谱 / 上下文工具

| 维度 | code-review-graph | Graphify（本库已调研） | Serena | repomix | grep/agentic search |
|------|-------------------|------------------------|--------|---------|---------------------|
| 存储 | 本地 SQLite 图 | 本地图 + MCP server | MCP（符号） | 打包成单一文本 | 无状态 |
| 核心 | blast-radius + 风险评分 | 知识图谱 + 边置信标签 | LSP 符号级 | 全量上下文打包 | 关键词/语义匹配 |
| 多跳能力 | 强（调用者/被调用者/测试） | 强 | 中 | 弱 | 弱（单跳） |
| 语言覆盖 | 40+（含 Jupyter） | tree-sitter 子集 | LSP 决定 | 任意（原文） | 任意 |
| 增量更新 | < 2s（SHA 比对） | 视实现 | — | 无 | 无 |
| 云依赖 | 零遥测，embedding 可选 | 本地优先 | 本地 | 本地 | 本地 |
| CI 集成 | GitHub Action 风险门禁 | 无内置 | 无内置 | 无 | 无 |

> 注：本库已收录 `Graphify-Labs/graphify`（代码知识图谱技能，tree-sitter 本地建图 + 边置信标签 + MCP server，替代 grep/RAG）。CRG 与 Graphify 思路同源（本地 AST 建图），但 CRG 更偏「code review 上下文压缩 + CI 风险门禁 + 多平台一键装」，Graphify 更偏「Agent 可调用的知识图谱技能」。

### 6.2 与 LSP / RAG 的本质区别（来自官方 FAQ）

- **vs LSP**：一个跨语言持久图，而非 per-language daemon；LSP 在单符号精度上仍更优。
- **vs RAG/embedding**：边是 AST 结构性解析出来的，不是相似度 chunk；embedding 仅辅助搜索，可选。
- **vs grep**：grep 在一跳查找赢，图在 multi-hop（影响半径、callers-of-callers、tests-for）赢。

---

## 七、核心研判

### 7.1 项目优势

- **切中 AI 编码的真实痛点**：上下文爆炸是 Agent 编码的头号成本，CRG 用「结构化图 + blast radius」给出可量化的 token 削减（中位数 82x）。
- **local-first + 零遥测 + MIT**：源码结构敏感数据不出本机，信任成本低，企业可用。
- **工程成熟度超预期**：30 MCP 工具、5 工作流模板、确定性 benchmark、CI Action、多仓 daemon、15+ 平台自动配置——完成度远高于同阶段项目。
- **方法论诚实**：主动标注局限性，长期口碑加分。

### 7.2 项目风险

- **搜索质量仍是短板**：MRR 0.35、flow detection 33% recall——语义/执行流检索体验待打磨。
- **小改动负收益**：trivial 单文件 diff 时图开销 > 直接读，需用户自行判断启用时机。
- **blast-radius 保守倾向**：precision 0.578（avg）偏低，大依赖图会有 false positive，需人工过滤。
- **生态新、长期维护未验证**：2026-02 才创建，能否持续维护待观察。

### 7.3 趋势判断

- 「AI 编码上下文压缩层」正从玩具变成刚需，CRG 与 Graphify 等代表「本地代码图谱」这一新品类。
- 若搜索/flow 精度补齐，CRG 有望成为 AI 编码工具的「标配中间件」（类似当年 ctags/LSP 的角色）。
- CI 风险门禁（fail-on-risk）是企业落地的关键钩子，可能先于交互式用法被采纳。

### 7.4 给同类需求的启发

- 做 AI 编码基础设施时，**先解决「少读无用上下文」比「读更多」更有杠杆**。
- 本地图 + MCP 是可复用的范式：把「代码理解」做成 Agent 可查询的服务，而非内嵌在单个工具里。

---

## 八、关键文件路径速查

| 路径 | 作用 |
|------|------|
| `code_review_graph/parser.py` | Tree-sitter 统一 walker，语言 node type → 统一图 schema（最大模块 ~388KB） |
| `code_review_graph/analysis.py` | 图分析：hub / bridge（betweenness）/ knowledge-gap / surprise 评分 / 自动 review 问题 |
| `code_review_graph/changes.py` | 变更检测与风险评分（detect_changes 核心） |
| `code_review_graph/incremental.py` | 增量更新（SHA-256 比对 + 依赖重解析，< 2s） |
| `code_review_graph/graph.py` | `GraphStore`：SQLite 图存储 + networkx 桥接 |
| `code_review_graph/communities.py` | Leiden 社区检测 |
| `code_review_graph/flows.py` | 执行流追踪（入口 → 加权关键度排序） |
| `code_review_graph/daemon.py` | 多仓 watch daemon（健康检查 + 自动重启） |
| `code_review_graph/tools/` | 30 个 MCP 工具实现 |
| `code_review_graph/token_benchmark.py` | token 效率基准（5 个样本问题） |
| `.code-review-graph/languages.toml` | 用户自定义语言（免 fork） |
| `.code-review-graphignore` | 排除索引路径（类比 .gitignore） |

---

> **声明**：本报告数据来自 GitHub API 实时获取与项目官方 README / 源码（`code_review_graph/` 包）实读，未编造任何第三方评论；口碑章节已明确标注信号来源。项目数据以 GitHub 实时信息为准。
