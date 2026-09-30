# nordicsemi/Android-nRF-Mesh-Library 深度调研

> 调研日期：2026-10-01 ｜ 数据源：gh API（README / 目录树 / mesh/src/main/java/no/nordicsemi/android/mesh/）｜ 定位：Android 平台蓝牙 Mesh（Bluetooth Mesh 1.0.1）配网与消息收发库（BSD-3-Clause，Nordic Semiconductor 官方）

## 一、项目定位（一句话）

**Android-nRF-Mesh-Library** 是 Nordic Semiconductor 官方维护的 Android 蓝牙 Mesh 库：提供对 **Bluetooth Mesh Profile 1.0.1 / Mesh Model 1.0.1 / Device Properties 2** 的完整支持，让 App 能完成**配网（Provisioning）**、管理网络密钥/应用密钥、向 Mesh 节点收发模型消息（如 Generic OnOff）。

## 二、项目亮点（差异化）

1. **协议级权威实现**：直接对照 Bluetooth SIG 的 Mesh 1.0.1 规范实现全网络层（network/transport/bearer），而非第三方封装；Nordic 是 BLE 芯片与协议的重要推动方，权威性高。
2. **配网全流程覆盖**：支持 OOB Public Key 及各类 OOB（Input/Output/Static），Identify → Provision 三步式，并能处理 Secure Network Beacon、IV Index 更新等网络层事件。
3. **密钥与模型管理完整**：Network Key / Application Key 的增删刷新、App Key 与 Model 的绑定/解绑、Publication/Subscription 设置、Group（含虚拟地址）、Proxy Filter 一应俱全。
4. **JSON 配置兼容**：网络配置 JSON Schema 兼容 Mesh Configuration Database Profile 1.0，便于与 Nordic 其他工具/桌面端互导。
5. **配套示例固件**：`ExampleFirmwares/` 内置 light server / light client 固件（nrf52832 DevKit），开箱即可真机联调。

## 三、核心架构

- **技术栈**：Android（Java/Kotlin）/ Gradle / 基于 Nordic 的 Android-BLE-Library 收发；Maven Central：`no.nordicsemi.android:mesh:3.5.0`；最低 Android 4.3。
- **包结构 `mesh/src/main/java/no/nordicsemi/android/mesh/`**：
  - **门面 API**：`MeshManagerApi.java`（核心入口）、`MeshMngrApi.java`、`MeshManagerCallbacks` / `MeshProvisioningStatusCallbacks` / `MeshStatusCallbacks`（回调三件套）。
  - **网络模型**：`MeshNetwork.java`、`BaseMeshNetwork.java`、`MeshNetworkDb.java`（持久化 DB）、`Provisioner.java`、`NetworkKey.java` / `ApplicationKey.java`、`Group.java`、`Scene.java`、`Range.java`（地址范围）、`IvIndex.java`、`MeshBeacon.java` / `SecureNetworkBeacon.java`。
  - **消息/传输**：`MeshMessageHandler.java`、`MeshProvisioningHandler.java`、`MeshTAITime.java`、`models/`（GenericOnOffSet 等模型消息）、`opcodes/`、`transport/`、`provisionerstates/`、`utils/`、`data/`、`logger/`、`sensorutils/`。
- **接入方式**：业务侧用 `Android-BLE-Library` 收发包，再调用 `mMeshManagerApi.handleNotifications(mtu, pdu)` / `handleWriteCallbacks(...)` 把字节喂给 Mesh 栈——栈本身只关心 Mesh PDU。

## 四、应用场景与启发

- **场景**：做 BLE Mesh 产品的 Android 配网 App（智能照明、传感器网络、楼宇自动化）；需要「手机即配网器/控制器」的 IoT 厂商；研究蓝牙 Mesh 协议栈实现的学习者。
- **启发**：
  - 它是「**把重型二进制协议栈封装成易用门面**」的典范：`MeshManagerApi` 一个类暴露配网/收发/密钥管理，内部按 network/transport/bearer 分层——这种「瘦门面 + 厚分层」结构，比直接暴露协议细节更适合 App 集成。
  - 跨进程/跨线程的 BLE 回调通过 `handleNotifications/handleWriteCallbacks` 统一注入 Mesh 栈，清晰地把「传输层（通用 BLE）」与「协议层（Mesh）」解耦，任何要做私有协议栈的项目都可借鉴。

## 五、源码深度解读（核心模块）

**1. `MeshManagerApi.java`：配网与收发的统一门面**

```java
// README 示例：初始化即用三套回调 + loadMeshNetwork()
MeshManagerApi mMeshManagerApi = new MeshManagerApi(context);
mMeshManagerApi.setMeshManagerCallbacks(this);
mMeshManagerApi.setProvisioningStatusCallbacks(this);
mMeshManagerApi.setMeshStatusCallbacks(this);
mMeshManagerApi.loadMeshNetwork();

// 配网三步：identify -> startProvisioning（含 Static/Output/Input OOB 变体）
mMeshManagerApi.identifyNode(deviceUUID);                       // 设备闪烁/震动/响铃 5s
mMeshManagerApi.startProvisioning(unprovisionedMeshNode);
// 或 mMeshManagerApi.startProvisioningWithStaticOOB(...) / WithOutputOOB(...) / WithInputOOB(...)
```

`MeshManagerApi` 把「配网状态 / Mesh 状态 / 管理器状态」三类回调分开，调用方按需实现；配网提供 4 种 OOB 重载，覆盖不同设备能力。

**2. 模型消息收发：`GenericOnOffSet` + `createMeshPdu`**

```java
final GenericOnOffSet genericOnOffSet = new GenericOnOffSet(
    appKey,                              // 用于签名的 App Key
    state,                               // 新状态（开/关）
    new Random().nextInt()               // TID，防重放
);
mMeshManagerAPi.createMeshPdu(address, genericOnOffSet);  // 生成 Mesh PDU 并下发
```

这是「应用密钥签名 + 模型消息 + TID」的标准 Mesh 模型交互范式；Config 类消息同样走 `createMeshPdu`，体现模型层与配置层的统一出口。

**3. 密钥与地址模型：`NetworkKey` / `ApplicationKey` / `Range`**

`NetworkKeysConfig` / `ApplicationKeysConfig` / `ProvisionersConfig` / `AllocatedUnicastRange` 等类把 Mesh 的「网络密钥、应用密钥、地址分配范围」建模为可序列化对象，`MeshNetworkDb` 负责持久化——整套网络拓扑以对象图形式存在，便于导出 JSON 与离线编辑。

## 六、社区口碑

- 477⭐、BSD-3-Clause、最近提交 2026-09-24（活跃）；Nordic 官方出品，质量与文档可信度高；Maven Central 直接依赖，配套 nRF Mesh App（F-Droid/Play）与示例固件。
- 局限：定位是「Mesh 配网/控制库」，不是端到端产品；需搭配 Nordic BLE 设备与固件才能完整体验。

## 七、竞品对比 + 核心研判

| 维度 | Android-nRF-Mesh-Library | Silicon Labs Bluetooth Mesh | 通用 BLE 库(如 RxAndroidBle) | 自研 Mesh 栈 |
|---|---|---|---|---|
| Mesh 1.0.1 协议完整度 | ✅ 官方 | ✅ 官方 | ❌ 仅 BLE | ⚠️ 看投入 |
| 配网/密钥/模型管理 | ✅ | ✅ | ❌ | ⚠️ |
| 权威性/文档 | ✅ Nordic | ✅ Silabs | ⚠️ 社区 | ❌ |
| 跨厂商中立 | ⚠️ Nordic 生态 | ⚠️ Silabs 生态 | ✅ | ✅ |
| 许可 | BSD-3 | 厂商协议 | 多 | 自定 |

**研判**：要做 Android 端蓝牙 Mesh 配网/控制，它是除芯片原厂 SDK 外最权威、最省心的开源选择，BSD-3 商用友好、协议层完整。风险：①偏向 Nordic 生态（虽协议中立，但示例/最佳实践围绕 nRF）；②定位为库非产品，UI/业务仍需自己搭；③Mesh 规范演进（如后续 Mesh 1.1 特性）跟进节奏取决于 Nordic。与用户的「Mesh/离线网络（meshtastic 兴趣）」背景契合，可作为 BLE Mesh 协议栈实现的高质量参考。

## 八、关键文件路径速查

- 仓库根：`https://github.com/nordicsemi/Android-nRF-Mesh-Library`
- 核心门面：`mesh/src/main/java/no/nordicsemi/android/mesh/MeshManagerApi.java`、`MeshMngrApi.java`、`MeshManagerCallbacks.java`、`MeshProvisioningStatusCallbacks.java`、`MeshStatusCallbacks.java`
- 网络模型：`MeshNetwork.java`、`MeshNetworkDb.java`、`Provisioner.java`、`NetworkKey.java`、`ApplicationKey.java`、`Group.java`、`Range.java`、`IvIndex.java`
- 消息/传输：`MeshMessageHandler.java`、`MeshProvisioningHandler.java`、`models/`（GenericOnOffSet 等）、`opcodes/`、`transport/`、`provisionerstates/`
- 示例与构建：`ExampleFirmwares/`、`app/`（示例 App）、`mesh/build.gradle`、`settings.gradle`
