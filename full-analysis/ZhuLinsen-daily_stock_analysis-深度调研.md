# ZhuLinsen/daily_stock_analysis — LLM 驱动的多市场股票智能分析系统深度调研

## 项目全景

- **仓库**: [ZhuLinsen/daily_stock_analysis](https://github.com/ZhuLinsen/daily_stock_analysis)
- **Stars**: ~18,500⭐ (Trending)
- **语言**: Python
- **许可**: MIT
- **核心定位**: 基于 AI 大模型的 A股/港股/美股/日股/韩股自选股智能分析系统，每日自动分析并推送「决策仪表盘」到多端

## 核心架构

### 技术栈
| 层 | 技术 |
|---|------|
| 语言 | Python |
| Web | FastAPI |
| 自动化 | GitHub Actions |
| 容器化 | Docker |
| 桌面 | 本地打包 (Electron?) |
| 数据库 | 自选股配置 (环境变量) |

### 功能矩阵
| 能力 | 覆盖内容 |
|------|----------|
| AI 决策报告 | 核心结论、评分、趋势、买卖点位、风险警报、催化因素、操作检查清单 |
| 多市场数据 | A股 · 港股 · 美股 · ETF · 日股(.T) · 韩股(.KS/.KQ) |
| 技术分析 | K 线、技术指标、资金流、筹码分布 |
| 基本面 | 新闻、公告、财务数据 |
| Agent 策略问股 | 15 种内置策略：均线、缠论、波浪、趋势、热点、事件、成长、预期等 |
| 智能导入 | 图片/CSV/Excel/剪贴板；股票代码/名称/拼音/别名补全 |
| 推送渠道 | 企业微信 · 飞书 · Telegram · Discord · Slack · 邮件 |
| Web/桌面工作台 | 手动分析、任务监控、历史报告、回测、持仓管理 |

### AI 模型支持
Anspire、AIHubMix、Gemini、OpenAI 兼容、DeepSeek、通义千问、Claude、Ollama 本地模型

### 数据源
- **行情**: TickFlow、AkShare、Tushare、Pytdx、Baostock、YFinance、Longbridge
- **新闻**: Anspire AI Search、SerpAPI、Tavily、Bocha、Brave、MiniMax、SearXNG
- **社交舆情**: Stock Sentiment API (Reddit/X/Polymarket)

## 竞品对比

| 维度 | daily_stock_analysis | StockBot | FinGPT | TradeStation |
|------|---------------------|---------|--------|-------------|
| 多市场 | ✅ A/H/US/JP/KR | ⚠️ 有限 | ⚠️ 有限 | ✅ 多市场 |
| 零成本 | ✅ GitHub Actions | ❌ 需服务器 | ❌ 需 GPU | ❌ 商业 |
| AI 原生 | ✅ 多模型切换 | ⚠️ | ✅ | ❌ |
| 策略问股 | ✅ 15 种策略 | ✅ 有限 | ✅ | ✅ 复杂 |
| 推送渠道 | ✅ 6 种渠道 | ⚠️ | ❌ | ✅ |
| 开源许可 | ✅ MIT | ✅ | ✅ | ❌ |
| 本地部署 | ✅ Docker + 源码 | ⚠️ | ✅ | ❌ |
| 技术分析 | ✅ 完整 | ✅ | ⚠️ | ✅ |
| Web UI | ✅ FastAPI | ❌ CLI | ❌ | ✅ |

## 核心研判

**优势**：
1. **零成本运营** — GitHub Actions 定时执行 + 免费/低价 API 可实现零服务器成本
2. **最广泛的市场覆盖** — 同时支持 A/H/US/JP/KR 五个主要市场
3. **极低部署门槛** — 5 分钟 Fork + Secrets 配置即可运行
4. **Agent 策略问股** — 15 种内置策略在同类中极为丰富
5. **MIT 许可** — 最宽松的开源许可，可自由商用

**风险/局限**：
1. **数据源质量依赖** — 免费 API（AkShare/Akshare）不稳定风险
2. **不是量化交易系统** — 定位是辅助分析而非自动交易，策略深度受限
3. **日韩市场支持有限** — 部分高阶功能会降级为 not_supported
4. **个性化配置复杂** — 虽然入门快，但深度配置需阅读大量文档
5. A 股用户为主，文档中文为主，英文版存在但非首优先

## 关键文件路径速查

```
/ZhuLinsen/daily_stock_analysis
├── main.py                  # 主入口
├── src/                     # 核心代码
├── docs/                    # 文档
│   ├── full-guide.md        # 完整配置与部署指南
│   ├── LLM_CONFIG_GUIDE.md  # LLM 配置指南
│   ├── market-support.md    # 市场支持边界
│   ├── INDEX.md             # 文档中心
│   ├── README_EN.md         # 英文文档
│   └── README_CHT.md        # 繁体中文文档
├── requirements.txt         # 依赖
├── .env.example             # 环境变量模板
├── docker-compose.yml       # Docker 部署
└── Dockerfile               # Dockerfile
```

## 快速部署

```bash
# 1. Fork 项目 + 配置 GitHub Secrets
# 2. 启用 GitHub Actions → Run workflow
# 3. 默认工作日 18:00 (北京时间) 自动执行
# 或本地部署：
git clone https://github.com/ZhuLinsen/daily_stock_analysis.git
cd daily_stock_analysis
pip install -r requirements.txt
cp .env.example .env
# 编辑 .env 填入 API Key + 自选股
python main.py
```

## 总结

daily_stock_analysis 是目前最成熟的中文 AIGC 股票分析系统，其「零成本 + 多市场 + 多模型 + 多推送」的产品形态在开源领域独树一帜。MIT 许可和极低的部署门槛使其适合个人投资者和小团队。虽然它不是量化交易系统，但其 AI 决策报告 + 策略问股的能力组合已远超同类工具。对于有 A/H 股分析需求的用户，这是目前的最优选择。
