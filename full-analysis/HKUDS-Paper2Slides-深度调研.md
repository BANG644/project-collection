# HKUDS/Paper2Slides 深度调研

> 调研日期：2026-09-20 | 星标：3,831⭐ | 语言：Python（3.12+）/ Vue | 许可：MIT | 默认分支：main | 最近提交：2026-05-20
> 定位：把论文/报告/文档"一键"转成专业 slides 与 poster 的 RAG 驱动生成框架，出自港大 HKUDS 实验室。

## 一、项目亮点（差异点）

1. **4 阶段可恢复流水线**：RAG → Analysis → Planning → Creation，每阶段落盘 JSON checkpoint（`checkpoint_rag/summary/plan.json`），中断后同命令自动续跑，改风格只需 `--from-stage plan`，改图只跑 `--from-stage generate`。
2. **RAG 溯源保真**：基于自研 `RAGAnything`（多模态解析，底层接 MinerU）构建检索索引，生成内容与原文档强关联，降低"幻觉漂移"。
3. **自然语言自定义风格**：`--style "Studio Ghibli ..."` 即可套主题，内置 `academic` / `doraemon` 等，兼顾开箱与个性化。
4. **并行 + 双形态**：`--parallel N` 多 worker 提速；同一条流水线产出 slides 或 poster。
5. **Web UI**：React/Vite 前端 + FastAPI 后端（`api/server.py`），含会话/历史/预览面板，降低使用门槛。

## 二、核心架构

```
python -m paper2slides --input paper.pdf --output slides --style doraemon --length medium --parallel 2
        │
   core/pipeline.py  ── 串联 4 阶段（每阶段 checkpoint 落盘）
        ├─ rag_stage      → raganything/ 多模态解析 + rag/(client,query) 建索引
        ├─ summary_stage  → summary/extractors/{figure,table}_extractor 抽结构/图/表
        ├─ plan_stage     → generator/content_planner 产出版式蓝图
        └─ generate_stage → generator/image_generator + prompts/ 渲染成稿
```

模块清晰分层：`rag/`（检索）、`summary/`（结构化抽取）、`generator/`（规划+生图）、`raganything/`（文档解析）、`prompts/`（各阶段提示词）、`core/`（编排与状态）。

## 三、应用场景与启发

- **给同类需求的解法**：做长文档→演示的产品，**"分阶段 + 每阶段 checkpoint"** 是工程上最稳的容错范式——比 agent 黑盒循环更易调试、可断点续跑、可单阶段重放。
- **对你（科研/PPT 方向）**：与 PPTAgent 互补——Paper2Slides 偏"论文一次性出稿+溯源"，PPTAgent 偏"多 agent 反思精修"。两者可串成"论文→slides 草稿→反思精修"链路；其 `raganything` 多模态解析也可单独用于论文伴读的知识抽取。
- **可借鉴**：自然语言风格指令、并行 worker、Fast/Normal 双模式（短文档跳过 RAG 直查 LLM）。

## 四、源码深度解读

**① 流水线编排（`core/pipeline.py` 思路）**——四阶段按 checkpoint 文件存在与否决定跳过重跑：

```python
# 伪结构（依据 README 的 --from-stage 与 checkpoint 命名）
stages = ["rag", "summary", "plan", "generate"]
for stage in stages:
    ckpt = f"checkpoint_{stage}.json"
    if os.path.exists(ckpt) and not force_from(stage):
        state = load(ckpt); continue   # 已跑过 → 复用，支持断点续跑
    state = run_stage[stage](state)     # 否则执行并把结果落盘
    save(ckpt, state)
```

**② 多模态解析（`raganything/`）**——依赖 MinerU 做 PDF/图/表抽取，向上提供统一 query 接口（`raganything/query.py` + `rag/query.py`），是 RAG 溯源保真的底座。阶段提示词集中在 `prompts/{paper_extraction,content_planning,image_generation}.py`，便于调优。

## 五、社区口碑

- 出自港大 HKUDS（同实验室有 ViMax、Paper2Slides 等系列研究工具），学术可信。
- 2025-12 开源即获 3.8k⭐，演示图（doraemon/academic/totoro 多主题）传播力强。
- 短板：最近提交停在 2026-05，更新节奏不如 PPTAgent 活跃；深度依赖外部 LLM API（需 `.env` 配 key）。

## 六、竞品对比

| 项目 | 生成范式 | 断点续跑 | 溯源保真 | 风格自定义 |
|------|---------|---------|---------|-----------|
| **Paper2Slides** | 4 阶段 pipeline | ✅ checkpoint | ✅ RAG | ✅ 自然语言 |
| PPTAgent/DeepPresenter | 多 agent + 反思 | 部分（上下文管理） | 弱 | 模板/自由 |
| 通用 LLM→PPTX | 单步 | ❌ | ❌ | 弱 |

## 七、核心研判

Paper2Slides 是"论文→slides/poster"场景里**容错工程最扎实、上手最轻**的开源方案，RAG 溯源 + checkpoint 续跑是它对抗幻觉与长任务失败的两张王牌。它走 pipeline 而非 agent 循环，代价是精修灵活性弱于 PPTAgent，但换来可预测与可调试。适合"批量把一堆论文/报告先出草稿"的科研工作流。

## 关键文件路径速查

- `paper2slides/core/pipeline.py` — 四阶段总编排（checkpoint 驱动）
- `paper2slides/core/stages/{rag,summary,plan,generate}_stage.py` — 各阶段实现
- `paper2slides/raganything/` — 多模态文档解析（MinerU 底座）
- `paper2slides/summary/extractors/{figure,table}_extractor.py` — 图/表抽取
- `paper2slides/generator/{content_planner,image_generator}.py` — 规划与生图
- `paper2slides/prompts/*.py` — 各阶段提示词
- `api/server.py` + `frontend/` — Web UI 后端/前端
