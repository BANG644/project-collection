# HKUDS/ViMax 深度调研

> 调研日期：2026-09-26 | 数据来源：GitHub API（README / 源码树 / pipeline 源码）| 许可：MIT | Stars：12,483 | Forks：1,880 | 语言：Python | 默认分支：main | 论文：arXiv 2606.07649

## 一、项目定位（一句话）

**Agentic 视频生成**框架——把「导演、编剧、制片、视频生成器」四位一体，提供 `idea→video` / `novel→movie` / `script→video` 三条端到端管线，让一句话或小说自动变成带角色一致性的视频。

## 二、项目亮点（差异化）

1. **多入口管线**：`Idea2Video` / `Novel2Movie` / `Script2Video` 三条流水线，覆盖从创意到成片的多种起点。
2. **角色一致性工程**：抽取角色→生成 front/side/back 三视角肖像→建注册表，解决 AI 视频「角色变脸」顽疾。
3. **可复现 + 断点续跑**：每个阶段产物落盘为 `story.txt` / `characters.json` / `script.json` / 分场景目录，重跑直接读缓存。
4. **HKUDS 出品**：同团队有 ClawWork、Paper2Slides 等高质量 agent 项目，学术品牌可信。
5. **配套基准**：`vimax_benchmark/` 用于评测，体现研究闭环。

## 三、核心架构

```
main_idea2video.py / main_script2video.py   # 入口
agents/        # Screenwriter, CharacterExtractor, CharacterPortraitsGenerator,
               # StoryboardArtist, SceneExtractor, EventExtractor, CameraImageGenerator...
pipelines/     # idea2video_pipeline.py / novel2movie_pipeline.py / script2video_pipeline.py
tools/         # render_backend.py（图像/视频生成后端抽象）
interfaces/    # 数据契约（CharacterInScene 等 pydantic 模型）
configs/ prompts/ utils/ ui/ web/ agent_runtime/
```

- 模型层用 `langchain.chat_models.init_chat_model` + `utils/provider_presets` 做 provider 解析，渲染后端经 `RenderBackend.from_config` 抽象，便于换图像/视频生成服务。

## 四、应用场景与启发

- **短剧/解说视频自动化**：小说/创意自动成片，适合影视解说、短视频批量生产。
- **借鉴点**：「多 agent 角色分工 + 每阶段落盘缓存 + 失败兜底」是长链路生成任务的通用健壮性范式；角色一致性（多视角肖像+注册表）值得任何视频生成项目抄。

## 五、源码深度解读

**`pipelines/idea2video_pipeline.py`——编排与健壮性内核**

`__call__` 主流程：
```python
story = await self.develop_story(idea, user_requirement)          # 编剧扩写
characters = await self.extract_characters(story)                 # 角色抽取
registry = await self.generate_character_portraits(characters, ...) # 三视角肖像
scene_scripts = await self.write_script_based_on_story(story, ...) # 剧本
for idx, scene in enumerate(scene_scripts):                      # 逐场景渲染
    Script2VideoPipeline(...) -> final_video_path
concatenate_video_files(all_video_paths, final_video_path)        # 拼接成片
```

两个值得抄的工程细节：
1. **可见性过滤**：`character.is_visible` 为假（仅语音/聊天角色）时跳过肖像生成，注释直言否则图像模型会 `finish_reason=IMAGE_OTHER` 空候选反复失败。
2. **失败兜底**：side/back 肖像生成重试仍失败时 `shutil.copy(front_portrait_path, ...)` 复用正面图而非中断整条管线。

每个阶段都先查本地缓存文件、存在即跳过——天然支持断点续跑与成本节省。

## 六、社区口碑

- 12.5k⭐ / 1.9k fork，配套 arXiv 2606.07649 论文，HKUDS 学术背书。
- 工程文档（README_ZH、Communication.md、assets 示例）较完整，偏研究原型而非开箱产品。

## 七、竞品对比

| 维度 | ViMax | Pika/Runway/Sora | NarratoAI |
|------|-------|------------------|-----------|
| 形态 | 开源 agentic 编排 | 闭源 API/产品 | 开源剪辑流水线 |
| 角色一致 | ✅ 三视角+注册表 | 各厂商私有 | 弱 |
| 可复现缓存 | ✅ 分阶段落盘 | 否 | 部分 |
| 学术基准 | ✅ vimax_benchmark | 否 | 否 |

**差异点**：开源、可审计、可复现，且把「角色一致性」作为一等公民工程化处理。

## 八、核心研判

- **研究原型属性强**：依赖多个外部图像/视频生成后端，生产需强算力与 API 预算；离「一键成片产品」尚有距离。
- **价值在范式**：其「agent 分工 + 缓存 + 兜底」的工程化处理，比模型本身更值得借鉴。
- **建议**：做 AI 视频/长链路生成需求时，优先参考其 pipeline 拆分与失败兜底设计；直接使用需评估图像/视频后端成本与许可。

## 关键文件路径速查

- `pipelines/idea2video_pipeline.py` — 创意到成片主编排
- `pipelines/script2video_pipeline.py` — 剧本到分镜渲染
- `agents/screenwriter.py` — 编剧/剧本生成 agent
- `agents/character_extractor.py` / `character_portraits_generator.py` — 角色与肖像
- `tools/render_backend.py` — 图像/视频生成后端抽象
- `vimax_benchmark/` — 评测基准
