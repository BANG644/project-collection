# localsend/localsend 深度调研

> 调研日期：2026-08-17（**本次为重写升级**，旧版 2026-08-13 存在架构事实错误，见文末勘误）
> ★ 88,486　|　Fork 4,909　|　Open Issues **1,075**　|　主语言 Dart（+ Rust 104 文件）　|　Apache-2.0
> 仓库：https://github.com/localsend/localsend
> 创建：2022-12-16　|　最近推送：2026-08-13　|　最新版 **v1.18.1 (2026-08-11)**
> Topics：`dart` `file-sharing` `flutter` `flutter-apps`

---

## 一、项目全景

LocalSend 是 GitHub 上最成功的开源 AirDrop 替代品：局域网内跨 Android / iOS / macOS / Windows / Linux / Fire OS 互传文件与消息，不经过任何第三方服务器。

**但如果你只看 README 或旧资料，你会完全错判它现在的技术形态。** 本次调研最重要的发现是：

> **LocalSend 在 2025-02 至 2026-08 这 18 个月里，把整个网络核心从 Dart 重写成了 Rust。仓库根目录现在是一个 Cargo workspace。**

证据链：

| 证据 | 说明 |
|---|---|
| 根目录 `Cargo.toml` + `Cargo.lock` + `rust-toolchain.toml` | 仓库**根级**就是 Rust workspace（`resolver = "3"`，toolchain 锁 `1.97.1` + clippy） |
| workspace members = `cli`, `packages/core`, `packages/localsend_isolates/rust`, `server` | 四个 Rust crate |
| `.rs` 文件 104 个 vs `.dart` 381 个 | Dart 仍占多数（UI/业务），但**所有网络协议实现已在 Rust 侧** |
| v1.17.0 (2025-02-19) → v1.18.0 (2026-08-10) | **17.7 个月无 release**，正是重写窗口 |
| `packages/localsend_isolates/rust/src/frb_generated.rs` | flutter_rust_bridge 自动生成的绑定 |

v1.18.0 的 changelog 第一条就是 `feat(cli): initial CLI release` —— 一个 Flutter 应用突然发布了 CLI，只有底层被抽成独立 Rust crate 才可能做到。

### 项目亮点（差异化）

| # | 亮点 | 说明 |
|---|---|---|
| 1 | **Rust 核心 + Flutter UI + 共享 crate** | `packages/core` 是纯 Rust 网络栈，同时被 Flutter app（经 FRB）、CLI、signaling server 复用 |
| 2 | **指纹即身份（TOFU）** | 自签 RSA-2048 证书，**SHA-256 DER 指纹作为设备唯一身份**；`CN=LocalSend User` 无任何有效信息，专门有 `v2_tls_pinning.rs` 集成测试 |
| 3 | **证书永不过期（1975→4096）** | 用 rcgen 默认有效期，刻意规避"证书过期导致传输失败"这类运维问题 |
| 4 | **协议 v2/v3 双栈并存** | `http/{client,server}/v2.rs` + `v3.rs` + `dto.rs`/`dto_v2.rs`，老版本客户端不掉线 |
| 5 | **内置 Web UI（无需装 App）** | Rust core 直接内嵌 `assets/web/{upload,download,error-403}.html`，对端用浏览器就能收发 |
| 6 | **WebRTC + 官方 signaling server** | `webrtc/{signaling,webrtc}.rs` + `server/`（Rust WebSocket + Dockerfile），支撑 v1.18.0 新增的"通过链接接收" |
| 7 | **自研 typed_isolates 包** | 把 Dart 裸 `Isolate`/`SendPort` 的 `dynamic` 消息包成三参数泛型 `<R, S, P>` 的类型安全通道，可独立发布（带独立 LICENSE/README） |
| 8 | **AI Agent 进入开发流程** | 根目录同时有 `CLAUDE.md` 和 `AGENTS.md` |

---

## 二、核心架构

### 2.1 全仓分层（1,024 文件）

```
localsend/
├── Cargo.toml            ← ★ Rust workspace 根（resolver 3）
├── rust-toolchain.toml   ← 锁 rustc 1.97.1 + clippy
├── CLAUDE.md / AGENTS.md ← AI coding agent 指令
├── app/            588 文件  Flutter 应用（Dart UI + 平台原生：11 swift / 5 cpp / 4 kt）
├── packages/       215 文件
│   ├── core/               61  ★ Rust 网络核心（crypto/discovery/http/multicast/webrtc/model）
│   ├── localsend_isolates/142     Dart isolate 层 + Rust FRB 绑定 + cargokit 构建
│   └── typed_isolates/     12     类型安全 isolate 封装（自研通用包）
├── cli/             22 文件  ★ Rust CLI（v1.18.0 首发）
├── server/          14 文件  ★ Rust WebSocket signaling server（含 Dockerfile）
├── support/        134 文件  文档、脚本、依赖层级图
├── fastlane/        17 文件  应用商店元数据
└── .github/         21 文件  CI
```

### 2.2 `packages/core` —— Rust 网络核心（本项目真正的心脏）

```
packages/core/src/
├── lib.rs
├── crypto/
│   ├── cert.rs        ★ 自签证书生成 + 指纹计算 + 验证（285 行）
│   ├── hash.rs           校验和（v1.18.0 新增 checksum 功能）
│   ├── nonce.rs          防重放
│   └── token.rs          会话令牌
├── discovery/
│   ├── mod.rs            发现主流程
│   └── store.rs          设备表
├── multicast/
│   ├── mod.rs
│   └── socket.rs      ★ v4/v6 组播套接字绑定（155 行）
├── http/
│   ├── client/{mod,v2,v3,url,scoped_host,server_cert_verifier}.rs
│   ├── server/
│   │   ├── {mod,v2,v3,web,internal,peer_ip,state}.rs
│   │   └── common/{client_cert_verifier,session,save,pin,query,response,error,collect_to_json}.rs
│   └── {dto,dto_v2}.rs
├── webrtc/{mod,signaling,webrtc}.rs    ← 链接分享 / 跨网段
├── model/{discovery,transfer,mod}.rs
└── util/{base64,error,filename,interface,time}.rs
├── assets/web/{upload,download,error-403}.html   ← 内嵌浏览器 UI
├── examples/stress_send.rs                        ← 压测示例
└── tests/  9 个集成测试（见 §3）
```

**关键观察**：`client_cert_verifier.rs`（服务端验客户端）+ `server_cert_verifier.rs`（客户端验服务端）**同时存在** → 双向证书校验。这直接推翻旧报告"自签证书仅加密不认证对端"的判断。

### 2.3 设备身份：指纹即一切

`crypto/cert.rs` 的文档注释把设计意图写得很清楚（原文摘录 + 关键实现）：

```rust
/// A freshly generated device identity: an RSA-2048 key pair and a
/// self-signed certificate whose SHA-256 fingerprint identifies the device.
pub struct SelfSignedCert {
    /// The SHA-256 fingerprint of the certificate in DER format,
    /// encoded as uppercase hex.
    pub fingerprint: String,
    ...
}

/// - RSA-2048, matching the certificates the Flutter app has historically
///   [generated]
/// - `CN=LocalSend User` and no SANs: peers identify each other purely by the
///   certificate fingerprint, so the name carries no information.
/// - Validity is rcgen's default (1975 to 4096), so certificates do not expire
pub fn generate_self_signed() -> anyhow::Result<SelfSignedCert> {
    let mut rng = rsa::rand_core::OsRng;
    let private_key = rsa::RsaPrivateKey::new(&mut rng, 2048)?;
    ...
    let certificate = params.self_signed(&key_pair)?;
    Ok(SelfSignedCert {
        fingerprint: fingerprint_from_cert_der(certificate.der()),
        ...
    })
}

/// Computes the SHA-256 fingerprint of a certificate in DER format.
/// Encoded as uppercase hex, the format used for LocalSend fingerprints.
pub fn fingerprint_from_cert_der(cert: &[u8]) -> String { ... }
```

三个刻意的设计决断：

| 决断 | 理由 |
|---|---|
| **RSA-2048 而非 ECDSA** | 注释明说是为了「matching the certificates the Flutter app has historically generated」——**向后兼容优先于密码学时髦**。代价：RSA 密钥生成在移动端慢，所以根 `Cargo.toml` 专门为 dev profile 开了优化（见 §2.6） |
| **`CN=LocalSend User`，无 SAN** | 证书里**故意不放任何可识别信息**，身份完全由指纹承载。副作用：任何标准 TLS 客户端都会拒绝这个证书，所以必须自定义 verifier |
| **有效期 1975→4096** | 证书永不过期。运维上是对的（没人愿意因为证书过期传不了文件），密码学上意味着密钥泄露后无自动失效 |

**安全模型准确表述**：TOFU（Trust On First Use）+ 指纹钉扎。不是"仅加密不认证"，而是"认证锚点是指纹而非 CA"。`tests/v2_tls_pinning.rs` 专门测这条路径。

### 2.4 组播发现：绕过 Windows 的坑

`multicast/socket.rs`（155 行）里一行注释解释了所有跨平台组播代码都要处理的问题：

```rust
fn bind_multicast_socket_v4(...) -> ... {
    // All sockets share the same port. Windows has no `SO_REUSEPORT`.
    ...
    socket.join_multicast_v4(&group, &interface)?;
}

fn bind_multicast_socket_v6(...) -> ... {
    socket.join_multicast_v6(&group, interface)?;
}
```

`bind_multicast_sockets()` 统一入口 → 按接口枚举（`util/interface.rs`）逐个绑定 v4/v6。v1.18.0 的 `feat: ipv6 support` 就落在这里。

**为什么这件事很难**：多网卡（有线 + WiFi + VPN 虚拟网卡）环境下，组播必须逐接口 join，否则只有默认路由那张网卡能收到。这正是 issue #1598（VPN 下无法发现，23💬）和 #654（手机 WiFi ↔ PC 网线，18💬）的根因所在。

### 2.5 Dart ↔ Rust 桥：typed_isolates + FRB + cargokit

三层结构，各管一段：

**① `packages/typed_isolates`（自研通用包，12 文件）** —— 解决 Dart 原生 isolate 无类型的问题。README 原文：

> Dart's raw `Isolate` / `SendPort` API is untyped — every message is `dynamic`.
> This package wraps the boilerplate and gives you a connector with statically-typed send and receive channels.
>
> - `R` — the type of messages the main isolate **receives** from the child.
> - `S` — the type of messages the main isolate **sends** to the child.
> - `P` — the type of the parameter passed to the child on startup.

```dart
final connector = await TypedIsolates.startIsolate<int, String, String>(
  param: 'greeting',
  task: _childTask,
);
connector.receiveFromIsolate.listen((value) => print('main received: $value'));
connector.sendToIsolate('hello');
```

**这个包有独立 LICENSE 和 README，说明是打算独立发布给整个 Flutter 社区的**——一个应用项目顺手解决了语言级痛点。

**② `packages/localsend_isolates/rust/src/api/`（13 个 Rust 模块）** —— FRB 暴露给 Dart 的 API 面：

```
cancel.rs  crypto.rs  discovery.rs  filename.rs  http.rs  logging.rs
metadata.rs  model.rs  server.rs  stream.rs  webrtc.rs  mod.rs
frb_generated.rs   ← flutter_rust_bridge 自动生成
```

`stream.rs` + `cancel.rs` 的存在说明传输进度是以 Rust→Dart 流的方式回推，且支持取消——对应 changelog 里 `fix: receiving / sending many files no longer freeze / lag`。

**③ `rust_builder/cargokit/`（32 文件）** —— cargokit（irondash 生态）负责五平台 Rust 交叉编译：`android/build.gradle`、`ios/`、`macos/build_pod.sh`、`windows/`、`linux/`。这是 Flutter+Rust 项目最脏的一块，用现成方案是明智的。

### 2.6 构建配置里的两处硬核细节

根 `Cargo.toml`（注释是作者亲手写的，值得原文引用）：

```toml
[workspace]
resolver = "3"
members = ["cli", "packages/core", "packages/localsend_isolates/rust", "server"]

# Full debuginfo dominates target/ size; line tables keep backtraces usable.
[profile.dev]
debug = "line-tables-only"

# RSA key generation is bignum-heavy and takes ~10x longer unoptimized;
# keep the crypto crates optimized in dev so tests stay fast.
[profile.dev.package.rsa]
opt-level = 2

[profile.dev.package.num-bigint-dig]
opt-level = 2
```

两个精准优化：`debug = "line-tables-only"` 大幅缩小 `target/`（对 CI 缓存很关键）；**只给 `rsa` 和 `num-bigint-dig` 两个包开 opt-level=2**，因为 §2.3 里选了 RSA-2048，debug 模式下密钥生成慢 10 倍会拖死测试。这种"按包精确开优化"的写法，是踩过坑才会有的。

### 2.7 Signaling Server：所以它不是"零服务器"

`server/README.md` 全文只有一句：

> # LocalSend Signaling Server
> A signaling server for LocalSend. Using Rust and WebSockets.

结构：

```
server/
├── Cargo.toml    Dockerfile    README.md
├── src/main.rs
├── src/controller/ws_controller.rs      ← WebSocket 控制器
├── src/config/{init,state,scheduler,error,mod}.rs
└── src/util/{base64,ip,mod}.rs
```

**准确表述**：
- **局域网直传** = 真正无服务器（组播发现 + 直连 HTTPS）✅
- **"通过链接接收"/ 跨网段** = 需要 signaling server 做 WebRTC 信令 ⚠️

`config/scheduler.rs` 说明服务端有定时任务（清理过期会话）。有 Dockerfile → 鼓励自托管，隐私可控。但"零服务器"这个说法在 v1.18.0 之后**已不完全成立**。

---

## 三、测试与工程化

`packages/core/tests/` 9 个集成测试，命名本身就是可靠性清单：

| 测试文件 | 测什么 | 为什么值得注意 |
|---|---|---|
| `discovery.rs` | 设备发现 | — |
| `multicast.rs` | 组播套接字 | 跨平台组播是第一大 bug 源 |
| `v2_server.rs` | 协议 v2 服务端 | 向后兼容保障 |
| **`v2_tls_pinning.rs`** | **证书指纹钉扎** | ⭐ 证明指纹校验是被测行为，不是宣传话术 |
| `v2_web_send.rs` | 浏览器发送路径 | 内嵌 Web UI 的回归 |
| `internal_server.rs` | 内部端点 | — |
| `hash.rs` | 校验和 | v1.18.0 新功能 |
| **`accept_resilience.rs`** | **接受流程韧性** | ⭐ 专门测异常/中断，不只测 happy path |
| **`event_backpressure.rs`** | **事件背压** | ⭐ 传大量文件时事件洪泛的防护——对应 `fix: receiving / sending many files no longer freeze / lag` |

加上 `examples/stress_send.rs` 压测示例。**`accept_resilience` + `event_backpressure` 这两个测试的存在，是判断一个项目"是否认真对待可靠性"的强信号**——绝大多数同类项目只测正常流程。

---

## 四、应用场景与启发

### 4.1 直接使用场景

| 场景 | 说明 |
|---|---|
| 跨生态传文件 | Android ↔ Windows ↔ iOS ↔ Linux，AirDrop 的通用替代 |
| **无网络环境传输** | 只要在同一个 WiFi/热点下即可，不需要互联网 |
| 隐私敏感传输 | 内容不经第三方（局域网模式） |
| **对方没装 App** | 内嵌 Web UI，对端浏览器打开链接即可收发 |
| **服务器/CI 环境** | v1.18.0 起有 Rust CLI，可脚本化 |
| 自托管信令 | `server/` 带 Dockerfile，企业可自建 |

### 4.2 可以偷走的思想

1. **把核心抽成语言中立的 crate，UI 只是消费者之一。** LocalSend 最漂亮的一步：`packages/core` 一份 Rust 代码同时喂 Flutter app、CLI、server 三个消费者。**任何"想做 GUI 又想做 CLI"的项目都该照这个分层。** 判断标准很简单：你的 CLI 能不能在不复制任何逻辑的前提下发布出来？
2. **指纹即身份，绕过 PKI。** 不需要 CA、不需要域名、不需要证书续期，SHA-256 DER 指纹就是设备 ID。这是 P2P/IoT/局域网场景的正确答案（SSH 用了 30 年的模式）。配合"证书永不过期"，把运维复杂度压到零。
3. **向后兼容可以压倒密码学时髦。** 明知 ECDSA 更好，仍选 RSA-2048，就因为"历史上 Flutter app 生成的是这个"。然后用构建配置（`opt-level=2` for rsa）解决它带来的性能问题。**这是成熟工程的取舍方式：不为技术正确破坏用户升级路径，用工程手段消化代价。**
4. **给无类型 API 加类型层，并独立成包。** `typed_isolates` 是"顺手把语言的坑填了，还包装成社区可用的礼物"。这种副产品往往比主项目影响面更广。
5. **协议版本号进目录结构。** `v2.rs` / `v3.rs` / `dto_v2.rs` 平级共存，而不是靠 if-else 分支。新旧协议物理隔离，删旧版就是删文件。
6. **背压和韧性要有专门测试。** `event_backpressure.rs` / `accept_resilience.rs` 这类测试名字本身就是设计文档。
7. **构建 profile 按包精调。** `[profile.dev.package.rsa] opt-level = 2` —— 只优化慢的那个依赖，既保留 debug 体验又不牺牲测试速度。很少有人知道 Cargo 能这么用。

---

## 五、社区口碑

### 5.1 发布节奏（信息量最大的一张表）

| 版本 | 日期 | 间隔 | 性质 |
|---|---|---|---|
| v1.16.1 | 2024-11-05 | — | 常规 |
| v1.17.0 | 2025-02-20 | 3.5 月 | 常规（**修了 path traversal 漏洞**） |
| **v1.18.0** | **2026-08-10** | **17.7 月** | ⭐ Rust 核心重写 + CLI 首发 + IPv6 + checksum |
| v1.18.1 | 2026-08-12 | 2 天 | 移动端 hotfix |
| 1.18.2 | 未发布 | — | 修代理兼容 + **不再跟随 peer 的 HTTP 重定向**（安全加固） |

近 18 个月的沉默不是停滞，是在做地基。v1.18.0 的 changelog 有 **30+ 条**，且大量署名外部贡献者（@ShlomoCode 一人贡献 8 条、@kartoshka95、@Voltra、@nixigaj、@chenxdust……），社区活性很高。

v1.18.2 的 `fix: do not follow HTTP redirects sent by peers` 值得单独指出——**这是防止恶意 peer 用重定向把你的上传引到外部服务器**，属于主动安全加固。

### 5.2 Issue 热度榜（1,075 open）

| Issue | 💬 | 标题 | 分类 |
|---|---|---|---|
| #125 | **57** | Socket Exception (Forbidden access) | 🔴 发现/权限 |
| #345 | 34 | Roadmap | 规划 |
| #850 | 27 | Feature request: Bluetooth Discovery | 功能 |
| #300 | 27 | UI Redesign | 设计 |
| #1598 | 23 | Cannot discover other devices on **VPN** | 🔴 发现 |
| #1575 | 23 | Main window not appearing | 桌面端 |
| #2746 | 22 | SocketException: Failed to create server socket (**errno 10013**), port 53317 | 🔴 发现/权限 |
| #168 | 21 | Connection refused | 🔴 发现 |
| #1591 | 20 | [500] Could not save file | 接收 |
| #654 | 18 | Cannot send from phone (WiFi) to PC (**ethernet**) | 🔴 发现 |
| #527 | 18 | Cannot discover other devices | 🔴 发现 |
| #2951 | 17 | Can't receive the file? | 接收 |

**结论极其清晰：Top 12 里 6 条是"发现不到设备"，占一半。** errno 10013 是 Windows 上端口 53317 被防火墙/其他进程/权限策略拦截；VPN 和多网卡场景组播不通。

这**不是代码 bug，而是这类产品的结构性天花板**：LocalSend 依赖组播发现，而组播在现代网络环境（AP 隔离、VPN 虚拟网卡、企业网策略、Windows 防火墙、Android 17+ 新增 `ACCESS_LOCAL_NETWORK` 权限）里越来越不可靠。#850 请求 Bluetooth Discovery（27💬）正是社区对此的自发解法呼声。

其他生态信号：Weblate 众包翻译（v1.18.1 一次就新增白俄罗斯语、爱尔兰语）；Repology 多发行版打包；Windows 二进制代码签名（`CODE_SIGNING.md`）；`fastlane/` 17 文件做商店元数据自动化。

---

## 六、竞品对比

| 维度 | **LocalSend** | Snapdrop / PairDrop | Warpinator | KDE Connect | AirDrop | Syncthing |
|---|---|---|---|---|---|---|
| 平台覆盖 | **全六平台原生** | 全平台（浏览器） | 仅 Linux/Win 移植 | 多平台（偏 Linux） | 仅 Apple | 全平台 |
| 局域网直传免服务器 | ✅ | ❌ 需信令服务器 | ✅ | ✅ | ✅ | ✅ |
| **链接/跨网段** | ⚠️ 需 signaling（可自托管） | ✅（公共服务器） | ❌ | ❌ | ❌ | ✅（relay） |
| 加密与身份 | TLS + **SHA-256 指纹 TOFU** | TLS（服务器可见元数据） | TLS + 组码 | TLS + 配对 | 苹果 PKI | TLS + 设备 ID |
| 无需装 App | ✅ **内嵌 Web UI** | ✅ 天然浏览器 | ❌ | ❌ | ❌ | ❌ |
| CLI | ✅ v1.18.0 起 | ❌ | ❌ | ✅ | ❌ | ✅ |
| 核心实现语言 | **Rust**（UI: Flutter） | JS | Python/GTK | C++/Qt | 闭源 | Go |
| 持续同步 | ❌（单次传输） | ❌ | ❌ | ⚠️ 部分 | ❌ | ✅ 主打 |
| 断点续传 | ❌ | ❌ | ❌ | ❌ | — | ✅ |
| 发现可靠性 | ⚠️ 组播依赖（第一大痛点） | ✅ 服务器撮合最稳 | ⚠️ | ⚠️ | ✅ 系统级 | ✅ 有 relay 兜底 |
| 星标 | **88.5k** | ~19k / ~7k | ~2k | ~2k | — | ~70k |

**定位判断**：
- vs **PairDrop/Snapdrop**：LocalSend 赢在原生体验和隐私（不经服务器），输在发现可靠性（浏览器方案由服务器撮合，从不"找不到设备"）。
- vs **Syncthing**：完全不同定位。LocalSend 是"传一次就走"，Syncthing 是"持续同步"。Syncthing 有 relay 和断点续传，LocalSend 有零配置和 6 平台原生 UI。
- vs **AirDrop**：LocalSend 是唯一真正跨生态的替代，但苹果的系统级发现（BLE + AWDL）在可靠性上仍不可比——这也正是 #850 想引入 Bluetooth 的原因。

---

## 七、核心研判

### 护城河（重新评估，比旧版判断更深）

1. **网络效应 + 全平台原生。** 88.5k star / 4.9k fork，六平台商店 + 各发行版包管理器 + Weblate 多语言。协议本身简单可复制，但"对方设备上也装着 LocalSend"这件事无法复制。
2. **⭐ Rust 核心是新增的、且是真实的技术壁垒。** 这是本次调研相对旧版的最大认知升级：一份 Rust crate 同时驱动 Flutter app / CLI / server，意味着后续做浏览器扩展（WASM）、NAS 插件、路由器固件、嵌入式接收端都是**增量成本**而非重写。竞品要追平，得先做同样的 18 个月重构。
3. **协议 v2/v3 双栈 + 证书永不过期。** 老设备永远能连上新设备，升级零摩擦。这是"用户不会因为升级而流失"的工程保障。
4. **工程严肃性可验证。** `event_backpressure.rs`、`accept_resilience.rs`、`v2_tls_pinning.rs`、`stress_send.rs`、按包精调的 build profile——这些不是宣传，是可以在仓库里读到的证据。

### 风险

| 风险 | 严重度 | 说明 |
|---|---|---|
| **组播发现的结构性天花板** | 🔴 高 | Top 12 issue 半数是发现失败；VPN / 多网卡 / AP 隔离 / Windows errno 10013 / Android 17+ 新权限，环境只会越来越严。这不是能靠修 bug 解决的问题 |
| **1,075 open issues** | 🟠 中 | 相对 88.5k star 不算失控，但 #125 挂了很久（57💬），说明最痛的问题最难解 |
| **无断点续传** | 🟠 中 | 大文件传到 90% 断网就重来。移动场景下是真实痛点 |
| **"链接分享"引入服务器依赖** | 🟠 中 | 隐私叙事被稀释；虽可自托管，但普通用户会用官方实例 |
| **RSA-2048 + 永不过期** | 🟡 低 | 兼容性换来的技术债；密钥泄露无自动失效机制 |
| **17.7 个月无 release** | 🟡 低 | 期间用户只能用旧版或自编译；已随 1.18.0 缓解，但显示大重构期的发布纪律缺口 |
| **重构后回归风险** | 🟡 低 | v1.18.1 在 v1.18.0 发布 2 天后就出移动端 hotfix，1.18.2 又在修代理兼容 —— 大重写后的余震仍在 |

### 谁该用 / 不该用

- ✅ **该用**：需要跨生态传文件的所有人；企业内网（可自托管 signaling）；需要脚本化传输的（CLI）；对方没装 App 的场景（Web UI）。
- ⚠️ **谨慎**：VPN 常开 / 复杂多网卡环境（发现大概率失败，需手动填 IP）；经常传超大文件（无断点续传）；企业网严格策略下（组播被封）。
- ❌ **不该用**：需要持续双向同步的（用 Syncthing）；需要跨互联网大规模传输的（用网盘/rsync）；不能容忍任何服务器参与的同时又要用链接分享的（自相矛盾，选局域网模式）。

### 一句话研判

**LocalSend 在 2026 年已经不是"一个 Flutter 应用"，而是"一个 Rust 网络协议实现 + 六平台前端"。** v1.18.0 那 17.7 个月的沉默买来的是可复用内核——CLI、signaling server、内嵌 Web UI 都是同一份 Rust 代码的产物，这才是它相对所有竞品真正拉开的距离。它最大的敌人也从来不是竞品，而是**现代网络环境对组播的持续绞杀**：Top issue 半数是"找不到设备"，而这不是 bug，是架构的物理边界。#850（蓝牙发现）是否落地，很可能决定它下一个五年的体验上限。

---

## 八、关键文件路径速查

| 路径 | 说明 |
|---|---|
| `Cargo.toml`（根） | ⭐ Rust workspace 定义（4 members）+ 按包精调的 dev profile |
| `rust-toolchain.toml` | 锁 rustc 1.97.1 + clippy |
| `packages/core/src/crypto/cert.rs` | ⭐ **最值得读**（285 行）：RSA-2048 自签、SHA-256 DER 指纹、`CN=LocalSend User`、有效期 1975→4096、`verify_cert_from_{pem,der}` |
| `packages/core/src/multicast/socket.rs` | ⭐ 155 行：v4/v6 逐接口 join，`// Windows has no SO_REUSEPORT` |
| `packages/core/src/discovery/{mod,store}.rs` | 发现主流程 + 设备表 |
| `packages/core/src/http/client/server_cert_verifier.rs` | 客户端验服务端证书（指纹钉扎实现） |
| `packages/core/src/http/server/common/client_cert_verifier.rs` | 服务端验客户端证书（双向校验） |
| `packages/core/src/http/{client,server}/v2.rs` / `v3.rs` | 协议 v2/v3 双栈 |
| `packages/core/src/http/server/common/{pin,session,save}.rs` | PIN 码保护 / 会话 / 落盘（v1.17.0 修 path traversal 的地方） |
| `packages/core/src/http/server/web.rs` + `assets/web/*.html` | 内嵌浏览器 UI（upload / download / error-403） |
| `packages/core/src/webrtc/{signaling,webrtc}.rs` | WebRTC 链接分享 |
| `packages/core/tests/v2_tls_pinning.rs` | ⭐ 指纹钉扎集成测试（证明安全模型可验证） |
| `packages/core/tests/{event_backpressure,accept_resilience}.rs` | ⭐ 背压 / 韧性测试 |
| `packages/core/examples/stress_send.rs` | 压测示例 |
| `packages/localsend_isolates/rust/src/api/*.rs` | 13 个 FRB 暴露模块（cancel/crypto/discovery/http/server/stream/webrtc/metadata/filename/logging/model） |
| `packages/localsend_isolates/rust/src/frb_generated.rs` | flutter_rust_bridge 自动生成绑定 |
| `packages/localsend_isolates/rust_builder/cargokit/` | 五平台 Rust 交叉编译（32 文件） |
| `packages/typed_isolates/` | ⭐ 自研类型安全 isolate 包（`<R,S,P>` 三泛型，可独立复用） |
| `cli/src/app/{discovery,sending,receive,devices,status,web_link}.rs` | Rust CLI 命令实现（v1.18.0 首发） |
| `cli/src/storage/{config,identity,paired}.rs` | CLI 侧配置 / 设备身份 / 已配对设备持久化 |
| `server/src/controller/ws_controller.rs` | Signaling server WebSocket 控制器 |
| `server/Dockerfile` | 自托管信令服务器 |
| `CHANGELOG.md` | ⭐ 判断项目真实演进的最佳入口（v1.18.0 那 30+ 条） |
| `CLAUDE.md` / `AGENTS.md` | AI coding agent 开发指令 |
| `support/docs/dependency-hierarchy.svg` | 依赖层级图 |
| `CODE_SIGNING.md` | Windows/macOS 签名流程 |

**端口**：TCP/UDP **53317**（防火墙需放行；Windows errno 10013 = 该端口被拦或占用）。
**协议规范**：独立仓库 https://github.com/localsend/protocol

---

## 九、勘误（相对 2026-08-13 旧版）

本次重写修正了旧报告的三处事实错误，记录在此以免再犯：

| # | 旧版表述 | 实际情况 |
|---|---|---|
| 1 | 「性能关键路径用 Rust（FFI）」「Flutter + Rust 混合，Dart 写界面、Rust 写热点」 | ❌ **不是"热点加速"**。整个网络协议栈（crypto / discovery / multicast / http v2+v3 / webrtc）都在 Rust；根目录即 Cargo workspace，含 4 个 crate；Dart 只剩 UI 与业务编排。是**核心重写**，不是局部加速 |
| 2 | 「零服务器、零互联网」 | ⚠️ **不完整**。局域网直传确实无服务器；但 v1.18.0 的"通过链接接收"依赖官方 Rust WebSocket signaling server（`server/`，带 Dockerfile，可自托管） |
| 3 | 「协议无强加密身份校验（自签证书仅加密不认证对端）」 | ❌ **错误**。设备身份 = 证书 DER 的 SHA-256 指纹（TOFU/pinning），客户端与服务端各有 cert verifier，并有 `tests/v2_tls_pinning.rs` 专项测试。准确说法是"信任锚是指纹而非 CA" |

补充：旧版遗漏了 v1.18.0 这次结构性重写、Rust CLI 首发、IPv6 / checksum 等新能力、`typed_isolates` 自研包、以及"发现失败占据 issue 榜半数"这一最关键的社区信号。
