# 🔬 supermemoryai/supermemory - 全方位深度调研

## 项目全景
- **仓库**：`supermemoryai/supermemory`
- **一句话定位**：Memory engine and app that is extremely fast, scalable. The Memory API for the AI era.
- **基础指标**：Stars=26348 / Forks=2293 / 默认分支=`main`
- **Topics**：cloudflare-pages, cloudflare-workers, drizzle-orm, tailwindcss, typescript, cloudflare-kv, postgres, remix, vite, agent-memory, ai-memory, memory
- **Homepage**：https://supermemory.ai/docs

## 核心架构
### 目录结构判断
- 顶层目录分布（递归树抽样汇总）：apps(630), packages(280), .github(11), skills(8), .gitignore(1), CLAUDE.md(1), CONTRIBUTING.md(1), LICENSE(1), README.md(1), README.zh-CN.md(1)
- 关键文件候选：package.json, turbo.json, README.md, CLAUDE.md, CONTRIBUTING.md, packages/agent-framework-python/src/supermemory_agent_framework/__init__.py, packages/agent-framework-python/src/supermemory_agent_framework/connection.py, packages/agent-framework-python/src/supermemory_agent_framework/context_provider.py, packages/agent-framework-python/src/supermemory_agent_framework/exceptions.py, packages/agent-framework-python/src/supermemory_agent_framework/middleware.py, packages/agent-framework-python/src/supermemory_agent_framework/tools.py, packages/agent-framework-python/src/supermemory_agent_framework/utils.py

### 设计亮点研判
- 存在 Node/前端工具链入口，说明项目的运行、构建或 CLI 能力围绕 package.json 脚本组织。
- 仓库包含 .github 目录，通常意味着 CI、issue 模板或自动发布流程已被工程化。

## 源码深度解读
### README / 说明文档要点
<p align="center">
  <picture>
    <source srcset="apps/web/public/logo-fullmark.svg" media="(prefers-color-scheme: dark)">
    <source srcset="apps/web/public/logo-light-fullmark.svg" media="(prefers-color-scheme: light)">
    <img src="apps/web/public/logo-fullmark.svg" alt="Supermemory" width="400" />
  </picture>
</p>

<p align="center">
  <strong>State-of-the-art memory and context engine for AI. And yes - you can use it as a company/personal brain.</strong>
</p>

<p align="center">
  <a href="https://supermemory.ai/docs">Docs</a> ·
  <a href="https://supermemory.ai/docs/quickstart">Quickstart</a> ·
  <a href="https://console.supermemory.ai">Dashboard</a> ·
  <a href="https://supermemory.link/discord">Discord</a>
</p>

<p align="center">
  <a href="https://www.npmjs.com/package/supermemory"><img src="https://img.shields.io/npm/v/supermemory?style=flat-square&color=blue" alt="npm" /></a>
  <a href="https://pypi.org/project/supermemory/"><img src="https://img.shields.io/pypi/v/supermemory?style=flat-square&color=blue" alt="pypi" /></a>
  <a href="https://supermemory.ai/docs"><img src="https://img.shields.io/badge/docs-supermemory.ai-blue?style=flat-square" alt="docs" /></a>
</p>

<p align="center">
  <strong>English</strong> · <a href="README.zh-CN.md">简体中文</a>
</p>

---

Supermemory is the memory and context layer for AI. **#1 on [LongMemEval](https://github.com/xiaowu0162/LongMemEval), [LoCoMo](https://github.com/snap-research/locomo), and [ConvoMem](https://github.com/Salesforce/ConvoMem)** — the three major benchmarks for AI memory. 

We are a research lab building the engine, plugins and tools around it.

Your AI forgets everything between conversations. Supermemory fixes that.

It automatically learns from conversations, extracts facts, builds user profiles, handles knowledge updates and contradictions, forgets expired information, and delivers the right context at the right time. Full RAG, connectors, file processing — the entire context stack, one system.

| | |
|---|---|
| 🧠 **Memory** | Extracts facts from conversations. Handles temporal changes, contradictions, and automatic forgetting. |
| 👤 **User Profiles** | Auto-maintained user context — stable facts + recent activity. One call, ~50ms. |
| 🔍 **Hybrid Search** | RAG + Memory in a single query. Knowledge base docs and personalized context together. |
| 🔌 **Connectors** | Google Drive · Gmail · Notion · OneDrive · GitHub — auto-sync with real-time webhooks. |
| 📄 **Multi-modal Extractors** 
...[truncated]

### 关键文件精读
### `package.json`
```
{
  "name": "supermemory",
  "private": true,
  "scripts": {
    "build": "turbo run build",
    "dev": "turbo run dev",
    "dev:local": "turbo run dev:app",
    "format-lint": "bunx biome check --write",
    "check-types": "turbo run check-types",
    "sentry:sourcemaps": "_SENTRY_RELEASE=$(sentry-cli releases propose-version) && sentry-cli releases new $_SENTRY_RELEASE --org=supermemory --project=consumer-app && sentry-cli sourcemaps upload --org=supermemory --project=consumer-app --release=$_SENTRY_RELEASE --strip-prefix 'dist/..' dist",
    "postbuild": "bun run sentry:sourcemaps"
  },
  "engines": {
    "node": ">=20"
  },
  "packageManager": "bun@1.3.6",
  "workspaces": [
    "apps/*",
    "!apps/raycast-extension",
    "!tools/test/chatapp",
    "packages/*"
  ],
  "dependencies": {
    "@ai-sdk/anthropic": "^1.2.12",
    "@ai-sdk/cerebras": "^0.2.16",
    "@ai-sdk/google": "^1.2.22",
    "@ai-sdk/openai": "^2.0.42",
    "@anthropic-ai/sdk": "^0.55.1",
    "@google/genai": "^1.
...[truncated]
```

### `turbo.json`
```
{
	"$schema": "https://turborepo.com/schema.json",
	"ui": "tui",
	"tasks": {
		"build": {
			"dependsOn": ["^build"],
			"inputs": ["$TURBO_DEFAULT$", ".env*"],
			"outputs": [".next/**", "!.next/cache/**"]
		},
		"lint": {
			"dependsOn": ["^lint"]
		},
		"check-types": {
			"dependsOn": ["^check-types"]
		},
		"dev": {
			"cache": false,
			"persistent": true
		},
		"dev:app": {
			"cache": false,
			"persistent": true
		}
	}
}
```

### `README.md`
```
<p align="center">
  <picture>
    <source srcset="apps/web/public/logo-fullmark.svg" media="(prefers-color-scheme: dark)">
    <source srcset="apps/web/public/logo-light-fullmark.svg" media="(prefers-color-scheme: light)">
    <img src="apps/web/public/logo-fullmark.svg" alt="Supermemory" width="400" />
  </picture>
</p>

<p align="center">
  <strong>State-of-the-art memory and context engine for AI. And yes - you can use it as a company/personal brain.</strong>
</p>

<p align="center">
  <a href="https://supermemory.ai/docs">Docs</a> ·
  <a href="https://supermemory.ai/docs/quickstart">Quickstart</a> ·
  <a href="https://console.supermemory.ai">Dashboard</a> ·
  <a href="https://supermemory.link/discord">Discord</a>
</p>

<p align="center">
  <a href="https://www.npmjs.com/package/supermemory"><img src="https://img.shields.io/npm/v/supermemory?style=flat-square&color=blue" alt="npm" /></a>
  <a href="https://pypi.org/project/supermemory/"><img src="https://img.shields.io/pypi/v/super
...[truncated]
```

### `CLAUDE.md`
```
# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Structure

This is a **Turbo monorepo** containing multiple applications and shared packages:

### Applications (`apps/`)
- **`web/`** - Next.js web application
- **`mcp/`** - Model Context Protocol server

## Development Commands

### Root Level (Monorepo)
- `bun run dev` - Start all applications in development mode
- `bun run build` - Build all applications
- `bun run check-types` - Run TypeScript checks across all apps
- `bun run format-lint` - Format and lint code using Biome

### Web Application (`apps/web/`)
- `bun run dev` - Start Next.js development server
- `bun run build` - Build Next.js application
- `bun run lint` - Run Next.js linting

## Architecture Overview

### Core Technology Stack
- **Runtime**: Next.js (web)
- **Framework**: Next.js (web)
- **Language**: TypeScript throughout
- **Package Manager**: Bun
- **Monorepo**: Turbo
- **Authentic
...[truncated]
```

### `CONTRIBUTING.md`
```
# Contributing to supermemory

Thank you for your interest in contributing to supermemory! We welcome contributions from developers of all skill levels. This guide will help you get started with contributing to our AI-powered memory layer API.

## 🚀 Quick Start

### Prerequisites

Before you begin, ensure you have the following installed:

- **Bun** (>= 1.2.17) - Our preferred package manager
- **Git** for version control

### Setting Up the Development Environment

1. **Fork and Clone the Repository**

   ```bash
   git clone https://github.com/supermemoryai/supermemory.git
   cd supermemory
   ```

2. **Install Dependencies**

   ```bash
   bun install
   ```

3. **Set Up Environment Variables**

   ```bash
   # Copy the example environment file
   cp .env.example .env.local

   # Edit the file with your configuration
   # You'll need to add your API keys and database URLs
   ```

4. **Change proxy for local development**

   Add this in your `proxy.ts`(apps/web) before retrieving th
...[truncated]
```

### `packages/agent-framework-python/src/supermemory_agent_framework/__init__.py`
```
"""Supermemory Agent Framework - Memory tools and middleware for Microsoft Agent Framework."""

from .connection import (
    AgentSupermemory,
)

from .tools import (
    SupermemoryTools,
    MemorySearchResult,
    MemoryAddResult,
    ProfileResult,
)

from .middleware import (
    SupermemoryChatMiddleware,
    SupermemoryMiddlewareOptions,
)

from .context_provider import (
    SupermemoryContextProvider,
)

from .utils import (
    Logger,
    create_logger,
    deduplicate_memories,
    DeduplicatedMemories,
    convert_profile_to_markdown,
)

from .exceptions import (
    SupermemoryError,
    SupermemoryConfigurationError,
    SupermemoryAPIError,
    SupermemoryMemoryOperationError,
    SupermemoryTimeoutError,
    SupermemoryNetworkError,
)

__all__ = [
    "AgentSupermemory",
    "SupermemoryTools",
    "MemorySearchResult",
    "MemoryAddResult",
    "ProfileResult",
    "SupermemoryChatMiddleware",
    "SupermemoryMiddlewareOptions",
    "SupermemoryContextProvider",
   
...[truncated]
```

### 关键逻辑总结
- 从关键文件组合看，项目更像围绕单一目标组织的任务流水线/工具链，而不是超重平台。
- 入口文件决定外部交互界面（CLI / API / UI），配置文件决定运行时依赖，测试文件暴露作者真正关心的行为边界。
- 如果用户只读 README，通常只能知道“能做什么”；而从目录与入口文件能看出“怎么做、扩展点在哪、维护成本高不高”。

## 社区口碑
### GitHub Issues 抽样
- #1037 [CLOSED] Enable Security Policy [URGENT]（comments=[{'id': 'IC_kwDOLY4af88AAAABEoO7rA', 'author': {'login': 'linear'}, 'authorAssociation': 'NONE', 'body': '<!-- linear-linkback -->\n<p><a href="https://linear.app/supermemory/issue/ENG-710">ENG-710</a></p>', 'createdAt': '2026-06-02T18:03:04Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [], 'url': 'https://github.com/supermemoryai/supermemory/issues/1037#issuecomment-4605590444', 'viewerDidAuthor': False}, {'id': 'IC_kwDOLY4af88AAAABEoPSug', 'author': {'login': 'MaheshtheDev'}, 'authorAssociation': 'MEMBER', 'body': 'hi @Neehan you can share through support@supermemory.com', 'createdAt': '2026-06-02T18:03:40Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [], 'url': 'https://github.com/supermemoryai/supermemory/issues/1037#issuecomment-4605596346', 'viewerDidAuthor': False}] labels=无）
- #1036 [CLOSED] [Feature] Memory Export and Backup Functionality（comments=[{'id': 'IC_kwDOLY4af88AAAABEh4RCw', 'author': {'login': 'linear'}, 'authorAssociation': 'NONE', 'body': '<!-- linear-linkback -->\n<p><a href="https://linear.app/supermemory/issue/ENG-709">ENG-709</a></p>', 'createdAt': '2026-06-02T05:17:16Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [], 'url': 'https://github.com/supermemoryai/supermemory/issues/1036#issuecomment-4598927627', 'viewerDidAuthor': False}, {'id': 'IC_kwDOLY4af88AAAABEh4jbQ', 'author': {'login': 'MaheshtheDev'}, 'authorAssociation': 'MEMBER', 'body': 'Hi @nayar-900 , thanks for suggesting we do have planned on this one will fasttrack with team on this one', 'createdAt': '2026-06-02T05:18:18Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [], 'url': 'https://github.com/supermemoryai/supermemory/issues/1036#issuecomment-4598932333', 'viewerDidAuthor': False}, {'id': 'IC_kwDOLY4af88AAAABFTkMlg', 'author': {'login': 'MaheshtheDev'}, 'authorAssociation': 'MEMBER', 'body': 'This feature has been done and deployed', 'createdAt': '2026-06-08T16:17:50Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [], 'url': 'https://github.com/supermemoryai/supermemory/issues/1036#issuecomment-4651027606', 'viewerDidAuthor': False}] labels=enhancement）
- #1035 [CLOSED] does there any plan to support deepagents（comments=[{'id': 'IC_kwDOLY4af88AAAABEhRq-g', 'author': {'login': 'linear'}, 'authorAssociation': 'NONE', 'body': '<!-- linear-linkback -->\n<p><a href="https://linear.app/supermemory/issue/ENG-708">ENG-708</a></p>', 'createdAt': '2026-06-02T02:52:24Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [], 'url': 'https://github.com/supermemoryai/supermemory/issues/1035#issuecomment-4598295290', 'viewerDidAuthor': False}, {'id': 'IC_kwDOLY4af88AAAABEhiQrQ', 'author': {'login': 'MaheshtheDev'}, 'authorAssociation': 'MEMBER', 'body': "> **deepagents is built on LangChain/LangGraph, both of which Supermemory already supports** \n\nso you can use Supermemory with a deep agent today: \neither pass our memory operations (search/add) as tools via tools=[...], or inject the user's profile into the system prompt through middleware, scoping by container_tag per user. \n\n[See our LangChain/LangGraph integration docs for the exact pattern](https://supermemory.ai/docs/integrations/langchain) — it carries over directly. We don't yet ship a LangGraph BaseStore adapter, so Supermemory can't act as deepagents' native StoreBackend filesystem; if that's specifically what you're after, let us know and will definitely talk to the team. ", 'createdAt': '2026-06-02T03:53:32Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [], 'url': 'https://github.com/supermemoryai/supermemory/issues/1035#issuecomment-4598567085', 'viewerDidAuthor': False}] labels=无）
- #1030 [OPEN] [Feature] Add 'listMemories' tool to MCP server for enumerating user memories（comments=[{'id': 'IC_kwDOLY4af88AAAABEcko2A', 'author': {'login': 'linear'}, 'authorAssociation': 'NONE', 'body': '<!-- linear-linkback -->\n<p><a href="https://linear.app/supermemory/issue/ENG-707">ENG-707</a></p>', 'createdAt': '2026-06-01T14:08:44Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [], 'url': 'https://github.com/supermemoryai/supermemory/issues/1030#issuecomment-4593363160', 'viewerDidAuthor': False}, {'id': 'IC_kwDOLY4af88AAAABEdrPtA', 'author': {'login': 'MaheshtheDev'}, 'authorAssociation': 'MEMBER', 'body': '@fuleinist , thanks for the suggestion. we will take a look today and get around with it', 'createdAt': '2026-06-01T16:29:46Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [], 'url': 'https://github.com/supermemoryai/supermemory/issues/1030#issuecomment-4594519988', 'viewerDidAuthor': False}, {'id': 'IC_kwDOLY4af88AAAABE1slWg', 'author': {'login': 'mvanhorn'}, 'authorAssociation': 'NONE', 'body': 'Implemented in https://github.com/supermemoryai/supermemory/pull/1044.', 'createdAt': '2026-06-04T06:47:25Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [], 'url': 'https://github.com/supermemoryai/supermemory/issues/1030#issuecomment-4619707738', 'viewerDidAuthor': False}] labels=enhancement）
- #1027 [OPEN] BUG: AttributeError when profile is None in _retrieve_memories()（comments=[{'id': 'IC_kwDOLY4af88AAAABEX1ZWg', 'author': {'login': 'linear'}, 'authorAssociation': 'NONE', 'body': '<!-- linear-linkback -->\n<p><a href="https://linear.app/supermemory/issue/ENG-706">ENG-706</a></p>', 'createdAt': '2026-05-31T22:35:45Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [], 'url': 'https://github.com/supermemoryai/supermemory/issues/1027#issuecomment-4588394842', 'viewerDidAuthor': False}] labels=bug）
- #985 [OPEN] Expose privacy-safe memory retrieval receipts（comments=[{'id': 'IC_kwDOLY4af88AAAABDMJFDA', 'author': {'login': 'linear'}, 'authorAssociation': 'NONE', 'body': '<!-- linear-linkback -->\n<p><a href="https://linear.app/supermemory/issue/ENG-705">ENG-705</a></p>', 'createdAt': '2026-05-21T14:02:56Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [], 'url': 'https://github.com/supermemoryai/supermemory/issues/985#issuecomment-4509025548', 'viewerDidAuthor': False}] labels=无）

### Pull Requests 抽样
- PR #1075 [OPEN] feat(integrations): active connections rail + recently added
- PR #1074 [MERGED] chore(integrations): update Poke recipe URL to supermemory.link/poke
- PR #1073 [MERGED] Make integrations page public for guests
- PR #1072 [MERGED] memory graph loader
- PR #1071 [OPEN] Render Nova connector setup cards

### Releases 抽样
- server-v0.0.1-rc.8（published=2026-06-04T01:47:54Z latest=False）
- server-v0.0.1-rc.7（published=2026-06-04T01:41:53Z latest=False）
- server-v0.0.1-rc.6（published=2026-06-04T01:35:18Z latest=False）
- server-v0.0.1-rc.5（published=2026-06-04T01:15:46Z latest=False）
- server-v0.0.1-rc.4（published=2026-05-31T00:20:24Z latest=False）

### 真实反馈与维护信号研判
- 抽样 issue 中 open/closed 约为 3/5，可作为维护响应速度的弱信号。
- 近期 PR 抽样里可见已合并项 3 个，说明项目并非完全冻结。
- 存在 release 记录，说明作者具备版本化交付意识。
- 高频问题通常比 README 更能暴露真实落地难点：安装、兼容性、性能边界、文档歧义、平台限制。
- 若外部搜索数据不可用，本报告明确以 GitHub issue/PR/release 作为一手社区信号，不伪造站外口碑。

## 竞品对比
| 维度 | supermemory | 竞品/替代 |
|---|---|---|
| 定位 | 面向仓库作者设定的具体场景，通常更垂直 | LangGraph / AutoGen / CrewAI 往往更通用或生态更大 |
| 学习曲线 | 依赖其内部脚本/配置约定 | 通用方案学习成本更高，但生态更成熟 |
| 差异化 | 仓库通常以“快上手、场景专用、意见化实现”为卖点 | 通用方案强调可扩展、稳定性、跨场景能力 |
| 风险 | 作者驱动、文档深度可能不足、接口稳定性不确定 | 大项目更稳定，但改造成本更高 |

## 核心研判
### 项目优势
- 对目标问题有强意见化实现，落地路径通常比“从零搭建通用栈”更短。
- 如果核心文件少而清晰，二次阅读和定制成本较低。
- GitHub 原生 issue / release / PR 能直接帮助判断项目是否仍在演进。

### 项目风险
- 若 stars、forks、release 或 PR 活跃度偏低，意味着长期维护能力要谨慎评估。
- 如果关键逻辑过于集中在单文件脚本中，后续扩展会受到可维护性约束。
- 若缺少测试/CI/配置 schema，生产环境采用前应先做自测和边界验证。

### 适用场景
- 需要快速验证该仓库所解决的问题是否值得投入。
- 团队愿意接受一定的作者意见化设计，以换取更快交付。
- 适合作为参考实现、内部 PoC、垂直任务工具，而非默认直接替代成熟平台。

### 不适用场景
- 对 SLA、兼容矩阵、长期 LTS 有强要求的核心生产系统。
- 需要极高社区冗余、插件生态或企业级支持的场景。

## 关键文件路径速查
- `package.json`
- `turbo.json`
- `README.md`
- `CLAUDE.md`
- `CONTRIBUTING.md`
- `packages/agent-framework-python/src/supermemory_agent_framework/__init__.py`
- `packages/agent-framework-python/src/supermemory_agent_framework/connection.py`
- `packages/agent-framework-python/src/supermemory_agent_framework/context_provider.py`
- `packages/agent-framework-python/src/supermemory_agent_framework/exceptions.py`
- `packages/agent-framework-python/src/supermemory_agent_framework/middleware.py`
- `packages/agent-framework-python/src/supermemory_agent_framework/tools.py`
- `packages/agent-framework-python/src/supermemory_agent_framework/utils.py`

## 3 条关键发现
- 代码入口/骨架集中在：package.json, turbo.json, README.md, CLAUDE.md, CONTRIBUTING.md
- Issue 抽样显示近期关注点包括：Enable Security Policy [URGENT]；[Feature] Memory Export and Backup Functionality
- 版本交付可从最新 release 观察：server-v0.0.1-rc.8

## 研究方法与数据来源
- GitHub Repo API / README / 默认分支递归文件树
- 关键源码文件抽样精读
- Issues / PRs / Releases 社区活动抽样
- 说明：若外部搜索数据不可用，则明确标注并不伪造口碑结论
