# 🔥 FireCrawl — Web Context API for AI Agents

> **仓库**: [firecrawl/firecrawl](https://github.com/firecrawl/firecrawl)
> **Stars**: 137,137⭐ | **今日新增**: 736⭐
> **语言**: TypeScript | **许可证**: AGPL-3.0
> **官网**: [firecrawl.dev](https://firecrawl.dev)

## 项目概述

FireCrawl 是 AI 时代的 Web Context API 基础设施。它的核心使命很简单：**让 AI Agent 能够像人类一样搜索、抓取并与网页交互**。138K+ GitHub Stars 和行业领先的 96% 网页覆盖率，使其成为目前最流行的开源网页数据提取方案。

与传统的爬虫工具（如 Scrapy、Puppeteer）不同，FireCrawl 专为 LLM/Agent 场景设计，输出可直接供 AI 消费的干净 Markdown 和结构化 JSON，而非原始 HTML。

## 核心能力

### 五大核心端点

| 端点 | 功能 | 延迟 (P95) |
|------|------|-----------|
| **Search** | 搜索引擎查询 + 返回完整页面内容 | ~2s |
| **Scrape** | 任意 URL → Markdown/JSON/截图 | ~3.4s |
| **Crawl** | 全站递归抓取，单请求爬取所有 URL | 可配置 |
| **Map** | 即时发现网站所有 URL | <1s |
| **Interact** | 抓取后通过 AI 或代码操作页面（点击、滚动、填写） | ~5s |

### 特色功能

- **96% 网页覆盖率**：包括 JS 密集的 SPA 页面，无需配置代理
- **媒体解析**：网页托管 PDF、DOCX 等文档自动解析
- **Action 系统**：在提取内容前执行点击、滚动、输入、等待等操作
- **Agent Ready**：通过 MCP 协议与 Claude Code、Cursor 等直接集成
- **LLM 友好输出**：干净的 Markdown（节省 Token）或结构化 JSON Schema
- **批量处理**：异步批处理数千个 URL

## 技术分析

### 架构设计

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  Agent/APP  │────▶│  FireCrawl   │────▶│   Headless  │
│  (SDK/REST) │     │  API Server  │     │   Browser   │
└─────────────┘     └──────┬───────┘     └──────┬──────┘
                           │                     │
                           ▼                     ▼
                    ┌──────────────┐     ┌─────────────┐
                    │  LLM Output  │     │  Proxy Pool │
                    │ (Markdown/   │     │  + Cache    │
                    │  JSON/SS)    │     │             │
                    └──────────────┘     └─────────────┘
```

核心组件链：Agent SDK → REST API → Router → Headless 浏览器池 + 代理池 → 内容提取管线 → LLM 友好输出。

### 技术亮点

1. **多层代理池**：自动旋转 IP，绕过 JS 封锁和机器人检测
2. **智能编排**：自动处理 Rate Limit、重试、JS 渲染等待
3. **并行浏览器池**：百万级页面高吞吐
4. **混合提取策略**：静态 HTML 直读 + JS 渲染双重保障
5. **MCP 协议适配**：原生支持 MCP Stdio 和 SSE 传输

## 与竞品对比

| 特性 | FireCrawl | Scrapy | Puppeteer | Jina Reader |
|------|-----------|--------|-----------|-------------|
| 覆盖率 | 96% | 低级 | 需配置 | ~70% |
| JS 渲染 | 内置 | ❌ | ✅ (手动) | ❌ |
| AI 推理集成 | ✅ (MCP/SDK) | ❌ | ❌ | ✅ |
| 批量抓取 | ✅ (Crawl) | ✅ | ❌ | ❌ |
| Markdown 输出 | ✅ | ❌ | ❌ | ✅ |
| 延迟 (P95) | 3.4s | 依赖配置 | 依赖配置 | ~5s |
| 自托管 | ✅ | ✅ | ✅ | ❌ |

## 使用场景

1. **AI Agent 知识获取**：Claude Code / Cursor 通过 MCP 直接调用获取网页内容
2. **RAG 数据管线**：批量爬取文档站构建知识库
3. **竞品监控**：定时爬取多网站获取结构化变化数据
4. **SEO 分析**：全站 Map + Scrape 获取站点结构和内容
5. **新闻聚合**：搜索 + 提取多源新闻内容

## 入门示例

```python
from firecrawl import Firecrawl

app = Firecrawl(api_key="fc-YOUR_API_KEY")

# 搜索
result = app.search("AI agent scraping tools", limit=5)

# 单页抓取
page = app.scrape("https://docs.firecrawl.dev")

# 全站爬取
crawl = app.crawl("https://example.com")
```

```bash
# CLI
firecrawl search "web scraping" --limit 5
firecrawl scrape https://example.com
firecrawl crawl https://docs.example.com
```

## 结论

FireCrawl 是当前 AI Agent 生态中 Web Context 层的标杆项目。138K+ Stars 验证了它在可观测性和数据获取方面的刚需价值。对 AI 开发者和 Agent 系统构建者来说，它是比传统爬虫更高效的现代替代方案。
