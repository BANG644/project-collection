# 🤖 AstrBot — 多平台开源 Agent 聊天框架

> **仓库**: [AstrBotDevs/AstrBot](https://github.com/AstrBotDevs/AstrBot)
> **Stars**: 37,019⭐ | **Forks**: 2,572 | **Issues**: 1,330 | **今日 Trending**: +330⭐
> **语言**: Python (3.10+) | **许可证**: AGPL-3.0 | **创建**: 2022-12-08 | **最近提交**: 2026-07-20
> **官网**: [astrbot.app](https://astrbot.app) | **默认分支**: `master`
> **定位**: 平台无关的开源 Agent 聊天基础设施——"一次配置，跑遍所有主流 IM 平台"，自述可作 OpenClaw 替代

## 项目亮点

- **平台无关 Agent 核心**：框架与 IM 平台解耦，所有平台共用同一套 LLM 交互层、知识库与人设；写一个插件，QQ/微信/飞书/Telegram 全都能用
- **中国 IM 覆盖最全**：QQ、个人微信（扫码）、企业微信、公众号、飞书、钉钉 + 西方 Telegram/Discord/Slack/LINE——国产 IM 支持是最大差异化壁垒
- **Agent 可执行沙箱**：代码执行、Shell 调用隔离在沙箱中运行，会话级资源复用，既安全又高效
- **1000+ 插件生态 + 原生 MCP/Skills**：插件市场一键安装；原生支持 MCP 工具与 Skills，让 Bot 真正"能干活"而非只聊天
- **开箱即用的 Agent 能力**：知识库（Markitdown 解析 + 稠密/BM25 混合检索，针对中文优化）、自动上下文压缩、语音（10+ TTS / STT）、WebUI、主动对话

## 核心架构

```
astrbot/
├── api/                      # 平台/Provider/事件抽象层（解耦核心与 IM）
│   ├── platform/ provider/   #   LLM Provider 与 IM 平台适配器
│   ├── event/filter/         #   事件过滤管线
│   └── message_components.py #   跨平台消息组件统一模型
├── core/agent/               # Agent 运行时
│   ├── agent.py              #   对话/Agent 主循环
│   ├── context/              #   上下文管理：compressor / truncator / token_counter
│   ├── mcp_client.py         #   原生 MCP 工具接入
│   ├── handoff.py hooks.py   #   子 Agent 交接 / 生命周期钩子
│   ├── runners/              #   Dify/Coze/DashScope/DeerFlow 等外部 Agent Runner 适配
│   └── tool.py tool_executor.py  # 工具定义与执行（含沙箱）
├── cli/                      # astrbot init / run / plug / conf
└── builtin_stars/            # 内置指令（admin/conversation/provider...）
```

核心思路是**"中间层"**：左侧接各种 IM 平台适配器，右侧接各种 LLM Provider，中间是统一的 Agent 运行时。平台适配与 Agent 逻辑解耦，因此"写一次 Bot 逻辑，部署到所有平台"。上下文压缩（`core/agent/context/`）保证长对话不爆 token；Agent Sandbox 把代码/Shell 执行隔离，避免裸跑风险。

## 应用场景与启发

- **跨平台统一客服/社群运营**：一个 Bot 同时存在于十几个聊天软件，不同群不同人问的是同一个 AI
- **个人 AI 伴侣 / 角色扮演**：人设编辑 + 主动对话 + 长期记忆插件，低成本搭建有"性格"的助手
- **企业知识库问答**：混合检索知识库 + MCP 工具调用，接入内部系统做自动化
- **对同类需求的启发**：AstrBot 的"平台无关核心"是做跨渠道 Agent 的标准范式——**把"渠道差异"收敛到适配器层，把"Agent 逻辑"留在平台无关的核心**。当你要支持多个入口（IM/Web/API）时，应先定义统一的消息组件模型（`message_components.py` 思路）与事件过滤管线，再逐个写适配器，而不是为每个渠道复制一套逻辑。这与本项目已调研的 `oomol-lab/open-connector`（Agent SaaS 连接器网关）解决的问题同向：都是"把 N 个外部系统的差异屏蔽掉"。

## 源码深度解读

**1. 平台无关的 Agent 主循环**
`astrbot/core/agent/agent.py` 是对话/Agent 编排中枢，接收 `api/event` 归一化后的事件，调用 LLM Provider，再经 `tool_executor` 执行工具（含沙箱）。关键在它不感知具体 IM——所有平台差异已在 `api/platform/` 适配层消化为统一消息组件。

**2. 上下文压缩（长对话不爆 token）**
`astrbot/core/agent/context/compressor.py` + `truncator.py` + `token_counter.py` 构成上下文管理三件套：
```python
# core/agent/context 设计意图（节选逻辑）
manager = ContextManager(config)          # 会话级上下文
compressed = compressor.compress(history) # 按 token 预算压缩/摘要旧轮次
truncated = truncator.truncate(compressed, max_tokens)
```
自动上下文压缩让长对话在有限窗口内保持连贯，是"生产可用聊天 Agent"的关键工程件。

**3. 外部 Agent Runner 适配**
`astrbot/core/agent/runners/` 下 `dify/`、`coze/`、`dashscope/`、`deerflow/` 等子目录把外部 Agent 平台封装成统一 Runner 接口（`tool_loop_agent_runner.py` 为本地 tool-loop 实现）。这种"外部编排可插拔"设计，使 AstrBot 既能自跑 Agent，也能把 Dify/Coze 当后端——避免被单一 Agent 框架锁定。

> ⚠️ 纠错：部分中文部署文章误称 AstrBot 为"Java+Spring 架构"，**实际仓库为 Python（`astrbot/` 包，已核实）**，请勿被过时文章误导。

## 全网口碑

- **势能**：2026 年 2 月约 17K⭐，6 月 34K⭐，7 月冲到 37K⭐，被列为"生态最全的开源 Agent 聊天框架"；官网称 200K+ 周活、1000+ 插件、100+ 贡献者
- **正面**：草根采用极盛（知乎/头条几十篇部署教程，覆盖 NAS/Docker/DeepSeek 接入/AI 伴侣）；用户实测"Bot 逻辑写一次，QQ+Telegram 都能跑""故意弄坏 API Key 后故障切换按预期工作"；国产 IM 覆盖无人能及
- **痛点**：学习曲线——部署简单但要吃透 Agent/插件系统需啃文档；QQ 稳定性依赖 NapCatQQ 等第三方协议，偶有波动；社区分散在 15 个群，信息检索成本高；AGPL-3.0 强 copyleft 对商业嵌入不友好；文档以中文为主
- **定位共识**：被公认为"中国 IM 市场的 Agent 框架领导者"，"OpenClaw 替代"叙事成立，但插件生态与 OpenClaw Skills 并不互通

## 竞品对比 + 核心研判

| 维度 | AstrBot | LangBot | OpenClaw | Dify |
|------|---------|---------|----------|------|
| 国产 IM 覆盖 | 最全 | 强 | 中 | 弱(非 IM 向) |
| 插件生态 | 1000+ | 中 | Skills | 中 |
| 沙箱 | ✅ | ✅ | ✅ | 部分 |
| 知识库 | ✅混合检索 | ✅ | 依赖外接 | ✅ |
| 协议 | AGPL-3.0 | 开源 | 开源 | 开源 |
| 定位 | 跨 IM Agent | 中文 IM Agent | Agent 运行时 | LLMOps 平台 |

**核心研判**
- **优势**：踩中"国产 IM + 私域/社群运营"刚需，平台无关核心 + 千级插件形成强网络效应；部署门槛低（uv 一行 + Docker + 桌面端），从个人到生产全覆盖
- **风险**：AGPL-3.0 限制商业产品化；对第三方微信/QQ 协议的依赖是稳定性与合规隐患；文档与社区中文为主，国际化天花板明显；Issue 1,330 未关闭量偏大，反映维护负载
- **趋势**：从"聊天机器人"演进为"Agent 基础设施"（沙箱/MCP/Skills/知识库齐备），与 OpenClaw 正面竞争；多平台统一正成为刚需而非加分项
- **启发**：做面向国内的 Agent 产品时，**"渠道适配层"本身就是护城河**——谁先把最多 IM 的差异屏蔽掉，谁就赢得私域/社群场景。AstrBot 用"平台无关核心 + 适配器"解耦，是这类中间层产品的标准架构范本

## 关键文件速查

| 路径（master 分支） | 作用 |
|------|------|
| `astrbot/core/agent/agent.py` | Agent 对话/编排主循环 |
| `astrbot/core/agent/context/` | 上下文压缩/截断/token 计数 |
| `astrbot/core/agent/mcp_client.py` | 原生 MCP 工具接入 |
| `astrbot/core/agent/tool_executor.py` | 工具执行（含沙箱） |
| `astrbot/core/agent/runners/` | Dify/Coze/DashScope/DeerFlow Runner 适配 |
| `astrbot/api/platform/` `api/provider/` | IM 平台与 LLM Provider 适配器 |
| `astrbot/api/message_components.py` | 跨平台统一消息组件模型 |
| `astrbot/api/event/filter/` | 事件过滤管线 |
| `astrbot/cli/commands/` | `init/run/plug/conf/password` 命令 |
| `astrbot/builtin_stars/` | 内置指令（admin/conversation/provider） |
