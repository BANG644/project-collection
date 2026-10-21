# twentyhq/twenty 深度调研

> 调研日期：2026-10-22 ｜ 星标：59,012 ⭐ ｜ 语言：TypeScript ｜ 许可：NOASSERTION（实际为商业 + AGPL 双许可，self-host 与 cloud 边界需留意）｜ 默认分支：main
> 定位：**#1 开源 CRM，"为 AI 设计" —— 技术团队像构建其余技术栈一样，把 CRM 建、版本化、部署成代码**

## 一、项目亮点（差异化）

1. **元数据驱动（objects/fields/views 即代码）**：用 `defineObject` + `FieldType` 在代码里声明对象、字段、视图，经 `npx twenty app:publish` 推到工作区——业务模型成为可版本化的源码，而非后台点出来的配置。
2. **Nx monorepo 统一全栈 + skills**：`packages/` 同时承载 server、front、CLI、SDK、官方 agent-skills、website，单仓库统一构建与发布。
3. **AI native 内建**：产品层内置 AI agents 与 chats；仓库侧提供 `packages/twenty-agent-skills`（create/develop/manage/publish-app + use-twenty-mcp），可在 Claude Code / Codex / Cursor / Pi 等 harness 运行。
4. **Self-host 友好 + 成熟社区**：Docker Compose 一键自托管；59k ⭐、活跃 Discord、开放贡献（无 allowlist）。

## 二、核心架构

- **构建编排**：Nx（`nx.json`）+ Yarn workspaces；`package.json` 中 `packages/*` 为工作区成员。
- **后端**：`packages/twenty-server` 基于 NestJS，GraphQL API，PostgreSQL 存储，Redis + BullMQ 做队列/缓存。`src/` 内部结构：`app.module.ts`（根模块）、`modules/`（按领域拆分的业务模块）、`database/`（迁移/连接）、`engine/`（元数据引擎）、`queue-worker/`（后台任务）、`command/`、`filters/`、`utils/`。
- **前端**：`packages/twenty-front` 基于 React + Jotai（状态）+ Linaria（零运行时 CSS）+ Lingui（i18n）。
- **AI 装配**：`packages/twenty-agent-skills` 与 `packages/twenty-claude-skills` 提供 agent skill 家族；`twenty-sdk` 暴露客户端 API；`SKILLS.md` 解释不同 skill 家族的受众与安装方式（仅 `agent-skills` 分支面向"在 Twenty 上构建应用"的人）。

## 三、应用场景与启发

- **业务系统"元数据驱动 + AI native"的标杆样本**：对想做可配置 SaaS / 内部工具平台（CRM、工单、项目管理）的团队，Twenty 展示了"用代码定义数据模型 + 用 agent 加速开发/运维"的完整闭环。
- **给自有 agent 接业务系统的参考**：`use-twenty-mcp` 把 agent 连到工作区以"可读方式呈现记录"，是"agent ↔ 业务数据库"的轻量集成范式，可类比用户已调研的众多 MCP 服务器。
- **Nx monorepo 治理大仓**：26 个 `packages/*` 的边界划分（server/front/sdk/skills/website 分离）是多包前端后端的成熟范本。

## 四、源码深度解读

**1) `packages/twenty-server/src` 的后端骨架**
NestJS 模块化 + GraphQL。根模块装配所有领域模块与基础设施：

```text
packages/twenty-server/src/
├── app.module.ts        # 根模块：装配 modules/、database/、engine/
├── modules/             # 按领域拆分（company, person, opportunity, ...）
├── database/            # 连接池 / 迁移
├── engine/              # 元数据引擎：把 objects/fields 定义映射为表与 GraphQL schema
├── queue-worker/        # BullMQ 后台任务
├── command/  filters/  utils/
```

`engine/` 是"元数据驱动"的核心——它消费用户在代码/界面里定义的 object/field，动态生成数据库表与 GraphQL resolver，使 CRM 可像代码一样演进。

**2) `packages/twenty-agent-skills/SKILLS.md` —— AI 装配清单**
把"建 App"拆成可组合技能：

```text
| create-app   | Scaffold a new Twenty app.                            |
| develop-app  | Add/modify objects, fields, logic fns, layouts, workflows. |
| manage-app   | Remotes, sync, build, deploy, logs, CI/CD.            |
| publish-app  | README, marketplace metadata, logos, screenshots.     |
| use-twenty-mcp | Connect an agent to a workspace over MCP.           |
```

**3) `SKILLS.md`（仓库根）** 说明多 skill 家族受众分层——把"给 Twenty 构建应用的人"与"在 Twenty 工作区内工作的人"的技能分开，避免误装。

## 五、社区口碑

- 59k ⭐，号称 "#1 Open-Source CRM"，Discord 活跃，贡献开放；"Salesforce 开源替代"叙事强，被众多技术团队采用。
- 文档站点（docs.twenty.com）覆盖用户指南与开发者参考；Roadmap 公开在 GitHub Projects。

## 六、竞品对比 + 核心研判

| 项目 | 类型 | 差异 |
|---|---|---|
| **twenty** | 开源 + 商业 | 元数据驱动 + AI native + 开发者体验优先 |
| Salesforce / HubSpot | 商业 SaaS | 闭源、按席位计费、定制成本高 |
| Odoo | 开源 ERP/CRM | 更重、模块广，开发者体验与 AI 叙事弱于 Twenty |
| SuiteCRM | 老牌开源 | 架构陈旧，缺乏元数据驱动与 agent 生态 |

**研判**：最适合**技术团队自建 CRM**（要版本化、要接 agent、要 self-host）的场景；对纯业务/非技术用户，商用 SaaS 上手更省事。许可为 NOASSERTION——官方实际是"self-host 社区版（AGPL 类）+ 商业云"双轨，生产使用前务必核对 `LICENSE` 与商业条款边界，避免把社区版当完全自由商用。

## 七、关键文件速查

- `packages/twenty-server/` —— NestJS + GraphQL 后端（`src/modules`、`src/engine`、`src/queue-worker`）
- `packages/twenty-front/` —— React + Jotai + Linaria 前端
- `packages/twenty-agent-skills/` / `packages/twenty-claude-skills/` —— 官方 agent skill 家族
- `packages/twenty-sdk/` —— 客户端 SDK（`defineObject` / `FieldType`）
- `SKILLS.md`（根）—— 多 skill 家族受众说明
- `nx.json` / `package.json` —— Nx monorepo 工作区编排
- `packages/twenty-docker/` —— Docker Compose 自托管
