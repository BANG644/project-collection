# 🔥 withastro/flue — 沙箱 Agent 框架

> GitHub: [withastro/flue](https://github.com/withastro/flue)  
> ⭐ 5,498 | 🔄 300 forks | 🏆 今日 162 stars  
> 语言: TypeScript | 协议: MIT  
> 抓取日期: 2026-06-19

---

## 一、项目概述

**Flue** 是由 Astro 团队（withastro）打造的开源 Agent 框架。它不是"又一个 SDK"——而是一个可编程的 TypeScript 框架，用于构建**真正自主的 AI Agent**。

核心哲学：以 Claude Code 和 Codex 为代表的"第二代 Agent"证明了自主式 Agent 的可行性，Flue 的目标是将这种架构范式**通用化、平台化**。

> "Flue unlocks this new architecture for agents."

---

## 二、核心架构

### 2.1 Agent 创建
```typescript
import { createAgent } from '@flue/runtime';
import { local } from '@flue/runtime/node';
import triage from '../skills/triage/SKILL.md' with { type: 'skill' };

export default createAgent(() => ({
  model: 'anthropic/claude-sonnet-4-6',
  tools: [...githubTools],
  skills: [triage, verify],
  sandbox: local(),
  instructions,
}));
```

每个 Agent 包含：
- **模型** — 可指定任意模型提供商
- **工具** — 类型安全的操作接口
- **技能** — 可复用的领域专业知识包
- **沙箱** — 安全的执行环境
- **指令** — 系统级行为引导

### 2.2 包架构

| 包名 | 功能 |
|------|------|
| `@flue/runtime` | 核心运行时：harness、会话、工具、沙箱 |
| `@flue/cli` | CLI 和构建/开发工具（flue 二进制） |
| `@flue/sdk` | 客户端 SDK，用于消费部署的 Agent 和工作流 |
| `@flue/opentelemetry` | OpenTelemetry 追踪适配器 |
| `@flue/postgres` | Postgres 持久化适配器 |

---

## 三、核心能力

### 3.1 Agent（自主型）
- 跨会话和事件保持上下文
- 自主朝目标工作
- 持久化执行：失败/重启时恢复进度

### 3.2 Workflows（工作流）
- 结构化自动化
- 代码引导 Agent 推理从输入到输出
- 适合确定性的业务流程

### 3.3 Sandboxes（沙箱）
- 虚拟、本地、远程容器沙箱
- 安全环境供 Agent 使用工具、修改文件
- 集成 Daytona 等远程沙箱提供商

### 3.4 子 Agent 编排
- 定义不同角色的专家 Agent
- 主 Agent 自动委派子任务

### 3.5 技能系统
- 打包可复用专业知识和流程
- 任务需要时自动加载

### 3.6 MCP 服务器集成
- 通过 MCP 协议连接外部工具和服务
- 支持鉴权和类型安全

### 3.7 渠道（Channels）
- Slack、Teams、Discord、GitHub 等事件源
- 验证事件真实性

### 3.8 可观测性
- OpenTelemetry 集成
- Braintrust、Sentry 支持
- 自定义 Observer

---

## 四、部署选项

| 平台 | 支持方式 |
|------|---------|
| Node.js | ✅ 原生 |
| Cloudflare Workers | ✅ |
| GitHub Actions | ✅ |
| GitLab CI/CD | ✅ |
| Render | ✅ |
| Daytona（沙箱） | ✅ |

---

## 五、技术栈

| 组件 | 说明 |
|------|------|
| 语言 | TypeScript |
| 运行时 | Node.js / Cloudflare Workers |
| 沙箱 | 虚拟/本地/远程容器 |
| 协议 | MCP, HTTP |
| 持久化 | Postgres（适配器）、内存 |
| 可观测性 | OpenTelemetry, Sentry, Braintrust |
| 编排 | 内置子 Agent 委派 |

---

## 六、与传统 Agent 框架对比

| 特性 | Flue | LangChain | CrewAI | AutoGPT |
|------|------|-----------|--------|---------|
| 沙箱 | ✅ 内置多类型 | ❌ 需要额外配置 | ❌ | ❌ |
| 类型安全 | ✅ TypeScript | ❌ Python | ✅ Python | ❌ |
| MCP 支持 | ✅ 原生 | ❌ | ❌ | ❌ |
| 持久化执行 | ✅ Durable | ❌ | ❌ | ❌ |
| 渠道集成 | ✅ 5+ 平台 | ✅ | ❌ | ❌ |
| 单二进制 CLI | ✅ flue | ❌ | ❌ | ❌ |
| 自主 Agent | ✅ 原生 | ✅ | ✅ | ✅ |
| 子 Agent | ✅ 内置 | ✅ 需额外 | ✅ 原生 | ❌ |
| Astro 生态 | ✅ 同团队 | ❌ | ❌ | ❌ |

---

## 七、适用场景

1. **Bug 分类与自动修复** — Agent 阅读 Bug 报告、复现、诊断、修复全流程
2. **代码审查自动化** — 分析 PR、运行测试、验证行为
3. **运维自动化** — 处理告警、执行回滚、分析日志
4. **知识工作流** — 文档撰写、研究汇总、报告生成
5. **Agentic SaaS** — 将 Agent 作为 API 部署，对外提供服务

---

## 八、关键发现

1. **Astro 团队跨界** — withastro 以前端框架 Astro 闻名，进入 Agent 框架领域是重大战略转型，说明 Agent 基础设施正在成为前端/全栈团队的自然延伸
2. **沙箱优先** — 与其他框架不同，Flue 把沙箱作为一等公民，说明安全执行是 Agent 生产化的核心挑战
3. **TypeScript 全栈** — 选择 TS 而非 Python 作为主力语言，瞄准的是 Web 开发者生态
4. **5.5K stars 快速增长** — 今日 162 stars，增长速度不错，社区反应积极
5. **实用主义设计** — 没有 reinvent the wheel，而是把 MCP、OpenTelemetry、Postgres 等成熟组件组合成一个统一的框架
