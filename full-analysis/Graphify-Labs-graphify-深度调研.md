# 🔍 Graphify-Labs/graphify — 全方位深度调研

> **调研日期**: 2026-07-14 | **Stars**: 84,377 ⭐ | **Forks**: 8,323 | **Open Issues**: 498 | **License**: MIT
> **语言**: Python（PyPI 包名 `graphifyy`，CLI 命令 `graphify`）| **背景**: YC S26
> **最新发布**: v0.9.14（2026-07-13，当日发布，极高活跃度）

---

## 一、项目定位（一句话）

一个给 AI 编码助手用的 **代码知识图谱技能**——把整个项目（代码、SQL schema、文档、PDF、图片、视频）解析成一张**可遍历的真实图谱**，让你用 `query / path / explain` 提问，而不是 grep 一堆文件；代码用 tree-sitter AST **本地**解析（零 LLM 调用），只有文档/媒体做语义层才走模型 API。

## 二、项目亮点（差异化）

1. **代码零 LLM、纯本地**：代码用 tree-sitter AST 确定性解析（覆盖 ~40 语言、36 个 grammar），不调模型、不出机器；构建图谱的 LLM 成本为 **0**（ benchmark 实测）。
2. **每条边都带置信标签**：`EXTRACTED`（源码明写，如 import/直接调用）/ `INFERRED`（合理推断，如调用图二pass）/ `AMBIGUOUS`（不确定、标给人审）——你能分清"读到的"和"猜的"。
3. **不是向量索引，是真实图**：不用 embedding、不用向量库，而是 NetworkX 图 + Leiden 社区检测，支持最短路径追踪、`explain` 单点展开、`query` 自然语言取子图。
4. **"为什么"成为一等公民**：`# NOTE:` / `# WHY:` / `# HACK:` 注释与 ADR/RFC 引用被抽成独立节点并连回代码，架构意图不再散落。
5. **20+ Agent 原生 + MCP 服务**：Claude Code / Cursor / Codex / Gemini CLI / Copilot 等一行 `graphify install` 接好；还能起 MCP stdio/http server（`query_graph` / `get_neighbors` / `shortest_path` / `triage_prs` 等工具），团队共享一份图。

## 三、核心架构

核心设计：**Claude Code skill 编排一个 Python 库；库也能独立用**。管道是 7 个纯函数、各管一个模块，通过普通 Python dict 和 NetworkX 图通信，无共享状态，副作用只落在 `graphify-out/`。

```
detect() → extract() → build_graph() → cluster() → analyze() → report() → export()
```

来自 `ARCHITECTURE.md` 的模块职责表（节选）：

| 模块 | 函数 | 职责 |
|------|------|------|
| `detect.py` | `collect_files(root)` | 目录 → 过滤后的 `[Path]` |
| `extract.py` | `extract(path)` | 文件 → `{nodes, edges}`（tree-sitter / 语义） |
| `build.py` | `build_graph(...)` | extraction 列表 → `nx.Graph` |
| `cluster.py` | `cluster(G)` | 图 → 带 `community` 属性的图（Leiden） |
| `analyze.py` | `analyze(G)` | god nodes / 意外连接 / 建议问题 |
| `report.py` | `render_report(G, analysis)` | → `GRAPH_REPORT.md` |
| `export.py` | `export(G, out_dir)` | → graph.json / graph.html / svg / Obsidian |
| `serve.py` | `start_server(graph_path)` | → MCP stdio server |
| `security.py` | `validate_url/...` | 所有外部输入先过校验 |

**提取输出 schema**（每个 extractor 都返回这个，再经 `validate.py` 校验）：
```json
{
  "nodes": [{"id": "unique", "label": "human name", "source_file": "p", "source_location": "L42"}],
  "edges": [{"source": "a", "target": "b", "relation": "calls|imports|uses",
             "confidence": "EXTRACTED|INFERRED|AMBIGUOUS"}]
}
```

**安全**：所有外部输入过 `security.py`——URL 仅 http/https + 阻断 `file://` 重定向；抓取有大小/超时上限；图路径必须解析在 `graphify-out/` 内；节点 label 去控制字符、截断 256、HTML 转义。

## 四、应用场景与启发

- **替代"AI 读完整仓库"的记忆方案**：graphify 的 `graph.json` 是给 Agent 的"代码索引"，比把整个 README/目录灌进 context 省 token 得多。同类需求（你给自己的 Agent 加代码感知）可直接复用其"AST 本地抽 → 图存盘 → MCP 按需查询"三段式，而不是每次全量 RAG。
- **置信标签是可复用设计**：任何"AI 从代码/文档抽取关系"的系统，都应像 graphify 一样给每条边打 `EXTRACTED/INFERRED/AMBIGUOUS`——否则使用者无法判断结论可信度。这是它区别于普通向量库的关键。
- **团队共享图 + git 合并驱动**：`graphify-out/` 提交进 git，`graphify hook install` 装 post-commit 自动重建 + 图合并驱动（graph.json 永不出现 conflict marker）。这是"代码索引随仓库走"的优雅实现，值得借鉴到任何需要团队共享派生产物的场景。
- **PR triage 是隐藏亮点**：`graphify prs --triage / --conflicts` 按图社区给 review 队列排序、标出共享社区的 PR（合并顺序风险）——把"代码理解"直接连到"协作流程"，是知识图谱少见的落地到工程流程的做法。

## 五、源码解读（关键模块）

**1. 七段式无状态管道**（ARCHITECTURE.md 核心）
```python
# 每个 stage 是独立函数，输入输出都是 dict / nx.Graph，无共享状态
G = build_graph([extract(p) for p in collect_files(root)])   # detect→extract→build
G = cluster(G)                      # Leiden 社区检测，写 community 属性
analysis = analyze(G)               # god nodes / surprises / questions
md = render_report(G, analysis)     # GRAPH_REPORT.md
export(G, "graphify-out/")          # graph.json + graph.html + svg ...
```
要点：模块间靠纯数据传递，测试可纯单测（无网络、无 tmp_path 外副作用），新语言 extractor 按 `extract_<lang>` 模式加函数 + 注册后缀即可。

**2. 置信标签的判别式**
`EXTRACTED`=源码显式（import/直接调用）；`INFERRED`=合理推断（调用图二pass、上下文共现）；`AMBIGUOUS`=不确定、在 GRAPH_REPORT 里标人审。这让"图查询"结果天然带可信度元信息，MCP 工具 `query_graph` 返回的边也能直接透出 confidence。

## 六、全网口碑

- **社区信号**：84K⭐ / 8.3K forks / 498 open issues，YC S26 背景，活跃度极高（v0.9.14 当日发布）；支持 20+ Agent、提供 Discord；benchmark 页公开（LOCOMO recall@10 **0.497** vs mem0 0.048、supermemory 0.149；LongMemEval-S 76% 持平 dense RAG；图构建 LLM 成本 0）。
- **口碑倾向**：正面集中在"本地优先/隐私好""图比向量检索更可解释""PR triage 实用"；疑虑多在执行文件体积（>5000 节点时 graph.html 打不开，需 `--no-viz` 走 JSON）、以及语义层（docs/PDF/视频）仍依赖外部 API key。
- **数据不可用**：具体 Twitter/Reddit 单帖评分未抓取；以上基于仓库元数据 + README 自述 + benchmark 页推断。

## 七、竞品对比 + 核心研判

| 维度 | graphify | mem0 / supermemory | repo-index(RAG) | Sourcegraph Cody |
|------|----------|-------------------|-----------------|------------------|
| 代码解析 | tree-sitter 本地、零 LLM | 主要靠 LLM 抽取 | LLM chunk+embed | 索引 + LLM |
| 存储 | 真实图（NetworkX） | 向量库 | 向量库 | 索引 |
| 边置信 | EXTRACTED/INFERRED/AMBIGUOUS | 无 | 无 | 部分 |
| 可解释/路径 | ✅ 最短路径追踪 | ❌ | ❌ | 弱 |
| 隐私 | 代码不出机 | 视后端 | 视后端 | 视部署 |

**核心研判**：
- **优势**：把"代码理解"从"丢给 LLM 做 RAG"升级成"本地 AST 建图 + 按需查询"，成本低、可解释、隐私好；置信标签 + 社区检测 + "why"节点是差异化的三件套；MCP server 让它真正嵌进 Agent 工作流。
- **风险**：图规模大时 HTML 可视化是瓶颈；语义层（非代码）仍依赖外部模型；生态虽广但部分集成（如 OpenClaw/Aider）并行抽取支持早期；498 open issues 说明功能扩张快、边界 case 多。
- **趋势判断**：在"Agent 需要代码级记忆"成为刚需的当下，graphify 的"本地图谱 + MCP"路线比纯向量记忆更有后劲。对想自建代码感知能力的团队，它是最值得直接借鉴（甚至直接装）的开源实现。

## 八、关键文件路径速查

- `ARCHITECTURE.md` — 七段式管道、模块职责表、提取 schema、加语言 extractor 流程、安全模型
- `graphify/extract.py` — `extract()` + 各 `extract_<lang>()`（tree-sitter 解析核心）
- `graphify/build.py` / `cluster.py` / `analyze.py` — 建图 / Leiden 社区 / god节点&意外连接
- `graphify/serve.py` — MCP stdio/http server（`query_graph` / `shortest_path` / `triage_prs` 等）
- `graphify/security.py` — `validate_url` / `safe_fetch` / `validate_graph_path` / `sanitize_label`
- `skills/graphify/skill.md` — 注入 Agent 的 `/graphify` 技能文件
- `BENCHMARKS.md` — LOCOMO / LongMemEval 对比表与复现命令
- `SECURITY.md` — 完整威胁模型
