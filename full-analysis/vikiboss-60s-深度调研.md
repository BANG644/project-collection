# vikiboss/60s 深度调研

> 调研日期：2026-09-29 ｜ 数据源：gh API（README / 目录树）｜ 定位：高质量开源聚合 API 集合（每天 60 秒读懂世界）

## 一、项目定位（一句话）

**60s API** 是一系列**高质量、开源、可靠、全球 CDN 加速**的免费开放接口集合：每天 60 秒看世界、各平台热搜、金价油价天气翻译壁纸 Epic 游戏二维码猫眼票房等，构建于 Deno、可一键部署到 Docker / Cloudflare Workers / Bun / Node.js。

## 二、项目亮点（差异化）

1. **多运行时零改造部署**：同一份 TS 源码提供 `deno.ts` / `bun.ts` / `node.ts` / `cf-worker.ts` 四个入口，覆盖 Deno Deploy、Cloudflare Workers、Docker、Bun、Node.js——"写一次，到处跑"。
2. **数据源权威 + 智能缓存**：优先选官方/权威源，部分接口智能缓存做到毫秒级响应、全球 CDN 加速。
3. **自动化数据流水线**：`vikiboss/60s-static-host` 仓库用 GitHub Actions 定时任务 + Gemini 大模型精准抓取，产出静态 JSON + CDN 缓存（如每日 60s 新闻由微信公众号经 Gemini 提炼 15 条）。
4. **Agent Skills 友好**：官方提供 `vikiboss/60s-skills` 并在 skills.sh 上架，可被 agent 直接调用。
5. **模块爆炸式覆盖**：`src/modules/` 下数十个独立模块（B站/抖音/微博/知乎/百度/必应/翻译/金价/油价/票房/奥运/网易云/Epic/Hacker News…），接入新数据源只需加一个 module。

## 三、核心架构

- **应用骨架 `src/`**：
  - `app.ts` — 应用装配
  - `router.ts` — 路由聚合（把各 module 挂到统一前缀）
  - `common.ts` — 公共工具（请求/响应/缓存）
  - `config.ts` — 运行配置
  - `middlewares/` — `cors.ts`、`blacklist.ts`、`encoding.ts`(text/json/image 多编码)、`debug.ts`、`favicon.ts`、`handle-global-error.ts`、`not-found.ts`
- **模块化路由 `src/modules/*.module.ts`**：每个接口一个 module（如 `60s.module.ts`、`bili.module.ts`、`douyin.module.ts`、`fanyi/`、`gold-price.module.ts`、`hacker-news.module.ts`、`maoyan/`、`olympics/`、`ncm.module.ts`…），`router.ts` 统一汇总——新增数据源成本极低。
- **多运行时入口**：根目录 `deno.ts` / `bun.ts` / `node.ts` / `cf-worker.ts` + `wrangler.toml` + `Dockerfile`，Node 端用 `node --experimental-strip-types` 免编译跑 TS。
- **数据侧（外部仓库）**：`vikiboss/60s-static-host` 承担抓取与 Gemini 提炼，本仓库只做 API 服务，职责清晰。

## 四、应用场景与启发

- **场景**：移动 App 资讯模块、网站首页信息流、聊天机器人新闻推送、邮件日报、桌面通知、个人 Dashboard、agent 工具调用。
- **启发（对同类需求）**：
  - "一个 module 一个数据源 + 统一 router + 多运行时入口"是把**聚合 API**做到易扩展的极简范式，加接口只是新增一个 `.module.ts`。
  - 把"重抓取/LLM 提炼"下沉到独立 `*-static-host` 仓库、主仓库只做轻量 API+缓存，是**关注点分离**的好样板，避免抓取逻辑污染服务。
  - 多运行时入口设计值得抄：同一 TS 代码用不同启动文件适配 Deno/Workers/Bun/Node，降低部署门槛。

## 五、源码深度解读（核心模块）

**1. 路由聚合 `src/router.ts` + `src/modules`**
每个 module 导出路由，router 统一挂载。例如 `60s.module.ts` 处理 `/v2/60s` 并支持 `encoding=text|image|image-proxy` 三种输出（纯文本 / 原图直链 / 代理返回二进制）——这种"同一接口多编码"模式在 `middlewares/encoding.ts` 统一处理。

**2. 中间件 `src/middlewares`**
`cors`/`blacklist`/`handle-global-error`/`not-found` 构成标准 API 网关能力；`encoding.ts` 负责按 `?encoding=` 切换响应形态，是 60s "一张图/一段文本/JSON"多形态输出的关键。

**3. 数据流水线（外部 `60s-static-host`）**
GitHub Actions 定时触发 → Gemini 提炼微信公众号等源 → 落静态 JSON → CDN 缓存。主 API 仅读缓存，做到毫秒响应、限流友好。这种"定时抓取与实时服务解耦"是开放 API 高可用的常用手法。

## 六、社区口碑

- 5.8k⭐、1108 fork（fork 比极高，说明大量人自建部署），MIT 许可。
- HelloGitHub 推荐，QQ 社群活跃；公共实例因额度有限鼓励自部署，社区公共实例列表在文档站维护。
- 文档站 `docs.60s-api.viki.moe`（Apifox）持续更新，并明确"公共 API 已迁移 Cloudflare Workers、额度有限、建议自部署"。

## 七、竞品对比 + 核心研判

| 维度 | 60s | RSSHub | 各平台官方 Open API |
|---|---|---|---|
| 免鉴权聚合 | ✅ | ✅ | ❌(各需 key) |
| 多运行时部署 | ✅ | 部分 | N/A |
| 数据缓存/CDN | ✅ | 视部署 | 视部署 |
| 中文场景覆盖 | 深(热搜/油价/票房) | 广(RSS 源) | 散 |

**研判**：60s 在"中文互联网实时信息聚合 + 免鉴权 + 一键多平台部署"上比 RSSHub 更贴近国内开发者需求，module 化使其扩展轻松。风险点：公共实例依赖单一 CDN 额度、部分数据源（如微信公众号）本身不稳定，生产务必自部署；另需注意部分接口实质是第三方页面的非官方抓取，商用前确认数据源合规。整体是"聚合 API 服务"的优秀参考实现。

## 八、关键文件路径速查

- 仓库根：`https://github.com/vikiboss/60s`
- 文档站：`https://docs.60s-api.viki.moe`
- 应用骨架：`src/app.ts`、`src/router.ts`、`src/common.ts`、`src/config.ts`
- 中间件：`src/middlewares/`（cors / blacklist / encoding / handle-global-error / not-found）
- 接口模块：`src/modules/`（60s / bili / douyin / fanyi / gold-price / hacker-news / maoyan / olympics / ncm …）
- 多运行时入口：`deno.ts`、`bun.ts`、`node.ts`、`cf-worker.ts`、`wrangler.toml`、`Dockerfile`
- 数据流水线：`vikiboss/60s-static-host`（Gemini 提炼 + Actions 定时）
- Agent Skills：`vikiboss/60s-skills`
