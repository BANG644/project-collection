# 🔬 bradautomates/claude-video — 全方位深度调研

> **仓库**: https://github.com/bradautomates/claude-video
> **调研日期**: 2026-07-07
> **Stars**: 4,137⭐
> **技术栈**: Python, yt-dlp, ffmpeg, Groq/OpenAI Whisper
> **许可**: MIT

## 📌 一句话定位

bradautomates/claude-video（又名 `/watch`）是一个 Agent Skill——给 Claude Code / Codex / Cursor / Gemini CLI 等 50+ AI 编程代理装上"眼睛"，让它们能下载视频、提取字幕、抽帧截图，真正"看"懂视频内容后回答问题。

## ⭐ 项目亮点

1. **"视频理解"是 Agent 能力的明确缺失环节** — AI Agent 能读代码、读网页、读 PDF，但唯一不能直接处理的就是视频。`/watch` 精准填补了这个空缺。它不是模糊的功能叠加，而是对"Agent vision"空缺的精准定位。
2. **从 Caption 到 Whisper 的多级降级策略** — 先走免费字幕（yt-dlp 拉取自动/手动字幕），字幕不可用才走 Groq Whisper（便宜快），最后才回退到 OpenAI Whisper。默认的情况下**大部分公共视频免费**。
3. **场景感知帧提取（scene-change detection）** — 不是均匀抽帧，而是用 ffmpeg 的场景检测算法只在"画面变化"时提取帧。3 级粒度（efficient/balanced/token-burner）对应不同 token 预算。
4. **帧去重（dedup）** — 录屏类视频同一画面可能持续几十秒，CodexBar 检测相邻帧的差异阈值，只保留画面有实质变化的帧。这避免了 Token 浪费在"同一张幻灯片上"。
5. **端到端 Skill 架构是教科书级** — `SKILL.md` 为入口、`scripts/` 为 runtime、`tests/` 为测试、`hooks/` 为启动钩子、`.claude-plugin/` + `.codex-plugin/` 为多平台分发。每个想要做 Agent Skill 的人都可以参考这个结构。

## 🏗️ 项目架构全景

### 目录结构

```
claude-video/
├── skills/watch/                # 自包含 Skill 单元
│   ├── SKILL.md                 # Skill 契约（所有平台共享）
│   └── scripts/
│       ├── watch.py             # 入口编排：下载→抽帧→转录
│       ├── download.py          # yt-dlp 下载封装
│       ├── frames.py            # ffmpeg 帧提取 + 去重
│       ├── transcribe.py        # VTT 解析 + Whisper 调度
│       ├── whisper.py           # Groq/OpenAI Whisper 客户端
│       ├── config.py            # ~/.config/watch/.env 配置
│       ├── setup.py             # 首次运行依赖安装
│       └── build-skill.sh       # 构建 claude.ai 上传包
├── tests/                       # pytest 测试套件
├── hooks/                       # Claude Code SessionStart 钩子
├── .claude-plugin/              # Claude Code marketplace
├── .codex-plugin/               # Codex/Agent Skills manifest
└── .github/workflows/           # 自动构建 release
```

**设计哲学**：整个 skill 是**自包含的**——`skills/watch/` 目录可以完整拷贝到任何 Agent 的 skills 目录，所有依赖（除 `ffmpeg` 和 `yt-dlp` 外）都是 Python stdlib + pip 包。这是"一次性安装，到处运行"的典范。

### 技术栈 & 依赖

| 模块 | 依赖 | 角色 |
|------|------|------|
| 视频下载 | yt-dlp | 支持 YouTube/Loom/TikTok/X/Instagram 等数百个平台 |
| 帧提取 | ffmpeg | 关键帧 + 场景检测 + 图像缩放 |
| 字幕转录 | yt-dlp（字幕）+ Groq/OpenAI Whisper | 免费字幕优先，付费 API 兜底 |
| 帧去重 | Python stdlib | 纯数学计算，零外部依赖 |
| 配置 | Python stdlib configparser | ~/.config/watch/.env |
| 测试 | pytest + ffmpeg 合成片段 | 无网络依赖的离线测试 |

## 💡 应用场景与启发

### 典型使用场景

1. **Bug 复现视频分析** — 同事/客户发来一个 `.mov` 屏幕录制，说"这里出 bug 了"。`/watch bug-repro.mov` → Claude 看完全部帧后诊断问题，精确到"UI 在 0:23 失去响应"。
2. **竞品视频拆解** — `youtube.com/@competitor latest` → `/watch` 帮抓开场 hook、结构分析、广告创意拆解。适用于市场营销和产品竞研。
3. **教学/会议视频摘要** — 长视频（1 小时+）→ `/watch --detail token-burner` 对所有场景变化帧做分析，输出结构化摘要。比手动 2x 倍速看快多了。
4. **频道的课程笔记化** — `youtube.com/playlist?list=...` → 逐集 `/watch summarize to a note` → 一个频道/课程变成可搜索的笔记集。

### 可借鉴的解决方案模式

- **多级降级策略**：脚本设计上，从"最便宜的方式开始，逐步回退到最贵的方式"。字幕→Groq Whisper→OpenAI Whisper，这个模式可以照搬到很多依赖外部 API 的 Agent Skill 设计上。
- **自包含 Skill 单元**：整个 `scripts/` 目录 + `SKILL.md` 等于一个可移植的 Agent 能力单元。拷贝即用，不依赖宿主系统的目录约定。这是 Agent Skill 开发的最佳实践。
- **`setup.py` 的智能检测**：首次运行自动检测 ffmpeg 和 yt-dlp 是否安装，未安装则根据操作系统自动安装。这种"detect + auto-install"模式比"用户自己看文档"友好得多。

### 同类需求的可参考思路

任何需要 AI Agent "感知"现实世界多媒体（视频/音频/图片流）的场景，都可以参考 `/watch` 的 pipeline 设计：[下载] → [转码] → [分帧/分段] → [转文字] → [喂给 Agent]。

## 🧠 核心源码解读

### 主流程编排

`watch.py` 是整个 Skill 的入口，编排了"下载→帧提取→转录→喂给 Claude"全链路：

```python
# skills/watch/scripts/watch.py（逻辑骨架）
def watch(url: str, detail: str = "balanced"):
    # Step 1: 下载视频
    video_path = download.video(url)

    # Step 2: 提取字幕
    caption_path = transcribe.extract_captions(video_path)
    if not caption_path:
        # Fallback: 下载音频→Whisper 转录
        audio_path = download.audio(video_path)
        caption_path = whisper.transcribe(audio_path)

    # Step 3: 提取帧（场景感知）
    frames = extract_frames(video_path, detail)
    deduped = deduplicate(frames)  # 去重

    # Step 4: 输出给 Claude
    print("Transcript:", caption_path)
    for f in deduped:
        print(f"Frame: {f.path} @ {f.timestamp}")
    # Claude 会自动 Read 这些帧作为图片
```

### 帧提取（场景感知 vs 关键帧）

```python
# skills/watch/scripts/frames.py（逻辑骨架）
def extract_frames(path, detail, fps, max_frames):
    if detail == "efficient":
        # 关键帧模式 — ffmpeg skip_frame nokey
        # 只解码 I 帧，极快（0.5s 处理 49 分钟视频）
        cmd = f"ffmpeg -skip_frame nokey -i {path} ..."
    elif detail in ("balanced", "token-burner"):
        # 场景变化检测 — 逐帧解码，检测 cuts
        # 慢但精确（20s 处理 49 分钟视频）
        cmd = f"ffmpeg -filter:v select='gt(scene,0.4)' ..."

    # 帧预算裁剪：采样到 max_frames 以内
    # 确保第一个和最后一个帧始终保留
    return even_sample(all_candidates, max_frames)
```

`efficient` 是"画面变但我不关心细节"的场景（如会议录像），`balanced` 是"我要看见每帧细节"的场景（如 UI 录制）。

### 帧去重算法

```python
# skills/watch/scripts/frames.py（去重逻辑）
def deduplicate(frames, threshold=2.0):
    # 1. 每帧缩放为 16×16 灰度缩略图
    # 2. 计算与"最后保留的帧"的均值绝对差
    # 3. 差值 ≤ 2.0 视为重复，丢弃
    # 4. 差值 > 2.0 视为新帧，保留
    kept = [frames[0]]
    for frame in frames[1:]:
        diff = mean_absolute_difference(to_grayscale(frame), to_grayscale(kept[-1]))
        if diff > threshold:
            kept.append(frame)
    return kept
```

这个算法用纯 Python stdlib 实现，不需要 OpenCV/PIL 等外部依赖。

## 📐 架构决策与设计哲学

### 关键设计决策

- **SKILL.md 作为唯一真相源**：一个 `SKILL.md` 同时服务 Claude Code、Codex、Cursor、Copilot、Gemini CLI 等 50+ 宿主。这在"多平台分发"上节省了大量维护成本。
- **Python 而非 Shell**：整个脚本集群用 Python 而非 bash，因为 bash 处理 JSON 解析、错误处理、参数校验的能力远不如 Python。
- **`--start/--end` 聚焦模式**：不是让用户对整个 1 小时视频做高密度分析，而是鼓励"聚焦到某一段"——这是 token 效率和人机交互的双赢设计。

### 设计红线

- **不需要 GPU**：所有计算在 CPU/Claude 多看里完成，不依赖本地 GPU
- **不需要云账号**：字幕免费的占绝大多数，Whisper 是可选兜底

## 🌐 全网口碑画像

### 好评共识

- "Claude Code 最实用的社区 Skill 之一" — 中文技术博客
- "/watch 解决了 Agent 不能看视频的大痛点" — 知乎
- 在 2026 年推特最火的 10 个 Claude Skills 中被提及

### 差评共识 & 踩坑高发区

- **长视频帧预算**：超过 10 分钟的默认 `balanced` 模式会变得稀疏，需要切换到 `token-burner` 或 `--start/--end`
- **Whisper 依赖性**：没有字幕的视频必须配 Whisper API key，增加配置步骤
- **macOS only 自动安装**：`brew install ffmpeg yt-dlp` 在 Linux/Windows 上需要手动处理

## ⚔️ 竞品对比

### 对比矩阵

| 维度 | claude-video (/watch) | 手动下载+Analyze | Anthropic 内置视频 |
|------|---------------------|-----------------|-------------------|
| 自动化程度 | 一键 `/watch url` | 手动下载→转帧→转录→粘贴 | 无（Claude 原生不支持视频输入） |
| 帧提取 | 场景感知+去重 | 需自行找工具 | N/A |
| 字幕处理 | 自动多级降级 | 需自行转录 | N/A |
| 多平台 | 50+ Agent 宿主 | 仅自己的脚本 | Claude.ai |
| 安装复杂度 | 低（`npx skills add`） | 高（手动搭 pipeline） | 零 |
| 长视频处理 | 有框架限制和解决策略 | 自定 | N/A |

### 选择建议

- **用 `/watch`**：任何使用 Claude Code/Codex/Cursor 等 Agent 的用户，需要分析视频的场景
- **手动处理**：需要更精细的帧控制（不是场景感知，而是逐帧）或高度定制化
- **Anthropic 官方**：目前不支持视频输入，所以没有替代

## 🎯 核心研判

### 项目优势

- **精准的市场空白**：Agent 能读网页、代码、PDF、图片，唯独不能"看"视频。`/watch` 就是填补这个空白的最直接方案。
- **工程化完善**：从管线设计（多级降级）、帧提取算法、去重、到多平台 SKILL.md 分发，整个项目工程化程度远高于同类 Agent Skill。
- **生态兼容**：同时支持 Claude Code/Codex/Cursor/Copilot/Gemini CLI/etc - 不绑定单一平台。

### 项目风险

- **依赖外部工具**：yt-dlp 和 ffmpeg 的可用性、版本兼容性不在项目控制范围内
- **API 兼容性**：Groq/OpenAI Whisper 的 API 变更可能随时断掉
- **Claude Code 生态依赖**：如果 Anthropic 以后内置视频支持，`/watch` 会被替代。但目前没有明确迹象

### 适用场景 & 不适用场景

✅ **用**：需要 Agent 分析视频内容的开发者 | Bug 诊断（屏录分析）| 视频摘要（会议/课程/发布会）| 竞品视频拆解

❌ **不用**：Agent 不支持 Skill 的（纯 ChatGPT 对话场景）| 不需要视频分析 | 对每帧精确控制有极高要求

### 趋势判断

**早期爬升期** — 4.1K Stars 还在快速增长。随着 Agent Skill 生态（Agent Skills marketplace 等）成熟，`/watch` 作为"Agent 视频理解"的先驱，潜力不小。

## 📂 关键文件路径速查

| 文件 | 用途 |
|------|------|
| `skills/watch/SKILL.md` | Skill 契约（唯一真相源） |
| `skills/watch/scripts/watch.py` | 主入口—编排全流程 |
| `skills/watch/scripts/frames.py` | 帧提取+去重算法 |
| `skills/watch/scripts/whisper.py` | Groq/OpenAI Whisper 客户端 |
| `skills/watch/scripts/config.py` | 配置管理 |
| `skills/watch/scripts/setup.py` | 首次运行依赖检测+安装 |
| `tests/` | pytest 测试套件 |
