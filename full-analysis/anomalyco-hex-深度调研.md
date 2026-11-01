# anomalyco/hex 深度调研

> 调研日期：2026-11-02 | 来源：GitHub Trending（净新增高价值项目）
> 仓库：`https://github.com/anomalyco/hex`
> 语言：Rust（Tauri 桌面外壳）+ TypeScript（SDK/站点）

---

## 一、项目定位（一句话）

**Hex 是一款完全在本地运行的跨平台语音听写工具**——按住快捷键说话，松手即把转写文本粘贴进当前光标所在的应用；首次运行下载语音模型后，数据不再离开本机。

---

## 二、项目亮点（差异化）

1. **纯本地、零云回传**：首次运行拉取一次模型后，所有录音与转写都在设备内完成，官方 README 明确"after that nothing leaves your machine"——对隐私/离线场景是硬卖点。
2. **按住即说、松手即贴的交互模型**：用"按住快捷键录音、松开自动粘贴"替代传统的录音-停止-复制三步走，把语音听写无缝嵌入任意编辑器/聊天框。
3. **跨三端一体分发**：同一套代码覆盖 macOS（Apple silicon/Intel）、Windows（x64/ARM64）、Linux（x86_64/ARM64，含 .deb/.rpm），并提供 Homebrew、AUR、Nix、安装脚本等多通道安装。
4. **工程化的"长停顿不丢词"算法**：`streaming.rs` 中的 `PauseCap` 通过对停顿音频的头/尾截断（head 40 000 样本、tail 4 800 样本），解决了 Parakeet 类流式模型在 >5.6 s 静音后丢失首词的问题（issue #324/#338），并保留整段录音作为离线兜底。
5. **实验功能下沉到 "Labs"**：把不稳定的新能力隔离在侧边栏底部的 Labs 区，与主路径解耦，便于快速试错而不污染稳定体验。

---

## 三、核心架构

Hex 是 **Rust + Tauri** 的桌面应用，整体可拆为四层：

```
┌─────────────────────────────────────────────┐
│  表现层：Tauri 窗口 + rune_ui（HUD/实时笔记）   │
│  src/rune_ui, src/desktop, ios/, macos/       │
├─────────────────────────────────────────────┤
│  业务层：dictation / transcription / capture  │
│  src/dictation, src/transcription/engine       │
│  src/capture_host, crates/capture-core         │
├─────────────────────────────────────────────┤
│  音频层：麦克风采集 + 停顿切分 + 流式喂帧       │
│  src/audio/hex_microphone, pause_segmenter     │
│  streaming.rs (PauseCap)                       │
├─────────────────────────────────────────────┤
│  推理层：transcribe_cpp（whisper.cpp 绑定）     │
│  模型首次下载后常驻本地                          │
└─────────────────────────────────────────────┘
```

- **crates/ 工作区**：`capture-core`（屏幕/光标捕获）、`capture`（导出，按 linux/win 分平台）、`router`（路由与 fixture）。
- **src/ 主模块**：`audio`（麦克风与录音环境）、`transcription/engine`（转写引擎封装）、`dictation`（听写编排）、`rune_ui`（HUD、capture_capsule、live_notes、onboarding_kit）、`local_api`（本地 HTTP API）、`updater`（自更新）。
- **SDK**：`sdk/typescript` 提供 TS 绑定，`sdk/service-darwin-arm64` 为原生服务；`site/` 是官网与文档站。
- **多端外壳**：`ios/`（HEXActivity / HEXKeyboard / HEXMobile / HEXWidgets）、`macos/HexMicrophoneDriver`、`src/windows`、`src/linux` 分别承载平台特有能力。

关键设计取舍：**把"是否安静"的判断交给 `pause_segmenter::SpeechFrames` 的噪声地板（noise floor）测度**，只有低于噪声地板的帧才算停顿——避免了"略高于稳态噪声的轻声被误判为静音而截断"（issue #458）。

---

## 四、应用场景与启发

- **隐私敏感写作/客服场景**：医疗、法务、金融等不允许语音出域的行业，可用 Hex 把口述直接落进本地文档，规避云端 ASR 合规风险。
- **给同类本地语音产品的工程启发**：
  - **流式长停顿丢词是通病**，Hex 用"保留停顿头 40 000 样本 + 尾 4 800 样本"的轻量裁剪，比整段重跑更省算力；其 `PauseCap` 结构可直接迁移到任何基于 whisper.cpp/Parakeet 的流式听写。
  - **整段录音作为离线兜底（the clip is authoritative）**：流式结果不可信时回退到全量离线转写，保证"绝不丢内容"——这是可靠听写产品的关键容错范式。
  - **macOS 尾部静音补零（issue #657）**：用 `stream_trailing_silence` 平台特化常量补齐整段推理的尾静音，保住句末标点，是跨平台 ASR 集成里容易忽略的细节。
- **"Labs 隔离实验区"模式**：把高风险功能收敛到独立入口，对桌面应用快速迭代很有参考价值。

---

## 五、源码深度解读（核心模块）

### 5.1 `streaming.rs` — `PauseCap`：流式停顿裁剪器

这是 Hex 流式转写最精妙的部分。核心常量与结构体如下（节选自 `streaming.rs`）：

```rust
/// Pause audio a dictation stream still hears before its long pauses are
/// cut: longer than a chunk plus its lookahead (2.08 s for Unified English),
/// so the words before a pause decode during it.
pub(super) const PAUSE_HEAD_SAMPLES: usize = 40_000;
/// Pause audio kept just before speech resumes after a cut.
pub(super) const PAUSE_TAIL_SAMPLES: usize = 4_800;

/// A dictation stream that hears at most the head and tail of each pause.
/// Parakeet's buffered stream can drop the first word after a pause longer
/// than its 5.6 s left context (#324, #338); the clip, and with it any
/// offline fallback, keeps every sample.
pub(super) struct PauseCap<'a, S> {
    stream: &'a mut S,
    speech: crate::transcription::pause_segmenter::SpeechFrames,
    frame: Vec<f32>,            // 未满 20ms 的残余样本
    pause: usize,               // 噪声地板以上静音累计样本数
    tail: VecDeque<f32>,        // 超过 head 后的停顿样本，语音恢复即释放
    pub(super) dropped: usize,
    heard: bool,
    trailing_silence: usize,
}
```

`frame()` 是裁剪核心：每凑满一帧（20 ms），先用 `speech.is_quiet` 判断是否静音——

```rust
fn frame(&mut self, out: &mut Vec<f32>) {
    if !self.speech.is_quiet(&self.frame) {   // 不是静音 → 说话了
        self.heard = true;
        out.extend(self.tail.drain(..));       // 把之前裁掉的尾补回来
        self.pause = 0;
        out.append(&mut self.frame);
        return;
    }
    self.pause += self.frame.len();
    if self.pause <= PAUSE_HEAD_SAMPLES {      // 停顿未超 head → 全部保留
        out.append(&mut self.frame);
        return;
    }
    self.tail.extend(self.frame.drain(..));    // 超 head → 只留 tail 窗口
    let overflow = self.tail.len().saturating_sub(PAUSE_TAIL_SAMPLES);
    self.tail.drain(..overflow);
    self.dropped += overflow;
}
```

逻辑链条：**短停顿（≤40 000 样本≈2.6 s @16kHz）整段保留，保证解码器在停顿内完成前面词语；长停顿只留最近 4 800 样本的"尾"，既切断过长静音、又保住恢复说话时的首词上下文。** `dropped` 字段用于可观测——可据此监控真实丢弃量。

### 5.2 `streaming.rs` — `StreamFeed` trait 与 macOS 特化

```rust
pub(super) trait StreamFeed {
    fn feed(&mut self, samples: &[f32]) -> Result<(), String>;
    fn finalize(&mut self) -> Result<String, String>;
    fn partial(&self) -> Partial;   // stable + tentative 两段文本
}

#[cfg(target_os = "macos")]
pub(super) fn stream_trailing_silence(model: &Model) -> usize {
    model.stream_trailing_silence()   // macOS 整段推理需补尾静音保句末标点
}
#[cfg(not(target_os = "macos"))]
pub(super) fn stream_trailing_silence(_model: &Model) -> usize { 0 }
```

`partial()` 把文本拆成 `stable`（已提交）与 `tentative`（暂定）两段——这正是听写 HUD 实时显示"前半句已锁定、后半句还在猜"的产品体验的代码基座。

### 5.3 推理后端：transcribe_cpp

`transcribe_cpp::Stream` 是 whisper.cpp 的 Rust 绑定（从 `Stream::feed / finalize / text()` 调用形态可判定）。`PauseCap<S: StreamFeed>` 以泛型持有该流，使裁剪逻辑与具体后端解耦——**日后换模型只需满足 `StreamFeed` 契约**。README 所述"first run downloads a speech model"对应 `src/transcription/engine` 的模型拉取与缓存逻辑（具体实现未在抓取范围内，标"数据不可用"）。

---

## 六、全网口碑

- **定位与背书**：由 anomalyco 维护，与同作者的商业化产品矩阵（含官网 anoma.ly 分发）绑定，属于"开源可读、产品化运营"的项目。
- **社区协作模式特殊**：README 明确 **"We don't take pull requests"**——用户通过 issue 描述问题，官方 agents 快速响应。这对想贡献代码的开发者是门槛，但对"只想要稳定产品"的终端用户反而降低了被社区 PR 拖慢的风险。
- **工程透明度高**：仓库不仅含源码，还带 `docs/research`、`docs/specs`、`tests/golden`、`tests/fixtures`（含 meetings / vocabulary 音频夹具），说明其测试与文档体系较完整。
- **数据不可用**：Star 数、Issue 关闭率、版本发布节奏等量化口碑指标本次未抓取，建议后续以 `gh api repos/anomalyco/hex` 补取。

---

## 七、竞品对比 + 核心研判

| 维度 | Hex (anomalyco) | Handy (cjpais) | Willow / WhisperDictation |
|------|----------------|----------------|---------------------------|
| 运行方式 | 纯本地 Tauri 桌面 | 纯本地（同源流式架构） | 本地模型 + 各平台原生壳 |
| 交互 | 按住快捷键说话、松手粘贴 | 类似按住即说 | 多为全局快捷键触发 |
| 长停顿处理 | PauseCap 头/尾裁剪 + 整段兜底 | 同源 `streaming.rs` 常量 | 多数无专门处理 |
| 跨平台 | macOS/Win/Linux 全覆盖 | 同覆盖 | 通常偏单平台 |
| 开源协作 | 只读 issue，不收 PR | 正常开源 | 视项目而定 |

**核心研判**：
1. **Hex 与 Handy 存在明显同源性**——两者 `streaming.rs` 的 `PAUSE_HEAD_SAMPLES=40_000 / PAUSE_TAIL_SAMPLES=4_800` 常量、`PauseCap` 结构与 `transcribe_cpp` 后端高度一致，属于同一流式听写技术谱系（Handy 偏开源参考实现，Hex 偏产品化分发）。调研时应视为"一套内核、两种包装"，避免重复计为两个独立技术路线。
2. **技术护城河在"停顿裁剪 + 整段兜底"的工程细节**，而非模型本身（模型来自 whisper.cpp/Parakeet 生态）。这类细节（#324/#338/#458/#657 等 issue 驱动）正是本地 ASR 产品"好用"与"能用"的分水岭。
3. **"不收 PR"的协作策略**使其更像一个商业化产品的代码窗口，而非社区驱动项目；长期演进节奏取决于 anomalyco 自身路线图，外部无法fork 反哺主干。
4. **入库存放建议**：作为"本地语音听写 / 隐私 ASR"领域的代表 repo，与 Handy 互为参照。重点保留其 PauseCap 裁剪范式与跨平台分发矩阵，作为同类需求（本地、离线、低延迟听写）的解决思路索引。

---

## 八、关键文件路径速查

| 作用 | 路径 |
|------|------|
| 流式停顿裁剪核心 | `src/transcription/engine/streaming.rs`（`PauseCap` / `PAUSE_HEAD_SAMPLES` / `PAUSE_TAIL_SAMPLES`） |
| 停顿判定（噪声地板） | `src/transcription/pause_segmenter.rs`（`SpeechFrames::is_quiet` / `FRAME_SAMPLES`） |
| 听写编排 | `src/dictation/` |
| 转写引擎封装 | `src/transcription/engine/` |
| 麦克风采集 | `src/audio/hex_microphone/`、`src/audio/recording_environment/` |
| 屏幕/光标捕获 | `crates/capture-core/src/`、`crates/capture/src/` |
| HUD / 实时笔记 UI | `src/rune_ui/`（含 `live_notes`、`capture_capsule`、`onboarding_kit`） |
| 本地 API | `src/local_api/` |
| TypeScript SDK | `sdk/typescript/src/` |
| 平台外壳 | `ios/`、`macos/HexMicrophoneDriver`、`src/windows/`、`src/linux/` |
| 文档与研究 | `docs/research/`、`docs/specs/`、`docs/features/` |
| 测试夹具 | `tests/fixtures/`（meetings / vocabulary / release-protocol）、`tests/golden/` |

---

*免责声明：本报告基于仓库 README、目录树与 `streaming.rs` 源码片段撰写；模型拉取/缓存、UI 渲染等未抓取模块标"数据不可用"，Star/Issue 等量化指标待补。*
