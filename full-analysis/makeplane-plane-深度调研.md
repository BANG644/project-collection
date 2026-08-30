# makeplane/plane — 深度调研

> 调研日期：2026-08-31（重写升级；初版 2026-08-21）｜ 星标：58,557 ⭐ ｜ 协议：AGPL-3.0 ｜ 语言：TypeScript / Python ｜ **默认分支：`preview`（不是 main）** ｜ 版本：v1.4.2 ｜ 仓库规模：5,228 文件

## 一、项目定位（一句话）

Plane 是一个完全开源、可自托管的**现代项目管理平台**，定位为 Jira / Linear / Monday / ClickUp 的一体化替代；工程上它是一个**由 6 个应用 + 15 个共享包组成的 pnpm + Turborepo 单仓**，前端 React Router v7 + Vite + MobX，后端 Django REST Framework，另有一个独立的 Yjs 实时协作服务。

## 二、项目亮点（差异化）

- **默认分支是 `preview` 而非 `main`** —— 这不是小事：**社区看到的、贡献 PR 的基线是"下一个版本"**。发布流才把 preview 合入稳定分支。想 clone 部署生产的人如果不注意会拿到未发布代码。
- **6 个独立应用，而非"前端 + 后端"两件套**：`web`（主应用）、`api`（Django）、`space`（公开分享页）、`admin`（实例管理后台）、`live`（实时协作服务）、`proxy`（反代）。**其中 `live` 是独立的 Node/Express + Hocuspocus + Yjs 服务** —— 文档协同不是塞在主 API 里，而是单独进程 + Redis 广播，可独立扩缩容。
- **自研设计系统 `@plane/propel`（397 文件）**：不是简单的组件库，而是带**逐组件 subpath exports** 的完整设计系统（`./button`、`./charts/area-chart`、`./charts/tree-map`…），内置 area/bar/line/pie/radar/scatter/tree-map 七种图表封装（底层 recharts）。这是 Plane 能在 web / space / admin 三个应用间保持视觉一致的基础。
- **前端工具链已切到 Rust 系**：根 `package.json` 用 **oxlint + oxfmt** 替代 ESLint + Prettier（lint-staged 里直接 `pnpm exec oxlint --fix --deny-warnings`），Node 要求 `>=22.22.0`，依赖版本统一走 pnpm 的 `catalog:` 协议。**在一个 5000 文件、1700 个包内文件的仓库里，lint 速度是生产力问题**，这个迁移动机很实在。
- **状态管理是 MobX，不是 Redux/Zustand**：`apps/web/core/store/` 有 100 个文件，配合 `mobx-react` + `mobx-utils`，数据获取用 `swr`。**"MobX 领域模型 + SWR 远程同步"** 这套组合在大型 B 端应用里比 Redux 更省样板代码，是 Plane 前端能承载 1394 个组件文件仍可维护的关键选择。
- **部署形态覆盖到"离线机房"级别**：`deployments/` 提供 AIO（单容器 + supervisor 跑全栈）、CLI 安装器（`install.sh` + 交互式管理）、Kubernetes、Docker Swarm 四种，**并且有 `restore-airgapped.sh`（气隙环境恢复）和 `migration-0.13-0.14.sh`（跨版本数据迁移脚本）** —— 这两个文件的存在说明它真的被部署在无外网的企业内网里。
- **i18n 是最大的单个包（553 文件）**，比设计系统还大。

## 三、核心架构（克制呈现）

### 3.1 仓库拓扑（实抓文件数）

```
apps/          3,454 文件
├── web    2,344   主应用：React Router v7 + Vite + MobX + SWR
├── api      709   Django + DRF（唯一 Python 应用）
├── space    213   公开分享站（deploy board 渲染）
├── admin    128   实例级管理后台（God mode）
├── live      56   ★ Hocuspocus + Yjs 实时协作服务（Express + ioredis）
└── proxy      4   反向代理
packages/      1,700 文件
├── i18n            553   多语言资源（最大包）
├── propel          397   ★ 设计系统 + 图表（subpath exports）
├── editor          238   ★ Tiptap + Yjs 协作编辑器
├── types           123   跨端类型契约
├── ui              101 / utils 97 / constants 62 / services 59
├── shared-state     21   跨应用共享状态
├── codemods         11   ★ 代码迁移脚本（大重构的产物）
└── hooks 9 / decorators 9 / logger 8 / typescript-config 7 / tailwind-config 5
deployments/      22   aio / cli / kubernetes / swarm
turbo.json + pnpm-workspace.yaml + patches/
```

### 3.2 后端：`apps/api/plane/` 的模块切分（实抓）

```
db/            180   模型 + 迁移（最重的目录）
app/           112   视图层（按域分子包）
tests/          73   pytest（配 pytest.ini + run_tests.py）
utils/          70
api/            49   ★ 对外公开 API（与内部 app/ 分离）
authentication/ 47   ★ 独立认证子系统
license/        37   ★ 许可/版本校验
bgtasks/        33   Celery 异步任务
space/          29   公开分享的后端
middleware/ 5 · settings/ 8 · seeds/ 8 · analytics/ 2 · throttles
celery.py · wsgi.py · asgi.py
```

三个设计值得注意：
1. **`app/`（内部视图）与 `api/`（对外 API）物理分离** —— 内部前端调的接口和第三方集成用的接口是两套代码路径，避免"为了给客户开 API 而破坏内部接口"。
2. **`authentication/` 独立成 47 文件的子系统**，且 `db/models/social_connection.py` + `session.py` 单独建模，说明 SSO / OAuth / 多方式登录是一等公民而非插件。
3. **`license/` 存在于开源仓库里** —— 这是"开源核心 + 商业版"双轨的技术痕迹：社区版也要跑许可校验代码路径（`deployments/*/community/` 的命名同样印证存在非 community 版本）。

### 3.3 数据模型全景（`apps/api/plane/db/models/` 实抓清单）

```
workspace · project · issue · issue_type · cycle · module · state · label · estimate
view · page · description · draft · intake · sticky · favorite · recent_visit
analytic · asset · notification · webhook · api · deploy_board · device · session
user · social_connection · exporter · importer/{github, slack}
```

**从模型名就能读出产品边界**：
- `cycle`（迭代）+ `module`（模块）+ `state`（状态机）+ `estimate`（估点）= 完整敏捷模型；
- `intake`（需求收件箱）+ `draft`（草稿）+ `sticky`（便签）= 从"想法"到"工作项"的前置漏斗，这是 Jira 没有而 Linear 有的东西；
- `issue_type` 独立成模型 = 支持自定义工作项类型（企业级需求）；
- `deploy_board` = 把某个视图公开发布成只读页面（对应 `apps/space`）；
- `recent_visit` + `device` = 用户行为与多端会话；
- `importer/{github,slack}` 已建模但只有两个 —— **迁移入口是短板，Jira/Asana 导入不在内置模型里**。

### 3.4 实时协作链路（本次调研新增，初版完全缺失）

```
packages/editor  ──  @tiptap/core + @tiptap/extension-collaboration + @hocuspocus/provider
                             │  (Yjs CRDT over WebSocket)
                             ▼
apps/live        ──  @hocuspocus/server + express-ws
                     ├─ extensions/database.ts   持久化到 Django API
                     ├─ extensions/redis.ts      多实例广播（ioredis）
                     ├─ extensions/title-sync.ts + title-update/  标题防抖同步
                     ├─ extensions/force-close-handler.ts  强制断连处理
                     ├─ controllers/collaboration.controller.ts
                     ├─ controllers/document.controller.ts
                     ├─ controllers/pdf-export.controller.ts   ★ 服务端 PDF 导出
                     └─ lib/auth.ts + auth-middleware.ts       复用主站鉴权
```

这一层是 Plane 架构里最"重"也最容易被低估的部分：**Pages 功能（内置文档）不是富文本存数据库，而是完整的 CRDT 协同**。`extensions/redis.ts` 让 live 服务可以多副本部署，`title-update/debounce.ts` 单独处理标题这种高频小字段的同步节流。

## 四、应用场景与启发（重点）

- **场景 1 — 替代 Jira 且要数据主权**：AGPL + 自托管 + 气隙恢复脚本，适合政企、金融、军工等不能上公有云的团队。CLI 安装器把门槛降到"跑一个 sh"。
- **场景 2 — 内部工具/自研 PM 系统的现成底座**：`intake → draft → issue → cycle/module → view/analytics` 这条链路已经建模完毕，比从零设计工作项模型省几个月。fork 后改的是 UI 与流程，不是数据模型。
- **场景 3 — 抄它的前端工程方案**：如果你要做一个 1000+ 组件、多应用共享设计系统的 B 端产品，Plane 是**目前开源里最完整的参考实现**（见下方启发）。
- **场景 4 — 白嫖 `apps/live`**：需要"多人协同编辑文档 + 服务端持久化 + 多实例广播 + 鉴权复用主站"的团队，可以直接把 `apps/live` 当模板改——它只有 56 个文件，边界清晰，Hocuspocus 扩展写法齐全。

**核心启发（五条，都是可直接迁移的工程决策）**：

1. **协同编辑必须独立成服务**。CRDT 服务的负载特征（长连接、高频小消息、内存态文档）和 REST API 完全不同，塞在一起会互相拖垮。Plane 的做法：独立进程 + Redis 广播 + 通过 `extensions/database.ts` 回写主 API，鉴权中间件复用主站 —— **独立部署但不独立造用户体系**，这是正确的切法。
2. **设计系统要做 subpath exports，不要单一 barrel 入口**。`@plane/propel` 的 `exports` 逐组件声明（`./button`、`./charts/area-chart`），使用方 import 一个按钮不会拖进整个图表库。在多应用共享的场景下，这直接决定各应用的产物体积。
3. **仓库里养一个 `codemods` 包**。Plane 的 `packages/codemods`（11 文件）说明它经历过需要机械化改写全仓库的重构（Next.js → React Router 的迁移痕迹）。**大型重构的正确姿势是写 codemod 而不是手改 1394 个组件文件**，而且把 codemod 留在仓库里，后来者能看懂历史。
4. **对外 API 与内部 API 物理分离**（`plane/api/` vs `plane/app/`）。一旦混在一起，任何内部重构都可能破坏第三方集成契约。分开之后内部可以自由演进，对外那 49 个文件才是要保稳定的部分。
5. **工具链换成 Rust 系是有明确收益门槛的**。5000 文件规模下 oxlint/oxfmt 的速度差异从"体感"变成"CI 分钟数"。反过来说，小项目为此付迁移成本不值得——**这个决策的触发条件是仓库规模，不是技术时髦**。

## 五、源码深度解读（核心模块）

### 5.1 `apps/live` — Hocuspocus 扩展的教科书用法

`apps/live/src/extensions/` 每个文件对应一个真实的生产问题：

| 扩展 | 解决什么 |
|---|---|
| `database.ts` | 文档持久化：Yjs 二进制状态如何落到 Django 侧 |
| `redis.ts` | 多实例同步：ioredis 做 pub/sub，让 N 个 live 副本共享同一文档房间 |
| `logger.ts` | 连接/断开/同步事件的可观测性 |
| `title-sync.ts` + `title-update/{debounce,title-update-manager,title-utils}.ts` | **标题是既在文档里又在列表里的字段**，高频改动需要防抖 + 双向一致，单独一个子目录处理 |
| `force-close-handler.ts` | 权限被撤销 / 文档被删时强制踢掉在线连接 |

`controllers/pdf-export.controller.ts` 也在这个服务里 —— **合理，因为要导出的是内存中的最新协同状态，而不是数据库里可能滞后的快照**。这个选址决策比"在后端加个导出接口"更正确。

### 5.2 `apps/web/core/` — 1679 文件如何不失控

```
components/  1394   按功能域组织
hooks/        116
store/        100   ★ MobX 领域 store
services/      53   ★ API 客户端层
lib/           13 · layouts/ 3
```

模式是：**`services/`（纯 HTTP 客户端）→ `store/`（MobX 可观察领域模型）→ `components/`（观察者视图）**，远程数据的新鲜度由 `swr` 负责。三层职责清晰，所以 1394 个组件文件不会互相纠缠。

值得注意的是 `apps/web` 与 `apps/space`、`apps/admin` 三者共享 `packages/{propel,ui,editor,types,services,constants,utils,shared-state}`。**`packages/services`（59 文件）独立于 `apps/web/core/services`（53 文件）** —— 前者是三应用共用的 API 客户端，后者是主应用私有的。这种"共享层 vs 私有层"的显式区分是多应用单仓不腐化的关键。

### 5.3 `packages/editor` — Tiptap 扩展清单即产品功能清单

从 `package.json` 依赖能直接读出 Pages 的能力边界：`extension-collaboration`（协同）、`extension-mention`（@提及）、`extension-emoji`、`extension-image`、`extension-task-list` + `task-item`（可勾选清单）、`extension-character-count`、`extension-placeholder`、`extension-blockquote`、`extension-heading`、`extension-list-item`… 配 `@hocuspocus/provider` 作为传输层。

**启发**：用 Tiptap 这类"扩展即功能"的编辑器框架时，`package.json` 的依赖列表天然就是功能矩阵文档。要评估一个开源产品的编辑器能力，读依赖比读文档快。

### 5.4 `deployments/` — 被低估的交付工程

```
aio/community/         Dockerfile + supervisor.conf + build.sh + start.sh
                       ← 单容器跑全栈（supervisor 托管多进程），适合小团队/演示
cli/community/         install.sh + docker-compose.yml + variables.env
                       + restore.sh + restore-airgapped.sh + migration-0.13-0.14.sh
                       + images/*.png（安装向导截图）
kubernetes/community/   K8s 部署
swarm/community/        swarm.sh
```

三个细节：
- **`supervisor.conf` 的 AIO 模式**：明知"一个容器跑多进程"违反 Docker 最佳实践，仍然提供——因为真实用户里有大量"我只想一条命令跑起来"的人。**工程正确性与采用率的取舍，这里选了后者，并且隔离在独立目录不污染标准部署。**
- **`restore-airgapped.sh`**：气隙环境恢复。没有真实的内网客户不会有人写这个脚本。
- **`migration-0.13-0.14.sh`**：为某次特定版本升级写的专用迁移脚本 + `images/migrate-error.png` 截图。**说明那次升级坑了很多人，团队用文档+脚本+截图兜住了。** 这种"为一次历史事故留下的资产"是判断项目成熟度的可靠信号。

## 六、全网口碑（真实信号）

- **规模与增速**：58,557 ⭐（初版调研 2026-08-21 记录 56,372，**10 天 +2,185**），项目管理开源品类第一梯队。
- **工程活跃度硬证据**：v1.4.2 版本号、默认分支 `preview` 上有 5,228 文件、`apps/api/tests` 73 个测试文件 + pytest 配置、`.github/` 15 个工作流文件、`.claude/` 5 个文件（团队已把 AI 辅助开发纳入仓库约定）。
- **技术栈现代化程度**（同类开源产品少见）：React Router v7（framework mode，`react-router typegen`）、Vite、Node ≥22.22、pnpm catalog 协议、oxlint/oxfmt、Turborepo、`react-doctor` 诊断命令。
- **争议与短板（基于代码事实，非道听途说）**：
  - **AGPL-3.0 对闭源商业化是硬约束**：修改后对外提供服务须开源。`packages/propel/package.json` 里 `"license": "AGPL-3.0"` + `"private": true` 说明设计系统也不打算单独开放给外部复用。
  - **迁移入口薄弱**：`db/models/importer/` 只有 `github.py` 和 `slack.py`。**从 Jira / Asana / Trello 迁入的官方路径在开源仓库里不存在**（可能是商业版能力）。这是评估"能否真正替代 Jira"时最该核实的一点。
  - **`license/`（37 文件）的存在** + `deployments/*/community/` 命名 = 开源版与商业版存在功能分界。选型时必须确认目标功能属于哪一侧。
  - **自托管运维不轻**：完整栈 = PostgreSQL + Redis + Django(+Celery) + 3 个前端应用 + live 服务 + proxy。AIO 单容器可缓解演示场景，但生产环境仍需要会运维的人。
  - **默认分支 `preview` 的陷阱**：直接 `git clone` 拿到的是预发布代码，生产部署应按 release tag 或官方 docker 镜像走。

## 七、竞品对比 + 核心研判

| 维度 | Plane | Linear | Jira | ClickUp | OpenProject | Focalboard/Taiga |
|---|---|---|---|---|---|---|
| 开源 | ✅ AGPL-3.0 | ❌ | ❌ | ❌ | ✅ GPLv3 | ✅ |
| 自托管 | ✅ 4 种形态 + 气隙 | ❌ | ✅ Data Center（贵） | ❌ | ✅ | ✅ |
| 现代 UX | ✅ 接近 Linear | ✅ 最佳 | ⚠️ 笨重 | ⚠️ 功能堆砌 | ⚠️ 偏传统 | ⚠️ 简陋 |
| 内置协同文档 | ✅ **Tiptap + Yjs CRDT** | ✅ | ⚠️ Confluence 另购 | ✅ | ⚠️ Wiki | ❌ |
| 敏捷模型完整度 | ✅ cycle/module/estimate/state | ✅ | ✅ 最全 | ✅ | ✅ | ⚠️ |
| 自定义工作项类型 | ✅ `issue_type` 模型 | ⚠️ | ✅ | ✅ | ✅ | ❌ |
| 从 Jira 迁入 | ❌ **开源版无** | ✅ | — | ✅ | ⚠️ | ⚠️ |
| 企业权限深度 | ⚠️ 追赶中 | ⚠️ | ✅ 最强 | ✅ | ✅ | ❌ |
| 设计系统可复用 | ⚠️ propel 为 private | — | — | — | — | — |

**核心研判**：

Plane 的真实定位是**"开源世界里工程完成度最高的 Jira 替代"**，但它对不同读者有两种完全不同的价值：

- **作为产品选型**：适合"要现代 UX + 数据必须自己拿着 + 团队规模中小 + 能接受 AGPL"的组合。**决策前必须核实两件事**：① 你需要的功能是否在 community 版（`license/` 与 `deployments/*/community/` 提示存在分界）；② 是否需要从 Jira/Asana 批量迁入（开源仓库无此能力）。如果这两条都过不了，Linear（体验）或 Jira DC（企业深度）仍是更省事的答案。
- **作为工程参考（对多数开发者更有价值）**：这是一个**"多应用单仓 + 共享设计系统 + 独立 CRDT 服务 + 四种部署形态"的完整参考实现**，而且规模真实（5,228 文件）。可以直接偷的五件东西：`apps/live` 的 Hocuspocus 扩展套路、`@plane/propel` 的 subpath exports 设计系统模式、`services → MobX store → observer 组件` 的三层前端架构、`plane/app` 与 `plane/api` 的内外接口分离、`deployments/` 的多形态交付（尤其 AIO supervisor 与气隙恢复脚本）。

- **风险点**：① AGPL 阻断闭源 SaaS；② 开源版与商业版边界未在仓库中显式说明，需实测；③ 默认分支为 `preview`，误用会部署到预发布代码；④ 自托管全栈组件多，运维成本真实存在；⑤ 迁移入口只有 GitHub/Slack，存量 Jira 用户切换成本高。
- **一句话建议**：**要用它 → 先确认功能是否在社区版、并按 release 而非默认分支部署；要学它 → 直接读 `apps/live` 和 `packages/propel`，这两处的信息密度最高。**

> **关键文件速查**：
> - 仓库编排 → `turbo.json`、`pnpm-workspace.yaml`（`catalog:` 版本统一）、根 `package.json`（oxlint/oxfmt + husky + lint-staged + `react-doctor`）、`patches/`
> - **实时协作（最值得读）** → `apps/live/src/hocuspocus.ts`、`extensions/{database,redis,logger,title-sync,force-close-handler}.ts`、`extensions/title-update/{debounce,title-update-manager,title-utils}.ts`、`controllers/{collaboration,document,pdf-export}.controller.ts`、`lib/{auth,auth-middleware}.ts`
> - 协作编辑器 → `packages/editor/`（`@tiptap/core` + `extension-collaboration` + `@hocuspocus/provider`）
> - **设计系统** → `packages/propel/package.json`（逐组件 subpath exports）、`packages/propel/src/{charts/*,button,calendar,combobox,command,context-menu,design-system,emoji-icon-picker,empty-state,...}`
> - 主应用架构 → `apps/web/core/{services → store（MobX）→ components}`、`apps/web/react-router.config.ts`、`apps/web/vite.config.ts`
> - 后端分层 → `apps/api/plane/{app（内部视图）, api（对外 API）, authentication, license, bgtasks（Celery）, space, middleware, throttles, analytics}`、`plane/celery.py`、`apps/api/{manage.py,pytest.ini,run_tests.py}`
> - **数据模型全景** → `apps/api/plane/db/models/{workspace,project,issue,issue_type,cycle,module,state,estimate,label,view,page,draft,intake,sticky,deploy_board,webhook,api,asset,notification,social_connection,session,device,recent_visit,exporter}.py` + `importer/{github,slack}.py`
> - 多形态部署 → `deployments/aio/community/{Dockerfile,supervisor.conf}`、`deployments/cli/community/{install.sh,docker-compose.yml,restore.sh,restore-airgapped.sh,migration-0.13-0.14.sh}`、`deployments/kubernetes/community/`、`deployments/swarm/community/swarm.sh`
> - 大重构痕迹 → `packages/codemods/`
