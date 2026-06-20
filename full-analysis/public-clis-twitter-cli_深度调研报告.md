# public-clis/twitter-cli — Twitter/X 终端 CLI 深度调研报告

> **一句话定位**：在终端中浏览 Twitter/X Feed、书签和用户时间线的命令行工具。

## 📊 项目全景

| 属性 | 值 |
|------|-----|
| **仓库** | [public-clis/twitter-cli](https://github.com/public-clis/twitter-cli) |
| **Stars** | 2,620 ⭐（2026-06-20） |
| **语言** | Python |
| **许可** | 开源 |
| **创建** | 2026-03-05 |
| **最新** | 2026-05-07 |
| **大小** | 366 KB |
| **组织** | public-clis（专注于公共 CLI 工具的组织） |
| **安装** | `uv tool install twitter-cli` 或 `pipx install twitter-cli` |

## 🏗 核心架构

### 系统架构

```
用户终端命令 (`twitter`)
    ↓
twitter-cli Python 包
    ├── CLI 入口（Click / Typer）
    ├── Twitter/X API 封装
    ├── 浏览器 Cookie 认证（自动提取）
    ├── 环境变量认证（TWITTER_COOKIES / 其他）
    └── 配置管理（config.yaml）
    ↓
Twitter/X Platform
    ├── Feed 时间线
    ├── 书签（Bookmarks）
    ├── 用户时间线
    └── 其他操作
```

### 关键目录结构

```
/
├── twitter_cli/            # Python 核心包
│   ├── __init__.py         # 包入口
│   ├── cli.py              # CLI 命令定义
│   ├── client.py           # Twitter API 客户端
│   ├── auth.py             # 认证模块
│   ├── config.py           # 配置管理
│   └── models.py           # 数据模型
├── tests/                  # 测试
├── docs/                   # 文档
├── AGENTS.md               # Agent 配置（关键文件）
├── SCHEMA.md               # API Schema 文档
├── SKILL.md                # Skill 定义（可直接供 Agent 使用）
├── config.yaml             # 默认配置
└── pyproject.toml          # 项目配置
```

## 🔍 核心功能

### 1. 终端刷推（Feed 时间线）
- 在终端中直接查看 Twitter/X 时间线
- 纯文本渲染，轻量快速
- 支持分页

### 2. 书签浏览
- 查看已收藏的书签
- 按时间排序

### 3. 用户时间线
- 查看指定用户的最新推文
- 支持分页查看

### 4. Agent 原生集成
- AGENTS.md + SKILL.md 双保险
- 可直接供 Claude Code / Cursor 等 Agent CLI 调用
- auth 通过浏览器 Cookie 自动提取（零配置）

### 5. 认证模式
- 浏览器 Cookie 自动提取（默认，最方便）
- 环境变量手动配置（高级用户）

## 📈 社区口碑

| 维度 | 评价 |
|------|------|
| **实用性** | 2.6K Stars，活跃更新中 |
| **Agent 适配** | 有完整的 SKILL.md/AGENTS.md，天然 Agent 友好 |
| **技术质量** | Python 代码结构清晰，有测试覆盖 |
| **组织背书** | public-clis 组织出品，非个人弃坑项目 |

## ⚔ 竞品对比

| 特性 | twitter-cli | Twitter Web | Twitter API | t-ruby |
|------|------------|------------|-------------|--------|
| 终端原生 | ✅ | ❌ | ❌ | ✅ |
| Agent 适配 | ✅ | ❌ | ⚠️ | ❌ |
| Cookie 认证 | ✅ | N/A | ❌ | ❌ |
| Feed 阅读 | ✅ | ✅ | ✅ | ✅ |
| 轻量（< 1MB） | ✅ | ❌ | ❌ | ⚠️ |
| 书签支持 | ✅ | ✅ | ❌ | ❌ |

## 💡 核心研判

1. **Agent 时代的新需求**：Agent CLI 需要访问社交媒体信息，但浏览器不行 — twitter-cli 填补空白
2. **极简认证**：浏览器 Cookie 自动提取解决了 API Key 配置的痛点
3. **SKILL.md 设计精巧**：专门为 Agent 调用优化，定义了功能边界和用法
4. **定位清晰**：不追求全功能 Twitter 客户端，聚焦 Agent 工作流中最常用的读取场景
5. **与 public-clis 生态契合**：同一个组织可能产出更多公共 CLI 服务

## 🔑 关键文件路径

| 用途 | 路径 |
|------|------|
| README | `README.md` |
| Agent 配置 | `AGENTS.md` |
| Skill 定义 | `SKILL.md` |
| Schema 文档 | `SCHEMA.md` |
| CLI 入口 | `twitter_cli/cli.py` |
| 认证模块 | `twitter_cli/auth.py` |
| 配置模板 | `config.yaml` |
| 项目配置 | `pyproject.toml` |
