# cjpais/Handy 深度调研

> 一句话定位：完全离线、免费、可扩展的本地语音转文字桌面应用——按住快捷键说话，文字直接粘贴进任意输入框，音频不出本机。
> 
> **元数据**：⭐ 36,363 ｜ 语言 Rust+Tauri(Svelte/TS 前端) ｜ 许可 MIT ｜ 默认分支 main ｜ 末提交 2026-10-27 ｜ 调研日期 2026-11-02

## 一、项目亮点（差异化）

1. **真·离线隐私**：VAD（Silero）与识别（Whisper / Parakeet V3）全在本地跑，无任何云端上报；首次下载模型后「nothing leaves your machine」。
2. **多模型可切换**：Whisper Small/Medium/Turbo/Large（GPU 加速）+ 针对 CPU 优化的 Parakeet V3（自动语言检测），并自动发现 `models/` 下的自定义 GGML 模型。
3. **三态快捷键**：按住录音 / 点按切换 / 混合模式，配合 Raycast 扩展与 CLI 远程控制（`--toggle-transcription` 等）。
4. **跨平台粘贴抽象**：Windows 用 enigo，Linux 按显示服务器自动选 xdotool/wtype/dotool，Wayland 还支持 `pkill -USR2 -n handy` 信号触发，把快捷键所有权交给窗口管理器。

## 二、核心架构

Tauri（Rust 后端 + Svelte 前端）单体桌面应用，典型「薄前端 + 原生音频管线」结构：

```
src/                      # 前端：Svelte/TS，设置页/历史/模型选择/overlay
src-tauri/src/
├── audio_toolkit/        # 音频采集 + Silero VAD（audio/sink, audio/vad）
├── managers/
│   ├── transcription.rs  # 转录主流程协调
│   ├── transcription/    # policy.rs(解码策略) / live.rs / chunked.rs / job.rs
│   └── model/            # 模型下载/加载（Whisper·Parakeet）
├── engine_supervisor/    # 推理引擎生命周期
├── paste_tx/             # 跨平台粘贴（enigo / xdotool / wtype）
├── shortcut/             # 全局快捷键（含 Wayland 信号兜底）
└── language_detection/
```

数据通路：**快捷键触发捕获 → Silero VAD 切静音段 → Whisper/Parakeet 解码 → 文本 → 按目标 App 粘贴**（Linux 用剪贴板回贴并延时恢复）。

## 三、应用场景与启发

- **可复用范式**：「Tauri 壳 + 本地 Whisper/Parakeet + 平台原生粘贴」是构建隐私优先桌面 AI 工具的成熟模板，比 Electron+云端 API 更轻、合规友好。
- **工程启发**：Handy 把「平台差异」收敛到 `paste_tx` 与 `shortcut` 两个适配层，并显式处理 Wayland 的权限边界（不抢全局键、让 WM 持有键绑）——这是跨平台桌面工具最易踩坑处，值得同类项目照搬。
- **对用户的价值**：若要做「本地优先的 AI 输入法/速记/会议转写」，Handy 的 VAD+模型热切换+粘贴抽象可直接作为参考实现。

## 四、源码深度解读

**① 解码策略决策（`src-tauri/src/managers/transcription/policy.rs`）**——按模型能力与设置选择「流式/分块/整段」解码：

```rust
pub struct ModelTraits { pub streaming: bool, pub long_form: bool }
pub fn live_decode(model: ModelTraits, long_form_chunking: bool) -> LiveDecode {
    if model.streaming      { LiveDecode::Stream }       // 流模型自己处理长音频
    else if long_form_chunking && !model.long_form { LiveDecode::Chunked }
    else { LiveDecode::None }
}
```

**② 暂停段裁剪（`src-tauri/src/transcription/engine/streaming.rs`）**——解决 Parakeet 缓冲流在长停顿后「吞掉首词」的问题：

```rust
pub(super) const PAUSE_HEAD_SAMPLES: usize = 40_000;  // 停顿前保留约 2.08s
pub(super) const PAUSE_TAIL_SAMPLES: usize = 4_800;   // 恢复前保留尾部
// PauseCap：仅让流听到每个停顿的 head+tail，超出的静音丢弃
if self.pause <= PAUSE_HEAD_SAMPLES { out.append(&mut self.frame); return; }
self.tail.extend(self.frame.drain(..));
let overflow = self.tail.len().saturating_sub(PAUSE_TAIL_SAMPLES);
self.tail.drain(..overflow); self.dropped += overflow;
```

这一处「为保首词而精确控尾静音」的细节，是离线听写质量差异的关键，也体现项目对真实失败模式（issue #324/#338/#458/#657）的响应密度。

## 五、全网口碑

- GitHub 36k⭐、Discord 社区活跃；README 透明度高（明文列出 macOS 蓝牙麦克风、fn 键、Wayland 限制、剪贴板回贴竞态等 Known Issues）。
- 定位对标 MacWhisper / Wispr Flow，但「全平台 + 完全离线 + 开源」组合在同类中稀缺，社区评价偏正面，主要吐槽集中在 Linux/Wayland 边缘情况（与项目自己承认的一致）。

## 六、竞品对比 + 核心研判

| 维度 | Handy | MacWhisper | Wispr Flow | Willow |
|---|---|---|---|---|
| 离线 | ✅ 完全 | ✅(Mac) | ❌ 云端 | ✅ |
| 跨平台 | ✅ Win/Mac/Linux | ❌ 仅 Mac | ✅ 但云 | 嵌入式 |
| 开源 | ✅ MIT | ❌ 商业 | ❌ 商业 | ✅ |
| 可扩展 | ✅ 自定义模型 | 中 | 低 | 硬件 |

**核心研判**：Handy 占据了「免费 + 全平台 + 真离线 + 开源」这一稀缺交集，是隐私敏感用户与开发者自托管的优选。主要风险是 Whisper 大模型在低端 CPU 上的实时性，以及 Linux/Wayland 拼贴生态的碎片化——但 Parakeet V3 的 CPU 路径与项目对平台差异的系统性收敛已在很大程度上缓解。值得持续关注其模型热切换与 Raycast/CLI 生态扩展。

## 七、关键文件路径速查

- 转录策略：`src-tauri/src/managers/transcription/policy.rs`
- 流/分块解码：`src-tauri/src/transcription_coordinator.rs`、`src-tauri/src/managers/transcription/live.rs`、`chunked.rs`
- 平台粘贴：`src-tauri/src/paste_tx/`
- 全局快捷键：`src-tauri/src/shortcut/`（含 Wayland 信号兜底）
- 模型管理：`src-tauri/src/managers/model/`
- 官方站：https://handy.computer ｜ CLI 版：cjpais/handy-cli
