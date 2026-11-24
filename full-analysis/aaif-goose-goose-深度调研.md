# 🔬 aaif-goose/goose - 全方位深度调研

- GitHub：https://github.com/aaif-goose/goose
- 调研时间：2026-11-25
- 仓库规模：⭐ 56,934 / Rust / Apache-2.0 / 最近推送 2026-11-24 / 最新版本 v1.60.2（2026-11-20）
- 治理归属：Agentic AI Foundation（AAIF，Linux Foundation 旗下），前身由 Block 开源
- 调研口径：本文基于仓库源码（main 分支）+ 官方治理文档 + 第三方评测原文；不转述 README 口号当作结论

## 📌 一句话定位

goose 不是"又一个终端编码助手"，而是**把完整 Agent 运行时拆成可复用 Rust 组件（oi-kit）、再在其上交付一个可嵌入的成品 Agent（goose）**的双层项目：你自己搭 Agent 时用 oi-kit 的状态机/操作/工具/压缩/本地推理模块，直接用 Agent 时用桌面端、CLI 或 ACP 后端。

> 核心判断：它的差异化不在"能写代码"，而在**可组合性 + 模型中立 + 基金会治理**。如果你要造自己的 Agent 产品，值得读的是它的运行时设计；如果你只是想找个编码 Agent，它未必比 Claude Code / Codex 更省事。

## ✨ 项目亮点（先看这 5 条）

1. **运行时与产品分离**：`crates/oi-kit-*` 是可独立依赖的 Agent 构建块，`crates/goose/*` 只是用这些块拼出来的一个"参考实现"。这种分层在开源 Agent 里少见——多数项目把编排逻辑和 UI/CLI 焊死。
2. **状态机可重入、可持久化**：`StateMachine` 接受外部 `MachineSession`（提供 conversation 与 thinking_effort），步骤序列由调用方注入，中断时能把未完成工具调用补成错误响应，而不是把会话卡死。
3. **审批是一等 Operation**：`ToolApprovalOperation` 作为可选策略步骤插在工具执行前，未回答的确认会让整轮 yield（暂停），而不是靠提示词祈祷模型别乱调工具。
4. **模型层彻底解耦**：85+ 云厂商、本地 llama.cpp / MLX 进程内推理、Python/Kotlin 绑定，都不改变上层状态机协议。
5. **治理中立**：2026-04 从 Block 转入 Linux Foundation 的 AAIF，Apache-2.0，企业采购时不用面对单一供应商转向风险。

## 🏗️ 项目架构全景

### 1. 两层结构：oi-kit（运行时库） + goose（成品 Agent）

README 明确写：Both live in this repository。从 `crates/` 目录可直接看出这条边界：

- `crates/oi-kit-agent/`：状态机、Operation、工具审批、子 Agent、skills、slash command、MCP 容器；
- `crates/oi-kit-context-management/`：上下文压缩（summarize / compact 两层 API）；
- `crates/oi-kit-local-inference/`：进程内本地推理，后端为 llama.cpp 与 MLX；
- `crates/oi-kit-providers/`、`oi-kit-provider-types/`：模型供应商抽象与消息/用量类型；
- `crates/oi-kit-bindings/`：uniffi 绑定，覆盖 Python/Kotlin；
- `crates/goose/`：把上述组件装配成真正的 Agent，含 ACP server、extension manager、session runtime；
- `crates/goose-cli/`、`crates/goose-mcp/`、`crates/goose-acp-types/`：CLI、MCP 服务、ACP 扩展协议类型。

oi-kit 官方定位是 **alpha**，文档要求"版本与依赖对齐"——这不是营销话术，而是 API 仍在变动的真实信号。

### 2. 三种使用形态共享同一内核

| 形态 | 入口 | 特点 |
|---|---|---|
| 桌面端 | macOS/Linux/Windows 原生 App | 内置扩展浏览器、MCP Apps 渲染 |
| CLI | `curl ... download_cli.sh` 安装 | 适合脚本/CI，recipes 可版本化 |
| ACP 后端 | `goose acp` 作为子进程启动 | 你的应用发提示、收流式响应/工具活动/权限请求，界面与工作流由你拥有 |

关键：**goose Desktop 自己也是通过 ACP 跟后端通信的**。也就是说，"外部应用嵌入 goose"和"官方桌面端"走的是同一条协议路径，不是二等公民接口。

### 3. 扩展协议栈：MCP + ACP + 自定义 `_goose/*`

- MCP 负责"Agent 怎么拿工具"（70+ 扩展，数据库/浏览器/GitHub/Google Drive 等）；
- ACP 负责"客户端怎么驱动 Agent"（stdio 子进程，流式消息 + 权限请求）；
- `_goose/*` 是 goose 自有的 JSON-RPC 方法族，`crates/goose-acp-types/src/lib.rs` 的注释明确它是 these wire types 的 single source of truth，涵盖 custom notifications 与 custom requests。

## 🧠 核心源码解读（只挑架构关键点）

### ① 状态机：步骤是外部注入的，不是硬编码的循环

`crates/oi-kit-agent/src/machine.rs` 定义的 `Step` 只有两类：

```rust
pub enum Step<'a, S, E = ConversationEffect> {
    Operation(Arc<dyn Operation<S, E> + 'a>),
    Inference(Arc<dyn Inference<S, E> + 'a>),
}

pub struct StateMachine<'a, S, E = ConversationEffect> {
    steps: Vec<Step<'a, S, E>>,
    cancel: CancellationToken,
    interrupted_step: Mutex<Option<usize>>,
}
```

这带来三个工程后果：

- **可预览**：`collect_prompt_contributions()` 能在轮次之外聚合所有 operation 的工具与提示片段，`add_tools_to_inference_input()` 用 `HashSet` 拒绝重名工具（"multiple operations registered tool '{}'"），把工具冲突提前到装配期而不是运行期；
- **可中断**：`interrupted_tool_responses()` 遍历 `pending_tool_requests()`，为每个未完成请求补一条 `CallToolResult::error("Tool call was interrupted before completing")`，避免会话里留下永远等不到答复的工具调用；
- **宿主拥有存储**：`MachineSession` 只要求 `id()`、`conversation()`、`thinking_effort()`、`reported_context_tokens()`；`SessionLoader` 负责从你的持久化层恢复。这正是 README 所说的 "Your application owns the interface, policies, and storage" 在代码层的落点。

`crates/goose/src/agents/state_machine/mod.rs` 则把具体步骤列成一张"操作清单"：`ops_auto_effort`、`ops_context_relevance`、`ops_doctor`、`ops_llm`、`ops_recipe`、`ops_retry`、`ops_skills`、`ops_stop_hook`、`ops_subagent`、`ops_tool_pair_compaction`、`ops_thinking_recovery`……模块注释自称 "an ordered, re-entrant pipeline over persisted conversation state"。**读这份 mod.rs 比读 README 更能理解 goose 实际做了什么**：它的复杂度主要花在上下文治理与恢复，而非工具调用本身。

### ② 审批闸门：拒绝不是软提示，而是暂停整轮

`crates/oi-kit-agent/src/tool_approval.rs` 的策略枚举只有三种：

```rust
pub enum ApprovalDecision {
    Allow,
    Deny { reason: String },
    Ask { prompt: Option<String> },
}
```

`ToolApprovalOperation` 的注释写明它 "yields the turn while any of its confirmation requests are unanswered"；用户答复经 `apply_user_answer()` 转成 `Message::user().with_visibility(false, false)` 的隐藏消息，并用 `seen_message()` 写入 `operation_note(APPROVAL_OPERATION, SEEN, ids)` 做幂等标记。允许时匹配 `Permission::AllowOnce | AlwaysAllow`。

**借鉴点**：把"权限确认"建模成状态机里的一个 Operation + 会话里的不可见消息，比在 system prompt 里写"请先询问用户"可靠得多，而且天然支持跨进程恢复（确认请求可以落库，下一次启动时继续）。

### ③ 上下文压缩：阈值 0.8，Rust trait 与跨语言绑定分离

`crates/oi-kit-context-management/src/lib.rs`：

```rust
pub const DEFAULT_COMPACTION_THRESHOLD: f64 = 0.8;

pub trait CompactionInput {
    fn messages(&self) -> Vec<Message>;
    fn templates(&self) -> Templates { Templates::default() }
}
pub trait CompactionOutput {
    fn set_summary(&mut self, summary: Message);
    fn set_usage(&mut self, usage: ProviderUsage);
}
```

两层 API：`summarize()`（给模型+消息产出一条摘要消息）与 `compact()`（trait 化，调用方从自己的会话表示读写）。Python/Kotlin 通过 `oi-kit-bindings` 的 uniffi 包装暴露。结合 Issue #12968（"context: Allow per-model auto-compact token limit"）可以看出：**社区痛点正是"恒定比例阈值不适配不同模型的实际上下文预算"**，这是使用该库时最需要自定义的一处。

### ④ 本地推理：进程内模型槽位 + 双后端

`crates/oi-kit-local-inference/src/lib.rs` 的 `InferenceRuntime` 维护 `HashMap<ModelCacheKey, ModelSlotHandle>`，key 由 `(backend_id, model_id, chat_template)` 组成；`ModelSlotState` 为 `Empty / Loading / Loaded` 三态，配 `Notify` 等待加载完成，另有 `cold_load_lock` 防止并发冷加载。内置后端为 `LlamaCppBackend` 与 `MlxBackend`（Apple Silicon）。README 强调"无需 Ollama 或独立推理服务"——代码层证实：模型就是在 Agent 进程里加载的。

## 🎯 应用场景与启发

1. **要造自己的 Agent 产品，而不是套壳**：直接用 oi-kit 组合状态机+审批+压缩+存储，界面与策略自己写。goose Desktop 通过 ACP 驱动后端这件事，就是官方给出的"产品化模板"。
2. **企业内网 / 气隙环境**：AAIF 官方博客（air-gapped industrial environments）给出的路子是： Recipe 定义 CATIA→Patran 这类非编码工作流，把 MCP 扩展裁剪到只剩领域工具，甚至全部禁用只留推理核心，用小型开源模型跑。注意：博客自己也承认这是作者个人技术观点，且需要前期工程投入。
3. **CI 中跑可复现的 Agent 流程**：YAML recipes 可入库、可在 CLI 无头执行，适合依赖升级、周报、批量代码审查这类重复任务。
4. **对同类需求的解决思路**：如果你正在设计"可中断/可恢复的 Agent"，抄三件事就够——① 步骤序列外置；② 审批作为状态机节点而非提示词；③ 中断时把 hanging tool call 补成显式错误消息。这三点与具体模型、具体工具生态无关。

## 🌍 全网口碑（含真实原话与差评）

- **Vibecodes 评测**（https://vibecodes.net/apps/goose）给 **7.6/10**："MCP-first design with a built-in extension browser"；同时直说 "Less specialised for large refactors than coding-only agents"、"Quality depends heavily on the model you choose"。
- **ailab.mobi**（https://ailab.mobi/tool/goose） verdict 用词很强（"blazing-fast"、"unmatched MCP connectivity"），但缺点栏写清：配置复杂 MCP 网络需要 CLI 熟悉度；多子 Agent 并发在大仓库上 token 消耗高；MCP Apps 渲染只有桌面端有。
- **威多 AI 中文评测**（https://wedoingai.com/article/goose-review-2026）提醒：Autonomous 模式默认带文件删改权限，重要环境建议切 Manual/Smart，并配工具权限与沙箱；明确"缺少商业 SLA 与合规认证"。
- **Every AI Finder**（https://everyaifinder.com/tools/goose）核对过官方页面后标注"这不是实测"，但确认 2026-04-07 转入 AAIF、软件本体 Apache-2.0 免费、模型费用另计、无付费 goose 计划。
- **AAIF 官方博客**（http://aaif.io/blog/ai-agents-for-air-gapped-industrial-environments-why-goose）由航空航天工程师 Hoseong Lee 撰写，强调基金会治理对合规审查的价值；属于作者观点而非独立基准。
- **Issue 侧的真实痛点**：#11680（MCP OAuth 跨进程串行化）、#11551（reasoning 吃掉 output token 预算）、#11795（shell 捕获内存实时限流）、#12968（每模型自动压缩 token 上限）——都不是"功能缺失"，而是**长时间运行后的资源与状态治理问题**。

## ⚔️ 竞品对比

| 维度 | goose | Claude Code | Codex CLI | Gemini CLI | aider / opencode |
|---|---|---|---|---|---|
| 治理 | AAIF / Linux Foundation，厂商中立 | Anthropic 单一厂商 | OpenAI 单一厂商 | Google 单一厂商 | 社区 |
| 模型 | 85+ 供应商 + 进程内本地模型 | 主要 Anthropic | 主要 OpenAI | 主要 Google | BYOK，多供应商 |
| 扩展协议 | MCP 原生 + ACP 可嵌入 | MCP | MCP/AGENTS.md | MCP | 各异 |
| 运行时可复用 | **oi-kit 作为独立 Rust 库（alpha）** | 否 | 否 | 否 | 否 |
| 工作流固化 | YAML recipes，可入 CI | hooks/skills | AGENTS.md | extensions | 脚本为主 |
| 代价 | 学习曲线较陡、子 Agent token 高、无 SLA | 订阅绑定 | 额度绑定 | 生态绑定 | 形态更轻 |

**结论**：goose 的护城河是"运行时可复用 + 治理中立"，不是 IDE 交互体验。若团队诉求只是"给我一个能改代码的终端 Agent"，Claude Code/Codex 的默认值更省事；若诉求是"把 Agent 能力产品化并嵌入自有应用"，goose 的 ACP + oi-kit 组合几乎没有同量级对手。

## 🧭 核心研判

- **值得读，但要分清两层**：oi-kit 是有长期价值的架构样本；goose 产品层则处在高速迭代（v1.60.x 几乎每天一版），不要把它当稳定 API 依赖。
- **alpha 标注要当真**：README 明写 oi-kit is in alpha，Python/Kotlin 绑定只覆盖 provider/streaming/compaction 子集，Rust 才是完整运行时。
- **安全默认值需自行收紧**：审批 Operation 的存在不代表默认启用所有确认；结合第三方评测提到 Autonomous 模式的删改权限，生产使用应显式配置策略步骤 + 沙箱。
- **成本与质量随模型波动**：项目本身免费，成本完全取决于接入的模型；多子 Agent 并发时 token 放大是已知问题。
- **一句话**：把 goose 当"Agent 运行时的参考实现与零件库"来读，收益远大于把它当"另一个编码助手"来用。

## 📁 关键文件路径速查

| 路径 | 看什么 |
|---|---|
| `README.md` | 双层定位（oi-kit vs goose）、ACP 用法、治理归属 |
| `crates/oi-kit-agent/src/machine.rs` | `Step` / `StateMachine` / 中断补错误响应 / 工具重名检查 |
| `crates/oi-kit-agent/src/operation.rs` | Operation 协议与 `RunStatus` 语义 |
| `crates/oi-kit-agent/src/tool_approval.rs` | `ApprovalDecision` 三态与 yield 语义 |
| `crates/oi-kit-context-management/src/lib.rs` | 压缩阈值 0.8、CompactionInput/Output trait |
| `crates/oi-kit-local-inference/src/lib.rs` | 模型槽位状态机、llama.cpp/MLX 双后端 |
| `crates/goose/src/agents/state_machine/mod.rs` | goose 实际装配的 operation 清单 |
| `crates/goose/src/acp/server/` | ACP 会话、工具、权限请求的服务端实现 |
| `crates/goose-acp-types/src/lib.rs` | `_goose/*` 自有 JSON-RPC 类型单一真源 |
| `GOVERNANCE.md` / `AGENTS.md` | AAIF 治理与贡献规约 |
