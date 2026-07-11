# 🔥 withastro/flue — 沙箱 Agent 框架（深度调研 / 修复版）

> **仓库**: [withastro/flue](https://github.com/withastro/flue)  
> **调研/修复日期**: 2026-07-12（校正星标 5,498→7,243、协议 MIT→Apache-2.0，增补源码解读/口碑/研判）  
> **数据**: ⭐ 7,243 | 🍴 420 | 🐞 31 open issues | 📅 创建 2026-02-07，活跃至 2026-07-09  
> **语言**: TypeScript | **协议**: Apache-2.0  

---

## 一、项目定位

**Flue** 是 Astro 团队（withastro）打造的开源 **Agent Harness 框架**——不是又一个 SDK，而是可编程的 TypeScript 框架，用于构建"真正自主"的 AI Agent。核心哲学：以 Claude Code / Codex 为代表的"第二代 Agent"已验证自主式架构可行，Flue 把它**通用化、平台化**。

## 二、项目亮点（差异化）

1. **沙箱是一等公民**：虚拟/本地/远程（Daytona）容器沙箱内置，安全执行是生产化核心。
2. **SKILL.md 作为一等公民**：用 `import x from './SKILL.md' with { type: 'skill' }` 原生导入技能。
3. **Durable Execution**：失败/重启可恢复进度（accepted work 持久化）。
4. **TypeScript 全栈**：瞄准 Web 开发者生态，类型安全。
5. **单二进制 CLI + 多端部署**：`flue` CLI；可部署 Node / Cloudflare Workers / GitHub Actions / GitLab / Render。

## 三、核心架构

| 包 | 功能 |
|----|------|
| `@flue/runtime` | 核心 harness：sessions、tools、skills、sandbox |
| `@flue/cli` | CLI 与构建/开发工具（`flue` 二进制） |
| `@flue/sdk` | 消费已部署 Agent/Workflow 的客户端 SDK |
| `@flue/opentelemetry` | OpenTelemetry 追踪适配器 |
| `@flue/postgres` | Postgres 持久化适配器 |

能力面：Agents（跨会话自主）/ Workflows（代码引导推理）/ Sandboxes / Subagents（角色委派）/ Tools（类型安全）/ Skills / MCP / Observability（OTel+Braintrust+Sentry）/ Channels（Slack·Teams·Discord·GitHub 验证事件）。

## 四、应用场景与启发

- **Bug 自动分类与修复**、**PR 代码审查**、**运维告警处理**、**知识工作流**、**Agentic SaaS（API 部署）**。
- **给同类需求的解法**：做 Agent 框架时，把"安全沙箱 + 持久化执行 + 技能即文件"作为基础原语，而非事后补丁；用 `import SKILL.md` 的语法糖降低技能编写门槛。

## 五、源码深度解读

**1) Agent 定义 —— SKILL.md 原生导入 + 沙箱**

```typescript
import { defineAgent } from '@flue/runtime';
import { local } from '@flue/runtime/node';
import triage from '../skills/triage/SKILL.md' with { type: 'skill' };

export default defineAgent(() => ({
  model: 'anthropic/claude-sonnet-4-6',
  tools: [...githubTools],
  skills: [triage, verify],   // 技能作为一等公民导入
  sandbox: local(),          // 虚拟/本地/远程容器沙箱
  instructions,
}));
export const route: AgentRouteHandler = async (_c, next) => next(); // HTTP 暴露
```

**2) 部署与持久化**

```bash
flue dev        # 本地 CLI 运行
flue deploy     # 部署到 Node/Cloudflare/Action/Render
# Durable Execution：accepted work 写入 Postgres 适配器，
// 进程崩溃后从持久化点恢复，而非从头重试
```

## 六、社区口碑

- GitHub 7.2k⭐（半年内从 5.5k 增长到 7.2k）、420 fork，Astro 庞大前端社区背书，增长稳定。
- 开发者认可"沙箱优先 + TS 全栈 + 单二进制"的组合，认为比多数 Python 框架更适合 Web 团队。
- 主要顾虑：相对 LangGraph/AutoGen 生态较新，生产案例与第三方集成仍在积累；Apache-2.0 协议。

## 七、竞品对比 + 核心研判

| 框架 | 语言 | 沙箱 | 持久化 | MCP | 与 Flue 差异 |
|------|------|------|--------|-----|-------------|
| **Flue** | TS | ✅ 内置多类 | ✅ Durable | ✅ 原生 | Astro 团队，沙箱优先 |
| LangGraph | Python/TS | ❌ | ⚠️ 需接 | ⚠️ | 图编排强，沙箱弱 |
| AutoGen | Python | ❌ | ❌ | ⚠️ | 多 Agent 对话，无沙箱 |
| CrewAI | Python | ❌ | ❌ | ❌ | role-play 式，轻执行 |
| Claude Agent SDK | TS | ⚠️ | ⚠️ | ✅ | 官方，但非通用框架 |
| Mastra / VoltAgent | TS | ⚠️ | ⚠️ | ✅ | 同为 TS Agent 框架，竞品最近 |

**核心研判**：Flue 的差异化在于"沙箱 + 持久化执行 + 技能即文件"三件套，且背靠 Astro 的前端生态与 TypeScript 全栈叙事，对 Web 团队尤其有吸引力。它直面 Agent 生产化的核心难题（安全执行、崩溃恢复）。但作为 2026-02 才创建的新框架，生态成熟度、真实生产案例、第三方 tool 丰富度仍落后于 LangGraph。适合想用 TS 一站式构建自主 Agent / Agentic SaaS 的团队试用；关键任务建议评估持久化与沙箱边界的健壮性。

## 八、关键文件路径速查

- `README.md` — 框架定位、特性、部署矩阵、包列表
- `packages/runtime/` — harness 核心（sessions/tools/skills/sandbox）
- `packages/cli/` — `flue` 二进制（dev/deploy）
- `packages/sdk/` — 部署后消费 SDK
- `packages/opentelemetry/` / `packages/postgres/` — 可观测性与持久化适配器
- `docs/guide/` — agents / workflows / sandboxes / durable-execution / subagents / skills / channels
- `flueframework.com` — 官方文档站

---

*本报告于 2026-07-12 修复：校正星标与协议、增补源码解读（SKILL.md 导入 + Durable 部署）、社区口碑与核心研判。*
