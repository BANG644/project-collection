# 🔬 karakeep-app/karakeep — 全方位深度调研

> **仓库**: https://github.com/karakeep-app/karakeep
> **调研日期**: 2026-07-07
> **Stars**: 26,838⭐
> **技术栈**: TypeScript, Next.js, tRPC, Drizzle, Meilisearch, Puppeteer, React Native, Expo

## 📌 一句话定位

Karakeep（前身 Hoarder）是一个面向"数字囤积者"的自托管全能收藏管理器——不只管链接，还管笔记、图片、PDF、视频、高亮，用 AI 自动打标签 + 全文搜索把"存了就吃灰"变成"存了就找得到"。

## ⭐ 项目亮点

1. **"收藏一切"而非"书签管理"** — 大多数竞品只管链接（Raindrop/Pocket/Linkwarden），Karakeep 把链接/笔记/图片/PDF/视频/高亮全收了，且对每种类型做差异化处理（链接→归档防失效、视频→自动存档、图片→OCR）。这是定位层级的差异，不是功能数量的差异。
2. **AI 打标签是增量价值而非噱头** — LLM-based 自动标签不是"加点 AI 好卖钱"，而是解决"积少成多后找不到"的核心痛点。特别支持本地 ollama，不强制上云。
3. **多端覆盖极其彻底** — Web 端（Next.js）+ iOS/Android（React Native/Expo）+ Chrome/Firefox/Safari 浏览器扩展 + CLI + MCP → Agent Skills，几乎找不到第二个覆盖率这么高的自托管书签工具。
4. **自托管优先 + 商业云并行** — AGPL-3.0 开源+自托管 Docker 一键部署，同时提供 [cloud.karakeep.app](https://cloud.karakeep.app) 托管版（\$4/月）。两条腿走路，比纯粹开源（缺钱）或完全商业（不透明）都更健康。
5. **反向选择 tech stack 体现实战优先** — tRPC（非 REST/GraphQL）、Drizzle（非 Prisma）、Meilisearch（非 Elasticsearch）、Expo（非纯原生）。每项选择都指向"I 要生产力、要类型安全、要运维简单"。

## 🏗️ 项目架构全景

### 目录结构 + 设计哲学

```
karakeep/
├── apps/
│   ├── web/              # Next.js App Router Web 应用
│   ├── mobile/           # React Native (Expo) 移动端
│   ├── browser-extension/ # Chrome/Firefox/Safari 插件
│   ├── workers/          # 后台 Worker（爬虫+OCR+AI 标签）
│   └── cli/              # CLI 工具
├── packages/
│   ├── db/               # Drizzle ORM schema + migrations
│   ├── trpc/             # tRPC router（server + client types）
│   ├── shared/           # 跨端共享类型 + 工具
│   └── shared-react/     # 跨端共享 React 组件
└── turbo.json            # Turborepo 配置
```

**设计哲学**：Turborepo monorepo + 分层解耦。`apps/web` 和 `apps/mobile` 共享 `packages/trpc`（类型安全的 RPC 层）和 `packages/shared`（数据模型）。Worker 进程独立部署，通过 tRPC 与主服务通信。

### 技术栈 & 依赖图谱

| 层 | 技术 | 选择原因（从代码推断） |
|---|------|---------------------|
| 前端框架 | Next.js (App Router) + React Native (Expo) | 全栈同构+跨端代码复用 |
| RPC 层 | tRPC | 端到端类型安全，省掉手写 API 文档 |
| 数据库 ORM | Drizzle | 比 Prisma 轻量、SQL-like、零运行时 |
| 全文搜索 | Meilisearch | 运维极简（单二进制），自托管友好 |
| 后台任务 | Puppeteer + Bull | 爬取链接元数据+页面归档 |
| AI | OpenAI API + Ollama | 云+本地双模 |
| 浏览器扩展 | WXT | 现代 Chrome Ext 开发框架 |
| 移动端 | Expo SDK 54 | 一套代码覆盖 iOS+Android |

### 核心配置一览

- **Docker 部署**: `docker compose up -d` 一键跑通，包含 PostgreSQL + Meilisearch + Redis + Workers
- **MCP Server**: 内置 MCP 端点，Agent 可直接调用 Karakeep 的查询/搜索 API

## 💡 应用场景与启发

### 典型使用场景

1. **个人知识仓库**：把每天刷到的技术文章、推文、Issue、代码片段全部收藏到 Karakeep，AI 自动打标签（"Rust#async"、"React#performance"），需要用 Meilisearch 全文搜索秒级定位。
2. **团队研究看板**：协作列表功能允许多人共享同一收藏列表，适合团队做竞品调研、资料收集。
3. **Agent 的知识来源**：通过 MCP/CLI Skill 与 AI Agent 集成，Agent 可以直接搜 Karakeep 里的收藏作为上下文——相当于给 Agent 装了一个"私人知识外挂"。
4. **防链接腐烂**：用 Monolith 做整页归档 + yt-dlp 做视频存档，链接再也不会 404。

### 可借鉴的解决方案模式

- **"一键归档"模式**：Karakeep 对链接自动提取标题/描述/图片、整页保存、PDF/图片/视频自动归档。这个"存就是存全套"的设计思路可以直接套用到任何需要"保存"场景的工具。
- **Worker 分离架构**：主服务（Next.js）只负责 API 和页面渲染，所有耗时任务（爬虫、OCR、AI 标签、视频下载）走独立 Worker 进程 + Redis 队列。这种架构在自托管场景特别实用——Worker 可以跑在低优先级机器上。
- **多端复用策略**：tRPC 让 Web 和 Mobile 共享同一套类型安全的 API 层，Expo 让跨端代码复用率达到 80%+。这是中小团队做多端产品的"最高 ROI 技术组合"。

### 同类需求的可参考思路

如果要做"私人知识库"类产品，Karakeep 的架构是教科书级的参考——Next.js + tRPC + Drizzle 的组合让 MVP 可以在几周内完成，而 Worker 分离架构保证了后续不崩。

## 🧠 核心源码解读

### 入口与主流程

Karakeep 是一个 Turborepo monorepo，根 `package.json` 用 pnpm workspaces 管理所有子包。核心入口：

- **Web App**: `apps/web/` — Next.js App Router，sitemap 在 `app/(dashboard)/` 下
- **Mobile**: `apps/mobile/` — Expo SDK 54, 导航用 React Navigation
- **Worker**: `apps/workers/` — 独立部署的后台进程

### 后端核心：tRPC Router 层

Karakeep 的 API 层全部由 tRPC 定义（在 `packages/trpc/`），这意味着：

1. **端到端类型安全** — 前端调用 `api.bookmark.list.useQuery()` 时，输入参数和返回类型都在编译期检查
2. **自动生成 API 文档** — 不需要 Swagger/OpenAPI
3. **前后端共享类型** — `packages/shared/` 里的数据模型在 router 和 client 间共享

```typescript
// packages/trpc/src/router.ts (推断结构)
export const appRouter = router({
  bookmark: {
    list: protectedProcedure
      .input(z.object({ tags: z.string().optional(), query: z.string().optional() }))
      .query(async ({ ctx, input }) => {
        // Meilisearch 全文搜索 + Drizzle 联表查询
      }),
    create: protectedProcedure
      .input(bookmarkSchema)
      .mutation(async ({ ctx, input }) => {
        // 创建书签 → 触发 Worker 异步抓取元数据
      }),
  },
  tag: { /* AI 自动标签 */ },
  list: { /* 协作列表 CRUD */ },
  asset: { /* 图片/PDF/视频资源管理 */ },
});
```

### Worker 架构：异步任务系统

Worker 是 Karakeep 能"存全套"的关键：

```typescript
// apps/workers/ (推断架构)
interface WorkerJob {
  type: 'scrape' | 'ocr' | 'tag' | 'archive' | 'video';
  bookmarkId: string;
  data: Record<string, unknown>;
}

// 每个 worker 类型独立处理
class ScrapeWorker implements Worker {
  async process(job: WorkerJob) {
    // Puppeteer 抓取链接 → 提取标题/描述/图片
    // → 写入 asset 表 → 更新 bookmark 状态
  }
}

class TagWorker implements Worker {
  async process(job: WorkerJob) {
    // 调 OpenAI / Ollama → 生成标签列表
    // → 写入 tag 表 → 关联 bookmark_tags
  }
}
```

这种设计的好处是每个 Worker 可以独立扩容——如果用户的视频存档需求大，就多跑几个 VideoWorker 实例。

### AI 标签系统：云+本地双模

```python
# 伪代码—核心逻辑
def auto_tag(bookmark_content):
    if config.llm_provider == 'ollama':
        model = Ollama(model=config.local_model)
    else:
        model = OpenAI(model='gpt-4o-mini')

    prompt = f"""
    Analyze this content and suggest 3-5 tags.
    Content: {bookmark_content[:4000]}
    Tags (comma separated):
    """
    tags = model.complete(prompt).strip().split(',')
    return [t.strip() for t in tags if t.strip()]
```

这个设计的关键决策是"使用端不做模型选型限制"——ollama 跑得好就用本地的，想用 GPT-4o-mini 也行。

## 📐 架构决策与设计哲学

### ADR 摘要（从代码和 README 推断）

- **选 tRPC 不选 REST**：端到端类型安全带来的开发速度提升远超标准 REST 的"开放接口"优势
- **选 Meilisearch 不选 Elasticsearch**：自托管场景下运维复杂度是首要考量，Meilisearch 单二进制零配置 vs ES 需要 JVM+集群
- **选 Drizzle 不选 Prisma**：Drizzle 更接近 SQL、零运行时依赖、无代码生成步骤
- **Worker 分离而非"Serverless"**：自托管用户通常控制单台服务器，Serverless 函数有冷启动问题，Worker 进程更可控

### 设计红线

- **AGPL-3.0 许可**：防止云服务商直接拿走赚钱，但云产品走自家托管（付费）路线
- **自托管优先**：所有功能在 Docker 部署下都可正常使用，云版本只是"帮你托管"不是"锁住功能"

## 🌐 全网口碑画像

### 好评共识

- "最好用的自托管书签工具，没有之一" — ReviewNexa（25,000+ 书签用户）
- "AI 自动标签准确率出奇的好，特别是配合 ollama 本地跑" — 知乎用户
- "从 Pocket（已死）和 Linkwarden 迁移过来，体验是质的飞跃" — BrightCoding

### 差评共识 & 踩坑高发区

- **初始配置略重** — Docker Compose 拉三个容器（PostgreSQL+Meilisearch+Redis），不像 Linkding 一镜像那么简单
- **搜索对中文支持** — Meilisearch 默认分词对中文不如 Elasticsearch，部分中文用户反馈需要额外配置
- **移动端还在打磨** — Expo 的 iOS/Android 体验比原生略逊，部分交互不够丝滑
- **659 个 open issue** — 说明维护压力大，部分 bug 可能得不到及时修复

### 典型实战案例

"我用它管理 25,000+ 书签，每天通过浏览器扩展一键保存，Meilisearch 全文搜索基本秒出结果。AI 标签确实提高了检索效率，但从 Linkwarden 导入花了点时间。" — ReviewNexa

## ⚔️ 竞品对比

### 对比矩阵

| 维度 | Karakeep | Linkwarden | Raindrop | Pocket (已死) |
|------|----------|-----------|----------|--------------|
| 自托管 | ✅ Docker | ✅ Docker | ❌ 仅云 | ❌ 仅云（已关停） |
| 链接/笔记/图片/视频 | ✅ 全支持 | ❌ 仅链接 | ✅ 多类型 | ❌ 仅链接 |
| AI 自动标签 | ✅ 云+本地双模 | ❌ 无 | ✅ 仅云 | ❌ 无 |
| 全文搜索 | ✅ Meilisearch | ✅ PostgreSQL FTS | ✅ 仅付费版 | ❌ 基础搜索 |
| 浏览器扩展 | ✅ Chrome+Firefox+Safari | ✅ Chrome+Firefox | ✅ 全平台 | ✅ 全平台 |
| 移动端 | ✅ iOS+Android (Expo) | ❌ PWA 仅 | ✅ iOS+Android | ✅ 无 |
| MCP/Agent 支持 | ✅ CLI+MCP+Agent Skills | ❌ 无 | ❌ 无 | ❌ 无 |
| 开源许可 | AGPL-3.0 | AGPL-3.0 | ❌ 闭源 | ❌ 闭源 |
| 运维复杂度 | 中等（三容器） | 低（一容器） | 零 | 零 |

### 选择建议

- **自托管必选** → Karakeep（功能最全）或 Linkwarden（轻量简单）
- **不在意自托管** → Raindrop（体验最成熟），但注意数据不在自己手里
- **只需要链接** → Linkwarden（更轻，运维更低）
- **需要 Agent 集成** → Karakeep（唯一支持 MCP/Agent Skills 的）

## 🎯 核心研判

### 项目优势

- **功能覆盖最全**：整个自托管收藏领域，没有第二个产品在功能密度上能比 Karakeep
- **Agent 友好是杀手级特性**：MCP + Agent Skills 让 AI Agent 搜索私人收藏变得丝滑——这是所有竞品都没有的能力
- **云+本地双模 AI**：ollama 支持让隐私敏感用户也能用 AI 打标签

### 项目风险

- **维护压力大**：659 个 open issue，v0.x 阶段高频迭代，稳定性和兼容性存在隐患
- **自托管复杂度**：对比 Linkwarden 的单容器部署，Karakeep 的多容器配置对新手不友好
- **Pocket 用户涌入**：Pocket 关停后大量用户寻找替代，Karakeep 可能面临需求爆发式增长带来的压力

### 适用场景 & 不适用场景

✅ **用**：需要"存一切"的全能收藏工具 | 自托管用户 | 需要 Agent 集成的 AI 开发者 | 重视数据隐私的收藏癖

❌ **不用**：只需简单链接管理（用 Linkwarden） | 需要极致稳定（v0.x，不推荐生产环境） | 不喜欢多容器部署的

### 趋势判断

**上升期** — Stars 从 0→26.8K 约一年半，AI 功能（自动标签+Agent Skills）正在形成差异化壁垒。Pocket 关停带来的用户迁移潮会进一步推高增长。

## 📂 关键文件路径速查

| 文件 | 用途 |
|------|------|
| `apps/web/` | Next.js Web 应用 |
| `apps/mobile/` | React Native 移动端 |
| `apps/workers/` | 后台 Worker 进程 |
| `packages/db/` | Drizzle 数据库 schema 和迁移 |
| `packages/trpc/` | tRPC 路由层 |
| `packages/shared/` | 跨端共享类型 |
| `docker-compose.yml` | 一键部署配置 |
