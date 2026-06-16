# 🔬 public-clis/twitter-cli — 全方位深度调研

## 📌 一句话定位

**用终端看推、发推、搜推，无需 API Key。** 一个纯浏览器 Cookie 认证的 Twitter/X 终端 CLI，覆盖从时间线浏览到发推、点赞、收藏、搜索的全流程。

> — 把 Twitter/X 变成了终端里的一个命令行工具，无需开发者账号和 API Token

---

## 🏗️ 项目架构全景

### 📊 核心指标

| 指标 | 值 |
|------|------|
| ⭐ Stars | 2,603 |
| 🍴 Forks | 238 |
| 📝 主语言 | Python 3.10+ |
| 📜 许可 | Apache 2.0 |
| 📅 创建 | 2026-03-05（3 个月） |
| 🔄 最后更新 | 2026-05-07 |
| 📦 PyPI 版本 | v0.8.6 |
| 🏪 安装 | `uv tool install twitter-cli` / `pipx install` |
| 👤 作者 | **jackwener**（jackwener） |
| 🏛️ 组织 | **public-clis** — 同一作者还维护了小红书、B站、Discord、Telegram CLI |

### 模块架构

```
twitter-cli
├── cli.py          — Click CLI 入口
├── client.py       — HTTP 客户端（curl_cffi 指纹模拟）
├── graphql.py      — Twitter GraphQL API 适配层
├── auth.py         — 浏览器 Cookie 提取（browser-cookie3）
├── parser.py       — HTML/JSON 响应解析
├── models.py       — 数据模型定义
├── filter.py       — 排序过滤器（按 engagement 权重排序）
├── formatter.py    — Rich 表格格式
├── output.py       — JSON / YAML / CSV 输出
├── serialization.py— 序列化
├── search.py       — 搜索模块
├── cache.py        — 本地缓存
├── config.py       — 配置文件管理
├── timeutil.py     — 时间工具
├── constants.py    — 常量定义
├── exceptions.py   — 自定义异常
└── commands/       — 命令模块
```

### Skill 系统集成

`SKILL.md` 是为 AI Agent（Claude Code / Codex）编写的完整操作指南，覆盖：
- 认证引导（3 种方法：浏览器 Cookie / 环境变量 / 完整 Cookie 字符串）
- 所有命令参考（读操作 10+ / 写操作 12+）
- Agent 工作流模板（发推并验证 / 追 thread / 引用推文 / 批量操作）
- 错误处理映射表（HTTP 226/401/403/429 等）

---

## 🧠 独家发现

### 发现 1：GraphQL 接口直接调用，不用 API

`twitter-cli` 不走 Twitter 官方 API（需要开发者账号和 Bearer Token），而是直接调用 Twitter/X 前端使用的 **GraphQL 接口**，用浏览器 Cookie 进行认证。

核心库 `xclienttransaction` 和 `curl_cffi` 负责：
- TLS 指纹模拟（匹配 Chrome 版本）
- User-Agent 匹配
- Cookie 转发

### 发现 2：多浏览器 Cookie 自动提取

`browser-cookie3` 可以自动从 Arc、Chrome、Edge、Firefox、Brave 五种浏览器提取登录 Cookie，支持指定浏览器（`TWITTER_BROWSER=chrome`）和 Chrome Profile（`TWITTER_CHROME_PROFILE="Profile 2"`）。

### 发现 3：作者的多平台 CLI 矩阵

作者 jackwener 不是只做了这一个工具——他做了一个完整的 **public-clis 系列**：
- **xiaohongshu-cli** — 小红书 CLI
- **bilibili-cli** — B 站 CLI
- **discord-cli** — Discord CLI（本地优先同步/搜索/导出）
- **tg-cli** — Telegram CLI（本地优先同步/搜索/导出）

这个矩阵说明作者在做一个系统性的「社交媒体终端化」工程。

### 发现 4：Agent 优化的输出格式

`twitter-cli` 设计了三个输出层级：
1. **Rich Table** — 人类友好的漂亮表格（默认）
2. **YAML/JSON** — 结构化数据（脚本和 AI Agent 使用）
3. **Compact (-c)** — 最少 token 的紧凑格式（AIContext 场景优化，节省约 80% tokens）

其中 YAML 被设为非 TTY 模式的默认输出格式，专为 Agent 调用设计。

### 发现 5：抗检测措施

- 写操作有 1.5-4 秒随机延迟（防止限频）
- TLS 指纹自动匹配浏览器版本
- 支持 HTTP 226 应对策略（浏览器 Cookie 优于 env var）
- 支持 Gift Handle（平台防自动化）的重试策略

---

## 🌐 全网口碑画像

| 来源 | 评价 |
|------|------|
| PyPI | v0.8.6，持续更新 |
| GitHub | 3 个月 2.6K Stars，238 Forks |
| Skill 生态 | 为 AI Agent 提供了完整的 SKILL.md 指南 |
| 作者矩阵 | 4 个同类 CLI 工具（小红书/B站/Discord/Telegram） |

---

## ⚔️ 竞品对比

| 维度 | twitter-cli | twint (已停维) | Twitter API v2 | t | nitter |
|------|-------------|----------------|-----------------|---|--------|
| **认证方式** | 浏览器 Cookie | 无（爬虫） | OAuth 2.0 | 浏览器 Cookie | 无需 |
| **API Key** | ❌ 不需要 | ❌ 不需要 | ✅ 需要 | ❌ 不需要 | ❌ 不需要 |
| **写操作** | ✅ 发/删/赞/转等 | ❌ 只读 | ✅ 完整 | ✅ 完整 | ❌ 只读 |
| **Agent 适配** | ✅ SKILL.md | ❌ | ❌ | ❌ | ❌ |
| **维护状态** | ✅ 活跃 (v0.8.6) | ❌ 停维 | ✅ 官方 | ✅ 活跃 | ✅ 活跃 |
| **Python** | ✅ | ✅ | 多种 | ❌ Rust | ❌ Nim |
| **多平台矩阵** | ✅ 4 个 CLI | ❌ | ❌ | ❌ | ❌ |

---

## 🎯 核心研判

### 🟢 项目优势

1. **零键入门** — 浏览器 Cookie 认证，不需要开发者账号、API Key 或复杂配置
2. **功能完整** — 读（时间线/搜索/书签/用户）+ 写（发/删/赞/转/引用/收藏）全覆盖
3. **Agent 生态加持** — SKILL.md 是为 AI Agent 量身设计的操作手册
4. **输出格式三阶** — Rich/YAML/Compact，覆盖人类、脚本、Agent 三种消费场景
5. **多平台矩阵** — 同一个作者同一个模式做了 4 个 CLI，形成了「public-clis」品牌

### 🔴 项目风险

1. **法律灰色地带** — 通过模拟浏览器，绕过 Twitter 官方 API，存在 TOS 违规风险
2. **GraphQL 接口不稳定** — Twitter 前端接口变更会导致 CLI 失效（作者通过 `xclienttransaction` 封装缓解）
3. **单点维护** — 全系 CLI 均为 jackwener 单人维护，存在 burnout 风险
4. **Cookie 过期** — 浏览器 Cookie 有效期有限（尤其密码变更后）
5. **功能局限** — 不支持视频/GIF 上传、不支持 DM、不支持通知、不支持投票

### 适用场景 ✅

- 不想申请 Twitter API 开发者账号的开发者
- 需要批量管理推文的 CLI 用户
- 嵌入 AI Agent 工作流的 Twitter 操作（Claude Code / Codex）
- 配合 public-clis 矩阵进行跨平台社交媒体管理

### 不适用场景 ❌

- 严肃的商业级 Twitter 运营（需要 API 合规性）
- 视频/GIF 上传场景
- 需要 DM/通知功能的场景

### 趋势判断

**实用的小工具，但定位在灰色地带。** 这类工具（浏览器 Cookie 模拟）在开源社区一直有需求，但 Twitter/X 越收越紧的反爬政策会使维护成本持续升高。如果作者能持续适配 GraphQL 接口变更（目前 v0.8.6 有此韧性），项目可以长期存活。最大价值是作为 **public-clis 矩阵的一块拼图**——jackwener 如果能把 4 个 CLI 统一成一套接口，潜力会更大。

---

## 📂 关键文件路径速查

| 文件 | 用途 |
|------|------|
| `twitter_cli/cli.py` | Click CLI 入口（所有命令定义） |
| `twitter_cli/client.py` | HTTP 客户端（curl_cffi 封装） |
| `twitter_cli/graphql.py` | GraphQL 查询适配层 |
| `twitter_cli/auth.py` | 浏览器 Cookie 自动提取 |
| `twitter_cli/parser.py` | 响应解析 |
| `twitter_cli/models.py` | 数据模型 |
| `twitter_cli/filter.py` | 排序过滤器 |
| `twitter_cli/output.py` | 多格式输出（JSON/YAML/Compact） |
| `twitter_cli/formatter.py` | Rich 表格格式 |
| `twitter_cli/search.py` | 搜索模块 |
| `SKILL.md` | AI Agent 操作指南（完整命令参考+认证引导+工作流模板） |
| `SCHEMA.md` | 结构化输出契约 |

## 🔗 参考链接

- GitHub: https://github.com/jackwener/twitter-cli
- PyPI: https://pypi.org/project/twitter-cli/
- public-clis 矩阵: https://github.com/jackwener/xiaohongshu-cli | bilibili-cli | discord-cli | tg-cli
