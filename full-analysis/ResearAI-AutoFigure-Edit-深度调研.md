# ResearAI/AutoFigure-Edit — 深度调研

> 调研日期：2026-09-28 ｜ 星标：4,292 ｜ 许可：MIT ｜ 语言：Python 3.10+ ｜ 论文：arXiv 2603.06674（AutoFigure 系，ICLR 2026 血统）｜ 在线：deepscientist.cc

## 1. 项目定位（一句话）
把论文**方法文本**一键变成**完全可编辑的 SVG 科研示意图**，并支持风格迁移——是 AutoFigure（ICLR 2026）的升级版。

## 2. 项目亮点
- **可编辑矢量输出（纯代码实现）**：不同于位图，输出是结构化 SVG，文字/形状/布局均可无损修改——解决"AI 出图不能改"的痛点。
- **四阶段管线**：Generation → SAM3 分割 → 占位符 SVG 模板 → 装配最终矢量图，每阶段落盘中间产物（`figure.png`/`samed.png`/`boxlib.json`/`template.svg`/`final.svg`）。
- **风格迁移 + 图标检测**：SAM3 多提示词检测图标区域并合并重叠；可模仿用户参考图的画风。
- **v1.1 实用增强**：支持用户自备 stage-1 图直接续跑；官方 OpenAI 模型（`gpt-image-2` / `gpt-5.5`）；Bianxie AI 与 `custom` OpenAI 兼容路由；中英双语界面与引导。
- **学术背书**：AutoFigure 中稿 ICLR 2026；HF Daily Papers 推荐；配套 HF 数据集 `WestlakeNLP/FigureBench`；姐妹项目 DeepScientist v1.5（ICLR 2026）。

## 3. 核心架构
- **主干**：`autofigure2.py`（约 137KB 的编排器）串起四阶段；依赖 SAM3 分割、RMBG-2.0 去背景、文本/多模态 LLM 生成 SVG。
- **部署**：Docker Compose 一键起 Web（端口 8000），需 `HF_TOKEN` 拉 `briaai/RMBG-2.0`；支持受限网络镜像（清华 PyPI /  DaoCloud 基础镜像）。
- **配置**：`.env` 控制 SAM3 后端（默认 Roboflow）、重试调参（`OPENROUTER_MULTIMODAL_RETRIES`）、DNS 覆盖。

## 4. 应用场景与启发
- **科研作图自动化**：用户做 OCR/ML 科研，写方法小节时常需画 pipeline 图；AutoFigure-Edit 能从文本直接产出"可改的"矢量图，比截图/PPT 手画高效且可迭代。
- **借鉴"文本→可编辑图"范式**：可迁移到用户**错题归因报告**的自动配图——把归因链路文本渲染成可编辑 SVG 示意图。
- **注意依赖**：需多模型（图像生成 + 多模态 SVG）+ SAM3 + RMBG-2.0，本地部署有算力/网络门槛。

## 5. 源码深度解读
`README.md` 给出的四阶段技术管线（"Detailed Technical Pipeline"）是核心，由 `autofigure2.py` 编排：
1. **Generation**：文本→图像 LLM 渲染期刊风示意图 → `figure.png`
2. **Segmentation**：SAM3 用 "icon/diagram/arrow" 等提示词分割，IoU 阈值合并重叠，输出 `samed.png`（带标签遮罩）+ `boxlib.json`（坐标/分数/提示来源）
3. **Templating**：以 `figure.png`+`samed.png`+`boxlib.json` 为多模态输入，LLM 生成占位符风格 `template.svg`
4. **Assembly**：比对 SVG 与原图尺寸算缩放，把去背景图标（RMBG-2.0，存 `icons/*.png`）按 label/ID 注入模板 → `final.svg`

关键配置项：`Placeholder Mode`(label/box/none) 控制图标框编码方式；`optimize_iterations=0` 可跳过多轮 LLM 优化直接用原始结构。

## 6. 社区口碑
- ICLR 2026 血统 + HF Daily Papers 推荐 + 在线免费平台，学术可信度高；4.3k⭐增长快。
- 局限：重依赖外部模型与 SAM3/RMBG，纯本地离线体验受限；核心 `autofigure2.py` 单体较大（~137KB），模块化可读性一般。

## 7. 竞品对比 + 核心研判
| 项目 | 输出 | 差异 |
|---|---|---|
| AutoFigure-Edit | **可编辑 SVG** + 风格迁移 | 编辑性最强 |
| AutoFigure (v1) | 初代，编辑性较弱 | 前身 |
| Diagrammer / Ichigraphics | 多为位图/固定版式 | 不可无损改 |

**研判**：在"科研配图"赛道凭**可编辑矢量 + 风格迁移**建立了差异点；对需要反复改图的论文作者价值显著。建议作为用户科研作图管线的一环试用，但需评估多模型成本。

## 8. 关键文件路径速查
- `autofigure2.py` — 四阶段编排主干
- `README.md` / `README_ZH.md` — 管线与技术细节、v1.1 说明
- `releases/v1.1.md` — 版本说明
- `Dockerfile` / `docker-compose.yml` / `.env.example` — 部署
- `CITATION.cff` / `CITATION_AND_ATTRIBUTION.md` — 引用与署名
- `img/pipeline.png` / `img/method.png` / `img/case/*` — 管线图与 9 组样例
