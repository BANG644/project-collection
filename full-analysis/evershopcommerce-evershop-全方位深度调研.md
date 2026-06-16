# 🔬 evershopcommerce/evershop - 全方位深度调研

## 项目全景
- **仓库**：`evershopcommerce/evershop`
- **一句话定位**：🛍️ Typescript E-commerce Platform
- **基础指标**：Stars=10123 / Forks=2340 / 默认分支=`dev`
- **Topics**：ecommerce, ecommerce-framework, ecommerce-platform, react, typescript
- **Homepage**：https://evershop.io/

## 核心架构
### 目录结构判断
- 顶层目录分布（递归树抽样汇总）：packages(1780), translations(84), .github(17), seed(17), .gitignore(1), .husky(1), .prettierignore(1), .prettierrc(1), CODE_OF_CONDUCT.md(1), CONTRIBUTING.md(1)
- 关键文件候选：package.json, tsconfig.json, README.md, CONTRIBUTING.md, packages/create-evershop-app/createEverShopApp.js, packages/create-evershop-app/index.js, packages/create-evershop-app/sample/extensions/sample/dist/api/createFoo/[bodyParser]createFoo.d.ts, packages/create-evershop-app/sample/extensions/sample/dist/api/createFoo/[bodyParser]createFoo.js, packages/create-evershop-app/sample/extensions/sample/dist/api/createFoo/bodyParser.d.ts, packages/create-evershop-app/sample/extensions/sample/dist/api/createFoo/bodyParser.js, packages/create-evershop-app/sample/extensions/sample/dist/bootstrap.d.ts, packages/create-evershop-app/sample/extensions/sample/dist/bootstrap.js

### 设计亮点研判
- 存在 Node/前端工具链入口，说明项目的运行、构建或 CLI 能力围绕 package.json 脚本组织。
- 仓库包含 .github 目录，通常意味着 CI、issue 模板或自动发布流程已被工程化。

## 源码深度解读
### README / 说明文档要点
<p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</p>
<p align="center">
<img width="60" height="68" alt="EverShop Logo" src="https://raw.githubusercontent.com/evershopcommerce/evershop/dev/.github/images/logo-green.png"/>
</p>
<p align="center">
  <h1 align="center">EverShop</h1>
</p>
<p align="center">
  <a href="https://trendshift.io/repositories/212" target="_blank"><img src="https://trendshift.io/api/badge/repositories/212" alt="evershopcommerce%2Fevershop | Trendshift" style="width: 250px; height: 55px;" width="250" height="55"/></a>
</p>
<h4 align="center">
    <a href="https://evershop.io/docs/development/getting-started/introduction">Documentation</a> |
    <a href="https://demo.evershop.io/">Demo</a>
</h4>

<p align="center">
  <img src="https://github.com/evershopcommerce/evershop/actions/workflows/build_test.yml/badge.svg" alt="Github Action"> <a href="https://twitter.com/evershopjs"><img alt="Twitter Follow" src="https://img.shields.io/twitter/follow/evershopjs?style=social"></a> <a href="https://discord.gg/GSzt7dt7RM"><img src="https://img.shields.io/discord/757179260417867879?label=discord" alt="Discord"></a> <a href="https://opensource.org/licenses/GPL-3.0"><img src="https://img.shields.io/badge/License-GPLv3-blue.svg" alt="License"></a>
</p>

<p align="center">
<img alt="EverShop" width="950" src="https://raw.githubusercontent.com/evershopcommerce/evershop/dev/.github/images/banner.png"/>
</p>

## Introduction

EverShop is a modern, TypeScript-first eCommerce platform built with GraphQL and React. Designed for developers, it offers essential commerce features in a modular, fully customizable architecture—perfect for building tailored shopping experiences with confidence and speed.

## Installation Using Docker


You can get started with EverShop in minutes by using the Docker image. The Docker image is a great way to get started with EverShop without having to worry about installing dependencies or configuring your environment.

```bash
curl -sSL https://raw.githubusercontent.com/evershopcommerce/evershop/main/docker-compose.yml > docker-compose.yml
docker compose up -d
```

For the full installation guide, please refer to our [Installation guide](https://evershop.io/docs/development/getting-started/installation-guide).

## Documentation

- [Installation guide](https://evershop.io/docs/development/getting-started/installation-guide).

- [Extension development](https://evershop.io/docs/development/module/create-your-first-extension).

- [Theme develo
...[truncated]

### 关键文件精读
### `package.json`
```
{
  "name": "evershop",
  "version": "2.1.0",
  "type": "module",
  "description": "A shopping cart platform with Express, React and Postgres",
  "workspaces": [
    "packages/*",
    "extensions/*"
  ],
  "scripts": {
    "dev": "node ./packages/evershop/dist/bin/dev/index.js",
    "start": "node ./packages/evershop/dist/bin/start/index.js",
    "build": "node ./packages/evershop/dist/bin/build/index.js",
    "build-fast": "evershop build -- --skip-minify",
    "setup": "evershop install",
    "theme:active": "evershop theme:active",
    "theme:twizz": "evershop theme:twizz",
    "theme:create": "evershop theme:create",
    "compile": "rimraf ./packages/evershop/dist && cd ./packages/evershop && swc ./src/ -d dist/ --config-file .swcrc --copy-files --strip-leading-paths",
    "compile:db": "rimraf ./packages/postgres-query-builder/dist && cd ./packages/postgres-query-builder && swc ./src/ -d dist/ --config-file .swcrc --copy-files --strip-leading-paths",
    "compile:tsc": "rimraf ./p
...[truncated]
```

### `tsconfig.json`
```
{
  "compilerOptions": {
    "module": "NodeNext",
    "target": "ES2018",
    "lib": ["dom", "dom.iterable", "esnext"],
    "esModuleInterop": true,
    "forceConsistentCasingInFileNames": true,
    "skipLibCheck": true,
    "declaration": true,
    "declarationDir": "./dist/types",
    "sourceMap": true,
    "allowJs": true,
    "checkJs": false,
    "jsx": "preserve",
    "outDir": "./dist",
    "resolveJsonModule": true,
    "allowSyntheticDefaultImports": true,
    "allowArbitraryExtensions": true,
    "baseUrl": ".",
    "paths": {
      "@components/*": ["packages/evershop/src/components/*"],
      "@evershop/postgres-query-builder": ["packages/postgres-query-builder/src/index.ts"],
      "@evershop/postgres-query-builder/*": ["packages/postgres-query-builder/src/*"]
    }
  },
}
```

### `README.md`
```
<p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</p>
<p align="center">
<img width="60" height="68" alt="EverShop Logo" src="https://raw.githubusercontent.com/evershopcommerce/evershop/dev/.github/images/logo-green.png"/>
</p>
<p align="center">
  <h1 align="center">EverShop</h1>
</p>
<p align="center">
  <a href="https://trendshift.io/repositories/212" target="_blank"><img src="https://trendshift.io/api/badge/repositories/212" alt="evershopcommerce%2Fevershop | Trendshift" style="width: 250px; height: 55px;" width="250" height="55"/></a>
</p>
<h4 align="center">
    <a href="https://evershop.io/docs/development/getting-started/introduction">Documentation</a> |
    <a href="https://demo.evershop.io/">Demo</a>
</h4>

<p align="center">
  <img src="https://github.com/evershopcommerce/evershop/actions/workflows/build_test.yml/badge.svg" alt="Github Action"> <a href="https://twitter.com/evershopjs"><img alt="Twitter Follow" src="https://img.shields.io/twitter/follow/evershopjs?style=social"></a> <a
...[truncated]
```

### `CONTRIBUTING.md`
```
# Contributing to EverShop

We love your input! We want to make contributing to this project as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features

---

- Read about our [Code Of Conduct](https://github.com/evershopcommerce/evershop/blob/main/CODE_OF_CONDUCT.md).

## Developing

To develop locally:

1. [Fork](https://help.github.com/articles/fork-a-repo/) this repository to your
   own GitHub account and then
   [clone](https://help.github.com/articles/cloning-a-repository/) it to your local device.

   ```sh
   git clone https://github.com/evershopcommerce/evershop.git
   ```

2. Create a new branch:
   ```
   git checkout -b MY_BRANCH_NAME
   ```
3. Install the dependencies with:
   ```
   npm install
   ```
4. Create a Postgres database:
   ```
   // EverShop use Postgres for database storage
   ```
5. Run installation command to create a database schema:
   ```
   npm run setup
  
...[truncated]
```

### `packages/create-evershop-app/createEverShopApp.js`
```
const https = require('https');
const chalk = require('chalk');
const commander = require('commander');
const dns = require('dns');
const { execSync } = require('child_process');
const fs = require('fs-extra');
const os = require('os');
const path = require('path');
const semver = require('semver');
const spawn = require('cross-spawn');
const url = require('url');
const validateProjectName = require('validate-npm-package-name');
const { mkdir } = require('fs/promises');
const packageJson = require('./package.json');

function isUsingYarn() {
  return (process.env.npm_config_user_agent || '').indexOf('yarn') === 0;
}

let projectName;

function init() {
  const program = new commander.Command(packageJson.name)
    .version(packageJson.version)
    .arguments('[project-directory]')
    .usage(`${chalk.green('<project-directory>')} [options]`)
    .action((name) => {
      projectName = name;
    })
    .option('--verbose', 'Print additional logs')
    .option('--info', 'Print environment
...[truncated]
```

### `packages/create-evershop-app/index.js`
```
#!/usr/bin/env node

const currentNodeVersion = process.versions.node;
const semver = currentNodeVersion.split('.');
const major = semver[0];

if (major < 14) {
  console.error(
    `You are running Node ${currentNodeVersion}.\n` +
      `Create React App requires Node 14 or higher. \n` +
      `Please update your version of Node.`
  );
  process.exit(1);
}

const { init } = require('./createEverShopApp');

init();
```

### 关键逻辑总结
- 从关键文件组合看，项目更像围绕单一目标组织的任务流水线/工具链，而不是超重平台。
- 入口文件决定外部交互界面（CLI / API / UI），配置文件决定运行时依赖，测试文件暴露作者真正关心的行为边界。
- 如果用户只读 README，通常只能知道“能做什么”；而从目录与入口文件能看出“怎么做、扩展点在哪、维护成本高不高”。

## 社区口碑
### GitHub Issues 抽样
- #944 [OPEN] [FEATURE REQUEST] Replace Discord Text Link with Discord Icon in Footer（comments=[{'id': 'IC_kwDOFb887M8AAAABE4d4Sw', 'author': {'login': 'ankiit-io'}, 'authorAssociation': 'NONE', 'body': "I'd like to work on this enhancement if it's accepted. Could this issue be assigned to me?", 'createdAt': '2026-06-04T13:31:50Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [], 'url': 'https://github.com/evershopcommerce/evershop/issues/944#issuecomment-4622612555', 'viewerDidAuthor': False}, {'id': 'IC_kwDOFb887M8AAAABE4_p6A', 'author': {'login': 'ankiit-io'}, 'authorAssociation': 'NONE', 'body': "While investigating the implementation, I found that the footer configuration appears to be located in the `evershopcommerce/docs` repository rather than the main `evershop` repository. If this feature is considered valuable, I'd be happy to open the corresponding issue and submit a PR in the docs repository instead.\n", 'createdAt': '2026-06-04T14:37:25Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [], 'url': 'https://github.com/evershopcommerce/evershop/issues/944#issuecomment-4623165928', 'viewerDidAuthor': False}] labels=无）
- #937 [OPEN] npm Audit（comments=[] labels=无）
- #935 [OPEN] [BUG] HEAD method not working（comments=[] labels=无）
- #934 [OPEN] Billing country missing or restricted for virtual products（comments=[] labels=无）
- #933 [OPEN] [BUG] SETUP: docker install is broken（comments=[{'id': 'IC_kwDOFb887M7_6AHB', 'author': {'login': 'EstevenJaviier'}, 'authorAssociation': 'NONE', 'body': 'you can use 2.1.1 version', 'createdAt': '2026-04-22T03:54:58Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [{'content': 'THUMBS_UP', 'users': {'totalCount': 1}}], 'url': 'https://github.com/evershopcommerce/evershop/issues/933#issuecomment-4293394881', 'viewerDidAuthor': False}, {'id': 'IC_kwDOFb887M8AAAABAEivzw', 'author': {'login': 'cyberrapr'}, 'authorAssociation': 'NONE', 'body': '> you can use 2.1.1 version\n\nthx will try', 'createdAt': '2026-04-22T20:27:31Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [], 'url': 'https://github.com/evershopcommerce/evershop/issues/933#issuecomment-4299730895', 'viewerDidAuthor': False}, {'id': 'IC_kwDOFb887M8AAAABAnX4-w', 'author': {'login': 'xavierhalison'}, 'authorAssociation': 'NONE', 'body': '> thx will try\n\n@cyberrapr did you find a fix for this? \n\n', 'createdAt': '2026-04-28T14:34:29Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [], 'url': 'https://github.com/evershopcommerce/evershop/issues/933#issuecomment-4336253179', 'viewerDidAuthor': False}, {'id': 'IC_kwDOFb887M8AAAABBjI7_g', 'author': {'login': 'thokich'}, 'authorAssociation': 'NONE', 'body': "I have the same error in docker image: evershop/evershop:2.1.2\n\nStarup Home Page Error:\nENOENT: no such file or directory, open '/app/.evershop/build/frontStore/login/client/index.json'\n\nWhen I run in the sh Container\n/app # npm run build\n\n> evershop@2.1.2 build\n> evershop build\n\n❌ error: \nUnhandled Rejection: ValidationError: Invalid options object. Progress Plugin has been initialized using an options object that does not match the API schema.\n - options should be one of these:\n   object { activeModules?, dependencies?, dependenciesCount?, entries?, handler?, modules?, modulesCount?, percentBy?, profile? } | function\n   Details:\n    * options has an unknown property 'name'. These properties are valid:\n      object { activeModules?, dependencies?, dependenciesCount?, entries?, handler?, modules?, modulesCount?, percentBy?, profile? }\n      -> Options object for the ProgressPlugin.\n    * options has an unknown property 'color'. These properties are valid:\n      object { activeModules?, dependencies?, dependenciesCount?, entries?, handler?, modules?, modulesCount?, percentBy?, profile? }\n      -> Options object for the ProgressPlugin.\n    * options has an unknown property 'reporters'. These properties are valid:\n      object { activeModules?, dependencies?, dependenciesCount?, entries?, handler?, modules?, modulesCount?, percentBy?, profile? }\n      -> Options object for the ProgressPlugin.\n    * options has an unknown property 'reporter'. These properties are valid:\n      object { activeModules?, dependencies?, dependenciesCount?, entries?, handler?, modules?, modulesCount?, percentBy?, profile? }\n      -> Options object for the ProgressPlugin. at: [object Promise]\n❌ error: \nUnhandled Rejection: ValidationError: Invalid options object. Progress Plugin has been initialized using an options object that does not match the API schema.\n - options should be one of these:\n   object { activeModules?, dependencies?, dependenciesCount?, entries?, handler?, modules?, modulesCount?, percentBy?, profile? } | function\n   Details:\n    * options has an unknown property 'name'. These properties are valid:\n      object { activeModules?, dependencies?, dependenciesCount?, entries?, handler?, modules?, modulesCount?, percentBy?, profile? }\n      -> Options object for the ProgressPlugin.\n    * options has an unknown property 'color'. These properties are valid:\n      object { activeModules?, dependencies?, dependenciesCount?, entries?, handler?, modules?, modulesCount?, percentBy?, profile? }\n      -> Options object for the ProgressPlugin.\n    * options has an unknown property 'reporters'. These properties are valid:\n      object { activeModules?, dependencies?, dependenciesCount?, entries?, handler?, modules?, modulesCount?, percentBy?, profile? }\n      -> Options object for the ProgressPlugin.\n    * options has an unknown property 'reporter'. These properties are valid:\n      object { activeModules?, dependencies?, dependenciesCount?, entries?, handler?, modules?, modulesCount?, percentBy?, profile? }\n      -> Options object for the ProgressPlugin. at: [object Promise]\n\nIn docker image: evershop/evershop:2.1.1 it works.", 'createdAt': '2026-05-07T16:19:08Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [], 'url': 'https://github.com/evershopcommerce/evershop/issues/933#issuecomment-4398922750', 'viewerDidAuthor': False}] labels=无）
- #932 [OPEN] [BUG] SETUP: "ValidationError: Invalid options object. Progress Plugin has been initialized..."（comments=[{'id': 'IC_kwDOFb887M8AAAABAIvsLw', 'author': {'login': 'FrontEndStudio'}, 'authorAssociation': 'NONE', 'body': 'Can verify that I have the same problem:\n\nnode --version v20.18.3 || v24.15.0\nnpm --version  11.12.1\nos: Ubuntu 22.04.5 LTS \npsql: (PostgreSQL) 14.22 (Ubuntu 14.22-0ubuntu0.22.04.1)\nevershop: 2.1.2\n', 'createdAt': '2026-04-23T11:53:45Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [{'content': 'THUMBS_UP', 'users': {'totalCount': 1}}], 'url': 'https://github.com/evershopcommerce/evershop/issues/932#issuecomment-4304137263', 'viewerDidAuthor': False}, {'id': 'IC_kwDOFb887M8AAAABDO-Ttg', 'author': {'login': 'CesarDavidAguirre'}, 'authorAssociation': 'NONE', 'body': 'hi, the error is in the package webpackbar. Try to add this in the package.json\n\n`\n"overrides": {\n    "webpackbar": "^7.0.0"\n  }\n`', 'createdAt': '2026-05-21T19:17:34Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [{'content': 'HEART', 'users': {'totalCount': 1}}], 'url': 'https://github.com/evershopcommerce/evershop/issues/932#issuecomment-4511994806', 'viewerDidAuthor': False}] labels=bug）

### Pull Requests 抽样
- PR #945 [CLOSED] Create file.txt
- PR #943 [OPEN] Spanish translations
- PR #942 [OPEN] Add translate to message for password reset error
- PR #939 [MERGED] feat: editor styling improvements
- PR #938 [MERGED] chore: bump version to 2.1.3 and update webpackbar to 7.0.0; change s…

### Releases 抽样
- v2.1.2（published=2026-04-03T08:54:47Z latest=True）
- v2.1.1（published=2026-02-25T04:53:21Z latest=False）
- v2.1.0（published=2025-11-12T03:30:52Z latest=False）
- v2.0.1（published=2025-07-11T06:36:15Z latest=False）
- v2.0.0（published=2025-07-04T11:13:38Z latest=False）

### 真实反馈与维护信号研判
- 抽样 issue 中 open/closed 约为 8/0，可作为维护响应速度的弱信号。
- 近期 PR 抽样里可见已合并项 2 个，说明项目并非完全冻结。
- 存在 release 记录，说明作者具备版本化交付意识。
- 高频问题通常比 README 更能暴露真实落地难点：安装、兼容性、性能边界、文档歧义、平台限制。
- 若外部搜索数据不可用，本报告明确以 GitHub issue/PR/release 作为一手社区信号，不伪造站外口碑。

## 竞品对比
| 维度 | evershop | 竞品/替代 |
|---|---|---|
| 定位 | 面向仓库作者设定的具体场景，通常更垂直 | Medusa / Saleor / Shopify Hydrogen 往往更通用或生态更大 |
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
- `packages/create-evershop-app/createEverShopApp.js`
- `packages/create-evershop-app/index.js`
- `packages/create-evershop-app/sample/extensions/sample/dist/api/createFoo/[bodyParser]createFoo.d.ts`
- `packages/create-evershop-app/sample/extensions/sample/dist/api/createFoo/[bodyParser]createFoo.js`
- `packages/create-evershop-app/sample/extensions/sample/dist/api/createFoo/bodyParser.d.ts`
- `packages/create-evershop-app/sample/extensions/sample/dist/api/createFoo/bodyParser.js`
- `packages/create-evershop-app/sample/extensions/sample/dist/bootstrap.d.ts`
- `packages/create-evershop-app/sample/extensions/sample/dist/bootstrap.js`

## 3 条关键发现
- 代码入口/骨架集中在：package.json, tsconfig.json, README.md, CONTRIBUTING.md, packages/create-evershop-app/createEverShopApp.js
- Issue 抽样显示近期关注点包括：[FEATURE REQUEST] Replace Discord Text Link with Discord Icon in Footer；npm Audit
- 版本交付可从最新 release 观察：v2.1.2

## 研究方法与数据来源
- GitHub Repo API / README / 默认分支递归文件树
- 关键源码文件抽样精读
- Issues / PRs / Releases 社区活动抽样
- 说明：若外部搜索数据不可用，则明确标注并不伪造口碑结论
