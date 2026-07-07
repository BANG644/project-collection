# 🔬 sansan0/TrendRadar — 全方位深度调研

> **调研时间**: 2026-07-08 | **Stars**: 60,330 ⭐ | **Forks**: 24,758
> **语言**: Python | **许可**: GPL-3.0 | **版本**: v6.10.0
> **仓库**: https://github.com/sansan0/TrendRadar

---

## 📌 一句话定位

AI 驱动的开源舆情监控与热点追踪工具——聚合 11+ 平台热搜、RSS 订阅源，支持 AI 智能分析/翻译/筛选，10+ 渠道推送，最快 30 秒 Docker 部署。

> 60K ⭐ 在 14 个月内从 0 到 6 万星，是 2025-2026 年增长最快的国产开源项目之一。

---

## ⭐ 项目亮点

1. **增长神话** — 14 个月从 0 到 60K+ Stars，GitHub 2025-2026 年增速最快的国产开源舆情工具
2. **部署即用** — 最快 30 秒 Docker 部署，也支持 GitHub Actions 零成本方案、Cloudflare Pages 等 4 种部署方式
3. **AI 全链路集成** — 支持 MCP 协议实现自然语言对话分析，AI 智能筛选（v6.5）、AI 翻译（v5.2）、AI 分析简报（v5.0）逐步加码
4. **推送全覆盖** — 微信/企业微信/飞书/钉钉/Telegram/邮件/ntfy/Bark/Slack/通用 Webhook 等 10+ 渠道
5. **极致配置灵活性** — 支持关键词/正则/必须词/过滤词四级筛选体系，三种推送模式（daily/current/incremental），时间线系统

---

## 🏗️ 项目架构全景

### 目录骨架

```
TrendRadar/
├── main.py                        # 主入口
├── manage.py                      # Docker 管理命令
├── config/
│   ├── config.yaml                # 主配置（推送/平台/AI）
│   ├── frequency_words.txt        # 关键词配置
│   ├── timeline.yaml              # 时间线调度
│   ├── ai_analysis_prompt.txt     # AI 分析提示词
│   └── ai_interests.txt           # AI 兴趣描述（自然语言）
├── mcp_server/                    # MCP AI 分析服务
├── docker/                        # Docker 编排
├── output/                        # 数据输出 + SQLite
└── .github/workflows/             # GitHub Actions 自动化
```

### 设计哲学：轻量 + 易部署

TrendRadar 不追求大而全的后端架构，而是**以配置文件为中心**的设计。核心是 config.yaml——它同时控制数据源选择、推送渠道、AI 接入、时间调度等。这意味着：用户不需要写一行代码就能完成全功能配置。

### 数据流

```
平台API → newsnow 抓取 → SQLite 存储 → 关键词/正则匹配
    ↓
热度计算 + AI 分析（可选）
    ↓
多渠道推送 + HTML 报告生成
```

---

## 💡 应用场景与启发

### 典型使用场景

| 角色 | 场景 | 部署方式 |
|------|------|----------|
| 个人投资者 | 监控金融/财经热点（财联社、华尔街见闻） | GitHub Actions（零成本） |
| 品牌公关 | 追踪品牌舆论、负面监控 | Docker VPS |
| 内容创作者 | 选题发现、热点趋势捕捉 | GitHub Actions |
| 信息安全团队 | FreeBuf、安全漏洞情报 | Docker + ntfy |
| AI 开发者 | 利用 MCP 协议做二次开发和集成 | Docker + 自定义 |

### 可借鉴的解决方案模式

1. **配置驱动设计** — 将行为全部暴露到 YAML 配置，用户改配置不改代码。降低了门槛但牺牲了灵活性——高级用户需要的数据源新增（如小红书、Twitter）必须改代码
2. **MCP 协议接入** — 将 AI 分析能力抽象为 MCP Server，与项目主体解耦。这个设计可以让 AI Agent 直接接入 TrendRadar 的数据管道做高级分析
3. **三条推送链的设计** — daily（当日汇总）面向快消类用户、current（当前榜单）面向实时监控、incremental（增量监控）面向关键词跟踪。三种模式覆盖了从"刷手机看看"到"敏感词实时告警"的全光谱需求

### 同类需求的可参考思路

如果你要做一个信息聚合推送系统，TrendRadar 的架构值得参考的核心思路是：**数据源层 (newsnow) → 筛选层 (关键词/正则) → AI 增强层 (MCP) → 推送层 (多通道)**。每层解耦意味着你可以换掉任意一层而不影响其他层。

---

## 🧠 核心源码解读

### 配置加载（核心抽象层）

TrendRadar 的核心设计决策在于 config.yaml 的配置解析。它采用 YAML + 条件模板（!template）语法，支持环境变量注入和条件渲染：

```yaml
# 推送渠道配置示例
push:
  multi:
    - name: "wechat"
      enabled: "{{ env.WECHAT_ENABLED | default('false') }}"
      # 仅在 enabled 为 true 时递归解析
      sckey: "{{ env.WECHAT_SCKEY }}"
    - name: "dingtalk"
      enabled: "{{ env.DINGTALK_ENABLED | default('false') }}"
      webhook_url: "{{ env.DINGTALK_WEBHOOK }}"
```

这种设计的精妙之处在于：**所有敏感信息（API Key、Webhook URL）通过环境变量注入，不硬编码在配置文件中**。同时 `enabled` 开关允许用户通过 `.env` 文件选择性地开启/关闭推送渠道，无需修改 YAML 结构。

### MCP Server（最值得借鉴的模块）

TrendRadar 的 MCP 服务让 AI 客户端可以直接对话式查询舆情数据。以下是其核心架构：

```python
# mcp_server/server.py 骨架
@mcp.tool()
async def search_news(
    query: str,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    sources: Optional[List[str]] = None
) -> List[Dict]:
    """搜索新闻热点，支持按时间范围和来源过滤"""
    data = load_trendradar_data()
    results = filter_by_query(data, query)
    if date_from:
        results = filter_by_date(results, date_from, date_to)
    if sources:
        results = filter_by_source(results, sources)
    return format_results(results)

@mcp.tool()
async def analyze_trend(
    topic: str,
    analysis_type: Literal["sentiment", "summary", "forecast"] = "summary"
) -> str:
    """对指定话题做情感分析/摘要/趋势预测"""
    news = search_news(topic)
    prompt = build_analysis_prompt(topic, news, analysis_type)
    return call_llm(prompt)
```

**为什么这样做？** 将 MCP Server 独立为 Docker 镜像（`trendradar-mcp`）意味着：即使用户不想运行完整的 TrendRadar 实例，也可以单独启动 MCP 服务来增强已有的 AI 客户端（如 Claude、OpenClaw）。这是"关注点分离"的优秀实践。

---

## 🌐 全网口碑画像

### 好评共识

- **"告别无效刷屏"** — 知乎用户评价指出项目"精准匹配需求，解决信息过载痛点"，30 秒部署即可运行（来源：知乎 2026-02 评测）
- **"功能密度极高"** — 从 v1.0 到 v6.9 快速演进，AI 筛选/翻译/分析等功能逐步加入，云+端+本地全场景覆盖（来源：腾讯云社区 2026-03 评测）
- **"推送渠道最全"** — 覆盖微信/飞书/钉钉/Telegram/邮件等主流渠道，对比同类项目是最全面的（来源：CSDN 技术博客）
- **"Docker 部署极其简单"** — 适合不同技术水平的用户，GitHub Actions 实现零成本部署是亮点（来源：AI产品库 2026-06 收录）
- **"MCP 协议支持优秀"** — 用户通过自然语言即可进行数据查询和分析，降低了使用门槛（来源：腾讯云社区评测）

### 差评共识 & 踩坑高发区

- **海外平台覆盖不足** — Issue #95（200+ 条评论）是最热的未关闭 Issue，用户反复要求增加 Twitter/X、路透社、彭博社、小红书等平台。项目依赖 newsnow 的数据源，新增平台需要先在 newsnow 中贡献代码
- **GitHub Actions 局限性** — 免费额度有限制，需要"签到"机制维持运行。长期运行需要迁移到 Docker 或 VPS
- **AI 分析需要额外付费** — AI 分析功能需要 API Key，对普通用户是额外成本（Issue #1139 建议添加更多免费 AI 选项）
- **Windows Docker 部署陷阱** — Issue #901 指出 `127.0.0.1` 导致局域网不可访问，需要手动改为 `0.0.0.0`
- **MCP 版本兼容性** — Issue #1049 指出与 OpenClaw 的协议版本冲突

### 维护者风格

sansan0（单一维护者）回应快速，对配置问题直接给出解决方案（如 Issue #893 点赞 78 次的 Docker 部署回复），但 Issue 数量庞大（1182 个 Open），长期维护压力可见一斑。

---

## ⚔️ 竞品对比

| 维度 | TrendRadar | newsnow | 今日热榜 | 即时热榜 |
|------|-----------|---------|---------|---------|
| ⭐ Stars | **60.3K** | 5K+ | N/A | N/A |
| 开源 | ✅ GPL-3.0 | ✅ MIT | ❌ | ❌ |
| AI 分析 | ✅ MCP 协议 + 3 大功能 | ❌ | ❌ | ❌ |
| 推送渠道 | **10+** | ❌（仅项目本身） | 有限 | 有限 |
| 关键词筛选 | ✅ 四级（普通/必须/过滤/正则） | ❌ | ✅ 基础 | ✅ 基础 |
| RSS 支持 | ✅ | ❌ | ❌ | ❌ |
| Docker 部署 | ✅ | ❌ | ❌ | ❌ |
| GitHub Actions | ✅ 零成本 | ❌ | ❌ | ❌ |
| MCP 协议 | ✅ | ❌ | ❌ | ❌ |
| 三模式推送 | ✅ daily/current/incremental | ❌ | ❌ | ❌ |
| AI 翻译 | ✅ | ❌ | ❌ | ❌ |
| 数据本地存储 | ✅ SQLite | ✅ | ❌ | ❌ |

### 选择建议

- **TrendRadar** — 需要 AI 分析 + 多平台推送 + 自部署的完整舆情监控方案（推荐）
- **newsnow** — 只需要原始热榜数据做二次开发的开发者
- **今日热榜 / 即时热榜** — 不想自己部署，只想要一个网页看热榜的普通用户

---

## 🎯 核心研判

### 不可替代的价值

1. **唯一开源的全链路舆情平台** — AI 分析 + 多通道推送 + 自部署 + MCP 协议的组合在开源领域没有直接竞品
2. **配置驱动设计降低了使用门槛** — 非技术用户也能通过 config.yaml 完成全功能配置
3. **功能密度极高** — 单一维护者在 14 个月内从 v1.0 迭代到 v6.10，功能迭代速度惊人

### 主要风险

1. **单一维护者依赖** — 1182 个 Open Issue 显示出明显的维护压力，Bug 修复和 Feature Request 的积压可能影响长期可持续性
2. **数据源集中风险** — 核心热榜数据依赖 newsnow 的 API，如果 newsnow 停止服务或变更策略，TrendRadar 的核心功能将受影响
3. **AI 功能的额外成本** — AI 筛选/翻译/分析需要用户自备 API Key，对非技术用户是额外门槛
4. **海外数据源缺失** — 无法监控 Twitter/X、Reddit 等海外平台，限制了全球化使用场景

### 适用场景 ✅

- 需要中文互联网舆情监控的个人/团队
- 想要零成本使用 GitHub Actions 部署的轻量方案
- 有 AI 开发能力，希望利用 MCP 协议做二次集成的开发者

### 不适用场景 ❌

- 需要监控海外社媒平台（Twitter、Reddit 等）
- 不想自行配置和部署，要求开箱即用的非技术用户
- 对 AI 功能有强需求但无 API Key

### 趋势判断

**高速上升期**。60K ⭐ 的增速曲线说明市场需求旺盛。但项目正处于"功能密度 vs 维护质量"的十字路口——继续堆功能可能加剧 Issue 积压，专注于打磨稳定性可能是更明智的选择。

---

## 📂 关键文件路径速查

| 文件 | 功能说明 |
|------|---------|
| `main.py` | 主入口程序 |
| `manage.py` | Docker 管理命令 |
| `config/config.yaml` | 核心配置文件（推送/平台/AI） |
| `config/frequency_words.txt` | 关键词/正则配置 |
| `config/timeline.yaml` | 时间线调度配置 |
| `config/ai_analysis_prompt.txt` | AI 分析提示词模板 |
| `mcp_server/server.py` | MCP AI 分析服务 |
| `docker/docker-compose.yml` | Docker 编排配置 |
| `.github/workflows/crawler.yml` | GitHub Actions 工作流 |
| `output/` | SQLite 数据 + HTML 报告输出 |
