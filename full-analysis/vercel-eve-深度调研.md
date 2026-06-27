# 🔬 vercel/eve — 全方位深度调研

## 📌 一句话定位

Vercel 出品的**文件系统优先的持久化 Agent 框架**——把 Agent 的所有配置（指令、工具、技能、频道、定时任务）都放在文件系统里而非数据库里，用 Next.js 式的"约定优于配置"哲学重新定义了 Agent 的开发体验。Beta 阶段，Apache-2.0 开源。

## ⭐ 项目亮点

- **Filesystem-First 设计哲学**：Agent 的指令是 `agent/instructions.md`，工具是 `agent/tools/get_weather.ts`，技能是 `agent/skills/plan_a_trip.md`——所有配置都是**人类和 AI 都可读的 Markdown/TypeScript 文件**，而不是藏在数据库里的 JSON blob。这个设计直接对标 Vercel 自己如何用 `pages/` 目录结构重新定义了 Web 开发
- **原生持久化 + HITL 支持**：不像 LangChain/CrewAI 需要外部状态管理，eve 的 session 持久化是**一等公民**。Human-in-the-Loop（审批、提问题等待用户输入）也是框架原生支持的
- **频道抽象 + 跨频道通信**：一个 Agent 可以同时暴露 HTTP API、Slack Bot、Discord Bot、定期 Cron Job——并且可以在不同频道之间 `receive()` 消息。Issue #235 的讨论显示社区对 Slack 的 `onReactionAdded` 钩子等高级功能有强烈需求
- **Vercel 平台深度整合**：与 Vercel AI SDK、AI Gateway、Observability 无缝集成。自托管也支持 Docker + 任何 Node.js 环境
- **TypeScript 原生 + Zod Schema**：所有工具定义、频道配置都使用 TypeScript 类型系统 + Zod 进行 Schema 验证，从工具输入到输出全程类型安全

## 🏗️ 项目架构全景

### 目录结构

```
vercel/eve/
├── packages/
│   ├── eve/                    # 核心 SDK
│   ├── eve-ai-sdk/             # Vercel AI SDK 适配器
│   └── ...                     # 更多子包
├── apps/
│   ├── docs/                   # 文档站（Next.js + Geist）
│   └── ...                     # 示例应用
├── e2e/                        # 端到端测试
├── .github/                    # CI/CD
├── AGENTS.md, CLAUDE.md        # AI Agent 配置文件
├── SKILL.md                    # 自身的 Skill 定义
└── Dockerfile                  # 容器化部署
```

### 设计哲学

```text
my-agent/
└── agent/
    ├── agent.ts            # 模型 + 运行时配置
    ├── instructions.md     # 系统提示词（永远生效）
    ├── tools/              # 模型可调用的函数
    │   └── get_weather.ts
    ├── skills/             # 按需加载的流程
    │   └── plan_a_trip.md
    ├── channels/           # 消息通道（HTTP、Slack、Discord）
    │   └── slack.ts
    └── schedules/          # 定时任务
        └── weekly_recap.ts
```

这个设计模式刻意复用了 Vercel 的 "文件即路由" 理念——你不需要学习一个复杂的 Agent 框架 API，只要在正确的目录下放文件即可。

### 技术栈

- **语言**：TypeScript (Node >=24)
- **构建**：Turborepo + pnpm workspaces
- **测试**：Vitest + Playwright
- **代码质量**：oxlint + oxfmt + syncpack
- **发布**：Changesets
- **文档**：Next.js + Geist Docs

### 核心依赖

- `ai` (Vercel AI SDK)
- `zod` (Schema 验证)
- Agent 框架自身的持久化引擎（state machine + durable runtime）

## 💡 应用场景与启发

### 典型使用场景

1. **独立后台 Agent**：不需要前端的纯服务端 Agent，通过 Slack/Discord/HTTP 与用户交互
2. **定时任务 Agent**：`schedules/` 目录下的 cron job 定义，比如每周五发送报告
3. **多频道 Agent**：同一个 Agent 同时服务 Slack 和 Web 界面，消息可以在两者间流转
4. **审批工作流**：HITL 支持让 Agent 在关键决策点停下来等人类确认

### 可借鉴的解决方案模式

- **Filesystem as API**：把 Agent 的每个能力映射到文件系统，降低了心智负担。这个设计模式可以类比到其他领域——比如把工作流定义、配置规则都放到文件系统里
- **频道 + 调度的统一抽象**：HTTP、Slack、Cron 在 eve 里都是"频道"（channel），统一了消息接收的抽象。这种统一接口的思想值得在自己的 Agent 系统中模仿

### 与竞品的差异化定位

- **vs LangChain**：LangChain 是 Agent 的"建筑材料"，eve 是 Agent 的"框架"。LangChain 给你积木自己搭建，eve 给你一个做好的脚手架
- **vs CrewAI**：CrewAI 专注多 Agent 协作，eve 专注单 Agent 的持久化 + 多频道部署
- **vs AutoGPT**：AutoGPT 追求完全自主，eve 强调 HITL（Human-in-the-Loop）的安全可控

## 🧠 核心源码解读

### 入口与主流程

eve 的核心入口在 `packages/eve/src/`。最关键的几个抽象：

1. **`defineAgent`** — Agent 的配置入口，定义模型、运行时、指令
2. **`defineTool`** — TypeScript 函数 → LLM 工具的一等公民转换
3. **Channel 抽象** — `httpChannel()` / `slackChannel()` / `discordChannel()` → 统一的 receive/send 接口
4. **Schedules** — Cron 表达式 → 周期性任务

### 关键设计模式

```typescript
// 工具定义（简洁且类型安全）
import { defineTool } from "eve/tools";
import { z } from "zod";

export default defineTool({
  description: "Return mock weather data for a city.",
  inputSchema: z.object({ city: z.string().min(1) }),
  async execute({ city }) {
    return { city, condition: "Sunny", temperatureF: 72 };
  },
});
```

这个模式在 `packages/eve/src/` 中通过 `normalizeToolDefinition` 和 `resolveToolDefinition` 做编译器级别的验证（Issue #203 的讨论显示，`defineClientTool` 是在看到用户遇到 `execute` + HITL 冲突后快速补出的分离抽象）。

### Issue 中的关键洞察

从 30 条 Issue 分析，eve 目前暴露的三个主要工程痛点：

| 问题 | Issue 数量 | 严重程度 |
|------|-----------|---------|
| Windows 兼容性（反斜杠路径问题） | #311 等 | 🔴 影响 Windows 开发者 |
| HITL 工具结果重复（`execute` + approval 冲突） | #203, #236 | 🔴 核心流程 bug |
| 外部 Provider 模型兼容性 | #317, #154 | 🟡 非 Vercel 生态的用户受影响 |

## 📐 架构决策与设计哲学

### ADR 摘要

从 SKILL.md、CLAUDE.md 和 AGENTS.md 中可以提取出以下几个关键设计决策：

1. **Filesystem 优先，不是唯一**：虽然核心设计是 FS-based，但 `channel` 抽象说明 eve 也考虑了远程 Agent 的通信
2. **持久化 = 一等公民**：不同于 LangChain 把 memory 当插件，eve 默认所有 session 都是持久化的，重启进程后自动恢复
3. **HITL 不是"将来加"**：approval、input-request 等模式是框架的原生能力，不是后加的补丁
4. **Beta 期明确**：README 末尾明确标注 "eve is currently in beta... the framework, APIs, documentation, and behavior may change before general availability."——这意味着现在用的 API 可能在未来变化

### 设计红线

从被关闭/拒绝的 Issue 中可以看出的边界：

- **不是多 Agent 编排框架**：eve 不解决多 Agent 协作的问题（那是 CrewAI 的领域）
- **不是低代码平台**：需要写 TypeScript，不是拖拽式
- **不绑定 Vercel 平台**：虽然深度集成了 Vercel 生态，但 Docker 部署可行

## 🌐 全网口碑画像

### 好评共识

- **"Next.js 是 Web 的答案，Eve 是 Agent 的答案"**（InfoQ）：InfoQ 的文章认为 eve 继承了 Vercel 在 Web 开发中的"约定优于配置"理念
- **"真正能落地生产的 Agent 工程化方案"**（CSDN）：CSDN 的文章指出 eve 的持久化 + HITL 设计是"区别于玩具级 Agent 框架的关键差异"
- **"用 Vercel 的方式写 Agent"**（博客园）：中文开发者社区认为 eve 拉低了 Agent 开发门槛，"你不需要学 LangChain 那套复杂的 Chain/Agent 抽象"

### 差评共识 & 踩坑高发区

- **Windows 兼容性差**：Issue #311 报告了 Windows 上 dev schedule dispatch route 500 的错误（反斜杠路径问题）。对于 Windows 开发者来说，体验可能不太好
- **Issue 数量多但 Beta 谅解度高**：30 条开放 Issue 中很多是 enhancement request，但也有一些确实是 bug（#282, #281）。社区普遍理解这是 Beta 阶段的阵痛
- **被批评为"Vercel 锁定的 Agent 框架"**：虽然支持自托管，但深度集成了 Vercel AI Gateway 和 Observability，部分开发者担心 vendor lock-in

### 争议焦点

- **eve vs AI SDK**：部分社区不理解 eve 和 Vercel AI SDK (`ai`/`@ai-sdk/*`) 的关系——AI SDK 是低层工具调用库，eve 是高层 Agent 框架。两者是互补关系
- **Filesystem 模式是否适合生产**：对于微服务/容器化部署，FS 化的配置管理可能比环境变量 + 数据库配置更复杂

### 典型实战案例

- **"把 Agent 做成 Slack Bot 只用了 3 个文件"**（GitHub Discussions）：社区用户在 Discussion 中分享的案例显示，一个 Slack channel agent 只需要 `instructions.md` + `tools/` + `channels/slack.ts` 三个文件

## ⚔️ 竞品对比

| 维度 | Vercel Eve | LangChain | CrewAI | AutoGPT |
|------|-----------|-----------|--------|---------|
| **定位** | FS-First 持久化 Agent 框架 | Agent 构建工具包 | 多 Agent 协作框架 | 完全自主 Agent |
| **配置方式** | 文件系统（Markdown + TS） | Python/TS API | YAML/TS | 命令行/JSON |
| **持久化** | ✅ 一等公民 | ❌ 需要额外配置 Mem0/Redis | ❌ 需外部存储 | ❌ 有限 |
| **HITL** | ✅ 原生支持 | ⚠️ 需自定义回调 | ⚠️ 有限 | ❌ |
| **频道抽象** | HTTP/Slack/Discord/Cron | 无原生抽象 | 无 | 无 |
| **多 Agent** | ❌ 单 Agent 设计 | ⚠️ 可构建 | ✅ 核心能力 | ❌ |
| **TypeScript** | 纯 TS | 多语言（Python 为主） | Python | Python |
| **Vercel 绑定** | 深度但可自托管 | 无 | 无 | 无 |
| **成熟度** | Beta (0.x) | 成熟 (0.3.x) | 较成熟 | Alpha |

### 选择建议

- **单 Agent 后台部署（持久化 + 多频道）** → **Vercel Eve**（最适合）
- **需要多 Agent 编排** → CrewAI
- **需要最大灵活度** → LangChain
- **需要完全自主 Agent** → AutoGPT

## 🎯 核心研判

### 项目优势

1. **Filesystem-First 是正确的选择**：这个设计模式降低了 Agent 开发的心智负担，而且是 Vercel 已验证过的（Next.js 的成功经验）
2. **Vercel 生态绑定 = 优势也是风险**：如果你已经在用 Vercel，eve 的集成体验无与伦比；如果你不用 Vercel，自托管也是可行的
3. **持久化 + HITL 的工程化做得好**：这是区分"玩具 Agent"和"生产 Agent"的关键差异

### 项目风险

1. **Beta 阶段的不确定性**：README 明确说 API 可能变化，不适合生产关键业务
2. **Windows 兼容性问题**：Issue #311 显示 Windows 支持不成熟，Windows 开发者可能遇到阻碍
3. **非 Vercel 生态用户的摩擦**：虽然可以自托管，但 Vercel AI Gateway 等集成是 eve 的重要卖点
4. **竞争格局激烈**：LangChain/CrewAI/AutoGPT 等都在快速迭代，eve 需要快速建立差异化

### 适用场景 & 不适用场景

**适用**：
- Vercel 生态内的 Agent 部署
- 单 Agent 后台（Slack Bot、HTTP API Agent、定时报告）
- 需要持久化 session + HITL 审批的工作流
- 不想学复杂 Agent 框架的 TypeScript 开发者

**不适用**：
- Python 技术栈的团队
- 多 Agent 协作场景
- Windows 开发环境下的调试
- 需要稳定 API 的生产环境

### 趋势判断

🟢 **快速上升期**。Vercel 的品牌效应 + 开源社区的快速反馈（2 周 2.8K star + 374 Issue）说明 eve 击中了一个真实需求。关键在于 Vercel 能否在 Beta 期内快速迭代到生产可用状态。

## 📂 关键文件路径速查

| 文件 | 作用 |
|------|------|
| `packages/eve/src/` | 核心 SDK 源码 |
| `AGENTS.md` | AI Agent 的项目级开发指南 |
| `CLAUDE.md` | Claude Code 配置 |
| `SKILL.md` | eve 自身的 skill 定义 |
| `Dockerfile` | 容器化部署 |
| `apps/docs/` | 官方文档站 |
| `docs/` | `node_modules/eve/docs`（npm 包内置文档） |
| `github.com/vercel/eve/discussions` | 社区讨论主线 |
