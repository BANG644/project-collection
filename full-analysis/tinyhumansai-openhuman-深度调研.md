# tinyhumansai/openhuman 深度调研

> 调研日期：2026-08-25 ｜ 星标：37,166 ⭐ ｜ 语言：Rust ｜ 协议：GPL-3.0 ｜ 默认分支：main ｜ 最后推送：2026-08-24
> 定位：个人 AI 超级智能（「大脑」+ 编排器 + 深度研究员三位一体），local-first、隐私优先的个人 Agent OS

## 一、项目亮点（差异化）

1. **Memory Tree + Obsidian Wiki 镜像**：把你世界的数据压缩成带评分的 Markdown 树存进本地 SQLite，并镜像为可编辑的 Obsidian 知识库（Karpathy LLM Wiki 范式）——**不是向量黑箱，而是人可读、可改的明文知识**。
2. **海量连接面**：100+ OAuth 集成、5,000+ MCP 服务器、90,000+ Skills 一键接入；Auto-fetch 每 20 分钟本地拉取，使 Agent「次日清晨已拥有今日上下文」。
3. **事件总线驱动的 Agent 编队**：Rust core 用 `tinybus` 进程内事件总线（`OnceBus<DomainEvent>`）做模块解耦，支持「反射型快 Agent 分诊 + 深度推理核 +  subconscious 潜意识层」的分脑编排。
4. **TokenJuice 压缩**：工具输出进模型前压缩，同等信息量 token 减少最高 80%，否则「这么大的脑」经济上不可行。
5. **Privacy Mode 强制本地**：Rust core 内强制「翻转开关后无任何推理离开本机」，配合 OS keyring 密钥、审批门、可选沙箱——隐私不是配置项而是架构保证。

## 二、核心架构

OpenHuman 是 Rust 单体核心 + 多前端（桌面/CLI/17 个消息渠道）的结构：

- **事件内核（`src/core/bus.rs`）**：`tinybus::OnceBus<DomainEvent>` 全局单例，定义本应用的事件目录（含 `EVENTS_ROOT` / `EVENTS_INTERFACE` / `EVENTS_VERSION`）。两个调用面：`BUS.publish`（广播发生了什么）与 `BUS.native()`（进程内传递 `Arc<dyn Tool>`、trait 对象、channel 的请求-应答）。**原生面因携带不可序列化的 Arc/trait，永久留在进程内**。
- **Agent 编排（`src/bin/fleet.rs` / `src/core/agent_cli.rs`）**：Agent 以 checkpointed graph 跑在开源 `tinyagents` 上，子 Agent 可三层嵌套，卡住的 Agent 变成根因报告；`bin/library_profile/scenarios/` 下有一整套性能画像场景（agent_turn / cold_phases / fleet / subagent_storm / workflow / memory_ingest）。
- **API 层（`src/api/`）**：`api/mod.rs` + `api/rest.rs` + `api/socket.rs` + `api/jwt.rs` + `api/models/`（auth / socket / product），对外暴露 REST + WebSocket + JWT 鉴权。
- **编排拓扑（README 明示）**：Graphs-not-loops（图而非循环，可暂停/重启/续跑）、Sub-agent fleets、split-brain（reflex + deep core + subconscious）、Agent economy（`@handle` on tiny.place，Signal 加密的 Agent 间编排 + x402 USDC 赏金）。
- **Brain 子系统**：Memory Tree（SQLite + 压缩 Markdown）、Obsidian Wiki 镜像、Goals & Todos、TokenJuice。
- **配套开源子仓**：`tinyflows`（workflow 画布引擎）、`tinyagents`（checkpointed graph harness）、`tinybus`（事件总线 crate）——核心能力下沉为独立可复用 crate。

## 三、应用场景与启发

- **个人知识/记忆中枢**：连接 Gmail/Notion/GitHub/Slack 等，20 分钟自动同步，构建可编辑的本地「第二大脑」，新手分钟级上手（区别于 Claude Code 需数周养上下文）。
- **Agent 编队与自动化**：把重复性工作流固化成 trigger-driven、approval-gated 的 graph，可重放并带真实 per-call 成本。
- **跨 Agent 编排**：用 Signal 加密的 Agent 间消息，把 Claude Code / Codex / OpenClaw / Hermes 等统一编排——是一个「Agent 的 Agent」。
- **架构启发**：
  - 「**明文 Memory 树 + 知识图谱镜像**」优于纯向量库：可审计、可编辑、可被人类直接复用，缓解了 RAG 黑箱不可解释的痛点。
  - 「**事件总线 + 原生面/广播面双通道**」是进程内多模块解耦的优雅方案——可序列化的走总线跨进程，不可序列化的（Arc/trait/channel）留在 native 面，避免为了跨进程而强行序列化导致的性能/复杂度灾难。
  - 「**TokenJuice 前置压缩**」是让「大记忆」经济可行的关键杠杆，值得任何长上下文 Agent 产品借鉴。

## 四、源码深度解读

### 1. 进程内事件总线（`src/core/bus.rs`）
`pub static BUS: OnceBus<DomainEvent> = OnceBus::new();` 是全局单例，类型由宿主声明（泛型 `OnceBus<E>` 无法自带 static，故由本应用固化 `DomainEvent`）。它显式区分两种面：
- **广播面**（`BUS.publish`）：事件被序列化，跨进程 peer 可订阅；
- **原生面**（`BUS.native().request(...)`）：传递 `Arc<Vec<Box<dyn Tool>>>` 与活进度 channel——这些无法跨进程编码，故永久留在进程内「by design」。

版本管理上，breaking change 以**新 interface 名**（`Events2`）而非重定义旧目录发布，peer 启动时交换 manifest 版本号，版本错配在启动即报双版本号而非运行期解码失败。这是工业级事件总线的成熟做法。

### 2. Agent 编队与性能画像（`src/bin/fleet.rs` + `bin/library_profile/scenarios/`）
`fleet.rs` 是 Agent 编队入口；`library_profile/scenarios/` 不是测试玩具，而是一套**生产级性能画像**：`agent_turn`（单轮）、`cold_phases`（冷启动各阶段耗时）、`long_agent`（长程）、`memory_ingest`（记忆摄入）、`subagent_storm`（子 Agent 风暴）、`workflow`（工作流）。它把「Agent 运行时该被当系统软件一样 profiling」这件事工程化，可借鉴到任何长程 Agent 产品的可观测性建设。

## 五、全网口碑

- **星标与热度**：37k ⭐，早期 beta（README 明标 "Early Beta, rough edges"），但发布一周内连续 9 天登 GitHub Trending 第一（Trendshift  badge 佐证），社区关注度高。
- **定位认知**：被社区视为「OpenClaw 一类的个人 AI 超级智能」但更强调 local-first 隐私与可编辑记忆；创作者 @senamakel。
- **客观短板（README 自承 + 社区常见质疑）**：① 仍是早期 beta，稳定性存疑；② GPL-3.0 + 部分能力走订阅（Exa 搜索/图像视频生成需订阅或 BYOK），「免费」边界需看清；③ 体量大（Rust core + 多前端 + 子仓），自托管门槛不低；④ "agent economy" 的 x402/USDC 赏金体系尚早。
- **数据来源**：来自仓库 README、Trendshift badge、发布说明；更细颗粒的 Reddit/HN 长帖口碑本次未逐条抓取，标注为「社区普遍认知」。

## 六、竞品对比 + 核心研判

| 维度 | OpenHuman | OpenClaw | MemOS / Letta | Claude Code memory |
|---|---|---|---|---|
| 记忆形态 | 明文 Markdown 树 + Obsidian 镜像 | 插件/上下文注入 | 记忆 OS（文本/激活/参数） | 会话内上下文 |
| 本地优先 | ✅ Privacy Mode 强制 | 部分 | ✅ | 否（云端） |
| Agent 编排 | 事件总线 + 编队 + 经济 | 插件生态 | 记忆调度 | 单 Agent loop |
| 连接面 | 100+ OAuth/5k MCP/90k Skills | 广 | 中 | MCP |
| 许可 | GPL-3.0 | 未明 | 各异 | 闭源分发 |

**核心研判**：
- ✅ **差异化清晰**：在「个人 AI 超级智能」赛道，OpenHuman 的「明文可编辑记忆 + 强制隐私 + 事件总线编队」组合与 OpenClaw 的「插件生态」、MemOS 的「记忆 OS」形成区隔，技术叙事完整。
- ⚠️ **风险**：早期 beta + GPL-3.0 + 订阅混合，生态与稳定性尚待验证；「9 天 Trending 第一」含发布期流量红利，需观察留存。
- 🔮 **趋势**：「可编辑明文记忆 + 知识图谱镜像」很可能成为下一代个人 Agent 记忆的标准范式，冲击纯向量 RAG 方案；其 `tinybus/tinyagents/tinyflows` 子仓下沉策略也值得 Agent 框架作者学习。
- 💡 **启发迁移**：做个人/企业 Agent 产品时，把记忆做成「人可读、可改、可审计的明文 + 图谱」，比黑箱向量库更能建立用户信任；事件总线双通道（序列化/原生）是解耦复杂 Agent 运行时的良方。

## 七、关键文件路径速查

| 路径 | 作用 |
|---|---|
| `src/core/bus.rs` | `tinybus::OnceBus<DomainEvent>` 全局事件总线（双调用面） |
| `src/core/agent_cli.rs` | Agent CLI 与编排入口 |
| `src/bin/fleet.rs` | Agent 编队主入口 |
| `src/bin/library_profile/scenarios/` | 生产级性能画像场景 |
| `src/api/mod.rs` / `rest.rs` / `socket.rs` / `jwt.rs` | REST + WebSocket + JWT API |
| `src/api/models/` | auth / socket / product 模型 |
| `Cargo.toml` | Rust workspace，依赖 tinybus/tinyagents 等子仓 |
| `.claude/agents/` | 内置 12+ 子 Agent 定义（build/dev/test/pr 等） |
