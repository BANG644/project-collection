# ToolJet 深度调研

> 调研日期：2026-08-15 ｜ 星标：38,963 ⭐ ｜ 协议：AGPL-3.0 ｜ 语言：JavaScript / TypeScript（前端 React，后端 Node/NestJS）
> 仓库：`ToolJet/ToolJet` ｜ 默认分支：`main`（开发分支 `develop`）｜ 官网：tooljet.com

## 一、项目定位（一句话）

开源（AGPL）的**企业内部工具 / 低代码平台**——拖拽式 App Builder + 80+ 数据源 + AI Agent 编排，是 **Retool 最知名的开源替代品**。

## 二、项目亮点（差异化）

1. **可视化构建器**：60+ 响应式组件（表格/图表/表单/列表/进度条），多页应用 + 多人实时协作编辑。
2. **80+ 数据源**：数据库、API、云存储、SaaS 工具全覆盖，内置 ToolJet Database（无代码数据库）。
3. **代码无处不在**：应用内可运行 JavaScript 与 Python，灵活度高于纯拖拽。
4. **AI 原生（企业版 ToolJet AI）**：自然语言生成应用、AI 查询生成/转换、AI 调试、Agent Builder、GitSync/CI-CD。
5. **部署灵活 + 安全**：Docker / K8s / AWS / GCP / Azure；AES-256-GCM 加密、代理-only 数据流、SSO。

## 三、核心架构

ToolJet 是一个典型的 **monorepo 全栈低代码平台**：

- **`server/`**：NestJS + TypeORM + PostgreSQL 后端
  - 依赖栈（节选自 `server/package.json`）：`@nestjs/*` 全家桶（core/config/websockets/throttler/typeorm/event-emitter/bull/bullmq）、`@casl/ability`（权限）、`@ai-sdk/anthropic|google|mistral|openai`（AI 能力）、`@bull-board`（任务队列看板）、`@keyv/serialize`、`@dagrejs/graphlib`（图布局）、`@google-cloud/spanner` 等。
  - 模块结构：`server/src/` 下 `modules/`（各业务域）、`entities/`（数据库实体）、`dto/`、`helpers/`、`mails/`、`otel/`（可观测）、`main.ts`（入口）。
- **`frontend/`**：React + webpack + Tailwind 前端，`src/` 为应用主体，`ee/` 为企业版扩展。
- **`plugins/` + `queryPanel/`**：数据源连接器与查询面板抽象——前端组件绑定 query，query 由插件后端执行，是低代码"数据驱动 UI"的核心机制。
- **`marketplace/`**：可分发组件/模板市场。
- **分支模型**：git-flow，基分支 `develop`，稳定版走 `main` / `v1.x.x` tag。

**关键设计**：AI 能力（`@ai-sdk/*`）与异步任务（`@nestjs/bullmq`）在依赖层即原生支持，说明 ToolJet 把"AI 生成 + Agent 编排"当作一等公民而非外挂。

## 四、应用场景与启发

**典型场景**：内部 admin 后台、CRM、数据看板、审批流、工单系统、AI Agent 工作台。

**架构启发（可复用）**：
- **低代码 + AI 生成 + Agent 编排三层叠加**：可视化构建解决"快"，AI 生成解决"零门槛"，Agent Builder 解决"自动化"——三者正交可组合。
- **开源商业化分层范式**：核心 CE 走 AGPL，企业能力（SOC2/审计/白标/GitSync/RBAC 细粒度）放 `server/ee/` 与 `frontend/ee/`，用代码目录天然划清免费/付费边界（与 n8n、Appsmith 同思路）。
- **连接器插件化**：把"连数据库/API/SaaS"做成可插拔插件，平台价值随连接器数量指数增长。

## 五、源码深度解读

### 1. 后端技术栈信号：`server/package.json`

```jsonc
"dependencies": [
  "@nestjs/common", "@nestjs/core", "@nestjs/typeorm", "@nestjs/websockets",
  "@nestjs/bullmq", "@nestjs/throttler", "@casl/ability",
  "@ai-sdk/anthropic", "@ai-sdk/google", "@ai-sdk/mistral", "@ai-sdk/openai",
  "@dagrejs/graphlib", "@google-cloud/spanner", "@hubspot/api-client"
]
```

这套依赖直接暴露架构意图：NestJS 模块化 + TypeORM 持久化 + WebSocket 实时 + BullMQ 异步队列 + CASL 权限 + **四家 AI SDK 并置** + graphlib（画布/依赖图）。一个 `package.json` 就把"低代码 + 实时 + AI + 权限"说清楚了。

### 2. 模块化后端：`server/src/modules`

NestJS 的 `modules/` 目录按业务域切分（数据源、应用、查询、用户、工作区等），`entities/` + `dto/` 定义数据模型与边界，`main.ts` 引导 Nest 应用并挂 WebSocket/静态服务。低代码平台的"模型驱动"本质：UI 配置 → query → 后端 module 执行 → 数据回填组件。

## 六、全网口碑

- **规模与地位**：38k+ 星标，是 Retool 之外最被频繁提及的开源低代码平台；ProductHunt / HackerNews 多次上榜，已有企业采用（企业版主打 SOC2/GDPR 就绪）。
- **社区反馈**：正面集中在"开源可控、数据源广、上手快"；常见讨论点是 **AGPL 对商业化的约束**、与 Appsmith/Budibase 的功能重叠，以及企业能力的付费墙。
- **总体**：口碑健康，少有技术争议，主要权衡在许可证与商业化模块。

## 七、竞品对比与核心研判

| 维度 | ToolJet | Retool | Appsmith | Budibase | n8n |
|---|---|---|---|---|---|
| 开源协议 | AGPL-3.0 | ❌ 闭源 | AGPL | GPL | Fair-code |
| 可视化构建 | ✅ | ✅ | ✅ | ✅ | ⚠️ 工作流 |
| 数据源广度 | 80+ | 广 | 广 | 中 | 400+ 集成 |
| AI Agent 原生 | ✅（企业版） | ✅ | 部分 | 部分 | ✅ |
| 定位 | 内部工具 | 内部工具 | 内部工具 | 内部工具/应用 | 工作流自动化 |

**核心研判**：
- **优势**：开源低代码赛道头部，可视化构建 + 数据源广度 + AI 原生三层叠加，自托管友好。
- **风险**：AGPL 对闭源商业产品有传染约束；高级 AI/Agent/合规能力集中在付费企业版。
- **启发**：如果要做"内部工具平台"或"低代码 + AI"产品，ToolJet 的"CE 开源引流 + EE 商业化 + 连接器插件化"是值得临摹的分层范本。

## 关键文件速查

| 路径 | 作用 |
|---|---|
| `server/src/main.ts` | NestJS 后端入口 |
| `server/src/modules/` | 业务域模块 |
| `server/src/entities/` `server/src/dto/` | 数据模型与边界 |
| `server/package.json` | 依赖栈（NestJS/AI SDK/BullMQ/CASL） |
| `frontend/src/` | React 前端应用 |
| `plugins/` `queryPanel/` | 数据源连接器与查询面板 |
| `marketplace/` | 组件/模板市场 |
| `server/ee/` `frontend/ee/` | 企业版能力 |
