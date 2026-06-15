# garrytan/gbrain 全方位深度调研报告

## 项目定位

**GBrain** 是一个面向 AI Agent 的"大脑层"知识库系统，由 Y Combinator 总裁兼 CEO Garry Tan 开发。它不仅仅是传统意义上的知识管理工具，而是一个集**信息检索、知识综合、图谱遍历、差距分析**于一体的 AI 原生知识基础设施。GBrain 的核心理念是：搜索给你原始页面，GBrain 给你答案。

Garry Tan 本人的部署数据：**146,646 页面、24,585 人、5,339 公司**，66 个 cron 任务自主运行。他的 Agent 在他睡眠时自动摄取会议、邮件、推文、语音通话和原创想法，并在夜间自动修正引用和整合记忆。

## 基本信息

| 项目 | 值 |
|------|-----|
| GitHub | https://github.com/garrytan/gbrain |
| Stars | 22,854 |
| Forks | 3,269 |
| 主要语言 | TypeScript (19.3MB) |
| 次要语言 | Shell, JavaScript, PLpgSQL, HTML, CSS |
| 许可证 | MIT |
| 创建时间 | 2026-04-05 |
| 最后推送 | 2026-06-14 |
| 默认分支 | master |
| Open Issues | 868 |

## 核心架构

### 三层架构
1. **存储层** — PGLite（本地，2 秒启动，无需 Docker）或 Postgres/Supabase（生产）
2. **检索层** — 混合评分（向量 + 关键词 + RRF + 源层级提升 + 重排序器）
3. **综合层** — `gbrain think` 在检索结果上自动生成带引用的综合答案 + 差距分析

### 核心模块 (`src/core/`)
- `ai/` — AI 集成层
- `calibration/` — 校准系统（含 `svg-renderer.ts` 服务端渲染 SVG 图表）
- `artifact/` — 制品管理
- `abort-check.ts` — 中止检查
- `archive-crawler-config.ts` — 归档爬虫配置
- `audit-*.ts` — 各类审计模块
- `cli.ts` — CLI 入口（105KB+ 单文件）

### 关键特性

| 特性 | 说明 |
|------|------|
| **综合层** | 返回带引用的综合答案，而非页面列表 |
| **差距分析** | 明确指出大脑不知道的内容 |
| **自布线知识图谱** | 页面写入时自动提取实体引用并创建类型化边（`works_at`, `invested_in` 等），零 LLM 调用 |
| **Schema Pack** | 无固定布局，支持自定义类型体系（`gbrain-base-v2` 默认 15 种类型） |
| **Dream Cycle** | 24/7 自动摄取、丰富、整合 |
| **MCP 支持** | stdio 和 HTTP 双模式 MCP 服务器 |
| **多租户** | 基于登录的权限隔离，零泄漏经过模糊测试 |
| **Signal Detector** | 每条消息自动捕获想法、实体提及、待办事项 |

### 性能基准
- **P@5 49.1%, R@5 97.9%**（240 页 Opus 生成语料）
- 图谱变体比非图谱变体 **+31.4 点 P@5**
- 全面超过 ripgrep-BM25 + 纯向量 RAG

### 设计系统
- 深色主题唯一（`--bg-primary: #0a0a0f`）
- WCAG AAA 对比度（正文 ~14:1）
- 字体：Inter（UI）+ JetBrains Mono（数字）
- 间距：4/8/16/24/32px
- SVG 图表服务端渲染，零客户端图表库依赖

## 安装与使用

### 安装方式
1. **Agent 自动安装（推荐）** — ~30 分钟，粘贴 `INSTALL_FOR_AGENTS.md` 链接即可
2. **Claude Code / Codex 快速集成** — `gbrain init --pglite` + `claude mcp add gbrain -- gbrain serve`
3. **CLI 独立安装** — `bun install -g github:garrytan/gbrain`

### 核心命令
- `gbrain search "query"` — 原始检索（页面列表）
- `gbrain think "query"` — 综合答案（带引用和差距分析）
- `gbrain capture "thought"` — 即时捕捉想法
- `gbrain schema detect/suggest/use` — Schema 检测和管理
- `gbrain agent run "task"` — 通过 Minions 队列执行

## 社区口碑

- 发布仅 2 个月即获得 22,854 ⭐，社区反响极为热烈
- YC 已将"公司大脑"（company-brain）列入 RFS（Request for Startups）
- 在 Hacker News、Twitter 等平台获得广泛讨论
- 被多个 AI 代理平台（OpenClaw、Hermes）视为"必装"的大脑层

## 竞品对比

| 特性 | gbrain | Notion AI | Obsidian + Copilot | Mem.ai |
|------|--------|-----------|-------------------|--------|
| 综合答案 | ✅ | ❌（搜索+摘要） | ❌ | ⚠️（有限） |
| 知识图谱 | ✅ 自布线 | ❌ | ✅ 手动 | ❌ |
| 差距分析 | ✅ | ❌ | ❌ | ❌ |
| 24/7 自主运行 | ✅ | ❌ | ❌ | ❌ |
| Schema Pack | ✅ 可自定义 | ❌ 固定 | ⚠️ 插件 | ❌ 固定 |
| MCP 协议 | ✅ | ❌ | ❌ | ❌ |
| 开源 | ✅ MIT | ❌ | ✅ | ❌ |
| 本地部署 | ✅ | ❌ | ✅ | ❌ |

## 核心研判

GBrain 的定位非常清晰：**不是另一个笔记工具，而是 AI Agent 的长期记忆层**。其差异化价值在于：
1. 综合层 + 差距分析的组合，远超传统 RAG
2. 自布线知识图谱零 LLM 成本，性能超越纯向量检索
3. 企业级多租户隔离，定位从个人工具扩展到公司基础设施
4. 由 YC CEO 本人打造，有很强的背书和持续迭代动力

## 关键文件路径

- `README.md` — 项目介绍和安装指南
- `DESIGN.md` — 设计系统规范
- `AGENTS.md` — Agent 配置指南
- `CLAUDE.md` — Claude Code 配置
- `src/cli.ts` — CLI 主入口（105KB）
- `src/core/` — 核心模块
- `docs/tutorials/` — 教程目录
- `docs/mcp/` — MCP 集成文档
- `docs/architecture/` — 架构文档
