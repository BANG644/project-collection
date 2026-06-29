# 🔬 browser-use/video-use — 全方位深度调研

## 📌 一句话定位

> **对话式 AI 视频编辑工作流**——不打开剪辑软件，不拖动时间轴，用自然语言告诉 Claude Code 等 AI Agent "把这几段素材剪成一条 Launch Video"，Agent 自动完成转录、粗剪、调色、字幕、动效叠加和自校验，最终产出 `final.mp4`。

由 browser-use（93k⭐ 浏览器自动化明星团队）推出，开源 1 天即获 5k+ Star。

## ⭐ 项目亮点

1. **「LLM 不看视频」的极致 token 优化**——不丢帧、不截图，只喂 12KB 的文本转录 + 按需视觉复合快照。一万帧素材的 token 成本从 45M 降到 12KB，相差 **3700 倍**。这是整个项目的"灵魂级设计决策"。
2. **Agent-first 视频生产线**——不是"AI 辅助人类操作剪辑软件"，而是 Agent 自主协调转录→推理→EDL 生成→渲染→自校验的完整流水线。Agent 是"剪辑师"，不是"帮手"。
3. **12 条硬性规则 + 弹性创作**——硬规则保障生产正确性（字幕顺序、音频 fade、帧对齐等不可协商），其余全交给 Agent 艺术判断。一次性解决了"AI 剪辑总出低级错误"这个行业难题。
4. **11 个分析维度参考文件夹**——`skills/manim-video/references/` 内置 16 份从场景规划、动画设计到故障排除的完整参考，相当于给 Agent 配了一本《视频制作百科》。

## 🏗️ 项目架构全景

### 目录结构

```
video-use/
├── SKILL.md                   # 核心技能定义（Agent 的"剪辑师手冊"）
├── install.md                 # 首次安装脚本（克隆→依赖→ffmpeg→skill 注册）
├── pyproject.toml             # Python 依赖（requests, librosa, matplotlib, pillow, numpy）
├── helpers/
│   ├── transcribe.py          # ElevenLabs Scribe 音频转录
│   ├── transcribe_batch.py    # 批量多文件转录
│   ├── render.py              # EDL → 渲染管线（调色/fade/字幕/叠加）
│   ├── grade.py               # 自动颜色分级预设
│   ├── pack_transcripts.py    # 多转录 → 压缩为 takes_packed.md
│   ├── timeline_view.py       # 波形+胶片条+标签 PNG 可视化
├── skills/manim-video/        # Manim 动画子技能
│   ├── SKILL.md               # Manim 动画技能定义
│   └── references/            # 16 份参考文档（动画、场景规划、3D 等）
└── static/
    ├── video-use-banner.png
    └── timeline-view.svg
```

### 设计哲学

**核心架构决策：「LLM 不应该"看"视频，而应该"读"视频」**

传统 AI 视频处理方案的做法是：逐帧截图 → 送入多模态模型 → 消耗天量 token。video-use 反其道而行：

```
                   原始视频素材
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
    ElevenLabs     audio 提取    yt-dlp 下载
    Scribe 转录    (ffmpeg)     (可选)
          │
          ▼
    takes_packed.md          ← LLM 的"主阅读视图"
    (≈12KB, 按说话片段+时间戳打包)
          │
          ▼
    LLM 推理 → EDL(剪辑决策表) → 渲染 → 自校验
          │                              │
          ▼                              ▼
    timeline_view.png              preview.mp4 → final.mp4
    (按需视觉复核)
```

这个设计的优雅之处在于：**把视频问题转化为文本问题**。Scribe 的 diarize（说话人分离）+ audio_events（笑声/掌声等事件标记）两层能力让 Agent 获得相当于"看过视频+听过音频"的双通道理解，而成本只是 12KB 的文本。

### 依赖轻量

```toml
# pyproject.toml（核心依赖仅 5 个）
dependencies = [
    "requests",      # ElevenLabs API 调用
    "librosa",       # 音频分析
    "matplotlib",    # timeline_view 可视化
    "pillow",        # 图像处理
    "numpy",         # 数值计算
]
```

极简依赖设计——video-use 不是沉重的剪辑平台，而是"一套助手脚本 + 一份 Agent 技能说明书"。真正的剪辑能力由 ffmpeg（4000+ 功能）和 Scribe（行业最佳 ASR）提供，video-use 只做编排层。这使它能在任何有 shell 访问的 Agent 上运行：Claude Code、Codex、Hermes、OpenClaw。

## 💡 应用场景与启发

### 典型使用场景

| 场景 | 适用性 | 说明 |
|------|--------|------|
| **口播/教程类视频** | ⭐⭐⭐⭐⭐ | 自动剪掉 umm/呃/重复开头，加字幕+调色 |
| **产品 Launch 视频** | ⭐⭐⭐⭐⭐ | 多条素材拼接，Agent 按文案规划结构 |
| **社交媒体短内容** | ⭐⭐⭐⭐⭐ | TikTok/Reels 竖版，包含动效叠加 |
| **多机位采访** | ⭐⭐⭐⭐⭐ | Scribe diarize 支持多说话人分离 |
| **长片/叙事型** | ⭐⭐⭐ | 依赖音轨切割逻辑，复杂叙事需要人工干预 |
| **运动/动态内容** | ⭐⭐ | 缺少视觉内容理解能力，运动节奏难以把握 |

### 可借鉴的解决方案模式

**1. "结构化文本 + 按需视觉"的双层信息架构**

这是 video-use 最值得借鉴的模式——不仅适用于视频，也适用于任何"视觉密集型但 AI token 成本极高"的场景：

- **UI 自动化**：browser-use 本身就是这个模式（DOM 结构树 + 截图），video-use 是其理念的延伸
- **PDF/文档理解**：先提取文本结构 + 关键位置截图，而不是整页 OCR
- **设计评审**：先读设计系统 token/spec，只在决策点去看渲染图

**2. Agent 编排的"提问→确认→执行→自检"闭环**

SKILL.md 中定义的 12 条硬规则中关键一条是「策略确认后才执行」。这不是效率妥协而是保险设计——在 Agent 自主性越来越强的当下，**确认环节是防止 Agent 做灾难性操作的最后一关**。

**3. EDL（Edit Decision List）作为 Agent 与渲染引擎的中介**

EDL 不是新概念（源自电影行业），但 video-use 把它用在 Agent 上下文中。Agent 输出 JSON EDL → render.py 消费 → ffmpeg 执行。这个解耦让：
- Agent 可以"大胆想象"剪辑方案（EDL 修改成本极低）
- 渲染引擎可以独立优化（用 ffmpeg 而不是重新走 Agent 流程）
- 用户可以审查 EDL 再做确认（而不是让 Agent 直接动刀）

### 同类需求的可参考思路

如果你在构建类似的"AI Agent 驱动的工作流"系统：
- **Agent 技能说明书（SKILL.md）比代码更重要**——video-use 的 `SKILL.md` 约 700 行，`helpers/` 下 Python 脚本总计约 800 行。大部分逻辑和约束写在自然语言指令中，而不是代码中。这意味着维护 Agent 的行为准则约等于维护一份文档，而不是修改代码。
- **外部能力 > 自研能力**——video-use 没有自研转码引擎或 ASR 模型，而是站在 ffmpeg + ElevenLabs Scribe 的肩膀上。选择"编排"而非"替代"，让团队能用零 AI 视频背景写出一个 10k star 项目。
- **Agent 记忆（project.md）**——每 session 的输出和决策都持久化到 `edit/project.md`，下次对话自动加载。这点虽小，但对长期项目至关重要（否则 Agent 每次都是一次性工人）。

## 🧠 核心源码解读

### 1. 转录管线 `helpers/transcribe.py`（~150 行）

```python
# transcribe.py — 从视频到结构化文本的核心入口
def call_scribe(audio_path, api_key, language=None, num_speakers=None):
    data = {
        "model_id": "scribe_v1",
        "diarize": "true",          # 说话人分离
        "tag_audio_events": "true", # 音频事件（掌声、笑声等）
        "timestamps_granularity": "word",  # 单词级时间戳
    }
    resp = requests.post(SCRIBE_URL,
        headers={"xi-api-key": api_key},
        files={"file": (audio_path.name, f, "audio/wav")},
        data=data, timeout=1800)
    return resp.json()
```

关键决策：Scribe 调用配置了 `diarize=true` + `tag_audio_events=true` + `timestamps_granularity=word`。triple 配置是整个项目的基石——只靠文本转录，无法区分说话人（多机位采访场景必备）且无法标记笑场/鼓掌等上下文事件。

### 2. 渲染管线 `helpers/render.py`（~250 行）

```python
# render.py — 渲染 EDL 的核心
# 管线顺序（不可协商）：
# 1. per-segment extract（带调色 + 30ms 音频 fade）
# 2. lossless -c copy concat → base.mp4
# 3. 叠加层（动效 + PTS 偏移 + 字幕filter LAST）→ final.mp4

SUB_FORCE_STYLE = (
    "FontName=Helvetica,FontSize=18,Bold=1,"
    "PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BackColour=&H00000000,"
    "BorderStyle=1,Outline=2,Shadow=0,"
    "Alignment=2,MarginV=90"  # MarginV=90 精确避免被社交平台UI遮挡
)
```

这段注释最有价值的部分不是代码，而是 `MarginV=90` 这个"非审美参数"——它解释了一个隐蔽的工程问题：TikTok/IG Reels 底部约 25-30% 区域会被平台 UI 遮挡。如果你在做任何视频处理的 AI 工具，这个 MarginV 值是一个"跳过就出 bug"的关键参数。

### 3. 自校验闭环 `render.py` 的调用约定

SKILL.md 定义了自校验循环：
```
Render → timeline_view on rendered output → 检查 cut boundary → 发现问题 → fix → re-render (max 3)
```

这比"AI 生成一个版本就交给用户"要负责任得多。Agent 用 `timeline_view.py` 在渲染输出的每个剪切边界处自动截图检查：视觉跳跃、音频爆音、字幕遮挡。这个"AI 自检"环节是在线剪辑工具没有的差异化能力。

## 📐 架构决策与设计哲学

### 关键决策

| 决策 | 选型 | 替代方案 | 理由 |
|------|------|---------|------|
| 转录方式 | ElevenLabs Scribe | Whisper/Deepgram | Scribe 的 diarize+audio_events 双能力目前最佳 |
| 渲染管道 | ffmpeg 分步处理 | MoviePy/OpenCV | ffmpeg 的硬件加速 + 滤镜链是最可靠的生产级方案 |
| 动效引擎 | 多引擎并行（HyperFrames/Remotion/Manim） | 单一引擎 | 每个引擎各有专长，Agent 按需选择，互不阻塞 |
| Skill 形态 | SKILL.md（自然语言指令） | Python API | Agent 理解自然语言比理解代码更好，维护成本最低 |

### 设计红线（Out-of-Scope）

- 不自研转码引擎，不替代 ffmpeg
- 不"看"视频帧，只"读"文本转录
- 不自动执行，每次需要用户确认策略
- 不写视频素材目录（输出严格在 `<videos_dir>/edit/`）

从 browser-use 到 video-use 可以看到 browser-use 团队的**方法论迁移**：结构化文本（DOM 树 / 转录）→ Agent 推理 → 执行。这不是一个偶然的"做视频工具"，而是他们验证过的 Agent 编排范式的复制。

## 🌐 全网口碑画像

### 好评共识

- **"剪辑效率极高"**：对于口播类视频，"剪掉口误、加字幕、调色全程 5 分钟"（掘金用户）
- **"零学习成本"**：不需要学 Final Cut Pro 或 Premiere，"就像和朋友描述你想要什么"（知乎）
- **"设计思路聪明"**：不丢帧读取视频的方式是"天才般的 token 节省方案"（tech blog）
- **"延续 browser-use 方法论"**：结构化文本+按需视觉的模式在视频领域再次证明可行（txtmix）

### 差评共识 & 踩坑高发区

- **依赖 ElevenLabs API Key**：Scribe 转录非免费，API Key 需要自行申请且有额度限制
- **macOS brew 优先**：`brew install ffmpeg` 预设了 macOS 环境，Linux/Windows 用户需要手动适配安装方式
- **无 Docker 镜像**：首次环境配置涉及 git clone + brew/pip 多步，非零配置开箱
- **长视频处理不稳定**：30 分钟以上的长视频，ElevenLabs 大文件转录和 ffmpeg 内存管理可能出现问题
- **Agent 选择的偏好**：官方预设 Claude Code 为第一目标 Agent，Codex 等其他 Agent 需要额外调试

### 争议焦点

- **"这不就是 ffmpeg 的 Agent 封装吗？"**——对也不对。外观上是 ffmpeg 封装，但核心价值是 Agent 能"智能决策"（什么时候切、用什么调色预设、字幕怎么排）。纯 ffmpeg 可做不到这些。
- **"AI 剪辑缺乏视觉审美判断"**——这是先天限制（Agent 不看视频）。但 video-use 通过自校验（timeline_view）部分缓解了这个问题。

## ⚔️ 竞品对比

| 维度 | video-use | Opus Clip | Descript | RunwayML |
|------|-----------|-----------|----------|----------|
| 核心定位 | AI Agent 视频工作流 | AI 自动剪辑（长→短） | AI 辅助剪辑软件 | AI 生成/编辑视频 |
| 操作方式 | 自然语言对话 | 一键自动处理 | GUI + AI 功能 | GUI + Prompt |
| 开放度 | **100% 开源** | 闭源 SaaS | 闭源 SaaS | 闭源 SaaS |
| 定价 | 免费（仅付 API 费） | $19+/月 | $24+/月 | $15+/月 |
| 自定义程度 | **极高**（可改 SKILL.md） | 低（预设模板） | 中 | 中 |
| Agent 集成 | 原生 Agent 编排 | 无 | 无 | 无 |
| 自校验 | 有（timeline_view 检查） | 无 | 有（文本级） | 无 |

**选择建议**：
- 你是 AI Agent 爱好者 → **video-use**（Agent 编排能力独一无二）
- 你要快速剪口播/教程 → **video-use**（对话式操作最快）
- 你需要专业多轨道编辑 → **Descript**（GUI 操作更精细）
- 你想用 AI 生成特效 → **RunwayML**（生成能力更强）

## 🎯 核心研判

### 项目优势

1. **范式创新**："LLM 不看视频"是第一性原理思维——不是问"怎么让 AI 看视频"，而是问"AI 需要看到什么才能剪辑"。这个思维可以迁移到很多领域。
2. **browser-use 团队光环**：100k+ Star 的团队背书意味着长期维护、活跃社区和持续迭代的高概率。
3. **极低进入门槛**：零代码基础的用户也能用（只需要会说自然语言）。这对"视频创作"这个大众需求的普及意义很大。
4. **Agent 可扩展性**：SKILL.md 是自然语言的，任何 Agent 都能理解和执行，不受框架限制。

### 项目风险

1. **ElevenLabs API 依赖**：Scribe 是核心依赖，API 涨价或下线将直接导致项目无法运行。缺乏自备转录的 fallback。
2. **ffmpeg 学习曲线**：虽然用户不需要懂 ffmpeg，但高级定制（自定义滤镜链、编码参数等）需要 ffmpeg 知识。
3. **长视频稳定性**：当前设计更适合短视频（<10min 素材），长视频的转录成本和渲染时间指数增长。
4. **竞品快速跟进**：Claude Code / Codex 支持的 Agent Skill 生态刚起步，大型剪辑软件公司（Adobe、Apple）推出类似功能的可能性不低。

### 趋势判断

**上升期** 🔥。视频内容创作是持续增长的市场，AI Agent 编排视频是还未被充分验证但极有潜力的方向。browser-use 团队的持续投入和社区反馈热度（1 天 5k⭐）说明这不是一个小众玩具。

## 📂 关键文件路径速查

| 文件 | 作用 |
|------|------|
| `SKILL.md` | Agent 核心技能定义（剪辑师手册，700+ 行自然语言规则） |
| `install.md` | 首次安装脚本（推荐阅读顺序：README → install.md → SKILL.md） |
| `helpers/transcribe.py` | ElevenLabs Scribe 转录（单文件，~150 行） |
| `helpers/render.py` | 渲染管线核心（EDL 消费，~250 行） |
| `helpers/grade.py` | 自动颜色分级预设 |
| `helpers/timeline_view.py` | 波形+胶片条可视化（自校验环节） |
| `helpers/pack_transcripts.py` | 多转录打包为 takes_packed.md |
| `skills/manim-video/` | Manim 动画子技能目录 |
| `skills/manim-video/references/` | 16 份参考文档（动画设计、故障排除等） |
| `pyproject.toml` | 依赖定义（仅 5 个核心依赖） |
