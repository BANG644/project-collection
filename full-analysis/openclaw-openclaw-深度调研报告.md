openclaw/openclaw — 深度调研报告🦞 一句话定位：GitHub Star 第三多的 AI Agent 平台（37.3 万⭐）——由同一作者维护的跨平台 AI 助手，支持 Any OS / Any Platform，以 skill 系统为核心扩展机制。📋 基本档案字段值⭐ Stars373,050🗓️ 创建时间2025-11-24🔄 最近提交2026-05-19（当天活跃）🔖 默认分支main💻 主要语言TypeScript🦞 Slogan"Your own personal AI assistant. Any OS. Any Platform. The lobster way."🏛️ 架构全景openclaw 是一个相当新的项目（2025年11月创建），但已经非常活跃。从仓库结构和 Issue 可见，其核心架构包括：openclaw/├── agent/                  ← Agent 核心运行时├── skills/                ← 内置 Skill 目录├── tools/                 ← Tool 框架（OpenClaw tool system）├── gateway/               ← Gateway 服务├── docs/                  ← 文档└── 各 channel 实现         ← WeChat/Discord/Telegram/QQ 等核心创新：skill 系统——将 AI Agent 的能力封装为可复用的 Skill 包，类似于 npm 包的概念，形成 SkillHub 生态。🔧 核心源码解读Agent RuntimeAgent 核心是一个 TypeScript 实现的运行时，负责：会话管理（多轮对话上下文）Tool 调用编排Skill 加载与执行多 channel 消息路由Skill 系统（关键创新）Skills 是 openclaw 的核心扩展机制，参考了 obra/superpowers 的框架思想。Skills 可以：定义新的 Tool处理特定类型的任务封装为可分发的包Tool Frameworkopenclaw 的 Tool 系统是 OpenAI-compatible 的，支持 function calling 格式，并且有自己的 MTClaw（Multi-Tool Claw）优化——Issue #84024 提到正在做 5-7x 的 tool call 性能优化。🌐 全网口碑分析从 GitHub Issues（2026-05-19）可见一个非常活跃的维护状态：好评共识（从 issue 标签推断）Skill 系统设计得到开发者认可（大量社区贡献的 skill）跨平台能力实用（WeChat、Discord、Telegram、QQ 均支持）Gateway 设计受到好评踩坑高发区（从 issue 分析）Bug 类型影响严重程度WeChat channel 消息响应慢体验P1xAI OAuth 被 Cloudflare 阻断认证P2Feishu xlsx 文件发送失败消息丢失P2Discord 事件抑制 final reply消息丢失P2Windows SessionStart hook 错误Windows 用户-观察：openclaw 在国内（微信、飞书）和海外（Discord）渠道上都有深度集成，这是一个独特的跨平台定位。争议焦点平台监管

### 风险

：微信/飞书等平台的政策

### 风险

可能导致 channel 被封Windows 支持：SessionStart hook 在 Windows 上有兼容性 bug，修复中🔍 竞品对比竞品Stars定位vs OpenClawClaude Code-Anthropic 官方 Agent CLI闭源，OpenClaw 开源可自托管Aider-终端 AI 编程工具更专注编程，OpenClaw 更通用Cursor-AI 代码编辑器桌面应用，OpenClaw 是 CLI/ServerCoze-字节跳动 Bot 平台云服务，OpenClaw 可自托管LangChain Agents-Agent 开发框架面向开发者，OpenClaw 面向终端用户OpenClaw 的独特性：它是目前 Star 数最高的开源 Agent 平台，且专注于「自托管 + 跨平台消息 channel」的组合，这个定位在竞品中是独特的。

## 🎯 核心研判

核心

### 优势

开源可自托管 — 对企业用户有吸引力（数据不经过第三方）跨平台 channel 集成 — 唯一一个同时支持微信/飞书/Discord/Telegram/QQ 的开源 Agent 框架Skill 生态 — 类似 npm 的 SkillHub，分发门槛低极高的社区活跃度 — 每天有大量 issue/PR，维护质量高主要

### 风险

平台政策

### 风险

 — 微信/QQ 等平台的自动化接口政策不稳定Cloudflare xAI 问题 — OAuth 被阻断说明依赖方生态脆弱Windows 支持不完善 — SessionStart hook bug 影响 Windows 用户体验新项目

### 风险

 — 2025年11月才创建，API 稳定性有待验证趋势判断openclaw 正处于快速生长期（Issue #84024 提到的 MTClaw 性能优化 5-7x 说明核心架构还在快速迭代）。它的差异化在于「开源 + 自托管 + 跨平台 channel」，在当前 AI Agent 隐私化和本土化趋势下，这个定位非常有战略价值。数据来源：gh repo view / gh issue list / gh release list，调研时间 2026-05-19
