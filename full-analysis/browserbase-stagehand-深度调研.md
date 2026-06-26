# Browserbase/Stagehand 深度调研报告

> 调研日期：2026-06-27 | 仓库状态：v3.6.0 / browse@0.9.0 | ⭐ 23,251 Stars | 🍴 1,594 Forks
> 
> 官方地址：[https://github.com/browserbase/stagehand](https://github.com/browserbase/stagehand) | 文档：[https://stagehand.dev](https://stagehand.dev)

---

## 📌 一句话定位

**Stagehand 是目前 TypeScript/Node.js 生态中「代码确定性与 AI 智能性」结合最紧密的浏览器自动化 SDK。它不是一个全自动 AI Agent，而是一个让你在 Playwright 之上按需注入 AI 能力的"精准外科手术刀"——该用选择器的用选择器，该用自然语言的交给 AI，并且会自动缓存、自愈、适应页面变化。**

---

## 🏗️ 项目架构全景

### 2.1 仓库结构（Monorepo）

```
stagehand/
├── packages/
│   ├── core/           # 核心 SDK（@browserbasehq/stagehand, v3.6.0）
│   │   └── lib/v3/     # 源码根（TypeScript，含 ~200+ 源文件）
│   │       ├── api.ts              # 云端 API 客户端（Browserbase SaaS 通信层）
│   │       ├── v3.ts               # 主入口类 V3（即 Stagehand 类）
│   │       ├── handlers/           # act/observe/extract 三大原语处理器
│   │       │   ├── actHandler.ts        # 动作执行：LLM 理解意图 → 执行浏览器操作
│   │       │   ├── observeHandler.ts    # 元素观察：LLM 扫描 DOM/A11y 树 → 返回候选元素
│   │       │   └── extractHandler.ts    # 数据提取：LLM 结构化抽取 → Zod Schema 验证
│   │       ├── agent/              # Agent 模式（多步自主执行）
│   │       │   ├── AgentClient.ts       # 抽象基类
│   │       │   ├── AgentProvider.ts     # 根据模型路由到不同 CUA 客户端
│   │       │   ├── AnthropicCUAClient.ts # Anthropic Computer Use
│   │       │   ├── OpenAICUAClient.ts    # OpenAI CUA
│   │       │   ├── GoogleCUAClient.ts    # Google CUA (Gemini)
│   │       │   ├── MicrosoftCUAClient.ts # Microsoft CUA
│   │       │   ├── tools/               # Agent 可用工具（act, click, type, scroll, extract...）
│   │       │   └── utils/               # 截图处理、坐标系归一化、CAPTCHA 解决等
│   │       ├── cache/              # 离线缓存与自愈系统
│   │       │   ├── ActCache.ts          # 动作级缓存（SHA256 键 → 回放已缓存操作）
│   │       │   ├── AgentCache.ts        # Agent 级缓存（跨会话持久化）
│   │       │   └── CacheStorage.ts      # 缓存存储后端（文件系统 / 内存）
│   │       ├── llm/                # LLM 统一抽象层
│   │       │   ├── LLMProvider.ts       # 模型路由（支持 15+ 提供商）
│   │       │   ├── LLMClient.ts         # LLM 调用基类（含 token 计量）
│   │       │   ├── OpenAIClient.ts      # OpenAI 客户端
│   │       │   ├── AnthropicClient.ts   # Anthropic 客户端
│   │       │   ├── GoogleClient.ts      # Google Gemini 客户端
│   │       │   └── aisdk.ts             # Vercel AI SDK 统一接口
│   │       ├── understudy/         # 浏览器底层控制（CDP 封装）
│   │       │   ├── context.ts           # V3Context：浏览器生命周期管理
│   │       │   ├── page.ts              # Page：页面对象封装
│   │       │   ├── a11y/                # 无障碍树处理
│   │       │   │   └── snapshot/        # Hybrid 快照：A11y Tree + DOM Tree + 坐标映射
│   │       │   ├── cdp.ts               # CDP 协议封装
│   │       │   ├── deepLocator.ts      # XPath 跨 Shadow DOM/iframe 深度定位
│   │       │   └── frameLocator.ts      # 跨 iframe 定位
│   │       ├── mcp/                # MCP 协议集成
│   │       ├── flowlogger/         # 事件流日志系统
│   │       ├── shutdown/           # 浏览器进程清理与守护
│   │       ├── launch/             # 浏览器启动（local Chrome / Browserbase 云端）
│   │       └── types/              # 类型系统（public SDK 类型 + private 内部类型）
│   ├── cli/             # CLI 工具（@browserbasehq/cli）
│   └── server/          # Stagehand Server（v3/v4 用于云端部署）
├── package.json         # Monorepo 根（pnpm workspace, turbo build）
└── claude.md            # AI Agent 上下文文件（供 Claude Code / Cursor 使用）
```

**核心统计数据：**

| 维度 | 数据 |
|------|------|
| 仓库总文件数（不含 node_modules） | 1,139 |
| 核心源码（packages/core/lib/v3/） | ~200 文件 |
| TypeScript 占比 | ~98%（总代码量 4.8M） |
| 测试框架 | Vitest + Playwright Test |
| 构建工具 | esbuild + tsc（esm/cjs 双输出） |
| 包管理器 | pnpm 9.x + Turbo monorepo |

### 2.2 技术栈依赖

**核心运行时依赖（packages/core/package.json）：**

| 依赖 | 用途 |
|------|------|
| `playwright-core` / `puppeteer-core` / `patchright-core` | Peer dep，三选一浏览器引擎 |
| `zod` ^3.25 / ^4.2 | Schema 验证，结构化提取的核心 |
| `@anthropic-ai/sdk` 0.39.0 | Anthropic Claude 直连客户端 |
| `openai` ^4.104 | OpenAI 直连客户端 |
| `@google/genai` ^1.22 | Google Gemini 直连客户端 |
| `@ai-sdk/provider` + `ai` ^5.0 | Vercel AI SDK 统一接口 |
| `devtools-protocol` | CDP 协议类型定义 |
| `@modelcontextprotocol/sdk` ^1.29 | MCP 协议集成 |
| `pino` + `pino-pretty` | 结构化日志 |
| `uuid` v7 | 实例/Session ID 生成 |

**可选 AI SDK 提供商（optionalDependencies，按需安装）：**
`@ai-sdk/anthropic`, `@ai-sdk/openai`, `@ai-sdk/google`, `@ai-sdk/azure`, `@ai-sdk/cerebras`, `@ai-sdk/deepseek`, `@ai-sdk/groq`, `@ai-sdk/mistral`, `@ai-sdk/perplexity`, `@ai-sdk/togetherai`, `@ai-sdk/xai`, `@ai-sdk/amazon-bedrock`, `@ai-sdk/google-vertex`, `ollama-ai-provider-v2`

### 2.3 部署模式

Stagehand 支持两种部署模式，通过 `env: "LOCAL" | "BROWSERBASE"` 切换（`v3.ts:line ~230`）：

```
┌──────────────────────────────────────┐
│  用户代码 (TypeScript / JavaScript)   │
├──────────────────────────────────────┤
│  Stagehand SDK (@browserbasehq/stagehand) │
├──────────────┬───────────────────────┤
│  LOCAL 模式  │  BROWSERBASE 模式     │
│  (CDP 直连)  │  (Browserbase API)    │
├──────────────┼───────────────────────┤
│  本地 Chrome │  Browserbase 云端      │
│  (chromium-  │  Chromium 容器         │
│   launcher)  │  + 代理 + CAPTCHA     │
└──────────────┴───────────────────────┘
```

**LOCAL 模式**：纯本地运行，Stagehand 通过 CDP 直接控制的本地 Chromium 浏览器。零额外费用，适合开发调试。

**BROWSERBASE 模式**：浏览器运行在 Browserbase 云端容器中，自带反检测隐身、CAPTCHA 解决、代理轮换、会话录制。按分钟计费（$0.01/min，免费额度 100 分钟/月）。

---

## 🧠 核心源码解读

### 3.1 主入口类 V3（Stagehand）

**文件**：`packages/core/lib/v3/v3.ts`

这是整个 SDK 的核心——所有用户调用的 `stagehand.act()`, `stagehand.extract()`, `stagehand.observe()`, `stagehand.agent()` 都经由这个类分发到对应的 Handler。

**关键设计**：

```typescript
// 核心状态机（v3.ts ~line 80）
private state: InitState = { kind: "UNINITIALIZED" };
// state 有三种状态：
// { kind: "UNINITIALIZED" } → 未初始化
// { kind: "LOCAL", ... }    → 本地 Chrome 模式
// { kind: "BROWSERBASE", ... } → Browserbase 云端模式

// Handler 委托
private actHandler: ActHandler | null = null;
private extractHandler: ExtractHandler | null = null;
private observeHandler: ObserveHandler | null = null;

// 缓存系统
private cacheStorage: CacheStorage;
private actCache: ActCache;
private agentCache: AgentCache;

// LLM 客户端（支持运行时切换模型）
public llmClient!: LLMClient;
private overrideLlmClients: Map<string, LLMClient> = new Map();
```

**架构决策分析**：
1. **Handler 分离**：每种 AI 操作（act/observe/extract）有独立的 Handler 类，职责清晰，易于测试和维护。
2. **LLM 可插拔**：通过 `LLMProvider` 统一管理 15+ 个模型提供商，并支持运行时 `model` 参数切换（如 `act("click", { model: "anthropic/claude-sonnet-4" })`）。
3. **缓存透明集成**：`ActCache` 和 `AgentCache` 在 act/agent 调用链中透明介入，对用户不可见但效果显著。
4. **API 模式**：`StagehandAPIClient`（api.ts）提供云端模式下的 SSE 流式通信，将 act/extract/observe 请求通过 HTTP 发送到 Browserbase 服务器端处理。这种分离使得云端部署可以共享 LLM 调用上下文。

### 3.2 ObserveHandler：AI 视觉元素定位

**文件**：`packages/core/lib/v3/handlers/observeHandler.ts`

这是 Stagehand 最核心的差异化能力——让 LLM "看懂"页面结构并找到可操作元素。

**核心执行流程（observeHandler.ts ~line 70-200）：**

```
1. 接收instruction（如"点击登录按钮"）
2. 调用 captureHybridSnapshot(page) → 生成包含以下内容的结构化快照：
   - combinedTree: 无障碍树 + DOM 树合并后的文本表示
   - combinedXpathMap: 每个元素的 EncodedId → XPath 映射表
3. 构建 LLM prompt，将 combinedTree 作为上下文
4. LLM 返回 elementId 列表（如 {"elementId": "1-67", "method": "click"}）
5. 从 combinedXpathMap 中查表得到实际 XPath：
   combinedXpathMap["1-67"] → "/html/body/div[2]/form/button"
6. 返回 Action[] 数组，每个包含 { selector: "xpath=...", method, description }

// 对 dragAndDrop 的特殊处理（observeHandler.ts ~line 145-175）：
// 因为拖拽需要两个元素，需要同时解析 source 和 target 的 XPath
if (rest.method === "dragAndDrop" && Array.isArray(rest.arguments)) {
  const targetArg = rest.arguments[0];
  if (typeof targetArg === "string" && /^\d+-\d+$/.test(targetArg)) {
    const argXpath = combinedXpathMap[targetArg];
    resolvedArgs = [`xpath=${trimmedArgXpath}`, ...rest.arguments.slice(1)];
  }
}
```

**关键设计洞察**：
- **A11y Tree + XPath 双索引**：Stagehand 不依赖 LLM 输出 CSS 选择器（因为 LLM 经常会编造不存在的选择器），而是让 LLM 输出一个短 ID（`1-67`），再从预先构建的 `combinedXpathMap` 中查找真实的 XPath。这从根本上避免了 LLM "幻觉"导致的定位失败。
- **Hybrid Snapshot**：`captureHybridSnapshot()` 结合了无障碍树（语义丰富但结构粗糙）和 DOM 树（结构精确但语义缺失）的优点，生成了一个既包含语义信息又有精确位置的复合文本表示。
- **Timeout Guard**：`createTimeoutGuard(timeout, (ms) => new ObserveTimeoutError(ms))` — 每次 snapshot 和 LLM 调用前都检查剩余时间，避免超时后继续浪费 LLM token。

### 3.3 ActCache：动作缓存与自愈系统

**文件**：`packages/core/lib/v3/cache/ActCache.ts`

这是 Stagehand "Write Once, Run Forever" 口号的工程实现基础。

**核心机制**：

```
ActCache 工作流（ActCache.ts ~line 30-210）：

┌─────────────┐
│ 用户调用 act │
└──────┬──────┘
       ▼
  prepareContext() → 计算缓存键
       │
       │ cacheKey = SHA256(instruction + normalizedURL + variableKeys)
       ▼
  tryReplay() → 查找缓存
       │
   ┌───┴───┐
   │ HIT  │ → replayCachedActions()
   │      │   → 逐个执行缓存中的 action
   │      │   → 每个 action 前 waitForCachedSelector()
   │      │   → 如果选择器失效 → act() fallback（自愈触发）
   │      │   → 成功后检查 actionsChanged() → refreshCacheEntry()
   └──────┘
       │
   ┌───┴───┐
   │ MISS │ → act() 走正常 LLM 流程
   │      │   → 成功 → store(context, result)
   └──────┘
```

**缓存键设计（ActCache.ts ~line 157-164）**：
```typescript
private buildActCacheKey(instruction: string, url: string, variableKeys: string[]): string {
  const payload = JSON.stringify({ instruction, url, variableKeys });
  return createHash("sha256").update(payload).digest("hex");
}
```

**自愈机制（ActCache.ts ~line 195-230）**：
```typescript
// 当缓存的 actions 回放成功后，检查是否有 actions 发生变化
if (this.haveActionsChanged(entry.actions, actions)) {
  await this.refreshCacheEntry(context, {
    ...entry, actions, message, actionDescription
  });
}
```
- 缓存回放成功后，比较原始 action 与实际执行的 action
- 如果页面结构变化导致 XPath 不同，自动更新缓存
- 这是 "self-heal" 的具体实现：页面变了，缓存自动跟着变

**变量支持**：ActCache 支持 `variables` 参数，缓存键包含 `variableKeys`（但不包含变量值），回放时检查所有必需的变量是否已提供。这使得 "点击第 N 个商品" 这类带参数的指令也能有效缓存。

### 3.4 AgentClient 与多模式 Agent

**文件**：`packages/core/lib/v3/agent/AgentClient.ts`, `AgentProvider.ts`, `AnthropicCUAClient.ts`, `OpenAICUAClient.ts`, `GoogleCUAClient.ts`, `MicrosoftCUAClient.ts`

Stagehand 的 Agent 能力通过一个抽象基类和多个策略实现：

```
AgentClient (抽象基类)
  ├── DOM Agent    → 使用 act/extract 工具（适用任何 LLM）
  ├── Hybrid Agent → DOM 工具 + 坐标工具（适用支持可靠坐标的 LLM）
  └── CUA Agent    → Computer Use Agent
       ├── AnthropicCUAClient  → Claude Computer Use
       ├── OpenAICUAClient     → OpenAI Operator
       ├── GoogleCUAClient     → Gemini Computer Use
       └── MicrosoftCUAClient  → 预留接口
```

**三种 Agent 模式对比（claude.md 文档）：**

| 模式 | 触发条件 | 可用工具 | 推荐模型 |
|------|---------|---------|---------|
| `dom` | 默认（任意模型） | act, fillForm, extract | 任意模型 |
| `hybrid` | 自动检测支持模型 | DOM 工具 + click, type, scroll, dragAndDrop | Claude Sonnet 4, GPT-5.4, Gemini 3 |
| `cua` | 显式指定 `mode: "cua"` | 模型原生的 Computer Use 工具 | Claude Sonnet 4, Gemini 2.5 CUA Preview |

**Agent 工具集**（`packages/core/lib/v3/agent/tools/`）：

```
act.ts          → 单步操作（最核心）
click.ts        → 坐标点击
type.ts         → 键盘输入
scroll.ts       → 页面滚动
extract.ts      → 结构化提取
fillform.ts     → 表单填写（DOM 方式）
fillFormVision.ts → 表单填写（视觉方式）
goto.ts         → 页面导航
navback.ts      → 后退
wait.ts         → 等待
keys.ts         → 组合键
screenshot.ts   → 截图
dragAndDrop.ts  → 拖拽
clickAndHold.ts → 长按
ariaTree.ts     → A11y 树获取
think.ts        → Agent 思考和规划
braveSearch.ts  → 外部搜索（Brave Search API）
browserbaseSearch.ts → Browserbase 搜索
```

### 3.5 LLM 统一抽象层：LLMProvider

**文件**：`packages/core/lib/v3/llm/LLMProvider.ts`

Stagehand 的 LLM 集成策略极其灵活——支持 **15+ 模型提供商**，通过两套接口实现：

**双入口策略**：
1. **原生 SDK 客户端**：`OpenAIClient`, `AnthropicClient`, `GoogleClient`, `CerebrasClient`, `GroqClient` — 对性能和特定 API 功能有最佳支持
2. **Vercel AI SDK 统一客户端**：`AISdkClient` — 通过 `ai` 包统一接口，支持 `@ai-sdk/openai`, `@ai-sdk/anthropic`, `@ai-sdk/google`, `@ai-sdk/azure`, `@ai-sdk/deepseek`, `@ai-sdk/mistral`, `@ai-sdk/groq`, `@ai-sdk/cerebras`, `@ai-sdk/togetherai`, `@ai-sdk/perplexity`, `@ai-sdk/xai`, `@ai-sdk/amazon-bedrock`, `@ai-sdk/google-vertex`, `ollama-ai-provider-v2`

**模型命名约定**：`provider/model-name`
- `openai/gpt-4.1-mini`
- `anthropic/claude-sonnet-4-20250514`
- `google/gemini-2.5-flash-preview`
- `ollama/llama-4`（本地模型）

**运行时模型切换**：每个 API 方法（act/extract/observe/agent）都支持 `model` 参数，可以在不同调用中使用不同模型，例如：act 用便宜模型做简单操作，extract 用强模型做复杂提取。

### 3.6 API 客户端（Browserbase 云端模式）

**文件**：`packages/core/lib/v3/api.ts`

当使用 Browserbase 云端模式时，SDK 通过 SSE（Server-Sent Events）流与 Browserbase 服务器通信。

**核心通信协议（api.ts ~line 350-450）**：

```
客户端 → 服务器：
POST /v1/sessions/:id/act    { input, options, frameId }
POST /v1/sessions/:id/extract { instruction, schema, options, frameId }
POST /v1/sessions/:id/observe { instruction, options, frameId }
POST /v1/sessions/:id/agentExecute { agentConfig, executeOptions, frameId }

服务器 → 客户端（SSE 流）：
event: log    → { type: "log", data: { message: LogLine } }
event: system → { type: "system", data: { status: "finished"/"error", result: T } }

响应头：
browserbase-cache-status: HIT | MISS  → 缓存命中状态
```

**设计特点**：
- **POST + SSE 响应**：请求用 POST 发送，响应通过 SSE 长连接流式返回，支持中间日志和最终结果
- **浏览器连接复用**：服务器端维护浏览器会话，客户端只需发送操作指令
- **多区域部署**：`us-west-2`, `us-east-1`, `eu-central-1`, `ap-southeast-1`

### 3.7 代码量级评估

核心模块的代码规模（基于文件大小推算）：

| 模块 | 估算行数 | 复杂度 |
|------|---------|--------|
| v3.ts (主入口) | ~1000+ | 最高 |
| api.ts (云端客户端) | ~600 | 高 |
| actHandler.ts | ~300+ | 高 |
| observeHandler.ts | ~200 | 中 |
| extractHandler.ts | ~200 | 中 |
| AgentClient + 各 CUA 客户端 | ~800+ | 高 |
| ActCache.ts | ~280 | 中 |
| LLMProvider.ts | ~200 | 中 |
| inference.ts (LLM prompt 构建) | ~300 | 高 |
| 各 agent/tools/ 文件 | ~15×100 | 中 |
| understudy/ (CDP 封装) | ~20×150 | 高 |
| types/ (类型定义) | ~30×50 | 中 |

---

## 📐 架构决策与设计哲学

### 决策 1：从 Playwright 之上到 CDP 之下（v2 → v3 跃迁）

**v2 架构**：Stagehand 是 Playwright 的一个包装层。

**v3 架构（2025年10月发布）**：Stagehand 移除了 Playwright 硬依赖，直接基于 Chrome DevTools Protocol (CDP) 操作浏览器。Playwright/Puppeteer 变为可选的 `peerDependencies`。

> 代码证据：`packages/core/package.json` 中 `playwright-core`, `puppeteer-core`, `patchright-core` 都是 `peerDependencies`，且带有 `peerDependenciesMeta.optional: true`。

**设计理由（来自 Stagehand v3 官方博客）：**
1. Playwright 的 actionability checks 和 auto-waiting 为测试场景设计，在自动化场景中增加了不必要的开销
2. iframe/Shadow DOM 导航需要更底层的 CDP 控制
3. 长会话自动化要求更低的内存占用和更少的 WebSocket 往返

**影响**：v3 性能提升 **44%**（尤其在 iframe 和 Shadow DOM 场景），同时支持 Bun 运行时。

### 决策 2：代码 + AI 混合控制（而非纯 AI Agent）

Stagehand 没有像 Browser Use 那样构建一个完全自主的 Agent 循环，而是提供了 `act()`/`extract()`/`observe()` 三个精准的 AI 原语，让开发者自主组合。

```
// Stagehand 哲学：开发者决定何时用代码、何时用 AI
await page.goto("https://example.com");              // 代码 — 确定、快速
await stagehand.act("click the login button");        // AI — 灵活、自愈
await page.locator("#email").fill("user@test.com");   // 代码 — 确定
await stagehand.extract("get the dashboard stats", schema); // AI — 结构化提取
```

这避免了纯 Agent 模式的三个问题：
1. **成本不可控**：每步都调用 LLM，复杂任务成本线性增长
2. **行为不可预测**：LLM 可能"迷路"或重复操作
3. **调试困难**：不知道哪一步会出错

### 决策 3：A11y Tree + XPath 索引（而非纯视觉或纯 DOM）

**纯视觉方案问题**：截图不能精确区分同色同类型元素，且 token 消耗巨大。
**纯 DOM 方案问题**：大量噪声信息，结构类化的页面会让 LLM 困惑。

Stagehand 的 Hybrid Snapshot 策略：
- 从 CDP 获取无障碍树（语义丰富但缺少精确坐标）
- 注入 JavaScript 脚本计算每个元素的 XPath 和坐标
- 合并生成 `combinedXpathMap: { "1-67" → "/html/body/div[2]/button" }`
- LLM 只需输出短 ID，从映射表中查 XPath

这既保证了 LLM 理解页面的语义能力，又保证了定位的精确性。

### 决策 4：缓存 → 自愈 的渐进式可靠性策略

```
第一次调用 act("click login")  → LLM 推理 → 执行 → 缓存结果
第二次调用 act("click login")  → 缓存命中 → 直接回放 → 验证结果
网站改版后 act("click login") → 缓存回放失败 → LLM 推理 → 自愈 → 更新缓存
```

这是一个精巧的"偷懒"设计：绝大多数情况下不用 LLM，只在需要时才调用。但自愈逻辑 `haveActionsChanged()` 和 `refreshCacheEntry()` 确保了缓存不会因页面变化而腐化。

### 决策 5：Open Core + Cloud Service 商业模式

Stagehand SDK 完全开源（MIT），但深度集成 Browserbase 云服务：
- LOCAL 模式：零费用，完全自托管
- BROWSERBASE 模式：按分钟计费，提供反检测、代理、CAPTCHA 解决、会话录制
- API 模式：SDK 通过 HTTP/SSE 与 Browserbase 服务器通信，模型推理在服务端进行

这是 Classic Open Core 模式：SDK 免费吸引开发者，云服务收费覆盖生产需求。

---

## 🌐 全网口碑画像

### 5.1 GitHub 数据画像

| 指标 | 数据 | 来源 |
|------|------|------|
| Stars | 23,251 | `gh repo view` (2026-06-27) |
| Forks | 1,594 | 同上 |
| Open Issues | 244 | GitHub REST API |
| 总 Issues（开+关） | 92 + 历史 | `gh repo view --json issues` |
| Watchers | 95 | 同上 |
| 最新 Core 版本 | @browserbasehq/stagehand@3.6.0 | Releases (2026-06-19) |
| 最新 CLI 版本 | browse@0.9.0 | Releases (2026-06-25) |
| 发版频率 | ~1-2 周 | 近 5 个 Release 跨 3 周 |

**趋势判断**：Star 增长迅速（23K+ 在约 2 年内），活跃维护，社区反馈积极。与 Browserbase 公司绑定紧密，开源服务于商业云产品。

### 5.2 专业评测来源

#### 来源 1：NxCode 全面对比（2026-02） [原文链接](https://www.nxcode.io/zh/resources/news/stagehand-vs-browser-use-vs-playwright-ai-browser-automation-2026)

**核心观点**：
> "对于确定性和大批量任务使用 Playwright，毫无疑问。当你需要在更大的自动化工作流中进行精确的 AI 操作时使用 Stagehand。"

**实测数据**（Google 搜索任务，Claude Sonnet 模型）：
- Stagehand: 6.4 秒, ~3,200 tokens, $0.012 成本, 100% 成功率
- Browser Use: 18.2 秒, ~12,400 tokens, $0.048 成本, 100% 成功率
- Playwright MCP: 8.1 秒, ~4,800 tokens, $0.018 成本, 90% 成功率

**关键发现**：Stagehand 在结构化提取场景中最快最省 Token，比 Browser Use 便宜约 4 倍。

#### 来源 2：FuturePicker 四工具深度评测（2026-04） [原文链接](https://futurepicker.com/ai-browser-automation-tools-browser-use-stagehand-skyvern-playwright-2026/)

**核心观点**：
> "如果你已经有工程团队，而且不想在 AI 和确定性控制之间二选一，Stagehand 更合理。它让你保留代码结构，同时把 AI 放进最难维护的环节。"

**关键发现**：
- Stagehand 的学习曲线"中"——需要一定的工程能力，不是给零基础用户的
- 真正强在"将 Playwright 的控制力与 AI 的灵活性拼接"
- 弱点：完全自主模式不如 Browser Use，高级功能需要 Browserbase 付费

#### 来源 3：Xavier Fok 六个月生产实测 [原文链接](https://dataresearchtools.com/browserbase-review-2026/)

**核心观点**：
> "The session replay feature genuinely changes how teams debug. Engineers stopped writing speculative fixes and started watching the actual browser behavior, which cut MTTR on scraper bugs by roughly half."

**关键发现**：
- 会话回放功能将爬虫 bug 平均修复时间缩短约 50%
- 三个月仅 3 次部分宕机，总停机 < 90 分钟——可靠性优于自建
- 成功率 96-98%（含 CAPTCHA 解决），对比自建 89%
- 主要槽点：住宅代理 $8/GB 约为市场价的 2 倍
- 成本拐点：月爬取 > 1000 万页面时，自建更经济

#### 来源 4：苏米客 10 方案对比（2026-04） [原文链接](http://xmsumi.com/detail/2846)

**核心观点**：
> "Browser Use 和 Stagehand 是目前最推荐的两个方案。最佳实践：先用 Browser Use 快速验证想法，确定需要生产级部署后再考虑 Stagehand。"

**评分**（简版）：
- Browser Use: ⭐⭐⭐⭐⭐（效果最强，WebVoyager 89.1%）
- Stagehand: ⭐⭐⭐⭐⭐（稳定可控，自愈合能力强）
- Skyvern: ⭐⭐⭐⭐（反爬克星，视觉驱动）
- Playwright: ⭐⭐⭐（非 AI 工具，但稳定快速）

#### 来源 5：Bonza 博客技术分析（2026-02） [原文链接](https://blog.bonza.cn/2026/02/26/stagehand-ai-browser-automation-framework/)

**核心观点**：Stagehand 代表了"代码与 AI 融合"的新范式。其自愈机制和智能缓存大幅降低了维护成本。特别适合需要处理动态页面或不确定性的自动化场景。

### 5.3 社区情绪总结

**正面反馈（高频出现）**：
1. **自愈能力惊艳** — "一改版就断"的问题被实质性解决
2. **Token 效率高** — 比纯 Agent 方案节省 3-4 倍 LLM 成本
3. **会话回放（Browserbase 模式）** — 调试体验"革命性"
4. **Schema 结构化提取** — Zod 集成使数据提取既灵活又类型安全
5. **工程化程度高** — 适合不想完全放弃控制权的开发团队

**负面反馈/风险点（高频出现）**：
1. **不完全自主** — 复杂多步骤任务不如 Browser Use 智能
2. **Browserbase 绑定** — 高级功能（反检测、代理、CAPTCHA）依赖付费云服务
3. **代理费用偏高** — 住宅代理价格约为市场均价 2 倍
4. **仅 TypeScript 优先** — Python SDK 仍在追赶（stagehand-python 项目较新）
5. **文档偶有过时** — v2→v3 迁移过程中部分示例未更新

---

## ⚔️ 竞品对比

### 6.1 核心竞品一览

| 维度 | **Stagehand** | **Browser Use** | **Playwright** | **Skyvern** | **AgentQL** |
|------|---------------|-----------------|----------------|-------------|-------------|
| **定位** | AI 增强的开发者 SDK | 全自主 AI Agent | 确定性自动化框架 | 视觉驱动业务自动化 | AI 原生网页查询 |
| **语言** | TypeScript/JS（主），Python（追赶中） | Python | JS/TS/Python/Java/C# | Python | TypeScript/JS |
| **开源** | MIT | MIT | Apache 2.0 | AGPL v3 | Apache 2.0（部分） |
| **Stars** | 23K | 50K+ | 70K+ | 8K+ | 3K+ |
| **AI 模式** | 混合（代码 + AI 原语） | 全自动 Agent 循环 | 无 | 计算机视觉 | AI 查询语言 |
| **底层引擎** | CDP 直连 / Playwright / Puppeteer | Playwright | Chromium/Firefox/WebKit | Playwright + CV | Playwright |
| **验证码支持** | Browserbase 集成 | 不内置 | 不支持 | 内置视觉处理 | 不支持 |
| **学习曲线** | 中（需熟悉 Playwright） | 低（自然语言即可） | 中高（选择器复杂） | 中 | 中（类似 GraphQL） |
| **单次操作速度** | 1-3 秒（混合模式） | 2-5 秒 | <100ms | 3-6 秒（视觉推理） | 1-3 秒 |
| **10 步任务成本** | $0.01-0.03 | $0.05-0.15 | $0 | $0.02-0.08 | $0.01-0.05 |

### 6.2 场景决策矩阵

| 场景 | 首选 | 次选 | 原因 |
|------|------|------|------|
| 已知页面测试 | Playwright | Stagehand | 确定性 + 零成本 |
| 动态 UI 抓取 | Stagehand | Browser Use | Token 效率最高 |
| 复杂多步探索 | Browser Use | Stagehand (agent) | 自主规划能力 |
| 反爬严格网站 | Skyvern | Browserbase+Stagehand | 视觉驱动绕过 |
| 结构化数据提取 | Stagehand | AgentQL | Zod Schema 集成 |
| 企业 CI/CD | Playwright | Stagehand | 成熟生态 |
| 快速原型 | Browser Use | Stagehand | 最少代码量 |
| 生产级自动化 | Stagehand | Playwright+Browserbase | 可控 + 可观测 |
| 本地离线部署 | Playwright | Stagehand (LOCAL) | 零外部依赖 |
| AI Agent 子能力 | Browser Use | Stagehand (agent) | 自然融入 Agent 框架 |

### 6.3 竞品趋势判断

1. **Browser Use** 的 Star 增长速度（50K+）远超 Stagehand（23K），背后是 Python AI 生态的巨大惯性——LangChain、CrewAI 等都优先对接 Python 工具。但 Stagehand 的工程化设计更适合生产环境。

2. **Playwright** 不会被替代，而是成为 AI 工具的"标准底座"。Stagehand v3 的 CDP 直连策略说明了这一点——AI 层应该往下走，而不是往上飘。

3. **视觉驱动方案（Skyvern）** 在反爬赛道上不可替代，但与 DOM 方案（Stagehand/Browser Use）是互补而非竞争关系。

4. **CUA 模型（Claude Computer Use、Gemini Computer Use）** 让浏览器自动化门槛进一步降低。Stagehand 的 `cua` Agent 模式（`AnthropicCUAClient`、`GoogleCUAClient`）是对此趋势的快速响应。

---

## 🎯 核心研判

### 7.1 核心优势（为什么选 Stagehand）

1. **代码+AI 混合控制是当前最优解**
   - 完全自主 Agent 成本高、不可预测，纯确定性方案易断裂。Stagehand 的混合方案在工程实践中证明了最佳性价比。
   - 证据：fp8.co 实测数据（6.4 秒 / $0.012 vs Browser Use 18.2 秒 / $0.048）

2. **A11y Tree + XPath 索引消除了 LLM 幻觉风险**
   - 其他 AI 工具让 LLM 直接输出 CSS 选择器，LLM 经常编造不存在的选择器。Stagehand 让 LLM 只输出 ID，后端查 XPath 表，从根本上解决了这个问题。
   - 证据：`observeHandler.ts` 中的 `combinedXpathMap` + `EncodedId` 设计

3. **缓存 + 自愈系统大幅降低长期运行成本**
   - 首调用 LLM，后续回放缓存。网站改版时自动更新缓存。
   - 这在经济模型上是"用少量存储换取大量 LLM 调用"，在高频操作场景中成本优势显著。

4. **v3 CDP 直连架构实现性能跃迁**
   - 44% 性能提升（官方基准测试），摆脱 Playwright 的测试开销，直接操作浏览器协议层。
   - 证据：Stagehand v3 官方博客 + `understudy/cdp.ts` 实现

5. **多模型 + 多浏览器引擎的灵活生态**
   - 支持 15+ LLM 提供商 + 3 种浏览器引擎（Playwright/Puppeteer/Patchright），业界无人能及。

### 7.2 风险与不足

1. **Browserbase 云服务绑定风险**
   - Stagehand 本身开源，但高级功能（CAPTCHA 解决、代理轮换、会话录制、隐身模式）严重依赖 Browserbase 付费云服务。
   - 如果 Browserbase 公司定价策略变化或停止服务，Stagehand 的"完整解决方案"完整性会受损。

2. **TypeScript 生态锁定**
   - Stagehand 的主力开发语言是 TypeScript。Python 版本（stagehand-python）存在但远不如主版本成熟。
   - 在 Python 主导的 AI/ML 生态中，这是一个结构性劣势——Browser Use 借此获得了巨大的 Star 优势（50K vs 23K）。

3. **完全自主能力有限**
   - Stagehand 的 Agent 模式（`stagehand.agent()`）是后来添加的，并不是核心设计的一部分。
   - 在需要多步规划、分支决策、错误恢复的复杂场景中，不如 Browser Use 成熟。

4. **文档和版本碎片化**
   - v2→v3 的架构重构（Playwright → CDP）较大，部分旧文档、教程、博客中的示例可能已过时。
   - `claude.md` 中的示例使用了旧版 API 调用风格。

5. **代理成本偏高**
   - Browserbase 住宅代理 $8/GB 约为竞品 2 倍。对于大规模数据抓取场景，需要权衡是否 BYO 代理。

### 7.3 适用场景画像

**强烈推荐 Stagehand 的场景：**

- ✅ 需要在 TypeScript/Node.js 项目中添加 AI 驱动的浏览器操作
- ✅ 数据结构化提取是核心需求（`extract()` + Zod Schema 能力业界最强）
- ✅ 目标网站 UI 经常变化，维护选择器成本高
- ✅ 需要混合工作流：80% 确定性步骤 + 20% AI 模糊步骤
- ✅ 团队有 Playwright 经验，想渐进式引入 AI
- ✅ 生产级自动化，需要缓存、自愈、可观测性

**不太适合 Stagehand 的场景：**

- ❌ 需要一个完全自主的 AI Agent 去探索未知网站（用 Browser Use）
- ❌ 纯 Python 项目且团队无 TypeScript 经验（用 Browser Use 或 Skyvern）
- ❌ 超高频操作（每秒 100+ 请求），每次操作都需 LLM 推理（即使缓存也有开销，用 Playwright）
- ❌ 完全离线/无外网的部署环境（LOCAL 模式可用，但需自备推理 API）

### 7.4 发展趋势预判

1. **收敛方向**：Stagehand 正在从"AI 增强的 Playwright"向"AI 原生浏览器自动化平台"演进。v3 移除 Playwright 硬依赖是关键信号。

2. **CUA 模型将降低使用门槛**：Claude Computer Use、Gemini Computer Use、GPT CUA 等原生模型能力越来越强，Stagehand 的 CUA Agent 模式（AnthropicCUAClient、GoogleCUAClient、OpenAICUAClient）会成为越来越多用户的首选。

3. **Python 版本快速发展**：为捕获 Python AI 生态的用户，Stagehand-python 预计会获得更多投入。

4. **Browserbase 云服务深入集成**：预计会出现更多 Browserbase 独占功能，开源版本和云版本的 gap 可能进一步拉大。

5. **Agent 模式持续增强**：`agent()` 方法虽然晚于 Browser Use，但工具集（act、click、type、scroll、extract、dragAndDrop、fillForm 等）已经非常丰富。未来可能会在自主规划能力上追赶。

---

## 📂 关键文件路径速查

### SDK 核心源码

| 文件路径 | 说明 | 行数（估） |
|---------|------|----------|
| `packages/core/lib/v3/v3.ts` | 主入口类 V3（Stagehand），状态机、生命周期管理 | 1000+ |
| `packages/core/lib/v3/api.ts` | Browserbase 云端 API 客户端（SSE 流） | 600+ |
| `packages/core/lib/v3/handlers/actHandler.ts` | act() 动作执行处理器 | 300+ |
| `packages/core/lib/v3/handlers/observeHandler.ts` | observe() 元素观察处理器 | 200 |
| `packages/core/lib/v3/handlers/extractHandler.ts` | extract() 数据提取处理器 | 200+ |
| `packages/core/lib/v3/handlers/v3AgentHandler.ts` | DOM/Hybrid Agent 处理器 | 400+ |
| `packages/core/lib/v3/handlers/v3CuaAgentHandler.ts` | CUA Agent 处理器 | 300+ |
| `packages/core/lib/v3/agent/AgentClient.ts` | Agent 抽象基类 | 60 |
| `packages/core/lib/v3/agent/AgentProvider.ts` | 模型到 CUA 客户端的路由 | 100+ |
| `packages/core/lib/v3/agent/AnthropicCUAClient.ts` | Anthropic Computer Use 适配 | 200+ |
| `packages/core/lib/v3/agent/OpenAICUAClient.ts` | OpenAI Operator 适配 | 200+ |
| `packages/core/lib/v3/agent/GoogleCUAClient.ts` | Gemini Computer Use 适配 | 200+ |
| `packages/core/lib/v3/cache/ActCache.ts` | 动作级缓存与自愈系统 | 280 |
| `packages/core/lib/v3/cache/AgentCache.ts` | Agent 级缓存 | 200+ |
| `packages/core/lib/v3/cache/CacheStorage.ts` | 缓存存储后端 | 100+ |
| `packages/core/lib/v3/llm/LLMProvider.ts` | 15+ LLM 提供商统一路由 | 200+ |
| `packages/core/lib/v3/llm/LLMClient.ts` | LLM 调用基类（含 token 计量） | 200+ |
| `packages/core/lib/v3/llm/OpenAIClient.ts` | OpenAI 原生客户端 | 150+ |
| `packages/core/lib/v3/llm/AnthropicClient.ts` | Anthropic 原生客户端 | 150+ |
| `packages/core/lib/v3/llm/aisdk.ts` | Vercel AI SDK 统一接口 | 100+ |

### 浏览器底层控制

| 文件路径 | 说明 |
|---------|------|
| `packages/core/lib/v3/understudy/context.ts` | V3Context：浏览器上下文管理 |
| `packages/core/lib/v3/understudy/page.ts` | Page 对象封装 |
| `packages/core/lib/v3/understudy/cdp.ts` | CDP 协议封装 |
| `packages/core/lib/v3/understudy/a11y/snapshot/index.ts` | Hybrid Snapshot：A11y + DOM + 坐标 |
| `packages/core/lib/v3/understudy/deepLocator.ts` | XPath 跨 Shadow DOM/iframe 定位 |
| `packages/core/lib/v3/understudy/frameLocator.ts` | 跨 iframe 定位 |
| `packages/core/lib/v3/launch/local.ts` | 本地 Chrome 启动 |
| `packages/core/lib/v3/launch/browserbase.ts` | Browserbase 云端会话创建 |

### Agent 工具集

| 文件路径 | 说明 |
|---------|------|
| `packages/core/lib/v3/agent/tools/index.ts` | 工具注册表 |
| `packages/core/lib/v3/agent/tools/act.ts` | 单步操作工具 |
| `packages/core/lib/v3/agent/tools/extract.ts` | 结构化提取工具 |
| `packages/core/lib/v3/agent/tools/click.ts` | 坐标点击工具 |
| `packages/core/lib/v3/agent/tools/type.ts` | 键盘输入工具 |
| `packages/core/lib/v3/agent/tools/scroll.ts` | 滚动工具 |
| `packages/core/lib/v3/agent/tools/fillform.ts` | 表单填写工具 |
| `packages/core/lib/v3/agent/tools/fillFormVision.ts` | 视觉表单填写 |
| `packages/core/lib/v3/agent/tools/dragAndDrop.ts` | 拖拽工具 |
| `packages/core/lib/v3/agent/tools/think.ts` | Agent 思考/规划工具 |

### LLL 推理核心

| 文件路径 | 说明 |
|---------|------|
| `packages/core/lib/inference.ts` | act/observe/extract 的 LLM Prompt 构建和执行 |
| `packages/core/lib/prompt.ts` | 系统提示词模板 |
| `packages/core/lib/modelUtils.ts` | 模型名称解析工具 |

### 配置与入口

| 文件路径 | 说明 |
|---------|------|
| `package.json` | Monorepo 根配置 |
| `packages/core/package.json` | Core SDK 包配置（依赖、版本、导出） |
| `claude.md` | AI Agent 上下文文件（Claude Code / Cursor 使用） |
| `.env.example` | 环境变量模板 |
| `packages/core/lib/v3/index.ts` | 公开 API 导出 |
| `packages/core/lib/v3/types/public/` | 公共类型定义 |
| `packages/core/lib/v3/types/private/` | 内部类型定义 |

### 测试与时评

| 文件路径 | 说明 |
|---------|------|
| `packages/core/tests/core/` | 核心单元测试 |
| `packages/core/tests/e2e/` | 端到端测试 |
| `.github/workflows/ci.yml` | CI 流水线 |
| `.github/workflows/feature-parity.yml` | 功能一致性检查 |

---

## 附录：调研方法论

本报告基于以下方法完成：

1. **GitHub API 深度调用**：通过 `gh repo view`、`gh api` 获取仓库元数据、文件树、核心源码
2. **源码精读**：阅读了 `packages/core/lib/v3/` 下 15+ 个核心文件，重点关注 `v3.ts`、`observeHandler.ts`、`ActCache.ts`、`AgentClient.ts`、`api.ts`、`LLMProvider.ts`
3. **Web 搜索**：中英文关键词各 4 组，覆盖专业评测、用户反馈、竞品对比
4. **内容分析**：精读 5 篇深度专业评测文章和 1 篇官方博客
5. **社区信号**：HN/Reddit 提及、Star 增长趋势、Release 频率

**数据时效**：所有 GitHub 数据采集于 2026-06-27，Web 内容截至 2026 年 4-6 月。

---

*本报告由 AI Agent 自动生成，基于公开的 GitHub 仓库和 Web 数据。所有观点均引用来源。*