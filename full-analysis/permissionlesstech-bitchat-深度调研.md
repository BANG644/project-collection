# 🔬 bitchat 深度调研

> **仓库地址**: https://github.com/permissionlesstech/bitchat
> **Stars**: 32,017 ⭐ | **语言**: Swift | **许可证**: Unlicense（公有领域）| **创建**: 2025-07-04
> **平台**: iOS / macOS | **作者**: permissionlesstech（Jack Dorsey / Block 团队）
> **白皮书**: `WHITEPAPER.md`（v2.0, 2026-07-06）

---

## 一、项目定位

bitchat 是一款**去中心化、点对点的加密通讯应用**：本地用蓝牙 LE 自组网状网络（离线可用），远程用 Nostr 协议跨互联网互通。无账号、无手机号、无中心服务器——官方定位为 "the side-groupchat"。

---

## 二、项目亮点（差异化）

- 📡 **双传输混合架构**：BLE mesh（离线/灾难场景）+ Nostr relay（全球可达），`MessageRouter` 自动择优
- 🔐 **分层端到端加密**：实时会话用 Noise XX（前向安全），离线密封用 Noise X，Nostr 路径用自研 XChaCha20-Poly1305 信封
- 📦 **四层存储转发栈**：发件箱 + 移动信使（spray-and-wait）+ 公聊 gossip 同步 + Nostr 邮箱，覆盖"对方此刻不在无线电范围"的全部情形
- 🧹 **紧急擦除（Panic Wipe）**：三击即清全部身份/收藏/历史，设计以"可被瞬间抹除"为安全模型
- 🌍 **地理频道**：用 geohash 精度把 Nostr 公共房间切成 block/neighborhood/city/province/region 层级

---

## 三、核心架构

```
┌─────────────────────────────────────────────┐
│               MessageRouter (协调者)          │
├──────────────────────┬──────────────────────┤
│  BLE Mesh Transport  │   Nostr Transport     │
│ (GATT central+periph)│ (kind-1059 信封)      │
│ 受控洪泛 / 最多 7 跳  │ 290+ relay 网络       │
└──────────────────────┴──────────────────────┘
         ↓ 都无法及时送达时启用
┌─────────────────────────────────────────────┐
│  Store-and-Forward: Outbox / Couriers /      │
│  Gossip Sync (GCS filters) / Nostr Mailbox  │
└─────────────────────────────────────────────┘
```

**BLE 层**：每设备同时是 GATT central 与 peripheral，受控洪泛（TTL 7，密集图 clamp 到 5）。LRU seen-set（1000 条 / 5 分钟）去重，fanout subsetting（~log₂(度数)）控制广播扩散，~469 字节分片重组。
**Nostr 层**：私信走 BitChat 私有信封（kind 13 seal 包 kind 1059 envelope），`v2:` 前缀内容是 secp256k1 ECDH + HKDF-SHA256 派生的 XChaCha20-Poly1305——**复用 NIP 的 kind 号但不兼容 NIP-17/44/59**，仅 BitChat 客户端互通。

---

## 四、应用场景与启发

| 场景 | 价值 |
|------|------|
| 抗议 / 灾难 / 无网地区通讯 | BLE mesh 完全离线，是少数真正"断网可用"的聊天 |
| 审查规避 | Nostr 走 Tor + 流量混淆（自有信封），无中心可封 |
| 临时群组 / 活动现场 | 地理频道 + 无需注册，开箱即用 |
| **架构启发** | 「双传输 + 存储转发」是离线优先通讯的范本：把"可达性"与"内容"彻底解耦，信封邮戳随机化 ±15 分钟抗时序关联 |

> 类比：Briar 也做蓝牙 mesh 但无 Nostr 全球桥；bitchat 用 Nostr 把"本地 feral mesh"和"全球可达"缝合，是设计上最值得借鉴的一点。

---

## 五、源码解读（核心模块）

**1. 协议白皮书即事实标准** — `WHITEPAPER.md` 把协议"as implemented"逐字段写清，是少见的工程与文档同版本号（v2.0）项目：

```
Noise XX（实时）: Curve25519 / ChaCha20-Poly1305 / SHA-256 → 互相认证 + 前向安全
Noise X（离线密封）: 单向密封到静态公钥 → 无前向安全（预密钥为未来工作）
Nostr 信封: secp256k1 ECDH + HKDF-SHA256 → XChaCha20-Poly1305 (v2: 前缀)
```

**2. 信使系统（Courier）** — 把无法直送的私信密封后托付给最多 3 个邻近节点，用 16 字节每日轮换的 HMAC 接收标签做"不透明寻址"，spray-and-wait 让邮件随移动人群扩散：

```
copy budget 初始 4 / 上限 8；相遇另一信使时让出一半预算
favorites 配额 5 / 普通已验证节点 2；池 20/40，永不让 favorites 邮件被挤掉
```

---

## 六、社区口碑

- **爆红项目**：Jack Dorsey 背书，App Store 已上架，单日 +2,344 stars，长期居 Trending 前列
- **透明度加分的诚实**：白皮书第 8、9 节**主动披露**两大弱点——元数据可被被动监听关联（8 字节 peer ID 永不轮换）、离线密封/Nostr 信封无前向安全——这种"把局限写进协议文档"的做法口碑极佳
- **争议/风险**：README 明言"本仓库曾收到下架要求，仓库消失时会出现无人可核的镜像"，且私有信封不兼容标准 Nostr 客户端（互操作锁定）

---

## 七、竞品对比 + 核心研判

| 项目 | 传输 | 服务器 | 前向安全 | 特点 |
|------|------|--------|---------|------|
| **bitchat** | BLE mesh + Nostr | 无 | 仅实时会话 | 离线+全球混合，地理频道 |
| **Briar** | Bluetooth/Wi-Fi mesh + Tor | 无 | ✅ | 更成熟，但无 Nostr 全球桥 |
| **Session** | Oxen 区块链 + Lokinet | 去中心 | ✅ | 元数据最小化，但需节点 |
| **Signal** | 中心服务器 | 有 | ✅ | 易用标杆，但依赖中心 |
| **SimpleX** | 双跳 relay（无身份） | 无身份 | ✅ | 元数据最克制 |

**核心研判**：
- ✅ **优势**：把"离线 feral mesh"与"全球可达"缝合的设计在同类中最完整；白皮书级别的协议透明度建立信任；iOS/macOS 原生且已上架，落地门槛低
- ⚠️ **风险**：元数据暴露（peer ID 不轮换、announcement 明文昵称+邻居表）是已知软肋；离线密封缺前向安全；私有信封不兼容标准 Nostr 形成锁定
- 💡 **启发**：做"抗封禁通讯"时，bitchat 的「双传输 + 存储转发 + 地理频道」是可直接参考的架构骨架；其"诚实披露局限"的文档策略也值得任何安全项目学习

---

## 八、关键文件路径速查

| 路径 | 内容 |
|------|------|
| `WHITEPAPER.md` | 协议白皮书 v2.0（架构/加密/存储转发唯一权威）|
| `bitchat/` | iOS/macOS 主 App（Transport / MessageRouter 实现）|
| `bitchatShareExtension/` | 分享扩展 |
| `localPackages/` | 本地 Swift 包（加密/协议核心）|
| `relays/` | 自建 Nostr relay 参考实现 |
| `docs/VERIFYING-A-BUILD.md` | 按发布哈希清单校验构建来源 |
| `SECURITY.md` / `PRIVACY_POLICY.md` | 安全与隐私政策 |
