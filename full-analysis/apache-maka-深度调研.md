# apache/maka 深度调研

> 调研日期：2026-08-26 ｜ 星标：3,254 ⭐ ｜ 语言：TypeScript ｜ 协议：Apache-2.0 ｜ 默认分支：main
> 定位：Apache 软件基金会孵化中的「本地优先 AI Agent 工作区」，用只追加日志（event sourcing）记录 Agent 执行的每一条事实

## 一、项目亮点（差异化）

1. **事件溯源（Event Sourcing）作为一等公民**：模型消息、工具调用、工具结果、权限决策、结束事件全部写成「可恢复的仅追加执行事实（append-only log）」，UI 和下一次模型调用只是这份记录的视图，而非唯一副本。
2. **单一执行权威 Runtime Host**：Desktop / TUI / CLI / Bot / Eval 全部只向 Runtime Host 请求执行，不存在第二个 Runtime —— 治理边界清晰，避免多入口状态分裂。
3. **「缩短上下文 ≠ 删除历史」**：压缩（compaction）只从下一次 provider 输入投影里省略旧工具输出，但**不丢弃已保存的证据**，支持崩溃恢复与中断回合续跑。
4. **Eval 原生内置**：`maka eval` 把基准实验建模为「Experiment → Cell(task×repetition×subject) → Attempt → Result」，且最早有效 attempt 为权威，操作方不能挑结果 —— 面向可复现评测。
5. **ASF 中立治理 + 本地优先**：Apache 孵化，vendor-neutral，会话/设置/运行记录默认留在本地，模型自带（云端 API / 本地模型 / 兼容网关皆可）。

## 二、核心架构

来自 `ARCHITECTURE.md` 的权威分层（Mermaid 原文提炼）：

```
Client(Desktop/TUI/CLI/Bot) → Runtime Host(唯一执行权威)
  → SessionManager → AgentRun + RuntimeKernel
      → Tool Runtime（沙箱边界内执行工具）
      → Runtime Event Log（模型消息/工具调用/结果/终止事实 的规范源）
  → Agent Graph Control Plane（用子 Session 调度依赖工作，每次激活都回 Runtime）
  → Context / Session / UI / Recovery projections（投影）
@maka/eval(Experiment→Cell→Attempt→Result) 也只穿过 Runtime Host 公共边界
```

**关键分层约束**：
- Runtime Event Log 是规范源；context pruning / compaction 改变的是「provider 输入投影」，不是历史本身。
- Storage 只拥有交互式 Runtime 状态，**没有** Eval 专属根、TaskRun 账本或实验结果权威。
- Eval 边界清晰：`repetition`=新实验样本，`infra retry`=同 cell 的替换 attempt，`continuation`=Maka subject 内部 Runtime Host 行为。

**代码边界（packages）**：

| 包 | 职责 |
|----|------|
| `packages/core` | 纯 Session / Runtime Event / AgentRun / 权限 / 协议契约 |
| `packages/storage` | 交互式 Runtime 存储 + SQLite 控制面 |
| `packages/runtime` | SessionManager、AgentRun、模型适配器、工具、上下文、恢复、Graph 调和 |
| `packages/runtime-host` | 唯一托管执行权威 + 公共客户端/协议 |
| `packages/eval` | 实验 cell、attempt、结果选择、subject/executor 适配器 |
| `packages/cli` | TUI、`maka run`、公共 `maka eval` 路由 |
| `apps/desktop/src/main` | Electron 组合 + 产品入口适配器 |

外加 `packages/computer-use`、`packages/mcp`、`packages/ui`。

## 三、应用场景与启发

- **企业/团队本地优先 Agent 运行时**：对「不能用单一厂商闭源 CLI」的组织，Maka 提供 ASF 背书的中立替代，且数据默认本地。
- **可审计 / 可复现的 Agent 执行**：事件溯源使每一次工具调用都可回放、可恢复，天然适配合规与评测场景。
- **Agent 评测基础设施**：内置 eval 把「跑基准」变成声明式实验，避免各团队自造轮子。
- **对同类需求的启发**：任何长期运行的 Agent 系统都应把「执行事实」与「上下文窗口」解耦 —— 用 append-only log 当规范源，compaction 只动投影，这比「把历史塞进 prompt」更稳健，也更易做崩溃恢复与多端同步。

## 四、源码深度解读

**1. 事件溯源规范源（`packages/core` 契约 + `packages/storage` 的 SQLite 控制面）**
Runtime Event Log 是 canonical source。以下伪代码体现「投影与历史分离」的设计哲学：

```text
// 设计要点（非逐行源码）
EventLog.append(turnEvent)        // 工具调用/结果/权限决策 只追加
ContextProjection.build(log)      // 下一次给 LLM 的 prompt = 对 log 的投影
ContextProjection.rebuild()       // compaction 只重投影，不删 log
Recovery.replay(log)              // 崩溃后从 log 重放恢复
```

**2. Agent Graph 调度（`packages/runtime` 的 Graph reconciliation）**
依赖工作用 child Sessions 表达，每次激活都回同一个 Runtime，保证「多 Agent 编排」也走唯一执行权威，不另起炉灶。

**3. Eval 结果内核（`packages/eval`）**
结果内核只含 `score / normalized usage / attributable cost / duration / status|failure_reason / artifacts`；cell 多 attempt 时**最早有效 attempt 为权威**，从协议层杜绝「挑好看的结果」。

## 五、社区口碑

- Apache 孵化身份带来较高初始信任度；`AGENTS.md` / `CLAUDE.md` 同仓存在，说明团队在用 Agent 自身 dogfooding 开发。
- ⚠️ 仍处 active development：macOS Apple Silicon 桌面为早期公测，Windows 为未签名预览，Linux 尚未支持；数据格式 / CLI 命令 / 实验能力仍可能变。
- 作为「ASF 孵化的 Agent 运行时」叙事清晰，但生态与插件成熟度远不及 Claude Code / OpenCode。

## 六、竞品对比与核心研判

| 维度 | apache/maka | Claude Code | OpenCode | Goose(Block) | Aider |
|------|------------|-------------|----------|--------------|-------|
| 治理 | ASF 中立孵化 | 厂商闭源 | 社区开源 | 厂商开源 | 社区开源 |
| 执行记录 | 事件溯源 append-only | 会话态 | 会话态 | 会话态 | 会话态 |
| 本地优先 | ✅ 默认 | 部分 | ✅ | ✅ | ✅ |
| 内置评测 | ✅ eval 原生 | ❌ | ❌ | ❌ | ❌ |
| 多端 | Desktop+TUI+CLI+Eval | CLI | CLI+TUI | CLI | CLI |

**核心研判**：
- ✅ **差异化真实且硬核**：事件溯源 + 单一 Runtime 权威 + eval 原生，是面向「组织级、可审计、可复现」Agent 运行的稀缺设计，不同于把历史塞进 prompt 的主流方案。
- ⚠️ **风险**：孵化期（ASF 未背书完成）、平台覆盖不全（Linux 缺位）、生态早期；与 Claude Code 的插件/MCP 丰富度差距大。
- 🔭 **值得持续观察**：若顺利从 ASF 孵化毕业并补齐 Linux/Windows + 插件生态，有潜力成为「不被单一厂商绑定的企业级 Agent 运行时标准」。当前适合技术前瞻者与评测驱动团队试用。

## 七、关键文件速查

| 文件 | 作用 |
|------|------|
| `ARCHITECTURE.md` / `ARCHITECTURE.zh-CN.md` | 后端架构权威文档（分层、Eval 边界、代码边界） |
| `DESIGN.md` | 设计原则 |
| `packages/core` | Session / Runtime Event / AgentRun / 权限 / 协议契约 |
| `packages/runtime` | SessionManager、AgentRun、工具、上下文、恢复、Graph 调和 |
| `packages/runtime-host` | 唯一托管执行权威 |
| `packages/eval` | 实验 cell/attempt/结果选择 |
| `apps/desktop` | Electron + React 桌面端 |
| `skills/` + `AGENTS.md` / `CLAUDE.md` | 团队用 Agent 自身 dogfooding 开发 |
