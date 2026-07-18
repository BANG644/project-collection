# 🔬 oomol-lab/open-connector — 全方位深度调研

> 调研时间：2026-07-19 ｜ 数据源：gh api 元数据 + 仓库 README + 关键源码（src/core/guarded-fetch.ts、src/connection-service.ts）+ 英文 dudarik 长文 + 中文 掘金/头条 拆解
> 星标：⭐ 2,913（2026-06-29 建仓，三周 2.9 千⭐，fork 214）｜ 语言：TypeScript/Node.js 22+ ｜ 协议：Apache-2.0 ｜ 定位：Composio 的开源替代

## 📌 一句话定位

**OpenConnector 是面向 AI Agent 的开源连接器网关（connector gateway）：用户连接一次 SaaS 账号，它就通过 SDK / CLI / MCP / HTTP / OpenAPI 把一份可审查的「1,000+ providers、10,000+ 预置 Actions」共享 catalog 暴露给 agent——核心是「把 Agent 访问外部 SaaS 的边界收口成一个网关」，而不是又一个让 agent 更聪明的框架。**

## ⭐ 项目亮点

- **「可检查的 tool 账号边界」视角新颖**：掘金评测点破——Agent demo 跑顺只需塞 token，但产品化一步就撞墙：当前动作用哪个用户账号？token 有哪些 scope？agent 能否调危险 action？日志是否泄露敏感输入？同一工具在 MCP/HTTP/SDK/CLI 是否一致 schema？OpenConnector 的价值正在此处。
- **凭证永不出 runtime 边界**：provider secret 留在网关后，agent 只收 metadata、安全 account 标签、执行结果——天然解决「把 provider credential 直接塞给 agent 进程」的暴露问题。
- **四接口同一 catalog**：Connector SDK（TS HTTP client）/ oo CLI（本地 agent relay）/ MCP（`http://localhost:3000/mcp`）/ HTTP+OpenAPI（`/v1/actions/*` + 生成的 `/openapi.json`）——团队按运行时架构选集成模式，无需各自写适配器。
- **Action contracts 可审查**：每个 Action 带 request/response schema、required scopes、lazy-loaded executor 源码——契约透明，上游 API 漂移被抽象掉。
- **多部署含边缘**：local Docker/Node + SQLite / Fly.io + 持久 SQLite / **Cloudflare Workers + D1/R2/Static Assets** / OOMOL hosted runtime。开源版与商业 SaaS 共享同一套 provider id / Action id / schema / contracts。

## 🏗️ 项目架构全景

### 目录结构与设计哲学

| 路径 | 内容 |
|------|------|
| `src/core/` | action-policy / action-search / cast / catalog / credential-fields / execution / **guarded-fetch** / json-schema / provider-definition / provider-id / request / types / validation |
| `src/mail/imap-smtp/` | 邮件 Actions（actions / config） |
| `src/connection-service.ts` `src/catalog-store.ts` | 连接服务 / catalog 存储 |
| `scripts/` | generate-catalog / generate-provider-registry / generate-provider / search-actions / runtime-data / healthcheck |
| `docs/` | catalog-format / cloudflare / configuration / credentials / docker-ghcr / fly-io / gmail-oauth-sdk / quickstart / runtime-api / sdk-cli / verification |
| `examples/` | local-http（client/github/gmail/hackernews/notion）/ mcp-client / openai-tools |

### 技术栈 & 依赖

- Node.js 22+ 基础；网关核心 TS，Cloudflare 部署走 Workers + D1（关系态）+ R2（ transit 文件）+ Static Assets（控制台）。
- 本地/Node 部署自动配 SQLite 存连接元数据、命名 credential 库、执行日志。
- 提供商覆盖 GitHub / Gmail / Notion / BigQuery / Google Analytics / Supabase / Airtable / Slack…；credential 处理 API key / OAuth2 / custom / no-auth。
- `src/core/guarded-fetch.ts` 是安全边界的底层机制（见源码解读）。

### 配置一览

`docs/configuration.md` + `docs/credentials.md` 管 connection 别名、scopes、runtime tokens、action allow/block policy、临时文件 transit、redacted run logs。`docker compose up` 即起 `ghcr.io/oomol-lab/open-connector:latest`。

## 💡 应用场景与启发（重点章节）

### 典型使用场景

- **Agent 产品需要跨工作 app / 开发工具 / 数据系统 / 通信平台 / AI 服务 的可复用访问**，且不想把 provider 凭证交给 agent 进程。
- **加 agent 工作流但需要稳定、可审查的 Action 契约**——产品方要能看「这个 action 要哪些 scope、返回什么」。
- **要托管 auth 提速、又保留私有/自托管路径**的团队（OOMOL hosted 与开源 runtime 共享契约）。

### 可借鉴的解决方案模式

- **「凭证边界后置 + 契约前置」的网关模式**值得所有 agent 工具集成抄：agent 不直接持凭证，只持「连接别名 + Action id」，网关负责注入 auth header、校验 scope、记录 redacted 日志。**下次你要让 agent 调第三方 API，优先想「能不能走一个 credential 不出界的网关」而非「直接把 key 塞环境变量」**。
- **guarded-fetch 的跨源凭证头剥离**（见源码）是 SSRF/credential-exfil 防护的教科书实现——任何「agent 代发 HTTP」场景都该有。

### 同类需求的可参考思路

> 如果你在做 agent 平台、要让用户连自己的 SaaS，OpenConnector 的「一次连接 → 多接口暴露 → 凭证不出界 → 契约可审查 → 多部署」五段式，是一张可直接改写的参考架构，不用自己从零设计凭证生命周期。

## 🧠 核心源码解读（克制代码量）

### 1. 安全边界：guarded-fetch（src/core/guarded-fetch.ts）

这是「credential stays behind the runtime boundary」的底层机制。两段关键设计：

```ts
// DNS resolved-address 校验：默认守卫 reserved/loopback/link-local/metadata，
// 仅当显式 allowPrivateNetwork 时才放 RFC1918/共享地址空间
const crossOriginCredentialHeaders = new Set([
  "authorization", "proxy-authorization", "cookie",
  "api-key", "apikey", // 跨源 redirect 时剥掉，防 credential 经跳转外泄
]);
// 跨源 redirect 时，上面这组凭证头被显式剥离——用 allowlist 而非名字匹配，
// 所以绝不会误剥 look-alike 但非凭证头（如 idempotency-key / x-correlation-id）
```

> **为什么这样设计**：agent 代发请求天然有 SSRF + credential-exfil 双重风险。guarded-fetch 用「DNS 解析地址校验 + 跨源凭证头 allowlist 剥离 + 最多 20 跳 redirect」三道闸，把「上游 URL 由 agent/用户提供」的危险场景兜住——比「信任模型不乱跳」可靠得多。

### 2. 连接服务（src/connection-service.ts）

699 行的核心服务，负责解析命名连接、按 credential 类型（API key / OAuth2 / custom / no-auth）注入正确 auth header、对 Action 契约做请求校验、写 redacted run log。它是「网关」语义的真正承载者——agent 侧只看到统一的 Action 调用面。

### 3. Action 契约与策略（src/core/）

`action-policy.ts`（allow/block）、`action-search.ts`（按语义搜 Action）、`cast.ts`（响应信封标准化）、`provider-id.ts`（跨部署稳定 id）共同构成「契约可审查」的实现层——同一 Action 在 MCP/HTTP/SDK/CLI 下 schema 一致。

### 隐藏功能 & 未文档化特性

- `src/core/guarded-fetch.ts` 的 `allowPrivateNetwork` 是**每次请求重求值**的函数——部署后才设的 flag 也会被 honoring，不需重启。
- `skipDnsValidation` 仅当请求 host 是**固定/代码控制**时安全（如自家网关），用户/凭证派生的 host 上校验不可省。
- `src/mail/imap-smtp/` 是少见的**自托管邮件 Action**实现（actions/config），不依赖 Gmail OAuth，给隐私取向部署留后路。

## 📐 架构决策与设计哲学

- **网关而非 SDK**：不追求「agent 直接调 provider」，而是把「连接一次 → 多接口暴露 → 凭证不出界」收口成一层——产品化 Agent 的身份证。
- **开源与商业共享契约**：provider id / Action id / schema / contracts 在开源版与 OOMOL SaaS 版一致，用户可从托管平滑迁到自托管，不留锁定。
- **边缘优先部署**：Cloudflare Workers + D1/R2 让网关能跑在离用户近的边缘，降低 agent 调工具的延迟。

## 🌐 全网口碑画像

### 好评共识

- **「可检查的边界」视角被赞新颖**（掘金 dudarik 长文一致）：它解决的是 Agent 产品化真实瓶颈——credential 轮换、scope 管理、执行可见性、契约稳定性——不是「更多 token」。
- **开源替代 Composio 的叙事成立**：Apache-2.0 + 多部署（含 Cloudflare 边缘）+ MCP-native，对不想被商业平台锁定的团队有吸引力。
- **契约透明降低集成摩擦**：request/response schema + required scopes + lazy executor 源码，让「这个 action 到底能干嘛」一眼可见。

### 差评共识 & 踩坑高发区

- **「1,000+ providers / 10,000+ actions」是官方说法未自验**：掘金评测者明言「我没有复现，只按官方说法记录」——实际覆盖数需谨慎看待。
- **provider 贡献门槛**：`CONTRIBUTING.md` 对加 provider 有规则约束，生态广度依赖社区供给速度。

### 争议焦点

- **数字可信度**：官方标称的 catalog 规模尚无独立复现，早期采用者应以「实际能连的几个核心 provider」评估，而非盯大数。
- **与 Composio 的功能对齐度**：作为开源替代，Action 深度（尤其长尾 SaaS 的细粒度操作）是否追平商业版仍需逐个比对。

### 典型实战案例（中英文社区）

- **dudarik 长文**：把 OpenConnector 定位为「直接、开源的 Composio 替代，专为 MCP-native agent runtime 与 enterprise-grade SaaS 集成优化」；详述本地 Docker / Cloudflare / OOMOL hosted 三部署路径与四接口（SDK/oo CLI/MCP/HTTP+OpenAPI）。
- **掘金**：用一连串产品化真问题（哪个账号？哪些 scope？能否调危险 action？日志泄露？schema 一致？轮换怎么办？）论证「Agent 产品需要的不是更多 token，而是可检查的 tool 账号边界」。
- **头条/多语 README**（英/简中/繁中/日/俄/法）：国际化文档投入明显，降低非英语团队采用门槛。

### 维护者响应风格

oomol-lab 出品，AGENTS.md + CODE_OF_CONDUCT + CONTRIBUTING + NOTICE + SECURITY 齐备，社区治理规范；GitHub 228 commits、最近活跃（Jul 13 仍 feat）。反馈走 GitHub Issues/PR。

## ⚔️ 竞品对比

| 维度 | OpenConnector | Composio | Zapier AI Actions | Pipedream | 自写 connector |
|------|----------------|----------|------------------|------------|--------------|
| 开源 | ✅ Apache-2.0 | ❌ 商业 | ❌ 商业 | 商业/自托管 | 取决于你 |
| MCP-native | ✅ | 部分 | 部分 | 部分 | 自己接 |
| 凭证不出界 | ✅ 网关后置 | 平台侧 | 平台侧 | 平台侧 | 自己保证 |
| 边缘部署 | ✅ Cloudflare | ❌ | ❌ | 部分 | 自己搭 |
| Action 契约可审查 | ✅ | 平台侧 | 平台侧 | 部分 | 自己写 |

### 选择建议

- 要**开源、自托管、凭证边界清晰、MCP-native** 的 agent 工具网关 → OpenConnector 当前最贴合。
- 要大生态/商业支持/少运维 → Composio 更成熟。
- 只要简单 API 串联 → Zapier/Pipedream 更轻。

## 🎯 核心研判

### 项目优势（不可替代的价值点）

1. **「凭证边界后置 + 契约前置」的网关范式**精准命中 Agent 产品化痛点，且开源+MCP+边缘部署组合稀缺。
2. **guarded-fetch 的安全边界实现**是 agent 代发 HTTP 场景的范本，可被广泛复用。
3. **开源/商业契约一致**，用户无锁定风险，迁移路径干净。

### 项目风险（潜在隐患和局限性）

1. **catalog 规模数字未独立复现**，早期评估应看实际核心 provider 而非大标称。
2. **生态广度依赖社区供给**，长尾 SaaS 的 Action 深度待比对商业竞品。
3. **星标基数小（2.9k）**，生产采用前需看真实大客户案例与 SLA。

### 适用场景 & 不适用场景

- ✅ 适合：Agent 产品做用户 SaaS 连接、要凭证不出界+契约可审查、想自托管或跑边缘。
- ❌ 不适合：只要轻量 API 串联、要商业级 SLA/大客户案例、不愿自己运维网关。

### 趋势判断

**上升期（niche 但命题精准）**。「Agent 需要可检查的 tool 账号边界」是 2026 年 agent 产品化的真问题，OpenConnector 用开源+MCP+边缘把它讲透了。变量在：catalog 真实广度能否跟上标称、以及能否从 Composio 抢到生产客户。

## 📂 关键文件路径速查

| 路径 | 内容 |
|------|------|
| `src/core/guarded-fetch.ts` | **安全边界**：DNS 解析校验 + 跨源凭证头剥离 + redirect 限跳 |
| `src/connection-service.ts` | 连接服务：解析命名连接、注入 auth、校验契约、写 redacted 日志 |
| `src/core/action-policy.ts` | Action allow/block 策略 |
| `src/core/action-search.ts` `src/core/cast.ts` | Action 语义搜索 / 响应信封标准化 |
| `src/core/provider-id.ts` `src/core/catalog.ts` | 跨部署稳定 provider id / catalog |
| `src/mail/imap-smtp/` | 自托管邮件 Action（actions/config） |
| `src/catalog-store.ts` | catalog 存储 |
| `scripts/generate-provider-registry.ts` | provider 注册表生成 |
| `docs/runtime-api.md` `docs/catalog-format.md` | 运行时 API / catalog 格式 |
| `docs/cloudflare.md` `docs/fly-io.md` `docs/credentials.md` | Cloudflare / Fly.io / 凭证部署 |
| `examples/local-http/` `examples/mcp-client/` `examples/openai-tools/` | 三接口集成示例 |
| `AGENTS.md` `NOTICE.md` `SECURITY.md` | 治理文档 |
