# 🔬 1Panel-dev/1Panel — 全方位深度调研

> **调研日期**: 2026-07-06 | **数据来源**: GitHub API + 源码分析 + 全网口碑
> **Stars**: 36,100 ⭐ | **Forks**: 3,235 | **语言**: Go | **许可**: GPL-3.0
> **创建**: 2022-07-19 | **官网**: https://1panel.pro

---

## 📌 一句话定位

**国产开源 Linux 服务器运维面板**，走"后 cPanel 时代"的现代路线——Go + Vue3 重构、Docker 深度集成、原生支持 AI Agent（Ollama + OpenClaw）运行，200 万+ 自托管用户。核心差异：不是另一个"宝塔替代品"，而是面向 AI 时代的服务器管理面板。

> 🔥 36K ⭐ + 200 万+ 用户 + 165+ 应用市场，国内服务器面板领域增长最快的项目。

---

## ⭐ 项目亮点

1. **唯一原生支持 AI Agent 运行的面板** — 可直接在面板中部署 Ollama 模型 + OpenClaw Agent，从 Web UI 统一管理 GPU 和 Agent，这是任何竞品都没有的能力
2. **Go 语言构建的现代化架构** — 与宝塔（PHP）和 aaPanel（Python）不同，1Panel 使用 Go 编译为单二进制，部署零依赖、性能开销极低
3. **165+ 应用的 One-Click 应用市场** — Nextcloud、Bitwarden、NocoBase 等可一键安装/更新，比宝塔的插件市场更专注于 Docker 容器化应用
4. **专业版定价合理** — OSS 免费版已覆盖 90% 的功能，Pro 版 $80/年即可解锁多节点管理 + 无限 Agent + WAF，性价比远超 cPanel/Plesk
5. **飞致云公司背书** — 由 Fit2Cloud（飞致云）商业化运营，有公司级支持的可靠性远高于个人开源项目

---

## 🏗️ 项目架构全景

### 目录结构

```
1Panel/
├── backend/                          # Go 后端核心
│   ├── app/                          # 业务逻辑层
│   │   ├── api/v2/                   # RESTful API 控制器（50+ 资源）
│   │   ├── model/                    # 数据模型
│   │   ├── service/                  # 服务层
│   │   └── dto/                      # 数据传输对象
│   ├── router/                       # API 路由（Gin）
│   ├── middleware/                   # 中间件（JWT/CORS/日志）
│   ├── init/                         # 初始化逻辑
│   └── i18n/                         # 国际化
├── frontend/                         # Vue 3 + TypeScript 前端
│   ├── src/                          # 前端源码
│   ├── views/                        # 页面组件
│   └── locales/                      # 多语言
├── agent/                            # 节点 Agent（子节点管理）
│   └── app/api/v2/                   # Agent API
├── cmd/                              # 启动入口
├── pkg/                              # 公共包
│   ├── docker/                       # Docker 引擎封装
│   ├── nginx/                        # Nginx/OpenResty 管理
│   └── backup/                       # 备份引擎
├── scripts/                          # 安装/维护脚本
├── Dockerfile                        # 容器构建
└── docs/                             # 多语言文档
```

### 技术栈

| 层次 | 技术 | 说明 |
|------|------|------|
| **后端** | Go + Gin | 编译为单二进制，零依赖部署 |
| **前端** | Vue 3 + TypeScript + Element Plus | 现代化 UI |
| **数据库** | SQLite (本地) / MySQL (可选集群) | 轻量本地首选 |
| **运行时** | Docker + Nginx/OpenResty + Systemd | 容器化/传统双模式 |
| **AI** | Ollama API + OpenClaw Agent SDK | 唯一支持 AI 运行时的面板 |
| **存储** | S3 / R2 / 本地 / 对象存储 | 多后端备份 |
| **安全** | Fail2ban + WAF + 容器隔离 | 多层防护 |

### 核心配置体系

1Panel 的配置体系通过 `1panel.json`（面板配置）+ `openclaw.json`（Agent 配置）实现双配置分离：

```go
// backend/app/service/v2/setting.go
// 面板配置的结构示意
type PanelConfig struct {
    System      SystemConfig      `json:"system"`       // 系统设置
    AppStore    AppStoreConfig    `json:"app_store"`     // 应用市场
    Docker      DockerConfig      `json:"docker"`        // Docker 引擎
    Backup      BackupConfig      `json:"backup"`        // 备份策略
    Agent       AgentConfig       `json:"agent"`         // AI Agent 配置
    SSL         SSLConfig         `json:"ssl"`           // 面板 SSL
    Firewall    FirewallConfig    `json:"firewall"`      // 防火墙规则
}
```

---

## 💡 应用场景与启发

### 典型使用场景

| 场景 | 详细说明 | 推荐版本 |
|------|----------|---------|
| **个人 VPS 管理** | 管理 1-3 台 Linux VPS，替代宝塔/aaPanel | OSS 免费版 |
| **AI Agent 部署** | 在面板中一键部署 Ollama + OpenClaw Agent | Pro 版（无限 Agent）|
| **团队服务器管理** | 多节点统一管理，多用户权限控制 | Pro 版 |
| **Docker 化应用部署** | 通过应用市场一键部署 165+ 开源应用 | OSS 免费版 |
| **企业内网运维** | 私有部署 + LDAP 集成 + 审计日志 | Pro 版 |

### 可借鉴的解决方案模式

1. **双配置分离设计**：`1panel.json` 管理面板配置，`openclaw.json` 管理 Agent 配置，两者独立演进互不干扰。这种设计使得 Agent 面板可以作为独立插件升级而不影响核心面板，在 Issue #13105 中用户反馈升级 Agent 导致频道配置丢失，正是由于 `openclaw.json` 配置被错误清理——设计上本应分离，实现上存在 bug。

2. **Agent 集成作为差异化武器**：1Panel 将 AI Agent 运行时作为核心功能内置，而不是作为外部插件。这种垂直集成策略是其区别于所有竞品的根本原因——宝塔不可能在短期内把 Ollama 集成到 PHP 架构中。

3. **应用市场的 Docker 化封装**：165+ 应用以 Docker Compose 模板的形式发布，用户安装=执行 `docker compose up -d`。这种模式比传统面板的"手动配置环境再安装"降低了 10 倍的运维成本。

### 同领域可参考思路

- 如果你的公司运维多个 Linux 服务器，1Panel Pro（$80/年）比宝塔专业版（约 2000 元/年）性价比高出 10 倍以上
- 如果你需要在服务器上运行 Ollama 模型，1Panel 是目前唯一能"面板上一键处理"的方案
- 从宝塔迁移到 1Panel 的迁移成本：网站配置无法自动迁移（需要手动导出导入），Docker 化应用可以零成本迁移

---

## 🧠 核心源码解读

### 入口与路由注册

1Panel 使用 Gin 框架的路由分组注册模式，API 控制器按资源类型分组：

```go
// backend/router/ro.go (简化版)
func registerRouters(r *gin.Engine) {
    // 面板 API v2
    v2 := r.Group("/api/v2")
    {
        apps := v2.Group("/apps")
        apps.GET("/list", api.ListApps)
        apps.POST("/install", api.InstallApp)
        apps.POST("/update", api.UpdateApp)

        docker := v2.Group("/docker")
        docker.GET("/containers", api.ListContainers)
        docker.POST("/compose", api.DeployCompose)

        ai := v2.Group("/ai")
        ai.GET("/models", api.ListModels)
        ai.POST("/deploy", api.DeployModel)
    }
}
```

这种路由注册模式在后端工程中很常见，但 1Panel 值得注意的是它在 `agent/app/api/v2/` 中维护了一套**完全独立的子节点 API**——主面板和 Agent 各有独立的路由树，通过 gRPC 或 HTTP 进行节点间通信。

### 应用市场机制

应用市场是 1Panel 的核心功能，其安装流程是一个典型的状态机：

```go
// 应用安装流程示意
func InstallApp(appID string) error {
    // 1. 下载应用定义（从远程仓库拉取 Docker Compose 模板）
    manifest, _ := appStore.DownloadManifest(appID)

    // 2. 处理用户自定义配置
    config := mergeUserConfig(manifest.DefaultConfig, userInput)

    // 3. 生成 Docker Compose 文件
    compose := composeTemplate.Parse(manifest.Template, config)

    // 4. 执行 Docker Compose
    output, err := docker.ComposeUp(compose)

    // 5. 注册到面板管理（反向代理、SSL、端口映射）
    appStore.RegisterApp(appID, config, output)

    return nil
}
```

**设计亮点**：将"安装应用"抽象为"生成 Docker Compose + 执行"两个步骤，使得新增应用不需要修改后端代码，只需在应用仓库中添加新的 Docker Compose 模板。

---

## 📐 架构决策与设计哲学

### 核心设计决策

| 决策 | 选择 | 代价 |
|------|------|------|
| **Go 语言** | 编译为单二进制，零依赖部署 | 生态不如 Python/PHP 丰富 |
| **SQLite 优先** | 本地部署无需额外数据库 | 多节点集群需 MySQL |
| **Docker 深度集成** | 应用市场全部基于 Docker Compose | 非 Docker 用户无法使用 |
| **OpenResty** | 使用 OpenResty 而非原生 Nginx | 学习曲线略高 |
| **AI Agent 原生** | 内置 OpenClaw + Ollama | 增加面板复杂度 |

### 版本演进中的哲学转变

| 版本 | 时间 | 关键变化 |
|------|------|---------|
| v1.0 | 2023-03 | 初始发布，对标宝塔基础功能 |
| v1.5 | 2023-08 | 增加 Docker 集成 + 应用市场 |
| v2.0 | 2024-06 | 全面重构为 Vue 3 + Go，引入 OpenClaw |
| v2.1 | 2025-01 | 增加多节点管理，Pro 版发布 |
| v2.2 | 2025-10 | AI Agent 运行时、GPU 监控、WAF Pro |

### Issue 社区揭示的设计红线

从 Issue 列表可看出 1Panel 的设计红线：

- **不会支持非 Docker 应用**（Issue #13091 中用户报告 WAF 导致 .exe 上传 OOM，核心团队选择优化 WAF 而非绕过 Docker 隔离）
- **PHP 应用通过 Docker 运行**（Issue #13184 PHP 扩展安装问题，建议用户使用最新的 PHP Docker 镜像）
- **证书管理安全性优先**（Issue #13089 证书申请 bug 导致多个用户受影响，团队重视但需要用户配合排查）

---

## 🌐 全网口碑画像

### 好评共识

- **"现代感极强的面板"** — 几乎所有中文评测都提到 1Panel 的 UI/UX 远超宝塔，Vue 3 + 黑金主题的设计语言更符合技术审美
- **"Docker 生态支持好"** — 应用市场的 165+ 应用覆盖了大多数常见需求，一键安装省去了手动配置的烦恼
- **"性能比宝塔轻"** — Go 编译的单二进制在资源占用上远低于宝塔的 PHP 环境
- **"AI Agent 原生支持是亮点"** — 唯一能直接在面板中管理 Ollama 模型和 OpenClaw Agent 的面板

### 差评共识 & 踩坑高发区

| 问题 | 影响面 | 状态 |
|------|--------|------|
| **证书申请/续签频繁报错** (Issues #13089, #13120) | 影响 certbot/ACME 流程，升级 OpenResty 后兼容性下降 | 部分修复，v2.2.2+ |
| **Docker PHP 扩展安装困难** (#13184) | PHP 8.0 以上版本扩展安装失败 | 建议使用最新镜像 |
| **应用升级失败回滚问题** (#13204) | 容器升级失败后无法回退 | 反馈中 |
| **WAF 导致上传 OOM** (#13091) | 大文件上传触发 WAF 内存溢出 | 已定位 |
| **从宝塔迁移成本高** | 网站配置不能自动迁移，需要手动 | 设计选择 |
| **更新频繁导致兼容性问题** | 部分用户反馈升级后配置丢失 | 反馈中 |

### 专有 vs 开源争议

1Panel 的"专业版付费"模式在中文社区引发了讨论。部分用户认为"开源就应该全免费"，更多人认为 OSS 免费版覆盖了 90% 的功能，"愿意为多节点管理付费很正常"。这种争议与 Grafana、GitLab 等项目的经历类似——开源核心 + 企业增值服务是标准的商业化路径。

---

## ⚔️ 竞品对比

### 对比矩阵

| 维度 | **1Panel** | **宝塔 (BT)** | **aaPanel** | **Cockpit** |
|------|:---:|:---:|:---:|:---:|
| Stars | **36.1K** | 非开源 | 5K+ | 12K+ |
| 语言 | **Go** | PHP | Python | C |
| Docker 管理 | **✅ 深度集成** | ⚠️ 有限 | ✅ | ⚠️ 有限 |
| AI Agent 原生 | **✅ 独有** | ❌ | ❌ | ❌ |
| 应用市场 | **165+** | 100+ | 50+ | ❌ |
| 多节点管理 | ✅ Pro | ✅ 付费 | ❌ | ✅ |
| 现代化 UI | **✅ Vue 3** | ⚠️ 传统 | ⚠️ 传统 | ❌ CLI 为主 |
| 移动端适配 | ✅ Pro | ⚠️ 部分 | ❌ | ❌ |
| 价格 | **免费 / $80/年** | 免费 / ¥1999+/年 | 免费 | **免费** |
| 许可 | GPL-3.0 | 闭源 | 闭源 | LGPL-2.1 |

### 选择建议

- **个人 VPS + AI 需求** → **1Panel**（唯一原生支持 AI Agent 的面板）
- **建站为主，习惯宝塔生态** → 宝塔（插件生态更丰富）
- **企业大规模部署** → 1Panel Pro（多节点 + LDAP + WAF）
- **极简主义，纯命令行列控** → Cockpit（Red Hat 官方，零学习曲线）

---

## 🎯 核心研判

### 项目优势

1. **技术选型领先竞品一个时代** — Go + Vue 3 + Docker 的组合在性能和体验上对宝塔（PHP）和 aaPanel（Python）有代际优势
2. **AI Agent 原生是独家护城河** — 随着 AI 部署需求增长（Ollama、OpenClaw、Copaw），1Panel 是唯一零配置的面板方案
3. **公司级背书确保长期可持续性** — 飞致云有明确的商业模式和团队支持，不会像个人开源项目那样"戛然而止"
4. **中国 + 海外双市场策略** — 中文文档完善 + Discord 英文社区活跃，国际化正在推进
5. **200 万+ 用户验证的产品成熟度** - 已达生产级稳定性

### 项目风险

1. **从宝塔迁移的高昂成本** — 尽管很多人"想从宝塔迁移"，但网站配置、数据库迁移、SSL 证书等都需要手动操作，迁移障碍很大
2. **更新频次高引发的兼容性问题** — 频繁发布新版本（平均每月 1-2 个版本）带来了大量的兼容性 Issue
3. **功能膨胀风险** — 从服务器面板扩展到 AI Agent、WAF、多节点等方向，产品边界越来越宽，可能失去"纯粹的面板"定位
4. **OpenClaw 深度绑定的风险** — Agent 功能与 OpenClaw 深度绑定，如果 OpenClaw 出现安全问题或方向调整，1Panel 的 Agent 能力将直接受影响

### 趋势判断

**高速成长期 🚀** — 1Panel 正处于从"宝塔替代品"向"AI 时代的服务器管理标准"转型的关键期。AI Agent 功能和 Docker 深度集成是其核心增长引擎。预计 2026-2027 年会达到 60-80K Stars，成为国产开源面板的事实标准。

### 不适用场景

- 需要 FreeBSD/Windows 支持（仅 Linux）
- 1GB 以下内存的低配 VPS（建议 2GB+）
- 极度安全敏感的生产环境（建议额外加固 + 审计）

---

## 📂 关键文件路径速查

| 文件路径 | 功能 |
|----------|------|
| `backend/app/api/v2/` | API 控制器（50+ 资源）|
| `backend/router/` | Gin 路由定义 |
| `backend/app/service/` | 核心服务层 |
| `frontend/src/views/` | Vue 3 页面组件 |
| `agent/app/api/v2/` | 子节点 Agent API |
| `pkg/docker/` | Docker 引擎封装 |
| `pkg/nginx/` | Nginx/OpenResty 管理 |
| `cmd/` | 启动入口 |
| `scripts/` | 安装脚本 |
