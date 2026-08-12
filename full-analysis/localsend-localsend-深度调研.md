# LocalSend 深度调研

> 调研日期：2026-08-13 | 星标：87,688（2026-08-12）| 协议：Apache-2.0 | 语言：Dart（Flutter）+ Rust | 定位：开源 AirDrop 替代

## 一、项目定位

LocalSend 是**免费开源的本地网络文件/消息分享应用**：无需互联网、无需第三方服务器，用 REST API + HTTPS 加密在附近设备间安全通信。跨平台覆盖 Android / iOS / macOS / Windows / Linux / Fire OS，是目前 GitHub 上最受欢迎的开源 AirDrop 替代品。

## 二、项目亮点

1. **零服务器、零互联网**：纯本地网络 P2P，隐私最优，无内容经过第三方。
2. **跨平台一致体验**：Flutter 一套代码多端；Windows 二进制签名。
3. **加密传输**：每台设备**即时生成 TLS/SSL 证书**（on-the-fly），HTTPS 加密。
4. **开放协议**：LocalSend Protocol 独立仓库（localsend/protocol），可被其他实现复用。
5. **丰富分发**：商店/包管理器/便携版；Weblate 众包翻译（极高本地化覆盖）。
6. **工程细节**：便携模式（同目录 `settings.json`）、`--hidden` 启动、Quick Settings Tile。

## 三、核心架构

- **协议层**：LocalSend Protocol（基于 REST over HTTPS，设备发现用 multicast/broadcast + HTTPS 握手）。
- **应用层**：Flutter/Dart 写 UI 与业务逻辑；`app/lib/localsend_app/` 下 `providers/` 负责设备发现等；性能关键路径用 Rust（FFI）。
- **网络**：TCP/UDP 端口 **53317**，需防火墙放行；建议关闭路由器 AP 隔离。
- **密钥**：每设备自签证书，无 CA、无中心信任。
- **依赖层级**：见 `support/docs/dependency-hierarchy.svg`。

## 四、应用场景与启发

- **场景**：替代 AirDrop 做 Android↔桌面↔iOS 跨生态传文件；内网/无网环境传输；隐私敏感场景。
- **启发 1**："本地 P2P + 即时自签证书"是**零信任本地传输**的极简范式——无需 PKI 基础设施即可获得加密。
- **启发 2**：把协议独立成**开放标准**（localsend/protocol）值得借鉴：生态可被其他客户端复用，协议与实现解耦。
- **启发 3**：Flutter + Rust 混合在"跨端 UI + 原生性能"上很实用（Dart 写界面、Rust 写热点）。

## 五、源码深度解读

### 1. `app/lib/localsend_app/providers/nearby_devices_provider.dart` — 设备发现核心
基于 mDNS/multicast 周期性广播 + 监听，维护附近设备列表。这是"无服务器发现"的关键实现。

### 2. LocalSend Protocol（独立仓库 `localsend/protocol`）
定义 HTTP 端点（`/api/localsend/v2/...`）、握手流程、加密信封。这是 LocalSend **可互操作**的根基，也是"应用协议与实现解耦"的范例——任何遵循该协议的客户端都能互传。

### 3. `app/android/.../MainActivity.kt` + `QuickTileService.kt`
Android 端 Quick Settings Tile 快速发送，体现平台集成深度（不止"能跑"，而是融入系统交互）。

## 六、社区口碑

- 87k⭐，Repology 多发行版打包；Weblate 众包翻译（极高本地化）；Windows 二进制签名。
- 口碑：被誉为"**最接近 AirDrop 体验的开源方案**"，跨 Android/Windows/Linux 传输稳定。
- 已知限制：Android 接收速度偏慢（flutter-cavalry/saf_stream 已知 issue）；需手动配置防火墙/关 AP 隔离；无自动更新（建议走商店/包管理器）。

## 七、竞品对比 + 核心研判

| 维度 | LocalSend | Snapdrop/ShareDrop | Warpinator | KDE Connect |
|------|-----------|-------------------|------------|-------------|
| 跨平台 | 全平台 | 全平台（Web） | 仅 Linux 系 | 多平台（偏 Linux） |
| 服务器 | 无 | 公共信令服务器 | 无 | 无 |
| 隐私 | 纯本地 | 依赖公共服务 | 本地 | 本地 |

- **核心护城河**："原生 + 零服务器 + 开放协议"三角。护城河不深（协议简单易复制），但**先发网络效应 + 全平台覆盖 + 社区翻译**构成壁垒。
- **风险**：协议无强加密身份校验（自签证书仅加密不认证对端）；大文件无断点续传。
- **研判**：适合"不想用微信/网盘、又要跨设备传文件"的日常场景，是对隐私与易用平衡得最好的开源方案。

## 八、关键文件速查

- `app/lib/localsend_app/providers/nearby_devices_provider.dart` — 设备发现
- `app/lib/localsend_app/` — UI 与业务逻辑（Dart）
- `.fvmrc` — Flutter 版本锁
- `CODE_SIGNING.md` / `CONTRIBUTING.md#distribution` — 签名与分发
- 协议仓库：`github.com/localsend/protocol`（独立）
