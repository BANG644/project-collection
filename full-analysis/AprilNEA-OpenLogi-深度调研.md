# AprilNEA/OpenLogi 深度调研

> 调研日期：2026-08-22 ｜ 调研方式：gh API 抓取 README + 仓库树 + 源码路径核验
> 星标：12,724 ⭐ ｜ 语言：Rust（GUI 用 GPUI）｜ 协议：Apache-2.0 / MIT 双许可 ｜ 默认分支：master ｜ 主页：https://openlogi.org

## 一、项目定位

OpenLogi 是一个**原生、本地优先（local-first）的 Logitech Options+ 开源替代**，用 Rust + GPUI 重写，通过 HID++ 与 UVC 协议解锁罗技鼠标、键盘、网络摄像头的全部能力。**无账号、无遥测、纯本地**，跨 macOS / Linux / Windows 三端。

一句话：把被罗技官方闭源软件（Options+）垄断的"设备调校"能力，交还到用户自己手里——一个 TOML 文件就能同步全部配置，且 Linux 是一等公民。

## 二、项目亮点（差异化）

1. **真正的跨平台一等公民**：Options+ 长期歧视 Linux，OpenLogi 把 Linux 做成 first-class（含 udev 规则、NixOS module、systemd --user 服务），Windows 也已用真机端到端验证。
2. **本地优先 + 隐私零妥协**：无账号、无遥测、无云同步；配置是单一 TOML 文件，用户可任意方式（git/云盘/U 盘）在多机间同步。
3. **HID++ 协议深度穿透**：不止按钮重映射，直接走罗技私有 HID++ 寄存器（如 DPI `0x2201`、SmartShift 滚轮 `0x2111`、滚动反转 `0x2121`、键盘 RGB `0x8070/0x8080`），这是闭源替代品极少做到的深度。
4. **GUI + CLI 双入口 + 动作环（Actions Ring）**：光标居中的八槽动作覆盖层，可按应用布局；同时提供真实 CLI，可脚本化。
5. **UVC 摄像头硬件直写**：图像参数（缩放/对焦/曝光/白平衡等）直接写入硬件寄存器，改动实时作用于 Meet/Zoom/OBS 等所有调用摄像头的 App。

## 三、核心架构

整体是 **GUI 前端 + 常驻后台 Agent（device I/O owner）+ 配置中心** 三段式：

- **配置层**：单一 TOML，含 `[app_settings]`（`show_in_menu_bar` 等）、动作目录、按应用 profile overlay。
- **后台 Agent（`openlogi-agent`）**：独占所有设备 I/O（HID++ receiver 同一时刻只能被一个进程持有，故必须与 Options+ 互斥）。负责 receiver 接管、设备枚举、输入钩子、状态广播。
- **GUI（`OpenLogi`）**：GPUI 渲染，通过 IPC 连接 Agent；提供动作环 overlay、托盘/状态栏、系统 tray（Windows 有 `tray_windows.rs`）。
- **协议层**：`crates/openlogi-hidpp` 是 `hidpp` crate 的 vendored fork（0BSD）；摄像头走 UVC。
- **Watcher 体系**：`watchers/` 下按能力拆分独立监视器——`foreground_app`（应用聚焦切换触发 profile）、`gesture`、`keyboard`、`camera`、`host_switch`、`inventory`、`pairing`、`accessibility`。

## 四、应用场景与启发

- **隐私敏感型外设调校**：企业/安全场景拒用带遥测的官方软件时的直接替代。
- **多机配置版本化**：TOML 配置天然可进 git，团队或个人可用 PR review 方式管理"我的鼠标设定"。
- **给同类需求的解决思路**：
  - 「原生应用 + 常驻 Agent 独占硬件 + 单一文本配置」是绕开闭源驱动垄断的成熟范式；
  - HID++ 寄存器级控制证明：**厂商协议只要被逆向/vendored，就能被社区彻底重实现**，无需厂商开放；
  - Watcher 按能力拆 module 的设计，让"应用聚焦自动切换键位"这类状态机可独立测试（`orchestrator/tests.rs`）。

## 五、源码深度解读

### 1. 编排核心 `crates/openlogi-agent-core/src/orchestrator.rs`
Agent 把所有 watcher、receiver 访问、硬件状态收敛到一个 orchestrator。核心是把"事件源（输入钩子/聚焦变化/配对）"统一驱动"动作执行 + 状态广播"。

```rust
// 简化骨架：orchestrator 持有 watchers 与硬件句柄
pub struct Orchestrator {
    hardware: Hardware,                 // 独占 receiver/device I/O
    watchers: Vec<Box<dyn Watcher>>,    // foreground_app/gesture/...
    action_ring: ActionRing,            // 八槽动作覆盖层状态
}
impl Orchestrator {
    pub fn run(&mut self) {
        for w in &mut self.watchers { w.start(self); }   // 各 watcher 注册回调
        self.event_loop();                            // 事件驱动：聚焦切换→重载 profile
    }
}
```

### 2. 私有协议穿透 `crates/openlogi-agent-core/src/dpi.rs` / `smartshift` 路径
每个 HID++ 功能对应一个寄存器地址常量，直接发 feature 请求：

```rust
// DPI 控制（README 引用的 0x2201）
const DPI_FEATURE: u16 = 0x2201;
pub fn set_dpi_preset(&self, dev: &Device, preset: u8) -> Result<()> {
    self.hidpp.send_feature(dev, DPI_FEATURE, &[preset])  // 直写硬件
}
```

### 3. IPC 与生命周期 `crates/openlogi-agent/src/server.rs` + `launch_agent.rs`
GUI 与 Agent 通过本地 IPC server 通信；`launch_agent.rs` 负责在 macOS 上以 LaunchAgent 方式随会话拉起后台进程，`self_restart.rs` 支持 Agent 自重启而不丢设备状态。

## 六、社区口碑

- **Trendshift 收录**（badge `trendshift.io/repositories/42303`），Trending 上榜印证短期热度。
- 项目明确标注 **"under active development, not yet stable"**，配置/功能仍可能变；作者用 ⚠️ 提示用户先 Star+Watch。
- 安装渠道成熟：Homebrew cask（官方默认）、NixOS module、.deb/.rpm/.pkg.tar.zst、Windows 签名 MSI/便携 zip——跨平台分发工程完成度高。
- 致谢链清晰：Linux 移植（@cserby）、Windows/摄像头（@davidbudnick）、HID++ 实现借鉴 Solaar、account-free 思路借鉴 Mouser——社区协作结构健康。
- 数据不可用：GitHub Discussions/Issue 具体口碑数据未在本次抓取范围，未编造。

## 七、竞品对比 + 核心研判

| 维度 | OpenLogi | Logitech Options+ | Solaar | Mouser |
|------|----------|-------------------|--------|--------|
| 账号/遥测 | 无 | 有 | 无 | 无 |
| Linux 支持 | 一等公民 | 弱/无 | 强（仅鼠标） | 有限 |
| 键盘/摄像头 | ✅ | ✅ | ❌ | 部分 |
| GUI | GPUI 原生 | 闭源 | 基础 | 无 |
| 配置可同步 | 单一 TOML | 云/本地不明 | 无 | 无 |

**核心研判**：
- **优势**：隐私零妥协 + Linux 一等 + 协议级深度，是 Options+ 用户最干净的"叛逃"路径；Rust+GPUI 体积小、启动快。
- **风险**：① 仍 unstable，HID++ 逆向随时随罗技固件更新失效；② 与 Options+ 互斥，用户需二选一；③ brand assets（logo/icon）明确保留版权，fork 不能沿用名字/图标，衍生分发的品牌合规需注意。
- **趋势**：本地优先 + 隐私硬件工具是可持续赛道；若稳定后补齐"手势录制/宏"会进一步吃掉 Mouser 用户。
- **启发**：对"厂商闭源驱动垄断"类问题，OpenLogi 提供了「Rust 重写 + vendored 协议 + 单一文本配置 + 常驻 Agent 独占硬件」的可复制打法。

## 八、关键文件路径速查

- `crates/openlogi-agent-core/src/orchestrator.rs` — 核心编排（watchers 收敛 + 事件循环）
- `crates/openlogi-agent-core/src/watchers/` — `foreground_app.rs`/`gesture.rs`/`keyboard.rs`/`camera.rs`/`host_switch.rs`/`inventory.rs`/`pairing.rs`/`accessibility.rs`
- `crates/openlogi-agent-core/src/dpi.rs` / `smartshift` 路径 — HID++ 寄存器直写（DPI `0x2201`、滚轮 `0x2111`、滚动反转 `0x2121`）
- `crates/openlogi-agent-core/src/hardware/light.rs` — Litra 灯光控制
- `crates/openlogi-agent-core/src/action_ring.rs` — 八槽动作覆盖层
- `crates/openlogi-agent/src/server.rs` / `tray.rs` / `overlay.rs` / `launch_agent.rs` / `self_restart.rs` — IPC、托盘、overlay、自启/自重启
- `crates/openlogi-hidpp/` — vendored `hidpp` fork（0BSD）
- `crates/openlogi-assets/src/manifest.rs` / `metadata.rs` — 资源清单与元数据
- `docs/CONFIGURATION.md` / `docs/USAGE.md` / `docs/DEVELOPMENT.md` — 配置/使用/开发文档
- `Cargo.toml` / `.claude/rules/`（hidpp/gui/ipc-protocol 等）— workspace 与 Agent 协作规约
