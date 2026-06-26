# 🔬 BuilderIO Agent-Native — Agent 原生应用框架深度调研

> **仓库地址**: https://github.com/BuilderIO/agent-native  
> **Stars**: 4K+ | **语言**: TypeScript | **许可证**: MIT  
> **组织**: BuilderIO（Builder.io 团队）
> **推荐指数**: ⭐⭐⭐⭐⭐

---

## 一、项目定位

Agent-Native 是 BuilderIO 推出的**开源 Agent 应用框架**，核心理念是：**不要在 Agent 和 UI 之间做选择——每个 Agent-Native 应用同时是 UI 应用和 Agent**。

传统方法下，Agent 要么只是一个聊天框（Chat），要么是一个静默的后端脚本。Agent-Native 打破了这种二分法：Agent 和 UI 共享同一个状态、同一个数据库，在同一个文档中实时协作。

---

## 二、核心技术架构

### 核心原语（Primitives）

```
defineAction()  →  一套定义，同时服务于 UI/Agent/HTTP/MCP/A2A/CLI
                     ↓
        Agent Runtime (chat, tools, skills, memory, jobs, observability)
                     ↓
            任何 Drizzle 兼容的 SQL 数据库 + Nitro 兼容的托管
```

### 关键特性

| 特性 | 说明 |
|------|------|
| **Actions** | 一次定义工作流，UI / Agent / HTTP / MCP / A2A / CLI 共用 |
| **Agent Runtime** | 内置聊天、工具、技能、记忆、作业、可观测性和委派 |
| **后端无关** | 任何 Drizzle 支持的 SQL 数据库 + Nitro 兼容的主机 |
| **实时协作** | CRDT 合并，实时存在感（光标、选中环、谁在哪页） |
| **上下文感知** | Agent 知道你当前在看什么——选中文本按 Cmd+I 即可指示 |
| **每用户工作区** | 技能、记忆、指令、子 Agent、MCP 服务器——SQL 后端，按用户个性化 |
| **A2A 通信** | Agent 之间互相发现并跨应用协作 |
| **自改进应用** | Agent 可以自行添加功能、修复 bug、优化 UI |

---

## 三、三种产品形态

Agent-Native 的一个核心理念是 **同一套底层原语，三种产品形态**：

| 形态 | 场景 | 技术栈 |
|------|------|--------|
| **Headless** | 从代码、CLI、HTTP、MCP、A2A 调用 | defineAction + auth + skills + memory |
| **Rich Chat** | 嵌入聊天，支持表格、图表、审批、设置向导 | 共享聊天运行时 + 适配器 |
| **Whole App** | 完整 SaaS UI，Agent 无缝嵌入 | SQL 状态 + 深度链接 + 实时同步 |

### 支持的协议集成

- A2A（Agent-to-Agent）
- MCP + MCP Apps + 标准远程 MCP OAuth
- HTTP / CLI action calls
- Native chat widgets
- OpenAI / AG-UI / Claude Agent SDK / Vercel AI SDK 聊天运行时
- Claude Code、Codex、Cursor、OpenCode、GitHub Copilot / VS Code

---

## 四、与同类框架对比

| 特性 | Agent-Native | LangChain | AutoGen | CrewAI | Claude Agent SDK |
|------|:-----------:|:---------:|:-------:|:------:|:---------------:|
| 开源 | ✅ MIT | ✅ MIT | ✅ MIT | ✅ MIT | ❌ 部分 |
| UI 集成 | 原生一等公民 | ⚠️ 通过第三方 | ❌ 无 | ❌ 无 | ❌ 无 |
| 实时协作 | ✅ CRDT 同步 | ❌ | ❌ | ❌ | ❌ |
| A2A 协议 | ✅ 内置 | ❌ | ⚠️ 部分 | ✅ 自定义 | ❌ |
| 多形态部署 | Headless/Chat/App | ✅ | ⚠️ | ✅ | ❌ |
| 自改进应用 | ✅ Agent 改 UI | ❌ | ❌ | ❌ | ❌ |
| 数据库独立 | ✅ 任何 SQL | ⚠️ | ⚠️ | ⚠️ | ❌ |
| MCP 支持 | ✅ 原生 | ✅ | ✅ | ⚠️ | ✅ |

---

## 五、实用模板（开箱即用）

Agent-Native 提供全套开源 SaaS 模板，部署即可用：

| 模板 | 功能 | 对标产品 |
|------|------|---------|
| Calendar | 事件管理 + Google 日历同步 + AI 日程 | Google Calendar / Calendly |
| Content | 本地 MDX 编辑 + agent 起草/改写/发布 | Obsidian |
| Plans | 可视化计划 + PR 回顾（用于编码 Agent） | Linear / Notion |
| Slides | React 驱动的 AI 幻灯片 | Google Slides / Pitch |
| Analytics | 数据分析 + 可复用仪表盘 | Amplitude / Mixpanel |
| Clips | 屏幕录制 + AI 字幕/摘要 | Loom |

### 立即体验技能
```bash
# 在 Claude Code / Codex / Cursor 中安装使用：
npx @agent-native/core@latest skills add visual-plan
# 添加 /visual-plan 和 /visual-recap 命令
```

---

## 六、社区与维护

| 维度 | 评分 | 说明 |
|------|:----:|------|
| 代码活跃度 | ★★★★★ | 每周频繁提交，已有 1900+ commmits |
| 文档质量 | ★★★★★ | 官方文档完善（agent-native.com），模板齐全 |
| 团队背景 | ★★★★★ | BuilderIO 团队（知名开源组织，Builder.io / Mitosis） |
| 兼容性 | ★★★★☆ | 需要 Drizzle SQL + Nitro 生态，有一定技术锁定 |
| 上手难度 | ★★★☆☆ | 概念较多，但模板迅速降低启动成本 |

---

## 七、综合评价

| 维度 | 评分 | 评价 |
|------|:----:|------|
| 技术创新 | ★★★★★ | Agent 与 UI 平权的理念远超同期框架 |
| 实用性 | ★★★★★ | 模板 SaaS 直接可用，技能可立即安装 |
| 生态适配 | ★★★★★ | MCP/A2A/OpenAI/Claude/Codex 全覆盖 |
| 文档 | ★★★★★ | 官网文档、模板、指南一应俱全 |
| 部署便利 | ★★★★☆ | MySQL/PostgreSQL/SQLite 可选，Nitro 部署 |

> **一句话总结**：Agent-Native 不是另一个 Agent 框架——它重新定义了 Agent 和 UI 的关系：一等公民的实时协作、原生 A2A 协议、自改进应用、三形态部署。如果你正在构建需要 Agent 协作的生产级应用，这是 2026 年最值得关注的框架之一。
