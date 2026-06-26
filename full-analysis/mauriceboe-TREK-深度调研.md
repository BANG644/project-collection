# mauriceboe/TREK — 深度项目研究报告

> 生成日期：2026-06-27  
> 仓库地址：https://github.com/mauriceboe/TREK  
> 在线演示：https://demo.liketrek.com  

---

## 1. 项目概览

### 1.1 基本信息

| 指标 | 数值 |
|------|------|
| **Stars** | 7,588 |
| **Forks** | 646 |
| **提交数** | 1,277 |
| **分支数** | 6 |
| **标签数** | 81 |
| **最新版本** | v3.1.2 |
| **许可证** | AGPL-3.0 |
| **主要语言** | TypeScript |
| **创建日期** | 2026-03-19 |
| **最后推送** | 2026-06-26 |
| **作者** | mauriceboe |

### 1.2 项目定位

TREK 是一个**自托管（Self-Hosted）的团队旅行规划器**，定位为 Wanderlog 的开源自架替代方案。核心价值主张是：**你的数据、你的服务器、你的规则**。只需一行 Docker 命令即可部署，支持 PWA（渐进式 Web 应用）、实时协作、交互式地图、预算追踪、打包清单、AI 集成（MCP）等功能。

项目描述原文：*"A self-hosted travel/trip planner with real-time collaboration, interactive maps, PWA support, SSO, budgets, packing lists, and more."*

### 1.3 仓库标签

`travel-planner` `self-hosted` `collaborative` `budget-tracker` `packing-list` `real-time` `PWA` `wanderlog-alternative`

---

## 2. 社区数据

### 2.1 Issues（问题追踪）

- 共抓取 20+ 个 Issues，包含活跃的 Bug 报告和功能请求
- 作者（mauriceboe）**亲自回复几乎所有 Issue**，响应迅速（通常在数小时内）
- 标签体系：`fixed`、`critical`、`bug`、`enhancement` 等
- **值得关注的 Issue：**
  - **OIDC 管理员降级问题**（critical）：JWT 轮换时可能导致管理员权限丢失
  - 路线优化 Bug：路径计算在某些场景下产生异常
  - i18n 翻译问题：部分语言的翻译不完整或错误
  - 移动端日期选择器交互问题

### 2.2 PRs（合并请求）

- 当前有 5 个 Open PRs：
  - v3.1.3 版本发布准备
  - LLM 预订提取（从邮件中的预订确认自动提取）
  - ICS 日历 Feed 导出
  - Unsplash 图片搜索集成
  - 日期选择器改进
- 发布节奏：大约每周一次，以 Bug 修复为主

### 2.3 Releases（发布版本）

| 版本 | 日期 | 说明 |
|------|------|------|
| v3.1.2 | 最新稳定版 | 当前推荐版本 |
| v3.1.1 | 前一版本 | Bug 修复 |
| v3.1.0 | 主版本 | Express → NestJS 迁移完成 |
| v3.1.0-pre.3/pre.2 | 预发布 | 预览版本 |

---

## 3. 功能全景

### 3.1 行程规划与管理

| 功能 | 详情 |
|------|------|
| 多日行程 | 创建有日期或无限期行程，自动生成每日结构 |
| 拖拽排序 | 拖拽重新排列每天的行程顺序，直觉化操作 |
| 插入日期 | 任何位置插入新的旅行日 |
| 住宿管理 | 设置每日住宿，以住宿为锚点优化路线 |
| 日历导出 | ICS 格式导出行程日历 |
| PDF 导出 | 完整行程手册导出（多段航班、地点坐标） |
| PDF 分包 | 按旅行分期生成子 PDF，支持封面品牌定制 |

### 3.2 地图与导航

| 功能 | 详情 |
|------|------|
| 双地图引擎 | Leaflet（免费） + Mapbox GL（高级） |
| 真实道路路线 | OSRM 驾车/步行路线替代直线连接 |
| 多段航线路 | 显示多段航线的弧形和标记 |
| POI 探索 | OpenStreetMap 搜索附近餐厅、咖啡馆、景点 |
| 地图罗盘 | Mapbox 模式下的指北罗盘 |
| GPX 导入 | 支持 GPX 轨迹/路线导入，多文件批量导入 |
| 离线地图 | PWA 离线瓦片缓存，覆盖真实行程区域 |

### 3.3 交通与预订

| 功能 | 详情 |
|------|------|
| 多段航班 | 支持转机/经停（FRA → BER → HND）的多段航线 |
| 11 种交通类型 | 飞机、火车、汽车、邮轮、公交、出租车、自行车、渡轮、步行等 |
| 预订导入 | KDE KItinerary 自动解析邮件/PDF/PKPass 预订确认 |
| AirTrail 集成 | 从 AirTrail 导入航班并双向同步 |
| 预订管理 | 酒店、餐厅、活动、旅游等多类型预订，含确认码 |
| 预订排序 | 日间预订和交通显示顺序可调整 |

### 3.4 协作功能

| 功能 | 详情 |
|------|------|
| 实时同步 | WebSocket 驱动的多人实时编辑 |
| 角色权限 | 细粒度权限控制（Owner / Editor / Viewer） |
| 邀请链接 | 一次性邀请链接，设定期限自动失效 |
| 协作文档 | 共享笔记（支持 Markdown、颜色、置顶） |
| 群聊 | 内置聊天频道（支持表情回应、回复线程、链接预览） |
| 投票 | 行程决策投票（单选/多选、截止日期） |
| 文件共享 | 行程文件上传（最大 50MB）和共享 |

### 3.5 预算与费用

| 功能 | 详情 |
|------|------|
| 费用分摊 | Splitwise 风格的多付款人费用分摊 |
| 多币种 | 每笔费用独立货币，实时汇率转换 |
| 12 个费用类别 | 交通、住宿、餐饮、活动、购物等 |
| 结算 | 清算历史记录和撤销功能 |
| 显示货币 | 用户可设默认显示货币 |

### 3.6 打包清单

| 功能 | 详情 |
|------|------|
| 物品管理 | 按数量计算重量 |
| 背包分组 | 16 种颜色自动分配子背包（随身携带、托运行李等） |
| 模板 | 管理员创建打包模板供成员使用 |
| 批量导入 | 按物品数量批量导入 |
| 成员分配 | 将物品指派给特定成员（谁带转接器、谁带急救包） |

### 3.7 认证与安全

| 功能 | 详情 |
|------|------|
| 密码登录 | 标准用户名/密码认证 + 密码策略 |
| Passkey/WebAuthn | 指纹/Face ID 等无密码登录 |
| OIDC SSO | 支持任意 OIDC 提供商（含 PKCE S256） |
| 两步验证 | TOTP 双因素认证 |
| OAuth 2.1 | MCP OAuth 服务器（27 个粒度 Scope） |
| 会话管理 | 可配置会话时长（SESSION_DURATION） |
| 密码重置 | 速率限制保护 |
| 审计日志 | 完整操作审计追踪 |

### 3.8 数据可视化

| 功能 | 详情 |
|------|------|
| Atlas 地图集 | 已访问国家/地区高亮（geoBoundaries 数据） |
| 仪表盘 | 登机牌式英雄卡片、倒计时、旗帜统计 |
| 旅行统计 | 国家数/距离/飞行公里数 |
| Journey 画廊 | 旅行日记和照片（支持 Immich/Synology） |
| 旅行记忆 | 跨行程旅行叙事，带条目、贡献者和分享链接 |

### 3.9 PWA 与离线支持

| 功能 | 详情 |
|------|------|
| PWA 安装 | iOS/Android 可安装为独立应用 |

### 3.10 国际化

支持 **20 种语言**：阿拉伯语、巴西葡萄牙语、捷克语、德语、希腊语、英语、西班牙语、法语、匈牙利语、印尼语、意大利语、日语、韩语、荷兰语、波兰语、俄语、土耳其语、乌克兰语、简体中文、繁体中文

### 3.11 附加组件（Addons）

TREK 采用插件化架构，通过 Addon 系统管理可选功能模块：

| Addon | 功能描述 |
|-------|----------|
| **Atlas** | 世界旅行地图 — 统计、已访问国家/地区、心愿单、洲际分布 |
| **Budget** | 预算追踪和费用分摊 |
| **Collab** | 聊天、投票、协作文档 |
| **Journey** | 跨行程旅行叙事，带条目、贡献者、分享链接 |
| **Packing** | 打包清单管理 |
| **Vacay** | 团队假期日历 — 年度计划、公共假日集成、天数统计 |
| **MCP** | Model Context Protocol — AI 助手工具集成（需管理员启用） |
| **Memories** | 照片记忆 — Immich / Synology Photos 集成 |
| **Booking Import** | 预订自动导入（KDE KItinerary） |

---

## 4. 技术架构深度分析

### 4.1 整体架构

```
┌─────────────────────────────────────────────────────────┐
│                      Docker Container                     │
│                                                           │
│  ┌───────────────────┐    ┌────────────────────────────┐ │
│  │   React 19 PWA    │    │     NestJS 11 Server       │ │
│  │   (Vite 8)        │◄──►│     (TypeScript)           │ │
│  │                   │    │                            │ │
│  │  ┌─────────────┐  │    │  ┌──────────────────────┐  │ │
│  │  │ Zustand     │  │    │  │ @trek/shared (Zod)   │  │ │
│  │  │ IndexedDB   │  │    │  ├──────────────────────┤  │ │
│  │  │ Dexie       │  │    │  │ WebSocket Server     │  │ │
│  │  │ Leaflet     │  │    │  ├──────────────────────┤  │ │
│  │  │ Mapbox GL   │  │    │  │ MCP Server (150+)    │  │ │
│  │  │ Tailwind    │  │    │  ├──────────────────────┤  │ │
│  │  │ vite-pwa    │  │    │  │ Scheduler (Cron)     │  │ │
│  │  └─────────────┘  │    │  └──────────────────────┘  │ │
│  └───────────────────┘    │           │                 │ │
│                            │    SQLite (better-sqlite3) │ │
│                            │    WAL Mode               │ │
│                            └────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

### 4.2 三层工作区结构

```
TREK/
├── client/          # React 19 前端
│   ├── src/
│   │   ├── components/    # Admin, Budget, Collab, Maps, Trip...
│   │   ├── api/           # HTTP client, WebSocket, OAuth scopes
│   │   └── App.tsx        # 路由、认证、暗色模式、PWA
│   ├── package.json       # Vite 8, Tailwind 3, Zustand, Dexie
│   └── e2e/               # Playwright 端到端测试
├── server/          # NestJS 11 后端
│   ├── src/
│   │   ├── nest/          # 30+ NestJS 模块
│   │   ├── mcp/           # MCP Server (StreamableHTTP)
│   │   ├── services/      # 50+ 业务服务
│   │   ├── middleware/    # 认证、幂等、MFA
│   │   └── db/            # SQLite 数据库层
│   └── package.json       # better-sqlite3, ws, zod, @modelcontextprotocol/sdk
└── shared/          # @trek/shared 共享包
    └── src/
        ├── i18n/          # 20 语言翻译
        └── **/            # Zod Schema 定义（trip, place, budget...）
```

### 4.3 关键技术决策

#### 4.3.1 Strangler Fig 迁移模式
项目经历了从 Express 到 NestJS 的完整迁移。NestJS 服务通过 Thin Wrapper 模式封装旧有业务逻辑，实现渐进式重构。核心注释："*Thin Nest wrapper around the existing service — behaviour is unchanged.*"

**优点**：降低迁移风险，保持业务逻辑稳定性  
**当前状态**：Express 已完全退役，所有路由统一在 NestJS 模块中

#### 4.3.2 SQLite 选择
以 better-sqlite3 作为数据库，采用 WAL 模式（Write-Ahead Logging）：

**选择理由：**
- 无需额外数据库服务，降低部署门槛
- 备份即复制文件
- 旅行规划数据量不需要 PostgreSQL 级别
- 通过 Proxy 模式实现数据库重初始化支持（导入备份时）

**数据库 Proxy 模式实现：**
```typescript
// server/src/db/database.ts
// 使用 Proxy 包装 better-sqlite3 实例
// 支持运行时切换数据库文件（备份恢复）
```

#### 4.3.3 共享 Schema 层
`@trek/shared` 包定义所有 Zod Schema，前后端共享数据验证逻辑：

```
shared/src/
├── trip/trip.schema.ts      # 行程 CRUD
├── place/place.schema.ts    # 地点管理
├── budget/budget.schema.ts  # 预算管理
├── packing/packing.schema.ts # 打包清单
├── auth/auth.schema.ts      # 认证
├── collab/collab.schema.ts  # 协作
├── ... (共 20+ Schema 模块)
```

每个 Schema 文件包含：
- Zod 类型定义
- TypeScript 类型导出
- 单元测试（`*.schema.spec.ts`）

#### 4.3.4 离线优先 PWA
前端采用 PWA 架构：

| 技术 | 作用 |
|------|------|
| **Dexie.js** | IndexedDB 封装，离线数据存储 |
| **Service Worker** | 资源缓存、离线访问 |
| **vite-plugin-pwa** | PWA 构建工具链 |
| **Workbox** | 缓存策略管理 |
| **离线编辑** | 离线创建/编辑/删除，联网自动同步 |
| **离线地图** | 预缓存行程区域地图瓦片 |

#### 4.3.5 WebSocket 实时同步
WebSocket 架构要点：

| 特性 | 实现 |
|------|------|
| **认证** | JWT + 一次性 Token（Ephemeral Token） |
| **房间模型** | tripId → Set\<WebSocket\>，按行程分组 |
| **心跳** | 30 秒 Ping/Pong 检测 |
| **速率限制** | 每连接 30 条消息/10 秒 |
| **消息大小** | 最大 64KB |
| **安全** | 令牌与密码版本绑定，密码变更后旧连接自动断开 |
| **来源控制** | 可选 ALLOWED_ORIGINS 白名单 |

#### 4.3.6 Docker 多阶段构建
五阶段构建流程：

```
Stage 1: gosu       → 安全用户切换工具（从源码构建，避免供应链风险）
Stage 2: shared     → @trek/shared 包构建（tsdown 打包）
Stage 3: client     → React 前端构建（Vite）
Stage 4: server     → NestJS 后端构建
Stage 5: production → 运行时镜像（Node 22 + KItinerary Extractor）
```

### 4.4 认证体系

TREK 实现了多层认证：

| 层级 | 方式 | 用途 |
|------|------|------|
| Web UI | JWT (httpOnly Cookie) | Web 应用会话 |
| MCP OAuth 2.1 | `trekoa_` 前缀 Access Token | AI 助手集成（推荐方式） |
| MCP Static | `trek_` 前缀 API Token | MCP 兼容（已弃用） |
| WebSocket | 一次性 Token + JWT | 实时通信 |
| Passkey | WebAuthn | 无密码登录 |
| OIDC | OpenID Connect + PKCE | SSO 单点登录 |

### 4.5 定时任务（Scheduler）

7 个 Cron 任务：

| 任务 | 功能 |
|------|------|
| 自动备份 | 定时数据库备份 |
| 行程提醒 | 出发前提醒通知 |
| 待办提醒 | 待办事项截止提醒 |
| 版本检查 | GitHub 最新版本检测 |
| 幂等性清理 | 过期幂等记录清理 |
| 照片缓存清理 | 过期缓存清理 |
| AirTrail 同步 | 航班数据定时同步 |

### 4.6 NestJS 模块全景

```
server/src/nest/
├── app.module.ts          # 根模块，30+ 子模块注册
├── admin/                 # 管理面板
├── airports/              # 机场搜索
├── assignments/           # 地点分配
├── atlas/                 # Atlas 地图集
├── auth/                  # 认证（JWT/Cookie/Passkey/OIDC/MFA）
├── backup/                # 备份管理
├── booking-import/        # 预订导入（KItinerary）
├── budget/                # 预算管理
├── categories/            # 地点类别
├── collab/                # 协作（聊天/投票/笔记）
├── common/                # 通用拦截器/过滤器
├── config/                # 配置管理
├── database/              # 数据库模块
├── days/                  # 日期管理
├── files/                 # 文件管理
├── health/                # 健康检查
├── integrations/          # AirTrail 集成
├── journey/               # 旅行叙事
├── maps/                  # 地图服务
├── memories/              # 照片记忆（Immich/Synology）
├── notifications/         # 通知管理
├── oauth/                 # OAuth 2.1 服务
├── oidc/                  # OIDC 提供商
├── packing/               # 打包清单
├── photos/                # 照片管理
├── places/                # 地点管理
├── platform/              # 平台路由 + SPA Fallback
├── reservations/          # 预订管理
├── settings/              # 用户设置
├── share/                 # 分享链接
├── system-notices/        # 系统公告
├── tags/                  # 标签管理
├── todo/                  # 待办事项
├── trips/                 # 行程管理
├── vacay/                 # 假期计划
└── weather/               # 天气预报
```

---

## 5. MCP 集成深度解析

### 5.1 架构概述

TREK 内建完整的 MCP（Model Context Protocol）服务器，基于 `@modelcontextprotocol/sdk`，使用 **Streamable HTTP Transport**。AI 助手（Claude Desktop、Cursor 等）可通过标准化协议直接操作 TREK 中的所有旅行数据。

**启用条件**：管理员在 Admin Panel > Addons 页面启用 MCP Addon。

### 5.2 工具体系

共 **150+ 个 MCP 工具**，按领域分组：

| 分组 | 工具数 | 功能范围 |
|------|--------|----------|
| Trips | 12 | 行程 CRUD、成员管理、复制、ICS 导出、分享 |
| Places | 8 | 地点 CRUD、搜索、URL 导入、分类管理 |
| Days | 10 | 日期规划、地点分配、时间设置、参与者管理 |
| Accommodations | 3 | 住宿创建/更新/删除 |
| Transports | 3 | 交通预订（航班/火车/汽车/邮轮） |
| Reservations | 5 | 预订管理、排序、住宿关联 |
| Budget | 5 | 费用管理、分摊设置、结算 |
| Packing | 16 | 打包清单、背包、模板、分配 |
| Day Notes | 3 | 日期笔记 |
| Todos | 7 | 待办事项、类别负责人 |
| Tags | 4 | 标签管理 |
| Notifications | 4 | 应用内通知 |
| Maps/Weather | 6 | 地点搜索、地理编码、天气预报 |
| Airports | 2 | 机场搜索 |
| Collab | 12 | 笔记、投票、聊天 |
| Atlas | 8 | 已访问国家/地区、心愿单 |
| Vacay | 23 | 假期计划全套管理 |
| Journey | 20 | 旅程创建、条目、贡献者、分享 |
| Prompts | 4 | 预构建上下文加载器 |

### 5.3 复合工具（Compound Tools）

将多步骤工作流合并为原子操作：

| 工具 | 原子操作 |
|------|----------|
| `create_and_assign_place` | 创建地点 + 分配到日期 |
| `create_place_accommodation` | 创建地点 + 创建住宿 |
| `create_budget_item_with_members` | 创建预算 + 设置分摊成员 |

### 5.4 OAuth 2.1 认证

完全符合 RFC 标准：

| 标准 | 实现 |
|------|------|
| RFC 9728 | 资源元数据发现 |
| RFC 8414 | 授权服务器元数据 |
| RFC 7591 | 动态客户端注册 |
| RFC 8707 | 资源标识符绑定 |
| PKCE | S256 挑战 |
| DPoP | Demonstration of Proof-of-Possession |

**27 个粒度 Scope**：

```
trips:read/write/delete/share
places:read/write
atlas:read/write
packing:read/write
todos:read/write
budget:read/write
reservations:read/write
collab:read/write
notifications:read/write
vacay:read/write
geo:read
weather:read
journey:read/write/share
```

**会话管理**：
- Access Token TTL：1 小时
- Refresh Token TTL：30 天（轮换机制）
- 每用户最大 20 个并发 MCP 会话
- 速率限制：每用户每分钟 300 请求（可配置）

### 5.5 Prompt 模板

| Prompt | 描述 |
|--------|------|
| `trip-summary` | 加载行程格式化摘要 |
| `packing-list` | 按类别分组的打包清单 |
| `budget-overview` | 格式化预算摘要 |
| `token_auth_notice` | 静态令牌弃用通知 |

### 5.6 AI 上下文指导

MCP 初始化时注入约 80 条行为规则（BASE_MCP_INSTRUCTIONS），包括：
- 数据模型说明
- 关键工作流指导（发现行程、加载上下文、添加地点到行程）
- 访问规则（权限限制）
- 日期和时间格式规范
- Addon 特性说明
- 行为约束（禁止批量销毁操作、trip-summary 优先等）

---

## 6. 数据库设计

### 6.1 表结构全景

```
users                   # 用户（含 OIDC、MFA、密码版本、集成配置）
password_reset_tokens   # 密码重置令牌
webauthn_credentials    # WebAuthn/Passkey 凭证
webauthn_challenges     # WebAuthn 挑战
settings                # 用户设置（键值对）
app_settings            # 应用全局设置
trips                   # 行程
days                    # 每天的日期
places                  # 地点/POI
categories              # 地点类别
tags                    # 用户标签
place_tags              # 地点-标签关联
day_assignments         # 日期-地点分配
assignment_participants # 地点分配参与者
day_accommodations      # 住宿记录
day_notes               # 日期笔记
photos                  # 照片
trip_files              # 行程文件
trip_members            # 行程成员
reservations            # 预订
budget_items            # 预算项目
packing_items           # 打包项目
collab_notes            # 协作笔记
collab_polls            # 投票
collab_poll_votes       # 投票记录
collab_messages         # 聊天消息
vacay_plans             # 假期计划
vacay_plan_members      # 假期计划成员
vacay_user_colors       # 假期用户颜色
vacay_years             # 假期年份
vacay_user_years        # 假期用户年份统计
vacay_entries           # 假期条目
vacay_company_holidays  # 公司假日
vacay_holiday_calendars # 假期日历
addons                  # 附加组件
photo_providers         # 照片提供商
photo_provider_fields   # 照片提供商字段
notifications           # 应用内通知
notification_channel_preferences # 通知渠道偏好
audit_log               # 审计日志
migrations              # 迁移记录
```

**总计：40+ 张表，全部 SQLite，完整外键约束和索引覆盖**

### 6.2 关键设计原则

1. **SQLite WAL 模式**：并发读性能优化
2. **CASCADE 删除**：子表自动级联删除
3. **索引策略**：高频查询字段全覆盖
4. **密码版本**：`password_version` 字段支持密码变更后 JW/WS Token 失效
5. **审计日志**：`audit_log` 表记录所有关键操作

---

## 7. 代码架构分析

### 7.1 Strangler Fig 模式

迁移采用经典的 Strangler Fig（绞杀榕）模式：

- 旧 Express 路由位于 `server/src/routes/`（已退役）
- 新 NestJS 模块位于 `server/src/nest/`
- Nest Controller 调用旧 Service 层（`server/src/services/`）
- Nest Service 通过 Thin Wrapper 封装旧服务逻辑

```typescript
// 典型 Nest Service 模式（以 TripsService 为例）
@Injectable()
export class TripsService {
  // 直接委托给旧有 Service 函数
  list(userId: number, archived: number) {
    return tripSvc.listTrips(userId, archived);
  }
  
  create(userId: number, data: ...) {
    return tripSvc.createTrip(userId, data);
  }
  // ...
}
```

这种设计确保了：
- 业务逻辑稳定性（不重写）
- API 兼容性（路由 1:1 映射）
- 渐进式重构（按模块迁移）

### 7.2 认证服务架构

```
authService.ts (业务逻辑层)
├── 密码哈希 (bcrypt/argon2)
├── JWT 生成/验证
├── MFA (TOTP)
├── Passkey/WebAuthn
├── OIDC 集成
├── 密码重置流程
└── API Token 管理

cookie.ts (会话层)
├── setAuthCookie()
└── clearAuthCookie()

Nest Auth 模块
├── JwtAuthGuard
├── CookieAuthGuard
├── OptionalJwtGuard
├── PasskeyEnabledGuard
├── AdminGuard
├── RateLimitService
└── CurrentUser Decorator
```

### 7.3 MCP 服务架构

```
server/src/mcp/
├── index.ts            # MCP Server 入口、认证验证、速率限制
├── oauthProvider.ts    # OAuth 2.1 Provider 实现
├── resources.ts        # 资源注册器
├── scopes.ts           # Scope 定义与验证
├── sessionManager.ts   # MCP 会话生命周期管理
└── tools/
    ├── _shared.ts      # 共享工具函数
    ├── trips.ts        # 行程工具
    ├── places.ts       # 地点工具
    ├── days.ts         # 日期规划工具
    ├── assignments.ts  # 分配工具
    ├── budget.ts       # 预算工具
    ├── packing.ts      # 打包工具
    ├── reservations.ts # 预订工具
    ├── transports.ts   # 交通工具
    ├── todos.ts        # 待办工具
    ├── tags.ts         # 标签工具
    ├── mapsWeather.ts  # 地图天气工具
    ├── notifications.ts # 通知工具
    ├── collab.ts       # 协作工具
    ├── atlas.ts        # Atlas 工具
    ├── vacay.ts        # Vacay 工具
    ├── journey.ts      # Journey 工具
    └── prompts.ts      # Prompt 模板
```

### 7.4 路由平台化

`server/src/nest/platform/platform.routes.ts` 统一管理所有 NestJS Controller 路由注册，支持 SPA Fallback（`SpaFallbackFilter`），确保前端路由正常工作。

### 7.5 全局过滤器

| 过滤器 | 作用 |
|--------|------|
| `TrekExceptionFilter` | 统一异常处理，转换为 API 错误响应 |
| `SpaFallbackFilter` | 404 路由回退到 SPA index.html |
| `ZodValidationPipe` | Zod Schema 自动验证请求体 |

### 7.6 中间件层

| 中间件 | 作用 |
|--------|------|
| `auth.ts` | JWT/Cookie 认证中间件 |
| `globalMiddleware.ts` | 全局中间件（安全头、CORS 等） |
| `idempotency.ts` | 幂等操作支持 |
| `mfaPolicy.ts` | MFA 强制执行策略 |
| `tripAccess.ts` | 行程访问权限验证 |
| `validate.ts` | 请求验证中间件 |

---

## 8. 社区反馈与评价

### 8.1 Scheepy Blog（2026-03-30）

**文章标题**：*TREK：一個讓揪團旅行不再崩潰的 Self-Hosted 旅行規劃器*

**核心观点**：
- 定位清晰：解决团体旅行中信息分散的痛点
- PWA 是聪明的设计决策："不需要说服五個朋友去 App Store 下載一個他們一年用一次的 App"
- SQLite 选择正确："旅行规划的資料量根本不需要 PostgreSQL 那個等級的能力"
- 功能完成度高："不是一個週末 side project，這是一個認真在做的產品"
- 建议使用场景：Home Lab 玩家、NAS 用户、团体旅行组织者
- AGPL-3.0 授权合理：保护社区贡献者

**评价等级**：5/5

### 8.2 AIBit（2026-04-03）

**文章标题**：*TREK：自托管旅行规划器，支持实时协作*

**核心观点**：
- 强调隐私优势："厌倦了将旅行数据锁定在订阅制背后的云端应用"
- 一键部署吸引人："只需一个 Docker 命令即可部署"
- 功能对比 Wanderlog："想要 Wanderlog 般功能而无订阅"
- 指出 3.3K GitHub 星标（当时）
- 强调 PWA 和离线能力

**定位**：功能发现型文章，为开源探索者介绍 TREK

### 8.3 GithubAwesome（2026-03-29）

**核心观点**：
- 切入痛点精准："Group trip planning always collapses into a Google Sheet nobody updates"
- PWA 无应用商店安装是核心差异化
- 实时协作是必需而非加分项

### 8.4 社区讨论要点

- 用户关注自托管部署门槛（Docker 要求）
- 对于非技术人员，"什么是 Docker"仍然是障碍
- PWA 方式受到广泛好评
- 功能完整度超出预期
- 部分用户期待移动端原生 App（但项目明确选择 PWA 路线）

### 8.5 竞品对比总结

| 维度 | TREK | Wanderlog | TripIt | Google Sheets |
|------|------|-----------|--------|---------------|
| 自架/数据主权 | ✅ | ❌ | ❌ | ❌ |
| 实时协作 | ✅ | ✅ (有限) | ✅ (有限) | ✅ (有延迟) |
| 拖拽行程 | ✅ | ✅ | ❌ | ❌ |
| 预算追踪 | ✅ | ✅ | ❌ | 手动 |
| 离线 PWA | ✅ | ✅ | ✅ | ❌ |
| 打包清单 | ✅ | ❌ | ❌ | 手动 |
| AI 集成 (MCP) | ✅ | ❌ | ❌ | ❌ |
| 免费 | ✅ | 部分 | 部分 | ✅ |
| 费用分摊 | ✅ | ✅ | ❌ | ❌ |
| 多语言 | 20 种 | 多种 | 多种 | 51 种 |

**TREK 的独特优势**：
1. **数据主权**：唯一全功能自架方案
2. **MCP 集成**：唯一支持 AI 工具调用的旅行规划器
3. **无订阅限制**：完全免费，无功能限制
4. **PWA 零安装成本**：无需 App Store
5. **功能广度**：覆盖旅行规划全链路

**TREK 的劣势**：
1. **部署门槛**：需要 Docker/服务器知识
2. **用户基数**：远小于 Wanderlog 等商业产品
3. **移动体验**：PWA 在某些平台可能不如原生 App
4. **维护负担**：自架需要用户自己维护和备份

---

## 9. 总结与展望

### 9.1 项目评价

**技术评分**：★★★★★（5/5）
- 架构设计优秀（Strangler Fig 迁移、三层工作区、共享 Schema）
- 代码质量高（TypeScript、Zod 验证、完整测试）
- 工程实践规范（Docker 五阶段构建、WAL 数据库、WebSocket 心跳）
- MCP 集成深度惊人（150+ 工具、OAuth 2.1、27 个 Scope）

**功能评分**：★★★★★（5/5）
- 功能全面覆盖旅行规划全链路
- 实时协作体验优秀
- PWA 离线支持完善
- 20 种语言国际化
- 插件化架构可扩展

**社区评分**：★★★★☆（4/5）
- 作者响应迅速，维护积极
- 开源社区活跃度高
- 版本迭代稳定（约每周一版）
- 文档完善（MCP.md 详尽、80+ Wiki 页面）

### 9.2 关键亮点

1. **MCP 集成**：150+ AI 可调用工具，使其成为第一个完整的 AI-Native 旅行规划器
2. **PWA 策略**：零安装成本，解决了团体旅行中"说服所有人下载 App"的痛点
3. **自架友好**：一行 Docker 命令即可部署，SQLite 零依赖
4. **数据主权**：敏感旅行数据完全由用户掌控，无 SaaS 锁定
5. **插件化架构**：Addon 系统保持核心精簡，按需扩展

### 9.3 适用场景

| 场景 | 适合度 | 说明 |
|------|--------|------|
| 团体旅行组织者 | ★★★★★ | 最佳场景，协作+预算+打包全覆盖 |
| Home Lab 玩家 | ★★★★★ | 零成本部署，充分利用 NAS/服务器 |
| 数字游民 | ★★★★☆ | PWA 离线+多货币+多语言 |
| 旅行社 | ★★★★☆ | 自架控制+多行程管理 |
| 个人旅行 | ★★★☆☆ | 功能过剩，Google Maps 可能足够 |
| 非技术人员 | ★★☆☆☆ | Docker 部署是门槛 |

### 9.4 发展趋势

基于当前开发动态和 PR 列表，未来可能的发展方向：

1. **LLM 预订提取** — AI 自动从邮件中解析预订确认并创建行程条目（已有 PR）
2. **ICS 日历 Feed** — 实时日历订阅输出（已有 PR）
3. **MCP 生态深化** — 更多 AI 集成能力，Agent 自主旅行规划
4. **移动端优化** — PWA 体验持续打磨
5. **更多集成** — 酒店、租车、活动预订平台接入
6. **社区模板** — 行程模板市场和社区贡献机制

### 9.5 最终总结

TREK 是目前 **最完整、最工程化的自托管旅行规划器**。它不是一个 MVP 或概念验证，而是一个经过精心设计、持续迭代、功能全面的产品级应用。其 MCP 集成将 AI 助手的能力与旅行数据深度结合，开创了"AI-Native 自架应用"的新范式。

对于具有自架能力的用户，TREK 提供了媲美甚至超越商业旅行规划器的功能，同时保有完全的数据主权。对于不具备自架能力的用户，社区已有公开 Demo 实例可供体验。

**一句话总结**：TREK 是 Wanderlog 的开源自架替代方案，但不止于此——它是旅行规划器的 AI 时代答案。

---

*报告完成于 2026-06-27 | 数据来源：GitHub API、社区文章、源码分析*