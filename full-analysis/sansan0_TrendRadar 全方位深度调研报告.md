sansan0/TrendRadar 全方位深度调研报告调研日期：2026-06-13 | 数据来源：GitHub API + README📦 项目概览属性值仓库sansan0/TrendRadarStars⭐ 59,359Forks24,638语言Python许可证GPL-3.0创建时间2025-04-28最后更新2026-06-08官网sansan0.github.io/TrendRadar一句话定位：AI 驱动的开源舆情监控与热点筛选工具，聚合多平台热点、RSS 订阅，支持 AI 智能分析、翻译和多渠道推送。📖 项目定位与核心功能定位TrendRadar 定位为个人级舆情监控工具，目标是帮助用户告别信息过载，从被动刷信息变为主动获取关注的内容。核心场景包括：投资监控、品牌舆情追踪、行业动态关注、生活资讯获取。核心功能矩阵功能模块子功能说明全网热点聚合11+ 平台知乎、抖音、B站、微博、百度热搜、头条等RSS 订阅自定义 RSS/Atom与热榜统一格式，支持关键词匹配AI 智能分析MCP 协议17 种分析工具，支持自然语言对话式查询AI 筛选自然语言兴趣描述替代传统关键词匹配，AI 自动分类打分AI 翻译多语言翻译支持任意语言，与 AI 分析共享模型配置精准筛选关键词/正则支持普通词、必须词、过滤词、正则表达式多渠道推送10+ 渠道飞书、钉钉、企业微信、Telegram、邮件、ntfy、Bark、Slack、通用 Webhook多模式推送daily/current/incremental当日汇总、当前榜单、增量监控智能调度时间线系统5 种预设模板，支持工作日/周末差异化HTML 报告可视化增强暗色模式、宽屏布局、搜索、快捷键热点算法权重可调排名/频次/热度三因子权重配置🏗️ 架构分析核心架构TrendRadar/├── config/                   # 配置文件目录│   ├── config.yaml          # 主配置（推送、平台、AI等）│   ├── frequency_words.txt  # 关键词配置│   ├── timeline.yaml        # 时间线调度配置│   ├── ai_analysis_prompt.txt   # AI 分析提示词│   ├── ai_interests.txt     # AI 兴趣描述│   └── custom/              # 用户自定义配置├── mcp_server/              # MCP AI 分析服务├── output/                  # 数据输出目录├── docker/                  # Docker 部署配置├── main.py                  # 主入口└── manage.py                # 管理命令数据流平台API → 爬虫抓取 → 关键词匹配 → 热度计算 → 内容聚合    ↓  SQLite 存储    ↓  推送生成 → 多渠道发送（飞书/钉钉/邮件等）    ↓  HTML 报告生成    ↓  AI 分析（可选）存储架构本地模式：SQLite 数据库（output/ 目录）远程模式：S3 兼容协议（Cloudflare R2/阿里云OSS/腾讯COS）自动切换：根据运行环境智能选择存储方式📈 社区口碑与影响力增长曲线2025-04-28：项目创建2025-06-09：100 Stars（42天）2025-06-18：200 Stars（9天）2025-10-31：v3.0.0 重大更新2026-01：v5.0.0 AI 分析功能2026-06-08：59,359 Stars（约14个月）积极评价功能实用：精准匹配用户需求，解决信息过载痛点部署简单：GitHub Actions 零成本部署AI 集成出色：MCP 协议支持实现自然语言查询持续迭代：从 v1.0 到 v6.9 的快速演进文档详尽：中文 README 超过 5000 行，教程完整局限性数据依赖：依赖第三方 API（newsnow），存在服务不稳定

### 风险

GitHub Actions 限制：需要签到机制维持运行AI 依赖付费：AI 分析功能需要 API Key 和付费仅国内平台：海外平台覆盖不足🔄 竞品对比特性TrendRadarnewsnow今日热榜即时热榜开源✅ GPL-3.0✅ MIT❌❌Stars59.3K5K+N/AN/AAI 分析✅ MCP 协议❌❌❌推送渠道10+❌有限有限关键词筛选✅ 强大❌✅ 基础✅ 基础RSS 支持✅❌❌❌Docker 部署✅❌❌❌GitHub Actions✅✅❌❌MCP 协议✅❌❌❌多模式推送✅ 3种❌❌❌AI 翻译✅❌❌❌

## 🎯 核心研判

项目价值解决真实痛点：信息过载是普遍问题，TrendRadar 提供精准的信息筛选方案AI 深度集成：从分析到筛选到翻译，AI 贯穿全流程部署零门槛：GitHub Actions 实现零成本部署，Docker 支持高级用户推送全覆盖：10+ 推送渠道覆盖所有主流即时通讯工具竞争力分析速度惊人：14 个月从 0 到 59.3K Stars，增速极快差异化定位：个人级舆情监控 + AI 分析 + 多渠道推送的组合独特社区活跃：Forks 24.6K，远超 Stars 比例，说明社区参与度高版本迭代快：从 v1.0 到 v6.9，功能密度极高潜在

### 风险

数据源依赖：核心数据来自第三方 API，存在服务中断

### 风险

GitHub Actions 政策：签到机制依赖 GitHub 免费额度，政策变化可能影响AI 成本：AI 分析功能需要 API Key，用户需要额外付费竞争加剧：类似开源项目可能出现（如 open-scouts）使用建议个人用户：GitHub Actions 部署 + incremental 模式 + AI 筛选企业用户：Docker 部署 + 自建 ntfy + 邮件推送开发者：利用 MCP 协议进行二次开发和集成🔑 关键文件路径路径说明main.py主入口程序manage.pyDocker 管理命令config/config.yaml主配置文件config/frequency_words.txt关键词配置config/timeline.yaml时间线调度配置config/ai_analysis_prompt.txtAI 分析提示词mcp_server/server.pyMCP AI 分析服务docker/docker-compose.ymlDocker 编排配置.github/workflows/crawler.ymlGitHub Actions 工作流📌 总结TrendRadar 是近年来增长最快的国产开源项目之一（14 个月 59.3K Stars），以"个人级 AI 舆情监控"的精准定位，结合多平台热点聚合、关键词/正则筛选、AI 智能分析/翻译/筛选、10+ 渠道推送等全链路功能，构建了完整的信息过滤到推送的闭环。其核心

### 优势

在于部署零门槛（GitHub Actions）、功能密度高、AI 集成深度（MCP 协议）。

### 风险

在于数据源依赖第三方、GitHub Actions 政策不确定性以及 AI 功能的额外成本。
