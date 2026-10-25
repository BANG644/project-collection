# Claude SEO 深度调研

> 调研时间：2026-10-26 ｜ 抓取自 GitHub API + 第三方评测（2026-08~10）｜ 报告编号：#538

## 一、项目定位（一句话）

**Claude SEO 是一个免费的 Claude Code SEO 审计插件（26 子技能 + 19 子代理），把整站技术 SEO / 内容 / Schema / GEO（AI 搜索引述优化）/ 本地 / 电商 / 国际 SEO 审计，变成可在 Claude Code 内并行跑、带「可证伪」结论的 agent 工作流。**

## 二、项目亮点（差异化）

- 🤖 **26 子技能 + 19 子代理并行**：全站审计最多爬 500 页，按领域委托给专项代理（technical/content/schema/sitemap/performance/visual/geo/agentic）并发执行。
- 🌐 **覆盖面极广**：技术 SEO、Core Web Vitals、E-E-A-T、Schema.org、GEO/AEO（让 ChatGPT/Perplexity/Gemini/Claude 引述你的站点）、本地 SEO、电商、hreflang、sitemap、Google APIs（GSC/GA4/PageSpeed/CrUX）、backlinks。
- ✅ **每条发现带「可证伪」标准**：每条建议附「how will I know if this failed?」，把审计变成可验证的行动计划，而非分数。
- 🔌 **9 个可选数据/MCP 扩展**：DataForSEO / Ahrefs / Firecrawl / Semrush / SE Ranking / Profound / Bing Webmaster / IndexNow 等接入实时数据。
- 🛡️ **硬化安全 fetch**：SSRF / DNS-rebinding 安全抓取器 + SPA-aware 无头渲染（render_page.py）。

## 三、核心架构

插件以声明式 `plugin.json` 为中心，运行时由 Python CLI（`scripts/claude-seo`）承担真实抓取与评分：

```text
.claude-plugin/plugin.json     # 声明 sub-skills / sub-agents / hooks
skills/                       # 26 个子技能目录
  seo-audit/                  #   编排器：全站审计入口
  seo-technical/ seo-content/ seo-schema/ seo-geo/ seo-ecommerce/ seo-hreflang/ ...
agents/                       # 19 个专家代理 .md
  seo-agentic.md seo-backlinks.md seo-cluster.md seo-performance.md ...
scripts/claude-seo            # Python CLI：render_page.py / crawl / score
AGENTS.md  CLAUDE.md          # 工程规约
```

`plugin.json`（v2.5.0）keywords 已涵盖 technical-seo / geo / ai-citation-optimization / ssrf-safe-fetchers / headless-rendering 等，印证其能力边界。

## 四、应用场景与启发

- **周常审计取代季审**：技术 SEO 顾问、代理公司、in-house 增长团队用它在 Claude Code 内把「跑 crawl → 导 CSV → 人工排序 → 写报告」压缩为一条 `/seo audit <url>`。
- **给同类需求的解法启发**：
  1. **「审计即 agent 编排」范式**：用 orchestrator 把宽领域任务拆给专项子代理，是「把专家方法论工程化」的清晰样板——任何垂直领域审计（安全/可访问性/合规）都可直接套用。
  2. **「可证伪」是 AI 交付物的质量闸门**：要求每条结论自带验证标准，是避免 agent 输出「看起来对」却不可信的关键设计，值得所有 AI 报告类工具借鉴。
  3. **SPA-aware 渲染 + 硬化 fetch** 说明：做网页感知类 agent，必须处理 JS 渲染与 SSRF，否则结论噪声很大。

## 五、源码深度解读（关键模块）

`skills/seo-audit/SKILL.md` 的真实流程：

```text
1. render_page.py <url> --mode auto --json   # 抓 raw/rendered HTML + 文本 + SPA 状态
2. detect business type                       # 据首页信号识别业务类型
3. crawl internal links ≤ 500 pages, respect robots.txt
4. delegate to subagents (inline or parallel):
     seo-technical / seo-content / seo-schema / seo-sitemap
     seo-performance / seo-visual / seo-geo / seo-agentic
5. return scored, prioritized report
```

- `.claude-plugin/plugin.json`：`version 2.5.0`，声明 22 核心 + 1 orchestrator + 1 framework + 2 extension mirror 子技能。
- `scripts/claude-seo run render_page.py`：SPA 感知渲染是整条流水线的数据基础，必须用 Playwright Chromium。

## 六、社区口碑

**数据**：本调研抓取 20,607⭐（2026-10-26）；第三方 10-19 为 19,292⭐、9 月 17,484⭐、8 月 12.7k⭐——**增长迅猛，是 2026 年最热的 Claude Code 插件之一**，Hacker News / Reddit 有高热讨论。

- ✅ **优势**：广度第一、本地控制、并行、可证伪、MIT 免费、报告可生成 PDF/Excel。
- ⚠️ **作者为个人**（AgriciDaniel），贡献者仅 12 人左右——治理集中度风险。
- ⚠️ **推广 footer 争议**：主编排技能含「Community Footer」指令，会在交付物后追加作者 AI Marketing Hub 社区推广链接；**用于客户交付前需自行删除/修改该指令**。
- ⚠️ **安全与使用注意**：安装脚本须先审查（Windows 官方建议 clone 后 inspect 再跑）；大审计 token 消耗高；需自备 Google API 凭证；无独立托管 dashboard；不能替代 Ahrefs/Semrush 的专有数据库。

## 七、竞品对比

| 项目 | 定位 | 关键差异 |
|------|------|---------|
| **Claude SEO** | Claude Code 插件 | 子技能/代理最多、可证伪、免费 MIT |
| InfraNodus SEO | Claude 技能 + MCP | 文本网络拓扑聚类，强于主题权威/LLMO |
| Claude Blog/Banana | 伴生技能 | 依 SEO 发现写博客/生图，非审计 |
| Screaming Frog | 桌面爬虫 | 深爬数据强，但无 agent 化计划 |
| Ahrefs / Semrush | 托管 SaaS | 专有关键词/反链库，非开源可自托管 |

## 八、核心研判

- **适合谁**：已深度使用 Claude Code 的技术 SEO 顾问、代理公司、in-house SEO lead——把季度深审变成周常、可复核的 agent 流程。
- **不适合谁**：想要开箱即用仪表盘、非技术用户、或要求「无人工即信任」的团队。
- **落地建议**：先在一两个站点试跑，把最高优先级问题与 Search Console/浏览器实测交叉验证；**务必审阅并移除推广 footer、审查安装脚本、控制 token 成本**。它是「SEO 从静态 dashboard 走向 agent 驱动」最具代表性的开源样本，价值取决于你接的数据质量与复核深度，而非星标数。

## 九、关键文件路径速查

```text
.claude-plugin/plugin.json        # 插件声明（版本/子技能/代理）
skills/seo-audit/SKILL.md         # 全站审计编排器流程
skills/<seo-*>                    # 26 个子技能
agents/<seo-*.md>                 # 19 个专家代理
scripts/claude-seo                # Python CLI（render/crawl/score）
AGENTS.md  CLAUDE.md              # 工程规约
```
