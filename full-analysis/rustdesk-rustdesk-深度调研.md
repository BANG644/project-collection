# RustDesk 深度调研

> 调研日期：2026-08-15 ｜ 星标：120,559 ⭐ ｜ 协议：AGPL-3.0 ｜ 语言：Rust（核心）+ Flutter（UI）
> 仓库：`rustdesk/rustdesk` ｜ 默认分支：`master` ｜ 官网：rustdesk.com

## 一、项目定位（一句话）

用 Rust 从零重写的开源远程桌面，**TeamViewer / AnyDesk 的自托管替代品**——开箱即用、端到端加密、P2P 直连优先、中继可自建，数据完全自控。

## 二、项目亮点（差异化）

1. **完全自托管 + 开箱即用**：可用官方免费 rendezvous/relay 服务器，也可一键自建（`rustdesk-server`），甚至自己写中继服务器。
2. **真正跨全平台**：Windows / macOS / Linux / iOS / Android / Web 统一覆盖，Rust 核心 + Flutter UI 双层。
3. **全链路自研能力库**：视频编解码（VP8/VP9/AV1 软解 + H264/H265 硬解）、屏幕捕获、键鼠注入、剪贴板、文件传输全部为自研 `libs/`，不依赖 TeamViewer/AnyDesk 的任何闭源组件。
4. **AGPL-3.0 全开源**：相比闭源商业远程桌面，审计与可控性彻底打开。
5. **细粒度服务拆分**：音频/剪贴板/输入/视频/显示各自独立服务与连接，故障隔离清晰。

## 三、核心架构

RustDesk 的分层非常清晰，README 的 "File Structure" 章节已给出权威映射：

- **`libs/` 能力库（Rust）**
  - `libs/hbb_common`：视频编解码、配置、TCP/UDP wrapper、protobuf、文件传输 fs 函数及工具函数（最核心的公共底座）
  - `libs/scrap`：屏幕捕获
  - `libs/enigo`：平台相关键鼠控制
  - `libs/clipboard`：Win/Linux/macOS 跨平台文件复制粘贴
  - `libs/virtual_display`、`libs/remote_printer`、`libs/portable` 等：虚拟显示、远程打印、便携化
- **`src/` Rust 核心**
  - `src/core_main.rs`：Flutter 与（已废弃）Sciter UI 共用的启动入口
  - `src/client.rs`：发起对端连接
  - `src/rendezvous_mediator.rs`：与 `rustdesk-server`（hbbs）通信，等待直连（TCP 打洞）或中继连接
  - `src/server/`：audio_service / clipboard_service / input_service / video_service / display_service / connection 等细粒度服务
  - `src/flutter.rs` / `flutter_ffi.rs`：Rust 核心与 Flutter UI 的 FFI 桥
- **`flutter/`**：桌面与移动端 UI（Dart）

**连接模型**：`rendezvous_mediator` 先连 hbbs 做信令/打洞，优先 P2P 直连，失败则回落到 hbbr 中继；加密在传输层完成（端到端）。这种"P2P 优先 + 中继兜底"的双通道是远程桌面可用性的关键。

## 四、应用场景与启发

**典型场景**：远程办公、IT 运维支持、工业设备远程维护、跨地域访问自有设备。

**架构启发（可复用）**：
- **高特权系统能力应拆成独立可审计服务**：屏幕捕获、输入注入、剪贴板都是高敏感操作，RustDesk 把它们拆成独立 service 并各自持有独立连接，便于权限边界与故障隔离——任何"需要操控本机"的 Agent/工具都可借鉴。
- **Rust 跨平台核心 + Flutter UI 分离**：核心逻辑一次编写多端复用，UI 交给声明式框架，避免 Electron 重包袱。
- **自建中继 + 公共中继可切换**：把"网络可达性"做成一个可替换的运维决策点，而非硬编码。

## 五、源码深度解读

### 1. 启动链：`src/core_main.rs`

```rust
/// shared by flutter and sciter main function
#[cfg(not(any(target_os = "android", target_os = "ios")))]
pub fn core_main() -> Option<Vec<String>> {
    if !crate::common::global_init() {
        return None;                       // 初始化失败 → 终止，不启动 GUI
    }
    crate::load_custom_client();
    #[cfg(windows)]
    if !crate::platform::windows::bootstrap() {
        return None;                       // Windows bootstrap 失败 → 终止
    }
    let mut args = Vec::new();
    // ... flutter_args / is_elevate / is_run_as_system 解析
}
```

`core_main()` 是 Flutter/Sciter 两套 UI 的共用入口，返回 `Option` 表达"是否继续启动 GUI"——这是 RustDesk 跨 UI 后端复用的关键抽象：平台相关代码全部用 `#[cfg(...)]` 条件编译隔离，核心流程统一。

### 2. 信令与连接：`src/rendezvous_mediator.rs`

该文件负责与 `rustdesk-server` 通信，完成 NAT 打洞或中继协商。其职责是"等待远端直连（TCP hole punching）或中继连接"——把网络可达性问题收敛到单一模块，上层 `client.rs` / `server/` 服务只面对已建立的连接。

### 3. 能力底座：`libs/hbb_common`

集中了视频编解码、protobuf 消息、TCP/UDP 封装、文件传输 fs 工具。几乎所有上层模块都依赖它，是整个项目的"标准库"——理解 RustDesk 体感应从 `hbb_common` 的编码/传输原语入手。

## 六、全网口碑

- **规模与分发**：120k+ 星标，F-Droid / Flathub 官方分发，Discord / Reddit / YouTube 社区活跃，官方提供二进制 nightly 与稳定 release。
- **⚠️ 信任层争议（务必知悉）**：
  1. **公共中继服务器被发现走中国节点**（Lemmy 等社区指出的核心争议之一）。
  2. **被指静默把 Wayland 用户切回 X11**（高特权被用于"为可用性强改显示后端"）。
  3. **诈骗滥用**：大量"技术支持骗局"诱导受害者安装 RustDesk 让骗子远程控制手机/电脑盗取资金（印度 UPI 诈骗案、中文"刷单"骗局均有报道）；官方**因诈骗滥用曾主动下架 Android 版**。
  4. **团队身份不透明**：注册地新加坡但多处线索指向中国，社区反映"删除质疑团队身份的 issue/discussion"。
- **客观评价**：技术价值高、自托管可控，但"信任层"有历史包袱。生产使用建议**自建 hbbs/hbbr 并禁用公共中继**，且警惕其被用作社工诈骗载体。

## 七、竞品对比与核心研判

| 维度 | RustDesk | TeamViewer | AnyDesk | RDP | moonlight/sunshine |
|---|---|---|---|---|---|
| 开源 | ✅ AGPL-3.0 | ❌ 闭源商业 | ❌ 闭源商业 | ⚠️ 微软生态 | ✅ 开源（串流） |
| 自托管中继 | ✅ | ❌ | ❌ | ✅（需网关） | ✅ |
| 全平台 | ✅ | ✅ | ✅ | ⚠️ Win 主导 | ⚠️ 游戏串流 |
| 端到端加密 | ✅ | ✅ | ✅ | ⚠️ 需 VPN | ✅ |

**核心研判**：
- **优势**：开源 + 自托管 + 全平台 + 全链路自研，是隐私/可控诉求下 TeamViewer 的最佳开源替代；Rust 跨平台核心的工程质量在同类中领先。
- **风险**：公共中继与团队透明度争议使"默认配置"的信任成本偏高；高特权 + 登录态能力天然易被诈骗利用。
- **启发**：远程控制赛道的"开源可控"需求真实存在，但**中继网络的地理/治理透明度**会成为用户决策的关键——自建是必选项而非可选项。

## 关键文件速查

| 路径 | 作用 |
|---|---|
| `src/core_main.rs` | Flutter/Sciter 共用启动入口 |
| `src/rendezvous_mediator.rs` | 与 hbbs 信令/打洞/中继协商 |
| `src/client.rs` | 发起对端连接 |
| `src/server/` | audio/clipboard/input/video/display 等服务 |
| `libs/hbb_common` | 编解码 + protobuf + 传输 + 文件传输底座 |
| `libs/scrap` `libs/enigo` `libs/clipboard` | 屏幕捕获 / 键鼠 / 剪贴板 |
| `flutter/` | 跨端 UI |
