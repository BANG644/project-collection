# WechatOnCloud (云微) 全方位深度调研报告

> **仓库**: [Gloridust/WechatOnCloud](https://github.com/Gloridust/WechatOnCloud)
> **调研日期**: 2026-06-17
> **分类**: 云微信 / Docker 应用 / NAS 工具

---

## 1. 项目定位

WechatOnCloud（云微，简称 WOC）是一个**在 NAS 或服务器上运行"服务端微信"的开源方案**，通过 Docker 容器化部署，支持多端浏览器共享同一微信会话，同时可作为 Chromium 浏览器实例登录 Telegram/X/Instagram 等网页版社媒。

**一句话定位**：让你在浏览器里随时随地用微信，不占手机。

**目标用户**：
- NAS 用户（飞牛 OS、群晖等）
- 需要 7×24 在线微信的用户
- 多设备共享同一微信会话的场景
- 需要云端运行网页版社媒的用户

**社区**：Telegram 交流群 [@WechatOnCloud](https://t.me/WechatOnCloud)

---

## 2. 核心架构

### 工作原理

每个实例 = 一个 Docker 容器，里面运行：
1. **Xvfb** — 虚拟显示（无头 X 服务器）
2. **微信官方 Linux 版** 或 **Chromium 浏览器**
3. **KasmVNC** — 将画面串流到浏览器

面板（自研 `woc-panel`）是唯一对外入口，通过 `docker.sock` 按需创建/销毁实例并反向代理。

```
用户浏览器 → [面板 :36080] → docker.sock → 实例容器
                                 ├─ 微信实例 (Xvfb + 微信 + KasmVNC)
                                 └─ 浏览器实例 (Xvfb + Chromium + KasmVNC)
```

### 技术栈

| 层 | 技术 |
|----|------|
| 面板 | Python Flask + Docker SDK |
| 容器 | Docker + docker-compose |
| 远程桌面 | KasmVNC |
| 虚拟显示 | Xvfb |
| PWA | Service Worker + Manifest |
| 多架构 | amd64 / arm64 预构建镜像 |

---

## 3. 核心功能

### 多实例管理
- 一个面板管理多个独立实例，每个实例独立容器 + 数据卷
- 新建实例可选「微信」或「Chromium 浏览器」

### 多端共享
- 多浏览器/设备共享同一会话
- 子账号体系（RBAC），按账号分配实例访问权限

### PC 式界面
- 左侧实例栏 + 右侧内嵌桌面
- 侧栏可折叠，移动端自动转抽屉
- 实例图标可自定义

### 微信按需下载
- 镜像不打包微信，面板一键下载安装
- 带进度条、按架构自动取包

### 其他特性
- 文件传输（拖拽上传/下载）
- 文本剪贴板中转
- 多端协作软锁（自动只读 + 申请接管）
- PWA 支持（iOS/Chrome 安装为 App）
- 设备伪装（machine-id / hostname / os-release）

---

## 4. 部署方式

### 方式 A：本地构建

```bash
git clone https://github.com/Gloridust/WechatOnCloud.git
cd WechatOnCloud
cp .env.example .env
./scripts/build-local.sh
docker compose up -d
```

### 方式 B：拉取官方镜像（推荐）

```bash
mkdir woc && cd woc
curl -fsSL https://raw.githubusercontent.com/Gloridust/WechatOnCloud/main/docker-compose.yml -o docker-compose.yml
docker compose up -d
```

访问 `http://<NAS_IP>:36080`，默认管理员 `admin / wechat`。

---

## 5. 安全设计

| 特性 | 说明 |
|------|------|
| 单入口 | 面板是唯一对外端口 |
| KasmVNC 凭据 | 服务端注入，永不下发前端 |
| docker.sock 管控 | 仅管理员可触达 |
| 独立数据卷 | 各实例数据隔离 |
| 子账号 RBAC | 权限精确到实例级别 |

---

## 6. 社区口碑

- GitHub Stars 增长迅速，定位精准
- 文档详尽（运行原理、部署运维、设备伪装、数据卷管理、技术方案）
- 社区活跃（Telegram 交流群）
- 预构建多架构镜像（GitHub Actions 自动发布）
- 被广泛用于飞牛 NAS 用户群体

---

## 7. 竞品对比

| 项目 | 方式 | 多实例 | 多端共享 | 开源 | 部署难度 |
|------|------|--------|----------|------|----------|
| **WechatOnCloud** | Docker + VNC | ✅ | ✅ | ✅ MIT | 低 |
| **Docker-微信** | Docker 直跑 | ❌ | ❌ | ⚠️ | 中 |
| **微信网页版** | Web | ❌ | ❌ | ❌ | 极低 |
| **微信 PC 版** | 原生 | ❌ | ❌ | ❌ | 极低 |

---

## 8. 核心研判

**优势**：
- 精准满足 NAS 用户"云端微信"的需求
- 架构设计优秀（容器隔离、面板管控、VNC 串流）
- 文档极其完善，新手友好
- 多架构支持（amd64/arm64）
- 活跃的社区和更新

**劣势**：
- 依赖微信 Linux 版，可能受微信官方策略影响
- 需要一定的 Docker 基础知识
- 浏览器实例需额外配置
- 首次镜像拉取可能因网络问题失败（有详细解决方案）

**适用场景**：
- NAS 用户的 7×24 云端微信
- 团队共享的微信/社媒账号管理
- 多设备间保持同一会话的办公场景

---

## 9. 关键文件路径

| 文件 | 说明 |
|------|------|
| `docker-compose.yml` | 主编排文件 |
| `.env.example` | 环境变量模板 |
| `doc/运行原理.md` | 架构与原理 |
| `doc/部署与运维.md` | 部署指南 |
| `doc/设备伪装.md` | 风控应对 |
| `doc/技术方案.md` | 完整设计文档 |
