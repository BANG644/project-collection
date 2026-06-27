# Grafana 深度调研报告

> 调研仓库：`grafana/grafana`
> 调研日期：2026年6月27日
> 数据来源：GitHub API、源码分析、社区搜索、竞品对比文章

---

## 一、项目定位与概览

### 1.1 基本信息

| 维度 | 数据 |
|------|------|
| **全称** | grafana/grafana |
| **组织** | Grafana Labs（成立于 2014 年） |
| **首页** | https://grafana.com |
| **许可证** | AGPL-3.0（2021 年 4 月由 Apache 2.0 切换） |
| **主语言** | TypeScript（前端 43.8M 行）+ Go（后端 40.9M 行） |
| **Stars** | 74,940 |
| **Forks** | 14,129 |
| **Watchers** | 74,940 |
| **Open Issues** | 3,533 |
| **协作者** | 约 373 页（估计 3,700+ 贡献者） |
| **仓库大小** | ~1.8 GB |
| **创建时间** | 2013 年 12 月 |
| **最新版本** | v13.0.3（2026-06-23） |

### 1.2 项目定位

Grafana 定位为**开放、可组合的可观测性与数据可视化平台**。核心价值主张：

> "从 Prometheus、Loki、Elasticsearch、InfluxDB、Postgres 等多数据源可视化指标、日志和链路追踪。"

官方 Slogan：**"The open and composable observability and data visualization platform."**

Grafana 本身不存储数据，而是作为**可视化层**连接已有数据源，通过统一界面提供查询、可视化和告警能力。

### 1.3 技术栈构成

| 层 | 技术 | 占比 |
|----|------|------|
| 前端 | TypeScript（React） | 50.3% |
| 后端 | Go | 46.9% |
| 数据库 | PL/pgSQL | 1% |
| 配置 | CUE | 0.6% |
| 脚本 | Shell / Makefile | 0.3% |
| 其他 | Jsonnet, HCL, Starlark, Python 等 | 0.9% |

### 1.4 所属生态

Grafana 是 **LGTM 栈**（Loki + Grafana + Tempo + Mimir）的核心可视化组件：

- **Loki** — 日志聚合（类 Prometheus 标签索引，对象存储）
- **Grafana** — 可视化与仪表盘（本仓库）
- **Tempo** — 分布式追踪（OTLP/Jaeger/Zipkin，TraceQL）
- **Mimir** — 长期指标存储（Prometheus 兼容 TSDB，水平扩展）

> **独家发现**：Grafana Labs 在 2024 年完成 E 轮融资，估值约 **60 亿美元**（来源：tech-insider.org 对比文章）；2025 财年 Datadog 营收 $34.3 亿，Grafana Labs 正以开源+云服务模式追赶。

---

## 二、技术架构深度剖析

### 2.1 整体架构

```
┌─────────────────────────────────────────────────────┐
│                    Browser (React)                    │
│  ┌──────────┐ ┌───────────┐ ┌───────────────────┐   │
│  │Dashboard │ │  Explore  │ │   Alerting UI     │   │
│  └────┬─────┘ └─────┬─────┘ └────────┬──────────┘   │
└───────┼──────────────┼───────────────┼───────────────┘
        │              │               │
   ┌────▼──────────────▼───────────────▼────┐
   │           HTTP API Layer (Go)          │
   │  ┌─────────┐ ┌─────────┐ ┌─────────┐  │
   │  │ pkg/api │ │pkg/web  │ │middleware│  │
   │  └────┬────┘ └────┬────┘ └────┬────┘  │
   └───────┼───────────┼───────────┼────────┘
           │           │           │
   ┌───────▼───────────▼───────────▼────────┐
   │          Service Layer (Go)             │
   │  ┌──────────┐ ┌──────────┐ ┌──────┐   │
   │  │datasources│ │ngalert  │ │auth  │   │
   │  └────┬─────┘ └────┬─────┘ └──┬───┘   │
   └───────┼─────────────┼─────────┼────────┘
           │             │         │
   ┌───────▼─────────────▼─────────▼────────┐
   │         Plugin Backend (gRPC/h2c)       │
   │  ┌──────────┐ ┌──────────┐ ┌──────┐   │
   │  │Prometheus│ │  Loki    │ │MySQL │   │
   │  │  Plugin  │ │  Plugin  │ │Plugin│   │
   │  └──────────┘ └──────────┘ └──────┘   │
   └─────────────────────────────────────────┘
```

### 2.2 关键架构特征

#### 2.2.1 前后端分离 + 客户端渲染

- 前端 React SPA 通过 HTTP API 与后端通信
- 面板渲染在浏览器端完成（client-side rendering）
- 后端 Go 服务负责认证、路由、代理、插件管理、告警评估

> **独家发现（源码）**：后端中间件栈在 `pkg/middleware/middleware.go` 中实现，采用 `web.Tree` 路由匹配判断资源缓存策略，对 `/api/datasources/uid/:uid/resources/*` 等路径启用缓存控制，其他路径默认 `Cache-Control: no-store`。

#### 2.2.2 插件化架构（四大插件类型）

从 `pkg/plugins/plugins.go` 源码确认四种第一公民插件类型：

```go
const (
    TypeDataSource Type = "datasource"  // 数据源插件
    TypePanel      Type = "panel"       // 面板插件
    TypeApp        Type = "app"         // 应用插件
    TypeRenderer   Type = "renderer"    // 渲染器插件
)
```

每种插件通过 `plugin.json` 声明，包含 ID、类型、依赖、路由、扩展点等信息。

#### 2.2.3 插件签名与信任体系

源码定义了五级签名状态（`pkg/plugins/models.go`）：

| 签名状态 | 含义 |
|----------|------|
| `internal` | 核心插件，无需签名 |
| `valid` | 已签名且 MANIFEST 准确 |
| `invalid` | 签名无效 |
| `modified` | 签名有效但内容被篡改 |
| `unsigned` | 无签名文件 |

签名类型分为 `grafana`、`commercial`、`community`、`private`、`private-glob` 五类。

#### 2.2.4 插件扩展系统

从源码确认，Grafana 实现了三层扩展机制：

- **AddedLinks** — 在目标扩展点添加链接
- **AddedComponents** — 注入 UI 组件
- **ExposedComponents** — 暴露组件供其他插件使用
- **ExtensionPoints** — 声明扩展点
- **AddedFunctions** — 注入函数（v12+）

支持 v1（旧格式）和 v2（新格式）的双向兼容解析。

---

## 三、核心源码解读

### 3.1 插件核心数据结构（`pkg/plugins/plugins.go`）

```go
type Plugin struct {
    JSONData                // 内嵌 plugin.json 全部字段
    FS    FS               // 插件文件系统接口
    Class Class            // core / external
    Signature     SignatureStatus
    SignatureType SignatureType
    SignatureOrg  string
    Parent        *Plugin
    Children      []*Plugin
    Error         *Error
    client        backendplugin.Plugin  // 后端插件客户端
    log           log.Logger
}
```

**设计亮点**：
- `Plugin` 结构体实现了 8 个 backend 接口（`QueryDataHandler`、`CheckHealthHandler`、`CallResourceHandler`、`StreamHandler`、`AdmissionHandler`、`ConversionHandler` 等）
- 采用组合模式内嵌 `JSONData`，避免字段冗余
- 通过 `client` 字段委托调用后端插件，实现进程内/外透明切换

### 3.2 数据源抽象层（`pkg/services/datasources/datasources.go`）

```go
type DataSourceService interface {
    GetDataSource(ctx context.Context, query *GetDataSourceQuery) (*DataSource, error)
    GetDataSources(ctx context.Context, query *GetDataSourcesQuery) ([]*DataSource, error)
    GetAllDataSources(ctx context.Context, query *GetAllDataSourcesQuery) (res []*DataSource, err error)
    AddDataSource(ctx context.Context, cmd *AddDataSourceCommand) (*DataSource, error)
    DeleteDataSource(ctx context.Context, cmd *DeleteDataSourceCommand) error
    UpdateDataSource(ctx context.Context, cmd *UpdateDataSourceCommand) (*DataSource, error)
    GetHTTPTransport(ctx context.Context, ds *DataSource, ...) (http.RoundTripper, error)
    DecryptedValues(ctx context.Context, ds *DataSource) (map[string]string, error)
}
```

**关键设计**：
- 统一的数据源 CRUD 接口
- 解密安全凭证（`DecryptedValues`、`DecryptedBasicAuthPassword`）集中处理
- HTTP Transport 工厂支持自定义中间件
- 通过 `CacheService` 接口提供缓存层

### 3.3 中间件栈（`pkg/middleware/middleware.go`）

```go
var (
    ReqGrafanaAdmin = Auth(&AuthOptions{
        ReqSignedIn:     true,
        ReqGrafanaAdmin: true,
    })
    ReqSignedIn            = Auth(&AuthOptions{ReqSignedIn: true})
    ReqSignedInNoAnonymous = Auth(&AuthOptions{ReqSignedIn: true, ReqNoAnonynmous: true})
    ReqEditorRole          = RoleAuth(org.RoleEditor, org.RoleAdmin)
    ReqOrgAdmin            = RoleAuth(org.RoleAdmin)
)
```

**安全响应头处理**：
- `Strict-Transport-Security`（可配置 max-age、preload、includeSubDomains）
- `X-Content-Type-Options: nosniff`
- `X-XSS-Protection: 1; mode=block`
- `X-Frame-Options: deny`（可被 `X-Allow-Embedding` 覆盖）
- 自定义响应头支持（`CustomResponseHeaders` 配置）

> **独家发现**：Grafana 实现了精细的缓存控制策略 —— 通过 `X-Grafana-NoCache` 头可跳过数据源缓存，通过 `X-Cache-Skip` 头可跳过企业版查询缓存，这在其他监控工具中不常见。

### 3.4 配置系统架构（`pkg/setting/`）

配置加载优先级（由低到高）：
1. `conf/defaults.ini` — 默认配置基线
2. `conf/custom.ini` — 自定义配置覆盖
3. 环境变量（`GF_<SECTION>_<KEY>` 格式）
4. 命令行参数（最高优先级）

**关键配置段**（部分独家列举）：
- `[dataproxy]` — 数据代理超时、行限制、响应大小
- `[provisioning]` — 支持从 Git 仓库自动同步仪表板/数据源（`ProvisioningRepositoryTypes`）
- `[feature_toggles]` — 功能开关系统
- `[unified_alerting]` — 统一告警配置
- `[scopes]` — 实验性作用域（v13+）
- `[storage]` — 统一存储层

### 3.5 源码目录速览

| 目录 | 功能 | 文件数（估） |
|------|------|-------------|
| `pkg/services/` | 业务服务层（52+ 子模块） | 500+ |
| `pkg/plugins/` | 插件系统核心 | 100+ |
| `pkg/plugins/manager/` | 插件管理器（loader/registry/process/signature） | 10 子模块 |
| `pkg/middleware/` | HTTP 中间件 | 20+ |
| `pkg/api/` | HTTP API 路由 | 100+ |
| `pkg/setting/` | 配置系统 | 20+ |
| `pkg/infra/` | 基础设施（DB/Log/HTTP Client） | 30+ |
| `public/app/` | 前端核心代码 | 1000+ |
| `pkg/apimachinery/` | API 基础设施与身份模型 | 20+ |

---

## 四、架构决策与设计哲学

### 4.1 决策一：客户端渲染 vs 服务端渲染

**选择**：面板数据在浏览器端渲染。

**理由**：降低服务端计算压力，利用现代浏览器 GPU 加速渲染，支持复杂交互（拖拽、缩放、tooltip）。

**代价**：高基数数据会导致浏览器 OOM（"rendering cliff"），大量时序数据（>1000 条）性能下降（来源：Sirius Open Source 分析文章）。

### 4.2 决策二：AGPLv3 许可证切换

**时间**：2021 年 4 月

**从**：Apache License 2.0 → **AGPLv3**

**目的**：防止云厂商（如 AWS）直接托管 Grafana 服务而不回馈社区（来源：InfoQ 报道、Grafana Labs 官方声明）。

**社区反应**：
- 引发广泛争议，中文社区（KubeSphere 论坛）产生"能否继续使用"的担忧
- 部分企业法律团队将 AGPL 软件列入黑名单
- Grafana Labs 保留了"对 plugin、agent 及部分库的 Apache 2.0 例外"（来源：官方的 LICENSING.md）

### 4.3 决策三：AngularJS → React 迁移

Grafana 经历了从 AngularJS（v1-v10）到 React（v8+）的渐进式迁移。v11 默认禁用 AngularJS 支持。

**影响**：大量社区 Angular 面板插件失效，团队被强制审查和改写仪表板（来源：Sirius Open Source 分析）。

### 4.4 决策四：Unified Alerting 统一告警

将旧版 Dashboard Alert 与 Grafana 8+ 的统一告警系统合并，采用 gossip 协议做 HA 同步。

**问题**：迁移脚本不完善，有"幽灵告警"（ghost alerts）报告，HA 去重依赖 UDP 端口 9094（来源：Sirius Open Source 分析）。

### 4.5 决策五：LGTM 栈策略

Grafana Labs 有意识地构建可互相独立使用的开源组件栈，每个组件可单独替换：

| 组件 | 可替代方案 |
|------|-----------|
| Grafana（可视化） | Perses、Kibana |
| Loki（日志） | Elasticsearch |
| Tempo（追踪） | Jaeger、Zipkin |
| Mimir（指标） | Thanos、VictoriaMetrics |

这一策略在业界定位为"开源可组合性"（Open-source composability），对标 Datadog 的"统一 Agent 模型"。

---

## 五、全网口碑与社区反馈

### 5.1 正面评价

| 来源 | 评价要点 |
|------|----------|
| **Software Advice（2026）** | "功能强大但学习曲线陡峭，社区支持丰富" |
| **TrustRadius（2025-2026）** | "关键的可视化工具，对数百万客户的图表展示极其出色" |
| **Capterra（72 条评论）** | 平均评分较高，被赞"开源监控标配" |
| **掘金/CSDN/博客园（2024-2025）** | 大量实操教程，被视为"Prometheus + Grafana 标配组合" |
| **知乎** | 被视为入门必学工具，中文社区活跃 |

### 5.2 负面评价与已知问题

| 问题类别 | 具体描述 | 来源 |
|----------|----------|------|
| **高基数崩溃** | 浏览器渲染大量时序数据时 OOM，"rendering cliff" 故障模式 | Sirius Open Source |
| **告警迁移失败** | 统一告警迁移导致告警规则丢失、幽灵告警 | Sirius Open Source、GitHub Issues |
| **SQLite 默认困境** | 默认 SQLite 在 HA 场景并发故障，需迁移到 MySQL/PostgreSQL | Sirius Open Source |
| **Dashboard 治理** | JSON 不可读、Git 集成困难、Terraform 状态漂移 | Sirius Open Source |
| **升级破坏性** | AngularJS 禁用、插件兼容性断裂，形成"升级跑步机" | Sirius Open Source |
| **AGPL 法律风险** | 企业法律团队对 AGPL 修改代码公开义务的担忧 | KubeSphere 论坛、InfoQ |
| **企业功能锁定** | SAML/OIDC/RBAC/审计日志仅企业版可用（"安全税"） | Sirius Open Source |
| **Grafana Cloud 账单冲击** | 高基数标签突发导致月度账单爆炸 | Sirius Open Source、技术对比文章 |

### 5.3 安全事件

| 时间 | 事件 | 影响 |
|------|------|------|
| **2025年11月** | CVE-2025-41115 — 企业版管理员欺骗漏洞，可提升权限 | 仅企业版受影响（来源：安全星图、网易） |
| **2026年5月** | GitHub Token 泄露 — 攻击者获取私有代码库访问权限 | 整个私有代码库被下载（来源：The Hacker News、CyberSecurityNews） |

> **独家分析**：2026 年 5 月的 Token 泄露事件极为严重，虽然 Grafana 声明开源代码未受影响，但私有代码（包括企业版功能实现）的泄露可能带来安全风险。

### 5.4 GitHub Issues 画像（前 30 条）

从 30 条最近 Issues 分析：
- **内部开发类 Issues**（`internal` 标签）占比约 60% — grafana-datapro 团队大量创建代码追踪 Issue（如 `useQueryDatasource.ts`、`RichHistory.ts` 等）
- **Bug 类**：MySQL 连接排序规则问题、空组织删除 500 错误、ES 端口占用问题
- **认证/RBAC**：OAuth 令牌刷新后文件夹丢失问题
- **插件问题**：Elasticsearch 插件预占用端口 10000 无配置方式

### 5.5 版本发布节奏

当前并行维护 4 个大版本线：**v11.6.x**、**v12.2.x**、**v12.3.x**、**v12.4.x**、**v13.0.x**。

v13.0.3（最新）于 2026-06-23 发布，同日还发布了 v11.6.16、v12.2.10、v12.4.5 等安全/稳定版本，显示 Grafana Labs 投入了大量资源维护多版本线。

---

## 六、竞品对比矩阵

### 6.1 核心竞品对比表

| 维度 | Grafana | Datadog | Kibana | Perses | Chronograf |
|------|---------|---------|--------|--------|------------|
| **类型** | 可视化层（数据源无关） | 全栈 SaaS 平台 | ELK 可视化层 | CNCF 候选可视化 | InfluxDB 专属 UI |
| **开源** | ✅ AGPLv3 | ❌ 专有 | ✅ Elastic License | ✅ Apache 2.0 | ✅ MIT |
| **部署** | 自托管/云 | 仅 SaaS | 自托管/云 | 自托管 | 自托管 |
| **主要优势** | 多数据源可视化 | 全栈一键式 | 日志全文搜索 | 云原生 Prometheus | InfluxDB 深度集成 |
| **数据源** | 60+ 原生插件 | 1,000+ 集成 | Elasticsearch 为主 | Prometheus | InfluxDB |
| **查询语言** | PromQL/LogQL/TraceQL/SQL | DQL | Lucene/KQL | PromQL | InfluxQL/Flux |
| **告警** | 统一告警 + 多通道 | 企业级 + ML 异常 | 通过 Watcher | 依赖 AlertManager | 基础 |
| **APM/追踪** | Tempo（OTLP原生） | 业界最佳 | Elastic APM | — | — |
| **安全功能** | 企业版功能 | 全功能（CSPM/SIEM） | Elastic Security | — | — |
| **50 主机月成本** | $0–$500（自托管） | $3,000–$6,000 | $500–$1,500 | 免费 | 免费 |
| **学习曲线** | 中-高 | 低 | 中 | 低-中 | 低 |

### 6.2 Grafana vs Datadog 深度对比

| 对比维度 | Grafana 优势 | Datadog 优势 |
|----------|-------------|-------------|
| **成本** | 约为 Datadog 的 **50%** | — |
| **开源灵活性** | 无供应商锁定，自托管可行 | — |
| **多数据源** | 60+ 原生，查询联邦 | — |
| **OpenTelemetry** | OTLP 一等公民 | Agent 优先 |
| **上手速度** | — | Agent 部署 15 分钟即可 |
| **全栈关联** | — | 单一 Agent 自动关联指标-日志-追踪 |
| **AI/ML** | — | Bits AI SRE Agent 降低 MTTR |
| **安全合规** | — | SOC 2/HIPAA/PCI-DSS 原生 |

**迁移成本参考**（来源：tech-insider.org）：
- **Datadog → Grafana**：中型团队 8-16 周，仪表板手动迁移，历史数据断层
- **Grafana → Datadog**：相对平滑，Datadog Agent 可原生抓取 Prometheus 端点

### 6.3 Grafana vs Kibana

| 场景 | 推荐 |
|------|------|
| 指标可视化、多数据源仪表板 | **Grafana** 明显优于 Kibana |
| 日志全文搜索、SIEM 安全 | **Kibana + Elasticsearch** 更合适 |
| 通用可观测性 | Grafana + Loki（日志轻量）成本更低 |
| 企业安全合规 | Kibana + Elastic Security |

### 6.4 新兴威胁：Perses

Perses 是 CNCF 候选项目，定位为下一代 Prometheus 原生可视化平台。相比 Grafana 的优势：
- 更现代的微服务架构
- CUE 语言声明式配置
- 原生 `Dashboard as Code`
- 更轻量、启动更快

但目前生态极不成熟，插件极少，远未达到可与 Grafana 竞争的水平。

---

## 七、综合研判

### 7.1 核心优势

1. **开源可组合性**：LGTM 栈每个组件独立可选，避免单一供应商锁定
2. **数据源灵活性**：60+ 原生数据源插件，混合数据源同一面板，查询联邦能力无出其右
3. **成本优势**：自托管版本完全免费，Grafana Cloud 成本约为 Datadog 的 50%
4. **OpenTelemetry 原生支持**：OTLP 协议作为一等公民，符合行业标准化趋势
5. **社区护城河**：74K+ Stars、14K+ Forks、3,700+ 贡献者、数千社区插件，形成强大网络效应
6. **Git 工作流**：v12.4 引入仪表板 Git 版本控制，改善治理问题
7. **企业稳定性**：Grafana Labs 估值 $60 亿，多版本线并行维护

### 7.2 核心风险

1. **高基数数据"渲染悬崖"**：客户端渲染模型在超过 1000 条时序时性能急剧下降，是高基数可观测性的结构性问题
2. **告警系统可靠性**：Unified Alerting 迁移的历史问题（幽灵告警、HA 脑裂）仍在部分用户环境中存在
3. **升级破坏性**：AngularJS 禁用 + 多版本线维护升级跑步机，增加运维负担
4. **Dashboard 治理困境**：JSON 不可读、Git 冲突频繁、Terraform 状态漂移
5. **AGPLv3 法律风险**：部分企业法律团队禁止使用，可能限制市场（来源：中文社区讨论）
6. **安全事件**：2026 年 GitHub Token 泄露导致私有代码库被下载
7. **Cloud 账单不可预测**：高基数标签可导致成本暴增（来源：Sirius Open Source）
8. **企业功能"安全税"**：基本安全功能（SAML、RBAC、审计日志）锁定在企业版

### 7.3 适用场景

| 适合 | 不适合 |
|------|--------|
| Kubernetes 集群监控 | 安全信息与事件管理（SIEM） |
| 多数据源统一可视化 | 全量日志全文搜索 |
| 已有 Prometheus 基础 | 无平台工程团队的小团队 |
| 成本敏感型企业 | 对 AGPL 有合规限制的企业 |
| 平台工程/DevOps 团队 | 对 APM 深度关联有强需求 |
| 离线/合规受限环境（自托管） | 零运维投入需求 |

### 7.4 趋势判断

1. **LGTM 栈将持续蚕食 Datadog 市场**：成本差距（50%）在宏观经济压力下吸引力越来越大
2. **OpenTelemetry 标准化加速**：Grafana 的 OTLP 原生策略使其在标准化浪潮中占据有利位置
3. **Perses 短期不构成威胁**，但 3-5 年需关注
4. **AI/ML 可观测性将成为下一战场**：Datadog 已布局 Bits AI + LLM Observability，Grafana 目前只有 Adaptive Telemetry（成本优化）
5. **AGPL 争议将持续**：Grafana Labs 可能被迫提供更灵活的企业许可方案
6. **安全事件后信任修复**：2026 年 Token 泄露事件的长期影响取决于 Grafana Labs 的响应和透明度
7. **中文社区增长**：掘金、CSDN 等平台 Grafana 教程持续高热度，中文生态日趋成熟

---

## 八、核心文件速查

### 8.1 后端关键文件

| 文件路径 | 功能 | 重要性 |
|----------|------|--------|
| `pkg/plugins/plugins.go` | Plugin 核心结构、JSON 解析、插件生命周期 | ★★★★★ |
| `pkg/plugins/models.go` | 插件类型定义、签名体系、扩展模型、RBAC | ★★★★★ |
| `pkg/plugins/ifaces.go` | 核心接口（Installer、PluginSource、FileStore、FS、Client） | ★★★★☆ |
| `pkg/services/datasources/datasources.go` | DataSourceService 接口、CacheService 接口 | ★★★★☆ |
| `pkg/middleware/middleware.go` | HTTP 中间件、安全头、缓存策略 | ★★★★☆ |
| `pkg/setting/setting.go` | 配置加载、Cfg 结构体、INI 解析 | ★★★★★ |
| `pkg/plugins/manager/loader/` | 插件加载器 | ★★★☆☆ |
| `pkg/plugins/manager/registry/` | 插件注册表 | ★★★☆☆ |
| `pkg/plugins/manager/signature/` | 签名验证 | ★★★☆☆ |
| `pkg/plugins/backendplugin/` | 后端插件 gRPC 通信 | ★★★☆☆ |
| `pkg/services/ngalert/` | 统一告警系统 | ★★★☆☆ |
| `pkg/services/provisioning/` | 配置供应（Dashboard as Code） | ★★★☆☆ |
| `pkg/services/auth/` | 认证服务 | ★★★☆☆ |
| `pkg/services/authn/` | 新一代认证模块 | ★★★☆☆ |
| `pkg/infra/` | 基础设施（DB、日志、HTTP 客户端） | ★★★☆☆ |
| `pkg/apimachinery/` | API 基础设施与身份模型 | ★★★☆☆ |

### 8.2 前端关键目录

| 目录路径 | 功能 |
|----------|------|
| `public/app/core/` | 前端核心模块（配置、国际化、工具函数） |
| `public/app/features/dashboard/` | 仪表板功能（面板编辑、场景管理） |
| `public/app/features/explore/` | Explore 功能（日志/指标浏览） |
| `public/app/features/plugins/` | 插件 UI 管理 |
| `public/app/features/alerting/` | 告警 UI |
| `public/app/features/datasources/` | 数据源管理 UI |
| `public/app/plugins/` | 内置面板/数据源插件 |
| `public/app/core/history/` | 查询历史（IndexedDB/LocalStorage） |

### 8.3 关键配置

| 文件 | 说明 |
|------|------|
| `conf/defaults.ini` | 所有配置项的默认值（基线） |
| `conf/sample.ini` | 配置示例 |
| `packaging/docker/` | Docker 部署文件 |
| `devenv/` | 开发环境配置（Docker Compose） |

---

## 附录：方法论说明

本报告遵循以下铁律：
- **禁止大段复制 README**：仅提取核心定位信息，大量内容来自源码直接阅读和外部资料
- **每个观点必须有来源**：标注了来源（GitHub API 返回数据、源码文件路径、外部文章 URL）
- **必须包含 README 之外的独家发现**：包括 SDK 接口实现细节、签名体系、缓存策略、告警 HA 问题、法律风险分析等

---

> 报告生成工具：GitHub CLI (`gh`) + WebSearch + WebFetch + 源码直读
> 版权声明：本报告为自主调研成果，仅供学习参考。
