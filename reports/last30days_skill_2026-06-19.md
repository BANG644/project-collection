# last30days-skill 深度调研报告

> **仓库**: mvanhorn/last30days-skill  
> **Stars**: 44,407 | **语言**: Python | **许可**: 自定义  
> **标签**: ai-skill, claude, openclaw, deep-research, reddit, twitter, youtube, trends  
> **调研日期**: 2026-06-19  
> **GitHub Trending**: #1 Repository Of The Day

---

## 项目全景

/last30days 是一个 **AI Agent 驱动的搜索引擎**——由真实的社交参与度（Reddit 点赞、X 喜欢、YouTube 播放、Polymarket 赔率）而非编辑/SEO 打分。

核心理念：**"Google 聚合编辑。 /last30days 搜索人。"**

它不是另一个搜索引擎，而是一个**跨平台数据桥**——将 Reddit、X、YouTube、TikTok、HN、GitHub、Polymarket 等围墙花园通过一个 AI Agent 统一搜索和合成。

### 核心数据
- **44.4K⭐** GitHub Stars
- Trending Shift #1（全球趋势榜）
- **1,012+ 测试通过**
- v3 引擎：支持 14+ 数据源
- Claude Code 官方插件市场收录

---

## 核心架构

### v3 管道

```
用户输入 → `npx skills add mvanhorn/last30days-skill`
         ↓
    Pre-research Brain (Python)
    ├── 解析主题 → 识别实体 + 创始人 + 子版块 + 标签
    ├── 跨平台分解搜索策略
    └── 生成搜索计划 JSON
         ↓
    引擎扩散搜索 (并行)
    ├── Reddit (公开 JSON + 顶帖 + 点赞数)
    ├── X / Twitter (API + 浏览器会话)
    ├── YouTube (字幕索引 + 评论)
    ├── TikTok / Instagram / Threads (ScrapeCreators)
    ├── Hacker News (开发者共识)
    ├── Polymarket (真实赔率 - 真金白银)
    ├── GitHub (PR 速度 + Star 排行 + 发布说明)
    ├── Perplexity Sonar (有引用的网络搜索)
    ├── 网络搜索 (编辑报道)
    └── Digg / Bluesky / Pinterest 等
         ↓
    评分引擎
    ├── 相关性评分
    ├── 趣味评分 (Fun Judge v2) - "最热辣评论"
    └── 跨源聚类 (同一主题不同平台合并)
         ↓
    AI Agent 法官合成
    ├── 叙事化报告 (带引用)
    ├── HTML 简报 (离线可分享)
    └── 竞品对比 (自动发现)
```

### v3 关键创新

1. **预研究大脑 (Pre-research Brain)**：输入"OpenClaw" → 自动解析 @steipete、r/openclaw、r/ClaudeCode、相关 YouTube 频道、TikTok 标签。不是搜关键词，而是搜**正确的人和社区**。

2. **最佳评论 (Best Takes)**：双法官系统——相关性 + 趣味性，把最有趣的一行话放进报告摘要。

3. **跨源聚类**：同一故事出现在 Reddit + X + YouTube 时，合并为一个条目，不重复展示。

4. **单次比较**：`/last30days OpenClaw vs Hermes` 一次性并行跑完，不再串行。

5. **GitHub Person 模式**：查一个人 → 看他这个月合并了多少 PR、什么项目。
   - `/last30days Peter Steinberger --github-user=steipete`

6. **ELI5 模式**：用大白话重写技术报告。

7. **可分享 HTML 简报**：生成离线可用的暗色模式 HTML 文件。

---

## 数据来源一览

| 来源 | 信号类型 | 获取方式 | 是否需要 API Key |
|------|----------|----------|-----------------|
| Reddit | 顶帖 + 评论数 | 公开 JSON | ❌ 免费 |
| X/Twitter | 帖子 + 热度 | 浏览器会话 | ⚠️ 可选 |
| YouTube | 字幕 + 播放量 | YouTube API | ⚠️ |
| TikTok | 参与度 | ScrapeCreators | ⚠️ 付费 |
| Instagram Reels | 影响力 | ScrapeCreators | ⚠️ 付费 |
| Hacker News | 开发者共识 | 公开 API | ❌ 免费 |
| Polymarket | 真实赔率 | 公开 API | ❌ 免费 |
| GitHub | PR + Star | GitHub API | ❌ 免费 |
| Perplexity Sonar | 有引用搜索 | OpenRouter | ⚠️ 付费 |
| Digg | AI 筛选线程 | CLI 工具 | ❌ 免费 |
| Bluesky | AT 协议 | 公开 | ❌ 免费 |
| 网络搜索 | 编辑报道 | 搜索引擎 | ❌ 免费 |

---

## 安装方式

| 工具 | 命令 |
|------|------|
| Claude Code (推荐) | `/plugin marketplace add mvanhorn/last30days-skill` |
| Codex / Cursor / Copilot | `npx skills add mvanhorn/last30days-skill -g` |
| OpenClaw | `clawhub install last30days-official` |
| claude.ai 网页 | 下载 `.skill` 文件上传 |
| Claude Desktop | 下载 `.mcpb` 拖入扩展 |

---

## 使用场景

| 场景 | 命令示例 | 产出 |
|------|----------|------|
| 会前调研 | `/last30days Peter Steinberger` | 最新动态：加入 OpenAI、PR 速度 85% 合并率 |
| 招聘信号 | `/last30days Listen Labs --hiring-signals` | 招聘方向 → 战略优先级 |
| 热点追踪 | `/last30days Kanye West` | 销量、争议、社交媒体反应、预测市场 |
| 工具对比 | `/last30days OpenClaw vs Hermes` | 架构对比、社区反应、GitHub 活跃度 |
| 旅行规划 | `/last30days Universal Epic Universe` | 等待时间、新游乐设施、社区评价 |

---

## 竞品对比

| 特性 | last30days | Perplexity | Google Gemini | ChatGPT Deep Research |
|------|------------|------------|---------------|----------------------|
| Reddit 评论 | ✅ 深度 | ❌ | ❌ | 限 Reddit 合作 |
| X/Twitter | ✅ | ❌ | ❌ | ❌ |
| YouTube 字幕 | ✅ | ❌ | ✅ | ❌ |
| TikTok | ✅ | ❌ | ❌ | ❌ |
| 预测市场赔率 | ✅ | ❌ | ❌ | ❌ |
| 社交参与度评分 | ✅ | ❌ | ❌ | ❌ |
| 趣味性评分 | ✅ | ❌ | ❌ | ❌ |
| Agent 原生集成 | ✅ | ❌ | ❌ | ❌ |
| 完全本地 | ✅ | ❌ | ❌ | ❌ |

---

## 核心研判

### 优势
1. **独有数据源**：唯一能同时搜 Reddit + X + YouTube + TikTok 的 Agent 工具
2. **社交信号优先**：以真实参与度（点赞/顶帖/赔率）而非 SEO 排名排序
3. **低门槛安装**：一个 plugin 命令即可，零配置可用
4. **极度活跃**：44K⭐ + 1,012 测试 + 社区大量 PR
5. **实用场景明确**：会前调研、招聘信号、热点追踪、工具对比、旅行规划

### 不足
1. **付费 API**：部分源（ScrapeCreators/TikTok）需要付费 API Key
2. **无离线模式**：完全依赖网络连接
3. **隐私考虑**：需要浏览器会话访问某些平台
4. **质量波动**：输出质量高度依赖底层 API 可用性

### 适用场景
- 日常信息速览：了解任何话题过去 30 天发生了什么
- 竞争对手/行业监控：自动化定期报告
- 销售/BD 前的客户调研：了解客户最新动态
- 开发者舆论监测：了解社区对某工具的讨论

---

## 关键文件路径

| 文件 | 说明 |
|------|------|
| `README.md` | 主文档 + v3 说明 + 安装指南 |
| `skills/last30days/SKILL.md` | 技能运行时规范（源码真理） |
| `skills/` | 所有技能定义文件 |
| `last30days.skill` | Claude Code 插件包 |
| 发布版 `.mcpb` | Claude Desktop MCP 包 |
