# Coolify 深度调研

> 调研时间：2026-10-26 ｜ 抓取自 GitHub API + 第三方评测（2026-10）｜ 报告编号：#537

## 一、项目定位（一句话）

**Coolify 是一个开源、可自托管的应用/数据库/服务部署平台，是 Vercel / Netlify / Heroku 的开源替代品**——你只需一台能 SSH 的服务器，就能获得类云平台的部署体验，而配置与运行资源始终留在自己的基础设施上。

## 二、项目亮点（差异化）

- 🚀 **360+ 一键服务市场**：数据库、监控栈、CMS、分析工具等从目录一键拉起，自带持久化存储与生成凭据。
- 🔧 **多构建器兼容**：Nixpacks / Railpack / Dockerfile / Docker Compose / 预构建镜像，覆盖从静态站到全栈应用。
- 🔌 **四入口 + 团队权限**：Dashboard / API / CLI / **MCP** 四种操作面，并支持基于团队的访问控制。
- 📈 **v4 已稳定**：2026-04 结束近两年的 beta；v4.4（2026-10）新增 opt-in 代理级流量分析 + OIDC 登录。
- 🔒 **数据主权**：配置留在你的服务器；停止用 Coolify，正在跑的资源照常工作且仍可管理。

## 三、核心架构

技术栈（来自 `composer.json` 真实依赖）：

| 层 | 技术 |
|----|------|
| 后端 | **Laravel 12.69**（PHP ^8.4） |
| 前端 | **Inertia.js + Svelte 5**（vite 构建）+ **Livewire 3.8** 交互组件 |
| 队列 | Horizon ｜ WebSocket：**Reverb** ｜ 认证：Sanctum + Fortify + Socialite |
| 远程管理 | phpseclib（SSH）、league/flysystem-sftp / aws-s3（远程文件） |
| AI/MCP | `laravel/mcp`（app/Mcp 目录提供 MCP server） |

`app/` 分层遵循 Laravel 惯例并做了领域切分：`Actions / Models / Services / Repositories / Http / Livewire / Mcp / Policies / Events / Jobs …`。路由文件已出现 `ai.php`——这是平台 AI 集成入口；另有 `api.php / web.php / webhooks.php / console.php / channels.php`。

部署引擎本质是**生成 docker-compose 并驱动 Docker API**：仓库根提供多套编排文件（`docker-compose.prod.yml / .dev.yml / .dev-multi.yml / .dev-side-by-side.yml / .windows.yml / .maxio.dev.yml`），一键服务模板定义在 `templates/` 目录。反向代理可在 **Traefik / Caddy** 间选择，自动签发 Let's Encrypt 证书。

```text
# 根目录关键结构（真实）
config/  docker/  lang/  resources/  scripts/  templates/  tests/
docker-compose*.yml   vite.config.js   bootstrap/   database/{migrations,schema,seeders}
```

## 四、应用场景与启发

- **个人/小团队降本**：用一台 $6 Hetzner VPS 跑多个 hobby 应用 + 数据库 + 服务，替代 Railway/Render 月费。
- **给同类需求的解法启发**：
  1. 「自托管 PaaS」的核心不是编排算法，而是**远程 SSH 管理 + compose 模板市场 + 反向代理/HTTPS 自动化**三件套——这是任何想做内部部署平台的团队可直接复用的骨架。
  2. **MCP server 内建于应用**（app/Mcp + laravel/mcp）让平台本身可被 AI agent 操作，是「平台即 agent 工具」趋势的样板。
  3. `templates/` 把「部署知识」沉淀为可版本化、可审核的声明式模板，比脚本化部署更可维护。

## 五、源码深度解读（关键模块）

`composer.json` 依赖节选佐证架构：

```jsonc
"laravel/framework": "^12.69.3",
"livewire/livewire": "^3.8.10",
"laravel/reverb": "^1.12.0",      // WebSocket 服务
"laravel/horizon": "^5.50.0",     // 队列
"laravel/mcp": "^1.0.1",          // MCP server
"laravel/sanctum": "^4.3.3",
"phpseclib/phpseclib": "^3.0.57", // SSH 远程管理
"league/flysystem-sftp-v3": "^3.36.0"
```

- `app/Mcp/`：MCP 工具实现，使外部 agent 可通过 MCP 协议驱动部署/查询。
- `routes/ai.php`：独立 AI 路由文件，承载平台侧 AI 能力（如智能部署建议）。
- `templates/`：360+ 服务定义，是「一键市场」的数据底座。

## 六、社区口碑

**数据**（2026-10 第三方评测与 GitHub）：62K+ Stars、Discord 20K+ 成员、Cloud 3,641+ 客户；本调研抓取 64,149⭐。

- ✅ **优势**：免费（Apache-2.0，无功能锁）、社区活跃、一键市场极大降低自托管门槛、v4 稳定后稳定性显著改善。
- ⚠️ **资源占用**：空闲 CPU 5–7%，开启监控栈可飙到 25%；官方推荐独立服务器部署。
- ⚠️ **安全记录**：2026-01 披露 11 个漏洞（含 3 个 CVSS 10.0，可经私钥泄露实现 RCE）；第三方统计 2026 全年 61 条安全公告、16 条严重。**运维铁律：勤打补丁、dashboard 不公开、不授予不可信用户团队权限**。
- ⚠️ **多节点弱**：Docker Swarm 已弃用并计划 v5 移除，当前多服务器仅支持 SSH 直连，无 K8s 路径、无内置 service mesh；**v5 无公开时间表**。

## 七、竞品对比

| 项目 | 定位 | 关键差异 |
|------|------|---------|
| **Coolify** | 自托管 PaaS | 功能最全、市场最大；重、安全公告多 |
| Dokploy | 自托管 PaaS | 更轻量（空闲 0.8–1.5% CPU）、增长快 |
| CapRover | 自托管 PaaS | 简单、无预览环境 |
| Temps | 自托管 PaaS+可观测 | 单二进制含错误追踪/会话回放/uptime |
| Railway / Render | 托管（非 OSS） | 省心但有用量计费与厂商锁定 |
| Supabase | 仅后端/DB | 不覆盖通用部署 |

## 八、核心研判

- **适合谁**：在受控 VPS 上跑可预测应用集的个人与中小团队——成本优势真实，是「自托管 PaaS 最快路径」。
- **不适合谁**：需要自动水平扩缩、多区域、复杂编排（K8s 级）的团队；以及对安全公告敏感的大型企业（需自备运维）。
- **落地建议**：自托管免费但有「2 AM 部署失败没人支援」的代价，务必自建 app 数据备份；生产可观测性缺口用 Sentry/Plausible/UptimeRobot 补齐。**它替代的是 Railway/Render 的部署体验，不是 K8s。**

## 九、关键文件路径速查

```text
composer.json                      # 技术栈与依赖事实源
app/Mcp/                          # 内置 MCP server 工具
routes/ai.php                     # AI 集成路由入口
templates/                        # 360+ 一键服务模板（市场底座）
docker-compose.prod.yml           # 生产编排
config/  resources/  bootstrap/   # Laravel 标准层
.agents/skills/                   # 仓库自带 agent 技能（fortify/laravel 等）
```
