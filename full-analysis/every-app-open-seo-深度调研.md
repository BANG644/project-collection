# 🔬 every-app/open-seo — 全方位深度调研

## 📌 一句话定位

Semrush 和 Ahrefs 的**开源替代品**——自托管的 SEO 平台，核心功能包括关键词研究、排名追踪、竞争对手分析、外链分析和网站审计。最大差异化是内置 MCP 服务器和 AI Agent Skills，可以接入 Claude Code/OpenClaw/Hermes 等 Agent。

## ⭐ 项目亮点

- **AI 优先级高于 UI**：OpenSEO 的核心竞争力不是 UI（虽然 UI 做得不错），而是**Agent 可以像人一样使用它**——通过 MCP 服务器直接查询关键词数据、分析外链、监控排名。这比传统 SEO 工具手动导出 CSV 再喂给 LLM 的流程高效太多
- **Pay-as-you-go 计费**：不像 Semrush 月付 $200+，OpenSEO 通过 DataForSEO API 实现按使用量付费——典型场景下每月只需 $5-$50
- **纯 TypeScript + Cloudflare 原生**：全栈 TypeScript 跑在 Cloudflare Workers 上，无需管理服务器。Docker 自托管也支持
- **7 个内置 Agent Skills**：keyword-research、seo-coach、competitive-landscape、link-prospecting 等，让 AI Agent 可以直接执行复杂的 SEO 工作流
- **MCP 集成是第一等公民**：不仅仅是"支持 MCP"，而是设计之初就把 MCP 作为核心交互接口。Issue 中的讨论（#30、#36）显示社区正在积极扩展 MCP 工具集

## 🏗️ 项目架构全景

### 目录结构

```
every-app/open-seo/
├── src/                        # 应用源码
│   ├── db/                     # Drizzle ORM 数据库 Schema
│   ├── ...                     # 各功能模块
├── drizzle/                    # 26 次数据库迁移
│   ├── 0000_*.sql ~ 0025_*.sql
├── .agents/skills/             # AI Agent Skills
│   ├── keyword-research/SKILL.md
│   ├── seo-coach/SKILL.md
│   ├── competitive-landscape/SKILL.md
│   ├── competitor-analysis/SKILL.md
│   ├── keyword-clustering/SKILL.md
│   ├── link-prospecting/SKILL.md
│   └── seo-project-setup/SKILL.md
├── .claude/skills/             # Claude Code 专用技能
│   ├── merge-ready/SKILL.md
│   └── openseo-release-notes/SKILL.md
├── docs/                       # 部署文档
├── e2e/                        # Playwright 端到端测试
├── cli-auth.ts                 # Auth.js CLI 配置
├── compose.yaml                # Docker Compose
├── Dockerfile.selfhost         # Docker 自托管构建
├── wrangler.jsonc              # Cloudflare Workers 配置
├── drizzle.config.ts           # Drizzle 配置
└── package.json
```

### 技术栈

- **前端**：React 19 + TanStack Router + Tailwind 4 + daisyUI
- **后端**：Cloudflare Workers + D1 数据库
- **ORM**：Drizzle ORM（26 次迁移）
- **Schema**：Zod 4 + Drizzle Schema
- **Auth**：Better Auth + Cloudflare Access
- **AI**：AI SDK + OpenRouter
- **测试**：Playwright + Vitest
- **部署**：Cloudflare Workers / Docker

### 核心依赖

- `dataforseo-client` — DataForSEO API 客户端（所有 SEO 数据的来源）
- `@modelcontextprotocol/sdk` — MCP SDK 实现
- `@cloudflare/workers-oauth-provider` — 自带 OAuth 提供者
- `@tanstack/react-router` — 路由（文件系统路由？类似 Vite 风格）

## 💡 应用场景与启发

### 典型使用场景

1. **Freelancer/小团队的 SEO 工具**：$200/月的 Semrush 太贵，$5-50/月的 OpenSEO 是完美替代
2. **AI Agent 驱动的内容策略**：让 Claude Code 通过 OpenSEO MCP 做关键词调研 → 内容规划 → 竞品分析的完整工作流
3. **自托管的白标 SEO 报告**：可以 fork 后定制 UI 和品牌，为客户生成 SEO 报告
4. **站群/多站点 SEO 监控**：Docker Compose 一键部署，每个站点独立配置

### 可借鉴的解决方案模式

- **MCP + Agent Skills 的双层架构**：底层 MCP 提供数据接口（关键词、外链、排名），上层 Agent Skills 提供工作流（"如何做 SEO 审计"）。这种架构值得其他数据驱动的工具参考
- **Pay-as-you-go 嵌入**：不自己做 API、不绑定用户到月费，而是让用户带自己的 API Key——降低了项目的法律风险（不是 SaaS 而是工具）
- **Cloudflare Workers + D1 的极致成本**：几乎零成本的数据库 + 全球部署，适合"自托管 SaaS"场景

### 同类需求的可参考思路

如果要做类似的开源 SaaS 替代品，从 OpenSEO 可以学到：
1. **先用 Agent Skills 兑现价值**：开发完整 UI 很慢，但先做好 MCP + 几个 Agent Skill，用户立刻能用 Agent 操作
2. **自己的 API Key，自己的数据**：用户自带 API Key = 无需担忧法律法规和数据隐私
3. **双部署路径**：Docker（简单） + Cloudflare（可暴露互联网）

## 🧠 核心源码解读

### Agent Skills 设计（以 keyword-research 为例）

```markdown
# .agents/skills/keyword-research/SKILL.md

## 工作流程

1. 用户提供种子关键词和目标网站
2. 通过 OpenSEO MCP 调用 `keyword_research` 工具获取数据
3. 分析关键词的搜索量、难度、竞争度
4. 按聚类分组成主题簇
5. 推荐长尾关键词和内容机会
```

这种 **Markdown 驱动的 Agent 工作流**设计，让非技术用户也可以理解 Agent 在做什么——同时它也是 Agent 实际执行的指令。这是 Agent 时代的"文档即代码"模式。

### 排名追踪架构

从 Issue 和 PR 来看，排名追踪（Rank Tracking）是 OpenSEO 最复杂的模块：

- 每个关键词可以独立设置检查间隔（manual/daily/weekly）
- 支持按设备（mobile/desktop）和国家过滤
- 调度器通过 Cloudflare Workers Cron 触发器执行
- 结果存储在 D1 数据库中

## 📐 架构决策与设计哲学

### 重要的设计决策

1. **MCP 优先于 API**：传统工具做 REST API，OpenSEO 做 MCP Server。这意味着 AI Agent 可以直接"理解"和使用 OpenSEO 的数据
2. **DataForSEO 依赖**：不自己采集 SEO 数据，而是依赖 DataForSEO 的聚合 API——好处是数据质量有保障，坏处是 DataForSEO 的延迟和可用性成了瓶颈
3. **Cloudflare Workers 优先**：选择了 Serverless + D1 的组合，放弃了传统 Node.js 服务器。这意味着冷启动可能是个问题，但成本极低
4. **GitHub 作为项目管理工具**：维护者 bensenescu 使用了 GitHub Issues 的标签系统（`status:spec-first`、`status:ready`、`type:enhancement`、`type:ux` 等）进行项目管理，分工明确

### 设计红线

从 Issue 和 README 可以看出：

- **不打算自己做数据采集**：依赖 DataForSEO，不是 Scraping 工具
- **不完全免费**：用户需要自己付 DataForSEO API 费用
- **Docker 版本是单用户**：没有认证，仅供本地使用

## 🌐 全网口碑画像

### 好评共识

- **"Semrush 太贵了，OpenSEO 真香"**：开发者社区普遍认为，对于个人站主和小团队，$200+/月的 SEO 工具太贵，OpenSEO 的 Pay-as-you-go 模式是巨大的价格优势
- **"Agent Skills 设计太聪明了"**：LobeHub 等社区对 OpenSEO 的 Agent Skills 整合特别关注，认为 AI + SEO 的结合很自然
- **"部署超简单"**：Docker Compose 一键部署获得了正面评价

### 差评共识 & 踩坑高发区

- **Cloudflare 部署按钮不好用**：Issue #27 长时间未解决，多个用户报告 Terraform 部署按钮的各种问题（KV 名称重复、无法更新）。维护者 bensenescu 的回应是"建议用 Wrangler CLI 手动部署"
- **功能还不够全面**：相比 Semrush/Ahrefs 的完整功能集，OpenSEO 目前缺少 Site Audit（#9）、Scheduled Report、Local SEO 等功能。部分用户在社区表达了"功能太少"的反馈
- **DataForSEO 的数据延迟**：DataForSEO 的数据不是实时更新的，部分用户发现排名数据有 1-3 天的延迟

### 争议焦点

- **"是不是真的替代 Semrush"**：对于重度 SEO 用户，OpenSEO 的功能集还远远不够。定位上更接近"独立站主够用的轻量工具"而非"企业级 SEO 平台完全替代"
- **DataForSEO 依赖风险**：DataForSEO API 的价格上涨或服务中断会直接影响 OpenSEO 的用户体验

### 社区活跃度

| 指标 | 数值 |
|------|------|
| Stars | 3,337 |
| Forks | 368 |
| Open Issues | 17 |
| 贡献者 | 10+（含 mvanhorn 等活跃贡献者） |
| 维护者 | bensenescu（回复迅速、态度友好） |

## ⚔️ 竞品对比

| 维度 | OpenSEO | Semrush | Ahrefs | SERPWatcher |
|------|--------|--------|--------|-------------|
| **价格** | 免费 + API 费 ($5-50/月) | $200+/月 | $99+/月 | $29+/月 |
| **开源** | ✅ MIT | ❌ | ❌ | ❌ |
| **自托管** | ✅ Docker/Cloudflare | ❌ | ❌ | ❌ |
| **MCP 集成** | ✅ 自建 MCP | ❌ | ❌ | ❌ |
| **AI Skills** | ✅ 7 个内置 | ❌ | ❌ | ❌ |
| **关键词研究** | ✅ | ✅ 完整 | ✅ 完整 | ✅ 基本 |
| **排名追踪** | ✅ | ✅ | ✅ | ✅ 核心功能 |
| **外链分析** | ✅ 基本 | ✅ 完整 | ✅ 完整 | ❌ |
| **网站审计** | ⬜ 开发中 | ✅ | ✅ | ❌ |
| **数据质量** | 依赖 DataForSEO | 自建 | 自建 | 自建 |

### 选择建议

- **开发者 + AI Agent 用户** → **OpenSEO**（最佳 Agent 整合）
- **内容创作者/个人站主（预算有限）** → OpenSEO（价格优势巨大）
- **企业级 SEO 团队** → Semrush/Ahrefs（功能更完整、数据更实时）
- **只看排名追踪** → SERPWatcher（够用且便宜）

## 🎯 核心研判

### 项目优势

1. **AI 原生是最大的差异化**：在其他 SEO 工具还在做 REST API 的时候，OpenSEO 已经用 MCP + Agent Skills 让 AI Agent 可以直接做 SEO 分析。这个差距在未来会越来越大
2. **成本优势无法忽视**：$5-50/月 vs $200+/月，对个人站主和初创团队来说，OpenSEO 几乎是唯一选择
3. **维护者反应积极**：bensenescu 在 Issue 和 PR 中的回复速度和质量都不错

### 项目风险

1. **DataForSEO 依赖风险**：OpenSEO 完全依赖第三方 API，如果 DataForSEO 改变定价/策略，整个项目会受影响
2. **功能覆盖不够**：相比 Ahrefs/Semrush 的完整功能集，OpenSEO 缺少的关键功能（Site Audit、批量报告、Local SEO）还需要较长时间的开发
3. **Cloudflare 依赖**：虽然支持 Docker，但 Cloudflare Workers 是首要部署目标，对于不使用 Cloudflare 的用户来说有摩擦

### 适用场景 & 不适用场景

**适用**：
- 独立开发者和内容创作者的个人网站 SEO
- AI Agent 驱动的自动化内容策略（Claude Code + OpenSEO）
- 预算有限的早期项目
- 需要自托管的隐私敏感场景

**不适用**：
- 需要实时 SEO 数据的大型团队
- 需要完整 Site Audit 功能的企业
- 需要白标批量报告输出的代理商

### 趋势判断

🟢 **稳定上升期**。3.3K star / 4 个月的增长节奏健康，社区贡献活跃。随着 MCP 生态的成熟和 AI Agent 的普及，OpenSEO 的"AI 原生"优势会越来越明显。

## 📂 关键文件路径速查

| 文件 | 作用 |
|------|------|
| `.agents/skills/keyword-research/SKILL.md` | 关键词研究 Agent Skill |
| `.agents/skills/seo-coach/SKILL.md` | SEO 教练 Agent Skill |
| `.agents/skills/competitive-landscape/SKILL.md` | 竞品分析 Agent Skill |
| `compose.yaml` | Docker Compose 部署配置 |
| `Dockerfile.selfhost` | Docker 自托管构建 |
| `docs/SELF_HOSTING_DOCKER.md` | Docker 部署文档 |
| `docs/SELF_HOSTING_CLOUDFLARE.md` | Cloudflare 部署文档 |
| `src/` | 应用核心源码 |
| `drizzle/` | 数据库迁移文件 |
| `e2e/` | Playwright E2E 测试 |
| Hosted 版 | https://openseo.so |
| Discord | https://discord.gg/c9uGs3cFXr |
