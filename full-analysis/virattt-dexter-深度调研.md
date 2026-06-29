# Dexter (virattt/dexter) 深度调研报告

> 调研日期：2026-06-30 | Stars: 27,241 | Forks: 3,375 | 主语言：TypeScript (Bun) | 许可证：MIT

---

## 1. 一句话定位

**"Think Claude Code but built specifically for financial research"**——把 Claude Code 的自主 Agent 工作范式完整迁移到金融研究领域的开源工具，让 AI 像资深分析师一样自主规划、执行、验证复杂金融查询。

---

## 2. 项目亮点（5条）

### 2.1 精准垂直的定位切割

Dexter 不试图做"通用的 AI 助手"，而是锁定了一个极其明确的痛点：**金融基本面研究的数据收集与分析自动化**。它将 Claude Code 的"规划-执行-验证"循环 + 终端交互体验，完整嫁接到 SEC 文件、财务报表、市场数据场景中。这种定位让它从三个月前（2026-03）的寥寥数百星飙升至今日的 27k+，说明垂直切口选准了。

### 2.2 工程化程度远超同类演示项目

这不是一个 README 项目。它拥有：
- **完整的评估套件**（LLM-as-judge + LangSmith 追踪）
- **全链路调试系统**（JSONL scratchpad 记录每次工具调用的参数、原始结果和 LLM 推理）
- **生产级错误处理**（上下文溢出恢复、指数退避重试、循环检测）
- **多通道部署**（CLI + WhatsApp 网关 + cron 定时任务）

许多 20k+ stars 的项目仍停留在演示阶段，Dexter 的工程成熟度在同量级项目中非常少见。

### 2.3 WhatsApp 原生集成——"你的口袋里住了一位分析师"

将 Agent 接入 WhatsApp 的意义远大于"加个聊天界面"：
- 零安装成本——每个智能手机都有 WhatsApp
- 通过"自我聊天"模式实现个人收件箱式交互
- 支持消息队列——Agent 工作时你可以继续发送消息，队列自动排空
- 完整的访问控制（配对码、白名单、群聊策略）

这个设计让金融研究从"坐在电脑前操作"变成了"随时随地发条消息就能触发分析"。

### 2.4 新颖的"Cron for Agents"定时任务系统

Dexter 内置了一个 cron 定时任务系统，允许用户配置定时触发的 Agent 查询。这个设计的关键创新点在于：

- **抑制机制**：如果 Agent 返回"一切正常"的监控信息，系统自动抑制不发送，只有真正需要关注的情况才推送通知
- **饱和检测**：相同的消息内容在指定时间内不会重复发送（防止监控疲劳）
- **活跃时段控制**：可设置在交易时间内才运行
- **一次性 / 持续 / 询问 三种履行模式**

这是"AI Agent 作为后台服务"的一个很有启发性的实践。

### 2.5 极致的上下文管理策略

Dexter 的上下文管理机制是多层级的防守体系，远不止"超了就 truncate"：

```
微压缩 (microcompact) → 上下文溢出重试 → 内存持久化 → 压缩 (compaction) → 截断
```

每一层都设计了保护机制（如 MAX_CONSECUTIVE_COMPACTION_FAILURES），避免单一策略失效时系统崩溃。配合 scratchpad 的"无损审计日志 + 有损上下文摘要"策略，做到了可审计性与 token 效率的平衡。

---

## 3. 项目架构全景

### 3.1 整体架构图

```
┌─────────────────────────────────────────────────────────────┐
│                      用户交互层                              │
│  CLI (Ink/React) │ WhatsApp │ Cron ── 多通道接入            │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                      网关层 (Gateway)                        │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │ 访问控制     │  │ Session管理  │  │ Heartbeat/抑制   │   │
│  │ (配对/白名单)│  │ (内存会话)   │  │ (消息去重)       │   │
│  └─────────────┘  └──────────────┘  └──────────────────┘   │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                    Agent 核心层                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Agent 主循环 (agent.ts)                  │   │
│  │  规划 → 执行工具 → 收集结果 → 反思 → 迭代(max=10)   │   │
│  └──────────────┬───────────────────────────────────────┘   │
│                  │                                           │
│   ┌──────────────┼──────────────┐                           │
│   ▼              ▼              ▼                           │
│ ┌──────┐   ┌──────────┐   ┌──────────┐                     │
│ │工具执行│   │ 提示词构建 │   │上下文管理 │                     │
│ │Executor│   │ Prompts  │   │(5层防线) │                     │
│ └──────┘   └──────────┘   └──────────┘                     │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────┐    │
│  │ Scratchpad   │  │ Memory系统   │  │ Token计数器    │    │
│  │ (JSONL日志)  │  │ (SQLite持久) │  │ (预估+实际)    │    │
│  └──────────────┘  └──────────────┘  └────────────────┘    │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                      工具层                                   │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐   │
│  │金融数据   │ │SEC文件   │ │网络搜索   │ │浏览器       │   │
│  │(Dataset) │ │(Filing)  │ │(Exa/Tavily)││(Playwright) │   │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────┘   │
│  ┌──────────┐ ┌──────────┐ ┌────────────────────────────┐   │
│  │财务指标   │ │内部交易   │ │Skill系统(可扩展工作流)    │   │
│  └──────────┘ └──────────┘ └────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 多Agent架构辨析

**重要澄清**：Dexter 本质上是**单Agent架构**，并非真正的多Agent系统。社区评测和部分中文文章将其描述为"多Agent架构"存在误读。

Dexter 的实际架构是：

| 角色 | 实现方式 | 说明 |
|------|---------|------|
| **规划器** | System Prompt 中编码的指令 | 模型在单轮推理中自主分解任务，没有独立的规划 Agent |
| **执行器** | Agent 主循环 + 工具调用 | 在 `agent.ts` 的 while 循环中迭代调用工具 |
| **验证器** | System Prompt 中的反思指令 | 同样依赖 Prompt 引导模型自我验证，没有独立的验证 Agent |
| **记忆** | Scratchpad + MemoryManager | JSONL 日志 + SQLite 持久化记忆 |

这是一个关键的设计取舍：**通过精心设计的 Prompt + 单 Agent 循环来模拟多角色协作**，避免了多 Agent 间的通信开销和协调复杂度。代价是缺乏真正的角色辩论（如 ai-hedge-fund 的多角色辩论）和并行规划能力。

### 3.3 网关系统

Gateway 模块是 Dexter 最成熟的工程模块之一：

**`gateway/access-control.ts`** 实现了完整的入站访问控制策略矩阵：
- `dmPolicy`: `pairing` / `allowlist` / `open` / `disabled` 四种策略
- `groupPolicy`: `open` / `allowlist` / `disabled`
- 支持通配符 `*`、E164 号码标准化、配对码验证
- fail-closed 设计：配置缺失或异常时默认拒绝

**`gateway/agent-runner.ts`** 实现了会话管理：
- 内存级 Session 存储（keyed by sessionKey）
- 串行化的会话处理（`session.tail = session.tail.then(run, run)`）
- 消息队列支持：Agent 工作时用户可继续发送消息
- 隔离会话模式：Cron 任务使用的无状态模式

**`gateway/channels/whatsapp/`** 实现了完整的 WhatsApp 集成：
- 基于 WhatsApp Web 协议（通过 whatsapp-web.js）
- 心跳检测 + 看门狗定时器
- 自动重连（指数退避）
- 消息超时机制（30分钟无消息自动关闭）

### 3.4 Cron 系统

Cron 系统在 `src/cron/` 下，设计亮点：

**定时调度（`schedule.ts`）**
- 支持 `interval`（分钟级定期间隔）和 `at`（一次性定时）两种模式
- 预计算 nextRunAtMs，最大定时器间隔 60s

**任务执行（`executor.ts`）**
- 每个 cron job 运行一个隔离的 Agent 实例
- 任务完成后评估抑制条件（消息去重、饱和检测、活跃时段）
- 结果通过 WhatsApp 推送
- 错误处理：指数退避（30s → 1min → 5min → 15min → 60min）

**三个核心设计决策值得学习：**

1. **不在 cron 内部做"调度器"**——使用最简的 setTimeout 实现，不引入外部依赖
2. **文件系统作为持久化层**——jobs.json 存储所有任务状态，每次 tick 重新 load
3. **错误不阻塞整体**——出错的 job 只影响自身，不影响其他 job 的执行

### 3.5 评估系统

`src/evals/` 是 Dexter 展示工程严谨性的重要模块：

- 数据集：`dataset/finance_agent.csv`（金融问答数据集）
- 评分方案：LLM-as-judge（使用 fast 模型评分）
- 追踪：LangSmith 链路追踪
- UI：Ink 实时 UI（进度、准确率统计）
- 采样运行：通过 `--sample N` 做快速验证

这让 Dexter 和仅靠直觉开发的 Agent 项目区分开来——它有量化的质量门禁。

---

## 4. 应用场景与启发

### 4.1 金融研究场景

**场景一：基本面筛选与监控**
> "找出标普500中连续3年研发投入占比超过15%的公司"

传统做法：需要访问 SEC EDGAR、解析 10-K 文件、提取 R&D 支出、计算比例 → 动辄数天。
Dexter 做法：一条命令，几分钟内得到初步列表（准确度取决于 Financial Datasets API 的数据覆盖）。

**场景二：财报季批量解读**
> "分析苹果、微软、谷歌三家最新季报的收入、利润和现金流趋势"

Dexter 可以并行调用多个工具（并发执行允许 read-only 工具同时运行），大幅缩短财报季的批量处理时间。

**场景三：竞品持续监控（Cron 系统最佳匹配）**
配置一个每交易日下午4点运行的 cron job：
> "检查特斯拉本周的做空比例变化和重大新闻"

当抑制机制发现"没有变化"时，你不会被打扰；只有当真正有值得关注的事件时，才会通过 WhatsApp 收到通知。

### 4.2 对 Agent 设计的核心启发

**启发一：垂直 Agent 的正确打开方式**

Dexter 证明了"一个工具 + 一个好 Prompt + 一个垂直场景"可以产生巨大的价值。它没有使用复杂的 multi-agent 编排、没有向量数据库、没有 RAG，而是聚焦于把金融研究的端到端流程自动化。

**垂直 Agent 的成功公式 ≈ 清晰的问题边界 × 高质量的数据工具 × 可控的执行循环**

**启发二：上下文管理是 Agent 的"操作系统"**

Dexter 的上下文管理策略可以提炼为一条通用原则：**先无损记录，再有损压缩**。

- Scratchpad 负责"无损记录"（完整的 JSONL 审计日志）
- Compaction 负责"有损压缩"（LLM 总结历史工具结果）
- Microcompact 负责"日常清理"（每轮循环前轻量级修剪）

这种分层策略让 Debug 成为可能（无损日志），同时让长链推理可持续（有损压缩）。

**启发三：Agent 也应该有 CI/CD**

Dexter 的 eval 套件为 Agent 开发提供了"测试驱动开发"的可能性。当你修改 Prompt、调整工具或更换模型时，可以运行 eval 来量化影响。这对 Agent 的可维护性是革命性的——Agent 的"回归测试"。

**启发四：消息队列模式解决"慢 Agent"的用户体验问题**

`drainQueue()` 的设计：用户在 Agent 工作时可以继续发送消息，Agent 会在下一轮迭代前排空队列并处理新消息。这种"非阻塞交互"模式解决了 AI Agent 响应慢（通常需要 10-60 秒）带来的用户等待焦虑。

### 4.3 跨领域迁移可能性

Dexter 的架构可以干净地迁移到其他垂直研究领域，只需要替换工具层：

| 领域 | 数据工具替代 | 对应 API |
|------|-------------|---------|
| 法律研究 | 法规检索、案例库 | CourtListener API, 裁判文书网 |
| 生物医药 | 论文检索、临床试验数据 | PubMed API, ClinicalTrials.gov |
| 竞争情报 | 专利检索、产品信息 | Google Patents, Crunchbase |
| 宏观研究 | 经济指标、央行数据 | FRED API, World Bank API |
| 链上数据 | 区块链分析 | Dune Analytics, The Graph |

核心 Agent 层（agent.ts、compact.ts、scratchpad.ts、tool-executor.ts）无需任何修改。

---

## 5. 核心源码解读

### 5.1 agent.ts：Agent 主循环

**位置**: `src/agent/agent.ts`（~700 行）

Agent 主循环是一个 `async generator`（`async *run()`），逐轮发射事件。关键设计：

```typescript
// 核心循环骨架
while (ctx.iteration < this.maxIterations) {
  // 1. 微压缩：每轮循环前轻量级修剪
  const mcResult = microcompactMessages(messages);

  // 2. 剥离旧推理文本（保留最近2轮的工具调用结构）
  this.stripOldThinking(messages, 2);

  // 3. 调用LLM（优先流式，失败回退阻塞）
  const result = yield* this.callModelWithStreaming(messages);

  // 4. 判断：没有工具调用 → 直接回答
  if (!hasToolCalls(response)) {
    yield* this.handleDirectResponse(responseText, ctx);
    return;
  }

  // 5. 有工具调用 → 执行（支持并发），收集结果
  let { toolMessages, denied } = yield* this.executeToolsAndCollectMessages(response, ctx);

  // 6. 结果后处理：大结果持久化、预算控制
  toolMessages = toolMessages.map(capLargeResults);
  toolMessages = enforceResultBudget(toolMessages);

  // 7. 上下文阈值管理（记忆持久化 → 压缩 → 截断）
  yield* this.manageContextThreshold(ctx, query, memoryFlushState, messageState);

  // 8. 排干消息队列（用户可能在Agent工作时发送了新消息）
  const drainResult = this.drainQueue();
}
```

**关键设计决策**：
- 使用 `async generator` 而非 `Promise`——允许 UI 层实时响应进度事件（`thinking`, `tool_start`, `tool_progress` 等）
- `overflowRetries` 机制应对上下文溢出——如果 LLM 返回 context overflow 错误，自动重试并截断（最多 2 次）
- `memoryFlushState.alreadyFlushed` 确保一次性执行中不会重复 flush

**值得关注的问题**：`drainQueue()` 仅在工具调用轮次之后执行，意味着如果 LLM 生成长篇思考，用户消息要等到工具执行完成后才被处理。这是单 Agent 循环的固有限制。

### 5.2 tool-executor.ts：工具执行引擎

**位置**: `src/agent/tool-executor.ts`（~215 行）

```typescript
// 关键：批处理分区算法
private partitionToolCalls(toolCalls: ToolCall[], ctx: RunContext): ToolCallBatch[] {
  const batches: ToolCallBatch[] = [];

  for (const call of toolCalls) {
    // Skill 去重：同一 skill 在单次查询中只执行一次
    if (call.name === 'skill') {
      const skillName = (call.args).skill;
      if (ctx.scratchpad.hasExecutedSkill(skillName)) continue;
    }

    const isSafe = this.concurrencyMap.get(call.name) ?? false;
    const lastBatch = batches[batches.length - 1];

    // 连续并发安全工具 → 合并到同一批次
    if (isSafe && lastBatch?.concurrent) {
      lastBatch.calls.push(call);
    } else {
      batches.push({ concurrent: isSafe, calls: [call] });
    }
  }
  return batches;
}
```

**设计要点**：
- **并发安全区分**：通过 `concurrencyMap`（name→bool）区分读写工具。`financial_search`、`web_search` 等只读工具可并发，`write_file`、`edit_file` 等写入工具串行执行
- **审核门禁**：`write_file` 和 `edit_file` 需要用户授信，支持一次性授权（`allow-session`）
- **进度通道**：通过 `createProgressChannel()` 实现工具执行进度的事件流式推送

### 5.3 Gateway 系统：会话管理与消息队列

**位置**: `src/gateway/agent-runner.ts`

```typescript
// 会话串行化模式
if (session) {
  // 关键行：session.tail.then(run, run)
  // 这保证了同一会话的消息按顺序处理，但不同会话可并发
  session.tail = session.tail.then(run, run);
  await session.tail;
} else {
  // 隔离会话：无状态模式（cron 任务使用）
  await run();
}
```

`session.tail` 是一个 Promise 链模式——每个新消息的处理追加到上一个处理之后。这是一个极其简洁但有效的并发控制模式：避免锁，不需要 Mutex，天然保证了同一会话的消息有序处理。

### 5.4 Cron 系统：Agent 的定时任务

**位置**: `src/cron/runner.ts` + `executor.ts`

```typescript
// 调度循环：最简实现
function scheduleNext(): void {
  // 找出所有启用的 job 中最早的 nextRunAtMs
  let earliest = Infinity;
  for (const job of store.jobs) {
    if (job.enabled && job.state.nextRunAtMs !== undefined) {
      earliest = Math.min(earliest, job.state.nextRunAtMs);
    }
  }
  
  // 最大定时器间隔 60s——确保能及时响应新增/修改的 job
  const delayMs = Math.min(Math.max(0, earliest - now), MAX_TIMER_DELAY_MS);
  timer = setTimeout(() => void tick(), delayMs);
  timer.unref();  // 不阻止进程退出
}
```

**启示**：不引入 Quartz、node-cron 等外部依赖，使用最简的 setTimeout + 文件存储实现。`timer.unref()` 确保进程可以在没有待处理任务时正常退出。

---

## 6. 全网口碑画像

### 6.1 好评集中点

**"工程师写给分析师的情书"**——社区普遍认可其工程完成度：
- Hacker News 评论："It's not a Q&A system, it's a self-correcting system."
- 评测博主 Andrew OO："月度 Token 成本约 $10-$30，相比 Bloomberg Terminal 的 $24,000/年，单位经济学惊人"
- 中文社区："这不是又一个单提示词的 LangChain 包装器，而是一个真正自主系统"

**Scratchpad 调试体验获一致好评**：
- 每位评测者都提到了 JSONL 日志的可审计性
- 金融合规场景下的审计追踪是社区公认的 killer feature

### 6.2 主要争议与批评

**争议一：付费 API 依赖**

社区最大的不满指向 Financial Datasets API——这是一个非免费的第三方 API。批评者认为，既然数据源来自公开的 SEC EDGAR，为什么不直接使用免费 EDGAR 数据？

**作者的回应**：Financial Datasets API 提供了结构化的财务数据（已解析的利润表、资产负债表），而 EDGAR 原始 XML/XBRL 格式需要大量预处理。这是工程效率 vs. 零成本的经典权衡。

**争议二：单 Agent 架构的局限性**

- 缺乏真正的多 Agent 辩论（对比 ai-hedge-fund）
- 没有定价/报价工具——仅限基本面研究，缺少分钟级 OHLC 数据
- 严重偏向美股，国际股票覆盖有限

**争议三：运行环境要求**

- 必须安装 Bun（对 Node.js 生态的团队是摩擦点）
- 需要配置多个 API Key（入门门槛较高）

### 6.3 数据来源

| 来源 | 态度 | 关键观点 |
|------|------|---------|
| Andrew.ooo (详细评测) | 积极，有保留 | "垂直 Agent 模式的干净范例"，指出数学错误和数据覆盖局限 |
| 知乎 (技术解析) | 技术深度解析 | 误标为多Agent架构，但技术分析详细 |
| Text Matrix | 客观介绍 | 实用导向，关注安装和使用体验 |
| Hacker News | 高度认可 | 关注工程化程度和自主能力 |
| GitHub Issues | 用户反馈 | API 配置复杂度和 Financial Datasets 付费是主要 Issue |

---

## 7. 竞品对比

### 7.1 对比矩阵

| 维度 | Dexter | FinGPT | ai-hedge-fund | TradingAgents | Bloomberg Terminal | ChatGPT 金融插件 |
|------|--------|--------|-------------|---------------|-------------------|-----------------|
| **定位** | 深度研究 Agent | 金融 LLM 框架 | 多角色投资组合 | 多 Agent 交易系统 | 专业终端 | 通用 AI + 插件 |
| **交互方式** | 自主 Agent (类似 Claude Code) | 固定 UI 界面 | 模拟辩论 | 多 Agent 辩论 | GUI 终端 | 聊天界面 |
| **数据覆盖** | 美股基本面 (SEC) | 取决于微调数据 | 美股 + 组合模拟 | 美股 + 交易信号 | 全球全资产 | 取决于插件 |
| **自主规划** | ✅ 强 | ❌ | ✅ 有限 | ✅ | ❌ | ❌ 单轮 |
| **自我验证** | ✅ 内置 | ❌ | ❌ | ❌ | ❌ | ❌ |
| **评估套件** | ✅ LLM-as-judge | ❌ | ❌ | ✅ 有限 | ✅ 内部 | ❌ |
| **多通道** | CLI + WhatsApp | Web | CLI | CLI | 桌面 + Web | Web |
| **定时任务** | ✅ Cron for Agents | ❌ | ❌ | ❌ | ✅ 高级 | ❌ |
| **实时性** | 中等 (基本面) | 低 | 中等 | 高 (交易信号) | 极高 (实时报价) | 中等 |
| **开源** | ✅ MIT | ✅ MIT | ✅ MIT | ✅ Apache-2 | ❌ 付费 | ❌ |
| **成本** | $10-30/月 API | GPU + 微调 | API 成本 | API 成本 | ~$24,000/年 | $20/月 + 插件 |
| **学习曲线** | 中等 (Bun + 配置) | 高 (微调) | 低 | 中高 | 极高 | 低 |

### 7.2 核心差异分析

**vs. FinGPT**：FinGPT 是"用金融数据微调一个 LLM"，Dexter 是"用通用 LLM + 金融工具组合自动化研究"。微调路线拥有更好的领域理解深度，但需要昂贵的 GPU 资源和持续的数据维护；工具路线更轻量、更灵活、更容易迭代。

**vs. ai-hedge-fund**：ai-hedge-fund 的多角色辩论（Buffett vs Munger vs Ackman）是更"娱乐化"的设计——通过模拟名人观点产生投资组合决策。Dexter 更贴近现实分析师的工作流（数据驱动、可审计、有置信度评估），而非角色扮演。

**vs. TradingAgents**：TradingAgents 面向交易执行和信号生成，Dexter 面向基本面研究和分析。两者在数据需求（报价 vs. 财务报表）和输出形态（交易信号 vs. 研究报告）上有本质差异。

**vs. Bloomberg Terminal**：Dexter 不是 Bloomberg Terminal 的替代品，而是"Bloomberg 数据研究那部分工作的自动化助手"。Bloomberg 的壁垒在于数据聚合和合规性，Dexter 的优势在于降低入门门槛和自动化重复劳动。$10-30/月 vs $24,000/年 的成本差距也说明了完全不同的市场定位。

### 7.3 Dexter 的竞争壁垒

1. **工程完成度**：评估套件 + 调试系统 + 错误恢复 = 同类开源项目中最高
2. **交互设计**：WhatsApp 集成 + 消息队列使交互延迟感最小化
3. **生态位**：第一个将"Claude Code 式 Agent 体验"移植到金融垂直领域的开源项目，拥有先发优势和社区网络效应

---

## 8. 核心研判

### 8.1 项目前景判断

**短期（6个月）**：Stars 将突破 35k-40k，成为金融 AI 领域标杆性的开源项目。主要增长驱动力来自：
- WhatsApp 集成带来的 viral 效应（示例截图极具传播力）
- 非美股数据源扩展（社区 PR 将推动）
- 企业场景的采用（审计式 scratchpad 对合规部门有吸引力）

**中长期挑战**：
- **API 依赖风险**：Financial Datasets API 的商业化策略变化会影响整个项目
- **竞争加剧**：LangChain/AutoGen 等框架内置类似功能后，Dexter 的差异化缩小
- **数据地域化**：专注美股是优势也是局限，中国市场需要完全不同的数据工具（A 股、港股的 API 生态远不如美股成熟）

### 8.2 对 Agent 生态的启示

Dexter 的崛起验证了一个重要命题：**"为通用而设计，为垂直而优化"的中间路线在 Agent 场景中可能是最优解**。

- 过于通用（AutoGPT）：容易陷入"什么都能做，什么都做不好"的困境
- 过于通用框架（LangChain Agent）：缺乏领域深度，用户需要大量定制
- 过于垂直（单用途交易机器人）：市场太小，缺乏迭代动力

Dexter 选择的是：**用通用 Agent 架构作为基底，用领域数据工具和 Prompt 实现垂直优化**。这个模式可以复制到法律、医疗、科研等领域。

### 8.3 值得关注的演进方向

1. **数据源扩展**：加入全球市场数据（A股、港股、加密货币），这是从"有趣"到"必备"的关键一跃
2. **多 Agent 协作**：目前是单 Agent 循环，未来可能引入真正的规划 Agent 和执行 Agent 分离
3. **自然语言报告生成**：目前的输出还偏结构化数据展示，向真正的分析师报告演进
4. **协作工作台**：多人共享研究结果、协作编辑分析报告

---

## 9. 关键文件路径速查

| 文件路径 | 职责 | 核心内容 |
|---------|------|---------|
| `src/agent/agent.ts` | Agent 主循环 | 迭代式工具调用引擎，~700 行 |
| `src/agent/tool-executor.ts` | 工具执行器 | 并发调度 + 审核门禁 |
| `src/agent/scratchpad.ts` | 调试日志 | JSONL 审计追踪 + 工具限流 |
| `src/agent/prompts.ts` | 提示词构建 | System Prompt 组装（Soul + Rules + Tools） |
| `src/agent/compact.ts` | 上下文压缩 | LLM 总结历史工具结果 |
| `src/agent/run-context.ts` | 运行上下文 | 迭代计数器 + Token 统计 |
| `src/gateway/agent-runner.ts` | 网关会话管理 | Session + 消息队列 + 串行化 |
| `src/gateway/access-control.ts` | 访问控制 | WhatsApp 配对/白名单/策略矩阵 |
| `src/gateway/channels/whatsapp/runtime.ts` | WhatsApp 运行时 | 心跳 + 重连 + 看门狗 |
| `src/cron/runner.ts` | Cron 调度器 | setTimeout 实现的最简定时器 |
| `src/cron/executor.ts` | Cron 执行器 | 抑制 + 饱和检测 + 错误退避 |
| `src/cron/store.ts` | Cron 持久化 | JSON 文件存储 job 状态 |
| `src/cron/schedule.ts` | Cron 调度计算 | interval/at 模式的下次运行时间 |
| `src/evals/run.ts` | 评估运行器 | LLM-as-judge + LangSmith 追踪 |
| `src/model/llm.ts` | 多 Provider 抽象 | OpenAI/Anthropic/Google/xAI/Ollama |
| `src/tools/registry.ts` | 工具注册中心 | 工具发现 + 并发策略映射 |
| `AGENTS.md` | 开发指南 | 编码规范、项目结构、命令 |
| `SOUL.md` | Agent 人格配置 | 角色定义、行为准则 |
