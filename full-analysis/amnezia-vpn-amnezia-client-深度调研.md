# 🔬 AmneziaVPN (amnezia-client) 深度调研

> **仓库地址**: https://github.com/amnezia-vpn/amnezia-client
> **Stars**: 13,710 ⭐ | **语言**: C++（Qt）| **许可证**: GPL-3.0 | **创建**: 不详（dev 分支活跃）
> **主页**: https://amnezia.org | **定位**: 最好的自托管 VPN 客户端

---

## 一、项目定位

AmneziaVPN 是**开源的 VPN 客户端，核心卖点是让你在自己的服务器上一键部署私有 VPN**——尤其强调**流量混淆（obfuscation）**，用于突破深度包检测（DPI）与网络审查。

---

## 二、项目亮点（差异化）

- 🚀 **一键自托管**：填入 IP + SSH 账号密码，自动在服务器装 Docker 容器并连上，零运维
- 🎭 **流量混淆协议矩阵**：OpenVPN-over-Cloak、OpenVPN-over-Shadowsocks、**AmneziaWG**（自研 WireGuard 混淆版）、XRay
- 🔀 **分流隧道（Split Tunneling）**：指定站点/App 才走 VPN（Android / 桌面）
- 📱 **全平台**：Windows / macOS / Linux / Android / iOS
- 🆓 **真正自由软件**：GPL-3.0，无订阅强制（另有 Premium 可选）

---

## 三、核心架构

```
AmneziaVPN 客户端（Qt6 C++）
   ├─ client/        ：Qt GUI（连接管理 / 协议选择 / 分流规则）
   ├─ service/       ：VPN 守护进程（拉起底层协议进程）
   ├─ ipc/           ：client ↔ service 进程间通信（权限分离）
   ├─ common/        ：协议抽象 / 配置模型
   └─ conanfile.py   ：Conan 管理 OpenSSL/WireGuard/Xray 等原生依赖
        │
        ▼ 通过 SSH 在用户服务器部署
    Docker 容器（OpenVPN / WireGuard / AmneziaWG / Xray / Cloak / SS）
```

**混淆核心**：AmneziaWG 是 WireGuard 的 fork，在握手/数据包外层叠加可配置的混淆层，使流量特征不像标准 WireGuard，从而绕开 DPI。这是相比「裸 WireGuard / 裸 OpenVPN」最大的差异化——普通 VPN 在审查环境下易被识别和封锁。

---

## 四、应用场景与启发

| 场景 | 适配度 |
|------|--------|
| 审查环境下突破封锁 | ⭐⭐⭐⭐⭐（AmneziaWG/XRay 专为此设计）|
| 个人私有 VPN（隐私）| ⭐⭐⭐⭐ |
| 企业站点到站点 | ⭐⭐⭐（通用协议即可）|
| 极简用户 | ⭐⭐⭐⭐（一键部署降低门槛）|

> **架构启发**：做"抗审查网络工具"时，Amnezia 的两个设计值得借鉴——① 把底层协议（WG/Ovpn/Xray）做成可插拔容器，混淆层独立叠加；② 客户端通过 SSH+Docker 把"部署"变成用户的一次性输入，极大降低自托管门槛。

---

## 五、源码解读（核心模块）

**1. 客户端 — `client/`**
Qt6 Widgets/QML GUI，管理服务器配置、协议下拉、分流规则。翻译文件在 `client/translations/*.ts`（社区共建）。

**2. 服务守护进程 — `service/`**
以独立进程运行（需提权），真正拉起底层协议进程；与 `client` 通过 `ipc/` 通信，实现 GUI 与特权操作的权限分离。

**3. 一键部署 — `deploy/` 脚本 + Docker**
客户端通过 LibSSH 连用户服务器，自动 `docker run` 对应协议镜像并完成握手配置，全程无需用户写命令。

---

## 六、社区口碑

- **审查规避圈口碑强**：在俄语区、伊朗、缅甸等被封锁地区有官方 Telegram 频道与活跃社区；Reddit r/AmneziaVPN 活跃
- **优点**：一键自托管真降低门槛、混淆协议在实战中有效、全平台 + 开源
- **短板**：相比商业 VPN 速度/稳定性依赖自建服务器；Qt6 + Conan 构建链偏重，编译门槛高；高级混淆配置对新手仍复杂

---

## 七、竞品对比 + 核心研判

| 项目 | 自托管 | 混淆 | 平台 | 许可 |
|------|--------|------|------|------|
| **AmneziaVPN** | ✅ 一键 | ✅ AmneziaWG/XRay | 全 | GPL-3.0 |
| **Outline (Jigsaw)** | ✅ | ⚠️ 弱（Shadowsocks）| 全 | Apache-2.0 |
| **Algo (Trail of Bits)** | ✅ | ❌ | 脚本 | MIT |
| **Streisand** | ✅ | ✅ | 脚本 | GPL-2.0 |
| **WireGuard 官方** | ✅ | ❌ 裸 | 全 | GPL-2.0 |

**核心研判**：
- ✅ **优势**：混淆协议矩阵（尤其 AmneziaWG）是审查环境下的关键差异；一键 Docker 部署把自托管门槛压到最低；真自由软件
- ⚠️ **风险**：依赖用户自建服务器质量；Qt/Conan 重构建链；混淆对抗是军备竞赛，需持续跟进 DPI 演进
- 💡 **启发**：做隐私/抗审查工具，"把复杂部署封装成一次输入" + "协议可插拔 + 混淆独立层"是该领域最稳的产品形态

---

## 八、关键文件路径速查

| 路径 | 内容 |
|------|------|
| `client/` | Qt6 GUI（连接/协议/分流）|
| `service/` | VPN 守护进程 |
| `ipc/` | client↔service 进程间通信 |
| `common/` | 协议抽象与配置模型 |
| `conanfile.py` | 原生依赖（OpenSSL/WG/Xray）|
| `deploy/` | 跨平台构建/打包脚本 |
| `cmake/` / `CMakeLists.txt` | 构建系统 |
| `docs/` / `metadata/` | 文档与发布素材 |
