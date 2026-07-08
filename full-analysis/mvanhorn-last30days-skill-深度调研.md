# 🔬 mvanhorn/last30days-skill — 全方位深度调研

> **调研日期**: 2026-07-09 | **数据来源**: GitHub API + README + 源码 + 中文社区评测 + 英文社区讨论 | **总评**: ⭐ 50,612 | 🍴 4,224

## 📌 一句话定位

**Agent 驱动的跨平台社交搜索引擎**——输入主题，AI 代理并行搜索 Reddit、X、YouTube、HN、Polymarket、TikTok 等 10+ 平台，以真实用户互动数据（upvotes、赔率、评论数）而非 SEO 权重来排序，合成为一份带来源的简报。

> 核心判断：这不是另一个"AI 搜索"——它不做网页索引，而是做**社交信号聚合**。50K ⭐ 意味着市场对"绕过封闭平台信息孤岛"的需求远大于供给。

## ⭐ 项目亮点

1. **社交信号驱动排名** — 不是 AI 估算的"相关性"，而是真实 Reddit upvotes、Polymarket 赔率、YouTube 观看量。这完全改变了"什么是重要信息"的定义
2. **10+ 封闭平台覆盖** — Reddit 评论、X 推文、TikTok 视频、Instagram Reels、Bluesky、Threads——这些是 Google 搜不到的内容
3. **渐进式架构（Progressive Disclosure）** — 先元数据、后工具定义、再执行，避免一次加载爆掉 Agent 上下文。这已成为 Agent Skills 生态的参考范式
4. **0 配置可用** — Reddit、HN、Polymarket、GitHub 无需任何 API Key 就能跑，大幅降低试用门槛
5. **Lyft 联合创始人出品** — Matt Van Horn 的背书不仅带来可信度，还意味着充足的工程资源和社区运营投入

## 🏗️ 项目架构全景

### 目录结构

```
last30days-skill/
├── skills/last30days/SKILL.md    # 核心技能文件（193KB，入口文件）
│   └── scripts/                   # Python 执行引擎
│       └── lib/                   # 各平台后端实现（backends.py 调度）
├── mcp/                           # MCP 服务实现（Go 语言）
├── tests/                         # 1000+ 测试用例
├── docs/                          # 架构决策文档 + 解决方案记录
├── AGENTS.md                      # Agent 治理规则（10KB）
├── CONCEPTS.md                    # 精确定义 Skill/Engine/Harness 术语
└── CONFIGURATION.md               # 完整配置指南（40KB）
```

### 核心架构：三层引擎

```
User: "/last30days topic"
        │
        ▼
┌─────────────────────────────────────┐
│  Layer 1: Planner（规划层）          │
│  - 实体解析（entity_extract.py）    │
│  - 查询扩展（query.py）             │
│  - 平台发现（categories.py）        │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  Layer 2: Fanout（并行搜索层）       │
│  - ThreadPoolExecutor 并发          │
│  - 后端适配器（backends.py）        │
│    ├── Reddit: RSS + keyless + API  │
│    ├── X: Bird (free) → xAI (paid) │
│    ├── YouTube: yt-dlp + transcript │
│    ├── Polymarket: API → real odds  │
│    └── TikTok/IG: ScrapeCreators    │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  Layer 3: Fusion（合成层）           │
│  - 归一化（normalize.py）           │
│  - 聚类去重（cluster.py）           │
│  - 重排序（rerank.py by engagement)│
│  - 富化（reddit_enrich.py 拿评论）  │
│  - 简报渲染（render.py → HTML）    │
└─────────────────────────────────────┘
```

### 设计哲学

**来源独立（Source Agnostic）**：每种数据源被抽象为统一的 `Backend` 接口，新增平台只需实现 `search() + enrich()` 两个方法。这是该架构能快速从 4 个平台扩展到 10+ 的核心原因。

**退化链（Degradation Chain）**：每个平台配有多个备选获取策略。以 Reddit 为例：RSS → keyless → public API → authenticated API。任一环节失败自动降级，而不是抛错退出。这是生产环境可靠性远超同类工具的关键。

## 💡 应用场景与启发

### 典型使用场景

| 场景 | 用法 | 传统替代方案 |
|------|------|-------------|
| 会议前了解一个人 | `/last30days Peter Steinberger` | 刷 LinkedIn/Twitter 30 分钟 |
| 竞品动态监控 | `/last30days company --competitors` | 手动跟踪多个 RSS |
| 投资决策参考 | `/last30days AI chip --hiring-signals` | 读季度报告 |
| 热点事件追踪 | `/last30days 总统竞选` | 刷新闻网站 |
| 旅行功课 | `/last30days Disney World` | 搜攻略文章 |

### 对同类项目的启发

1. **"封闭平台数据提取"是 Agent 搜索最大的差异化空间**：Google 搜不到 Reddit 内部讨论、Twitter 内部趋势、TikTok 内部标签。能够绕过这些"信息孤岛"的 Agent 工具具有无可替代的价值
2. **真实参与度远比 AI 估算可靠**：用 Polymarket 赔率（真金白银）和 Reddit upvotes（真实用户行为）来排序，比 OpenAI 的"相关性评分"更接近真实世界的关注度
3. **渐进式披露是 Agent Skill 的架构答案**：Agent 工具面临的最大问题是上下文窗口有限。last30days 的 3 层加载策略（元数据→定义→执行）值得所有 Agent Skill 参考

## 🧠 核心源码解读

### 1. Planner：实体解析引擎（`planner.py` 32KB）

这是最容易被忽略但最精妙的部分。并非简单拼接搜索词，而是**智能解析用户意图**：

```python
# 核心逻辑：从用户输入中提取结构化实体
def plan(self, topic: str) -> Plan:
    # Step 1: 实体粗提取
    entities = self._extract_entities(topic)  # 识别可能的人/公司/产品
    
    # Step 2: 实体解析（resolve）
    resolved = self._resolve_entities(entities)
    # 如果 topic="OpenClaw" → 解析出:
    #   - GitHub: openclaw/openclaw
    #   - Reddit: r/openclaw
    #   - X: @openclaw
    #   - 创始人: @binaryberry
    
    # Step 3: 查询规划
    queries = []
    for entity in resolved:
        for platform in entity.get_platforms():
            queries.append(Query(
                entity=entity,
                platform=platform,
                query=self._build_search_query(entity, platform)
            ))
    return Plan(queries=queries)
```

这种实体预解析机制确保了"OpenClaw vs Paperclip"这样的比较查询能被拆解为两个实体的独立平台搜索，而不是当做一个模糊的关键词。

### 2. Fanout：并发调度引擎（`fanout.py` 3KB + `backends.py` 22KB）

Thin orchestrator 的典范——文件极小但调度逻辑极其稳健：

```python
def fanout_search(plan: Plan) -> SearchResults:
    # 关键策略：每个查询独立线程，互不阻塞
    with ThreadPoolExecutor(max_workers=20) as exe:
        futures = {
            exe.submit(backend.search, query): query
            for query in plan.queries
        }
        for future in as_completed(futures):
            query = futures[future]
            try:
                result = future.result(timeout=30)
            except Exception as e:
                # 关键设计：错误不抛出，只记录
                results.append(ErrorResult(query, e))
            else:
                results.append(result)
    return results
```

独立线程 + 异常捕获为 `ErrorResult`（而非抛出）= 一个平台的超时不会拖垮整体搜索。这在多 API 依赖场景下是生死攸关的设计决策。

### 3. Fusion：数据富化引擎（`reddit_enrich.py` 9KB）

从"搜索到结果"到"搜索到有价值的结果"的核心差异：

```python
def enrich_reddit_post(post_id: str) -> Enrichment:
    # 调用 Reddit 公共 JSON API 拿真实数据
    data = requests.get(
        f"https://www.reddit.com/comments/{post_id}/.json",
        headers={"User-Agent": "mozilla/5.0"}
    ).json()
    return Enrichment(
        upvotes=data[0]['data']['children'][0]['data']['ups'],
        upvote_ratio=data[0]['data']['children'][0]['data']['upvote_ratio'],
        num_comments=data[1]['data']['children'][0]['data']['num_comments'],
        top_comments=[  # Top 10 评论
            c['data']['body']
            for c in data[1]['data']['children'][:10]
            if c['kind'] == 't1'
        ]
    )
```

"富化"（Enrichment）是整个项目的杀手锏——普通 AI 搜索给摘要，它给的是**真实评论原文 + upvote 数据**。用户可以自己判断哪些评论有价值，而不是听 AI 撮合。

## 🌐 全网口碑画像

### 好评共识

- **"选题效率提升 10 倍"** — 多个中文内容创作者反馈，传统需数小时刷屏的工作，`/last30days` 30 秒搞定（来源：掘金文章、今日头条评测）
- **"数据准确性远超 AI 搜索"** — 评测指出其"评分机制确保 Reddit 高赞评论不会因 SEO 优化不足被埋没"
- **"Google 搜不到的东西它能搜"** — 评论指出跨平台数据聚合是传统和 AI 搜索都无法提供的能力
- **"标杆级文档质量"** — CONCEPTS.md 和 CONFIGURATION.md 被社区誉为 Agent Skills 生态的"最佳实践"
- **"有 1000+ 测试用例的开源 Agent Skill"** — 来自 Hacker News 的技术讨论（来源：HN 相关主题）

### 差评共识 & 踩坑高发区

| 痛点 | 具体表现 | 来源 |
|------|---------|------|
| **API Key 配置复杂** | 需要配置 OpenAI、xAI、YouTube 等多个 Key | GitHub Issues |
| **付费 API 依赖** | X/Twitter 的 xAI API 需付费，TikTok/Instagram 需 ScrapeCreators | 社区反馈 |
| **YouTube 转录浪费** | Issue #531：转录预算耗在非目标窗口视频上 | Open Issue |
| **无订阅模式** | Issue #532：只能手动执行，不能定时推送 | Open Issue |
| **配置门槛高** | 配置向导（setup wizard）体验仍需改进 | CONFIGURATION.md 评论区 |

### 争议焦点

- **"Skil 还是 App 的边界在哪里"**：部分用户认为它太大太重（193KB 的 SKILL.md），已经超出了"Skill"的范畴，更像是一个独立应用
- **"数据源合法性"**：使用无头抓取 Reddit/X/TikTok 是否违反 ToS？项目本身未提供法律声明

## ⚔️ 竞品对比

| 维度 | last30days-skill | Agent-Reach | Perplexity | OpenAI Deep Research |
|------|-------------------|-------------|------------|---------------------|
| **定位** | Agent 跨平台研究 | CLI 调研工具 | AI 搜索引擎 | AI 深度研究 |
| **平台覆盖** | 10+ 个（含社交平台） | 7 个（含 B站/小红书） | 通用网页 | 通用网页 |
| **数据准确性** | 真实 upvotes/赔率 | 无公开保障 | 混合来源 | AI 生成摘要 |
| **安装方式** | npx skills / 插件市场 | pip install | Web | Web |
| **费用** | 自带 API Key 即可 | 0 API 费用 | 订阅制 | 使用额度 |
| **差异化** | Polymarket 赔率 + 跨平台 | 国内平台 | 通用搜索 | 深度推理 |

**选择建议**：
- **面向英文互联网的内容创作者/投资人** → last30days-skill（独家覆盖 Reddit/X/Polymarket）
- **面向国内平台的内容创作者** → Agent-Reach（覆盖 B站/小红书）
- **需要通用问答** → Perplexity（零配置、低门槛）

## 🎯 核心研判

### 不可替代的价值

last30days 的真正护城河不是代码（MIT 开源），而是**它与 10+ 个封闭平台建立的数据管道**。每个平台都需要独特的认证、抓取、解析策略——这种"反向集成"的成本在新进入者复现前只会越来越高。

### 风险

1. **API 依赖风险**：X/xAI 的 API 政策变更、TikTok 反爬升级、Reddit API 收费——任何一个平台的反向工程失败都会削弱价值
2. **Agent 格式依赖**：Agent Skills 生态尚在发展初期，如果 Claude/Cursor 改变 Skill 加载方式，rewrite 成本不小
3. **1000+ 测试的维护负担**：80 个 Open Issue + 4.2K Forks 表明社区贡献活跃但核心维护者压力大
4. **配置复杂度**：多 API Key 的配置体验对非技术用户不友好

### 趋势判断

**高速成长期**。50K ⭐ 的增速（2026年1月创建，7月即达 50K）表明市场对"社交信号搜索"有大量未满足需求。核心风险在平台 API 政策变化，而非竞争。

## 📂 关键文件路径速查

| 文件 | 大小 | 说明 |
|------|------|------|
| `skills/last30days/SKILL.md` | 193KB | 核心技能定义（入口） |
| `skills/last30days/scripts/lib/planner.py` | 32KB | 实体解析与查询规划 |
| `skills/last30days/scripts/lib/backends.py` | 22KB | 多后端适配器调度 |
| `skills/last30days/scripts/lib/reddit_enrich.py` | 9KB | 数据富化（核心差异化） |
| `skills/last30days/scripts/lib/pipeline.py` | 76KB | 全流程编排 |
| `skills/last30days/scripts/lib/render.py` | 89KB | 简报 HTML 渲染 |
| `CONFIGURATION.md` | 40KB | 完整配置指南 |
| `CONCEPTS.md` | 3.6KB | 术语精确定义 |
| `AGENTS.md` | 10KB | Agent 治理规则 |
