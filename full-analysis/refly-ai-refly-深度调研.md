# 🔬 refly-ai/refly — 全球首个开源 Agent Skills 构建平台深度调研

> 调研时间：2026-07-02 | ⭐ 7,416 | 🍴 719 | TypeScript

## 📌 一句话定位

Refly 是全球首个开源 Agent Skills 构建平台——通过可视化 Vibe Workflow 编辑器将企业 SOP / 业务逻辑编译为**确定性的、版本化的、可随处运行的 Agent Skills**，支持导出到 Claude Code / Cursor / Codex、部署为 MCP Server / REST API、或嵌入 Slack / 飞书作为 Bot。

## ⭐ 项目亮点

1. **"Skills 不是提示词，是可基础设施"**——核心哲学：传统 AI Agent 开发把逻辑藏在 prompt 里（脆弱、不可复用、不可测试）；Refly 把逻辑编译为结构化、版本化、原子化的 Skill，可在工作流/团队/运行时之间复用。
2. **Vibe Workflow 可视化 IDE**：不写代码，通过拖拽节点编排多步 AI 工作流（LLM 调用、API 调用、条件分支、文本处理等），同时支持底层导出为标准 Skills 文件。
3. **一次构建，到处运行**：一个 Skill 可导出为 Claude Code / Cursor / Codex 的 MCP Tool、标准的 REST API 端点、飞书/钉钉 Bot 的 webhook handler，或作为 Clawdbot 的底层能力——"编译一次，部署到处"。
4. **内置 Skill 市场**：refly-skills 仓库提供官方可执行 Skill 注册表，社区可以 import / fork / publish 自己的 Skills，形成生态飞轮。
5. **API-first 设计**：每个 Workflow 自动生成 REST API 端点，Lovable / Bolt / Cursor 等无代码/低代码平台可直接调用，是"AI 时代的 Zapier"定位。

## 🏗️ 项目架构全景

### 目录结构 + 设计哲学

```
refly/
├── apps/
│   ├── api/                  # 后端 API 服务（NestJS + TypeScript）
│   ├── web/                  # 前端 Web UI（Next.js）
│   └── ai-service/           # AI 推理服务层
├── packages/                 # 共享包
│   ├── common/               # 类型定义、工具函数
│   ├── workflow-engine/      # Vibe Workflow 执行引擎（核心）
│   ├── skill-compiler/       # Skill 编译/导出器（Claude Code / MCP / API）
│   └── skill-registry/       # Skill 注册表管理
├── docker/                   # Docker 部署配置
└── docs/                     # 文档站（docs.refly.ai）
```

**前端**：Next.js（React）— Monorepo 结构，TypeScript 全栈
**后端**：NestJS — 模块化 API 服务
**AI 服务**：独立 Python/TS 服务层处理 LLM 调用
**工作流引擎**：自定义 DAG 编排引擎，支持条件/循环/并行

### 技术栈

| 层级 | 技术选型 |
|------|---------|
| 前端 | Next.js (React), TailwindCSS, Radix UI |
| 后端 | NestJS (TypeScript), PostgreSQL (via Drizzle ORM) |
| 工作流引擎 | 自定义 DAG 引擎（packages/workflow-engine） |
| AI | OpenAI SDK / Anthropic SDK（多模型适配） |
| 部署 | Docker + docker-compose, GitHub Actions CI/CD |
| 文档 | Docusaurus (docs.refly.ai) |
| 测试 | Playwright E2E, Vitest |

### 核心理念：Skills = Infrastructure

Refly 定义了一个 Skills 的五层模型：

```
Layer 5: User Interface  — 可视化 Workflow Builder / Chat 界面
Layer 4: Workflow Runtime — DAG 引擎 + 状态管理 + 错误重试
Layer 3: Skill Compiler   — 将 Workflow 编译为 MCP / API / CLI 格式
Layer 2: Skill Registry   — 版本化存储 + 依赖管理 + 可发现性
Layer 1: Execution Runtime — Claude Code / Cursor / Codex / 自定义
```

**分层设计意味着**：在 Layer 4 构建的工作流可被 Layer 3 编译为任何 Layer 1 可执行的格式——与 Docker 的 Build → Ship → Run 理念相同。

## 💡 应用场景与启发

### 典型使用场景

1. **企业 SOP 数字化**：将标准操作流程（如"客户投诉处理流程"）编译为 Agent Skill，员工通过 Slack/飞书 Bot 一键触发执行
2. **AI 自动化中间件**：Refly Skills 作为 Claude Code / Cursor 的 MCP Server，提供结构化的企业数据查询/业务操作能力
3. **Lovable / Bolt 的 API Backend**：通过 Refly 的自动 API 生成，无代码平台可以直接调用复杂的 AI 工作流
4. **飞书/钉钉 Bot 后台**：将 FAQ、客服话术、审批流程等编译为 Skill，挂到飞书 Bot 上自动响应

### 可借鉴的解决方案模式

1. **"Vibe Workflow"作为 DSL**：Refly 的可视化工作流本质是一种领域特定语言（DSL），但通过图形界面降低了使用门槛。这个思路适用于任何需要非程序员配置复杂 AI 流程的场景。
2. **多层编译架构**：内部 DAG → 导出为多种可执行格式。这与编译器设计（IR → 多目标代码生成）惊人相似——AI 工具链正在复制传统软件工程的抽象模式。
3. **Skills 市场生态**：refly-skills 仓库是生态飞轮的关键——让社区贡献可复用的 Skill，每个新 Skill 都增加了平台的价值。

### 同类需求的可参考思路

如果你正在考虑"如何让 AI Agent 执行可靠的企业级任务"，Refly 的三层方案值得参考：
1. **第一层（Vibe Workflow）**：提供可视化/声明式的方式定义"What to do"
2. **第二层（Skill Compiler）**：自动编译为"How to execute"（MCP / API / CLI）
3. **第三层（Execution Runtime）**：在 Claude Code / Cursor 等运行时中"Where to run"

## 🧠 核心源码解读

### Workflow 执行引擎（packages/workflow-engine）

```typescript
// 核心：DAG 节点定义
interface WorkflowNode {
  id: string;
  type: 'llm_call' | 'api_call' | 'condition' | 'loop' 
      | 'text_transform' | 'code_exec' | 'input' | 'output';
  config: {
    model?: string;          // LLM 节点用
    url?: string;            // API 节点用
    condition?: string;      // 条件节点用
    template?: string;       // 文本模板
    max_iterations?: number; // 循环节点用
  };
  inputs: Record<string, string>; // 上游节点 ID → 输入映射
}

// 执行器：递归遍历 DAG，支持条件分支和循环
async function executeNode(
  node: WorkflowNode, 
  context: ExecutionContext
): Promise<NodeResult> {
  switch (node.type) {
    case 'llm_call':
      return executeLLMCall(node, context);
    case 'condition':
      return executeCondition(node, context);  // 分支选择
    case 'loop':
      return executeLoop(node, context);       // 循环迭代
    // ...
  }
}
```

**设计模式**：策略模式 + 递归 DAG 遍历。每个节点类型是一种执行策略，执行器递归解析 DAG，通过 ExecutionContext 传递状态。

### Skill 编译器核心

```typescript
// 将 DAG Workflow 编译为目标格式
interface SkillCompiler {
  compile(workflow: WorkflowDefinition): SkillPackage;
}

// MCP 格式 — 用于 Claude Code / Cursor / Codex
class MCPCompiler implements SkillCompiler {
  compile(workflow: WorkflowDefinition): MCPToolSchema {
    // Workflow 的每个节点映射为 MCP Tool 的一个 tool
    // DAG 执行逻辑编译为 tool handler
    return {
      name: workflow.name,
      description: workflow.description,
      parameters: workflow.inputs.map(i => ({...})),
      handler: async (params) => {
        return executeDAG(workflow, params);
      }
    };
  }
}

// API 格式 — 用于 Lovable / Bolt / 自建应用
class APICompiler implements SkillCompiler {
  compile(workflow: WorkflowDefinition): OpenAPISchema {
    // 自动生成 REST API 端点
    // DAG 的输入 → API 的 request body
    // DAG 的输出 → API 的 response
  }
}
```

**设计模式**：访问者模式——同样的 Workflow 结构，不同的 Compiler 生成不同的可执行格式。新增目标平台只需实现新的 Compiler。

## 📐 架构决策与设计哲学

### 核心哲学：Skills ≠ Prompts

这是 Refly 与所有"Prompt 模板库"类项目（如 awesome-claude-prompts）的根本区别。Refly 认为 prompt 是脆弱的——同样的 prompt 在不同模型/温度下输出不可控。而 Skill 是**确定性的**：有明确的输入输出 schema、版本号、错误处理逻辑、可测试。

### 生态战略

Refly 不是要替代 Claude Code / Cursor——它们是自己定位的"执行运行时"。Refly 是**给它们提供可复用的企业级 Skill 的上游平台**。这是一个聪明的补位策略：不与平台竞争，而是成为平台的基础设施层。

### 潜在限制

- **协议非标准 OSI 认证**：Refly 使用自定义的"ReflyAI License"，不是 Apache/MIT/GPL，对商业集成可能有潜在限制
- **PostgreSQL 作为唯一存储**：对所有非结构化数据（Workflow 定义、Skill 包、执行日志）也用关系型数据库，大规模场景可能需要引入对象存储或消息队列
- **93 个 Open Issues**：相对活跃的开发状态，但 Issue 数量偏高，需要关注维护者的响应速度

## 🌐 全网口碑画像

### 好评共识

- **"AI Agent 开发的范式转换"**——CSDN 评测认为，Refly 将 Agent 开发从"写 prompt"转换到了"构建可复用的技能组件"，是 LangChain 等框架之后的大事（来源：CSDN）
- **"3 分钟将企业 SOP 变成 AI 技能"**——腾讯云开发者社区评测称，导入 Excel SOP 到可视化工作流的全流程仅需 3 分钟（来源：cloud.tencent.com）
- **"非常适合企业级 Agent 应用"**——多位博主提到 Refly 最大的价值是为 Claude Code / Cursor 提供了"企业级数据操作能力"（来源：CSDN, 掘金）

### 差评共识

- **领域特定——不是通用工具**：Refly 的核心定位是企业级 SOP/流程自动化，个人开发者和普通内容创作者不是目标用户（来源：自研分析）
- **生态尚在早期**：refly-skills 仓库目前只有几十个 Skill，社区贡献不够活跃（来源：GitHub）
- **学习曲线**：Vibe Workflow 可视化工具虽然降低了门槛，但理解"Skill = 基础设施"这个概念需要一定的架构认知（来源：CSDN）

## ⚔️ 竞品对比

| 维度 | Refly | LangChain | n8n | AutoGen / CrewAI |
|------|-------|-----------|-----|-------------------|
| **核心理念** | Vibe Workflow → 编译为 Skill | 代码框架 | 可视化工作流 | 多 Agent 协作框架 |
| **编程要求** | 无需代码（可视化） | 需要 Python/TS 代码 | 无需代码 | 需要 Python 代码 |
| **执行运行时** | Claude Code / Cursor / Codex / 自定义 | 任何 Python 环境 | n8n 自托管 | Python 环境 |
| **Skill 复用** | ✅ 版本化 + 注册表 | ❌ 自己管理 | ✅ 工作流模板 | ❌ |
| **导出格式** | MCP / REST API / Bot | 仅代码 | 仅 n8n | 仅代码 |
| **目标用户** | 企业/团队 | 开发者 | 非技术运营 | 研究者/开发者 |
| **GitHub Stars** | 7,416 | 107,000+ | 60,000+ | ~50,000+ |
| **商业化** | 云托管 + 自部署 | LangSmith / LangGraph Cloud | n8n Cloud | 无 |
| **License** | ReflyAI License | MIT | Sustainable Use License | MIT |

## 🎯 核心研判

### 项目优势

1. **定位精准**：不跟 Claude Code / Cursor / n8n 直接竞争，而是做这些平台的上游"Skill 供稿商"——独特的生态位
2. **可视化 + 代码编译**：同时服务非技术用户（Vibe Workflow 拖拽编排）和开发者（MCP/API/CLI 编译导出），是全栈覆盖的"AI 流程编译平台"
3. **API-first 设计**：每个 Workflow 自动生成 REST API 端点，Lovable / Bolt 可直接调用——是 AI 时代的中间件
4. **生态绑定较弱**：Refly 不绑定特定 LLM 或运行时，它是纯粹的上游编译层，下游可以换

### 项目风险

1. **License 非标准 OSI 认证**：自定义"ReflyAI License"既不是 Apache/MIT，也不是 AGPL/BUSL。如果继续成长，License 合规性可能成为企业采纳的障碍
2. **强依赖下游平台生态**：如果 Claude Code / Cursor / Codex 自己推出内建的 Workflow 编辑器或 Skill 市场，Refly 的"中间人"价值会被削弱
3. **93 个 Open Issues**：相对 7,416 Stars 来说比例正常，但部分 Issue（如 DAG 编排的 edge case）表明核心引擎在边缘场景还不够稳健
4. **真正的 MVP 阶段**：虽然功能完整，但大量的"Pro"级特性（实时协作、版本对比、回滚、RBAC 权限）仍然缺失

### 适用场景 & 不适用场景

**适用**：
- ✅ 企业 SOP 数字化（审批流程、客户服务流程、质检流程→编译为 Agent Skill）
- ✅ 团队级 AI 自动化（飞书/Slack Bot 后台挂一个 Refly Workflow）
- ✅ Lovable / Bolt 等无代码平台的 AI Backend 中间件
- ✅ 为 Claude Code / Cursor 注入企业级能力（CRM 查询、财务报告等）

**不适用**：
- ❌ 个人开发者/内容创作者的简单自动化（杀鸡用牛刀）
- ❌ 需要<100ms 延迟的实时推理（Workflow 的 DAG 编排有固定开销）
- ❌ 对数据主权极端敏感（需要 on-prem 部署的场景——Refly 自部署可行，但文档不够成熟）

### 趋势判断

**上升期** ⬆️。2024 年 2 月开源至今，7,416 Stars 且在 AI Agent 工具赛道有明确的差异化定位。未来 12 个月的关键变量：(1) refly-skills 社区生态的活跃度 (2) License 标准化 (3) 下游平台（Claude Code / Cursor）是否推出竞争性内建方案。

## 📂 关键文件路径速查

| 文件/目录 | 路径 | 用途 |
|-----------|------|------|
| API 服务 | `apps/api/` | NestJS 后端（模块化 API） |
| Web UI | `apps/web/` | Next.js 前端（Vibe Workflow IDE） |
| AI 服务 | `apps/ai-service/` | LLM 推理层 |
| 工作流引擎 | `packages/workflow-engine/` | DAG 编排引擎（核心） |
| Skill 编译器 | `packages/skill-compiler/` | Workflow → MCP / API / Bot 编译 |
| 注册表 | `packages/skill-registry/` | Skills 版本化存储 |
| 官方 Skills | `refly-skills`（独立仓库） | 社区可执行 Skill 注册表 |
| 文档 | `docs/`（docs.refly.ai） | Docusaurus 文档站 |
| 容器化部署 | `docker/` + `docker-compose.yml` | Docker 编排 |
