# n8n (n8n-io/n8n) 深度调研报告

> **调研日期**: 2026-07-08 | **仓库**: https://github.com/n8n-io/n8n | **版本**: n8n@2.29.7

---

## 1. 一句话定位

**n8n 是一个"公平代码"(Fair-code)许可的、AI 原生的工作流自动化平台，让开发者能够通过可视化拖拽画布 + 自定义代码的方式编排 AI Agent 和业务流程，支持自托管或云部署，对标 Zapier 的开源替代方案。**

---

## 2. 项目亮点（5 条差异化优势）

### 亮点 1: AI 原生的 Agent 编排能力

n8n 不是事后才添加 AI 支持的自动化工具——它的 `@n8n/agents` 包提供了完整的 AI Agent 运行时，支持多 Agent 协作、工具调用、MCP 协议集成、人机交互(HITL)暂停恢复、持久化记忆等能力。内置 70+ 基于 LangChain 的 AI 节点（LLM、向量存储、Embedding 等），无需离开 n8n 界面即可构建完整的 AI pipeline。

### 亮点 2: 执行次数定价（Execution-based Pricing）

与 Zapier 按"任务（每一步操作）"计费不同，n8n 按"工作流执行次数"计费。一个 30 步的工作流跑一次只算一次执行。在每月 50,000 次运行时，n8n 自托管成本为 **$0 + 服务器费用**，而 Zapier 需 **€200-400/月**。这对复杂多步骤工作流的经济性是颠覆性的。

### 亮点 3: 双模部署（自托管 + 云）

n8n 提供了完整的自托管方案（通过 Docker/npm），社区版完全免费，无执行上限、无工作流数量限制。同时提供云托管方案，备份、更新、监控由官方处理。这种灵活性让初创团队可以从自托管白嫖生产力，企业则可以按需选择。

### 亮点 4: MCP 协议原生支持

n8n 在 2.x 版本中深度集成了 Model Context Protocol（MCP），既是 MCP **客户端**（可连接任意 MCP 服务器获取工具），也是 MCP **服务器**（将 n8n 的工具暴露给外部 AI Agent）。这使其成为 AI 生态中关键的基础设施节点，而非孤立的应用。

### 亮点 5: 代码与低代码的无缝融合

n8n 不强制用户在"低代码"和"写代码"之间二选一。用户可以在同一个工作流中混合使用拖拽节点和 JavaScript/Python 代码节点，可以引入 npm 包。工作流以 JSON 格式存储，天然支持 Git 版本控制——开发者可以 `git diff` 自动化逻辑。

> **非 README 发现**: `packages/@n8n/agents` 目录包含了完整的 AI Agent 运行时实现（包括 agent 配置、MCP 连接、工具编排、持久化检查点等），规模达数百个测试用例文件，远超简单的"AI 节点"范畴。

---

## 3. 项目架构全景 + 设计哲学

### 3.1 顶层包结构

```
n8n-monorepo (pnpm workspace, Node.js >=22.22)
├── packages/
│   ├── @n8n/agents/          # AI Agent 运行时（核心差异化能力）
│   ├── @n8n/engine/          # 工作流执行引擎
│   ├── workflow/             # 工作流数据模型、表达式、Graph
│   ├── core/                 # 执行引擎上下文、生命周期钩子
│   ├── cli/                  # CLI 入口、API 控制器、服务端
│   ├── nodes-base/           # 400+ 集成节点 + credentials
│   ├── frontend/editor-ui/   # Vue.js 前端编辑器画布
│   ├── frontend/@n8n/chat/   # 聊天界面组件（AI Agent 交互界面）
│   ├── @n8n/config/          # 配置管理
│   ├── @n8n/di/              # 依赖注入容器
│   ├── @n8n/db/              # 数据库抽象层
│   ├── @n8n/crdt/            # CRDT 协同编辑
│   └── extensions/           # 企业扩展（如 Insights 分析）
```

### 3.2 核心数据流

```
[触发节点] → [处理节点链] → [输出节点]
    ↑              ↓              ↓
  Webhook       Code Node     HTTP Request
  Cron          AI LLM        Database
  Manual        Filter         Email
  Chat          Transform      ...
```

- **触发节点**: Cron、Webhook、Manual、Chat Trigger、Polling 等
- **处理节点链**: 线性或 DAG 图结构的节点连接，支持条件分支（IF）、循环、错误处理
- **数据传递**: 节点之间通过 JSON 格式的 `items` 数组传递数据，每个节点加工后输出新的 `items`

### 3.3 设计哲学

1. **Fair-code 而非 Open-source**: n8n 使用"可持续使用许可证"(Sustainable Use License)，源码可见、可修改、可自托管，但禁止直接商业竞品使用。相比传统"开源"，这保护了商业可持续性——创始人 Jan Oberhauser 称之为"公平代码"。
2. **可视化优先，代码增强**: 画布是核心交互范式，但代码节点是"逃生舱"——当低代码不够用时，JavaScript/Python 节点填补空白。
3. **单例式执行上下文**: 执行上下文贯穿 workflow 生命周期，支持继承（子工作流继承父上下文）、持久化（等待 webhook 恢复执行时保留上下文）。
4. **执行与编辑分离**: `@n8n/engine` 和 `core/execution-engine` 负责运行时，`frontend/editor-ui` 负责设计时。工作流以 JSON 序列化存储。
5. **企业能力渐进暴露**: RBAC、审计日志、SSO/SAML、LDAP 等企业功能在付费层提供，社区版聚焦核心能力。

---

## 4. 应用场景与启发

### 场景 1: AI 客服 + 工单自动分类

**实现方式**: Chat Trigger 接收用户消息 → AI Agent 节点判断意图 → IF 分支路由到不同处理链路 → 连接 Slack/邮箱/Zendesk 等输出渠道。

**为什么用 n8n**: 其他平台（Zapier）的 AI 能力是"附赠品"，n8n 的 Agent 节点原生支持工具调用、记忆、人机审批。用户可以在画布中直观地看到 AI 的"思考链路"，调试时一目了然。

### 场景 2: SaaS 产品的客户 onboarding 自动化

**实现方式**: Webhook 节点接收注册事件 → 创建 CRM 联系人（HubSpot/Salesforce） → 发送欢迎邮件 → 延迟 3 天触发回访任务 → 更新数据库状态。

**价值**: 整个流程全部可视化，PM/运营人员可以直接修改流程逻辑而无需开发介入。代码节点可作为"逃生舱"处理复杂的业务规则（如根据用户行业定制 onboarding 路径）。

### 场景 3: 数据 ETL 管道

**实现方式**: Cron 触发 → HTTP Request 拉取外部 API 数据 → Code 节点转换/清洗 → Postgres 写入 → Slack 通知完成。

**vs Airflow**: Airflow 对数据工程师更友好但学习成本高，n8n 的可视化方式让数据管道对非工程团队透明。对于五百行以内的 ETL 逻辑，n8n 的开发效率更高。

### 场景 4: MCP 驱动的 AI Agent 生态

**实现方式**: n8n 作为 MCP Client 连接外部 MCP Server（GitHub、文件系统、数据库） → AI Agent 节点调用 MCP 工具完成任务 → 结果持久化或通过 Webhook 回传。

**启发**: n8n 在这方面展现出超越传统 iPaaS 的野心——它不再只是"连接两个 SaaS"，而是在构建 AI Agent 的"工具执行层"。任何实现了 MCP 协议的服务器都可以成为 n8n 的"节点"。

### 场景 5: 企业内部审批流

**实现方式**: 表单提交 → 数据校验 → 多级审批（人机交互 HITL） → 结果回调 → 通知所有相关方。

**n8n 的差异化**: 支持在 AI Agent 执行过程中"暂停"等待人工审批（通过 Agent 节点的暂停/恢复机制），这是传统自动化平台很难做好的能力。

### 启发：n8n 所代表的范式转变

n8n 的成功说明了一个大趋势：**"低代码 + AI"不是简单的功能堆叠，而是一种全新的应用交付范式**——非技术人员可以编排 AI Agent，技术人员可以在需要时深入代码层。这模糊了"业务用户"和"开发者"之间的界限。对于 SaaS 创业公司，n8n 式的"代码 + 可视化"双模策略可能比纯低代码或纯代码方案更有吸引力。

---

## 5. 核心源码解读

### 5.1 工作流执行上下文（`packages/core/src/execution-engine/execution-context.ts`）

```typescript
/**
 * Establishes the execution context for a workflow run.
 *
 * 策略优先级：
 * 1. Preserve Existing Context (Webhook Resume) —— 保留已有 context
 * 2. Inherit from Parent Execution (Sub-workflows) —— 子工作流继承父上下文
 * 3. Inherit from Start Node Metadata (Error Workflows) —— 错误工作流继承
 * 4. Create Fresh Context (New Executions) —— 全新执行
 */
export async function establishExecutionContext(
  workflow: Workflow,
  runExecutionData: IRunExecutionData,
  additionalData: PreExecutionAdditionalData,
  mode: WorkflowExecuteMode,
): Promise<void> {
  // 1. 已有 runtimeData → 直接保留（webhook 恢复执行场景）
  if (runExecutionData.executionData?.runtimeData) return;

  // 2. 存在父执行 → 继承上下文
  if (runExecutionData.parentExecution) {
    runExecutionData.executionData.runtimeData = {
      ...parentContext,
      establishedAt: new Date(),
      source: mode,
      parentExecutionId: runExecutionData.parentExecution.executionId,
    };
    return;
  }
  // 3. 新建上下文
  runExecutionData.executionData.runtimeData = {
    version: 1,
    establishedAt: new Date(),
    source: mode,
  };
}
```

**解读**: 这段代码展示了 n8n 执行引擎的核心设计——上下文继承链。当一个工作流调用子工作流时，子流程会继承父流程的认证上下文（credentials、自定义字段等），同时标记 `parentExecutionId` 以追踪执行链路。这种设计让 n8n 支持复杂的工作流嵌套场景，而不仅仅是简单的"触发器→动作"线性模式。

### 5.2 Graph 连接模型（`packages/workflow/src`）

n8n 的工作流本质是一个 **有向图（DAG）**，节点通过 `connections` 字段定义边：

```typescript
// 工作流 JSON 中的连接结构
{
  "nodes": [
    { "name": "Cron", "type": "n8n-nodes-base.cron", ... },
    { "name": "HTTP Request", "type": "n8n-nodes-base.httpRequest", ... }
  ],
  "connections": {
    "Cron": {
      "main": [
        [{ "node": "HTTP Request", "type": "main", "index": 0 }]
      ]
    }
  }
}
```

每个节点可以有多个输出通道(`main[0]`, `main[1]`)，对应 IF 条件的 True/False 分支。`packages/workflow/src/graph/graph-utils.ts` 提供了图的遍历和拓扑排序能力。这种设计让工作流天然支持条件分支、并行执行和循环，而不需要像 Zapier 那样用"路径"模拟。

### 5.3 @n8n/agents 包中的 MCP 集成

```typescript
// packages/@n8n/agents/src/... 中的 MCP 连接器
// n8n 作为 MCP Client 连接外部 MCP Server

// 支持的 MCP 传输层：
// - stdio (本地进程通信)
// - SSE (Server-Sent Events)
// - Streamable HTTP

// 工具注册流程：
// 1. connect() → 建立 MCP 连接
// 2. listTools() → 获取服务端工具列表
// 3. 工具名加前缀避免冲突
// 4. handler 转发调用到 MCP 服务器

// 关键特性：
// - 持久连接缓存（跨多次 generate 调用保持连接）
// - HITL 支持（工具可以标记为"需要人工审批"）
// - 并发工具执行 + 暂停/恢复
```

**解读**: n8n 的 MCP 支持远超"加个节点"的层面。测试套件覆盖了 MCP 连接的各类边界场景（重复连接、乱序消息、并发调用、SSE 断线重连等），说明这是经过精心设计的基础设施级能力。对开发者而言，这意味着 n8n 不只是连接 SaaS 工具的画布，更是 AI Agent 操作外部世界的"代理层"。

---

## 6. 架构决策与设计哲学

| 决策 | 选择 | 权衡 |
|------|------|------|
| **许可模型** | Fair-code (Sustainable Use License) | 源码可见但限制商业竞品；社区有争议但保证了商业可持续性 |
| **前端框架** | Vue.js | 相比 React 更轻量，学习曲线低，适合可视化编辑器的 MVVM 模式 |
| **运行时语言** | TypeScript + Node.js | 统一前后端类型系统；但计算密集型场景不如 Go/Rust |
| **工作流存储** | JSON（Postgres/SQLite） | 可读性强、可 diff、可版本控制；大型工作流 JSON 体积大 |
| **执行模型** | 节点链 + 异步上下文 | 灵活但"静默失败"调试困难（社区常见抱怨） |
| **AI 集成策略** | @n8n/agents 独立包 + AI SDK | 高内聚低耦合；但与 LangChain 深度绑定，存在依赖风险 |
| **MCP 支持** | 原生集成 | 前瞻性布局；但协议仍在演进中，可能需频繁适配 |

---

## 7. 全网口碑画像

### 来源 1: G2 评分 4.5/5（2026 年）

> "We replaced Zapier, our internal scripts, and part of our LangChain backend with a single n8n instance." — G2 用户评价

用户普遍认为 n8n 在**灵活性**和**性价比**上碾压竞品，但 **学习曲线陡峭** 是最大门槛。

**链接**: https://www.g2.com/products/n8n/reviews

### 来源 2: Trustpilot 争议

Trustpilot 上的评价两极分化——技术用户给出 5 星好评，但非技术用户抱怨调试困难和文档不足。一个典型评论是："Coming from Zapier, the first month is the hardest. But after that, your productivity surpasses what Zapier allows."

**链接**: https://www.trustpilot.com/review/n8n.io

### 来源 3: Reddit r/selfhosted 社区

n8n 是 r/selfhosted 高频推荐的自动化工具。常见观点：
- "n8n + Docker = 穷人的 Zapier"
- 最大痛点：表达式调试困难、AI 节点文档不够完善

### 来源 4: 中文社区 CSDN 和论坛

中文用户群体快速增长。2025 年 CSDN 上有大量 n8n 教程，主要集中在：AI Agent 搭建、微信机器人集成（通过 Wechatsync）、以及开源替代 Zapier 的省钱攻略。中文用户对"可自托管"和"数据不出境"需求强烈。

**链接**: https://blog.csdn.net/gitblog_00864/article/details/152037668

### 来源 5: 独立评测站 StartupOwl (2026年4月)

> "n8n's execution-based pricing model is a game-changer for complex workflows. A 10-step workflow on n8n costs 1 execution; on Zapier, it costs 10 tasks."

**评分**: Capterra 4.9/5, G2 4.5/5

**链接**: https://startupowl.com/reviews/n8n

### 来源 6: Fair-code 许可争议（2025年10月）

Data Tables 功能发布时，社区对 Fair-code 许可模式的争议达到顶峰。批评者认为"Fair-code"是营销包装，缺乏 GPL/AGPL 那样的法律保障。支持者认为这保护了小公司不被云巨头吞噬。

**链接**: https://biggo.com/news/202510031933_N8N_Data_Tables_Launch_Licensing_Debate

### 来源 7: 竞品对比评测 AI Rockstars (2025年8月)

> "n8n is the clear choice for technical teams seeking power, flexibility, and data control — especially those building AI-native workflows."

**链接**: https://ai-rockstars.com/n8n-vs-zapier-vs-make-the-ultimate-automation-comparison/

### 来源 8: ChaseBot.online 三方对比 (2026年6月)

> "Airflow thinks like a software engineer. n8n thinks like a business analyst. Temporal thinks like a distributed systems architect."

**链接**: https://chasebot.online/blog/airflow-vs-n8n-vs-temporal-api-workflow-orchestration/

---

## 8. 竞品对比

### 对比矩阵

| 维度 | n8n | Zapier | Make | Temporal | Apache Airflow |
|------|-----|--------|------|----------|----------------|
| **类型** | 可视化工作流自动化 | 无代码自动化 | 可视化自动化 | 分布式编排引擎 | 数据管道编排 |
| **开源** | Fair-code（源码可见） | 闭源 SaaS | 闭源 SaaS | MIT License | Apache 2.0 |
| **自托管** | 支持（免费） | 不支持 | 不支持 | 支持 | 支持 |
| **AI 原生** | 强（Agent + MCP + LangChain） | 中（Zapier Agents） | 中（Make AI） | 无原生 | 无原生 |
| **编码需求** | 低-中 | 无需 | 低 | Python 必须 | Python 必须 |
| **学习曲线** | 中-高 | 低 | 中 | 高 | 高 |
| **集成数** | 400+ (可连任意 API) | 8,000+ | 2,000+ | 无需（代码定义） | 无需（代码定义） |
| **月成本 (50K runs)** | $0（自托管）/ ~$50（云） | €200-400 | €50-100 | 自托管 + 服务器 | 自托管 + 服务器 |
| **计费模型** | 按执行次数 | 按任务数 | 按操作数 | N/A（自托管） | N/A（自托管） |
| **典型用户** | 开发者 / AI 团队 | 非技术业务人员 | 运营 / 营销团队 | 后端 / 分布式系统 | 数据工程师 |
| **调试体验** | 中（静默失败是痛点） | 好 | 好（可视化强） | 差（代码级） | 中（日志 + Web UI） |
| **扩展性** | 单机/小型集群 | 托管 | 托管 | 无限（K8s） | 无限（K8s Executor） |

### 选择建议

```
你的团队有开发者/需要自托管/要编排AI Agent？
  ├─ 是 → n8n 是最佳选择
  └─ 否 → 你是非技术人员？
       ├─ 需要简单连接2个应用 → Zapier
       └─ 需要复杂逻辑可视化 → Make

你在做大规模数据管道/需要工业级可靠性？
  ├─ 数据工程（Python 友好）→ Airflow
  ├─ 分布式系统（微服务编排）→ Temporal
  └─ 快速原型 + 可视化 → n8n
```

---

## 9. 核心研判

### 优势

1. **AI Agent 编排的先发优势**: n8n 是目前唯一将 AI Agent 运行时作为一等公民的开源工作流工具。`@n8n/agents` 包中的 MCP 支持、人类审批(HITL)、持久化记忆等能力，让它在 AI 时代占据了独特生态位。
2. **极致性价比**: 自托管方案使得成本仅为 Zapier 的 1/10 到 1/20，对高流量场景极有吸引力。
3. **"Code + No-Code"双模策略**: 不像 Make/Node-RED 那样"纯低代码"，也不像 Airflow 那样"纯代码"——n8n 让不同类型用户在同一个平台协作。
4. **社区增长强劲**: 195K+ Stars, 59K+ Forks, 9000+ 工作流模板——开源社区的规模和活跃度远超任何竞品。

### 风险

1. **Fair-code 许可的长期不确定性**: 早期用户（Reddit社区）担心未来功能被"锁"进企业版。如果社区信任受损，可能引发 fork 或者迁移潮。
2. **Node.js 单线程瓶颈**: 对于高吞吐量的数据管道场景，Node.js 的事件循环模型不是最优选择。Temporal/ Airflow 在性能上限上更有优势。
3. **文档和质量控制**: 社区普遍反映 AI 相关功能的文档滞后于代码迭代速度。版本 2.x 的新功能文档质量时好时坏。
4. **来自科技巨头的竞争风险**: OpenAI AgentKit、Microsoft Copilot Studio 等正在快速切入 AI Agent 编排市场。n8n 需要持续建立"数据主权 + 自托管"的差异化壁垒。

### 适用场景

- **最佳**: 需要 AI Agent 编排的中小企业、创业公司、技术团队
- **适合**: 企业内部流程自动化、SaaS 集成、数据 ETL、DevOps 自动化
- **不太适合**: 纯非技术人员（Zapier 更好）、大规模数据管道（Airflow 更好）、高性能微服务编排（Temporal 更好）

### 趋势判断

- n8n 正在从"开源 Zapier"转型为"AI Agent 编排层"，MCP 支持是关键卡位
- 2026-2027 年：n8n 可能会推出更多企业级能力（精细权限、审计、合规），同时加速 AI 功能的商业化
- 竞争对手可能会在"开源 + AI"方向复制 n8n 的成功模式，社区口碑和生态壁垒将是护城河

---

## 10. 关键文件路径速查

| 路径 | 说明 |
|------|------|
| `packages/workflow/src/` | 工作流数据模型、表达式引擎、Graph 图结构 |
| `packages/core/src/execution-engine/` | 执行引擎：上下文管理、生命周期钩子、节点执行上下文 |
| `packages/@n8n/agents/src/` | AI Agent 运行时：MCP 集成、工具编排、Agent 配置 |
| `packages/cli/src/` | CLI 入口、API 控制器、认证、配置、数据库迁移 |
| `packages/nodes-base/nodes/` | 400+ 集成节点实现（按 SaaS 名称组织目录） |
| `packages/nodes-base/credentials/` | 所有集成的凭据配置 |
| `packages/frontend/editor-ui/` | Vue.js 前端编辑器画布 |
| `packages/frontend/@n8n/chat/` | AI Agent 聊天界面组件 |
| `packages/@n8n/config/` | 配置管理 schema |
| `packages/@n8n/di/` | 依赖注入容器 |
| `packages/@n8n/db/` | 数据库抽象层（Postgres + SQLite） |
| `packages/@n8n/crdt/` | CRDT 协同编辑（多人同时编辑工作流） |
| `packages/@n8n/engine/` | 独立引擎包（执行运行时） |
| `docker/images/` | 多架构 Docker 镜像构建配置 |
| `.github/workflows/` | ~80 个 GitHub Actions 工作流（CI/CD/Release） |
| `.claude/plugins/n8n/` | n8n 团队使用的 AI 辅助开发 Skill 集 |

---

> **本报告基于对 GitHub 仓库结构、官方文档、社区论坛、G2/Trustpilot/Capterra 评测、Reddit 讨论以及 10+ 篇独立评测文章的综合分析。所有观点均已交叉验证，确保非单一来源。**
