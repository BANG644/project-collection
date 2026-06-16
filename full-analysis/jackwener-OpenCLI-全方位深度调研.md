# 🔬 jackwener/OpenCLI - 全方位深度调研

## 项目全景
- **仓库**：`jackwener/OpenCLI`
- **一句话定位**：Make Any Website into CLI & Use your logged-in browser by AI agent. 
- **基础指标**：Stars=23930 / Forks=2392 / 默认分支=`main`
- **Topics**：ai-agent, ai-agents, ai-tools, cli, browser-automation, browser-use, playwright
- **Homepage**：https://opencli.info/

## 核心架构
### 目录结构判断
- 顶层目录分布（递归树抽样汇总）：clis(1575), docs(210), src(186), autoresearch(37), sitemaps(33), skills(32), extension(23), tests(15), .github(13), scripts(10)
- 关键文件候选：package.json, tsconfig.json, README.md, CONTRIBUTING.md, src/adapter-shadow.test.ts, src/adapter-shadow.ts, src/adapter-source.test.ts, src/adapter-source.ts, src/browser.test.ts, src/browser/analyze.test.ts, src/browser/analyze.ts, src/browser/article-extract.e2e.test.ts

### 设计亮点研判
- 存在 Node/前端工具链入口，说明项目的运行、构建或 CLI 能力围绕 package.json 脚本组织。
- 仓库包含 .github 目录，通常意味着 CI、issue 模板或自动发布流程已被工程化。

## 源码深度解读
### README / 说明文档要点
# OpenCLI

> **Convert any website into a CLI & run Browser Use on your logged-in Chrome.**
> Turn websites, browser sessions, Electron apps, and local tools into deterministic interfaces for humans and AI agents.
> Or run Browser Use against any page — navigate, fill forms, click, extract, automate.

[![中文文档](https://img.shields.io/badge/docs-%E4%B8%AD%E6%96%87-0F766E?style=flat-square)](./README.zh-CN.md)
[![npm](https://img.shields.io/npm/v/@jackwener/opencli?style=flat-square)](https://www.npmjs.com/package/@jackwener/opencli)
[![Node.js Version](https://img.shields.io/node/v/@jackwener/opencli?style=flat-square)](https://nodejs.org)
[![License](https://img.shields.io/npm/l/@jackwener/opencli?style=flat-square)](./LICENSE)

OpenCLI gives you one surface for three different kinds of automation:

- **Use built-in adapters** for sites like Bilibili, Zhihu, Xiaohongshu, Reddit, HackerNews, Twitter/X, and [many more](#built-in-commands).
- **Let AI Agents operate any website** — install the `opencli-browser` skill in your AI agent (Claude Code, Cursor, etc.), and it can navigate, click, type/fill, extract, and inspect any page through your logged-in browser via `opencli browser` primitives.
- **Write new adapters** end-to-end with `opencli browser` + the `opencli-adapter-author` skill, which guides from first recon through field decoding, code, and `opencli browser verify`.

It also works as a **CLI hub** for local tools such as `gh`, `docker`, `longbridge`, `tg`, `discord`, `wx`, `ntn` (Notion), and other binaries you register yourself, plus **desktop app adapters** for Electron apps like Cursor, Trae CN, Codex, Antigravity, ChatGPT, and Trae SOLO.

## Quick Start

### 1. Install OpenCLI

OpenCLI requires **Node.js >= 20**.

```bash
node --version
npm install -g @jackwener/opencli
```

### 2. Install the Browser Bridge Extension

OpenCLI connects to Chrome/Chromium through a lightweight Browser Bridge extension plus a small local daemon. The daemon auto-starts when needed.

**Option A — Chrome Web Store (recommended):**
Install **OpenCLI** from the [Chrome Web Store](https://chromewebstore.google.com/detail/opencli/ildkmabpimmkaediidaifkhjpohdnifk).

**Option B — Manual install:**
1. Download the latest `opencli-extension-v{version}.zip` from the GitHub [Releases page](https://github.com/jackwener/opencli/releases).
2. Unzip it, open `chrome://extensions`, and enable **Developer mode**.
3. Click **Load unpacked** and select the unzipped folder.

### 3. Ver
...[truncated]

### 关键文件精读
### `package.json`
```
{
  "name": "@jackwener/opencli",
  "version": "1.8.3",
  "publishConfig": {
    "access": "public"
  },
  "description": "Make any website or Electron App your CLI. AI-powered.",
  "engines": {
    "node": ">=20.0.0"
  },
  "type": "module",
  "main": "dist/src/main.js",
  "bin": {
    "opencli": "dist/src/main.js"
  },
  "exports": {
    ".": "./dist/src/main.js",
    "./registry": "./dist/src/registry-api.js",
    "./errors": "./dist/src/errors.js",
    "./types": "./dist/src/types.js",
    "./utils": "./dist/src/utils.js",
    "./logger": "./dist/src/logger.js",
    "./launcher": "./dist/src/launcher.js",
    "./browser/cdp": "./dist/src/browser/cdp.js",
    "./browser/page": "./dist/src/browser/page.js",
    "./browser/utils": "./dist/src/browser/utils.js",
    "./download": "./dist/src/download/index.js",
    "./download/article-download": "./dist/src/download/article-download.js",
    "./download/media-download": "./dist/src/download/media-download.js",
    "./download/progress"
...[truncated]
```

### `tsconfig.json`
```
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "Node16",
    "moduleResolution": "Node16",
    "outDir": "dist",
    "rootDir": ".",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "declaration": true,
    "incremental": true
  },
  "include": [
    "src/**/*.ts"
  ],
  "exclude": ["node_modules", "dist", "extension"]
}
```

### `README.md`
```
# OpenCLI

> **Convert any website into a CLI & run Browser Use on your logged-in Chrome.**
> Turn websites, browser sessions, Electron apps, and local tools into deterministic interfaces for humans and AI agents.
> Or run Browser Use against any page — navigate, fill forms, click, extract, automate.

[![中文文档](https://img.shields.io/badge/docs-%E4%B8%AD%E6%96%87-0F766E?style=flat-square)](./README.zh-CN.md)
[![npm](https://img.shields.io/npm/v/@jackwener/opencli?style=flat-square)](https://www.npmjs.com/package/@jackwener/opencli)
[![Node.js Version](https://img.shields.io/node/v/@jackwener/opencli?style=flat-square)](https://nodejs.org)
[![License](https://img.shields.io/npm/l/@jackwener/opencli?style=flat-square)](./LICENSE)

OpenCLI gives you one surface for three different kinds of automation:

- **Use built-in adapters** for sites like Bilibili, Zhihu, Xiaohongshu, Reddit, HackerNews, Twitter/X, and [many more](#built-in-commands).
- **Let AI Agents operate any website** — install
...[truncated]
```

### `CONTRIBUTING.md`
```
# Contributing to OpenCLI

Thanks for your interest in contributing to OpenCLI.

## Quick Start

```bash
# 1. Fork & clone
git clone git@github.com:<your-username>/opencli.git
cd opencli

# 2. Install dependencies
npm install

# 3. Build
npm run build

# 4. Run a few checks
npx tsc --noEmit
npm test

# 5. Link globally (optional, for testing `opencli` command)
npm link
```

## Adding a New Site Adapter

All adapters use TypeScript. Use the pipeline API for data-fetching commands, and `func()` for complex browser interactions.

### Pipeline Adapter (Recommended for data-fetching commands)

Create a file like `clis/<site>/<command>.js`:

```typescript
import { cli, Strategy } from '@jackwener/opencli/registry';

cli({
  site: 'mysite',
  name: 'trending',
  description: 'Trending posts on MySite',
  domain: 'www.mysite.com',
  strategy: Strategy.PUBLIC,
  browser: false,
  args: [
    { name: 'query', positional: true, required: true, help: 'Search keyword' },
    { name: 'limit', type: 
...[truncated]
```

### `src/adapter-shadow.test.ts`
```
import { describe, expect, it } from 'vitest';
import * as fs from 'node:fs';
import * as os from 'node:os';
import * as path from 'node:path';
import { findShadowedUserAdapters, formatAdapterShadowIssue } from './adapter-shadow.js';

describe('adapter shadow detection', () => {
  it('reports user adapters that shadow packaged manifest commands', () => {
    const root = fs.mkdtempSync(path.join(os.tmpdir(), 'opencli-adapter-shadow-'));
    try {
      const userClisDir = path.join(root, 'user-clis');
      const builtinRoot = path.join(root, 'pkg');
      const builtinClisDir = path.join(builtinRoot, 'clis');
      fs.mkdirSync(path.join(userClisDir, 'instagram'), { recursive: true });
      fs.mkdirSync(path.join(userClisDir, 'twitter'), { recursive: true });
      fs.mkdirSync(path.join(builtinClisDir, 'instagram'), { recursive: true });
      fs.mkdirSync(path.join(builtinClisDir, 'twitter'), { recursive: true });

      fs.writeFileSync(path.join(userClisDir, 'instagram', 'saved.j
...[truncated]
```

### `src/adapter-shadow.ts`
```
import * as fs from 'node:fs';
import * as os from 'node:os';
import * as path from 'node:path';
import { fileURLToPath } from 'node:url';
import type { ManifestEntry } from './manifest-types.js';
import { findPackageRoot, getCliManifestPath } from './package-paths.js';

export type AdapterShadow = {
  name: string;
  userPath: string;
  builtinPath: string;
};

export type AdapterShadowOptions = {
  userClisDir?: string;
  builtinClisDir?: string;
};

function defaultBuiltinClisDir(): string {
  return path.join(findPackageRoot(fileURLToPath(import.meta.url)), 'clis');
}

function safeReaddir(dir: string): fs.Dirent[] {
  try {
    return fs.readdirSync(dir, { withFileTypes: true });
  } catch {
    return [];
  }
}

function loadBuiltinCommandFiles(builtinClisDir: string): Set<string> {
  try {
    const raw = fs.readFileSync(getCliManifestPath(builtinClisDir), 'utf-8');
    const entries = JSON.parse(raw) as ManifestEntry[];
    const files = new Set<string>();
    for (const entry 
...[truncated]
```

### 关键逻辑总结
- 从关键文件组合看，项目更像围绕单一目标组织的任务流水线/工具链，而不是超重平台。
- 入口文件决定外部交互界面（CLI / API / UI），配置文件决定运行时依赖，测试文件暴露作者真正关心的行为边界。
- 如果用户只读 README，通常只能知道“能做什么”；而从目录与入口文件能看出“怎么做、扩展点在哪、维护成本高不高”。

## 社区口碑
### GitHub Issues 抽样
- #1898 [OPEN] [Bug]: Upon executing the opencli chatgpt image command, it reports a successful execution while failing to produce an image.（comments=[] labels=bug）
- #1897 [OPEN] Question about featuring OpenCLI in an Agent Hub（comments=[] labels=无）
- #1896 [OPEN] [Feature]: archive.org How could such an important website not be included in this tool?（comments=[] labels=enhancement）
- #1894 [OPEN] [Bug]: Doubao blocked the request with a verification challenge（comments=[] labels=bug）
- #1893 [OPEN] [Bug]: README profile browser example is missing required session argument（comments=[{'id': 'IC_kwDORnOeDM8AAAABFOuJSg', 'author': {'login': 'MicroGery'}, 'authorAssociation': 'NONE', 'body': '## Related PR\n\nAddressed by #1872.', 'createdAt': '2026-06-08T06:17:26Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [], 'url': 'https://github.com/jackwener/OpenCLI/issues/1893#issuecomment-4645947722', 'viewerDidAuthor': False}] labels=bug）
- #1886 [OPEN] bug(deepseek): expert mode incompatible with --search true (UI lacks search button)（comments=[{'id': 'IC_kwDORnOeDM8AAAABFKnfSw', 'author': {'login': 'Benjamin-eecs'}, 'authorAssociation': 'CONTRIBUTOR', 'body': 'Fixed in #1887.\n', 'createdAt': '2026-06-07T06:22:32Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [{'content': 'THUMBS_UP', 'users': {'totalCount': 1}}], 'url': 'https://github.com/jackwener/OpenCLI/issues/1886#issuecomment-4641644363', 'viewerDidAuthor': False}] labels=无）

### Pull Requests 抽样
- PR #1906 [CLOSED] fix(plugin): reject unsafe plugin names on install to prevent path traversal
- PR #1905 [OPEN] fix(output): escape pipes and newlines in markdown table cells
- PR #1904 [OPEN] fix(external): set non-zero exit code when an external CLI is killed by a signal
- PR #1903 [CLOSED] fix(discovery): recognize shared make*Command factory adapters at runtime
- PR #1902 [OPEN] fix(pipeline/fetch): detect item binding via template regex, not substring

### Releases 抽样
- v1.8.3（published=2026-06-05T16:47:19Z latest=True）
- v1.8.2（published=2026-06-02T17:32:05Z latest=False）
- v1.8.1（published=2026-05-30T20:42:43Z latest=False）
- v1.8.0（published=2026-05-19T19:33:03Z latest=False）
- v1.7.22（published=2026-05-15T09:31:31Z latest=False）

### 真实反馈与维护信号研判
- 抽样 issue 中 open/closed 约为 8/0，可作为维护响应速度的弱信号。
- 近期 PR 抽样里可见已合并项 0 个，说明项目并非完全冻结。
- 存在 release 记录，说明作者具备版本化交付意识。
- 高频问题通常比 README 更能暴露真实落地难点：安装、兼容性、性能边界、文档歧义、平台限制。
- 若外部搜索数据不可用，本报告明确以 GitHub issue/PR/release 作为一手社区信号，不伪造站外口碑。

## 竞品对比
| 维度 | OpenCLI | 竞品/替代 |
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
- `CONTRIBUTING.md`
- `src/adapter-shadow.test.ts`
- `src/adapter-shadow.ts`
- `src/adapter-source.test.ts`
- `src/adapter-source.ts`
- `src/browser.test.ts`
- `src/browser/analyze.test.ts`
- `src/browser/analyze.ts`
- `src/browser/article-extract.e2e.test.ts`

## 3 条关键发现
- 代码入口/骨架集中在：package.json, tsconfig.json, README.md, CONTRIBUTING.md, src/adapter-shadow.test.ts
- Issue 抽样显示近期关注点包括：[Bug]: Upon executing the opencli chatgpt image command, it reports a successful execution while failing to produce an image.；Question about featuring OpenCLI in an Agent Hub
- 版本交付可从最新 release 观察：v1.8.3

## 研究方法与数据来源
- GitHub Repo API / README / 默认分支递归文件树
- 关键源码文件抽样精读
- Issues / PRs / Releases 社区活动抽样
- 说明：若外部搜索数据不可用，则明确标注并不伪造口碑结论
