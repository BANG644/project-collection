# 🔬 datawhalechina/Agent-Learning-Hub — 深度调研报告

> **调研时间**: 2026-06-15  
> **仓库**: [datawhalechina/Agent-Learning-Hub](https://github.com/datawhalechina/Agent-Learning-Hub)  
> **状态**: 活跃维护中，由 Datawhale 成员陈思州维护

---

## 一、项目概览

Agent-Learning-Hub 是一份**可执行的 AI Agent 学习路线图**，专门为"想要构建有用、可靠的 Agent，而不是收集一堆链接"的人设计。它不是又一份 paper list 或资源聚合，而是一份**按 Stage 分级、每步可打勾的 todo list**——从上到下做，完成即掌握。

### 核心理念

> "这个仓库只维护一个核心展示面：README。目标是把社区里优秀分享、官方博客、论文、开源项目和真实工程经验，整理成一份可以照着执行的 AI Agent 学习 todo list。"

这与常见的"awesome"类仓库形成本质区别：后者是链接目录，前者是**学习路径 + 行动清单**。

---

## 二、路线结构详解

### Stage 0 — 基础认知（为什么需要 Agent）

核心目标：区分 chatbot、workflow、agent、multi-agent，理解 agent 循环 (observe → think → act → observe)，更重要的是**明白什么时候不该用 agent**。

推荐阅读：
- [Anthropic: Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)
- [OpenAI: A practical guide to building agents](https://openai.com/business/guides-and-resources/a-practical-guide-to-building-ai-agents/)

**产出**：一页短笔记

### Stage 1 — 最小 Agent 实现

从零实现一个 50-150 行的最小 agent：LLM API 对话 → 结构化 JSON 输出 → 工具函数定义 → tool call 解析 → 工具执行 → agent loop 加 max_steps/timeout/错误处理。

推荐的 API 文档：
- [OpenAI Function Calling](https://platform.openai.com/docs/guides/function-calling)
- [Gemini API Function Calling](https://ai.google.dev/gemini-api/docs/function-calling)
- [Claude Tool Use](https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/overview)

### Stage 2 — 带工具的 Agent

进阶到 RAG：chunk → embed → retrieve → answer with citations。学会接入搜索、数据库、文件、浏览器、代码执行作为工具。涵盖短期上下文、会话记忆、长期记忆的区分与实现。

**推荐的参考项目**：
| 项目 | 学习价值 |
|------|---------|
| GPT Researcher | 搜索→抓取→筛选→引用→生成长报告的完整管道 |
| Open Deep Research | LangGraph 写的 deep research 示例 |
| STORM (Stanford) | 多视角资料综合的研究写作系统 |
| Khoj | 本地文档+网页+语义搜索的个人 second brain |
| mem0 | 记忆层组件 |
| Letta | 面向 stateful agents 的上下文管理平台 |

### Stage 3 — 深入一个 Agent System

不学"框架 API 怎么调"，而是学**如何组织工具、上下文、权限、状态、日志、子任务和反馈**。

推荐的深入对象：
- **Claude Code** — 真实 coding agent 的 CLI、工具、权限、hooks、subagents、MCP
- **learn-claude-code** — 从 0 到 1 复刻 Claude Code-like harness
- **claw0** — 从 agent loop 一路构建 session、channel、gateway、memory
- **OpenClaw** — 本地长运行 agent、skills、消息入口、系统工具和安全边界
- **Hermes Agent** — 长期记忆、skills、toolsets、多平台消息网关
- **LangGraph** — 状态图、可恢复执行、可控编排

### Stage 4 — 多 Agent 系统

理解 planner/executor/reviewer/critic/router 等角色，用 supervisor 或 graph 管理多 agent，防止循环、争论、任务漂移、上下文膨胀。

推荐协议：A2A (Agent2Agent)、ACP (Agent Client Protocol)

### Stage 5 — Skills（可复用能力包）

核心洞察：Skill ≠ Tool（tool 是可调用接口，skill 是可复用流程知识）；Skill ≠ Prompt（prompt 是一次性指令，skill 是可发现可版本化的能力包）；Skill ≠ MCP（MCP 接入外部工具/数据源，skill 告诉 agent 如何完成一类任务）。

### Stage 6 — Browser Agent

用 Playwright 做网页观察和点击，加安全限制，处理页面变化/弹窗/加载失败。

### Stage 7 — 评测与安全

记录成功率、工具调用次数、成本、延迟，看 trace 分析失败原因，给危险工具加人工确认。

---

## 三、2026 年 Agent 学习优先级（仓库维护者观点）

| 优先级 | 方向 | 为什么值得投入 |
|--------|------|---------------|
| 1 | Claude Code / Codex-style coding agents | 真实代码库、shell、文件编辑、测试、权限、上下文压缩 |
| 2 | Agent harness engineering | 工具协议、权限、状态、反馈、回放、CI、评测 |
| 3 | OpenClaw / Hermes-style personal agents | 长运行、本地优先、跨应用、记忆、skills |
| 4 | Skills / MCP / A2A / ACP | 能力复用、工具连接、agent 间通信 |
| 5 | Evaluation and safety | 没有 eval 和权限边界的 agent 只能算 demo |

明确不建议：把精力重押在已经泛化成模板的**老式 crew/role-play 框架**上。

---

## 四、仓库质量评估

| 维度 | 评分 | 说明 |
|------|------|------|
| 内容深度 | ⭐⭐⭐⭐⭐ | 每个 Stage 都有具体产出物定义 |
| 可执行性 | ⭐⭐⭐⭐⭐ | 每步都有阅读材料+产出要求 |
| 时效性 | ⭐⭐⭐⭐⭐ | 2026 年观点，紧跟当前技术趋势 |
| 社区活跃 | ⭐⭐⭐⭐ | Datawhale 社区支持，持续更新 |
| 学习曲线 | ⭐⭐⭐⭐ | 从零基础到高级循序渐进 |

---

## 五、总结与建议

**Agent-Learning-Hub 是目前中文社区质量最高的 Agent 学习路线图**，没有之一。它最大的价值不是"收集链接"而是"定义路径"——告诉你先学什么、后学什么、每步学到什么程度算过关。

适合人群：
- LLM 应用开发者想转型 Agent 方向
- 已有 agent 基础想系统补全知识盲区
- 团队/公司需要 agent 培训材料

建议使用方式：**逐 Stage 执行，不打勾不跳过**。前 3 个 Stage 大约需要 2-4 周全职投入。

---

*报告基于仓库 README 及 ANTHROPIC/OPENAI 官方文档综合整理，核心观点来自仓库维护者。*
