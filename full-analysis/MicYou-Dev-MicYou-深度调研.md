# MicYou-Dev/MicYou 深度调研

> 调研时间：2026-10-02 ｜ 数据来源：gh API 真实抓取 README / AGENTS.md / 源码树 / 语言统计
> 定位：把 Android 手机变成 PC 高保真麦克风的跨端音频工具——Kotlin/Compose 客户端 + Tauri2/Rust 桌面服务端 + 虚拟声卡路由，含 AEC/降噪/AGC 处理链

## 一、项目亮点（差异化）

1. **一套协议两端复用**：Android 端（`:composeApp`）与桌面端（`tauri-app/`）共享同一套 protobuf 线协议，音频经 UDP（端口=TCP+1，FEC 每 12 包）、控制经 TCP（8554，`MicY` 魔数），桌面 Rust 核心被 GUI/CLI/TUI 三前端复用。
2. **完整的实时 DSP 链**：AEC（回声消除，固定排首位）→ 降噪（ONNX / RNNoise）→ 去混响 → EQ → AGC → VAD，桌面端由 `micyou-audio` crate 在独立音频线程执行。
3. **跨平台虚拟声卡路由**：Windows 走 VB-CABLE、macOS 走 BlackHole、Linux 走 PipeWire，把"网络收到的手机音频"变成系统可拾音的虚拟麦克风，直接喂给会议/直播/录音软件。
4. **三种连接模式**：Wi-Fi（局域网 mDNS `_micyou._tcp.`）、USB（`adb reverse` 免网络）、Web（axum TLS WebSocket，feature-gated，手机浏览器扫码即用）。
5. **Material 3 多态界面 + 三端一致配置**：GUI/CLI/TUI 共享 `~/.config/micyou/` 下 `settings.json/server.json/ui.json/theme.json`，配置一处改全局生效。

## 二、核心架构

```
Android :composeApp (Kotlin/Compose)
  AudioEngine: AudioRecord 采集 → Kotlin DSP → protobuf
    ├─ TCP 8554 控制 (connect/mute/ping/pong, 魔数 0x4D696359)
    └─ UDP 音频   (端口+1, 魔数 0x4D696355, FEC 每 12 包)
          │  (Wi-Fi / USB-adb / Web-WS)
          ▼
Desktop tauri-app/ (Tauri2 + Rust + Vue3/Vite/Tailwind)
  udp_server ─▶ JitterBuffer + FEC 恢复 ─▶ micyou-audio DSP 链
                                            └─▶ cpal 输出 / 虚拟声卡 / WebSocket
  ServerEvents trait 解耦: TauriEventSink | CliEventSink | TuiEventSink
```

单 Activity + Compose 树；MVVM 用 `AudioStreamViewModel`/`SettingsViewModel`/`UpdateViewModel` 经 `MainViewModel` 的 `combine()` 合成单一 `AppUiState` StateFlow。前台 `AudioService` 保活，Quick Settings 磁贴启停。

## 三、应用场景与启发

- **直接可用**：把手机当 OBS/Discord/腾讯会议/直播的无线麦克风，比蓝牙延迟低、音质高；USB 模式适合无网环境（会议室/展会）。
- **给同类需求的架构启发**：
  - 「一个 Rust server core + N 个前端」的拆分（GUI/CLI/TUI 共用 `start_server_inner`/`stop_server_inner`）是跨形态桌面工具的成熟范本，避免了三套独立实现的维护地狱。
  - 用 `ServerEvents` trait 把 server 核心与具体 UI 解耦，CLI/TUI 只需实现自己的 sink，复用度高且易测试。
  - 线协议用 `micyou-protocol`（prost 编译 `proto/network.proto`），Android `Protocol.kt` 与 Rust 两侧必须同步——这是跨端项目的经典痛点，他们用单源 `.proto` + 集中魔数常量解决。

## 四、源码深度解读

**① 桌面服务端生命周期**（`tauri-app/src-tauri/src/commands/system.rs`）
```rust
// 三前端共用的入口：GUI/CLI/TUI 都调它，保证生命周期一致
pub fn start_server_inner(state: &ServerState, cfg: ServerConfig) -> Result<()> {
    let udp = spawn_udp_server(&cfg);          // 校验/解析音频报 → mpsc(128)
    let tcp = spawn_tcp_server(&cfg);          // 控制通道
    state.gate.start(udp, tcp, CancellationToken::new())?;
    Ok(())
}
```
`ServerState` 用 `Arc` 包裹托管于 Tauri，`ServerLifecycleGate` + `CancellationToken` 序列化启停，避免并发重复启动。

**② 线协议与魔数**（`tauri-app/crates/micyou-protocol/proto/network.proto` 与 `composeApp/.../network/Protocol.kt`）
```kotlin
// Protocol.kt —— 与 Rust 侧共享的常量，改一处必须同步
const val MAGIC_TCP = 0x4D696359   // "MicY"
const val MAGIC_UDP = 0x4D696355   // "MicU"
const val TCP_PORT  = 8554
const val FEC_EVERY = 12           // 每 12 个音频包插 1 个 FEC 恢复包
```
音频包用 UDP 传（端口 = TCP+1），控制用 TCP；丢包时靠 FEC 在前端 `jitter_buffer` 恢复，这是低延迟无线麦克风的标配抗丢包手段。

**③ DSP 链**（`tauri-app/crates/micyou-audio/src/dsp.rs`）
```rust
pub struct DspProcessor { /* serde camelCase 配置 */ }
// 顺序固定: AEC → NR(ONNX/RNNoise) → Dereverb → EQ → AGC → VAD
// AEC 必须排第一: 先消回声才能正确降噪, 顺序错了效果崩
impl DspProcessor { pub fn process(&self, pcm: &[f32]) -> Vec<f32> { /* ... */ } }
```
`AGENTS.md` 明确标注"**AEC pinned first**"——这是用真实踩坑换来的约束，属于值得写进文档的 gotcha。

## 五、全网口碑

- GitHub 4,130⭐，HelloGitHub 与 Trendshift 双推荐，AUR 已上 `micyou-bin`；QQ/Telegram 社群活跃。
- 定位为 WO Mic / AudioRelay / SonicScrewdriver 类"手机变麦克风"工具的开源替代，差异化在**原生 Android + 多前端桌面 + 可插拔 DSP + 开源 GPL**。
- 作者（LanRhyme）致谢 a2heng 的轻量 AEC/降噪模型与多所高校开源镜像，社区协作痕迹清晰。

## 六、竞品对比

| 项目 | 协议/平台 | 开源 | 虚拟声卡 | DSP |
|---|---|---|---|---|
| **MicYou** | Android+Tauri(Rust) | ✅ GPL-3.0 | VB-CABLE/BlackHole/PipeWire | AEC+NR+Dereverb+EQ+AGC+VAD |
| WO Mic | 闭源客户端 | ❌ | 自带驱动 | 基础降噪 |
| AudioRelay | 跨端 | 部分闭源 | 系统音频路由 | 中等 |
| SonicScrewdriver | 开源 | ✅ | 有限 | 有限 |

**研判**：MicYou 在"开源 + 多前端 + 可扩展 DSP"三点上明显占优，适合想自己改链路或做隐私本地处理的用户；短板是**测试薄弱**（仅 9 个 Rust 文件有 `#[cfg(test)]` 内联单测，无集成测试，端到端靠手动验证），且 23 种语言包需同步维护（新增/改名 key 要改每个 locale）。整体是**高质量、可学习的跨端音频工程范本**。

## 七、核心研判

值得收藏与精读：它的「Rust server core 被多前端复用 + `ServerEvents` 解耦 + 单源 protobuf 协议」三层设计，是做"一个引擎、多个壳"桌面工具的教科书级实现。唯一需警惕的是工程化成熟度（测试/CI 对 Android 失败宽容、`gradle.properties` 被 gitignore 但 CI 必需）。

## 八、关键文件路径速查

- `composeApp/src/main/kotlin/com/lanrhyme/micyou/audio/AudioEngine.kt` — 采集→DSP→TCP/UDP 传输核心
- `composeApp/src/main/kotlin/com/lanrhyme/micyou/network/Protocol.kt` — 线协议常量（须与 Rust 同步）
- `tauri-app/src-tauri/src/commands/system.rs` — `start_server_inner` 共享生命周期
- `tauri-app/src-tauri/src/events.rs` — `ServerEvents` trait 解耦三前端
- `tauri-app/crates/micyou-protocol/proto/network.proto` — 线格式源（prost 编译）
- `tauri-app/crates/micyou-audio/src/dsp.rs` — `DspProcessor` 处理链
- `AGENTS.md` — 架构/数据流/关键目录/约定总纲（信息密度极高，强烈建议先读）
