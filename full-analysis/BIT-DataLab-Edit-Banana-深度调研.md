# BIT-DataLab/Edit-Banana 深度调研

> 调研日期：2026-10-01 ｜ 数据源：gh API（README / 目录树 / main.py / server_pa.py / modules/）｜ 定位：把静态图（流程图/架构图/示意图/公式）转成可编辑 DrawIO XML 的 AI 重建工具（AGPL-3.0，许可证存在争议）

## 一、项目定位（一句话）

**Edit-Banana** 是一个「通用内容再编辑」框架：用 SAM 3 分割 + 多模态大模型（VLM）文字识别，把**不可编辑的静态图片图表**高精度重建为**完全可拖拽/改样式的 DrawIO（.drawio）XML**，让图片版流程图、架构图、技术示意图、公式变成可二次编辑的资产。

## 二、项目亮点（差异化）

1. **SAM3 + VLM 双引擎重建**：自研/微调的 SAM3 做元素级分割（掩码），VLM 做多轮固定扫描提取文本与逻辑，二者融合生成 DrawIO——保真度优于「截图 OCR 后丢结构」的常规做法。
2. **全元素可编辑**：还原后每个形状/箭头/文字均可独立选中、改色、改样式，并兼容 DrawIO 原生模板替换与布局优化。
3. **多 OCR/公式引擎可插拔**：本地 Tesseract（含中文 chi_sim）/ PaddleOCR 做文字定位，Pix2Text 做数学公式→LaTeX 识别，Crop-Guided 策略把高分辨率裁图送公式引擎。
4. **面向多用户服务的工程化**：内置用户系统（注册赠 10 免费额度、按次计费防滥用）、`Global Lock` 保证线程安全的 GPU 访问、`LRU Cache` 持久化图片 embedding 以扛并发。
5. **学术背书**：北理工（BIT）数据实验室出品，负责人为数据库/多媒体方向教授团队，配套在线 Demo（editbanana.net）。

## 三、核心架构

- **技术栈**：Python 3.10+ / PyTorch(CUDA 推荐) / FastAPI（`server_pa.py`）/ SAM3（facebookresearch/sam3）/ Tesseract·PaddleOCR / Pix2Text / DrawIO XML。
- **流水线（README 明示）**：Input 图片 → SAM3 分割 → 文本提取（并行：Tesseract/PaddleOCR 定位 + Pix2Text 公式）→ 合并 SAM3 空间信息与 OCR 文本 → 生成 DrawIO XML。
- **模块划分**：
  - `main.py`：CLI 入口，定义 `Pipeline` 类，按「懒加载单例」组织各处理器。
  - `modules/`：`sam3_info_extractor.py`（SAM3 信息抽取）、`basic_shape_processor.py`（基础形状）、`icon_picture_processor.py`（图标+去背景 RMBG）、`xml_merger.py`（XML 合并）、`metric_evaluator.py`（保真度评估）、`refinement_processor.py`（人工修复）、`text/`（TextRestorer：OCR+公式）、`data_types.py`（`ProcessingContext`/`ElementInfo`/`LayerLevel`）。
  - `server_pa.py`：FastAPI 后端（`/convert` 端点），支撑 Web API。
  - `sam3_service/`：可选的 SAM3 HTTP 服务（多进程部署）。
  - `flowchart_text/`：独立 OCR 入口（`src/main.py`）。

## 四、应用场景与启发

- **场景**：想把论文/文档里的「图片版流程图、架构图、技术示意图、公式」变成可编辑 DrawIO；科研绘图复原；把截图归档成可维护的知识资产。
- **启发**：
  - 它把「图像→结构化矢量」拆成**分割（SAM3）+ 文本（OCR/公式）+ 空间合并（XML）**三段，且每段可独立替换模型（如换本地 VLM）——这种「感知与结构解耦」的管线，比端到端黑盒更易调参与落地。
  - `Pipeline` 用「懒加载单例 + 配置驱动」组织重模型，是本地 GPU 服务避免重复加载的经典写法，可直接借鉴到任何多模型推理服务。

## 五、源码深度解读（核心模块）

**1. `main.py`：配置驱动、懒加载单例的重建流水线**

```python
class Pipeline:
    def __init__(self, config=None):
        self.config = config or load_config()
        self._text_restorer = None; self._sam3_extractor = None
        self._icon_processor = None; self._shape_processor = None
        self._xml_merger = None; self._metric_evaluator = None
    @property
    def text_restorer(self):                 # OCR/公式步骤，依赖缺失时为 None
        if self._text_restorer is None and TextRestorer is not None:
            ocr_engine = (self.config.get("ocr") or {}).get("engine", "tesseract")
            self._text_restorer = TextRestorer(formula_engine="none", ocr_engine=ocr_engine)
        return self._text_restorer
    @property
    def sam3_extractor(self) -> Sam3InfoExtractor:
        if self._sam3_extractor is None:
            self._sam3_extractor = Sam3InfoExtractor()
        return self._sam3_extractor
    # icon_processor / shape_processor / xml_merger 同理——全部按需实例化
```

`from modules import (Sam3InfoExtractor, IconPictureProcessor, BasicShapeProcessor, XMLMerger, MetricEvaluator, RefinementProcessor, TextRestorer, ProcessingContext, ...)`——`Pipeline` 把每个重模型都做成「第一次用到才建」的属性，避免 CLI/服务启动时一次性占满显存。

**2. `modules/sam3_info_extractor.py`：`PromptGroup` 引导 SAM3 分割**

`PromptGroup` 枚举把「要分割的元素类别」做成提示组，配合 SAM3 的 mask decoder 做定向抽取——是「用结构化提示引导分割」而非盲分割的关键。`xml_merger.py` 则负责把 SAM3 的空间盒子与 OCR 的文本/公式按坐标对齐合并成合法 DrawIO XML。

**3. `server_pa.py`：FastAPI 暴露 `/convert`**

89 行的轻量 FastAPI 服务，把 `Pipeline` 包成 `POST /convert`（文件上传）与交互式 `/docs`，体现「CLI 内核 + HTTP 外壳」的双形态发布，便于集成到自己的工作流。

## 六、社区口碑

- 5.5k⭐、最近提交 2026-09-23（活跃）；北理工出品 + 在线 Demo，中文 AI 绘图圈关注度高。
- **许可证争议（重要）**：README 明确声明「Apache License 2.0，允许商用与二次开发」；但 GitHub 自动检测为 **AGPL-3.0**。两处冲突，引用/商用前必须以仓库实际 `LICENSE` 文件为准并谨慎核实。
- 官方提示：GitHub 仓库功能**落后于**在线服务（editbanana.net），开源版未必含最新特性。

## 七、竞品对比 + 核心研判

| 维度 | Edit-Banana | draw.io 自带导入 | 通用 OCR/截图转图 | 商业图表识别 SaaS |
|---|---|---|---|---|
| 图片→可编辑 DrawIO | ✅ SAM3+VLM | ❌ 需手动 | ⚠️ 丢结构 | ✅ |
| 公式→LaTeX | ✅ Pix2Text | ❌ | ❌ | ⚠️ |
| 本地可离线 | ✅（除 API VLM） | ✅ | ✅ | ❌ |
| 开源可审计 | ⚠️ 许可证冲突 | ✅ | 视工具 | ❌ |

**研判**：对「把图片版图表/公式变成可编辑资产」的需求，Edit-Banana 在保真度与可编辑性上明显优于「截图+OCR」常规方案，且学术团队背书、架构清晰（分割/文本/合并解耦）。风险：①许可证 Apache-2.0 与 AGPL-3.0 自相矛盾，商用合规必须先澄清；②强依赖 SAM3 权重与 CUDA GPU，部署门槛偏高；③GitHub 版落后于在线版。与用户的「文档/图表 AI 化」兴趣契合，其管线拆分思路值得借鉴。

## 八、关键文件路径速查

- 仓库根：`https://github.com/BIT-DataLab/Edit-Banana`；在线 Demo：`https://www.editbanana.net`
- 流水线入口：`main.py`、`server_pa.py`（FastAPI）
- 处理器：`modules/sam3_info_extractor.py`、`modules/basic_shape_processor.py`、`modules/icon_picture_processor.py`、`modules/xml_merger.py`、`modules/metric_evaluator.py`、`modules/refinement_processor.py`、`modules/text/`（TextRestorer）
- 数据/类型：`modules/data_types.py`（`ProcessingContext`/`ElementInfo`/`LayerLevel`）
- 模型与部署：`sam3/`、`sam3_service/`、`scripts/setup_sam3.sh`、`scripts/merge_xml.py`、`config/config.yaml.example`
