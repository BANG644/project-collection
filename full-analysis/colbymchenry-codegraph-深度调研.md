# CodeGraph 深度调研（colbymchenry/codegraph）

> 调研日期：2026-11-27 ｜ 星标：78,777 ⭐（5,257 forks / 261 open issues）｜ 语言：TypeScript ｜ 协议：MIT ｜ 创建：2026-01-18 ｜ 最近推送：2026-11-23 ｜ 默认分支：main
>
> **旧稿问题**：2026-06-19 模板骨架——"预索引层/自动同步层/Agent 集成层"三段抽象空话、口碑写"没有可靠第三方长评"、关键路径全是占位符。本次基于真实源码树（`src/engine.ts`、`src/db/wal-valve.ts`、`AGENTS.md`、`TELEMETRY.md`）与多份第三方实测全文重写，沿用原文件位置与索引编号。

## 一、项目定位（一句话）

CodeGraph 是**本地优先的代码知识图谱库 + CLI + MCP server**：用 tree-sitter 把代码解析成符号/边/文件存入 SQLite（FTS5），经 MCP 暴露给 Claude Code、Cursor、Codex、Gemini CLI、OpenCode、Kiro、Copilot、Hermes 等编码 Agent，让 Agent 用"一次结构查询"替代"反复 grep + 逐文件读"，从而省 token、少工具调用。核心承诺：确定性提取（AST 派生，非 LLM 摘要）、100% 本地、代码变更自动增量同步。

## 二、项目亮点（差异化，开篇呈现）

- 📉 **有真实基准而非口号**：第三方 andrew.ooo 复现 README 的 7 仓库 × 4 轮中位数（Opus 4.7 headless, `--strict-mcp-config`）：VS Code（~10k 文件）$0.60→$0.80、601k→2.8M tokens、8→55 次工具调用；Excalidraw 工具调用 3 vs 79（-96%）。**OkHttp 是诚实的离群点**（仅便宜 2%），作者自己标注"并非每个问题都值得用图"。
- 🛡️ **遥测"默认开但完全可审计"的诚实设计**：README 主打"100% local"，但 `TELEMETRY.md` 明说会采集匿名使用统计（命令/语言/Agent 类型，不含代码/路径/IP），ingest 端点用 allowlist 且 worker 源码在仓库内公开；`codegraph telemetry off` / `CODEGRAPH_TELEMETRY=0` / `DO_NOT_TRACK=1` 可彻底关闭，"off means off"。
- ⚙️ **WAL 阀门——为机械硬盘做工程optimization**：`src/db/wal-valve.ts` 记录了 defer checkpoint 让 bulk index 从 19+ 分钟降到 45 秒（95% 磁盘 I/O 来自反复重写热页），又用"基于上次完整 backfill 的基线跟踪增长"解决"WAL 文件永不缩小导致 size-trigger 永久触发"的陷阱。这是 README 绝不会写的硬核细节。
- 🧪 **测试即护城河**：仓库有数百个 `__tests__/`，文件名直白暴露覆盖边界（`call-receiver-no-fabrication.test.ts`、`ambient-module-imports.test.ts`、`chinese-filename-retrieval.test.ts`、`cjk-query-tokens.test.ts`）——针对"解析准确性"这一命门做回归网。
- 📦 **一个二进制三种角色**：`@colbymchenry/codegraph` npm 包同时是安装器、索引器与 MCP server；`codegraph install -i` 自动探测并写入 8 种 Agent 的 MCP 配置，"system prompt shim 与索引同等重要"。
- 🌍 **跨语言/跨端桥接**：Swift↔ObjC `@objc`、JS `NativeModules.X.fn()` ↔ ObjC `RCT_EXPORT_METHOD`/Java `@ReactMethod`、Expo Module DSL 等静态解析器通常丢弃的桥接关系被显式建模。

## 三、核心架构

```
源码文件 --tree-sitter--> AST --extraction/languages/*--> 符号/边
   --> resolution (import/alias/route/bridge 解析) --> SQLite(FTS5) @ .codegraph/
   --> watcher 增量同步 --> MCP tools (context/explore/node/search/callers/impact…)
   --> Claude Code / Codex / Cursor / Gemini / OpenCode / Kiro / Hermes
```

关键设计：`src/engine.ts` 顶部注释明确"构建/更新索引的那一半"通过 `./lazy-engine` 的 `engine()` 访问，**只读索引的命令绝不 import 它**——用显式门面隔离重依赖，避免每次查询都加载整条提取链。`src/extraction/` 按语言拆 adapter（java/python/go/rust/php/csharp/swift/cfml/cobol… 20+），配合 `parse-pool.ts`/`parse-worker.ts`/`parse-budget.ts` 控制解析成本；`src/db/` 负责 schema、FTS5、name-substring 索引、参数流查询与 WAL 阀门；`src/sync/watcher.ts` 负责变更增量。AGENTS.md 特别规定 `copy-assets` 必须把 schema.sql 与 grammar wasm 拷进 dist，否则 viewer 高亮与提取都会缺件。

## 四、应用场景与启发

- **大仓库架构问答**："鉴权怎么走的""扩展宿主怎么和主进程通信"一次 `codegraph_explore` 拿到入口点 + 邻居；VS Code 级仓库可实现 Agent 零文件读取直接作答。
- **影响面分析**：`codegraph impact <symbol> --depth=2`、`codegraph affected src/auth.ts` 在改动前找受影响测试与调用点。
- **CI/自定义 Agent 的上下文供给**：可当 Node 库嵌入——`CodeGraph.init(path)` → `indexAll()` → `searchNodes()` → `watch()`，用于脚手架或自家 Agent。
- 💡 **启发一（收益随仓库规模跃迁）**：andrew.ooo 的实测结论是 ROI 在 ~1k 文件处开始显现、5k 以上戏剧性放大；110 文件的 Gin 只有 21% 成本优势。**别在小项目上背索引负担**。
- 💡 **启发二（父 Agent 的委派方式决定成败）**：作者自述的 caveat——若父 Agent 把探索委托给会读文件的 sub-agent，图谱永远不会被调用，反而变成纯开销。所以 **system prompt shim 与索引同等重要**；接入时要把"先查 codegraph"写进指令层。
- 💡 **启发三（"本地优先"与遥测可以并存但要讲清楚）**：把采集字段写成 allowlist、worker 开源、提供 `telemetry status` 与一键关闭，比含糊宣称"100% local"更可取；`DO_NOT_TRACK=1` 连后台版本检查一起关，是尊重用户选择的细节。

## 五、源码深度解读（真实路径）

### 1. `src/engine.ts` —— 用门面隔离重依赖

```ts
/**
 * The half of CodeGraph that builds and updates an index: extraction,
 * resolution and the file watcher. `src/index.ts` reaches all of it through
 * `engine()` in `./lazy-engine`, never with an import of its own, so a command
 * that only reads an index doesn't load it.
 */
export { ExtractionOrchestrator, extractFromSource } from './extraction';
export { FileWatcher } from './sync/watcher';
```

一个"导出清单 + 懒加载门面"就把只读命令与构建链切开。对任何"读写两条路径成本悬殊"的工具，这是低成本的启动性能优化范式。

### 2. `src/db/wal-valve.ts` —— 从 19 分钟到 45 秒，再到 5.9GB 事故

注释披露的因果链：SQLite 默认 `wal_autocheckpoint=1000` 在 bulk index 中反复重写热 B-tree/FTS 页，**占全部磁盘 I/O 的 ~95%**；在 150 IOPS 的 HDD 上，defer checkpoint 把耗时从 19+ 分钟压到 45 秒。但无界 defer 会撑出 **5.9GB WAL（DB 仅 ~340MB）**，第一次解析读阻塞主线程 >60 秒，被 `#850` liveness watchdog 杀掉。

```ts
// 核心洞察：WAL 文件大小永不缩小；size-trigger 一旦越过阈值就永久触发。
// 正确做法：跟踪 sizeAtLastFullBackfill（checkpoint 报告 log === checkpointed 时刷新），
// 只对"相对基线的增长"触发；增长超 2× soft cap 时对 writer 施加 backpressure。
```

`PRAGMA wal_checkpoint(PASSIVE)` 放在 worker-thread 连接上——PASSIVE 不阻塞 writer，off-thread 保证 watcher 心跳继续转。这段源码是全仓最有借鉴价值的"性能-可靠性权衡实录"。

### 3. `TELEMETRY.md` —— 可关闭、可审计的匿名统计

| 字段 | 例子 | 说明 |
|---|---|---|
| `machine_id` | `b3a8c1…` | 首次发送时随机生成的 UUID，不从任何信息派生 |
| `codegraph_version` / `os` / `arch` / `node_major` / `ci` | `0.9.9` / `darwin` / `arm64` / `22` / `false` | 仅平台标识 |

关闭路径三种：`codegraph telemetry off`（删除本地身份与未发送队列）、环境变量 `CODEGRAPH_TELEMETRY=0`、跨工具标准 `DO_NOT_TRACK=1`（优先级最高）；MCP 单项可加 `--no-telemetry`。注意反向开关 `CODEGRAPH_TELEMETRY=1` 可在存储选择为关时**对该进程强制开启**——企业部署要留意这个覆盖语义。

### 4. `AGENTS.md` —— 给编码 Agent 的构建红线

根文件刻意控制在 ~35KiB（关键 build/test/arch/retrieval 规则），因为环境 `project_doc_max_bytes = 49152`，避免超过 32KiB 默认截断被静默丢规则；长验证方法论拆到 `docs/AGENTS.md`。明确"新增 SQL 或 grammar wasm 必须拷进 dist"，并有 `scripts/check-ui-build.mjs` 在每次构建与发布包里断言。这是"写给 Agent 的规约文件也要做体积治理"的少见实践。

## 六、全网口碑（真实来源）

- **[andrew.ooo 英文实测](https://andrew.ooo/posts/codegraph-review-pre-indexed-knowledge-graph-claude-code)**：给出完整基准原始数据与三条解读——收益随仓库规模放大；工具调用降得比 token 更狠（Excalidraw 3 vs 79）；OkHttp 是诚实离群点。并强调"作者自己的 caveat 很健康"：委派给读文件的 sub-agent 时图谱闲置。
- **[稀土掘金](https://juejin.cn/post/7645917873245585454)**：35K⭐ 一夜爆火标题，逐仓库列出成本/token/时间/工具调用四项数据，VS Code 场景"全程零文件读取、4 次调用出答案"。
- **[liting.life 深度研究](https://liting.life/2026/06/15/codegraph-%E6%B7%B1%E5%BA%A6%E7%A0%94%E7%A9%B6%E6%9C%AC%E5%9C%B0%E4%BB%A3%E7%A0%81%E7%9F%A5%E8%AF%86%E5%9B%BE%E8%B0%B1%E4%B8%8E-ai-agent-%E5%8A%A0%E9%80%9F%E5%99%A8/)**：median 成本↓16%/token↓47%/时间↓22%/工具调用↓58%；MCP 四核心工具 + `CODEGRAPH_MCP_TOOLS` 扩展集；遥测字段与关闭方式；"索引完全本地、遥测仅聚合数据"。
- **[時光博客](https://blog.shiguang666.eu.org/2026/06/12/a75acce9f707)**：v0.9.9（2026-06-02）、TS 92.6%；强调"用 tree-sitter 解析 AST→SQLite，一次 explore 拿完整上下文"。
- **一手信号**：78.8k⭐ / 261 issue、MIT、11 月 23 日仍在推送；`__tests__/` 数量与语言 adapter 数量同步扩张。

## 七、竞品对比 + 核心研判

| 方案 | 图谱深度 | 基准透明度 | 隐私 | 短板 |
|---|---|---|---|---|
| **CodeGraph** | 符号/调用/路由/跨端桥接、20+ 语言 | 7 仓库 × 4 轮，含离群点自曝 | 索引本地、遥测可关 | 需改 Agent 指令 shim；小仓 ROI 低；默认开遥测 |
| GitNexus | 类型推断/PDG/跨仓契约 + Web UI | 无同等公开基准 | 零服务器 | 更重、许可证 NOASSERTION |
| Sourcegraph | 企业级跨仓搜索 | 商业产品 | 服务端 | 部署重、非本地优先 |
| Agent 自带 grep/read | 无结构 | — | 本地 | 大仓库 token/调用爆炸 |

- ✅ **优势**：基准方法论透明（中位数、多轮、诚实 outlier）；工程细节扎实（WAL 阀门、懒加载门面、海量针对误报的测试）；安装/卸载覆盖 8 种 Agent，接入摩擦低。
- ⚠️ **风险**：收益前提苛刻——父 Agent 必须真的调用图谱；110 文件级小仓几乎没有收益；遥测默认开与"100% local"口号有张力；261 issue 与 20+ 语言 adapter 的维护面在快速膨胀。
- 🔮 **研判**：CodeGraph 与 GitNexus 代表两条路线：**前者赌"轻量、可嵌入、成本可证明"，后者赌"图谱深度、跨仓语义"**。如果你的痛点是 Claude Code 账单和工具调用数，且仓库 >1k 文件，CodeGraph 是当前可验证性最好的选择；如果需要跨仓接口契约核对，则 GitNexus 更合适。接入时务必同时做两件事：把"先查 codegraph"写进 Agent 指令层、按隐私要求关掉遥测。

## 八、关键文件路径速查

| 路径 | 看点 |
|---|---|
| `src/engine.ts` | 懒加载门面：只读命令不加载构建链 |
| `src/db/wal-valve.ts` | bulk index 性能与 5.9GB WAL 事故的完整权衡（本报告主依据） |
| `src/db/{schema.sql,queries.ts,parameter-flow-queries.ts,name-substring-index.ts}` | SQLite/FTS5 图谱存储与查询 |
| `src/extraction/languages/` | 20+ 语言 tree-sitter adapter |
| `src/extraction/{parse-pool.ts,parse-worker.ts,parse-budget.ts}` | 解析并发与预算控制 |
| `src/sync/watcher.ts` | 变更增量同步 |
| `src/context/formatter.ts` / `markers.ts` | 返回给 Agent 的上下文格式 |
| `src/bin/codegraph.ts` / `uninstall.ts` / `command-supervision.ts` | CLI 全生命周期 |
| `AGENTS.md` / `docs/AGENTS.md` | 给编码 Agent 的构建红线与体积治理 |
| `TELEMETRY.md` / `telemetry-worker/` | 采集字段 allowlist 与开源 worker |
| `__tests__/call-receiver-no-fabrication.test.ts` 等 | "不许编造调用关系"类回归网 |
