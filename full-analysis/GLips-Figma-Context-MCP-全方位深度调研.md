# 🔬 GLips/Figma-Context-MCP - 全方位深度调研

## 项目全景
- **仓库**：`GLips/Figma-Context-MCP`
- **一句话定位**：MCP server to provide Figma layout information to AI coding agents like Cursor
- **基础指标**：Stars=15046 / Forks=1190 / 默认分支=`main`
- **Topics**：ai, cursor, figma, mcp, typescript
- **Homepage**：https://www.framelink.ai/

## 核心架构
### 目录结构判断
- 顶层目录分布（递归树抽样汇总）：src(62), .github(5), scripts(4), .claude(1), .env.example(1), .gitignore(1), .nvmrc(1), .prettierrc(1), .release-please-manifest.json(1), CHANGELOG.md(1)
- 关键文件候选：package.json, tsconfig.json, README.md, CLAUDE.md, CONTRIBUTING.md, src/bin.ts, src/commands/fetch.ts, src/config.ts, src/extractors/built-in.ts, src/extractors/design-extractor.ts, src/extractors/index.ts, src/extractors/node-walker.ts

### 设计亮点研判
- 存在 Node/前端工具链入口，说明项目的运行、构建或 CLI 能力围绕 package.json 脚本组织。
- 仓库包含 .github 目录，通常意味着 CI、issue 模板或自动发布流程已被工程化。

## 源码深度解读
### README / 说明文档要点
<a href="https://www.framelink.ai/?utm_source=github&utm_medium=referral&utm_campaign=readme" target="_blank" rel="noopener">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://www.framelink.ai/github/HeaderDark.png" />
    <img alt="Framelink" src="https://www.framelink.ai/github/HeaderLight.png" />
  </picture>
</a>

<div align="center">
  <h1>Framelink MCP for Figma</h1>
  <h3>Give your coding agent access to your Figma data.<br/>Implement designs in any framework in one-shot.</h3>
  <a href="https://npmcharts.com/compare/figma-developer-mcp?interval=30">
    <img alt="weekly downloads" src="https://img.shields.io/npm/dm/figma-developer-mcp.svg">
  </a>
  <a href="https://github.com/GLips/Figma-Context-MCP/blob/main/LICENSE">
    <img alt="MIT License" src="https://img.shields.io/github/license/GLips/Figma-Context-MCP" />
  </a>
  <a href="https://framelink.ai/discord">
    <img alt="Discord" src="https://img.shields.io/discord/1352337336913887343?color=7389D8&label&logo=discord&logoColor=ffffff" />
  </a>
  <br />
  <a href="https://twitter.com/glipsman">
    <img alt="Twitter" src="https://img.shields.io/twitter/url?url=https%3A%2F%2Fx.com%2Fglipsman&label=%40glipsman" />
  </a>
</div>

<br/>

Give [Cursor](https://cursor.sh/) and other AI-powered coding tools access to your Figma files with this [Model Context Protocol](https://modelcontextprotocol.io/introduction) server.

When Cursor has access to Figma design data, it's **way** better at one-shotting designs accurately than alternative approaches like pasting screenshots.

<h3><a href="https://www.framelink.ai/docs/quickstart?utm_source=github&utm_medium=referral&utm_campaign=readme">See quickstart instructions →</a></h3>

## Demo

[Watch a demo of building a UI in Cursor with Figma design data](https://youtu.be/6G9yb-LrEqg)

[![Watch the video](https://img.youtube.com/vi/6G9yb-LrEqg/maxresdefault.jpg)](https://youtu.be/6G9yb-LrEqg)

## How it works

1. Open your IDE's chat (e.g. agent mode in Cursor).
2. Paste a link to a Figma file, frame, or group.
3. Ask Cursor to do something with the Figma file—e.g. implement the design.
4. Cursor will fetch the relevant metadata from Figma and use it to write your code.

This MCP server is specifically designed for use with Cursor. Before responding with context from the [Figma API](https://www.figma.com/developers/api), it simplifies and translates the response so only the most relevant layout and styling information is provided t
...[truncated]

### 关键文件精读
### `package.json`
```
{
  "name": "figma-developer-mcp",
  "version": "0.12.0",
  "mcpName": "io.github.GLips/Figma-Context-MCP",
  "description": "Give your coding agent access to your Figma data. Implement designs in any framework in one-shot.",
  "type": "module",
  "main": "dist/index.js",
  "bin": {
    "figma-developer-mcp": "dist/bin.js"
  },
  "files": [
    "dist",
    "README.md"
  ],
  "scripts": {
    "build": "tsup --dts",
    "type-check": "tsc --noEmit",
    "test": "vitest run",
    "start": "node dist/bin.js",
    "start:cli": "cross-env NODE_ENV=cli node dist/bin.js",
    "start:http": "node dist/bin.js",
    "dev": "cross-env NODE_ENV=development tsup --watch",
    "dev:cli": "cross-env NODE_ENV=development tsup --watch -- --stdio",
    "lint": "eslint .",
    "format": "prettier --write \"src/**/*.ts\"",
    "inspect": "pnpx @modelcontextprotocol/inspector",
    "benchmark:simplify": "tsx scripts/benchmark-simplify.ts",
    "prepack": "pnpm build"
  },
  "engines": {
    "node": ">=20.20
...[truncated]
```

### `tsconfig.json`
```
{
  "compilerOptions": {
    "baseUrl": "./",
    "rootDir": "src",
    "paths": {
      "~/*": ["./src/*"]
    },

    "target": "ES2022",
    "lib": ["ES2022", "DOM"],
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "resolveJsonModule": true,
    "verbatimModuleSyntax": true,
    "allowJs": true,
    "checkJs": true,

    /* EMIT RULES */
    "outDir": "./dist",
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "removeComments": true,

    "types": ["vitest/globals"],

    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true
  },
  "include": ["src/**/*"]
}
```

### `README.md`
```
<a href="https://www.framelink.ai/?utm_source=github&utm_medium=referral&utm_campaign=readme" target="_blank" rel="noopener">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://www.framelink.ai/github/HeaderDark.png" />
    <img alt="Framelink" src="https://www.framelink.ai/github/HeaderLight.png" />
  </picture>
</a>

<div align="center">
  <h1>Framelink MCP for Figma</h1>
  <h3>Give your coding agent access to your Figma data.<br/>Implement designs in any framework in one-shot.</h3>
  <a href="https://npmcharts.com/compare/figma-developer-mcp?interval=30">
    <img alt="weekly downloads" src="https://img.shields.io/npm/dm/figma-developer-mcp.svg">
  </a>
  <a href="https://github.com/GLips/Figma-Context-MCP/blob/main/LICENSE">
    <img alt="MIT License" src="https://img.shields.io/github/license/GLips/Figma-Context-MCP" />
  </a>
  <a href="https://framelink.ai/discord">
    <img alt="Discord" src="https://img.shields.io/discord/1352337336913887343?color=738
...[truncated]
```

### `CLAUDE.md`
```
# Framelink MCP for Figma

Framelink MCP for Figma is a Model Context Protocol (MCP) server that gives AI coding tools (Cursor, etc.) access to Figma design data. It fetches Figma files/nodes via the Figma API, simplifies the response to include only relevant layout and styling information, and serves it to AI clients.

## Build & Development Commands

```bash
pnpm install          # Install dependencies
pnpm build            # Build with tsup (outputs to dist/)
pnpm dev              # Development mode with watch + auto-restart (HTTP)
pnpm dev:cli          # Development mode (stdio)
pnpm test             # Run Vitest tests
pnpm type-check       # TypeScript type checking only
pnpm lint             # ESLint
pnpm format           # Prettier formatting
pnpm inspect          # Run MCP inspector for debugging
```

### Running the Server

```bash
pnpm start            # HTTP mode (default port 3333)
pnpm start:cli        # stdio mode for MCP clients
```

### Running a Single Test

```bash
pn
...[truncated]
```

### `CONTRIBUTING.md`
```
# Contributing to Framelink MCP for Figma

Thank you for your interest in contributing to the Framelink MCP for Figma! This guide will help you get started with contributing to this project.

## Philosophy

### Unix Philosophy for Tools

This project adheres to the Unix philosophy: tools should have one job and few arguments. We keep our tools as simple as possible to avoid confusing LLMs during calling. Configurable options that are more project-level (i.e., unlikely to change between requests for Figma data) are best set as command line arguments rather than being exposed as tool parameters.

### MCP Server Scope

The MCP server should only focus on **ingesting designs for AI consumption**. This is our core responsibility and what we do best. Additional features are best handled externally by other specialized tools. Examples of features that would be out of scope include:

- Image conversion, cropping, or other image manipulation
- Syncing design data to CMSes or databases
- Code ge
...[truncated]
```

### `src/bin.ts`
```
#!/usr/bin/env node

import { cli } from "cleye";
import { getServerConfig, UsageError } from "./config.js";
import { startServer } from "./server.js";
import { fetchCommand } from "./commands/fetch.js";

const argv = cli({
  name: "figma-developer-mcp",
  version: process.env.NPM_PACKAGE_VERSION ?? "unknown",
  flags: {
    figmaApiKey: {
      type: String,
      description: "Figma API key (Personal Access Token)",
    },
    figmaOauthToken: {
      type: String,
      description: "Figma OAuth Bearer token",
    },
    env: {
      type: String,
      description: "Path to custom .env file to load environment variables from",
    },
    port: {
      type: Number,
      description: "Port to run the server on",
    },
    host: {
      type: String,
      description: "Host to run the server on",
    },
    json: {
      type: Boolean,
      description:
        "Output data from tools in JSON format instead of YAML. Back-compat alias for --format=json.",
    },
    format: {
    
...[truncated]
```

### 关键逻辑总结
- 从关键文件组合看，项目更像围绕单一目标组织的任务流水线/工具链，而不是超重平台。
- 入口文件决定外部交互界面（CLI / API / UI），配置文件决定运行时依赖，测试文件暴露作者真正关心的行为边界。
- 如果用户只读 README，通常只能知道“能做什么”；而从目录与入口文件能看出“怎么做、扩展点在哪、维护成本高不高”。

## 社区口碑
### GitHub Issues 抽样
- #385 [CLOSED] No mcp tools to make designs?（comments=[{'id': 'IC_kwDON4uODc8AAAABFOAmbg', 'author': {'login': 'GLips'}, 'authorAssociation': 'OWNER', 'body': "Yeah, this doesn't handle authoring at the moment.", 'createdAt': '2026-06-08T03:35:50Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [], 'url': 'https://github.com/GLips/Figma-Context-MCP/issues/385#issuecomment-4645201518', 'viewerDidAuthor': False}] labels=无）
- #375 [OPEN] Feature request: expose image download/export support in the CLI（comments=[] labels=无）
- #364 [CLOSED] `download_figma_images` returns success, but no file is actually written to the local target（comments=[] labels=无）
- #363 [CLOSED] 下载素材失败（comments=[{'id': 'IC_kwDON4uODc8AAAABAX-2ng', 'author': {'login': 'GLips'}, 'authorAssociation': 'OWNER', 'body': "English is helpful—looks like you closed the other ticket that was in English. If it's the same, you can open it back up.", 'createdAt': '2026-04-25T16:55:55Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [], 'url': 'https://github.com/GLips/Figma-Context-MCP/issues/363#issuecomment-4320114334', 'viewerDidAuthor': False}] labels=无）
- #362 [CLOSED] Late `notifications/progress` after tool response crashes stdio transport ("unknown progress token")（comments=[{'id': 'IC_kwDON4uODc8AAAABAYIi1A', 'author': {'login': 'GLips'}, 'authorAssociation': 'OWNER', 'body': 'Thanks for the report! Should be fixed in the next release. LMK if not', 'createdAt': '2026-04-25T18:22:13Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [{'content': 'HEART', 'users': {'totalCount': 1}}], 'url': 'https://github.com/GLips/Figma-Context-MCP/issues/362#issuecomment-4320273108', 'viewerDidAuthor': False}] labels=无）
- #358 [CLOSED] Getting 403 on FrameLink MCP call in claude code even though MCP shows as connected（comments=[{'id': 'IC_kwDON4uODc7_Nd9j', 'author': {'login': 'GLips'}, 'authorAssociation': 'OWNER', 'body': "\nDid you follow [the troubleshooting steps in the docs](https://www.framelink.ai/docs/troubleshooting#cannot-access-file)?\n\n403 means you don't have permission to access the file. It's a Figma API error.\n\nWhen you get the error what does your coding agent say about it?\n\nIf you figure out the issue, let me know what it ends up being. I'd like to improve the error message that's sent back when this happens.", 'createdAt': '2026-04-20T14:34:49Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [], 'url': 'https://github.com/GLips/Figma-Context-MCP/issues/358#issuecomment-4281720675', 'viewerDidAuthor': False}, {'id': 'IC_kwDON4uODc7_PBjk', 'author': {'login': 'asifdotdev'}, 'authorAssociation': 'NONE', 'body': '\nThis is the error I\'m getting, I have added instructions to fallback to the Official MCP Figma server, it works fine with official MCP but their output mostly exceeds the text limit so I switched to FrameLink and it had been working good previously only has issues with SVG\'s inconsistencies.\nThe framelink was working fine a couple days ago with the same token but now its broken and gives me this.\nI have tried the troubleshooting. I\'m the owner of that figma file and everything is sorted.\n\n<img width="1058" height="266" alt="Image" src="https://github.com/user-attachments/assets/034408eb-531e-49e9-917e-65ddd25aa6bd" />', 'createdAt': '2026-04-20T15:27:27Z', 'includesCreatedEdit': True, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [], 'url': 'https://github.com/GLips/Figma-Context-MCP/issues/358#issuecomment-4282128612', 'viewerDidAuthor': False}, {'id': 'IC_kwDON4uODc7_XZuQ', 'author': {'login': 'GLips'}, 'authorAssociation': 'OWNER', 'body': "Very odd. I'm about to push an update that might fix the issue, but I'm unsure about the root cause still. If it isn't fixed in `v0.11.0` at the very least I hope we'll get better error messaging. Let me know once you have the latest version if the issue is resolved.", 'createdAt': '2026-04-20T21:12:56Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [], 'url': 'https://github.com/GLips/Figma-Context-MCP/issues/358#issuecomment-4284324752', 'viewerDidAuthor': False}, {'id': 'IC_kwDON4uODc7_m5h0', 'author': {'login': 'asifdotdev'}, 'authorAssociation': 'NONE', 'body': "## Update: Root Cause Found & Resolved\n\nAfter debugging this, the issue turned out to be a duplicate MCP server configuration, not a bug in Framelink itself. Here's the full breakdown:\n\n---\n\n### What happened\n\nI had the Framelink MCP server configured in two places:\n\n1. `~/.claude.json` (global user config) — using `${FIGMA_API_KEY}` env var  \n   - I added this manually because in some directories the MCP server wasn’t being configured automatically by default  \n2. `~/.claude/settings.json` (project settings) — with a hardcoded key  \n\nThis duplicate configuration caused a conflict where the MCP server wasn't receiving the correct API token during tool calls, resulting in **403 Invalid token** from the Figma API.\n\n---\n\n### Why it was confusing\n\n- The MCP server connected successfully and listed tools correctly — the Figma API key isn't used during the MCP handshake, only during actual tool calls.  \n- I verified the API key was valid by testing directly with `curl` against the Figma API — it returned `200` and full file data with the same key.  \n- So the key was valid, the MCP was connected, but every tool call still failed with `403`.  \n\n---\n\n### How I fixed it\n\n1. Removed the duplicate MCP server config from `~/.claude/settings.json`, keeping only the one in `~/.claude.json`  \n2. Restarted Claude Code — Framelink worked immediately after  \n---\n\nThanks @GLips for the quick response and the v0.11.0 update!\n\nThe updated errors definitively helped me in Claude Code to fix all of this", 'createdAt': '2026-04-21T12:07:39Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [], 'url': 'https://github.com/GLips/Figma-Context-MCP/issues/358#issuecomment-4288387188', 'viewerDidAuthor': False}, {'id': 'IC_kwDON4uODc8AAAABAYbxUg', 'author': {'login': 'GLips'}, 'authorAssociation': 'OWNER', 'body': '> The updated errors definitively helped me in Claude Code to fix all of this\n\nAwesome! Glad to hear the updated error messages were helpful. An ongoing process to make those more actionable. Appreciate the bug report.', 'createdAt': '2026-04-25T21:23:02Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [{'content': 'THUMBS_UP', 'users': {'totalCount': 1}}], 'url': 'https://github.com/GLips/Figma-Context-MCP/issues/358#issuecomment-4320588114', 'viewerDidAuthor': False}] labels=bug）

### Pull Requests 抽样
- PR #386 [OPEN] feat(strokes): include strokeAlign in simplified stroke output
- PR #384 [OPEN] feat: support request bearer oauth tokens over HTTP
- PR #381 [MERGED] fix(layout): include positions for children of SECTION nodes
- PR #380 [MERGED] fix: stop collapsing auto-layout frames to a single IMAGE-SVG
- PR #379 [MERGED] fix(layout): respect parent axis for dimensions

### Releases 抽样
- v0.12.0（published=2026-05-27T21:32:06Z latest=True）
- v0.11.0（published=2026-04-20T21:12:06Z latest=False）
- v0.10.1（published=2026-04-10T22:25:38Z latest=False）
- v0.10.0（published=2026-04-10T18:15:47Z latest=False）
- v0.9.0（published=2026-04-09T04:12:38Z latest=False）

### 真实反馈与维护信号研判
- 抽样 issue 中 open/closed 约为 2/6，可作为维护响应速度的弱信号。
- 近期 PR 抽样里可见已合并项 3 个，说明项目并非完全冻结。
- 存在 release 记录，说明作者具备版本化交付意识。
- 高频问题通常比 README 更能暴露真实落地难点：安装、兼容性、性能边界、文档歧义、平台限制。
- 若外部搜索数据不可用，本报告明确以 GitHub issue/PR/release 作为一手社区信号，不伪造站外口碑。

## 竞品对比
| 维度 | Figma-Context-MCP | 竞品/替代 |
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
- `tsconfig.json`
- `README.md`
- `CLAUDE.md`
- `CONTRIBUTING.md`
- `src/bin.ts`
- `src/commands/fetch.ts`
- `src/config.ts`
- `src/extractors/built-in.ts`
- `src/extractors/design-extractor.ts`
- `src/extractors/index.ts`
- `src/extractors/node-walker.ts`

## 3 条关键发现
- 代码入口/骨架集中在：package.json, tsconfig.json, README.md, CLAUDE.md, CONTRIBUTING.md
- Issue 抽样显示近期关注点包括：No mcp tools to make designs?；Feature request: expose image download/export support in the CLI
- 版本交付可从最新 release 观察：v0.12.0

## 研究方法与数据来源
- GitHub Repo API / README / 默认分支递归文件树
- 关键源码文件抽样精读
- Issues / PRs / Releases 社区活动抽样
- 说明：若外部搜索数据不可用，则明确标注并不伪造口碑结论
