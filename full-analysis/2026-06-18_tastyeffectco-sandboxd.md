# 🔍 深度调研报告：tastyeffectco/sandboxd

> **调研日期**: 2026-06-18
> **Stars**: 494 ⭐ (2026-06-08 Trending)
> **语言**: Go
> **简介**: 自托管开发沙箱，一键启动，无需 Kubernetes，为编码 Agent 和 SaaS 工厂而生

---

## 一、项目概述

sandboxd 是 AI 应用构建器的开源引擎。它做的事情非常直白：你发送一个 HTTP 请求，它就创建一个隔离的 Linux 沙箱，在里面运行 AI 编码 Agent，然后给你一个可分享的预览 URL。

**一句话**: 像 Lovable、Bolt、v0、Replit 那种"告诉我你要什么 → 秒出可访问的网站"的后端基础设施，在你的服务器上运行。

## 二、核心架构

```
┌──────────────── your host (just needs Docker) ────────────────┐
 browser ──▶│ Traefik ──▶ sandbox (coding agent + dev server :3000) │
            │             ▲            ▲              ▲             │
 API/CLI ──▶│ sandboxd ───┘            └─ workspace dir (persists)  │
            │           SQLite (source of truth) · idle→stop · request→wake  │
            └─────────────────────────────────────────────────────────-┘
```

### 组件堆栈
- **Go 控制平面** — 单一的 Go 程序，指挥 Docker
- **Traefik** — 处理 URL 路由和 TLS
- **SQLite** — 数据库（真相源）
- **Docker** — 容器运行时，无需 Kubernetes

## 三、核心技术特性

### 1. 多租户隔离
每个沙箱是独立的 Linux 容器，有自己的文件系统和资源限制，一个用户的代码不会影响另一个。

### 2. 内置编码 Agent
OpenCode 和 Claude Code CLI 预装在沙箱中。提交 prompt → Agent 在沙箱内写代码。

### 3. 预览 URL
沙箱内的开发服务器自动获得可分享的预览链接，无需端口管理。

### 4. 智能休眠
- 空闲沙箱自动停止 → 释放内存
- 访问链接时自动唤醒 → 磁盘上文件完好无损
- 一台普通服务器可承载数十个用户

### 5. 崩溃恢复
SQLite 是真相源；每次启动时 reconciler 将 Docker 状态收敛回数据库。

## 四、与轻量方案对比

| 场景 | 推荐方案 | 理由 |
|------|---------|------|
| 需要 1-2 个容器给自己用 | shell 脚本 / docker run | sandboxd 过度设计 |
| 为其他用户运行多个沙箱 | **sandboxd** ✅ | URL/TLS/休眠/恢复/API 全自动 |
| 构建 AI app-builder 产品 | **sandboxd** ✅ | 开箱即用的多租户基础设施 |
| 需要 Kubernetes | sandboxd 可适配 | 接口层面可替换容器后端 |

## 五、安装方式

```bash
# 一键安装
./install.sh
```

## 六、适用场景

- **AI App-Builder 产品**：作为"描述 → 预览"产品的后端
- **Agent Platform**：为每个用户/每次运行分配隔离环境
- **编码游乐场**：在线 IDE 的沙箱基础设施
- **预览环境**：按分支/用户分配临时预览 URL

## 七、为什么不直接用 shell 脚本？

当从 docker run 脚本增长为一套完整的基础设施时，你需要：
- 每个沙箱一个干净 URL + 自动 TLS（不是端口编排）
- 智能睡眠/唤醒（空容器 → 释放内存 → 透明重启）
- 崩溃后恢复（脚本在重启后忘光一切）
- 真实 HTTP API（create / exec / stop / run-agent-task）
- 跨用户隔离（内存/PID 限制 + 宿主机压力回收器）

沙箱团队把这些全部做成了 `./install.sh`，避免你从脚本逐步重新发明。

## 八、核心结论

sandboxd 的核心洞察是：AI app-builder 产品的瓶颈不在 prompt 质量，而在下层基础设施——多租户隔离、预览 URL、成本控制（空闲释放）、Agent 编排。它选择"无聊但可靠"的 SQLite + Docker CLI + Traefik 组合，用最少的移动部件解决这些问题。

**局限**: Beta 阶段；仅支持单台 Docker 主机（暂不原生支持 Kubernetes）；依赖 Docker 守护进程；不适合单用户单容器场景。
