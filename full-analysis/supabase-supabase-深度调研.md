# 🔬 supabase/supabase — 全方位深度调研

> 调研日期：2026-09-01 ｜ 星标：108,651 ⭐ ｜ Fork：13,685 ｜ 语言：TypeScript（含大量 Go/Elixir/Rust 服务）｜ 协议：Apache-2.0 ｜ 默认分支：master ｜ 实时状态：极活跃（pushed 2026-08-31）

## 📌 项目定位

`supabase/supabase` 是 **"开源的 Firebase 替代"——以 Postgres 为唯一真相源的后端开发平台**。它不重新发明数据库，而是把 Postgres 之上的 Auth、REST、Realtime、Storage、Edge Functions、向量检索全部用开源组件"组装"成一个开箱即用的后端，并配一个 Next.js  dashboard（Studio）。

> 核心判断：Supabase 的本质不是"一个产品"，而是**一套围绕 Postgres 的后端服务体系 + 一个统一控制面**。它的护城河是"你永远拥有底层 Postgres，随时可以裸奔跑路"，而不是把数据锁进私有存储。

## 🏆 项目亮点（差异化）

1. **Postgres 是唯一真相源**：所有能力（Auth/REST/Realtime/Storage/向量）都直接读写同一份 Postgres，没有独立的状态孤岛，迁移/备份/SQL 都标准化。
2. **开源组件拼装，而非黑盒**：GoTrue（Auth）、PostgREST（REST）、Realtime（Elixir）、Storage API（S3 兼容）、Kong（网关）、pg-meta（管理）、Supavisor（连接池）——每个都能单独理解、单独替换。
3. **行级安全（RLS）即权限模型**：权限直接写进 Postgres 的 RLS 策略，数据库层兜底，而不是在应用层各自实现，安全边界清晰。
4. **AI / 向量原生**：pgvector + embeddings + `ai-commands`，把"语义检索/向量库"做成 Postgres 的一等能力，AI 应用零额外基础设施。
5. **自托管与云等价**：`docker/docker-compose.yml` 一键拉起完整栈，本地开发环境和云端架构一致，没有"云上魔法"。

## 🏗️ 核心架构（克制版）

这是典型的 **"控制面仓库 + 多服务后端"**：本仓库主要是 Studio（dashboard）、docker 自托管栈、以及若干前端/工具 packages；核心客户端 SDK（`supabase-js`、`auth-js`/`gotrue`、`realtime-js`、`storage-js`、`postgrest-js`）在独立仓库，但都通过本仓库的 Studio 与 docker 栈串起来。

`docker/docker-compose.yml` 暴露的真实服务矩阵（**这是 Supabase 架构最该记住的一张图**）：

```
            ┌─────────────────────────────────────────┐
   浏览器 → │ Kong (api-gw)  统一入口 / 路由 / 限流      │
            └──────┬────────┬────────┬────────┬────────┘
                   │        │        │        │
                ┌──▼──┐  ┌──▼───┐ ┌──▼────┐ ┌─▼──────┐
                │auth │  │ rest │ │realtime│ │storage │   ← 全部读写同一 Postgres
                │GoTrue│ │Postg-│ │(Elixir)│ │(S3兼容)│
                └─────┘  │REST │ └────────┘ └────────┘
                         └──┬───┘
                    ┌───────▼────────┐   ┌──────────┐  ┌──────────┐
                    │  db (Postgres) │   │ meta     │  │ imgproxy │
                    │  + pgvector    │   │(pg-meta) │  │(图片处理) │
                    └────────────────┘   └──────────┘  └──────────┘
                 ┌──────────┐  ┌──────────┐  ┌──────────┐
                 │functions │  │supavisor │  │db-config │  ← Edge Functions(Deno)/连接池/配置
                 └──────────┘  └──────────┘  └──────────┘
                              └──── Studio (Next.js dashboard) ────┘
```

`packages/` 关键内部包（本仓库内）：`pg-meta`（Postgres 元数据客户端）、`ui` / `ui-patterns`（dashboard 组件）、`ai-commands`、`generator`、`common`、`config`、`marketing`。

## 💡 应用场景与启发（重点）

- **"别自建后端"的默认选项**：需要 Auth + 数据库 + 文件 + 实时 + 向量，又不想逐个接 SDK 时，Supabase 把这一整套拼图一次给齐，尤其适合 AI 应用（pgvector 直接当向量库）。
- **RLS 作为单一权限真理**：把"谁能读/写哪行"下沉到数据库策略，比在十几个微服务里各写一遍鉴权更可靠、更易审计。做多租户/协作类产品时强烈建议借鉴。
- **"开源组件拼装"的可替换架构**：每个能力都是独立开源项目，哪个不满意（如想换连接池、想换网关）可单独替换，没有全家桶绑架。自研平台时这是一种抗锁定、易演进的范本。
- **自托管 = 生产等价**：docker 栈和云端同构，本地就能完整复现线上行为，CI/调试不再"线上才能测"。

## 🧠 源码深度解读（3 个核心模块）

### 1) 网关与路由 — `docker/docker-compose.yml` 的 `api-gw` (Kong)
所有客户端请求先到 Kong，再按路径分发到 auth/rest/realtime/storage：

```yaml
services:
  api-gw:      # Kong：统一入口、路由、限流
  auth:        # GoTrue：JWT + OAuth + RLS 用户
  rest:        # PostgREST：把 Postgres 表自动暴露成 REST（带 RLS）
  realtime:    # Elixir：基于 Postgres 逻辑复制的实时变更广播
  storage:     # S3 兼容对象存储网关
  db:          # Postgres（含 pgvector）
```

关键认知：**rest 服务就是 PostgREST**——你建表即自动获得 CRUD API，权限由 RLS 决定，不需要手写 controller。

### 2) 权限模型 — Postgres Row Level Security
Supabase 的"用户只能看自己的数据"不是应用层 if 判断，而是数据库策略：

```sql
create policy "用户只能读自己的 todo"
  on todos for select
  using (auth.uid() = user_id);   -- auth.uid() 来自 GoTrue 签发的 JWT
```

JWT 中的 `sub`（用户 ID）直接进入 SQL 上下文，RLS 在数据库层强制生效，绕过应用层也无效。

### 3) 客户端聚合 — `supabase-js`（独立仓库，本仓库引用）
前端一个 client 串起所有能力，底层是各独立 SDK：

```ts
import { createClient } from "@supabase/supabase-js";
const sb = createClient(URL, ANON_KEY);
await sb.from("todos").select();          // → PostgREST
await sb.auth.signInWithOAuth({provider}); // → GoTrue
await sb.channel("room").on("broadcast").subscribe(); // → Realtime
```

`supabase-js` 本身很薄，真正的逻辑在 `postgrest-js / auth-js / realtime-js / storage-js`，职责清晰、可单独测试。

## 🌐 全网口碑画像

- **正面**：开源 Firebase 替代的事实标准；pgvector 让它在 AI 浪潮里吃尽红利（大量 AI 原型/产品直接拿它当后端）；文档与 DX 口碑极好；自托管社区活跃。
- **中性/风险**：完整自托管对运维要求不低（十几个服务、Kong/RLS/Supavisor 都要懂）；部分高级能力（如 Realtime 大规模、Auth 复杂流）调优有门槛；云端版存在"Supabase 特有功能"带来的轻度绑定（但底层 Postgres 永远可导出，跑路成本远低于 Firebase）。
- **与 Firebase 对比口碑**：开发者普遍偏好 Supabase 的"SQL 可控 + 开源 + 可自托管"，但 Firebase 在"零后端心智 + 谷歌生态"上仍占优。

> 数据来源：GitHub 元数据（108k⭐、13k fork、Apache-2.0、每日 push）、`docker-compose.yml` 服务矩阵真实抓取、`packages/` 结构、公开社区长期反馈。未编造具体评测数字。

## ⚔️ 竞品对比

| 方案 | 内核 | 优势 | 风险/短板 |
|---|---|---|---|
| **Supabase** | Postgres | 开源、SQL 可控、可自托管、pgvector/AI 原生 | 自托管运维重、部分功能 Supabase 绑定 |
| **Firebase** | 私有 NoSQL + 专有服务 | 零后端心智、谷歌生态、实时强 | 闭源、NoSQL 锁定、导出难、成本不可控 |
| **Appwrite** | 自有服务 | 轻量、容器友好、API 清晰 | 生态/规模不如 Supabase、SQL 非核心 |
| **PocketBase** | SQLite 内嵌 | 单文件、极简、自带 UI | 不适合大规模分布式、生态小 |
| **Nhost** | Postgres（同路线） | 也是 PG + GraphQL | 规模/社区远小于 Supabase |

## 🎯 核心研判

- **采用建议**：AI 应用 / 中小团队后端 / 需要快速上线且保留"随时裸奔"能力的项目 → Supabase 是首选；纯前端无 SQL 意愿且深度谷歌生态 → 考虑 Firebase。
- **最大风险**：自托管不是"一条命令"，RLS 写错 = 数据裸奔，务必把权限策略当代码审查；云端高级功能会带来轻度绑定，关键数据保持可导出。
- **借鉴价值**：① RLS 作为单一权限真理；② 开源组件拼装抗锁定；③ 自托管与生产同构。这三点对任何后端平台设计都成立。
- **一句话**：Supabase 的护城河不是技术多新，而是"把 Postgres 之上成熟的开源组件，拼装成开发者体验极佳、且永远可跑路的后端平台"。

## 📂 关键文件路径速查

- `docker/docker-compose.yml` — 完整自托管服务矩阵（架构总图）
- `studio/` — Next.js 控制面（dashboard）
- `packages/pg-meta/` — Postgres 元数据客户端
- `packages/ui` `packages/ui-patterns` — dashboard 组件库
- `packages/ai-commands` `packages/generator` — AI / 代码生成工具
- 客户端 SDK（独立仓库，被本平台引用）：`supabase/js`、`supabase/auth-js`、`supabase/realtime-js`、`supabase/storage-js`、`supabase/postgrest-js`

## 🧪 研究方法与数据来源

- GitHub API 元数据（stars/forks/license/pushed_at/open_issues/topics 含 postgres/postgrest/realtime/pgvector）
- `docker/docker-compose.yml` 服务矩阵真实抓取（studio/api-gw/auth/rest/realtime/storage/imgproxy/meta/functions/db/supavisor/db-config/deno-cache）
- `packages/` 目录结构真实抓取
- 公开社区长期反馈（非编造评测数字）
