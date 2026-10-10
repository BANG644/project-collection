# Lakr233/vphone-cli 深度调研

> 调研日期：2026-10-11 | 星标：15,157⭐ | 语言：Swift | 许可：MIT | 默认分支：main | 最近提交：活跃（pushed 2026-10-10）| 趋势：GitHub Trending（当日新增）

## 一句话定位

vphone-cli 在 Apple Silicon Mac 上用 Apple 的 Virtualization.framework + PCC 研究虚拟机跑「虚拟 iPhone」——面向安全研究、逆向工程与调试，图形窗口可用、固件预修补、支持备份/克隆与本地 HTTP+WebSocket 自动化 API，运行时无需 Xcode/Python/Homebrew。

## 项目亮点

- **原生虚拟化**：基于 Apple 官方 `Virtualization.framework` 与 PCC（Private Cloud Compute）研究虚拟机，无需 QEMU 等模拟器。
- **为安全研究而生**：固件预修补（pre-patched），可装包环境；文档明确面向 security research / reverse engineering / debugging。
- **零运行时依赖**：运行时不需要 Xcode、Python 或 Homebrew；Launchpad + `VPhone.bundle` 自包含驱动。
- **自动化 API**：可选本地 HTTP + WebSocket 接口（`--api-listen 127.0.0.1:8765` + token），并有 `Skills/vphone-guest-control/SKILL.md` 供 coding agent 操控。
- **完整文档与研究笔记**：`Documents/Guides/`（主机设置/网络/快照/兼容性）+ `Research/`（二进制补丁对比、固件 manifest、txm fullchain 分析等逆向笔记）。

## 核心架构

- **Launchpad + VPhone.bundle 双层**：Launchpad（GUI）负责下载固件、修补、恢复系统、启动 VM；`vphone-cli` 在 `VPhone.bundle` 内作为实际命令行驱动。
- **VPhoneDaemon（Swift 守护进程）**：`Daemon/` 下以 `APIWire`（线协议）+ `GuestAPI`（Guest 端 API 面）为核心，外加 `Bootstrap/GuestIrisinInstaller*`（固件/包/RootHide/Rootless 引导）。
- **Guest API 面**：`GuestAPI+*.swift` 把 App 详情、输入、文件、进程、设备、定位、陀螺仪、日志等能力拆成独立扩展，经 `APIWire` 的 JSON-RPC 暴露给宿主。
- **VM 存储于 `~/.vphone/`**，支持 `vm list / launch / export`（导出为 `.tzst`）。

## 应用场景与启发

- 没有实体机也能做 iOS 安全研究 / 逆向 / 调试；对无法承担多台真机的个人研究者尤其有价值。
- **Agent 可控虚拟设备的范式**：`Skills/vphone-guest-control/SKILL.md` + 本地 HTTP/WS API，让 coding agent「开一台 iPhone、装环境、跑测试」成为可编排步骤——这与「给 agent 接真实/虚拟设备」的工具链方向一致。
- 对构建自有虚拟化/devtool 的启发：用官方框架 + 预修补固件 + 薄 CLI/守护进程分层，比从零造模拟器省力且快。

## 源码深度解读

**线协议（`VPhoneDaemon/Daemon/APIWire.swift`）——JSON-RPC over HTTP/WS**

```swift
enum APIWire {
    static func decode(_ data: Data) throws -> APIRequest {
        guard let object = try JSONSerialization.jsonObject(with: data) as? [String: Any],
              let method = object["method"] as? String, !method.isEmpty,
              method.count <= 128,   // 方法名长度硬上限，防滥用
              object["params"] == nil || object["params"] is [String: Any]
        else { throw GuestAPIError.invalidRequest("Expected {method, params?, id?}") }
        return APIRequest(method: method, params: object["params"] as? [String: Any] ?? [:], id: object["id"])
    }
    static func execute(_ request: APIRequest) -> APIReply {
        let result = try GuestAPI.execute(method: request.method, params: request.params)
        return .json(["type": "response", "id": request.id ?? NSNull(), "result": result])
    }
}
```

设计要点：① `decode` 对 method 长度做硬上限（≤128）+ 参数类型校验，是面向不可信输入的防御性解析；② `execute` 把分发统一到 `GuestAPI.execute(method, params)`，所有 Guest 能力经同一入口——新增能力只需在 `GuestAPI+*.swift` 加一个扩展，线协议零改动。

## 全网口碑

- 发布即登 GitHub Trending；社区聚焦「终于能免实体机做 iOS 研究」「MIT 真开源难能可贵」。
- **合规提示**：需 `csrutil enable --without debug` + `allow-research-guests`（SIP 仅放宽调试限制，仍启用），属研究用途；工具本身定位安全研究，非应用盗版。

## 竞品对比 + 核心研判

- **竞品**：Corellium（商业虚拟设备，收费且闭源）、实体 iOS 设备、QEMU（iOS 支持极差）。
- **差异化**：用原生 Virtualization.framework、MIT 开源、面向安全研究的预修补固件 + 研究笔记，且提供 agent 可控 API。
- **研判**：iOS 安全研究圈的强力工具，MIT 许可降低采用门槛。注意三点——① 仅 Apple Silicon + macOS 15+；② 需放宽 SIP 安全设置（权衡）；③ 研究用途，勿用于侵权。对「虚拟设备 + agent 自动化」方向是优质参考实现。

## 关键文件路径速查

- `VPhoneDaemon/Daemon/APIWire.swift` — JSON-RPC 线协议（decode/execute）
- `VPhoneDaemon/Daemon/GuestAPI.swift` + `GuestAPI+*.swift` — Guest API 面（App/Input/File/Process/Device…）
- `VPhoneDaemon/Daemon/Bootstrap/GuestIrisinInstaller*.swift` — 固件/包/RootHide/Rootless 引导
- `Research/` — 二进制补丁对比、固件 manifest、txm fullchain 分析（逆向笔记）
- `Skills/vphone-guest-control/SKILL.md` — Agent 控制技能
- `Documents/Guides/` — 主机设置 / 网络 / 快照 / 兼容性文档
