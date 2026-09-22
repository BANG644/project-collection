# linyqh/NarratoAI 深度调研

> 调研日期：2026-09-23 ｜ 定位：一站式 AI 影视解说 + 自动化剪辑工具（文案撰写→自动剪辑→配音→字幕→导出剪映草稿）｜ Stars：11,174 ｜ 语言：Python ｜ 许可：MIT（LICENSE 文件）｜ 默认分支：main ｜ 最近活跃：2026-09-17（v0.8.6）

## 一、项目定位（一句话）

NarratoAI 是一款面向**影视解说 / 纪录片 / 短剧混剪**的一站式自动化工具：用 LLM 写解说文案、用视觉模型理解视频、用 ffmpeg 自动剪辑、接多种 TTS 配音并生成字幕，最终导出可继续编辑的剪映草稿，主打本地开源部署 + 云端托管版。

## 二、项目亮点（差异化）

- **三类业务流水线齐备**：`film_tv_narration`（影视解说）、`documentary`（纪录片逐帧分析）、`SDP/SDE`（短剧混剪），覆盖从长视频理解到短剧批量生产的常见场景。
- **多模态理解后端可插拔**：视觉理解默认 LLM，可选 `Qwen2-VL`、TwelveLabs Pegasus（原生理解整段画面挑高光）、Fun-ASR 转录；大模型供应商抽象为 OpenAI 兼容 + 硅基流动 + 火山 + TwelveLabs。
- **TTS 矩阵丰富**：IndexTTS-1.5/2（含 Apple Silicon 的 MLX 本地克隆）、豆包语音、OmniVoice、腾讯云 TTS、Fun-ASR 字幕，配音与音色克隆一条龙。
- **产出可继续编辑**：`jianying_draft_builder.py` 直接导出剪映草稿（`.draft` 工程），而非只给成品视频，贴合国内创作者的二次精修习惯。
- **低门槛分发**：整合包（Windows x64 / macOS arm64）、Docker（`docker compose up -d`）、本地 `uv` 三套启动方式，WebUI 跑在 `127.0.0.1:8501`。

## 三、核心架构

```
输入（视频/素材）──▶ 抽帧 + 视觉理解（UnifiedLLMService · 多后端）
        │
        ▼
文案生成（SDP 短剧 / film_tv_narration / documentary 提示词链）
        │
        ▼
配音（TTS Manager：IndexTTS/豆包/OmniVoice…）──▶ 字幕（SRT/校正/翻译）
        │
        ▼
剪辑（ffmpeg：clip_video / merger_video / audio_*）──▶ 导出剪映草稿 / 成片
        │
        ▼
Streamlit WebUI（webui.py · webui/ 组件 · i18n 中英文）
```

- **抽象层 `app/services/llm/`**：`UnifiedLLMService` 统一文本/视觉调用，`manager.py` 注册 provider，`providers/openai_compatible_provider.py` 统一 OpenAI 兼容链路（README 提到 2026-03 已移除 LiteLLM 依赖以收敛安全面）。
- **业务层 `app/services/`**：`SDP/`（短剧）、`documentary/frame_analysis_service.py`（纪录片逐帧）、`generate_narration_script.py`、`jianying_draft_builder.py`、`subtitle_*.py`、`video_*.py` 等各司其职。
- **提示词工厂 `app/services/prompts/`**：按 `film_tv_narration / short_drama_editing / short_drama_narration / documentary` 分组，含 `plot_analysis / script_generation / segment_planning / script_repair` 等可复用链。

## 四、应用场景与启发

- **自媒体批量生产**：当你要日更影视解说/短剧混剪，NarratoAI 提供"抽帧理解 → 文案 → 配音 → 剪映草稿"的端到端骨架，可直接复用其 `SDP` 流水线思路做自己的剪辑 agent。
- **"LLM 供应商抽象 + 输出校验"范式**：它的 `UnifiedLLMService` + `OutputValidator` + `PromptManager` 三层设计（见下）是做"多模型可切换、输出格式可验证"的干净模板，对搭任何 LLM 应用都有借鉴。
- **本地优先 + 可插拔后端**：默认本地、可选云端 TTS/理解，契合"数据不出本机 + 按需上云"的务实路线。

## 五、源码深度解读（关键片段）

`app/services/llm/unified_service.py` 中的 `UnifiedLLMService` 是全局 LLM 抽象，关键在"按能力取 provider + 统一校验"：

```python
text_provider = LLMServiceManager.get_text_provider(provider)
result = await text_provider.generate_text(prompt=prompt, system_prompt=system_prompt, ...)
# 解说文案生成后强制格式校验
if validate_output:
    narration_items = OutputValidator.validate_narration_script(result)
```

视觉理解与文案生成解耦：`analyze_images()` 走 `get_vision_provider()`，文案链走 `PromptManager.get_prompt(category="short_drama_narration", name="plot_analysis", parameters={...})` 注入系统提示词。这种"能力注册 + 提示词工厂 + 输出校验"三段式，让换模型/加后端只改 `manager` 与 `providers`，业务代码零改动。

剪辑侧 `app/services/jianying_draft_builder.py`（5.6 万行级）负责把时间轴、素材、字幕拼成剪映可导入草稿，是"成片 → 可编辑工程"的出口；`app/services/SDP/` 则是短剧混剪的核心编排。

## 六、全网口碑

- **正面**：星标 11k+，国内影视解说/短剧自动化赛道头部开源项目；迭代极勤（2026 几乎月更、v0.8.6 仍在加 MLX 本地 TTS）；文档/社群/整合包完善，被多个 AI 剪辑教程引用。
- **风险/争议**：README 显著警示"有人改名贩卖，请警惕"，社区存在盗版/二改带货问题；重度依赖外部 TTS/视觉 API（部分按量付费），完整链路成本不低；基于 MoneyPrinterTurbo 重构而来，部分实现偏脚本化（参考图/脚本散落在 `resource/`）；许可声明为 MIT 但需以仓库/作者方式注明出处。

## 七、竞品对比与核心研判

| 维度 | NarratoAI | MoneyPrinterTurbo | 通用视频 agent |
|------|-----------|-------------------|----------------|
| 定位 | 影视解说/纪录片/短剧混剪 | 短视频一键生成 | 任意视频任务 |
| 理解后端 | Qwen2-VL/TwelveLabs 可选 | 较弱 | 取决于 agent |
| 产出 | 剪映草稿（可二次编辑） | 成片 | 成片 |
| 本地化 | 强（整合包/Docker） | 中 | 弱 |

**竞品**：`harry0703/MoneyPrinterTurbo`（前身）、`FujiwaraChoki/MoneyPrinter`、各类 browser-use/video-use 剪辑 agent。**NarratoAI 的差异**在于"中文影视解说/短剧"垂直深耕 + 剪映草稿导出 + 多 TTS 矩阵。

**核心研判**：⭐⭐⭐⭐ — 想做"中文短视频自动化生产"或研究"多模态理解→文案→剪辑"流水线的团队，这是性价比最高的开源样本，其 **LLM 抽象 + 提示词工厂 + 剪映草稿导出** 三段式值得抄；但代码偏脚本化、外部 API 成本与盗版风险需在使用前评估。关注其对 TwelveLabs/本地 MLX 的进一步整合。

## 八、关键文件路径速查

- `app/services/llm/unified_service.py` — 统一 LLM 抽象（文本/视觉/校验）
- `app/services/llm/manager.py` / `providers/openai_compatible_provider.py` — provider 注册与 OpenAI 兼容链路
- `app/services/SDP/`（短剧）· `app/services/documentary/frame_analysis_service.py`（纪录片）— 业务编排
- `app/services/jianying_draft_builder.py` — 导出剪映草稿
- `app/services/prompts/` — 分场景提示词工厂
- `webui.py` · `webui/` — Streamlit 界面与组件
- `config.example.toml` · `docker-compose.yml` — 配置与部署
- 前身参考：[MoneyPrinterTurbo](https://github.com/harry0703/MoneyPrinterTurbo) ｜ 文档：[官方 Wiki](https://github.com/linyqh/NarratoAI/wiki)
