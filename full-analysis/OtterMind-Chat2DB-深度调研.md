# 🔬 OtterMind/Chat2DB — 开源 AI 数据库客户端 + SQL 工作区

> **调研日期**：2026-07-26 | **数据来源**：GitHub API + README + 源码树走读
> **实时数据**：⭐ 26,261（Trending +129/日）| 协议 Source-available（Apache-2.0 + 附加条款，v5.3.0+）| 语言 Java + TypeScript | 官网 chat2db.ai

## 一、项目定位（一句话）

一款 **免费、跨平台、本地优先的开源数据库客户端**，把完整 SQL 工作区与「自带模型」的 AI 助手（text2sql / 解释 / 优化）合二为一，覆盖 30+ 数据库。

## 二、项目亮点（3-5 条差异化，开篇呈现）

- 🤖 **BYO AI 模型**：AI 助手不走厂商锁定，接入你自己的模型做自然语言生成/解释/优化 SQL。
- 🗄️ **30+ 数据库**：MySQL/PostgreSQL/Oracle/SQL Server/ClickHouse/MongoDB/Redis/SQLite/TiDB/Hive/DB2/Snowflake/BigQuery/Elasticsearch… 靠插件扩展。
- 🔒 **本地优先 + 加密**：单用户、local-first，存储的数据源密码与 AI API Key 用 **AES-256-GCM** 每安装密钥加密；HTTP 服务应绑 127.0.0.1。
- 🐳 **Docker 一键部署**：官方提供 `docker run` 与 Compose 定义，社区版开箱即用。
- 📁 **不止 SQL**：数据导入导出、Dashboard/图表、ER 图、可视化数据管理，外加开源 CLI（Chat2DB-CLI，支持 MCP）。

## 三、核心架构

前后端分离，社区版仓库两个顶层模块：

```
Chat2DB/
├── chat2db-community-client/   # 前端：React/TypeScript（yarn，--frozen-lockfile）
├── chat2db-community-server/   # 后端：Spring Boot（Java 17，Maven）
│   └── chat2db-community-start/  # 启动模块（打包成可执行 jar）
├── docker/                     # Dockerfile + docker-compose
├── script/security/            # 加密 key 初始化脚本
└── AGENTS.md                   # AI-agent 友好说明（仓库已为 agent 协作准备）
```

运行模式由 JVM 参数决定：`chat2db.runtime.mode=community` + `chat2db.mode=WEB|DESKTOP`，并通过 `loader.path` 加载 lib。AI 与数据源凭据共用一把密钥、分 AAD 隔离，互不可解密。

## 四、应用场景与启发

- **DBeaver / Navicat 开源替代**：需要免费、跨库、又能用 AI 写 SQL 的团队首选。
- **私有化 AI-SQL 底座**：BYO 模型意味着可接内网大模型，数据不出域——金融/医疗等敏感场景友好。
- **Agent 接数据库范本**：Chat2DB-CLI 支持 MCP，可作为 agent 执行 SQL 动作的安全通道；`AGENTS.md` 说明仓库已考虑 agent 协作。

## 五、源码解读（核心模块精读）

启动命令揭示后端是标准 Spring Boot fat-jar + 自定义 loader：

```bash
java -Dloader.path=chat2db-community-server/chat2db-community-start/target/lib \
     -Dchat2db.runtime.mode=community -Dchat2db.mode=WEB \
     -Dchat2db.community.encryption-key-file="$HOME/.config/chat2db-community/encryption.key" \
     -Dserver.address=127.0.0.1 -Dserver.port=10825 \
     -jar chat2db-community.jar
```

加密 key 解析顺序（首命中即权威）：JVM prop → env → key-file → 默认路径；值须为合法 Base64 且解码恰 32 字节，否则启动失败（不静默降级）。这套「密钥即密钥材料、文件优先避免落参」的设计，是本地优先应用处理凭据的模范实现。

## 六、全网口碑

- 老牌开源 DB 工具，星标 26K+，Trending 仍有增长；社区版功能完整，讨论区（Issues/Discussions/Discord）活跃。
- 用户普遍赞「开源 + 多库 + AI 一体」，对「社区版为 source-available（附加条款）」的许可边界有关注。
- 安全提醒明确：单用户、无账号体系，切勿把 HTTP 暴露到不可信网络。

## 七、竞品对比 + 核心研判

| 维度 | Chat2DB | DBeaver | Navicat/DataGrip | AI2SQL/ByteBrain |
|------|---------|---------|------------------|------------------|
| 开源 | Source-available | ✅ OSS | ❌ 商业 | 各异 |
| 多库 | 30+ | 多 | 多 | 少 |
| 内置 AI | ✅ BYO | ❌ | 部分 | ✅ |
| 本地隐私 | ✅ 加密 | 中 | 中 | 看厂商 |

**核心研判**：
- ✅ **优势**：开源（相对）、数据库覆盖广、AI text2sql 开箱即用、本地加密与 Docker 部署成熟，是企业免授权 DB 工具 + AI 助手的优质底座。
- ⚠️ **风险**：v5.3.0 起改为「Apache-2.0 + 附加条件」的 source-available 许可，闭源商用需读 `LICENSE` 确认；单用户架构不适合多租户托管。
- 🎯 **启发**：要做私有化「对话式数据库」产品，Chat2DB 是现成脚手架；注意许可与「本地优先不可暴露」两条红线。

## 八、关键文件速查

- `README.md` / `README_CN.md` — 功能、Quick Start、安全与加密说明
- `chat2db-community-server/` — Spring Boot 后端（核心逻辑所在）
- `chat2db-community-client/` — React/TS 前端
- `script/security/init-community-encryption-key.sh` — 密钥初始化
- `AGENTS.md` — agent 协作说明
- GitHub：`https://github.com/OtterMind/Chat2DB`
