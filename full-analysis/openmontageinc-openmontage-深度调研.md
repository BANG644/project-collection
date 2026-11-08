# OpenMontage 深度调研

> 调研日期：2026-11-09 ｜ Stars：78,597 ｜ 语言：Python ｜ 协议：AGPL-3.0 ｜ 主分支：main ｜ 官网：openmontage.video ｜ 创建：2026-03-29

## 一、项目全景

OpenMontage（owner：`OpenMontageInc`，早期为 `calesthio`）自称"全球首个开源 agentic 视频生产系统"。它**不是带 UI 的剪辑软件**，而是一套把你的 AI 编码助手（Claude Code / Cursor / Copilot / Codex / Windsurf）变成视频工作室的工具 + 技能 + 状态层。你用自然语言描述需求（"做一个 60 秒讲神经网络怎么学习的动画解说"），agent 自主跑完 research → proposal → script → scene_plan → assets → edit → compose → render 全流程，最终吐出 MP4。

关键数字（仓库元数据 + 第三方实测交叉验证）：
- **13 条生产管线**（`pipeline_defs/` 下 13 个 YAML：animated-explainer / animation / avatar-spokesperson / character-animation / cinematic / clip-factory / documentary-montage / framework-smoke / hybrid / localization-dub / podcast-repurpose / screen-demo / talking-head）
- **100+ 工具**（`tools/video` 75、`tools/graphics` 48、`tools/audio` 40 等），零密钥可用 36 个（Piper 配音、Remotion/HyperFrames 渲染、FFmpeg、字幕）
- **700+ agent skill 与 production-knowledge 文件**
- 2026-03-29 首发，7 个月冲到 7.8 万 Stars（crazycoderslab 实测 10 月约 64.4K / 8.1K forks；11 月 78.6K）

**项目亮点**
1. **"你的编码助手就是编排器"**——没有中央 orchestrator 代码，Python 只提供工具与状态持久化，生产知识沉淀在可读的 YAML 管线 + Markdown"导演技能"里。
2. **预算护栏**：`config.yaml` 内置 `budget.mode`（observe/warn/cap）、单动作审批阈值（$0.50）、预留金（reserve_pct 10%），把"失控烧钱"工程化。
3. **Checkpoint + 人工审批门**：每个 stage 可设 `checkpoint_required` / `human_approval_default`，Backlot 本地看板实时呈现生产进度。
4. **渲染后质检**：render 后用 ffprobe 校验、抽帧、查音频电平、查字幕。
5. **供应商无关**：Veo/Kling/Runway/ElevenLabs/fal.ai 全部可选，零密钥也能出片。

## 二、核心架构

OpenMontage 可概括为 **"工具层 + 知识层 + 编排层（你自己的 agent）+ 状态层"** 四层，且编排层刻意外置：

- **工具层 `tools/`**：按模态拆分 `video/`、`graphics/`、`audio/`、`analysis/`、`capture/`、`enhancement/`、`avatar/`、`provider_contracts/`。每个供应商一个文件（`kling_video.py`、`veo_*`、`hunyuan_video.py`、`comfyui_video.py`、`cogvideo_video.py`…）。
- **知识层**：`pipeline_defs/*.yaml` 声明式定义管线；`skills/pipelines/<name>/` 下每个 stage 一个"导演技能"；`schemas/artifacts/*.schema.json` 是**生产知识图谱**的数据契约（brief / script / scene_plan / character_design / edit_decisions / render_report / cost_log / decision_log …）。
- **状态层 `lib/`**：`checkpoint.py`（断点续做）、`pipeline_loader.py`（加载并校验 YAML）、`config_model.py`、`asset_cache.py`、`scoring.py`（供应商打分）、`delivery_promise.py`、`providers/`（供应商抽象）。
- **呈现层 `backlot/` + `remotion-composer/`**：Backlot 本地实时故事板看板；remotion-composer 是 React/Remotion 合成器；另有 `ink-theater/`（mocap 动作捕获）、`hyperframes_style_bridge.py`（HTML/GSAP 渲染桥）。

数据流：自然语言 → agent 选管线 → 逐 stage 调对应导演技能 → 技能调 `tools/` 工具 + 读写 schemas 契约 → checkpoint 落盘 → compose + render + ffprobe 质检。

## 三、源码深度解读

### 1. 供应商能力注册表（`tools/video/_shared.py`）
用"能力表"抽象几十家视频供应商，关键是 **operations 能力门禁**——引擎只做表里声明的能力，拒绝加载做不到的 checkpoint：

```python
WAN_VARIANTS = {
    "wan2.2-ti2v-5b": {
        "hf_id": "Wan-AI/Wan2.2-TI2V-5B-Diffusers",
        "params_b": 5.0, "vram_mb": 12000, "quality": "high",
        # 能力门禁：表里没有的操作直接拒绝，而非硬上不匹配的 checkpoint
        "operations": ["text_to_video","image_to_video","video_to_video",
                       "first_last_frame","text_to_image"],
        "default_width": 1280, "default_height": 704,  # TI2V 16x VAE+2x patch，720 非 32 倍数
        "default_num_frames": 121, "default_steps": 50,
        "spatial_alignment": 32, "temporal_scale": 4, "fps": 24,
    },
}
```
同文件 `HEYGEN_PROVIDERS` 记录每家供应商 quality/speed 矩阵——这是"自带供应商打分"的数据底座。

### 2. 声明式管线（`pipeline_defs/talking-head.yaml`）
一条管线 = 一组导演技能的有向编排 + 阶段门禁：

```yaml
orchestration:
  mode: executive-producer
  skill: pipelines/talking-head/executive-producer
  budget_default_usd: 0.50
  max_revisions_per_stage: 3
stages:
  - name: idea
    skill: pipelines/talking-head/idea-director
    produces: [brief, decision_log]
    checkpoint_required: true
    human_approval_default: true
```
`required_skills` 列出 executive-producer / idea-director / script-director / scene-director / asset-director / edit-director / compose-director / publish-director / meta/reviewer / meta/checkpoint-protocol 共 10 个技能，构成完整"制片班组"。

### 3. 生产契约（`schemas/artifacts/script.schema.json`）
用 JSON Schema 2020-12 把"脚本"结构化，其中 `voice_performance` 是交给 TTS 的**配音履约契约**：

```json
"voice_performance": {
  "properties": {
    "pacing_profile": {"enum":["contemplative","conversational",
       "energetic","technical","cinematic","custom"]},
    "energy_curve": {"type":"string"},
    "pause_policy": {"type":"string"},
    "sample_section_id": {"description":"最需表演敏感度的段落，用于 TTS 样片确认"}
  }
}
```
契约化让 agent 之间、agent 与渲染器之间的接口可校验、可审计。

## 四、应用场景与启发

- **个人/小团队 AI 视频工作站**：独立创作者用零密钥路径（Piper + 开源素材 + Remotion + FFmpeg）即可出解说/混剪；付费 API 仅用于高级镜头。
- **把"生产规范"当代码管理**：核心启发是把影视工业里"导演怎么拍、审稿人怎么卡"沉淀成可读 YAML/Markdown 技能，而非提示词堆砌。任何**多步骤、强规范、需人工把关**的知识工作（法律尽调、医学报告、论文写作）都能用同构模式重做。
- **预算护栏范式**：把"单动作成本上限 + 预留金 + 审批门"做进配置，值得任何**按调用计费**的 agent 系统借鉴（与本仓库已入库的 pr-agent、agent-desktop 等方法论呼应）。
- **契约化中间产物**：用 JSON Schema 约束每段产出（brief/script/scene_plan），比"让 LLM 自由写 Markdown"更可回滚、可质检——对 agent 编排系统是高价值工程实践。

## 五、社区口碑

- **增长与定位争议**：notatechguy 指出"world's first"是宣传语、所有成本数字（如 "The Last Banana" $1.33）均来自维护者自述、无独立基准，且初始提交 240K 行体量大。
- **实测可用**：crazycoderslab 在 Linux 实测 setup 与 contract tests 通过（1,229 passed / 7 skipped），工具注册表识别 137 个工具、36 个零密钥可用，零密钥 demo 渲染 25 秒 1080p MP4 约 90 秒；但作者坦言未跑完整 agent 生产、不评价成片质量。
- **安全与企业化质疑**：CSDN aicoding 给出 3.8/5，核心扣分项——AGPL 协议 + 强外网 API 依赖使**企业私有化部署困难**（30/100）；700+ 技能文件 = 700 个潜在 prompt-injection 攻击面；凭据集中管理、网络出口隔离弱。
- **产品定位共识**：heatdrop 总结"适合想要可复现、code-first 视频生成、不愿被 SaaS 黑箱绑架的开发者；如果你要时间轴 GUI/WYSIWYG，它不是给你的"。

> 口碑研判：工程完成度与"agent 即编排器"的范式创新获普遍认可；主要隐忧集中在成本可信度、AGPL 商用边界、技能文件安全面、无人类 GUI。

## 六、竞品对比

| 维度 | OpenMontage | Runway/Kling/Sora（闭源 API） | ComfyUI 工作流 | n8n + 视频节点 |
|------|-----------|------------------------------|---------------|---------------|
| 编排主体 | 你的编码 agent | 厂商平台 | 节点图（人拖） | 可视化流程（人配） |
| 协议 | AGPL-3.0 | 闭源 SaaS | 开源（节点各自许可） | 开源 |
| 生产知识沉淀 | YAML 管线 + 700 技能 | 无（黑箱） | 社区 JSON 流 | 社区模板 |
| 人工把关 | 内置 checkpoint+审批门 | 平台内有限 | 手动 | 手动 |
| 预算护栏 | 内置（$） | 仅账单 | 无 | 无 |
| 零密钥可用 | ✅ | ❌ | 视模型 | 视模型 |

结论：它的对手不是"另一个剪辑软件"，而是**"你直接调视频模型 API"**——它把零散调用升级成带规范、带把关、带质检的生产系统。相对 ComfyUI/n8n，差异化是**以 agent 为编排核心 + 制片级技能资产 + 预算/质检护栏**。

## 七、核心研判

1. **范式价值高**：把"导演知识"工程化为可加载技能、把预算/质检做成配置，是 agentic 生产系统的优秀参考实现，值得任何多步知识工作借鉴。
2. **落地门槛与风险并存**：依赖一个"够强"的编码 agent（Claude Code/Cursor 等常付费）；最佳成片仍需付费 API；AGPL 对闭源商用不友好，企业内网/离线场景受限。
3. **安全面需警惕**：700+ 技能文件应视作不可信代码，引入前需审计；成本数字勿直接采信，应自建可复现 cost log。
4. **数据不可用**：无独立第三方基准、无公开准确率/成本审计报告；"world's first"未经验证。

## 八、关键文件路径速查

- `config.yaml` — 全局配置（LLM 供应商、budget 护栏、checkpoint 策略、输出格式）
- `pipeline_defs/*.yaml` — 13 条声明式生产管线（talking-head / cinematic / clip-factory …）
- `tools/video/_shared.py` — 供应商能力注册表（HEYGEN_PROVIDERS / WAN_VARIANTS + operations 门禁）
- `tools/{video,graphics,audio}/` — 模态工具实现（kling_video.py / hunyuan_video.py / comfyui_video.py …）
- `skills/pipelines/<name>/` — 各 stage 的"导演技能"（executive-producer / script-director …）
- `schemas/artifacts/*.schema.json` — 生产知识图谱契约（script / scene_plan / edit_decisions / cost_log …）
- `lib/checkpoint.py` `lib/pipeline_loader.py` `lib/config_model.py` `lib/scoring.py` — 状态/加载/配置/打分
- `backlot/` — 本地实时故事板看板；`remotion-composer/` — React/Remotion 合成器
- `render_demo.py` `render-demo.sh` — 零密钥 demo 渲染入口
