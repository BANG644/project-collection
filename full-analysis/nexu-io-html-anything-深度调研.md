# nexu-io/html-anything — Agentic HTML 编辑器深度调研报告

> **一句话定位**：让 AI Agent 把任何 Markdown 内容变成世界级设计水准的 HTML 发布物，75 套 Skill 模板 × 9 种导出格式。

## 📊 项目全景

| 属性 | 值 |
|------|-----|
| **仓库** | [nexu-io/html-anything](https://github.com/nexu-io/html-anything) |
| **Stars** | 7,009 ⭐（2026-06-20） |
| **语言** | TypeScript (61.4%) / HTML (22.3%) / CSS (10.8%) |
| **许可** | MIT |
| **创建** | 2026-05-11 |
| **最新** | 2026-06-16 |
| **大小** | 15 MB |
| **开发者** | nexu-io 团队（open-design 40K+ Stars 的原班人马） |
| **安装** | `git clone + pnpm install + pnpm dev` |

## 🏗 核心架构

### 系统架构

```
用户内容（Markdown / 链接 / 粘贴文本）
    ↓
html-anything Editor（Next.js Web 应用）
    ├── Agent Detector → 自动识别 18 种 Code Agent CLI
    │   （Claude Code / Codex / Cursor / Gemini / OpenClaw / Qwen / Aider ...）
    ├── Skill Template Engine → 75 套模板
    ├── Export Engine → 9 种输出格式
    ├── Preview → 沙盒安全预览
    ├── Security → 隐私安全检查
    └── Deploy → 一键发布
    ↓
交付物（HTML / PNG / 微信 / 知乎 / X / 小红书 / 数据报告 / Deck / Hyperframes）
```

### 关键目录结构

```
/
├── next/                        # Next.js 前端
│   ├── src/
│   │   ├── app/
│   │   │   ├── api/
│   │   │   │   ├── agents/      # 18 种 Agent CLI 检测
│   │   │   │   ├── convert/     # 转换引擎
│   │   │   │   ├── deploy/      # 部署接口
│   │   │   │   └── draft/       # 草稿管理
│   │   │   ├── components/      # React 组件
│   │   │   └── lib/
│   │   │       ├── agents/      # Agent 集成层
│   │   │       ├── deploy/      # 发布逻辑
│   │   │       ├── export/      # 9 种导出格式
│   │   │       ├── security/    # 安全检测
│   │   │       ├── skills/      # 模板仓库
│   │   │       └── templates/   # 模板引擎
│   │   └── middleware.ts        # 中间件
│   ├── AGENTS.md                # Agent 配置
│   └── CLAUDE.md                # Claude Code 配置
├── docs/                        # 文档
├── e2e/                         # 端到端测试
└── scripts/                     # 脚本
```

## 🔍 核心功能

### 1. 75 套 Skill 模板 × 9 种输出格式

| 格式 | 适用场景 |
|------|---------|
| Magazine | 公众号长文、博客 |
| Keynote Deck | 演示 PPT、汇报 |
| Poster | 宣传海报、活动物料 |
| XHS Card | 小红书图文卡片 |
| Tweet Card | Twitter/X 推文配图 |
| Resume | 个人简历 |
| Web Prototype | 网页原型、落地页 |
| Data Report | 数据分析报告 |
| Hyperframes | 类视频 HTML 动效 |

### 2. Zero API Key — BYOK（Bring Your Own Key）
- 自动检测本地已安装的 18 种 Code Agent CLI
- Claude Code / Codex / Cursor / Gemini / Copilot / OpenCode / Qwen / Aider 等
- 无 API 费用，完全本地运行

### 3. 一键发布
- 微信 / X(Twitter) / 知乎 / 小红书
- HTML / PNG 导出
- 剪切板复制

### 4. 安全设计
- 沙盒预览：生成内容在隔离环境渲染
- 内容扫描：自动检测注入风险
- 隐私优先：所有处理在本地完成

## 📈 社区口碑

| 维度 | 评价 |
|------|------|
| **团队背书** | nexu-io 之前做出 open-design（40K+ Stars），质量有保障 |
| **上手指南** | README + AGENTS.md + CLAUDE.md 三件套齐全 |
| **爆发速度** | 开源 4 天破 1,700 Stars，后续稳定增长至 7K |
| **实用评价** | "比截图工具好一万倍"、"AI 时代的 Canva 替代品" |

## ⚔ 竞品对比

| 特性 | html-anything | Canva | Open-Design | Markdown → 截图 |
|------|--------------|-------|-------------|----------------|
| Agent 原生 | ✅ | ❌ | ❌ | ❌ |
| 本地运行 | ✅ | ❌ | ✅ | ✅ |
| 75 模板 | ✅ | ✅ | ❌ | ❌ |
| 9 种导出 | ✅ | ⚠️ | ❌ | ❌ |
| 零 API 成本 | ✅ | ❌ | ✅ | ✅ |
| 微信/小红书 | ✅ | ❌ | ❌ | ❌ |
| 开源 | ✅ MIT | ❌ | ✅ | ✅ |

## 💡 核心研判

1. **精准定位**：Markdown 是草稿，HTML 才是人类阅读的格式 — 抓住 Agent 时代内容生产的痛点
2. **强团队背书**：nexu-io 连续做出 open-design + html-anything 两个爆款，产品理解力一流
3. **生态兼容性**：零 API Key + 支持 18 种 Agent CLI = 最低采用门槛
4. **细分场景碾压**：微信/小红书/知乎等国内容平台的排版痛点，传统工具无法解决
5. **潜在风险**：纯 HTML 编辑器赛道窄，需横向扩展到更多使用场景

## 🔑 关键文件路径

| 用途 | 路径 |
|------|------|
| README（中文） | `README.zh-CN.md` |
| AGENTS.md | `next/AGENTS.md` |
| Agent 检测 API | `next/src/app/api/agents/` |
| 导出引擎 | `next/src/lib/export/` |
| 技能模板 | `next/src/lib/templates/skills/` |
| 安全模块 | `next/src/lib/security/` |
| 部署模块 | `next/src/lib/deploy/` |
| 模板列表 | `next/src/lib/skills/` |
| 配置 | `CLAUDE.md` / `AGENTS.md` |
