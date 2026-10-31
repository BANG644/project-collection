# Orkas-AI/Orkas 深度调研

> 索引编号：#552 ｜ 调研日期：2026-11-01 ｜ 报告类型：GitHub 仓库深度调研

## 一、项目定位（一句话）

一个**开源（MIT）、本地优先**的多 Agent 桌面应用：一个 "Commander" 把你的目标拆成待办、协调 16 个内置专家 Agent，并把你本机已装的 Claude Code、Codex、OpenCode、OpenClaw、Hermes-Agent 也拉进同一支团队一起干活。

- **仓库**：https://github.com/Orkas-AI/Orkas
- **协议**：MIT
- **语言**：JavaScript / TypeScript（Electron 桌面壳 + 独立 `core-agent` 运行时）
- **数据**：⭐ 6,034 ｜ Fork 365 ｜ Open Issues 7 ｜ Releases 21（最新 v2026.10.27）｜ 贡献者 12 ｜ 创建 2026-04-29 ｜ 末次推送 2026-10-31

## 二、项目亮点（差异化）

1. **"不是二选一，而是组队"**：Orkas 把 Claude Code、Codex 当作自己的成员 Agent 来调度，而不是与之竞争——一次对话里修 bug、审改动、写发布说明可分给不同成员。
2. **Commander 三件套调度原语**：`dispatch_to`（等结果或异步）、`hand_off_to`（移交剩余工作并结束本轮）、`run_worker`（匿名隔离子任务，无历史）清晰区分"协作 / 移交 / 沙箱"。
3. **纯算术的上下文预算**：`context-budget.ts` 把"何时压缩上下文"做成**确定性数学**，不靠 LLM 判断——按模型可用输入窗口推导压缩阈值，留下 1/6 增长余量。
4. **本地优先 + 设备端向量库**：对话/文件/密钥默认在本地磁盘；Library 用本机 embedding 建 SQLite 向量索引，可检索并引用原文段落。
5. **Agent 自进化**：后台反思编排器在空闲时审视新活动，更新各 Agent 的 `COMPETENCE.md` / `LEARNING_STRATEGIES.md`，且"无值得保存则不动笔"。

## 三、核心架构

```
src/
  main/                       # Electron 主进程 + 桌面功能
    features/
      group_chat/            # bus.ts(MessageBus) / router.ts / plan_executor.ts
                              #   / dispatch_planner.ts / task_board.ts / state.ts
      memory.ts               # 跨会话作用域记忆（MEMORY/USER/AGENT/PROJECT）
      connectors/             # Gmail/Calendar/Sheets/Drive/Notion/Slack/Shopify/Stripe...
      auto_tasks.ts           # 定时自动化（时/日/周/月）
    util/
      file_to_chunks.ts       # 文档切片 → 向量索引
      conversation-cost-meter.ts
      crypto-vault.ts         # 本地加密密钥
  core-agent/                 # 模型无关的 Agent 运行时（可被复用）
    src/agent/
      context-budget.ts       # 纯算术上下文压缩预算
      runner.ts               # Agent 运行时主循环
      session.ts              # 会话历史与检查点
      workspace-state.ts      # 工作区状态记录（可跨压缩存活）
      evolution/metacognition.ts  # 反思/学习提示词
```

**任务路由（Commander）**：Commander 自己处理通用工作，专业工作经三件套下派；命名 Agent 任务与匿名 worker 各有独立并发控制（`bus.ts` 的 `ConversationScheduler` 负责准入：同 Actor 串行、会话 Agent 上限、命名任务门禁）。路由只认 `router.resolveRecipients` 解析出的 `to[]`；`to[]` 含 `user` 的消息写入 group jsonl 并发给监听者，但**永不入队**（人是人类，UI 才是唯一消费者）。

**上下文管理**：运行时按所选模型的可用输入容量做预算，计入 prompt/工具/常驻状态；已完成对话用有界近期窗口，长任务用检查点压缩早期过程消息同时保留近期工作；文件读写/命令执行均有可跨压缩存活的结构化记录。

**记忆与 Library**：持久笔记分 `memory`（共享事实）/ `user`（用户画像）/ `agent`（每 Agent 领域笔记）/ `project`（本项目事实）四个作用域，用 `§` 分隔条目，冻结进系统提示；Library 把文档切段存入本地 SQLite 向量索引，embedding 在设备端跑。

**外部 CLI Agent**：Claude Code / Codex / OpenCode（编码）+ OpenClaw / Hermes-Agent（个人）作为本地子进程拉起，Commander 保持统一计划横跨它们。

## 四、应用场景与启发（重点）

- **"桌面编排层"模式可复制**：Orkas 的核心洞察是**不要重写编码 Agent，而是给它们套一层会派活的 Commander**。任何想"把多个现成 Agent 编成团队"的产品，都可直接借鉴 `dispatch_to / hand_off_to / run_worker` 三件套 + 统一计划 + 各自并发上限的设计，省去从零造轮子。
- **上下文预算的工程化**：`context-budget.ts` 把上下文压缩做成**纯函数**（`room = ceiling - overhead - resident`，分层 60/40，小窗口降级到应急层），意味着你能在任何长程 Agent 运行时里复用这套"确定性压缩时机"算法，而不依赖模型自我判断——对稳定、可预测的多轮 Agent 系统价值很大。
- **本地优先 + 设备端向量库**：密钥本地加密、Library 本机 embedding、可选云同步——是兼顾隐私与能力的成熟范式，适合任何"不想把数据送出本机"的 Agent 产品。
- **给你的项目参考**：若你的"错题归因"想做成多 Agent（检索/定位/归因/复核分角色），Orkas 的"Commander 统一计划 + 成员 Agent 独立并发 + 作用域记忆 + 自进化"链路，是比 CCGS 更偏"运行时编排"的另一极参照；尤其 `run_worker` 的隔离子任务思路，正适合"归因一个独立搜索空间"这类互不污染的子任务。

## 五、源码解读（核心模块）

### 1. `src/main/features/group_chat/bus.ts`（552KB 的调度核心，节选头部）

```ts
/**
 * MessageBus — group chat 的 actor/消息传递核心。每进程一个 bus 实例。
 * 每 cid 状态：queue（顶层回合有序待办）、executions（每 running 回合一个
 *   WorkerState，按 turnId 索引）、listeners（该会话的 IPC 流订阅者）。
 * 准入由 ConversationScheduler 决定：按列表序扫描，凡通过确定性规则（同 Actor
 *   串行、会话 Agent 上限、命名任务门禁）的项都启动。Commander 执行不占上限也不占
 *   门禁。dispatch fan-out 与有界内部 review 在回合内进程内发生，对调度器不可见。
 */
import { yieldReflectionForTask } from '../reflection-coordination';
// ... 大量 router / state / taskBoard / dispatch_planner 的导入
```

> 注：该文件达 **552KB**，是 dispatch/router/plan-executor 的超富集实现，节选仅展示其 actor 模型与准入语义；实际调度逻辑极重，建议按需深读 `router.ts` / `plan_executor.ts` / `dispatch_planner.ts`。

### 2. `src/core-agent/src/agent/context-budget.ts`（纯算术压缩）

```ts
export const TOOL_RESULT_RESERVE_FLOOR_TOKENS = 16_000;
export const CONTEXT_COMPACTION_SUMMARY_PREFERRED_MAX_TOKENS = 1_200;
const ACTIVE_TRIGGER_SHARE_OF_REST = 0.6;   // 活跃进程占 60%
const HISTORY_ROOM_SHARE_OF_REST   = 0.4;   // 历史占 40%，未用部分可借给活跃层
const INLINE_ROOM_SHARE = 1 / 6;            // 留 1/6 作增长余量
export const MAX_ACTIVE_CHECKPOINT_INPUT_TOKENS = 150_000;

function deriveContextBudget(room, usable, residentState, historyOccupancy?) {
  const windowTooSmall = room < MIN_LAYERED_ROOM_TOKENS;
  const rest = Math.max(0, room - toolResultReserveTokens);
  const activeShare = Math.round(rest * ACTIVE_TRIGGER_SHARE_OF_REST);
  const historyRoom = windowTooSmall ? usable : Math.round(rest * HISTORY_ROOM_SHARE_OF_REST);
  // 历史层未用空间借给活跃回合；窗口过小则整体降级到应急层
  const activeBorrowedTokens = windowTooSmall || occupancy===undefined ? 0
                             : Math.max(0, historyRoom - occupancy);
  ...
}
```

**看点**：压缩时机与阈值完全由窗口算术推导，且对"小窗口"有降级路径（停掉分层、只跑应急层），避免抖动式反复压缩——这是长程 Agent 稳定运行的关键工程细节。

### 3. `src/main/features/memory.ts`（作用域记忆 + 注入扫描）

```ts
export const MEMORY_CHAR_LIMIT = 2500;   // 共享事实（跨项目跨 Agent）
export const USER_CHAR_LIMIT   = 1500;   // 用户画像
export const AGENT_CHAR_LIMIT  = 2000;   // 每 Agent 领域笔记
export const MEMORY_ENTRY_LIMIT = 16;    // 既限字符也限条目数
const INJECTION_PATTERNS = [
  { re: /ignore\s+(all\s+)?previous\s+instructions/i, label: 'prompt-injection' },
  { re: /you\s+are\s+now\s+/i, label: 'prompt-injection' },
  { re: /(curl|wget)\s+.*\b(api[_-]?key|bearer|token|secret)\b/i, label: 'exfiltration' },
  { re: /[\u202A-\u202E]/, label: 'invisible-unicode' },  // bidi 控制符
];
// 写入永不驱逐；store 满则拒绝增长，直到调用方自行合并
```

**看点**：记忆写入带**注入扫描**（prompt injection / 密钥外泄 / 隐形 unicode），且"写满就拒、不驱逐"的保守策略避免了自动遗忘导致的上下文丢失——是 Agent 持久记忆的安全基线实现。

## 六、全网口碑

- **GitHub Trending 当日上榜**，21 个 release、12 位贡献者、仅 7 个 open issue，迭代节奏健康活跃（末次推送即为 10-31，当日）。
- README 极其完整，自带与 Claude Code / Codex / CrewAI / LangChain / OpenClaw / Hermes-Agent 的逐项对比表，定位清晰不浮夸。
- 打包版含 500 内置积分 + 付费云同步/共享项目；**源码构建无账号层**，开机即进应用——开源纯度高。
- 第三方长文评测「数据不可用」（新近项目）；口碑信号主要来自 Trending 排名与社区 issue/PR 活跃度。

## 七、竞品对比 + 核心研判

| 工具 | 形态 | Orkas 差异点 |
|------|------|------|
| Claude Code / Codex | 编码 Agent（终端/IDE） | Orkas 把它们当成员，外面包一层模型无关团队 |
| CrewAI / LangChain | 代码优先的编排框架 | Orkas 是聊天驱动桌面应用，数据默认本地 |
| OpenClaw / Hermes-Agent | 个人 Agent 平台/单 Agent | Orkas 提供桌面工作区 + 内置专家 + 跨 CLI Agent 协调 |

**核心研判**：
- ✅ **强项**：本地优先 + 多模型任意切换 + 把现有编码 Agent 编队而非重写，产品思路务实；上下文预算与作用域记忆的工程实现可直接借鉴；自进化机制让 Agent "越用越懂你"。
- ⚠️ **风险**：核心 `bus.ts` 高达 552KB，调度逻辑高度耦合、学习曲线陡；重度依赖 Electron + 原生模块（whisper.cpp / sqlite-vec / sharp），Linux 仅源码运行、musl 不支持；打包版部分能力（共享项目/云同步/发布）需付费，与"开源即全功能"预期有落差。
- 🎯 **结论**：它是**"桌面 Agent 操作系统"方向的代表选手**——值得精读其调度原语与上下文/记忆工程，作为你多 Agent 系统的架构参照；但若只想嵌入代码库当库用，它偏"应用"而非"框架"，需注意定位错配。

## 关键文件速查

| 文件 | 作用 |
|------|------|
| `src/main/features/group_chat/bus.ts` | MessageBus 调度核心（actor 模型 + 准入） |
| `src/main/features/group_chat/router.ts` | `resolveRecipients` 路由解析 |
| `src/main/features/group_chat/plan_executor.ts` | 计划执行器 |
| `src/main/features/group_chat/dispatch_planner.ts` | 派活计划（planUserDispatch / buildAssignmentContext） |
| `src/core-agent/src/agent/context-budget.ts` | 纯算术上下文压缩预算 |
| `src/core-agent/src/agent/runner.ts` | Agent 运行时主循环 |
| `src/main/features/memory.ts` | 跨会话作用域记忆 + 注入扫描 |
| `src/main/util/file_to_chunks.ts` | 文档切片 → 向量索引 |
| `src/main/features/reflection-orchestrator.ts` | 后台反思/学习编排 |
| `src/core-agent/src/evolution/metacognition.ts` | 反思提示词 |
| `README.md` | 含与 6 个竞品的逐项对比表 |
