# Screenpipe 深度调研报告

> 调研日期：2026-06-27 | Stars: 19,515 | 公司：YC S26 | 开源协议：MIT

---

## 一、一句话定位

**Screenpipe 是一个 24/7 本地运行的 AI 屏幕+音频记录引擎——为 AI Agent 提供完整的人类数字工作上下文，让你从此不需要"打字提问"。**

它既不是传统的"录屏软件"，也不是简单的"会议纪要工具"，而是定位为 **AI Agent 的上下文基础设施层**：截取你每一秒的屏幕内容（OCR 或无障碍树提取文字）+ 麦克风与系统音频转写，全部本地索引、本地存储，并通过 REST API / MCP 协议供任意 AI 消费。

---

## 二、项目亮点

### 1. 事件驱动（Event-Driven）捕获架构

**这是在代码层面最被低估的架构决策**。早期版本（core.rs 中可看到注释说明）是轮询（polling-based `continuous_capture`），后来完全重写为事件驱动模型：

```rust
// crates/screenpipe-engine/src/event_driven_capture.rs
// This module previously contained the legacy continuous capture pipeline
// (start_continuous_recording, record_video, VideoCapture).
// That code has been removed in favor of event-driven capture.
```

捕获只发生在有意义的事件上：**应用切换、窗口焦点变化、点击、打字暂停、滚动停止、剪贴板变化**，以及每 30 秒一次的 Idle fallback。对比轮询方案，这种设计对 CPU 的消耗降低了 1-2 个数量级，让 24/7 后台运行变得可行。

```rust
/// Types of events that trigger a capture.
pub enum CaptureTrigger {
    AppSwitch   { app_name: String, target: Option<(i32, i32)> },
    WindowFocus { window_name: String, target: Option<(i32, i32)> },
    Click       { x: i32, y: i32 },
    TypingPause,
    ScrollStop,
    KeyPress,
    Clipboard,
    VisualChange,
    Idle,
    Manual,
}
```

默认配置：最小捕获间隔 200ms，空闲捕获间隔 30s，JPEG 质量 80，视觉变化阈值 5%。

### 2. 三层文本提取：无障碍树 > OCR > 自定义

绝大多数同类产品只做 OCR（截图+识别），Screenpipe 的设计中**无障碍树（Accessibility Tree）是优先方案**，OCR 只是 fallback。这意味着：

- 在 macOS/Linux/Windows 上，它通过 A11Y API 直接读取 UI 元素文本，比 OCR 更快、更准、更省电
- 仅在无障碍树无法覆盖时才回退到 Tesseract OCR / Apple Vision / Windows OCR
- 还支持自定义 OCR（`CustomOcrConfig`），可接入私有 OCR 服务

代码中可以看到跨平台的无障碍实现：
- `crates/screenpipe-a11y/src/platform/macos.rs`
- `crates/screenpipe-a11y/src/platform/windows_uia.rs`
- `crates/screenpipe-a11y/src/platform/linux.rs`

此外还包含一个 **StreamLivenessWatch** 组件，用于检测屏幕捕获流是否僵死（如某些 DRM 内容导致流冻结），30 秒无帧序列增长则自动重启流。

### 3. Pipes 插件系统——真正的"个性化 AI 应用商店"

**Pipes 是 Screenpipe 最大的差异化能力。** 它不是一个固定的功能列表，而是一个插件运行时——任何人可以编写一个 pipe（JavaScript/TypeScript），订阅用户的屏幕/音频数据，输出任何结果。

已预置的 pipe 包括：Obsidian 同步、Gmail 日报、会议助手、LinkedIn 智能助手等。Pipes 通过 MCP 协议对外暴露，Cursor、OpenClaw、Claude Code 等工具可直接消费这些数据。

Pipe 安全性也有设计——有 `PipePermissions` 模块和 `pipe_permissions_middleware.rs`，限制 pipe 能访问的数据范围。

### 4. 90+ 外部连接器（Connectors）

`crates/screenpipe-connect/src/connections/` 目录下有超过 90 个连接器适配器：Slack、Notion、Jira、Linear、GitHub Issues、Google Calendar、Zoom、Teams、Obsidian、Discord、Salesforce、HubSpot、Stripe…**几乎覆盖了知识工作者使用的所有 SaaS 工具。**

每个连接器实现了 OAuth 流程和增量同步。`sync_scheduler.rs` 和 `remote_sync.rs` 负责定时同步数据回 Screenpipe 的本地数据库。

### 5. PII 自动脱敏管线

**这是从源码中挖掘到的重要隐私安全设计**，READEME 中很少提及。`crates/screenpipe-redact/` 是一个完整的 PII 识别与脱敏管线：

```rust
// pipeline.rs 中的核心策略
// 1. 正则预扫描（免费、确定性强）——捕获邮箱、信用卡、JWT、私钥块、连接字符串
// 2. 缓存命中则直接返回（同一文本+正则版本）
// 3. AI 回退（Tinfoil / ONNX）——仅当正则未完全覆盖且文本长度足够时调用
// 4. 优雅降级：AI 失败则只返还正则清洗结果，绝不返还未脱敏输入
```

支持图像级脱敏（`image/frame_redactor.rs`）和文本级脱敏（`adapters/regex.rs` + `adapters/rfdetr.rs`），甚至包含一个基于 MLX 的 RFDETR 实现（`crates/screenpipe-rfdetr-mlx/`）。

---

## 三、项目架构全景

```
┌──────────────────────────────────────────────────────────┐
│                    Tauri Desktop App                      │
│   (Next.js + shadcn UI, 纯黑白极简设计, 无圆角, 无颜色)      │
│   - 时间线(Timeline) / 搜索(Search) / 聊天(Chat) / 设置      │
└──────────────────────┬───────────────────────────────────┘
                       │ REST API (axum)
┌──────────────────────▼───────────────────────────────────┐
│                screenpipe-engine (核心引擎)                  │
│   - 事件驱动捕获 + 高帧率控制器 + 热帧缓存 + 资源监控         │
│   - Pipe Store + MCP Server + 连接器 API                   │
│   - 搜索路由 / 会议检测 / 存档 / 同步                       │
└──────┬──────────────┬──────────────┬──────────────────────┘
       │              │              │
┌──────▼──────┐ ┌────▼─────┐ ┌─────▼──────────────────┐
│ screenpipe   │ │screenpipe│ │screenpipe-redact       │
│ -screen      │ │ -audio   │ │  PII脱敏管线             │
│ 屏幕截图+OCR  │ │ 音频转录  │ │  - 正则/ONNX/AI混合    │
│  - Tesseract │ │  - Whisper│  │  - 图像级脱敏          │
│  - Apple Vis │ │  - Deepgram│ │  - 文本级脱敏          │
│  - Win OCR   │ │  - Parakeet│ │  - 假名化(Pseudonyms)  │
│  - Custom OCR│ │  - 声纹识别│ │                        │
│  - Xcap/WGC  │ │  - VAD    │ │                        │
│  - sck_rs    │ │  - 人声分离│ │                        │
└──────┬──────┘ └────┬─────┘ └──────────────────────────┘
       │              │
┌──────▼──────────────▼───────────────────────────────────┐
│              screenpipe-db (SQLite + FTS5)               │
│   - 帧索引 / OCR 文本 / 音频转录 / 视频块                │
│   - 全文搜索 + 时间范围过滤 + 应用/窗口过滤               │
│   - 访问无障碍树事件索引                                 │
└──────────────────────────────────────────────────────────┘
```

### 核心 crate 职责速览

| Crate | 职责 |
|-------|------|
| `screenpipe-engine` | 引擎入口、CLI、HTTP 路由、事件驱动捕获循环、会议检测 |
| `screenpipe-screen` | 屏幕截图、OCR（Tesseract/Apple/Windows/Custom）、帧对比 |
| `screenpipe-audio` | 音频流管理、Whisper/Deepgram/Parakeet 转录、VAD、声纹 |
| `screenpipe-db` | SQLite 数据库层、FTS5 全文搜索、写队列 |
| `screenpipe-a11y` | 无障碍树捕获、跨平台 A11Y 文本提取 |
| `screenpipe-redact` | PII 检测与脱敏（正则 + ONNX + AI） |
| `screenpipe-connect` | 90+ 外部服务的 OAuth 连接器 |
| `screenpipe-core` | Pipe 权限、同步、PII 移除、Agent 管道 |
| `screenpipe-events` | 全局事件管理器（音频状态、电源、连接、会议等） |
| `screenpipe-vault` | 加密存储敏感数据 |
| `screenpipe-secrets` | 密钥链集成（macOS Keychain / Windows Credential Manager） |

---

## 四、应用场景与启发

### 场景 1：知识工作者的"数字记忆"

**痛点**：每天的 Slack 讨论、Zoom 会议、代码 Review、Notion 文档——信息散落在十几个工具里，事后想找回"那个链接""那个数据"如同大海捞针。

**Screenpipe 解法**：24/7 记录一切，OCR 提取所有屏幕文字，音频转写所有对话，统一 SQLite 索引。直接在搜索框里输入"上周二 standup 上提到的那个 API key"，Screenpipe 会通过语义搜索命中对应的屏幕帧和音频片段。配合 Obsidian Pipe，每日工作内容自动回流到个人知识库。

**启发**：这种"被动采集 + 统一索引"的模式正在成为知识管理的默认范式。不是用户主动去"记笔记"，而是工具自动记录一切，需要时通过搜索/对话获取。

### 场景 2：AI Agent 的上下文供给

**痛点**：当前 AI Agent（如 Claude Code、Cursor）对用户"此时此刻在做什么"一无所知。Agent 只能根据当轮对话的有限输入推断上下文，经常答非所问。

**Screenpipe 解法**：通过 MCP 协议，Agent 可以直接查询 Screenpipe 的完整上下文——"用户在过去 5 分钟看了哪些文件、终端输出了什么错误、正在编辑哪个函数"。这比 RAG 更实时、比文件索引更精准。

**启发**：`VISION.md` 中明确提出——"Sending prompts is obsolete, AI should just watch and work." 这预示了下一代 AI 交互范式：不需要提问，AI 通过持续的上下文观察就能理解意图并主动行动。

### 场景 3：会议自动化笔记

**痛点**：手动记会议笔记分心、飞书/腾讯会议自带纪要质量不稳定、无法回溯会议中的屏幕共享内容。

**Screenpipe 解法**：音频管道自动转写会议（支持声纹识别区分发言人），配合屏幕 OCR 捕捉共享的 PPT/表格/链接。`meeting_detector.rs` 实现自动检测会议开始/结束（通过音频特征和日历事件），会议结束后 Pipe 自动生成结构化纪要。

**启发**：Screenpipe 的"日历连接 + 音频流分析 + 屏幕 OCR"三合一方案，正在模糊"会议纪要工具"的边界。比起独立的 Otter.ai 或 Granola，它的优势在于**不需要会议工具显式集成**——它被动监听，什么都记录。

### 场景 4：ADHD / 注意力障碍辅助

**有中文用户反馈的独特场景**（来自知乎和 Linux.DO 社区）：

> "注意力分散后经常忘记几分钟前在做什么，Screenpipe 可以回放我当时在看的页面和听到的内容，帮我快速回到状态。"

这种"数字记忆外挂"对注意力障碍者的价值巨大：不需要依赖大脑短期记忆，一切都有可搜索的记录。

**启发**：Screenpipe 的"记录 → 检索 → 回放"闭环，本质上是对人类有限注意力的补偿。在信息过载时代，这类工具正从"奢侈品"变成"必需品"。

---

## 五、核心源码解读

### 5.1 事件驱动的截图引擎

`crates/screenpipe-engine/src/event_driven_capture.rs` 是整个系统的调度核心。

关键设计：**事件先进入通道（trigger_channel），再按优先级合并（reduce_drained_triggers）**。多个事件同时到来时（比如用户在打字中切换窗口），只保留最高优先级的事件触发截图。

```rust
// 事件合并逻辑
fn reduce_drained_triggers(
    drained: Vec<CaptureTriggerMsg>,
    skip_clipboard: bool,
    skip_keypress: bool,
) -> (Option<CaptureTrigger>, Vec<CorrelationId>) {
    // 优先级：KeyPress > Clipboard > Click > 其他
    // 取最高优先级触发，携带所有 correlation_id
    let best = drained.into_iter()
        .fold(None, |best, msg| {
            let rank = trigger_rank(&msg.trigger);
            let best_rank = best.as_ref().map_or(-1, |b| trigger_rank(&b.trigger));
            if rank > best_rank { Some(msg) } else { best }
        });
    // ...
}
```

每个事件触发后，系统会检查帧是否与上一帧相同（`FrameComparer` + `FrameComparisonConfig`），只有确实变化时才存储——避免了静态桌面（如 IDE 闲置）的冗余记录。

帧损坏检测也内置：全黑帧（DRM 内容、睡眠唤醒中间态）和绿底带状帧（解码错误）会被自动丢弃，不影响索引。

### 5.2 音频转录管道

`crates/screenpipe-audio/src/core/` 下的音频处理链：

1. **音频来源**：麦克风 + 系统输出（通过 cpal / CoreAudio Process Tap / PulseAudio）
2. **VAD 检测**（`vad/silero.rs` + `vad/webrtc.rs`）：检测语音活动，只转写有语音的片段
3. **转录引擎**：支持 11 种引擎——Whisper（Tiny/LargeV3/LargeV3Turbo 等 + 量化版本）、Deepgram（云端）、Parakeet、Qwen3-ASR、OpenAI 兼容接口
4. **声纹识别**（`speaker/embedding.rs`）：使用 pyannote 模型（ONNX 格式）提取说话人嵌入，结合会议日历识别发言人身份
5. **会议检测**（`meeting_detector.rs` / `meeting_streaming/`）：自动检测会议开始/结束，支持 Deepgram 实时流式转写

```rust
// 转录引擎枚举，支持 11 种方案
pub enum AudioTranscriptionEngine {
    Deepgram,
    WhisperTiny,
    WhisperTinyQuantized,
    WhisperLargeV3Turbo,        // 默认
    WhisperLargeV3TurboQuantized,
    WhisperLargeV3,
    WhisperLargeV3Quantized,
    OpenAICompatible,
    Qwen3Asr,
    Parakeet,
    ParakeetMlx,
    Disabled,
}
```

### 5.3 搜索索引

`crates/screenpipe-db/src/db/search.rs` 实现了全功能搜索，基于 SQLite FTS5 全文索引：

```rust
pub struct SearchQuery {
    pub q: Option<String>,                    // 查询关键词
    pub content_type: ContentType,            // OCR / 音频 / 无障碍 / UI 事件
    pub start_time: Option<DateTime<Utc>>,    // 时间范围
    pub end_time: Option<DateTime<Utc>>,
    pub app_name: Option<String>,             // 应用过滤
    pub window_name: Option<String>,          // 窗口过滤
    pub include_frames: bool,                 // 是否包含帧数据
    pub min_length: Option<usize>,            // 最小文本长度
    pub offset: i64,
    pub limit: i64,
    pub order: Order,                         // 正序/倒序
}
```

搜索结果可同时包含 OCR 文本、音频转写、无障碍树文本和 UI 事件——**真正实现了跨模态的统一搜索**。配合 `include_related` 参数（从 Issue #4429 新增），还可以返回关联的帧和音频片段，实现搜索结果到原始上下文的跳转。

---

## 六、架构决策与设计哲学

### 为什么是 Event-Driven 而不是 Continuous？

这是项目最核心的架构决策。从 `core.rs` 的注释可以直接读出：

> "// This module previously contained the legacy continuous capture pipeline
> // That code has been removed in favor of event-driven capture."

**决策逻辑**：
- 连续轮询（每秒 1-30 帧）在 24/7 场景下 CPU 开销不可接受
- 事件驱动将平均捕获率降到每分钟几次，仅在真正有内容变化时才触发
- 使用 `HighFpsBookkeeping` 智能管理高帧率模式——只在会议/游戏等特定场景提高帧率

**权衡代价**：事件驱动方案依赖 OS 事件的可靠传递。某些场景（静默后台更新、全屏游戏）可能漏捕获。项目用 Idle fallback（30s 一次）和 VisualChange 检测来弥补。

### 为什么是 Local-First？

`VISION.md` 中明确："Data never leaves the device unless the user explicitly opts in."

**深层原因**：
- 屏幕录音包含最高敏感度数据（密码、银行账户、私人对话）
- 云端处理意味着信任成本和合规风险（GDPR、HIPAA、CCPA）
- 本地处理在 Latency 上比云端快 1-2 个数量级（搜索不经过网络）

**商业化的边界**：Screenpipe 采取了"核心引擎开源 + 云增值服务"的模式。本地处理免费完整可用，云服务（S3 归档、云端搜索、团队同步）是付费功能。`$400 lifetime license` 是桌面客户端的价格，CLI 可自行编译免费使用。

### Pipes 系统的设计哲学

Pipe 是 Screenpipe 最重要的扩展点，其设计原则是：

1. **数据不动，计算靠近数据**——Pipe 运行在用户本地，不把敏感数据传到外部
2. **渐进式披露**（来自 CLAUDE.md）——"always use progressive disclosure when designing agentic systems"
3. **权限隔离**——`PipePermissions` 限制每个 pipe 能访问的数据范围和频次

与 Obsidian 插件的类比：Obsidian 是个人知识库的插件商店，Screenpipe 是**个人活动数据的插件商店**。

---

## 七、全网口碑画像

### 中文社区

**知乎**（来自《Screenpipe 食用报告：甜美的梦》）：
- "Screenpipe 的出现使得个人较为完善地收集自身产生的数据并结构化存储成为了可能"
- "Screenpipe 的 Rust 含量极高，是生长潜力巨大的种子级项目"
- 实际体验：会议总结"对比飞书自带，较为好用"
- 批评：Windows 构建困难，官方 GUI 收费（$400），功能尚在迭代中

**Linux.DO 论坛**（2024 年 9 月）：
- "搜索目前只能单字搜索"（FTS5 早期限制，后续已改进）
- "由于大模型有上下文限制，总结还是不能太多上下文"
- "Windows 下没成功"——跨平台稳定性的早期问题
- "他的想法感觉比 Rewind 还好"
- 开发者社区活跃：Issue 有 $100+ 赏金

**CSDN / GitCode**：
- "离线版 Rewind.ai" 是中文社区最常见的标签
- 重点关注的维度：隐私保护（100% 本地化）、安装配置教程、OCROCR 优化

### 英文社区

**GitHub Issues**（真实运营状态速览）：
- 每日活跃：日均 10-20 个新 Issue / PR
- 社区质量高：Bug 报告带有详细的复现步骤和截图
- 核心 Bug 集中在：Windows 兼容性（Cortex XDR 杀进程 #4549）、蓝牙音频转写不完整（#4455）、高负载下搜索超时（#4474）
- Feature Request 活跃：用户对 pipes 和连接器生态有强烈需求

**YC 背景**：
- S26 批次，团队风格直接、迭代速度快（每天发版）
- VISION.md 中的原则："Ship daily. Small, focused changes. Every commit should be deployable."

### 性能口碑

- CPU 目标：< 20%（Release 构建）
- 内存目标：< 3GB RAM
- 磁盘占用：约 2-3 GB/月（持续录制）
- 中文用户反馈的共性问题：Windows 构建流程复杂、OCR 中文精度待提升

---

## 八、竞品对比

| 维度 | Screenpipe | Rewind.ai / Limitless | Microsoft Recall | Granola | Otter.ai |
|------|-----------|----------------------|-----------------|---------|----------|
| **屏幕捕获** | 有（事件驱动） | 有 | 有（NPU） | 无 | 无 |
| **音频转录** | 有（本地/云端） | 无 | 无 | 有（云端） | 有（云端） |
| **数据本地化** | 100% 本地 | 云端 | 本地（Windows 11） | 云端 | 云端 |
| **开源** | MIT 开源 | 闭源 | 闭源（系统功能） | 闭源 | 闭源 |
| **跨平台** | macOS/Win/Linux | macOS（原）+ 硬件挂坠 | Windows 11 仅 | macOS/Windows | Web |
| **开发者 API** | REST + MCP | 有限 | 无 | 无 | 有限 |
| **Pipes 插件** | 支持（核心差异化） | 无 | 无 | 无 | 无 |
| **连接器生态** | 90+ 工具 | 少 | Windows 生态内 | 日历 | 日历+会议 |
| **PII 脱敏** | 内置管线 | 未知 | 无 | 无 | 无 |
| **终身价格** | $400 | $20/月 | 免费（需 Copilot+ PC） | $10/月 | $17/月 |
| **会议检测** | 自动（音频+日历） | 手动 | 无 | 手动 | 自动（会议加入） |
| **声纹识别** | 支持（pyannote ONNX） | 未知 | 无 | 无 | 支持 |

### 关键差异化发现

1. **Rewind 已经变道**：Rewind.ai 转型 Limitless，重心从桌面录制转向硬件挂坠。Screenpipe 实际继承了 Rewind 最初的"本地屏幕录制+AI 搜索"愿景，而且是开源的
2. **Recall 受限于生态**：仅 Windows 11 Copilot+ PC、无音频、无 API。Screenpipe 在跨平台和扩展性上完胜
3. **Otter/Granola 不是直接竞品**：它们解决的是"会议纪要"这一狭窄场景，Screenpipe 解决的是"数字活动全记录"
4. **Screenpipe 的真正差距**：产品成熟度和用户体验。GUI 收费 $400 且迭代未完成，不如竞品开箱即用

---

## 九、核心研判

### 1. Screenpipe 是 AI 时代的基础设施，不是应用
它的最大价值不在于自身 UI（目前收费 $400 的 GUI 反而可能是获客障碍），而在于**作为后台守护进程提供上下文 API**。随着 Cursor、Claude Code、OpenClaw 等 AI 工具通过 MCP 接入，Screenpipe 的网络效应会越来越强。

### 2. Pipes 生态是长期护城河
90+ 连接器 + 可编程 Pipe 运行时，已经形成了类似 Obsidian 插件市场的生态雏形。如果 Screenpipe 能成功激励第三方开发者编写 pipes，市场地位将难以被单纯的"录屏工具"撼动。

### 3. 本地优先是双刃剑
本地化保障了隐私和安全，但也限制了功能的上限（无法做跨用户的智能、难以训练全局模型）。Screenpipe 的云增值服务方向是正确的，但需要在"本地隐私"和"云端智能"之间找到更好的平衡点。

### 4. 商业化仍处早期
$400 终身 License 的定价策略暗示团队在平衡开源社区和收入需求。CLI 是 MIT 开源免费的，GUI 收费——这种"开源核心 + 付费壳"的模式（类似 Obsidian）已被验证可行，但 Screenpipe 的 GUI 成熟度仍有差距。

### 5. 最大的风险来自平台级竞争
Apple 如果将类似功能深度集成到 macOS（如 on-device screen indexing），Screenpipe 的生存空间将被挤压。但 Apple 在跨平台和开放 API 上的缺失给了 Screenpipe 窗口期。

---

## 十、关键文件路径速查

| 路径 | 说明 |
|------|------|
| `crates/screenpipe-engine/src/event_driven_capture.rs` | 事件驱动捕获引擎（核心调度器） |
| `crates/screenpipe-engine/src/core.rs` | 引擎入口（已迁移到事件驱动） |
| `crates/screenpipe-engine/src/hot_frame_cache.rs` | 热帧缓存（避免重复 OCR 新帧） |
| `crates/screenpipe-engine/src/high_fps_controller.rs` | 高帧率控制器（会议/游戏场景） |
| `crates/screenpipe-engine/src/focus_aware_controller.rs` | 焦点感知控制器（窗口切换协调） |
| `crates/screenpipe-screen/src/custom_ocr.rs` | 自定义 OCR 接口（可接入私有 OCR） |
| `crates/screenpipe-screen/src/tesseract.rs` | Tesseract OCR 引擎 |
| `crates/screenpipe-screen/src/apple.rs` | Apple Vision OCR（macOS） |
| `crates/screenpipe-screen/src/microsoft.rs` | Windows OCR 引擎 |
| `crates/screenpipe-screen/src/frame_comparison.rs` | 帧对比（判断内容是否变化） |
| `crates/screenpipe-audio/src/core/engine.rs` | 音频转录引擎枚举（11 种方案） |
| `crates/screenpipe-audio/src/core/stream.rs` | 音频流管理 |
| `crates/screenpipe-audio/src/vad/silero.rs` | Silero VAD 语音活动检测 |
| `crates/screenpipe-audio/src/speaker/embedding.rs` | 声纹嵌入（说话人识别） |
| `crates/screenpipe-audio/src/meeting_detector.rs` | 会议检测 |
| `crates/screenpipe-db/src/db/search.rs` | 搜索路由（FTS5 + 多模态过滤） |
| `crates/screenpipe-db/src/db/frames.rs` | 帧数据写入与查询 |
| `crates/screenpipe-db/src/db/audio.rs` | 音频转录数据存储 |
| `crates/screenpipe-redact/src/pipeline.rs` | PII 脱敏管线 |
| `crates/screenpipe-redact/src/adapters/regex.rs` | 正则脱敏适配器 |
| `crates/screenpipe-redact/src/adapters/rfdetr.rs` | RFDETR 模型脱敏适配器 |
| `crates/screenpipe-a11y/src/platform/` | 跨平台无障碍树实现 |
| `crates/screenpipe-a11y/src/events.rs` | A11Y 事件处理 |
| `crates/screenpipe-connect/src/connections/` | 90+ 外部连接器 |
| `crates/screenpipe-connect/src/oauth.rs` | OAuth 认证流程 |
| `crates/screenpipe-core/src/pipes/` | Pipes 插件系统 |
| `crates/screenpipe-core/src/sync/` | 数据同步模块（加密 S3 归档） |
| `crates/screenpipe-events/src/` | 全局事件管理器 |
| `crates/screenpipe-secrets/src/` | 密钥链集成 |
| `apps/screenpipe-app-tauri/` | Tauri 桌面应用（Next.js UI） |
| `CLAUDE.md` | AI 开发协作规范 |
| `DESIGN.md` | 设计系统规范（黑白极简） |
| `VISION.md` | 产品愿景与原则 |

---

*本报告基于公开源码、Issues、Release Notes 和社区讨论撰写，力求客观中立。部分分析涉及主观判断，仅供参考。*
