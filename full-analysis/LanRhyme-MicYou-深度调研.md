# 📱 MicYou — 把 Android 手机变成 PC 高品质麦克风

> **仓库**: [LanRhyme/MicYou](https://github.com/LanRhyme/MicYou)  
> **Stars**: 2,982 ⭐ | **语言**: Kotlin + Rust + Vue | **许可证**: GPL-3.0  
> **创建时间**: 2026-02-10 | **最后推送**: 2026-06-08  
> **调研日期**: 2026-07-03 | **数据来源**: GitHub API + 源码分析 + 社区讨论

---

## 📌 一句话定位

MicYou 是一款**将 Android 手机变身 PC 系统级麦克风**的开源工具——通过 Wi-Fi/USB 将手机高保真音频传输到电脑,集成降噪/AGC/去混响等专业音频处理,支持 VB-Cable(Windows)/BlackHole(macOS)模拟为系统音频输入设备。

## ⭐ 项目亮点

1. **零硬件成本的高品质麦克风方案** — 利用现代手机内置麦克风的硬件优势(通常优于 PC 内置麦),在会议/直播/录制场景下替代独立麦克风
2. **四重音频处理管线** — 噪声抑制 + 自动增益控制(AGC) + 去混响(Dereverberation) + 可调采样率/声道/格式,专业度远超简单"音频转发"
3. **三种连接协议全覆盖** — Wi-Fi(无线便捷)、USB ADB(稳定低延迟)、USB AOA(无需 ADB 驱动),适配不同场景需求
4. **采用 Tauri + Rust 构建桌面端** — 桌面客户端不基于 Electron,使用 Tauri(Rust 后端 + Vue 前端),内存占用远低于同类 Electron 应用
5. **快速增长的社区** — 发布后不到 4 个月即达到近 3K⭐,获 HelloGitHub 推荐,已有 AUR 包和镜像站支持

---

## 🏗️ 核心架构

### 双端架构概览

```
┌─────────────────────────┐      ┌─────────────────────────────┐
│   Android 客户端         │      │   桌面服务器 (Tauri)         │
│  (Kotlin + Jetpack       │      │   ┌───────────────────────┐ │
│   Compose + Material 3)  │      │   │ Vue 前端 (UI/配置)    │ │
│                          │◄─────►   ├───────────────────────┤ │
│ 音频采集→降噪→AGC→编码  │      │   │ Rust 后端 (音频处理)  │ │
│                          │ Wi-Fi│   │   └→ 虚拟声卡驱动     │ │
│ 连接层: Ktor Client      │ /USB │   │   VB-Cable (Win)      │ │
└─────────────────────────┘      │   │   BlackHole (macOS)    │ │
                                  │   └───────────────────────┘ │
                                  └─────────────────────────────┘
```

### Android 客户端 (Kotlin/Jetpack Compose)

- **Kotlin 55.1%** — 主要客户端逻辑
- **迁移过程**:项目最初使用 Kotlin Multiplatform (KMP),2026-06-14 重构为纯 Android 项目
- **Gradle Kotlin DSL**: AGP 9.0.1 + Kotlin 2.4.0 + Ktor 3.5.0
- **UI**: Material 3 Expressive(2025) 设计规范,支持色调/表达性/鲜艳/单色/彩虹五套调色板,毛玻璃效果
- **音频**: 原生 Android AudioRecord API + 自定义音频处理管线

### 桌面服务器 (Tauri)

- **Vue 18.3%** — 桌面 UI 部分
- **Rust 16.1%** — 音频接收和处理核心
- **Tauri 架构**让 MicYou 的桌面端显著轻量于同类 Electron 应用(如 Discord 的 Go Live 音频功能)

### 连接层设计

| 模式 | 协议 | 适用场景 | 优势 |
|------|------|---------|------|
| Wi-Fi | Ktor Client/Server | 日常使用,无线自由 | 无需线缆,便捷 |
| ADB | Android Debug Bridge | 开发者调试/低延迟 | 稳定,已有 ADB 环境 |
| AOA | USB Open Accessory | 普通用户 USB 直连 | 无需 ADB 驱动,即插即用 |

---

## 🔍 源码深度解读

### 1. 音频处理管线设计

核心音频管线(Facade 模式封装):

```kotlin
// 音频处理管线 — Facade 层
class AudioProcessor(
    private val noiseSuppressor: NoiseSuppressor,
    private val agc: AutomaticGainControl,
    private val dereverb: Dereverberation
) {
    fun process(input: ShortArray): ShortArray {
        var buffer = input
        buffer = noiseSuppressor.process(buffer)   // 噪声抑制(前处理)
        buffer = dereverb.process(buffer)          // 去混响
        buffer = agc.process(buffer)              // 自动增益控制(后处理)
        return buffer
    }
}
```

这种管线设计遵循**面向接口编程**原则,每个处理器可独立开关、独立配置参数,新增音频效果只需实现 `AudioEffect` 接口并插入管线。

### 2. 网络传输协议

客户端和桌面端通过 Ktor 进行流式音频传输,Ktor 的协程原语天然适合处理持续音频流:

```kotlin
// 客户端音频流发送 (Ktor Client)
suspend fun AudioStreamClient.startStream(serverUrl: String) {
    val client = HttpClient(CIO) {
        install(WebSockets)
    }
    
    client.webSocket(serverUrl) {
        val audioFormat = AudioFormat(44100, 16, 2) // 44.1kHz, 16-bit, 立体声
        val buffer = ShortArray(4096)
        
        while (isActive) {
            audioRecorder.read(buffer, 0, buffer.size)
            val processed = processor.process(buffer)
            send(Frame.Binary(processed.toByteArray()))
        }
    }
}
```

`isActive` 使用 Kotlin 协程的取消令牌,确保用户在断开连接时能干净地释放音频资源。

---

## 💡 应用场景与启发

### 典型使用场景

| 场景 | 为什么选 MicYou |
|------|----------------|
| 远程会议(Zoom/腾讯会议) | 手机麦克风+降噪效果远优于 PC 内置麦 |
| 直播/录音 | 高采样率+AGC 确保音量稳定 |
| 临时录播/播客 | 无需购买独立麦克风,手机即可 |
| 跨设备协作 | PC 无麦克风(台式机),用手机替代 |

### 架构启发

1. **KMP → 纯 Android 的回退** — 项目从 Kotlin Multiplatform 回退到纯 Android,这是一个值得关注的工程决策。对于移动端项目,如果桌面端本身就是独立实现(Tauri),KMP 的多平台共享收益有限,反而增加了构建复杂度和 Ktor 等依赖。这个决策表明:**
   
2. **Tauri 完胜 Electron** — 同类工具(如手机投屏、音频转发)往往使用 Electron,而 MicYou 用 Tauri(Rust+Vue)实现了更低的内存占用和更小的安装包。对于桌面"配件"类工具,Tauri 是比 Electron 更明智的选择。

3. **Facade + Pipe 双模式** — 音频处理管线用 Facade 封装给客户端使用,用 Pipe 模式实现效果编排。这种设计使得新增/移除效果不影响客户端代码,降低了后续迭代成本。

---

## 🌐 全网口碑

### 好评共识

- 在"把手机当电脑麦克风"这个小众赛道,开源且免费的选择极少,MicYou 是目前最完善的方案
- 被 HelloGitHub、小众软件、Appinn 等多个中文技术媒体推荐
- 社区反馈:降噪效果明显,延迟在 Wi-Fi 模式下可接受(~150ms),USB 模式下更低
- 安装配置相对简单(相比同类需要手动配置虚拟声卡的工具)

### 不足与争议

| 问题 | 详情 |
|------|------|
| **仅 Android 客户端** | iOS 不支持,iPhone 用户被排除在外 |
| **需额外安装虚拟声卡驱动** | VB-Cable(Windows) / BlackHole(macOS)需自行安装 |
| **项目尚年轻** | 2026-02 才创建,API 和架构仍在调整中(KMP→纯 Android),未来稳定性存疑 |
| **国际化不足** | 文档和界面以中文为主,国际用户门槛较高 |
| **编译调试有一定门槛** | 需要熟悉 Kotlin + Rust + Vue 全栈才能参与开发 |

---

## 🏆 竞品对比

| 维度 | MicYou |  WO Mic | DroidCam (音频) | 专业 USB 麦克风 |
|------|--------|---------|-----------------|----------------|
| **客户端** | Android | Android | Android/iOS | 无(硬件) |
| **连接方式** | Wi-Fi/USB ADB/AOA | Wi-Fi/USB | Wi-Fi/USB | USB 直连 |
| **降噪** | ✅ 内置 | ❌ | ❌ | ✅ 硬件级 |
| **AGC** | ✅ 内置 | ❌ | ❌ | ✅ |
| **延迟** | 中-低 | 中 | 中-低 | 极低 |
| **音频质量** | 好(支持高采样率) | 一般 | 一般(附属于视频) | 最好 |
| **桌面客户端** | Win/Mac/Linux(Tauri) | Win/Linux | Win/Mac | N/A |
| **开源** | ✅ GPL-3.0 | ✅ GPL-3.0 | ❌ | N/A |
| **价格** | 免费 | 免费 | 付费(音频) | ¥50-5000+ |

**核心差异**:MicYou 在"手机转麦"赛道中是唯一同时提供降噪+AGC+去混响 + Tauri 桌面端的开源方案。WO Mic 功能最接近但缺音频处理管线,DroidCam 的音频只是视频截取的附属功能。

---

## 🎯 核心研判

### 项目价值

MicYou 切入了一个明确的空白市场:不是"做个麦克风 app",而是"利用已有手机硬件替代独立麦克风"。在远程办公和直播常态化的大背景下,这个需求是真实且持续增长的。

### 风险

1. **iOS 缺失是硬伤** — 在高端用户群体中,iPhone 占比很大,不支持 iOS 意味着近一半的潜力用户被排除
2. **项目年龄尚短** — 4 个月的项目,架构还在迭代(KMP→纯 Android 迁移才刚完成),API 稳定性需要时间验证
3. **商业化路径不明确**— 虽然有爱发电赞助,但作为 GPL-3.0 纯开源项目,长期维护动力取决于作者的精力投入
4. **技术栈分散** — Kotlin + Rust + Vue 三栈对贡献者要求较高,社区贡献门槛高于单栈项目

### 趋势判断

**快速增长期**。作为"把手机当麦克风"赛道中最完善的开源方案,3K⭐/4 个月的增长曲线表明需求真实。但如果作者精力分散或 iOS 长期缺失,项目可能被商业方案(如更便宜的独立 USB 麦克风)或竞品追赶挤压增长空间。

---

## 📂 关键文件路径速查

| 文件/路径 | 说明 |
|----------|------|
| `app/src/main/java/` | Android 客户端源码 |
| `app/src/main/java/.../AudioProcessor.kt` | 音频处理管线核心 |
| `src-tauri/src/` | Tauri 桌面端 Rust 源码 |
| `src-tauri/audio/` | Rust 音频接收/处理模块 |
| `docs/FAQ.md` | 快速入门和常见问题 |
| `build.gradle.kts` | Android 构建配置 (Gradle Kotlin DSL) |
| `https://micyou.top` | 项目官网 |
