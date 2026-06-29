# 🔬 altic-dev/FluidVoice — 全方位深度调研

## 📌 一句话定位

**macOS 上最快的全本地语音转文字（离线听写）应用** — 支持 Nemotron Speech 3.5/Parakeet/Whisper/Apple Speech 等 8 种语音模型，所有语音数据不上云端，自带"Fluid Intelligence"本地 AI 增强引擎，支持命令模式和写作模式控制 Mac。Homebrew 一键安装，开源核心（GPLv3）+ 私有 AI 引擎的混合模式。

## ⭐ 项目亮点

1. **最快的 Parakeet 本地实现** — 官方宣称"几乎零延迟的 Parakeet 实现"，从说话到文字出现在屏幕上的延迟极低。这与 Whisper 那种需要整段音频处理完后才出文字的方式不同，是流式（streaming）的
2. **"Fluid Intelligence"本地 AI 增强引擎** — 完全本地的 AI 后处理：智能格式排版、上下文感知大写、后处理纠错——无需云 API Key，无需数据离机。这是跟 Dragon Dictate 等服务化产品的核心差异
3. **命令模式 + 写作模式（Command/Write Mode）** — 不仅做听写，还能通过语音控制 Mac：启动应用、运行 Shortcuts、选中文本后改写、在任意应用文本框中语音编写。这已经突破了"语音转文字"的范畴
4. **每应用独立 Prompt 配置（Per-App Configuration）** — 不同应用可以配不同提示词集合。写代码时用技术 prompt，写邮件时用正式 prompt——这是专业级设计
5. **`brew install --cask fluidvoice` 的一键体验** — 从安装到使用的门槛极低。8 种语音模型覆盖 99 种语言，Apple Silicon + Intel 全支持

## 🏗️ 项目架构全景

### 文件结构

```
FluidVoice/
├── Fluid.xcodeproj/      # Xcode 项目（SPM 依赖管理）
├── Package.swift          # SPM 包配置
├── Sources/Fluid/        # 主代码
│   ├── AppDelegate.swift  # 应用入口
│   ├── ContentView.swift  # SwiftUI 主视图
│   ├── Services/          # 核心服务层（~40 文件）
│   │   ├── ASRService.swift           # ASR 核心（多模型转录）
│   │   ├── ParakeetRealtimeProvider   # Parakeet 流式实现
│   │   ├── WhisperProvider.swift      # Whisper 封装
│   │   ├── AppleSpeechProvider.swift  # Apple 系统语音
│   │   ├── NemotronProvider.swift     # Nemotron 集成
│   │   ├── FluidAudioProvider.swift   # 音频采集
│   │   ├── CommandModeService.swift   # 命令模式
│   │   ├── RewriteModeService.swift   # 写作/改写模式
│   │   ├── TypingService.swift        # 跨应用文本注入
│   │   ├── PrivateAIProvider.swift    # Fluid Intelligence 集成
│   │   ├── DictationPostProcessingService.swift
│   │   ├── GlobalHotkeyManager.swift  # 全局热键
│   │   ├── NotchOverlayManager.swift  # 转录悬浮窗
│   │   └── ModelRepository.swift      # 模型下载管理
│   ├── Persistence/       # 持久化（Keychain/UserDefaults）
│   ├── Networking/        # 网络层（AI Provider）
│   └── UI/                # SwiftUI 视图
└── Tests/
```

### 语音模型矩阵

| 模型 | 延迟 | 语言 | 下载大小 | 硬件 |
|------|------|------|---------|------|
| Nemotron Speech 3.5 → Ultra Fast | 流式，极低 | ~40 语言 | ~670MB | Apple Silicon |
| Parakeet Flash (Beta) | 最低 | English | ~250MB | Apple Silicon |
| Parakeet TDT v3 | 低 | 25 语言 | ~500MB | Apple Silicon |
| Parakeet TDT v2 | 低 | English | ~500MB | Apple Silicon |
| Cohere Transcribe | 中 | 14 语言 | ~1.4GB | Apple Silicon |
| Apple Speech | 零下载 | 系统语言 | 内置 | Apple Silicon + Intel |
| Whisper (Tiny→Large) | 高 | 99 语言 | 75MB→2.9GB | Apple Silicon + Intel |

### 核心架构流

```
语音输入 → AudioDeviceService（音频采集）
    → ASRService（多模型路由）
        → ParakeetRealtimeProvider / WhisperProvider / AppleSpeechProvider / NemotronProvider
        → 转录文本
    → DictationPostProcessingService（可选 AI 增强）
        → PrivateAIProvider（Fluid Intelligence 本地）/ OpenAI / Groq 等云端
    → TypingService（跨应用注入）
        → Accessibility API → 目标文本框
```

### 流式转录（Parakeet 的核心优势）

```swift
// 简化骨架：TranscriptionExecutor actor（ASRService 中的并发控制）
private actor TranscriptionExecutor {
    // 严格串行化 CoreML 转录（防竞态条件）
    func run<T>(_ operation: @escaping () async throws -> T) async throws -> T {
        let previous = self.lastTask
        let task = Task<T, Error> {
            _ = await previous?.result      // 等前一个完成
            return try await operation()    // 再执行当前
        }
        self.lastTask = Task { _ = try? await task.value }
        return try await task.value
    }
}
```

**为什么这个重要**：CoreML 在并发访问时有竞态条件问题，`TranscriptionExecutor` actor 通过 Task 链严格串行化。这是实时转录应用的关键底层设计。

## 💡 应用场景与启发

### 典型使用场景

- **程序员语音编码**：写作模式下在 VS Code/Cursor 中用语音直接写代码或注释，每应用独配 prompt
- **会议记录**：MeetingTranscriptionService 支持会议模式，转录历史可本地归档
- **Mac 全语音控制**：命令模式下"启动 Chrome"、"新建文件夹"、"打开系统偏好设置"——不需要记快捷键
- **残障辅助**：免费、离线、跨应用——是 macOS 上最完整的语音辅助工具之一
- **多语翻译工作者**：Nemotron 3.5 支持 ~40 种语言，一键切换

### 可借鉴的解决方案模式

1. **本地 AI 引擎（Fluid Intelligence）作为增值层** — 核心开源（GPLv3）+ 私有增强引擎。这是开源项目可持续的商业化模式：核心功能免费，高级本地 AI 引擎单独维护。用户"福利"（高级功能）不依赖云服务
2. **每应用 Prompt 路由** — 不同应用自动匹配不同的转录后处理 prompt。这个设计可以扩展到任何 AI 辅助工具：一个 AI 写作助手在 IDE 中应该是"代码补全"模式，在 Mail 中应该是"正式邮件"模式
3. **Everything is Optional** — README 明确说"AI enhancement, Fluid Intelligence, audio history, analytics, and beta builds are all opt-in"。用户隐私通过"全部默认关闭"保障而不是"隐私政策承诺"

### 同类需求的可参考思路

如果你也在做一个"本地 AI 应用"：

- **流式 > 批处理** — Whisper 的"录音完才能出文字"体验远不如 Parakeet 的"边说边出"。用户对延迟的敏感度 > 对精度的敏感度
- **模型选择即产品功能** — 给予用户从零下载（Apple Speech）到高精度（Nemotron 3.5）到广泛语言（Whisper 99 语言）的连续光谱选择——这是给用户控制感
- **Accessibility API 比模拟键盘更可靠** — `TypingService` 使用 macOS 辅助功能 API 注入文本，而非模拟键盘事件。这对跨应用兼容性至关重要

## 🧠 核心源码解读（克制代码量）

### 模块 1：ASRService — 多模型转录总管

ASRService 是整个应用的中央调度器，管理着多个转录提供者（Parakeet、Whisper、Apple Speech、Nemotron）。关键设计是 `TranscriptionExecutor` actor 对 CoreML 并发访问的序列化（见上文代码片段），以及通过 `switch` 在多提供者间选择。

### 模块 2：GlobalHotkeyManager — 全局热键系统

macOS 全局热键是一个众所周知的难题（需要 CGEvent 权限、系统偏好设置授权）。FluidVoice 通过 Combine Publisher 模式管理热键事件：

```swift
// 简化骨架
class GlobalHotkeyManager: ObservableObject {
    func registerHotkey(_ shortcut: HotkeyShortcut) {
        // 通过 Carbon RegisterEventHotKey API 注册
        // 事件回调 → Combine PassthroughSubject
        // → 触发 ASRService.start() 或 command mode
    }
}
```

### 模块 3：TypingService — 跨应用文本注入

TypingService 是"语音转文字"最后一步的关键——把转录文本注入到用户当前聚焦的应用。使用 Accessibility API（AXUIElement）而非模拟键盘事件：

```swift
// 简化骨架
class TypingService {
    func typeText(_ text: String, into element: AXUIElement) {
        // 1. 获取聚焦的文本控件
        // 2. 用 AXUIElementSetAttributeValue 注入文本
        // 3. 支持选中文本后改写（Rewrite Mode）
    }
}
```

**为什么不模拟键盘**：`CGEvent` 键盘事件在某些 app（如终端、IDE）中行为不可预测，且不支持中文输入法。Accessibility API 是 macOS 上最可靠的跨应用文本注入方式。

## 📐 架构决策与设计哲学

### "先做 macOS 独占"

FluidVoice 从一开始就只做 macOS（SwiftUI + Swift Package Manager）。这对功能深度的帮助巨大：
- 原生 notch-overlay（DynamicNotchKit 库）
- 原生 Menu Bar 集成
- 原生 Accessibility API 文本注入
- Sparkle 风格的自动更新（AppUpdater 库）

作为对比，跨平台方案在 macOS 上通常会损失这些原生体验。

### "开源核心 + 私有增值"混合许可

- 2026-02-23 之前：Apache 2.0
- 2026-02-23 之后：GPLv3
- Fluid Intelligence：私有维护，不开源

这是一个清晰的信息：核心听写能力是免费开源的，但本地 AI 增强引擎是商业化的。GPLv3 的选择也防止了商业公司直接 fork 走做封闭产品。

### Privacy-by-Default

- 所有语音数据默认本地
- 云端 AI Provider 必须用户手动配置 API Key（Keychain 存储）
- Analytics 是 opt-out（用户可在设置中关闭）
- "Not Collected" 清单明确列出了：声音/音频/转录文本/选中文本/提示词/终端命令/窗口标题/文件路径/剪贴板——几乎没有灰色地带

## 🌐 全网口碑画像

### 好评共识

| 来源 | 评价 |
|------|------|
| 什么值得买（smzdm）| "高效、私密且实时的语音输入体验……支持多语言输入、全局热键操作、自动增强" |
| Utilo 评测平台 | 评分良好，"将安全性放在首位" — 隐私是用户最认可的点 |
| Brave 社区 | "强大的 Mac 语音输入解决方案……命令模式和写作模式将传统语音听写提升到新高度" |
| GitHub Star 增长 | 4323⭐（快速上升），856 stars today 说明今天大火 |
| Discord 社区 | 活跃的 Discord 频道，479 open issues 有大量用户反馈 |

### 差评共识 & 踩坑高发区

从 GitHub Issues（479 open！）可以看到一些高频用户痛点：

- **音频设备冲突** — Issue #452 "AirPods playback briefly drops when starting dictation" — 蓝牙耳机用户的高频痛点
- **AI Enhancement 截断** — Issue #457 "AI Enhancement cutting off parts of prompt" — AI 后处理时的 prompt 长度问题
- **转录粘贴失败** — Issue #469 "Dictation won't paste into any app no matter what copy setting I change" — Accessability API 的边界场景
- **模型重置** — Issue #467 "Speech model silently resets to Whisper Tiny after an in-app update" — 更新的状态持久化 Bug
- **命令模式阻塞** — Issue #444/445/446 分别讨论了 terminal 命令执行、reasoning model 兼容性和 macOS 权限对话框导致的卡死

**注意**：479 个 open issues 对于一个 4.3k Star 的项目来说偏高。但很多是 feature request 和提升性讨论，说明社区活跃度高，但也可能意味着维护压力大。

### 维护者响应

- 平均响应速度较快，有活跃的 PR 审查
- Discord 社区活跃（从 README 链接可见）
- 赞助上已启用 GitHub Sponsors

## ⚔️ 竞品对比

| 维度 | FluidVoice | macOS 内置听写 | Dragon Dictate | MacWhisper |
|------|-----------|--------------|---------------|-----------|
| **语音模型** | 8 种（含 Parakeet/Nemotron/Whisper）| Apple Speech 限定 | 云端 | 仅 Whisper |
| **离线** | ✅ 全部支持 | ✅ | ❌ 需联网 | ✅ |
| **命令模式** | ✅ | ❌ | ✅ | ❌ |
| **写作模式** | ✅ | ❌ | ❌ | ❌ |
| **每应用 Prompt** | ✅ | ❌ | ❌ | ❌ |
| **AI 增强** | ✅ 本地 + 云端可选 | ❌ | ❌ | ❌ |
| **macOS 版本** | 15.0+ | 内置 | 10.15+ | 13.0+ |
| **硬件** | Apple Silicon + Intel | 全系 | 全系 | Apple Silicon |
| **价格** | 免费 (GPLv3) | 免费 | 付费（$300+/年）| 免费/Pro |
| **安装** | brew install | 内置 | 官网下载 | App Store |

**选择建议**：要最强离线听写 + 语音控制 → FluidVoice。只需要基础听写 → macOS 内置足够。企业级付费方案 → Dragon Dictate。只要 Whisper 单模型 → MacWhisper。

## 🎯 核心研判

### 项目优势
- **macOS 上最完整的离线听写体验** — 模型选择面、功能深度（命令/写作/改写）、用户体验（notch overlay）三者综合最优
- **流式 Parakeet 实现** — 这是 Whisper 路线做不到的"边说边出"体验，对用户主观延迟感知差异极大
- **开源核心 + 私有引擎的可持续模式** — 不依赖云 API、不出卖用户数据。这是当前 AI 开源项目最被认可的商业化路径之一

### 项目风险
- **维护压力巨大** — 479 open issues 对于一个 4.3k Star 的单人/小团队项目是沉重负担。很多是 feature request，但也有一些影响使用体验的 bug（#469 粘贴问题等了 4 天仍未解决）
- **macOS Sequoia 独占** — macOS 15.0 的最低要求意味着大量 Intel Mac + 旧版本用户被排除（虽然 1.5.1+ 支持了 Intel + Whisper）
- **Fluid Intelligence 私有化** — 如果 Fluid Intelligence 是核心差异化功能却不开源，长期可能引起开源社区的不满

### 趋势判断
- **快速上升期** — 今天 Trending 上一天 836 星说明曝光度正在爆发。Homebrew 一键安装降低了获取门槛
- 下一步关注点：是否推出 Windows 版本（从 GitHub Sponsors 页面暗示"future platform work for iOS and Windows"）、Fluid Intelligence 是否会部分开源

## 📂 关键文件路径速查

| 文件 | 说明 |
|------|------|
| `Sources/Fluid/Services/ASRService.swift` | ASR 核心调度器（多模型转录 + 流式处理）|
| `Sources/Fluid/Services/ParakeetRealtimeProvider.swift` | Parakeet 流式实现（核心差异化）|
| `Sources/Fluid/Services/WhisperProvider.swift` | Whisper 封装（Intel Mac 兼容）|
| `Sources/Fluid/Services/NemotronProvider.swift` | Nemotron 多语言集成 |
| `Sources/Fluid/Services/PrivateAIProvider.swift` | Fluid Intelligence 本地 AI 引擎 |
| `Sources/Fluid/Services/GlobalHotkeyManager.swift` | 全局热键管理 |
| `Sources/Fluid/Services/TypingService.swift` | Accessibility API 文本注入 |
| `Sources/Fluid/Services/CommandModeService.swift` | 命令模式 |
| `Sources/Fluid/Services/RewriteModeService.swift` | 写作/改写模式 |
| `Sources/Fluid/Models/HotkeyShortcut.swift` | 热键数据模型 |
| `Package.swift` | SPM 依赖（FluidAudio/DynamicNotchKit/AppUpdater）|
| `build.sh` | 构建脚本 |
| `scripts/check-team-id.sh` | Git pre-commit hook |
