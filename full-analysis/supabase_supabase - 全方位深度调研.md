# 🔬 supabase/supabase - 全方位深度调研

## 📌 一句话定位

The Postgres development platform. Supabase gives you a dedicated Postgres database to build your web, mobile, and AI applications.

## 🏗️ 项目全景

仓库：supabase/supabase
- **解决的问题**：该项目试图把 README 中描述的能力产品化/脚本化，降低特定任务的搭建或执行门槛。
- **基础指标**：Stars=103924 / Forks=12690 / 默认分支=master
- **Topics**：firebase, supabase, realtime, postgrest, postgres, postgresql, websockets, deno, embeddings, vectors, alternative, auth, database, example, nextjs, oauth2, pgvector, postgis, ai
- **Homepage**：https://supabase.com

## 🧠 核心架构

目录结构判断
- **顶层目录分布（递归树抽样汇总）**：apps(12921), examples(1463), packages(883), blocks(117), e2e(74), .github(59), supabase(56), docker(55), i18n(50), .claude(25)
- **关键文件候选**：
- `package.json`, pnpm-workspace.yaml, tsconfig.json, 
- `README.md`, 
- `CONTRIBUTING.md`, packages/ai-commands/edge.ts, packages/ai-commands/index.ts, packages/ai-commands/src/docs.ts, packages/ai-commands/src/errors.ts, packages/ai-commands/src/sql/cron.ts, packages/ai-commands/src/sql/functions.test.ts, packages/ai-commands/src/sql/functions.ts设计亮点研判
- 存在 Node/前端或工具链入口，依赖与脚本编排主要由 
- `package.json` 驱动。
- 仓库包含 .github 自动化配置，通常代表 CI 或 issue 模板已被纳入工程流程。

## 🔍 源码深度解读

README / 说明文档要点<p align="center">
<img src="https://user-images.githubusercontent.com/8291514/213727234-cda046d6-28c6-491a-b284-b86c5cede25d.png#gh-light-mode-only" />
<img src="https://user-images.githubusercontent.com/8291514/213727225-56186826-bee8-43b5-9b15-86e839d89393.png#gh-dark-mode-only" />
</p>SupabaseSupabase is the Postgres development platform. We're building the features of Firebase using enterprise-grade open source tools.Hosted Postgres Database. DocsAuthentication and Authorization. DocsAuto-generated APIs.REST. DocsGraphQL. DocsRealtime subscriptions. DocsFunctions.Database Functions. DocsEdge Functions DocsFile Storage. DocsAI + Vector/Embeddings Toolkit. DocsDashboardWatch "releases" of this repo to get notified of major updates.<kbd><img src="https://raw.githubusercontent.com/supabase/supabase/d5f7f413ab356dc1a92075cb3cee4e40a957d5b1/web/static/watch-repo.gif" alt="Watch this repo"/></kbd>DocumentationFor full documentation, visit supabase.com/docsTo see how to Contribute, visit Getting StartedCommunity & SupportCommunity Forum. Best for: help with building, discussion about database best practices.GitHub Issues. Best for: bugs and errors you encounter using Supabase.Email Support. Best for: problems with your database or infrastructure.Discord. Best for...[truncated]

### 关键文件精读

package.json{  "name": "supabase",  "description": "The Postgres Development Platform.",  "version": "0.0.0",  "author": "Supabase, Inc.",  "license": "Apache-2.0",  "private": true,  "scripts": {    "preinstall": "npx only-allow pnpm",    "build": "turbo run build",    "build:studio": "turbo run build --filter=studio",    "build:studio:docker": "docker build . -f apps/studio/Dockerfile --target production -t supabase-studio:local --build-arg NEXT_PUBLIC_STUDIO_AUTH_MODE=supabase --no-cache",    "build:design-system": "turbo run build --filter=design-system",    "build:docs": "turbo run build --filter=docs",    "clean": "turbo run clean --parallel && rimraf -G node_modules/{*,.bin,.modules.yaml} .turbo/cache",    "dev": "turbo run dev --parallel",    "dev:studio": "turbo run dev --filter=studio --parallel",    "dev:studio-local": "pnpm setup:cli && NODE_ENV=test pnpm --prefix ./apps...[truncated]pnpm-workspace.yamlpackages:  - apps/*  - packages/*  - blocks/*  - e2e/*blockExoticSubdeps: truecatalog:  '@sentry/nextjs': ^10.26.0  '@supabase/auth-js': 2.108.0  '@supabase/postgrest-js': 2.108.0  '@supabase/realtime-js': 2.108.0  '@supabase/ssr': 0.10.2  '@supabase/supabase-js': 2.108.0  '@types/node': ^22.0.0  '@types/react': ^19.2.14  '@types/react-dom': ^19.2.3  '@vitejs/plugin-react': ^6.0.1  '@vitest/coverage-v8': ^4.1.4  '@vitest/ui': ^4.1.4  lodash: ^4.18.1  lodash-es: ^4.18.1  next: 16.2.6  next-themes: ^0.4.6  postcss: ^8.5.10  radix-ui: ^1.4.3  react: ^19.2.6  react-dom: ^19.2.6  recharts: ^2.15.4  tailwindcss: ^4.2.4  tsx: 4.20.3  typescript: ~6.0.0  valtio: ^1.12.0  vite: ^8.0.8  vite-tsconfig-paths: ^6.1.1  vitest: ^4.1.4  zod: 3.25.76ignoredBuiltDependencies:  - '@parcel/watcher'  - '@sentry/cli'  - contentlayer2  - core-js  - es5-ext  - esbuil...[truncated]tsconfig.json{  "compilerOptions": {    "jsx": "react",    "skipLibCheck": true  }}
- `README.md`<p align="center"><img src="https://user-images.githubusercontent.com/8291514/213727234-cda046d6-28c6-491a-b284-b86c5cede25d.png#gh-light-mode-only" /><img src="https://user-images.githubusercontent.com/8291514/213727225-56186826-bee8-43b5-9b15-86e839d89393.png#gh-dark-mode-only" /></p># Supabase[Supabase](https://supabase.com) is the Postgres development platform. We're building the features of Firebase using enterprise-grade open source tools.- [x] Hosted Postgres Database. [Docs](https://supabase.com/docs/guides/database)- [x] Authentication and Authorization. [Docs](https://supabase.com/docs/guides/auth)- [x] Auto-generated APIs.  - [x] REST. [Docs](https://supabase.com/docs/guides/api)  - [x] GraphQL. [Docs](https://supabase.com/docs/guides/graphql)  - [x] Realtime subscriptions. [Docs](https://supabase.com/docs/guides/realtime)- [x] Functions.  - [x] Database Functions....[truncated]
- `CONTRIBUTING.md`# 
- `CONTRIBUTING.md`Thank you for contributing to Supabase! We’re a big, exciting open source project and we’d love to have you contribute! Here’s some resources and guidance to help you get started:[1. Getting Started](#getting-started)[2. Issues](#issues)[3. Pull Requests](#pull-requests)## Getting StartedTo ensure a positive and inclusive environment, please read our [code of conduct](https://github.com/supabase/.github/blob/main/CODE_OF_CONDUCT.md) before contributing. For help setting up the code in this repo, please follow our [DEVELOPERS.md](https://github.com/supabase/supabase/blob/master/DEVELOPERS.md) file. For the [docs](https://supabase.com/docs) site, follow this [
- `CONTRIBUTING.md`](https://github.com/supabase/supabase/blob/master/apps/docs/
- `CONTRIBUTING.md`) guide.## IssuesIf you find a bug, please create an Issue and we’ll triage it.- Please search [existing Issue...[truncated]packages/ai-commands/edge.tsexport * from './src/errors'export * from './src/docs'export * from './src/sql/cron'

### 关键逻辑总结

从关键文件组合看，项目更像是围绕单一目标组织的任务流水线/工具链，而不是超重平台。
- 入口文件决定外部交互界面（CLI / API / UI），配置文件决定运行时依赖，测试文件则暴露作者真正关心的行为边界。
- 如果用户只读 README，通常只能知道“能做什么”；而从目录与入口文件能看出“怎么做、扩展点在哪、维护成本高不高”。

## 🌐 社区口碑

### GitHub Issues 抽样

#46744 [CLOSED] UI bug on table editor（comments=[{'id': 'IC_kwDODMpXOc8AAAABFScNBg', 'author': {'login': 'coderabbitai'}, 'authorAssociation': 'CONTRIBUTOR', 'body': '<!-- This is an auto-generated issue plan by CodeRabbit -->\n<details>\n<summary>🔗 Related PRs</summary>\n\nsupabase/supabase#45914 - Fix width of unified logs table to fit viewport, which fixes centering of load more button [merged]\n</details>\n\n---\n<details>\n<summary>📝 Issue Planner</summary>\n\n<sub>Check the box below or use the @coderabbitai plan command to generate an implementation plan and prompts that you can use with your favorite coding assistant.</sub>\n\n- [ ] <!-- {"checkboxId": "8d4f2b9c-3e1a-4f7c-a9b2-d5e8f1c4a7b9"} --> Create Plan\n</details>\n\n\n---\n<details>\n<summary> 🧪 Issue enrichment is currently in open beta.</summary>\n\n\nYou can configure auto-planning by selecting labels in the issue_enrichment configuration.\n\nTo disable automatic issue enrichment, add the following to your .coderabbit.yaml:\nyaml\nissue_enrichment:\n  auto_enrich:\n    enabled: false\n\n</details>\n\n💬 Have feedback or questions? Drop into our discord!', 'createdAt': '2026-06-08T14:10:59Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [], 'url': 'https://github.com/supabase/supabase/issues/46744#issuecomment-4649848070', 'viewerDidAuthor': False}] labels=bug,frontend,pr-opened）
- #46730 [CLOSED] Database Tables list stays stale after delete and overstates paginated progress（comments=[{'id': 'IC_kwDODMpXOc8AAAABFQ-LZw', 'author': {'login': 'coderabbitai'}, 'authorAssociation': 'CONTRIBUTOR', 'body': '<!-- This is an auto-generated issue plan by CodeRabbit -->\n<details>\n<summary>🔗 Related PRs</summary>\n\nsupabase/supabase#45885 - fix(studio): reports table footer overflow [merged]\nsupabase/supabase#46251 - fix(design-system): fix last table cell showing independent hover state [merged]\nsupabase/supabase#46285 - feat(studio): add useInfiniteTablesQuery hook for paginated tables [merged]\nsupabase/supabase#46402 - feat(studio): paginate Schema Designer via useInfiniteTablesQuery [merged]\nsupabase/supabase#46514 - feat(studio): paginate Tables list with server-side search [merged]\n</details>\n\n---\n<details>\n<summary>📝 Issue Planner</summary>\n\n<sub>Check the box below or use the @coderabbitai plan command to generate an implementation plan and prompts that you can use with your favorite coding assistant.</sub>\n\n- [ ] <!-- {"checkboxId": "8d4f2b9c-3e1a-4f7c-a9b2-d5e8f1c4a7b9"} --> Create Plan\n</details>\n\n\n---\n<details>\n<summary> 🧪 Issue enrichment is currently in open beta.</summary>\n\n\nYou can configure auto-planning by selecting labels in the issue_enrichment configuration.\n\nTo disable automatic issue enrichment, add the following to your .coderabbit.yaml:\nyaml\nissue_enrichment:\n  auto_enrich:\n    enabled: false\n\n</details>\n\n💬 Have feedback or questions? Drop into our discord!', 'createdAt': '2026-06-08T11:10:04Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [], 'url': 'https://github.com/supabase/supabase/issues/46730#issuecomment-4648307559', 'viewerDidAuthor': False}, {'id': 'IC_kwDODMpXOc8AAAABFRJCgA', 'author': {'login': '7ttp'}, 'authorAssociation': 'CONTRIBUTOR', 'body': 'thanks @luna-vivawq 💚\ncan confirm its reproducible, pushing up a fix :D ', 'createdAt': '2026-06-08T11:29:07Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [], 'url': 'https://github.com/supabase/supabase/issues/46730#issuecomment-4648485504', 'viewerDidAuthor': False}] labels=bug,frontend,pr-opened）
- #46707 [CLOSED] Anything（comments=[] labels=bug,external-issue,to-triage）
- #46701 [OPEN] Project stuck "Unhealthy" / API unreachable for 2+ hours — pmo-llm-demo（comments=[{'id': 'IC_kwDODMpXOc8AAAABFL374w', 'author': {'login': 'Hallidayo'}, 'authorAssociation': 'CONTRIBUTOR', 'body': "Hi @ChalaAkkaraju - if you aren't seeing any errors in the logs then you'd need to email support@supabase.com.", 'createdAt': '2026-06-07T14:31:13Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [], 'url': 'https://github.com/supabase/supabase/issues/46701#issuecomment-4642962403', 'viewerDidAuthor': False}] labels=bug,awaiting-details,external-issue）
- #46699 [OPEN] HTTP 522 on all auth endpoints — project fully unhealthy for several hours (PRO plan)（comments=[{'id': 'IC_kwDODMpXOc8AAAABFL4IIA', 'author': {'login': 'Hallidayo'}, 'authorAssociation': 'CONTRIBUTOR', 'body': 'Hi @Rishgundi - which region is your project in?', 'createdAt': '2026-06-07T14:32:34Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [], 'url': 'https://github.com/supabase/supabase/issues/46699#issuecomment-4642965536', 'viewerDidAuthor': False}] labels=bug,awaiting-details,external-issue）
- #46696 [CLOSED] VACUUM FULL + DD（comments=[{'id': 'IC_kwDODMpXOc8AAAABFHtt4g', 'author': {'login': 'coderabbitai'}, 'authorAssociation': 'CONTRIBUTOR', 'body': '<!-- This is an auto-generated issue plan by CodeRabbit -->\n<details>\n<summary>🔗 Related PRs</summary>\n\nsupabase/supabase#46486 - fix: cron job editing was done by name rather than Job ID [merged]\n</details>\n\n---\n<details>\n<summary>📝 Issue Planner</summary>\n\n<sub>Check the box below or use the @coderabbitai plan command to generate an implementation plan and prompts that you can use with your favorite coding assistant.</sub>\n\n- [ ] <!-- {"checkboxId": "8d4f2b9c-3e1a-4f7c-a9b2-d5e8f1c4a7b9"} --> Create Plan\n</details>\n\n\n---\n<details>\n<summary> 🧪 Issue enrichment is currently in open beta.</summary>\n\n\nYou can configure auto-planning by selecting labels in the issue_enrichment configuration.\n\nTo disable automatic issue enrichment, add the following to your .coderabbit.yaml:\nyaml\nissue_enrichment:\n  auto_enrich:\n    enabled: false\n\n</details>\n\n💬 Have feedback or questions? Drop into our discord!', 'createdAt': '2026-06-06T12:38:48Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [], 'url': 'https://github.com/supabase/supabase/issues/46696#issuecomment-4638600674', 'viewerDidAuthor': False}, {'id': 'IC_kwDODMpXOc8AAAABFHvbjA', 'author': {'login': '7ttp'}, 'authorAssociation': 'CONTRIBUTOR', 'body': 'please open a new issue w the template properly filled :) 💚', 'createdAt': '2026-06-06T12:49:01Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [], 'url': 'https://github.com/supabase/supabase/issues/46696#issuecomment-4638628748', 'viewerDidAuthor': False}] labels=bug,external-issue,to-triage）

### Pull Requests 抽样

PR 
- #46792 [OPEN] fix: clarify business purchase tooltip copyPR 
- #46791 [MERGED] Fixed a link in the Hosted Postgres pagePR 
- #46790 [OPEN] docs: clarify Advanced Telemetry section in Reports pagePR 
- #46789 [OPEN] chore(docs): add details and troubleshooting steps for auth schema er…PR 
- #46787 [OPEN] feat: first pass at db report chart colours

### Releases 抽样

v1.26.05（published=2026-05-07T23:45:42Z latest=True）
- v1.26.04（published=2026-04-09T14:38:08Z latest=False）
- v1.26.03（published=2026-03-05T18:43:08Z latest=False）
- v1.26.02（published=2026-02-05T21:38:22Z latest=False）
- v1.26.01（published=2026-01-08T15:46:04Z latest=False）

### 真实反馈与维护信号研判

抽样 issue 中 open/closed 约为 3/5，可作为维护者响应速度的弱信号。近期 PR 抽样里可见已合并项 2 个，说明项目并非完全冻结。存在 release 记录，说明作者有版本化交付意识。若外部搜索链路不可用，本报告明确以 GitHub issue/PR/release 作为一手社区反馈源，不用二手转载冒充口碑数据。
- 高频问题通常比 README 更能暴露真实落地难点：安装、兼容性、性能边界、文档歧义、平台限制。

## ⚔️ 竞品对比

维度supabase竞品/替代定位面向仓库作者设定的具体场景，通常更垂直Firebase / Neon + 自建后端 / Appwrite 往往更通用或生态更大学习曲线依赖其内部脚本/配置约定通用方案学习成本更高，但生态更成熟差异化仓库通常以“快上手、场景专用、意见化实现”为卖点通用方案强调可扩展、稳定性、跨场景能力

### 风险

作者驱动、文档深度可能不足、接口稳定性不确定大项目更稳定，但改造成本更高

## 🎯 核心研判

### 优势

对目标问题有强意见化实现，落地路径通常比“从零搭建通用栈”更短。如果核心文件少而清晰，二次阅读和定制成本较低。GitHub 原生 issue / release / PR 能直接帮助判断项目是否仍在演进。

### 风险

若 stars、forks、release 或 PR 活跃度偏低，意味着长期维护能力要谨慎评估。如果关键逻辑过于集中在单文件脚本中，后续扩展会受到可维护性约束。若缺少测试/CI/配置 schema，生产环境采用前应先做自测和边界验证。

### 适用场景

需要快速验证该仓库所解决的问题是否值得投入。团队愿意接受一定的作者意见化设计，以换取更快交付。适合作为参考实现、内部 PoC、垂直任务工具，而非默认直接替代成熟平台。不

### 适用场景

对 SLA、兼容矩阵、长期 LTS 有强要求的核心生产系统。需要极高社区冗余、插件生态或企业级支持的场景。

## 📂 关键文件路径速查

package.jsonpnpm-workspace.yamltsconfig.json
- `README.md`
- `CONTRIBUTING.md`packages/ai-commands/edge.tspackages/ai-commands/index.tspackages/ai-commands/src/docs.tspackages/ai-commands/src/errors.tspackages/ai-commands/src/sql/cron.tspackages/ai-commands/src/sql/functions.test.tspackages/ai-commands/src/sql/functions.ts

## ⭐ 三条关键发现

代码入口/骨架集中在：
- `package.json`, pnpm-workspace.yaml, tsconfig.json, 
- `README.md`, 
- `CONTRIBUTING.md`近期开源反馈以 issue 为主，典型议题包括：UI bug on table editor；Database Tables list stays stale after delete and overstates paginated progress发布节奏可从最新 release 观察：v1.26.05

## 🧪 研究方法与数据来源

GitHub Repo API / README / 默认分支递归文件树关键源码文件抽样精读Issues / PRs / Releases 社区活动抽样说明：
- 若外部搜索数据不可用，则明确标注并不伪造口碑结论
