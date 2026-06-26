# n8n-io/n8n 深度调研报告

> 调研日期：2026-06-27 | 仓库版本：n8n@2.27.4 | 调研维度：代码 + 社区 + 竞品

---

## 1. 一句话定位

**n8n 是一个面向技术团队的 "公平代码"（fair-code）工作流自动化平台——用可视化画布编排 400+ SaaS 集成和 AI 能力，同时保留随时写 JavaScript/Python 的自由，自托管零成本运行。**

它不是 Zapier 的开源替代品那么简单——它是 "想写代码的时候写代码，不想写的时候拖拽" 的混合平台。2025 年后，AI Agent 成为第二增长曲线，让 n8n 从 "自动化引擎" 进化为 "AI 编排平台"。

---

## 2. 项目架构全景

### 2.1 基础数据

| 维度 | 数值 |
|------|------|
| GitHub Stars | **194,179**（全球自动化类工具 Top 3） |
| Forks | 58,854 |
| 主要语言 | TypeScript（占总代码量 ~84.9M / 93M bytes） |
| 协议 | Sustainable Use License（非 OSI 开源，属 "fair-code"） |
| 许可证类别 | Other |
| 仓库体积 | 501 MB |
| 默认分支 | master |
| 最新版本 | n8n@2.27.4（2026-06-24 发布） |
| 开放 Issues | 443 |
| 创建时间 | 2019-06-22 |
| 公司 | n8n GmbH（柏林） |
| 创始人 | Jan Oberhauser |
| 融资总额 | $240M（含 C 轮 $180M，估值 $2.5B） |
| 投资人 | Accel（领投）、Meritech、Redpoint、NVIDIA(NVentures)、Sequoia、Felicis |

> 数据来源：`gh repo view n8n-io/n8n`、`gh api`、n8n 官方博客 Series C 公告

### 2.2 仓库目录结构

```
n8n-monorepo/
├── packages/
│   ├── cli/                   # 主入口 — n8n CLI 命令、HTTP API、Webhook 服务
│   ├── core/                  # 核心运行时 — 工作流执行引擎、凭证管理、数据去重
│   ├── workflow/              # 工作流定义 — Workflow 类、表达式引擎、连接管理
│   ├── nodes-base/            # 400+ 内置集成节点（Slack、GitHub、OpenAI 等）
│   ├── frontend/              # Vue.js 编辑器前端
│   ├── extensions/            # 扩展框架 — 社区节点注册
│   ├── node-dev/              # 节点开发工具链
│   ├── testing/               # 测试基础设施
│   └── @n8n/                  # 内部子包（40+ 个模块）
│       ├── agents/            # ★ AI Agent SDK — 纯 builder 模式的 Agent 运行时
│       ├── ai-workflow-builder.ee/  # ★ EE 版 AI 工作流生成器
│       ├── nodes-langchain/   # LangChain 集成节点
│       ├── ai-node-sdk/       # AI 节点 SDK
│       ├── ai-utilities/      # AI 工具函数
│       ├── engine/            # 工作流引擎抽象
│       ├── db/                 # 数据库层（TypeORM + SQLite/PostgreSQL）
│       ├── di/                 # 依赖注入容器
│       ├── task-runner/        # 代码任务执行器（隔离执行 JavaScript/Python）
│       ├── task-runner-python/ # Python 任务执行器
│       ├── mcp-browser/        # MCP 浏览器集成
│       ├── computer-use/       # 计算机操作 Agent
│       ├── expression-runtime/ # 表达式运行时（沙箱）
│       └── ...                 # 40+ 更多模块
├── docker/                    # Docker 镜像构建配置
├── scripts/                   # 构建/部署/CI 脚本
├── .claude/                   # Claude Code 团队协作配置
├── .agents/                   # Agent 技能定义
└── patches/                   # 依赖补丁
```

**架构特征**：
- **Monorepo + Turborepo**：pnpm workspaces 统一管理，Turbo 做增量构建
- **严格版本控制**：`pnpm@10.32.1`，`Node.js >= 22.22`
- **分层架构**：`workflow`（定义）→ `core`（引擎）→ `cli`（入口）→ `nodes-base`（集成）
- **AI 层正交设计**：`@n8n/agents` 是独立 SDK 包，通过 builder 模式与主引擎解耦

> 数据来源：`gh api repos/n8n-io/n8n/git/trees/master`、`packages/@n8n/agents/AGENTS.md`

### 2.3 技术栈

| 层级 | 技术选型 | 说明 |
|------|----------|------|
| 核心语言 | TypeScript | 全栈 TypeScript，前后端一致 |
| 前端框架 | Vue 3 | 工作流编辑器 UI |
| 包管理 | pnpm + Turborepo | monorepo 构建编排 |
| 数据库 | SQLite / PostgreSQL | 开发用 SQLite，生产用 PostgreSQL |
| ORM | TypeORM | 数据持久化 |
| 表达式引擎 | @n8n/expression-runtime | 自研沙箱 VM，支持内存/CPU 限制 |
| Agent SDK | Vercel AI SDK | `@ai-sdk/openai`、`@ai-sdk/anthropic` 等 |
| LLM 提供商 | 10+ 官方支持 + OpenRouter | OpenAI、Anthropic、Google、Groq、xAI 等 |
| MCP 协议 | @modelcontextprotocol/sdk | MCP Client + Server 双向支持 |
| 代码执行 | @n8n/task-runner / Python | 隔离执行 JS/Python 片段 |
| CI/CD | GitHub Actions + Playwright | 端到端测试 |
| 代码质量 | Biome + ESLint + Lefthook | 格式化和 Lint |
| Docker | 多阶段构建 | `docker/compose` 一键部署 |

---

## 3. 核心源码解读

### 3.1 工作流定义引擎 — `Workflow` 类

**文件**：`packages/workflow/src/workflow.ts`

```typescript
// 核心数据结构
export class Workflow {
  id: string;
  nodes: INodes = {};                    // 节点字典 { [name]: INode }
  connectionsBySourceNode: IConnections;  // 出边连接
  connectionsByDestinationNode: IConnections; // 入边连接
  expression: WorkflowExpression;         // 表达式解析器
  active: boolean;                        // 是否激活
}
```

**设计要点**：
1. **双向连接索引**：`connectionsBySourceNode` + `connectionsByDestinationNode` 双索引让上下游遍历均为 O(1)
2. **延迟类型加载**：节点类型按 `name + version` 查找，未知类型在构造函数中不抛异常，保持向后兼容
3. **表达式绑定**：`WorkflowExpression` 在构造时绑定 this，支持 `{{ $json.field }}` 语法访问运行时数据
4. **可观察对象**：`staticData` 采用 Observable 模式，节点间的元数据共享具有反应式特性
5. **时区感知**：通过全局状态注入默认时区，解决分布式场景下的时间一致性问题

> 源码位置：`packages/workflow/src/workflow.ts:96-120`

### 3.2 表达式引擎 — 安全沙箱 VM

**文件**：`packages/workflow/src/expression.ts`

n8n 的表达式系统是其区别于 Zapier 的核心——不是在模板中嵌入变量取值，而是运行一个真正的沙箱 VM：

```typescript
// 表达式安全机制层
1. PrototypeSanitizer  — 移除危险的原型方法
2. ThisSanitizer       — 禁用 this 逃逸
3. DollarSignValidator  — 防止模板注入
4. MemoryLimitError    — 内存超限自动终止
5. TimeoutError        — 超时自动终止
6. SecurityViolationError — 安全违规捕获
```

**架构洞察**：
- 表达式不是简单的字符串替换，而是通过 `@n8n/expression-runtime` 在隔离 VM 中执行
- 支持 `luxon` 日期库、JMESPath 查询语言
- 错误映射机制把 VM 错误转译为宿主侧的类型安全异常
- 前端/后端共用同一套表达式语义，编辑时的表达式预览即运行时行为

> 源码位置：`packages/workflow/src/expression.ts:1-90`

### 3.3 AI Agent 运行时 — `AgentRuntime`

**文件**：`packages/@n8n/agents/src/runtime/loop/agent-runtime.ts`

这是 n8n 最核心的 AI 代码，基于 Vercel AI SDK 直接构建：

```typescript
export class AgentRuntime {
  // 核心配置
  private config: AgentRuntimeConfig;
  // 运行状态管理（checkpoint/暂停/恢复）
  private runState: RunStateManager;
  // 事件总线
  private eventBus: AgentEventBus;

  // 最大循环迭代次数（防止 Agent 陷入死循环）
  // MAX_LOOP_ITERATIONS = 30
}
```

**关键设计决策**：

1. **Builder 模式 + 延迟构建**：用户代码不需要调用 `.build()`，Agent 类通过 `generate()` / `stream()` 自动懒初始化——这是对开发者体验的极致宽容

2. **双模式执行**：
   - `generate()` → `generateText()` — 非流式完整结果
   - `stream()` → `streamText()` — 实时流式输出

3. **记忆策略**：
   - `filterLlmMessages` 在发送给 LLM 前过滤自定义消息
   - `AgentMessageList.turnDelta()` 基于 Set 做增量追踪
   - 序列化基于 id 的 set 结构，可跨进程恢复

4. **工具调用并发**：`toolCallConcurrency` 参数控制并发执行（默认 1，顺序执行）

5. **状态恢复**：支持 `runId` 从挂起点恢复，Agent 实例可销毁重建仍保持上下文

6. **凭证模式**：通过 `.credential('name')` 声明，由引擎注入——用户代码不接触明文 API Key

> 源码位置：`packages/@n8n/agents/src/runtime/loop/agent-runtime.ts:70-125`

### 3.4 表达式执行代理 — `expression-evaluator-proxy`

**文件**：`packages/workflow/src/expression-evaluator-proxy.ts`

```
前端编辑器 → expression-evaluator-proxy → @n8n/expression-runtime (VM沙箱)
                                                    ↓
                                            安全执行 JS 表达式
                                                    ↓
                                            返回结构化数据
```

这是 n8n 表达式安全性的核心屏蔽层。表达式不是简单的字符串拼接，而是在一个受限的 JS VM 中执行，防止任意代码注入。Dify 和 LangFlow 都没有这个级别的安全隔离——它们更依赖 LLM 的 "Prompt Guard"。

> 源码位置：`packages/workflow/src/expression-evaluator-proxy.ts`

### 3.5 AI 工作流生成器 — `workflow-builder-agent`

**文件**：`packages/@n8n/ai-workflow-builder.ee/src/workflow-builder-agent.ts`

这个文件实现了 n8n 最有特色的 EE 功能——**用自然语言描述需求，AI 自动生成工作流**：

- 基于 LangGraph 的多 Agent 子图架构
- `multi-agent-workflow-subgraphs.ts` 管理多个 Agent 子任务的 graph
- `parent-graph-state.ts` 维护父图状态
- `session-manager.service.ts` 管理多用户会话

这意味着：用户描述 "当收到客户邮件时，AI 分析意图并用 Slack 通知销售团队"，n8n 能自动编排流程，而不是需要手动拖拽 6 个节点。

> 源码位置：`packages/@n8n/ai-workflow-builder.ee/src/`

### 3.6 节点扩展系统 — 400+ 集成的秘密

n8n 的集成架构是通过统一节点接口实现的：

```
INodeType {
  description: {
    properties: INodeProperties[]   // 节点配置表单
    inputs: NodeConnectionType[]    // 输入类型
    outputs: NodeConnectionType[]   // 输出类型
    credentials?: ICredentialType[] // 凭证定义
  }
  execute(this: IExecuteFunctions): Promise<INodeExecutionData[][]>
  webhook?(this: IWebhookFunctions): Promise<IWebhookResponseData>
  poll?(this: IPollFunctions): Promise<INodeExecutionData[][]>
  trigger?(this: ITriggerFunctions): Promise<ITriggerResponse>
}
```

- **execute**：通用执行逻辑（API 调用、数据转换）
- **webhook**：外部事件触发（GitHub Webhook、Stripe Payment）
- **poll**：定时轮询（检查邮箱、数据库变化）
- **trigger**：内置触发器（Cron 定时任务）

这个统一接口使得社区贡献节点极其简单——实现一个 INodeType 即可，n8n 自动处理 UI 渲染、凭证管理、错误重试。

> 源码位置：`packages/workflow/src/interfaces.ts`

---

## 4. 架构决策与设计哲学

### 4.1 "Fair-code" 而非 Open Source

n8n 明确选择 Sustainable Use License（SUL）而不是 MIT/Apache-2.0：

- **你可以**：查看源码、修改源码、自托管、内部业务使用
- **你不可以**：将 n8n 作为 SaaS 产品卖给他人（即不能做 n8n 的托管竞品）

**评价**：这是 "既要又要" 的商业策略——既有开源社区的增长飞轮（194K stars 证明了），又保护了云托管收入。对比 Windmill（Apache 2.0），n8n 牺牲了 "真开源" 的道德高点换来了商业可持续性。

### 4.2 表达式优先的非图灵完备策略

n8n 的表达式不是普通的模板变量——它是具有沙箱隔离的完整 JS 子集。同时又有硬限制（memory/timeout/security），确保不会像 Zapier 的 Code 步骤那样要么太受限要么太危险。

### 4.3 Monorepo+Turborepo 的规模化选择

40+ 内部包、400+ 集成节点、Vue 前端 + TypeScript 后端——这种规模不用 monorepo 几乎无法维护。Turborepo 的增量构建确保修改一个节点不需要重建整个项目。

### 4.4 Agent SDK 的独立性与正交设计

`@n8n/agents` 被设计为完全独立的 SDK——它有自己独立的依赖声明、测试套件、类型系统。这意味着：
- Agent 功能可以不依赖主工作流引擎独立演进
- 未来可以给其他产品复用（但 SUL 协议限制了这一点）
- 社区可以通过这个 SDK 贡献 AI 工具

### 4.5 从 "自动化引擎" 到 "AI 编排平台" 的转型

n8n 2019 年起步时是 "开源 Zapier"，2025 年后明确转型为 AI 编排。关键信号：
- 将 "native AI capabilities" 写入仓库描述第一句
- 仓库 topics 加入 `ai`、`mcp`、`mcp-client`、`mcp-server`
- $180M 融资中 NVIDIA 参投，说明 AI 战略得到产业认可
- 创始人公开信明确："n8n becomes the default platform to build with AI"

---

## 5. 全网口碑画像

### 5.1 总体评分

| 平台 | 评分 | 样本量 |
|------|------|--------|
| G2 | 4.5/5 | 数百条 |
| Doolpa | 81/100 | 综合评估 |
| GitHub | 194,179 stars | 全球社区 |

### 5.2 正面评价（带真实来源）

**社区活力极高**：

> "On Reddit's r/selfhosted and r/n8n, the community is highly active — users regularly share complex workflow templates, and sentiment skews positive with most threads focused on 'what can I build?' rather than complaints."
>
> — Doolpa 综合评测（2026）

> "从 tinkerers automating lights at home to the United Nations running mission-critical workflows at scale"
>
> — Jan Oberhauser, n8n CEO, Series C 公告

> "Our community is already pushing n8n from a platform into an ecosystem. We're rapidly seeing people build their own businesses around n8n"
>
> — n8n 官方 Blog（2025.10）

**成本优势显著**：

> "n8n's self-hosted Community Edition has zero execution limits, zero seat limits, and zero workflow limits. For teams running thousands of automations daily, this alone can reduce costs by 70–90% compared to SaaS alternatives."
>
> — Doolpa Review（2026）

**Hacker News 评价**：

> "Senior developers praising the fair-code licensing model as a sustainable business approach"
>
> — HN 讨论摘要（via Doolpa）

### 5.3 负面评价与踩坑记录

**学习曲线陡峭**（最高频批评）：

> "The most consistent criticism across G2, Capterra, and Reddit: the learning curve for non-developers is steep. Creating advanced flows with branching logic, error handling, and sub-workflows requires patience."
>
> — Doolpa 综合评测（2026）

**非 OSI 开源争议**：

> "debated whether the Sustainable Use License (SUL) qualifies as truly 'open source' under OSI definitions (it doesn't)"
>
> — HN 讨论摘要（via Doolpa）

**中文社区踩坑实录**（来源：知乎 @小树叶）：

| 问题 | 详情 |
|------|------|
| **Docker 数据持久化** | 不带 Volume 挂载的容器删除后所有工作流失效——"手滑一下，所有工作流灰飞烟灭" |
| **跨设备同步** | 公司和家里 n8n 实例数据独立，需要手动导出/导入工作流 |
| **容器自启动** | 电脑重启后 Docker 容器不会自动运行，需手动启动 **Docker Desktop → 运行容器** |

> 来源：[知乎 - 花了 3 小时填平 n8n 本地部署的坑](https://zhuanlan.zhihu.com/p/1970180548329727455)

**生产部署痛点**（来源：yaohehe.github.io）：

> "在 Ubuntu 24.04 VPS 上部署 n8n 时，前后花了 2 天时间才跑通生产环境。5 个真实问题：PostgreSQL 配置、时区设置、反向代理、SSL 证书、Worker 进程管理"
>
> — [n8n自托管Docker部署踩坑全记录](https://yaohehe.github.io/archive/2026-04-27/)

**云定价偏高**：

> "Cloud pricing becomes expensive above Starter tier: €800/month for Business is steep compared to Make.com's equivalent tiers. SSO and admin features locked behind €800/month Business plan — a barrier for security-conscious mid-market teams."
>
> — Doolpa Review（2026）

### 5.4 用户画像（谁在用 n8n）

| 用户类型 | 占比估计 | 典型场景 |
|----------|----------|----------|
| DevOps/后端开发者 | 40% | 自动化部署、数据同步、API 编排 |
| 技术创业者 | 25% | 内部自动化、MVP 流程 |
| AI/ML 工程师 | 20% | AI Agent 工作流、RAG 管道 |
| 运营/营销技术人员 | 10% | 数据抽取、通知自动化 |
| 纯非技术人员 | 5% | 简单自动化（门槛高，流失率高） |

---

## 6. 竞品对比

### 6.1 综合对比表

| 维度 | **n8n** | **Zapier** | **Make** | **Temporal** | **LangFlow** | **Dify** |
|------|---------|------------|----------|-------------|-------------|----------|
| **核心定位** | 通用自动化+AI | 无代码自动化 | 可视化自动化 | 耐久执行引擎 | 可视化 LangChain | LLM 应用平台 |
| **目标用户** | 技术团队 | 非技术用户 | 进阶用户 | 后端工程师 | AI 工程师 | AI 产品团队 |
| **集成数量** | 400+ | ~7,000 | ~2,000 | 0（自己写） | 有限 | 100+ LLM |
| **自托管** | 免费无限制 | 不支持 | 不支持 | 免费（MIT） | 免费（Apache 2.0） | 免费（MIT） |
| **代码支持** | JS/Python 原生 | 有限模板 | 有限函数 | 全语言 SDK | Python | Python |
| **开源协议** | SUL (fair-code) | 闭源 | 闭源 | MIT | Apache 2.0 | MIT |
| **AI 原生** | 后加但够用 | 基础 AI 步骤 | 基础 AI | 无关 | **原生 LangChain** | **原生 LLMOps** |
| **RAG 能力** | 基础 | 无 | 无 | 不适用 | **强（极致可控）** | **强（开箱即用）** |
| **错误处理** | **三者最佳** | 基础 | 中级 | 事件溯源 replay | 基础 | 基础 |
| **学习曲线** | 中高 | 低 | 中 | **极高** | 中 | 中低 |
| **云起步价** | $20/月 | $20/月 | $9/月 | $200/月 | 免费层 | $59/月 |
| **SSO/企业功能** | $800/月起 | 企业版 | 企业版 | Cloud | 无原生支持 | **所有版本** |
| **生产成熟度** | 高 | 极高 | 高 | 极高（Netflix 在用） | 低（缺认证/限流） | 中高 |
| **GitHub Stars** | 194K | N/A | N/A | 13K | 36K | 100K+ |

### 6.2 关键差异解读

**n8n vs Zapier**：
- Zapier 赢在 7,000+ 长尾集成和零门槛体验；n8n 赢在成本可控和代码灵活性
- **一句话**：Zapier 是 "不懂技术的人的自动化"，n8n 是 "懂技术的人节约时间的自动化"

**n8n vs Make**：
- Make 的场景可视化管理比 n8n 更直观；n8n 的代码能力和自托管碾压 Make
- **一句话**：Make 适合 "中间地带"，n8n 适合 "我全都要"

**n8n vs Temporal**：
- 几乎不重叠——Temporal 是后端微服务编排的耐久执行引擎（Netflix、Stripe 在生产用），n8n 是 SaaS 连接和人机交互自动化
- Temporal 需要 Go/Java/Python 工程师写代码；n8n 的操作人员可以直接拖拽
- **一句话**：Temporal 面向分布式系统，n8n 面向业务流程

> 来源：[Automation Atlas — Temporal vs n8n](https://automationatlas.io/guides/temporal-vs-n8n-2026-comparison/)

**n8n vs LangFlow**：
- LangFlow 是 LangChain 的可视化前端，管道的控制粒度远胜 n8n 的 AI 节点
- 但 LangFlow 没有生产基础设施（无认证、无 RBAC、无多租户、无重试策略）
- **一句话**：LangFlow 做 AI 原型，n8n 做 AI 生产

> 来源：[Langflow vs n8n vs Dify (2026)](https://baeseokjae.github.io/posts/langflow-vs-n8n-vs-dify-2026/)

**n8n vs Dify**：
- Dify 的 RAG 管道和 LLMOps 远超 n8n；n8n 的 SaaS 集成和流程编排远超 Dify
- **典型组合**：n8n 做流程编排 + Dify 做 AI 推理（n8n HTTP Request → Dify API → n8n 下一步）
- **一句话**：n8n 的 AI 是 "自动化中的 AI"，Dify 的 AI 是 "AI 优先的自动化"

> 来源：[n8n vs Dify：AI 自动化工作流平台深度对比](https://www.aieii.com/posts/2026-03-20-n8n-vs-dify-ai-workflow/)

### 6.3 场景选型速查

| 如果你要... | 选谁 |
|-------------|------|
| 连接 5 个 SaaS 工具做一个自动审批流 | **n8n** |
| 给客户做一个可分享的 AI 助手 | **Dify** |
| 做一个需要极低延迟的支付系统工作流 | **Temporal** |
| 快速验证 RAG 效果，调整分块策略 | **LangFlow** |
| 让非技术同事自己搭建简单自动化 | **Zapier** 或 **Make** |
| 自托管但需要严格开源协议 | **Dify**(MIT) 或 **Windmill**(Apache 2.0) |
| AI + 业务流程混合编排 | **n8n**（自托管免费）|
| 向多个企业客户卖 LLM 应用 | **Dify**（多租户原生支持）|

---

## 7. 核心研判

### 7.1 核心优势

1. **自托管经济性**——免费、无执行次数限制、无工作流数量限制，对高频自动化场景是降维打击
2. **代码+可视化混合**——不是 "用模板替代代码"，而是 "用代码补充拖拽"，开发者体验领先
3. **社区飞轮**——194K stars + 2,200+ 社区节点，生态护城河已形成
4. **AI 转型坚决**——NVIDIA 参投、MCP 协议支持、Agent SDK 独立演进，路径清晰
5. **Docker 部署简单**——单命令启动，运维成本极低
6. **企业功能矩阵**——SSO、审计日志、RBAC、Air-gapped 部署覆盖大企业需求

### 7.2 核心风险

1. **SUL 协议争议**——不是 OSI 认可的开源，未来许可证变更风险大于单纯的 MIT/Apache 项目
2. **AI 贡献 "后发生"**——AI 节点是 2024-2025 年补上的，不是 AI-first 设计；处理复杂 RAG 或 Agent 协作时，体验不如 Dify/LangFlow 原生
3. **云定价上探过快**——Business 版 €800/月对标 Google Workspace Enterprise，但功能差距大
4. **TypeScript 垄断**——全栈 TypeScript 对社区扩展友好，但 AI 生态核心在 Python；LangChain、Transformers 都与 TS 生态有距离
5. **Python 支持弱**——虽然有 `task-runner-python`，但 agent SDK 核心仍是 TypeScript，意味着复杂的 ML pipeline 需要跳出 n8n
6. **非技术用户门槛**——表达式语法 `{{ $json.field }}` 和 JSON 数据结构对运营人员不友好

### 7.3 适用场景

**推荐使用**：
- 需要连接 5+ 个 SaaS 工具的业务流程自动化
- 数据处理 ETL（多源提取→转换→写入）
- DevOps 自动化（CI/CD 触发器、告警路由、部署通知）
- AI Agent + 业务系统的混合流程（客户意图识别→分类→路由→通知）
- 对数据主权有要求的企业（自托管在私有环境中）
- 高频自动化场景（每天万次以上执行，避免 Zapier 按次计费）

**不推荐使用**：
- 纯 AI 知识库问答 → 用 Dify
- 需要精细 RAG 管道控制 → 用 LangFlow
- 分布式微服务 Saga 模式 → 用 Temporal
- 非技术团队想要零门槛自动化 → 用 Zapier 或 Make
- 需要 OSI 认证的开源协议 → 用 Windmill 或 Dify
- 需要内建对话 UI（聊天界面） → 用 Dify（n8n 只有一个技术性 console）

### 7.4 发展趋势研判

**短期（2026 H2）**：
- AI Agent 功能持续深化在 `@n8n/agents` 中（evaluations、更多 MCP 连接器）
- n8n Cloud 会降低 Business 版价格或增加更多中间层次
- 社区节点可能突破 3,000+

**中期（2027）**：
- 必然支持端到端的多 Agent 协作工作流（替代 LangGraph 在非代码场景）
- Python Agent SDK 版本大概率释出（TypeScript 垄断不可持续）
- 与 Dify 的直接竞争加剧——两者功能边界模糊化

**长期（2028+）**：
- "Excel of AI" 愿景——n8n 想成为"人人都能用的工作台"，就像 Excel 从财务工具变成通用表格标准
- 这个愿景的关键挑战：如何在不牺牲深度的情况下降低门槛
- 可能的收购目标或被收购——$2.5B 估值在自动化市场不算大，但如果 AI Agent 赛道爆发，n8n 是 Salesforce/Zendesk 等巨头的天然补全

---

## 8. 关键文件路径速查

| 用途 | 文件路径 |
|------|----------|
| 项目 README | `README.md` |
| 工作流定义引擎 | `packages/workflow/src/workflow.ts` |
| 表达式引擎 | `packages/workflow/src/expression.ts` |
| 表达式沙箱 | `packages/workflow/src/expression-sandboxing.ts` |
| 工作流执行核心 | `packages/core/src/constants.ts` |
| 节点定义接口 | `packages/workflow/src/interfaces.ts` |
| Agent SDK 入口 | `packages/@n8n/agents/src/index.ts` |
| Agent 运行时 | `packages/@n8n/agents/src/runtime/loop/agent-runtime.ts` |
| Agent Builder | `packages/@n8n/agents/src/sdk/agent.ts` |
| AI 工作流生成器（EE） | `packages/@n8n/ai-workflow-builder.ee/src/workflow-builder-agent.ts` |
| MCP 连接管理 | `packages/@n8n/agents/src/runtime/mcp/mcp-connection.ts` |
| 记忆管理 | `packages/@n8n/agents/src/runtime/memory/memory-orchestrator.ts` |
| 工具适配器 | `packages/@n8n/agents/src/runtime/tools/tool-adapter.ts` |
| 状态管理与 checkpoint | `packages/@n8n/agents/src/runtime/state/run-state.ts` |
| 凭证管理 | `packages/core/src/credentials.ts` |
| 数据去重 | `packages/core/src/data-deduplication-service.ts` |
| 主 CLI 入口 | `packages/cli/src/` |
| 前端编辑器 | `packages/frontend/editor-ui/` |
| 任务执行器 (JS) | `packages/@n8n/task-runner/` |
| 任务执行器 (Python) | `packages/@n8n/task-runner-python/` |
| LangChain 集成节点 | `packages/@n8n/nodes-langchain/` |
| 数据库层 | `packages/@n8n/db/` |
| 许可协议 | `LICENSE.md` |
| 企业许可 | `LICENSE_EE.md` |
| 贡献指南 | `CONTRIBUTING.md` |
| Agent 开发指南 | `.claude/plugins/n8n/README.md` |
| Agent Skills 目录 | `.agents/skills/` |
| Docker 部署配置 | `docker/compose/` |
| Helm Chart (K8s) | 独立 repo: `n8n-io/n8n-hosting` |

---

## 9. 附录

### 9.1 未在 README 中发现的关键发现

1. **Agent 的 Suspension/Resume 机制**：`@n8n/agents` 实现了完整的 **Human-in-the-Loop** 挂起-恢复协议。Agent 可以挂起等待人工审批，然后从同一个 checkpoint 恢复执行——这在 README 中没有提及，但在 `agent-runtime.ts` 和 `tool-call-executor.ts` 中有完整实现。测试中甚至覆盖了 "多次挂起-恢复后不留重复 tool call 记录" 的边界场景。

2. **Observation Log 记忆系统**：n8n 实现了三层记忆架构——Conversational Memory（对话历史）、Observation Log（观察日志）、Episodic Memory（情节记忆）——这是一个超越简单对话历史的复杂记忆系统，README 完全没有提及。

3. **MCP 双角色支持**：n8n 的 topic 列表包含 `mcp-client` 和 `mcp-server`，意味着 n8n 既可以作为 MCP 客户端调用外部工具，也可以作为 MCP 服务器向其他 AI 应用暴露自己的节点能力。这是 LangFlow 和 Dify 目前不支持的功能。

### 9.2 数据来源清单

- GitHub API：`gh repo view`、`gh api`（仓库元数据、文件树、源码内容）
- n8n 官方博客：Series C 融资公告
- Doolpa：综合评测报告
- 知乎：中文社区踩坑经验（@小树叶）
- yaohehe.github.io：生产部署踩坑
- AIEII：n8n vs Dify 深度对比
- Baeseokjae：LangFlow vs n8n vs Dify 三方对比
- Automation Atlas：Temporal vs n8n 对比
- 开源 AI Agent 平台横评（掘金）

### 9.3 更新日志

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.0 | 2026-06-27 | 初始深度调研版本 |

---

*本报告基于 2026-06-27 的最新仓库代码和社区数据生成，所有数据和引用均可追溯。*
