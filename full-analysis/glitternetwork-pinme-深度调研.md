# glitternetwork/pinme 深度调研

> 调研日期：2026-09-21 | 星标：3,748⭐ | 语言：TypeScript | 许可：MIT | 默认分支：main | 最近提交：活跃

## 一句话定位
PinMe 是零配置一键部署 CLI：前端 + Cloudflare Worker 后端 + D1 数据库，一条命令上线；同时支持纯静态资源上传到 IPFS（含 CAR 导入导出、域名绑定），并原生支持 Claude Code Skill。

## 项目亮点
- **项目模式分层部署**：`create` 拉模板 + 平台开通资源；`save` 一键部署 Worker+SQL+前端；`update-worker / update-db / update-web` 按需只更新某一层，避免全量重传。
- **IPFS 原生 + Worker 一体**：静态 `upload` 直接上 IPFS，`import / export` 走 CAR 文件，域名绑定支持 PinMe 子域与 DNS 域；后端用 Cloudflare Worker + D1，无需自管服务器。
- **面向 Agent 的协议**：`pinme.toml` 描述项目；错误是机器可读的结构化 `CliError`（含修复建议），guardrails 明确「不要传 src/、node_modules、.env」；`npx skills add glitternetwork/pinme` 直接装技能。
- **测试严谨**：Vitest + nock 拦截 + Stryker 变异测试门禁，`TESTING.md` 规定不调用真实服务。
- **agent-first 工程化**：仓库带 `AGENTS.md` / `CLAUDE.md` / `llms.txt.md`，显式给 AI 工作流协议（Project-mode / Static-upload fallback）。

## 核心架构
- `bin/index.ts`：commander 注册全部子命令（upload / import / export / rm / login / create / save / update-* / delete / domain / list…）。
- `bin/services/uploadService.ts` + `bin/utils/`：上传 / 鉴权 / API 客户端 / IPFS 分片 / 域名校验。
- `save` 流程：`loadConfig` → `buildWorker`（wrangler）→ 上传 Worker+SQL → 构建并上传 `frontend/dist` → 可选绑定域名。

## 应用场景与启发
- 「生成即上线」：Agent 产出的前端/全栈 demo，一条 `pinme save` 拿到公开 URL，适合作品集 / 原型 / 内测。
- 分层 `update-*` 命令揭示「声明式部署」应支持增量更新，避免每次全量。
- `AGENTS.md` + 结构化错误 + guardrails 是「CLI 如何对 Agent 友好」的范本。

## 源码解读
**命令注册（`bin/index.ts`）**

```ts
program.command('save')
  .description('Deploy the project (frontend + backend)')
  .option('-d, --domain <name>', 'Bind a domain after frontend deploy')
  .action((options) => saveCmd(options));
// 其余 upload/import/export/rm/login/create/update-* 同构注册
```

**部署流程（`bin/save.ts`）**

```ts
function buildWorker() {
  execSync('npm run build:worker', { cwd: PROJECT_DIR, stdio: 'inherit' });
}
// save: loadConfig → buildWorker → upload Worker+SQL → build+upload frontend/dist → bind domain
```

## 全网口碑
GitHub 3.7k⭐、Cloudflare 生态、文档含 `AGENTS.md` / `CLAUDE.md` / `llms.txt.md` 体现 agent-first 取向；社区以「IPFS + Worker 一键部署」为卖点。

## 竞品对比 + 核心研判
- 竞品：`wrangler`（Cloudflare 官方）、`vercel` / `netlify` CLI、Railway。
- 研判：PinMe 把「全栈（前端+Worker+D1）一键部署 + 静态 IPFS 上传」合并进一个 agent 友好的 CLI，差异化在 IPFS 原生与分层更新；代价是平台绑定 glitternetwork（钱包 / 域名需余额）。适合「快速把 demo 公开」的 Agent / 独立开发者。

## 关键文件路径速查
- `bin/index.ts` — 命令注册入口
- `bin/save.ts` — 项目部署流程
- `bin/services/uploadService.ts` — 上传服务
- `bin/utils/` — apiClient / auth / uploadToIpfs* / domainValidator
- `AGENTS.md` / `CLAUDE.md` / `llms.txt.md` — Agent 协议
- `example/` — 官方示例（blog / supabase）
