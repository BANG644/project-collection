# Meshrabiya（Android 虚拟网状网络）深度调研

> 数据来源：GitHub API 抓取（stars / README / 目录树 / 源码），抓取日期 2026-10-03。许可：开源（含 LICENSE 文件，SPDX 未自动识别；README 未声明具体类型）。语言：Kotlin（Android 库）。

## 一、项目定位（一句话）
Android 上的**虚拟网状网络库**：在多个 WiFi Direct / Local Only Hotspot 之间跨多跳转发，给应用提供「虚拟 IP + SocketFactory」，让节点像直连一样用 TCP/UDP 通信——无需 root、无 Google Play Services 依赖。

## 二、项目亮点（差异化）
1. **虚拟 IP + 多跳路由**：每个节点拿到 APIPA 地址（`169.254.x.y`），通过 SocketFactory 跨多跳收发，如同直连。
2. **BATMAN OGM 式发现**：周期性广播起源消息（originator message）建立路由表，受 BATMAN-adv 启发。
3. **零厂商依赖**：不依赖 Google Play Services / Nearby Connections，可在 AOSP 设备上跑。
4. **上层库友好**：SocketFactory 可直接喂给 OkHttp 等，虚拟/非虚拟地址通吃。
5. **双热点模式 + BLE 备选**：WiFi Direct Group 或 Local Only Hotspot，连接发现还可走 BLE 广播。

## 三、核心架构
- `lib-meshrabiya` 模块（核心库）。
- `vnet/VirtualNode.kt`（抽象节点，实现 `VirtualRouter`）。
- `vnet/VirtualRouter.kt`（路由接口：`route` / `lookupNextHopForChainSocket`）。
- `vnet/socket/ChainSocketFactory` + `ChainSocketServer`（socket chain 下一跳转发，类似 HTTP 代理的 host 头）。
- `vnet/OriginatingMessageManager`（起源消息广播/老化）。
- `vnet/MeshrabiyaConnectLink`（通过二维码/URI 传递热点 SSID、passphrase、IPv6 link-local、服务端口）。
- 子包：`wifi/`、`bluetooth/`、`quic/`、`datagram/`、`socket/`、`mmcp/`（mesh management control protocol）、`portforward/`。
- 附带 `test-app` + `test-shared` 用于真机验证。

## 四、应用场景与启发
- 离线/弱网多设备互联：无 WiFi AP 的学校、诊所、徒步、救灾场景，实测 WiFi 直连可达 300Mbps+。
- 把「mesh 路由」做成**可插拔的 Socket 层**而非内核模块，对应用开发者极其友好。
- 对标 BATMAN-adv 但运行在用户态、无需 root，是「应用层自组网」的好范本。

## 五、源码深度解读
**`vnet/VirtualNode.kt`（节点抽象）**：节点地址在 APIPA 段随机生成，持有数据报 socket、chain socket 工厂与起源消息管理器，状态用 `StateFlow` 暴露：
```kotlin
fun randomApipaAddr(): Int {                 // 169.254.x.y
    val fixed = (169 shl 24).or(254 shl 16)
    return fixed.or(Random.nextInt(Short.MAX_VALUE.toInt()))
}
abstract class VirtualNode(
    override val address: InetAddress = randomApipaInetAddr(),
    override val networkPrefixLength: Int = 16,
    val config: NodeConfig = NodeConfig.DEFAULT_CONFIG,
) : VirtualRouter, Closeable {
    protected val chainSocketFactory: ChainSocketFactory =
        ChainSocketFactoryImpl(virtualRouter = this, logger = logger)
    val socketFactory: SocketFactory   // 供 OkHttp 等上层库直接使用
}
```

**`vnet/VirtualRouter.kt`（路由接口）**：路由与「chain socket 下一跳查询」是库的核心契约：
```kotlin
interface VirtualRouter {
    val address: InetAddress
    fun route(packet: VirtualPacket,
              datagramPacket: DatagramPacket? = null,
              virtualNodeDatagramSocket: VirtualNodeDatagramSocket? = null)
    fun lookupNextHopForChainSocket(address: InetAddress, port: Int): ChainSocketNextHop
}
```
> 机制：发送时把目标虚拟地址写进 socket 流（类似代理 host 头），每跳查询 `lookupNextHopForChainSocket` 转发，直到抵达直连目标节点；对非虚拟地址回退系统默认 socket。

## 六、全网口碑
约 **198 ⭐**，小众但专业——出自 UstadMobile（做离线教育方案），工程完整（Gradle 多模块、androidTest）。非热门但针对性强。

## 七、竞品对比
| 维度 | Meshrabiya | BATMAN-adv | Wi-Fi Aware / NAN | Google Nearby | Briar |
|------|-----------|-----------|-------------------|---------------|-------|
| 运行层 | 应用层（无 root） | 内核态 | 系统 | Play Services | 应用层 |
| 多跳 | ✅ | ✅ | 有限 | ❌ | ✅（BT/网格） |
| 厂商依赖 | ❌ 无 | ❌ | 系统 | ✅ Google | ❌ |
| 上库友好 | ✅ SocketFactory | ❌ | 中 | 中 | 消息级 |

差异化：用户态、零 Play Services、Socket 层可插拔。**风险**：API 仍可能变动、仅 Android、文档偏 README 级。

## 八、核心研判
在「离线自组网」细分里是质量较高、依赖最干净的实现，适合需要 Android 多设备直连的科研/教育/救灾场景；作为库学习「应用层 mesh + Socket 虚拟化」也很合适。生产前需关注其版本稳定性与 WiFi 并发热点（STA/AP concurrency）的机型差异。

## 关键文件路径速查
- `lib-meshrabiya/src/main/java/com/ustadmobile/meshrabiya/vnet/VirtualNode.kt` — 节点抽象（APIPA 地址 / SocketFactory / 起源消息）
- `lib-meshrabiya/src/main/java/com/ustadmobile/meshrabiya/vnet/VirtualRouter.kt` — 路由接口
- `lib-meshrabiya/src/main/java/com/ustadmobile/meshrabiya/vnet/MeshrabiyaConnectLink.kt` — 热点连接链接序列化
- `lib-meshrabiya/src/main/java/com/ustadmobile/meshrabiya/vnet/socket/ChainSocketServer.kt` — 多跳 socket chain 转发
- `lib-meshrabiya/src/main/java/com/ustadmobile/meshrabiya/vnet/wifi/` — WiFi Direct / Local Only Hotspot 管理
- `lib-meshrabiya/src/main/java/com/ustadmobile/meshrabiya/vnet/bluetooth/` — BLE 备选发现
- `lib-meshrabiya/src/main/java/com/ustadmobile/meshrabiya/mmcp/` — 网状管理控制协议
