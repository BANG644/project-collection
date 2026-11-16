# 🔬 getarcaneapp/arcane - 全方位深度调研

> 调研日期：2026-11-17 ｜ 数据源：GitHub API（仓库/Issue/Release/提交/源码）+ 官方站 r/selfhosted 真实用户评价 + selfhostable.dev 实测 + pistack/中文社区对比评测
> 说明：main 分支为 v3（2026-11-14 刚发布 v3.0.0），2.x 在 `release/2.x.x` 分支。

## 📌 一句话定位

一个「为所有人设计的现代 Docker 管理平台」——Go + SvelteKit 全栈，把容器/镜像/卷/网络的全生命周期管理、Compose 部署、GitOps、多环境远程 Agent、OIDC/LDAP/Passkey 认证塞进一个单容器应用里，主打 BSD-3 完全免费、轻量、界面现代，是当下 self-hosted 圈最热的 Portainer 替代候选。

## ⭐ 项目亮点

- **社区口碑异常一致地正面**：官网直接嵌了几十条 r/selfhosted 用户原话，从 Portainer/Dockge 迁来的用户几乎一边倒好评——「本该早点迁过来」「比 Portainer 好看且占用更小」「API 响应压缩都没开都能用得爽」。这种"迁移者满意度"在 Docker UI 赛道很少见。
- **工程架构极其规整（50+ 领域模块 + Fx DI）**：`backend/internal/` 下按领域切了 container/image/network/volume/gitops/oidc/passkey/swarm 等 50 余个 domain，每个 domain 遵循 `module.go/service.go/model.go/handler.go` 标准文件集；用 `go.uber.org/fx` 做依赖注入、Uber Fx 生命周期钩子管优雅停机。AGENTS.md 把贡献规范写到近乎"强迫症"程度（无 god file、无 wrapper、不得嵌套三元、child 不得反向 import 父）。这是专业团队级别的 Go 工程纪律，远比一般开源 UI 项目严谨。
- **多环境远程 Agent + 现代认证栈**：不仅有本地 Docker socket 管理，还能通过自己的 agent 管理远端多台主机；认证支持 OIDC、LDAP 登录与用户同步、Passkey/WebAuthn、API key、RBAC 角色——这套认证组合拳在 self-hosted Docker UI 里属于第一梯队。
- **GitOps 是真正的卖点**：把 Compose 文件放进 Git，Arcane 从"已审阅的 Compose 状态"部署，提供历史、回滚、review——第三方评价「GitOps 方向才是它比'又一个容器列表'更有趣的地方」。
- **轻量 + 透明**：所有状态以文件存在自己的 data volume（不像 Dokploy 用 Postgres、Komodo 用 MongoDB），1 vCPU/1GB 就能跑，是三方对比里 footprint 最小的；提供公开 SBOM、Trivy 扫描、CodeQL、Snyk 徽章，安全透明度做得足。

## 🏗️ 项目架构全景

### 目录结构 + 设计哲学

```text
backend/
├── cmd/              # 进程入口
├── api/              # API 装配 + 例外 HTTP/stream/WebSocket 路由
├── internal/
│   ├── <domain>/     # 50+ 领域：module/service/model/handler/helpers 标准集
│   │   └── children/<feature>/   # 子特性，child 永不反向 import 父
│   ├── bootstrap/    # 应用生命周期、router、jobs、启动装配
│   ├── di/           # Fx 依赖图与 providers
│   ├── config/       # 环境配置
│   ├── database/     # DB 与共享持久化原语（SQLite）
│   └── middleware/   # 认证/鉴权/环境代理（cors/csrf/role/ratelimit/traversal...）
├── pkg/              # 可复用引擎与基础设施
├── resources/        # migration、邮件模板、运行时资源
└── frontend/         # 内嵌的 SvelteKit 前端
frontend/             # SvelteKit 源 + 20+ 语言 i18n（en/zh-CN/zh-TW/ja...）
```

设计哲学：**领域驱动 + 编译期依赖图 + 严格分层**。每个领域自包含行为与路由，跨领域只通过顶层 `types/` 的共享契约和父级 API 通信；Fx 在启动期把 50+ 服务编织成一张图（`ActorOptions` / `ServiceOptions` 分组）。README 极简、文档外置、规范内嵌（AGENTS.md/AI_POLICY.md）——把"信息架构"和"工程纪律"分开管理。

### 技术栈 & 依赖图谱

- **后端**：Go 1.27.4，Echo v5 + Huma v2（声明式 API + OpenAPI）+ Uber Fx（DI）+ `moby/client`（Docker SDK）+ `compose-go/v2`
- **数据**：SQLite（`libtnb/sqlite`），状态落文件 volume
- **认证**：OIDC（coreos/go-oidc）、LDAP、WebAuthn/Passkey（go-webauthn）、JWT（lestrrat-go/jwx）
- **云原生**：AWS SDK（ECR/S3）、go-git（GitOps）、Docker Compose v5、containerd 生态
- **实时**：`coder/websocket` + 自研 ws handler（container_stats/log_streams/exec/system_stats）
- **前端**：SvelteKit + Vite，20+ 语言 Paraglide/i18n（Crowdin 托管翻译）
- **生态集成**：Podman、Swarm、Federated credentials、APNs 通知、Telemetry、Updater

### 核心配置一览

单容器部署挂载 `/var/run/docker.sock`，暴露 3552 端口，必填 `ARCANE_ENCRYPTION_KEY`（32 字符）。安全建议（第三方实测）：生产环境应挂 docker-socket-proxy 限制 API 端点、放 VPN/Tailscale 后、接 OIDC——"Docker 控制面板的漏洞等于家门钥匙"。

## 💡 应用场景与启发（重点章节）

### 典型使用场景

1. **Home Lab / 多 VPS 统一管理**：一台轻量面板管所有 Docker 主机，远程 agent 纳管，告别逐台 `ssh docker ps`。
2. **从 Portainer/Dockge 迁移**：想要 Portainer 的全功能 + Dockge 的简洁 + 现代 UI，且不愿付商业版订阅费。
3. **GitOps 式部署**：Compose 文件进 Git、Renovate 提更新 PR、Arcane 从审阅后状态部署，追求可回滚的基础设施变更。
4. **团队共享管理**：需要 RBAC、OIDC/LDAP 对接企业身份、审计活动的场景。

### 可借鉴的解决方案模式

- **领域驱动的后端分层模板**：`internal/<domain>/{module,service,model,handler,helpers}.go` + `children/<feature>/` 子域规则，是一份可直接照搬的 Go 中大型项目组织范本——尤其"子域只被直接父级 import、永不反向依赖"的纪律，从结构上杜绝了循环依赖和 god package。
- **Fx 依赖图 + 生命周期钩子**：`fx.Annotate(..., fx.As(...), fx.OnStop(...))` 把接口绑定、优雅停机声明式地写进 DI 图，而不是散落在 main 里手工管理——适合任何"几十个服务对象要按序装配"的系统。
- **AI 协作治理（AI_POLICY.md + AGENTS.md）**：项目把"AI 能做什么、贡献者如何披露 AI 使用、测试怎么写、改完必须 format+lint"写成强约束文件，甚至规定"不得声称未做过的手工验证"。这是"人机协作工程"的范本——AI 时代仓库该如何约束 agent 贡献者，这个项目给出了认真答案。
- **状态外置为文件**：对比 Dokploy(Postgres)/Komodo(Mongo) 把状态塞数据库，Arcane 用文件 volume 换最小 footprint 和备份直觉——"基础设施工具自身应该简单到可丢弃"的设计取舍。
- **i18n 前置**：20+ 语言从项目早期就用 Crowdin 托管，说明面向全球 self-hoster 的产品要把本地化当基础设施而非事后补丁。

### 同类需求的可参考思路

要做"Web 管控某类本地资源"的工具（Docker/K8s/数据库/系统服务）时，Arcane 给出模板：**领域分层 + DI 图装配 + WebSocket 实时流 + 多层认证 + 远程 agent 纳管 + GitOps 对接 + 状态文件化**。关键是它证明了"功能全面"和"轻量现代"不必然矛盾——靠的是架构纪律而非堆代码。

### 可复用片段

- `backend/internal/di/di.go` 的 `fx.Options` 分组（`ActorOptions`/`ServiceOptions`）+ `fx.Annotate(fx.As(...), fx.OnStop(...))`：Uber Fx 大型依赖图组织的可复用骨架。
- `AGENTS.md` 的 Go 风格条款（`cmp.Or` 代替空值 if、`kit.FromPtr` 代替指针判断、5+ 依赖用 `fx.In` params struct、导出函数不用 bool flag）：一份精炼的团队 Go 编码规范，可直接借鉴到自己的 CONTRIBUTING。
- `backend/api/ws/` 的 handler 拆分（log_streams/container_stats/exec/system_stats 各自独立）：WebSocket 多流复用的分文件组织方式。

## 🧠 核心源码解读（克制代码量）

### 入口与主流程：`backend/internal/di/di.go` + bootstrap

DI 图是理解整个系统的钥匙——50+ 领域服务在此编织：

```go
var (
    ActorOptions = fx.Options(
        fx.Provide(provideActorRuntime, provideRunCoordinator),
        fx.Provide(provideAdmissionGate),
        fx.Provide(fx.Annotate(provideJobScheduler,
            fx.As(fx.Self()), fx.As(new(types.DynamicScheduler)), fx.As(new(types.JobController)))),
        fx.Provide(provideWorkflowEngine, provideTunnelRegistry),
    )
    ServiceOptions = fx.Options(
        fx.Supply(resources.FS),
        fx.Provide(
            fx.Annotate(activity.NewActivityService, fx.As(fx.Self()), fx.As(new(activitylib.Service))),
            fx.Annotate(event.NewEventService,
                fx.OnStop(func(ctx context.Context, s *event.EventService) error { return s.Stop(ctx) })),
            job.NewJobService,
            ...
```

**关键点**：`fx.As(fx.Self())` + 多接口 `fx.As(new(...))` 让同一实现同时以具体类型和多个接口被注入；`fx.OnStop` 把优雅停机逻辑绑在依赖图上。**注意**：ActorOptions 里出现 `provideAdmissionGate`、`provideWorkflowEngine`、`provideTunnelRegistry`——暗示 v3 引入了"准入闸门 + 工作流引擎 + 隧道注册"这类 agent 化能力，远超普通 Docker UI。

### 关键模块一：领域组织规约（`AGENTS.md` 的架构约束）

AGENTS.md 不是普通说明文档，而是可执行的架构规约：

```text
Domain files: module.go(组合+路由) / service.go(业务) / model.go(持久化) / handler.go(IO)
Child features: <domain>/children/<feature>/，同文件集
  - children/ 本身无 Go 文件；只有直接父级 import child
  - 兄弟、祖先、其他 domain、DI、bootstrap 一律走父级 API
  - Children 永不 import 父；父级负责协调并私有化 child 实例
Wiring: DI 在 internal/di；启动顺序/生命周期在 internal/bootstrap
Don't: 把 api/handlers 长成中心层，或重建全局 internal/services
```

**为什么这样设计**：用目录结构和 import 规则把"高内聚低耦合"变成机器可检查的约束——"父级协调、子级私有、单向依赖"本质是每个领域内部再套一层干净的六边形架构，避免了传统 Go 项目 service 层膨胀成上帝包的老问题。

### 关键模块二：中间件栈（`backend/internal/middleware/`）

`aggregate.go / cors.go / csrf.go / role.go / ratelimit.go / traversal.go / environment.go / telemetry.go / huma.go`——安全相关能力全部中间件化。结合 Issue #4819「所有 /api JSON 响应未压缩，dashboard 每次加载 921.6KB」和 #4821「agent-proxy 路由 403 no known permission mapping」可以看出：v3 的中间件栈正处在快速迭代期（聚合、权限映射、压缩都在补）。

### 类型系统与抽象设计

共享契约放顶层 `types/`（独立 module `getarcane.dev/types/v3`），持久化模型留各 domain 的 `model.go`——**契约与存储分离**，让领域模型可独立演进。CLI 也拆成独立 module（`getarcane.dev/cli/v3`），通过 `replace` 指向本地，说明项目有意把"控制面板""类型契约""命令行"解耦成可单独发布的组件。

### 隐藏功能 & 未文档化特性

- **headless agent modes + Cobra CLI**：AGENTS.md 明确提到"headless agent modes and a Cobra CLI"——Arcane 不只是 Web UI，还有无头 agent 模式（配合多环境纳管）和完整 CLI（含 admin reset_mfa/reset_password、recovery、upgrade 子命令）。README 完全没展开。
- **AI_POLICY.md 贡献者豁免条款**：AGENTS.md 提到"maintainer exemption"——维护者在 AI 使用上有豁免，外部贡献者必须披露。这种"区别对待"的 AI 治理策略很少见。
- **federated credentials / APNs / vulnerability(KEV)**：领域列表暴露了联邦凭证、iOS 推送、CISA KEV 漏洞同步等高级能力，README 只字未提。
- **Workspace 级 v3 重构**：v3.0.0（11-14）刚发布，从 2.17.x 跳跃而来，main 分支和 release/2.x 并存——正处大版本切换期（Issue 里 v3.0.1 的 GitOps/Synology 兼容 bug 频出）。

## 📐 架构决策与设计哲学

### ADR 摘要

无独立 ADR，但决策可从代码与规约读出：
- **DDD 领域切分 + Fx DI**：50+ 领域按业务边界组织，依赖在启动期编织——选"结构清晰"而非"快速堆砌"。
- **文件状态而非数据库**：最小 footprint + 备份直觉，牺牲的是复杂查询能力。
- **Docker-and-compose-centric**（pistack 评价）：刻意不做 Swarm/K8s 编排（相比 Komodo），专注把 Docker 单机/多机 agent 管理做到极致。
- **BSD-3-Clause**：最宽松的开源协议之一，利于商业嵌入（对比 Komodo GPL-3、Dokploy 自定义协议）。

### 设计红线（Out-of-Scope）

不做 K8s/Swarm 编排、不自带数据库 provisioner（数据库当普通容器部署）、feature request 一律移到 Discussions（issue 只收 bug）——从流程上控制范围蔓延。

### 版本演进中的哲学转变

2025-04 创建，2026-11-14 发布 v3.0.0（11-15 即 v3.0.1 热修），从 2.17 到 3.0 是一次大重构（Go 1.27、Echo v5、Huma v2、全新 agent/工作流架构）。近期提交密集（11-16 一天多条：agent 请求解堵、环境聚合、LDAP 同步、缓存加速），呈现"大版本发布后高频打磨"的节奏。

## 🌐 全网口碑画像

### 好评共识

- **迁移者满意度极高**（官网汇总 r/selfhosted 原话）：
  - u/Subietoy78：「used portainer prior and it was fine but arcane looks nicer and has a smaller footprint」
  - u/planetearth80：「Switched to Arcane and pretty happy with it. Only complaint is that I should have moved earlier」
  - u/Renoglodon：「Switched from Portainer a couple of months ago and absolutely loving it」
  - u/regalen44：「great UX and the update prompts for containers are perfect, no need for watchtower」
  - u/JuanToronDoe：「beautiful, simple yet powerful, with a lot of advanced features in submenus...running a distant agent was super easy」
- **维护者响应快**：u/bradmatt275：「logged a bug and they had a fix and a release ready within a week」——与 Issue 列表里高频 release 吻合。
- **第三方评测正面**：中文教程（tycp.xyz）称其为「冲着 Portainer 全功能+Dockge 极简+CasaOS 美观组合需求来的」，6.6k⭐；selfhostable.dev 评价「如果今天重建个人 VPS，会第一个试的轻量干净 dashboard」。
- **GitOps 被点名为差异化钩子**：pistack 和 selfhostable.dev 都强调 Git 化 Compose 部署是它区别于"又一个容器 UI"的关键。
- **文档好评**：u/GrumpyGander：「didn't even have to spin up the container. Just read the documents and I feel like I know everything I need to」。

### 差评共识 & 踩坑高发区

- **年轻项目、安全需谨慎**：selfhostable.dev 明确警告"控制面板漏洞等于家门钥匙"，建议 socket-proxy 限权、VPN 后、接 OIDC、快速打补丁——这是对"年轻项目"的通用谨慎，不是 Arcane 独有缺陷，但 v3 刚发布更需注意。
- **v3 大版本切换期 bug 多**：Issue 列表里大量 v3.0.1 新问题：
  - #4819：所有 /api JSON 未压缩，dashboard 每次加载 921.6KB（性能硬伤）。
  - #4830：Synology 上未改动的非可执行 Compose 文件被误报 GitOps 冲突。
  - #4821：agent-proxy 路由对部分路径 403 "no known permission mapping"（权限映射不全）。
  - #4823：CISA KEV 同步在云主机 IP 上被 cisa.gov 403 拦截。
  - #4825：webhook 不再重新部署项目。
- **功能取舍明确**：pistack 指出 Arcane"不做 DB provisioner、不做 K8s/Swarm 编排"，需要这些的人得选 Dokploy/Komodo；label 路由也不自动生成（从 Portainer/Dokploy 迁移要手工重建 Traefik/nginx 路由）。
- **单点维护风险信号**：虽然近期有多位贡献者（José M. Requena Plens 等），但核心提交仍高度集中在 Kyle Mendell 一人。

### 争议焦点

- **"该不该现在迁移"**：pistack 的建议很克制——「只有在你有具体痛点（无 Git 部署、无多节点编排、无 DB 生命周期）时才从 Portainer 迁走，Portainer 依然是 solid 的容器浏览器」。这与官网用户"本该早点迁"的热情形成有趣对照：重度/生产用户仍需要 Portainer 的成熟度。
- **轻量 vs 全能**：Arcane 选择文件状态 + Docker-centric 换轻量，代价是复杂场景（多节点编排、DB 生命周期）需外部工具——这是定位选择，不是缺陷。

### 典型实战案例

- **selfhostable.dev 实测建议**：给出 socket-proxy 最小权限 Compose 配置和"先拿 Uptime Kuma/Homepage 这种无聊服务试水、故意搞坏 Compose 分支测回滚、理解 Arcane 拥有什么 vs Docker 拥有什么"的上手路径。
- **中文社区**（tycp.xyz）：详细部署教程 + Docker 四资源生命周期管理 + Compose 拖拽导入 + 多代理远程管理的实操介绍。
- **真实迁移案例**：多位 r/selfhosted 用户报告从 Portainer/Dockge/CasaOS 迁入，TrueNAS 与 Ubuntu VPS 双环境部署（u/Anarchist_Future）。

### 维护者响应风格

Issue 响应快（用户称一周内修复发版），feature request 分流到 Discussions 以保 issue 区聚焦 bug；维护者亲自高频提交并快速发 release。整体是"响应迅速、节奏激进、v3 打磨期 bug 与新功能齐飞"的风格。

## ⚔️ 竞品对比

| 维度 | Arcane | Portainer | Dockge | Dokploy | Komodo |
|------|--------|-----------|--------|---------|--------|
| 定位 | 现代全能 Docker 管理 + GitOps | 老牌成熟、团队/多环境 | 极简 Compose stacks 编辑 | PaaS 式部署平台 | 舰队级编排 |
| 技术栈 | Go 1.27 + SvelteKit | Go + Angular | Node + Svelte | - | Rust + React |
| 状态存储 | 文件 volume（最轻） | SQLite/卷 | 文件 | Postgres | MongoDB |
| 协议 | BSD-3（最宽松） | 混合(有商业版) | MIT | 自定义 | GPL-3 |
| GitOps | ✅ 原生 | 部分(商业) | ❌ | ✅ | ✅ |
| 多节点/编排 | 远程 agent | ✅ CE/BE | ❌ | Swarm | ✅ K8s/Swarm/Nomad |
| DB provisioner | ❌ | ❌ | ❌ | ✅ | ❌ |
| 认证 | OIDC/LDAP/Passkey/RBAC | RBAC/SSO(商业) | 基础 | 基础 | 基础 |
| UI 现代度 | 高 | 偏重 | 简洁 | 中 | 中 |
| 成熟度 | 年轻(v3 刚发) | 最成熟 | 成熟稳定 | 活跃 | 活跃 |
| 适合 | 重建个人 VPS、要 GitOps+轻量 | 生产/团队稳妥 | 只管 Compose | 要 PaaS+DB | 要舰队编排 |

### 选择建议

- **重建个人 VPS、要轻量现代 + GitOps** → Arcane（该场景首选）。
- **生产/多环境/要最稳** → Portainer（pistack：仅在有具体痛点时才迁走）。
- **只管 Compose stacks** → Dockge。
- **要自动 provision 数据库/PaaS 体验** → Dokploy。
- **要跨 K8s/Swarm/Nomad 舰队编排** → Komodo。

## 🎯 核心研判

### 项目优势（不可替代的价值点）

1. **"全功能 + 轻量 + 现代 UI + BSD-3 免费"的组合在当前市场稀缺**，从 Portainer/Dockge 迁来的用户满意度极高，口碑自增长明显。
2. **工程架构质量在同类 UI 工具里属顶部**：50+ 领域 DDD + Fx DI + 严格 AGENTS.md 规约 + 现代认证栈，超出"Docker UI"应有的工程水准。
3. **GitOps + 远程 agent + 文件状态**三重差异化，精准命中 self-hoster 对"可回滚、可多机、轻量"的核心诉求。

### 项目风险（潜在隐患和局限性）

- **v3 大版本切换期 bug 密集**：#4819 未压缩 921KB、#4830 Synology GitOps 误报、#4821 agent 权限映射不全、#4823 KEV 403、#4825 webhook 失效——生产采用需等 v3 稳定。
- **安全责任在用户**：Docker socket 直挂风险高，必须自行做 socket-proxy/VPN/OIDC 加固——年轻控制面板一旦有洞后果严重。
- **能力边界**：不做 K8s/Swarm 编排、不做 DB provisioner、不自动管理 ingress 路由——从 Portainer/Dokploy 迁移有手工重建成本。
- **单点维护**：核心高度集中在一人，bus factor 风险（虽有第二贡献者活跃）。
- **快速迭代的副作用**：一个月多个 release、major 版本 breaking change（Go 1.27、Echo v5），浮动 tag 可能某天重启生产栈——务必 pin 版本。

### 适用场景 & 不适用场景

- ✅ **适合**：Home Lab/个人 VPS 的 Docker 统一管理；从 Portainer/Dockge 迁来想要更现代轻量；GitOps 式 Compose 部署；需要 OIDC/LDAP/Passkey 团队认证。
- ❌ **不适合**：要 K8s/Swarm/Nomad 编排或 DB 生命周期管理（选 Komodo/Dokploy）；不能做安全加固的生产环境；要求绝对稳定、不愿跟版本的保守团队（选 Portainer）。

### 趋势判断

**快速上升期（v3 重构刚落地）**。6.6k⭐、社区口碑自发传播、11-14 刚发 v3.0.0、日均多条提交，势头强劲；但 v3 bug 密集、安全需用户加固、编排能力有限。结论：**个人/Home Lab 场景现已值得采用（做好加固+pin 版本），生产/多节点场景建议观察 v3 稳定后再评估**。工程架构本身（DDD+Fx+AI 治理规约）已值得作为范本学习，与是否采用产品无关。

## 📂 关键文件路径速查

| 路径 | 用途 |
|------|------|
| `AGENTS.md` | 项目级工程规约：领域分层、命名、Go 风格、测试、AI 协作规则 |
| `AI_POLICY.md` | AI 使用政策（含 maintainer exemption） |
| `backend/internal/di/di.go` / `providers.go` | Uber Fx 依赖图（ActorOptions/ServiceOptions）与 providers |
| `backend/internal/bootstrap/*.go` | 生命周期、router、jobs、server、telemetry 装配 |
| `backend/internal/<domain>/{module,service,model,handler}.go` | 50+ 领域的标准文件集（container/image/gitops/oidc/...） |
| `backend/internal/<domain>/children/<feature>/` | 子域（如 image/children/patch、system/children/backup） |
| `backend/internal/middleware/*.go` | cors/csrf/role/ratelimit/traversal/environment/telemetry |
| `backend/api/ws/*.go` | WebSocket 实时流（container_stats/log_streams/exec/system_stats） |
| `backend/cli/` | Cobra CLI（admin/reset_mfa、recovery、upgrade、health、openapi） |
| `backend/pkg/agent/` · `pkg/podman/` | headless agent 模式与 Podman 支持 |
| `frontend/` · `frontend/messages/*.json` | SvelteKit 前端 + 20+ 语言 i18n |
| `getarcane.app/sbom` | 公开软件物料清单（SBOM） |
| `release/2.x.x` 分支 | 旧 2.x 版本（main 为 v3） |
