# Goose（WHOOP 5.0 本地数据伴侣）深度调研

> 数据来源：GitHub API 抓取（stars / README / 目录树 / 源码），抓取日期 2026-10-03。许可：未声明（README 未标注许可证，仓库无标准 LICENSE 识别）。语言：Swift（SwiftUI）+ Rust（iOS 静态库）。状态：**Alpha proof of concept**（作者明示非成品）。

## 一、项目定位（一句话）
local-first 的 **WHOOP 5.0 数据与健康指标项目**：iOS 应用经 BLE 连接 WHOOP 手环，把原始数据包经 Rust core 解析存储，呈现睡眠/恢复/Strain/压力/心率等视图；与 WHOOP 无隶属关系，不含 WHOOP 源码。

## 二、项目亮点（差异化）
1. **本地优先 + 隐私默认**：健康数据本地存储，未来后端/AI 需独立授权流程。
2. **SwiftUI + Rust core 跨语言架构**：Rust 编译为 iOS 静态库 `.a`，经 C 桥接。
3. **BLE 直连解析**：CoreBluetooth 扫描/连接/同步 WHOOP 5.0，原始包走 Rust core。
4. **完整健康视图**：Home / Health（睡眠·恢复·Strain·压力·Cardio·能量）/ Coach / More。
5. **HealthKit 集成**：睡眠导入 + 训练写入。
6. **Live Activity 扩展**：实时运动 widget（`GooseWorkoutLiveActivityExtension`）。

## 三、核心架构
- `GooseSwift/`：SwiftUI 应用——`AppShellView`（标签壳）、`GooseAppModel`（状态/BLE 所有权/生命周期）、`GooseBLEClient`（蓝牙）、`GooseRustBridge`（Swift 侧 C 桥接）、`CoachView`/`Health*`。
- `Rust/core/`：Rust 核心——`metrics`、`activity_sessions`、`recovery_rollup`、`capture_import`、`store`、`bridge.rs` 等，编译为 `libgoose_core.a`。
- `Rust/core/include/goose_core_bridge.h`：C 桥接头。
- `Scripts/build_ios_rust.sh`：Xcode 构建阶段按平台编译 Rust。
- `GooseWorkoutLiveActivityExtension/`：实时运动 widget。

## 四、应用场景与启发
- 展示「SwiftUI 应用 + Rust 核心 + FFI」在 iOS 上落地的完整范式，适合需要跨平台复用算法核心的项目。
- **local-first 健康数据自托管**：拆解厂商锁定（WHOOP 数据本地解析），对可穿戴数据主权有参考价值。
- 对做蓝牙设备逆向解析 / 健康仪表盘的开发者是真实案例。

## 五、源码深度解读
**`GooseSwift/GooseRustBridge.swift`（Swift 侧 C 桥接）**：用 JSON-over-C 协议把方法调用送往 Rust，并记录各阶段耗时（微服务级可观测）：
```swift
func requestValue(method: String, args: [String: Any] = [:]) throws -> Any {
    let payload: [String: Any] = [
        "schema": "goose.bridge.request.v1",
        "request_id": "goose-swift-\(...)",
        "method": method, "args": args ]
    let data = try JSONSerialization.data(withJSONObject: payload)
    var responsePointer: UnsafeMutablePointer<CChar>?
    request.withCString { pointer in
        responsePointer = goose_bridge_handle_json(pointer)   // Rust FFI
    }
    defer { goose_bridge_free_string(responsePointer) }
    let resp = try JSONSerialization.jsonObject(with: Data(responseText.utf8))
    guard let ok = resp["ok"] as? Bool, ok else { throw ... }
    return resp["result"] ?? [:]
}
```
> 模式：Swift 把 `{schema, method, args}` 序列化为 JSON 字符串 → `goose_bridge_handle_json(cstr)` → Rust 返回 `{ok, result, timing}` JSON → Swift 反序列化；`lastTiming` 记录编码/FFI 往返/解码耗时。

**`Rust/core/src/lib.rs`**：crate 根（精简），对外暴露 bridge；真正的派发在 `bridge.rs`（FFI 方法路由到 `metrics`/`sessions`/`recovery_rollup` 等模块，约 310KB）。**`GooseBLEClient.swift`**：CoreBlueooth 扫描/连接/同步 WHOOP 5.0，字节流交给 Rust core 解析。

## 六、全网口碑
**2719 ⭐**，Alpha POC（作者明示未成品，预告 2026-06 公开 beta）；社区 X 群协作；UI 设计参考 Bevel。热度高于多数同类个人项目。

## 七、竞品对比
| 维度 | Goose | 官方 WHOOP App | Bevel（UI 参考） | 其他 WHOOP 第三方 |
|------|-------|---------------|-----------------|-------------------|
| 数据位置 | 本地优先 | 厂商云 | 本地+云 | 各异 |
| 跨设备/自托管 | ✅ | ❌ | 中 | 各异 |
| 厂商依赖 | ❌ 逆向 BLE | ✅ | 读 WHOOP | 读 WHOOP |
| 平台 | iOS（Swift+Rust） | iOS/Android | iOS | iOS |

差异化：本地优先、自托管解析、不依赖厂商云。**风险**：Alpha、仅 WHOOP 5.0、依赖逆向 BLE 协议（无 WHOOP 源码）、性能未优化、需 iOS 26 SDK。

## 八、核心研判
作为「拆解厂商锁定的本地健康数据伴侣」范式价值高，Swift+Rust FFI 架构清晰、可观测性到位；但处 Alpha、单设备、依赖逆向，生产可用前路仍长。更适合作为**学习 iOS 跨语言架构与可穿戴数据自托管**的参考，而非直接上手的成品。

## 关键文件路径速查
- `GooseSwift/GooseRustBridge.swift` — Swift 侧 JSON-over-C FFI 桥接
- `GooseSwift/GooseBLEClient.swift` — CoreBluetooth 扫描/连接/同步
- `GooseSwift/GooseAppModel.swift` — 应用状态与生命周期
- `Rust/core/src/lib.rs` — Rust crate 根（暴露 bridge）
- `Rust/core/include/goose_core_bridge.h` — C 桥接头（Swift 链接）
- `Rust/core/src/bridge.rs` — Rust 侧 FFI 方法派发（metrics/sessions/recovery…）
- `Scripts/build_ios_rust.sh` — Xcode 构建阶段编译 Rust 核心
- `GooseWorkoutLiveActivityExtension/` — 实时运动 Live Activity widget
