# Roboflow Supervision 深度调研报告

> 仓库: [roboflow/supervision](https://github.com/roboflow/supervision)
> 调研日期: 2026-06-30
> 数据来源: GitHub API、官方源码、知乎/CSDN/阿里云/腾讯云开发者社区、Text Matrix、The Menon Lab Blog、GitTrending

---

## 1. 一句话定位

Supervision 是 Roboflow 推出的**模型无关（Model-Agnostic）的计算机视觉后处理工具箱**，不负责模型推理，而是统一接管"模型输出之后"的整个后处理链路 —— 标准化检测结果、可视化标注、目标追踪、区域计数、数据集转换、指标评估 —— 将 CV 工程中的重复胶水代码收敛到一处。

---

## 2. 项目亮点（5 条差异化价值）

### 2.1 统一的 `sv.Detections` 中间表示

这是 supervision 的架构核心。无论模型来自 Ultralytics、Transformers、Detectron2、MMDetection 还是 Roboflow Inference，全部通过 Connector 模式转换为统一的 `sv.Detections` 数据类（`detection/core.py` 第 47 行）。下游的标注器、区域工具、追踪器只认这个统一接口，切换模型无须修改下游代码。

### 2.2 20+ 开箱即用的可组合标注器

从基础 `BoxAnnotator`、`MaskAnnotator` 到高级的 `HeatMapAnnotator`、`TraceAnnotator`、`RoundBoxAnnotator`、`IconAnnotator` 等。标注器设计为可组合 —— 链式调用叠加多种视觉效果。对比手写 `cv2.rectangle` + `cv2.putText` 的样板代码，标注器封装了标签防重叠（smart_position）、边界裁剪（snap_boxes）、智能颜色映射（ColorLookup）等大量细节（`annotators/core.py` 第 33-87 行）。

### 2.3 区域计数与穿线计数的业务级抽象

`PolygonZone` 和 `LineZone` 将复杂的几何计算（点-多边形包含判断、跨线方向判定、抖动过滤）封装为声明式 API。这在工业安防、交通监控、人流统计等场景中直接对应业务需求，避免了每次重写几何判断逻辑。

### 2.4 内置 ByteTrack 追踪与推理切片

- **ByteTrack**：已集成高性能多目标追踪器（`tracker/byte_tracker/core.py`），支持 track_activation_threshold、lost_track_buffer 等参数调优。
- **InferenceSlicer**：封装大图切片推理的完整流程 —— 切图、重叠区域处理、边界去重、坐标还原、batch 推理（`detection/tools/inference_slicer.py`）。

### 2.5 数据集格式转换的"通用语言"

支持 COCO、YOLO、Pascal VOC 三种主流标注格式的加载、保存、拆分、合并。单次调用即可实现 `from_yolo().as_coco()` 的链式转换，内置类别名自动去重和索引重映射（`dataset/core.py` 第 32-80 行）。

---

## 3. 项目架构全景

### 3.1 目录结构

```
supervision/
├── __init__.py                  # 包入口，统一导出
├── config.py                    # 全局常量（CLASS_NAME_DATA_FIELD, ORIENTED_BOX_COORDINATES）
├── detection/
│   ├── core.py                  # Detections 核心数据类 + 多模型 Connector
│   ├── line_zone.py             # 穿线计数 LineZone + LineZoneAnnotator
│   ├── vlm.py                   # VLM（视觉语言模型）集成
│   ├── tools/
│   │   ├── inference_slicer.py  # 大图切片推理
│   │   ├── polygon_zone.py      # 多边形区域过滤
│   │   ├── smoother.py          # 检测平滑器
│   │   ├── csv_sink.py          # CSV 导出
│   │   └── json_sink.py         # JSON 导出
│   └── utils/
│       ├── boxes.py             # 框坐标变换
│       ├── converters.py        # mask/polygon/xyxy/xcycwh 互转
│       ├── iou_and_nms.py       # IoU、NMS、OverlapFilter
│       ├── masks.py             # 掩码操作
│       ├── polygons.py          # 多边形操作
│       └── vlms.py              # VLM 解析辅助
├── annotators/
│   ├── core.py                  # 20+ 标注器实现
│   ├── base.py                  # BaseAnnotator 抽象基类
│   └── utils.py                 # ColorLookup、Trace、标签布局
├── classification/
│   └── core.py                  # Classifications 数据类（分类任务）
├── key_points/
│   └── core.py                  # KeyPoints 数据类（姿态估计）
├── tracker/
│   └── byte_tracker/
│       ├── core.py              # ByteTrack 主逻辑
│       ├── kalman_filter.py     # 卡尔曼滤波
│       ├── matching.py          # 匹配算法
│       ├── single_object_track.py # STrack 单目标跟踪
│       └── utils.py             # IdCounter
├── dataset/
│   ├── core.py                  # DetectionDataset / BaseDataset
│   ├── utils.py                 # 数据集工具（train_test_split, mask_to_rle 等）
│   └── formats/
│       ├── coco.py              # COCO 格式
│       ├── pascal_voc.py        # Pascal VOC 格式
│       └── yolo.py              # YOLO 格式
├── metrics/
│   ├── core.py                  # Metric 抽象基类 + MetricTarget/AveragingMethod
│   ├── detection.py             # ConfusionMatrix + MeanAveragePrecision
│   ├── f1_score.py / precision.py / recall.py / mean_average_precision.py / mean_average_recall.py
│   └── utils/
├── draw/
│   ├── color.py                 # Color / ColorPalette
│   ├── base.py                  # ImageType 类型定义
│   └── utils.py                 # 底层绘图函数
├── geometry/
│   └── core.py                  # Point / Position / Rect 几何基元
├── utils/
│   ├── video.py                 # VideoInfo / VideoSink / process_video
│   ├── image.py                 # ImageSink / crop / resize / overlay
│   ├── file.py / conversion.py / iterables.py / notebook.py / internal.py
└── validators/
    └── __init__.py              # 字段校验
```

### 3.2 设计哲学

1. **模型无关**：Supervision 不依赖任何模型框架，只关心统一的数据结构 `sv.Detections`
2. **声明式 API**：标注器是纯声明式的 —— 初始化时配置，调用 `annotate` 时执行
3. **NumPy 原生**：所有数据字段用 `np.ndarray`，索引和过滤直接使用 NumPy 布尔索引
4. **可组合**：标注器链式调用、检测器-追踪器-区域工具流水线

### 3.3 技术栈依赖

| 依赖 | 用途 | 版本要求 | 是否可选 |
|------|------|----------|----------|
| numpy | 核心数据容器 | >=1.21.2 | 必选 |
| opencv-python | 图像/视频 I/O 与标注渲染 | >=4.5.5 | 必选 |
| matplotlib | 颜色与可视化 | >=3.6 | 必选 |
| pillow | PIL 图像支持 | >=9.4 | 必选 |
| scipy | 曲线插值（标注器） | >=1.10 | 必选 |
| requests | 资产下载 | >=2.26 | 必选 |
| pyyaml | YAML 解析 | >=5.3 | 必选 |
| tqdm | 进度条 | >=4.62.3 | 必选 |
| defusedxml | 安全 XML 解析 | >=0.7.1 | 必选 |
| pydeprecate | 废弃 API 管理 | >=0.9 | 必选 |
| rasterio | GeoTIFF 支持 | >=1.3 | 可选 |
| pandas | 指标结果表格化 | >=2 | 可选 |

**关键发现**：依赖非常轻量，无任何深度学习框架（PyTorch/TensorFlow）的硬依赖。这意味着 Supervision 的安全漏洞面极小，CI/CD 也快。

---

## 4. 应用场景与启发

### 4.1 什么场景用 Supervision

| 场景 | 使用组件 | 典型用户 |
|------|---------|---------|
| 视频监控人流/车流统计 | `LineZone` + `ByteTrack` | 安防集成商、智慧城市 |
| 工业质检的检测结果可视化 | `BoxAnnotator` + `LabelAnnotator` | 制造业 AI 团队 |
| 遥感/航拍大图小目标检测 | `InferenceSlicer` | 地理空间分析 |
| 多模型对比评估 | `sv.Detections.from_*` + `MeanAveragePrecision` | CV 研究员 |
| 数据集格式迁移 | `DetectionDataset.from_coco().as_yolo()` | 算法工程师 |
| 行为分析（姿态+区域） | `KeyPoints` + `PolygonZone` | 体育分析、医疗康复 |
| AI 内容审核可视化 | `BlurAnnotator` + `PixelateAnnotator` | 内容安全 |

### 4.2 对同类需求的启发

1. **胶水代码的工厂化**：Supervision 证明了"模型输出后的胶水代码"本身可以成为一个独立的高价值开源项目。许多 CV 项目 80% 的工程代码在模型之外，这些重复劳动中存在着"标准化"的巨大机会。
2. **数据结构是架构的灵魂**：`sv.Detections` 这个统一数据类的设计让整个库的扩展性极好 —— 新增模型来源只需写一个 Connector，新增功能只需理解 Detections。对比很多 CV 工具"上来就封装模型"，Supervision 选择了"封装数据"的路线，这是更优雅的解耦。
3. **文档即代码**：源码中每个类和方法都有完整的 Google 风格 Docstring，包含类型注解、参数说明、完整代码示例。这使新贡献者上手极快 —— 如 GitTrending 文章提到"首次贡献者的上手体验让我大开眼界"。

---

## 5. 核心源码解读

### 5.1 `sv.Detections` —— 整个库的数据基石（`detection/core.py`）

```python
@dataclass
class Detections:
    xyxy: np.ndarray                       # (n, 4) 检测框 [x1,y1,x2,y2]
    mask: np.ndarray | None = None         # (n, H, W) 分割掩码
    confidence: np.ndarray | None = None   # (n,) 置信度
    class_id: np.ndarray | None = None     # (n,) 类别 ID
    tracker_id: np.ndarray | None = None   # (n,) 追踪 ID
    data: dict[str, np.ndarray | list] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
```

- 使用 `dataclass` 而非自定义类，干净无模板
- 字段均为 `Optional[np.ndarray]`，适应检测/分割不同任务
- `data` 字典用于扩展字段（类别名、VLM 结果），保持核心简洁
- 通过 `__post_init__` 调用 `validate_detections_fields` 做输入校验（`validators/__init__.py`）

### 5.2 Connector 模式 —— 适配多种模型源

```python
@classmethod
def from_ultralytics(cls, ultralytics_results) -> Detections:
    if hasattr(ultralytics_results, "obb") and ultralytics_results.obb is not None:
        # OBB (Oriented Bounding Box) 处理
        return cls(
            xyxy=ultralytics_results.obb.xyxy.cpu().numpy(),
            confidence=ultralytics_results.obb.conf.cpu().numpy(),
            class_id=class_id,
            data={ORIENTED_BOX_COORDINATES: oriented_box_coordinates, ...}
        )
    if hasattr(ultralytics_results, "boxes") and ultralytics_results.boxes is None:
        # 仅有 mask（如 SAM）的情况
        masks = extract_ultralytics_masks(ultralytics_results)
        return cls(xyxy=mask_to_xyxy(masks), mask=masks, class_id=...)
    # 标准检测结果
    return cls(xyxy=..., confidence=..., class_id=..., mask=..., data=...)
```

每个 Connector 都处理了对应模型的输出格式差异，包括：
- CPU/GPU 张量转换（`.cpu().numpy()`）
- 空检测的 `cls.empty()` 优雅处理
- 不同模型的特有数据类型（OBB、mask-only、分类）

### 5.3 标注器的智能标签布局（`annotators/core.py`）

```python
class _BaseLabelAnnotator(BaseAnnotator):
    def _adjust_labels_in_frame(self, resolution_wh, labels, label_properties):
        # 1. 标签框不越界
        adjusted_properties[:, :4] = snap_boxes(_, resolution_wh)
        # 2. 多重标签不重叠（spread out 算法）
        if len(labels) > 1:
            spread_boxes = spread_out_boxes(boxes)
            adjusted_properties[:, :4] = spread_boxes
        # 3. 展开后再次检查边界
        adjusted_properties[:, :4] = snap_boxes(_, resolution_wh)
        return adjusted_properties
```

三层防碰撞策略：先 snap 到画布内 → spread_out 避免重叠 → 再 snap。这是手写 `cv2.putText` 绝对不会处理的细节。

### 5.4 ByteTrack 追踪核心（`tracker/byte_tracker/core.py`）

```python
class ByteTrack:
    def update_with_detections(self, detections: Detections) -> Detections:
        tensors = np.hstack((detections.xyxy, detections.confidence[:, np.newaxis]))
        tracks = self.update_with_tensors(tensors=tensors)
        if len(tracks) > 0:
            # 匈牙利算法匹配检测与轨迹
            ious = box_iou_batch(detection_bounding_boxes, track_bounding_boxes)
            matches, _, _ = matching.linear_assignment(1 - ious, 0.5)
            detections.tracker_id = np.full(len(detections), -1, dtype=int)
            for i_detection, i_track in matches:
                detections.tracker_id[i_detection] = tracks[i_track].external_track_id
            return detections[detections.tracker_id != -1]
        return Detections.empty()
```

- 输入统一为 `sv.Detections`，输出也是 `sv.Detections`，保持了数据流的一贯性
- 使用 `linear_assignment`（匈牙利算法）+ `IoU` 做匹配
- 支持参数调优：track_activation_threshold（激活门槛）、lost_track_buffer（丢失缓冲帧）、minimum_matching_threshold（匹配阈值）

### 5.5 视频处理流水线（`utils/video.py`）

```python
def process_video(source_path, target_path, callback):
    video_info = VideoInfo.from_video_path(source_path)
    with VideoSink(target_path=target_path, video_info=video_info) as sink:
        for index, frame in enumerate(get_video_frames_generator(source_path)):
            annotated_frame = callback(frame, index)
            sink.write_frame(frame=annotated_frame)
```

简洁的 callback 模式：用户只需写 `callback(frame, index) -> frame` 函数，框架负责帧的读取和写出。这种模式降低了视频处理的心理门槛。

---

## 6. 架构决策与设计哲学

### 6.1 关键架构决策

| 决策 | 选型 | 理由 |
|------|------|------|
| 数据结构 | `dataclass` + `np.ndarray` | 轻量、向量化、无序列化开销 |
| 模型适配 | Connector 模式（`from_*` classmethod） | 每个模型源独立处理格式差异，不污染核心类 |
| 标注渲染 | 独立 Annotator 类体系 | 每个 Annotator 单一职责、可组合、可测试 |
| 追踪状态管理 | 内存中的状态列表（tracked/lost/removed） | 简单直接，适合单视频流处理 |
| 视频处理 | 回调 + 逐帧读写的同步模式 | 保持 API 简洁，不做流式/并行的过度设计 |
| 废弃 API | `pydeprecate` 库管理 | 向后兼容的同时逐步推进 API 演进 |

### 6.2 设计哲学

1. **信任 NumPy**：整个库以 `np.ndarray` 为核心数据类型，过滤、排序、索引全部用 NumPy 向量化操作，不引入 pandas 或 torch 作为硬依赖。
2. **约定优于配置**：标注器默认颜色从 ColorPalette.DEFAULT 自动循环，ColorLookup 默认按 CLASS 映射。80% 场景无需显式配置。
3. **渐进增强**：项目先做强检测后处理（Detections + Annotators），再扩展追踪、区域计数、数据集、VLM 等。不一步到位，但每一步都基于已有的统一接口。
4. **测试金字塔**：`test/` 目录覆盖了每个核心模块的单元测试，使用 pytest + doctest，且 CI/CD 通过 `.github/workflows/uv-test.yml` 自动运行。`pyproject.toml` 中 TOML 配置了 ruff、mypy（strict）、codespell、pytest 等全套质量工具。

### 6.3 独家发现：废弃 API 的版本策略

代码中 `keypoint/core.py` 和 `key_points/core.py` 同时存在，前者在 0.27.0 标记为废弃，提示在 0.30.0 移除。同样 `ByteTrack` 在 0.28.0 标记为 deprecated，计划迁移到独立的 `trackers` 包。这说明 Supervision 在 API 演进上采用**双版本共存 + 明确移除时间线**的策略，这是成熟开源项目的标志。

---

## 7. 全网口碑画像

### 7.1 中文社区反馈（5 条）

**来源 1：知乎专栏 [AI开源]（2024-08-24）**
- 评价："一款出色的 Python 计算机视觉低代码工具，其设计初衷在于为用户提供一个便捷且高效的接口"
- 亮点：低代码、数据集处理方便、标注器丰富
- [来源](https://zhuanlan.zhihu.com/p/716262011)

**来源 2：腾讯云开发者社区（2025-08-22）**
- 评价："GitHub 超 30,000+ star 背后，让你告别重复造轮子"
- 对比结论：Supervision 在多模型兼容、区域计数工具、可视化注释工具、跟踪组件支持、数据集工具支持五个维度全面优于手写逻辑
- [来源](https://cloud.tencent.com/developer/article/2558067)

**来源 3：阿里云开发者社区（2025-08-22）**
- 评价："本文详细介绍广受欢迎的视觉工具库 Supervision"
- 核心观点：可与 YOLO、Detectron2、Transformers 等模型无缝对接，适用于视频分析、物体追踪、区域计数等场景
- [来源](https://developer.aliyun.com/article/1678671)

**来源 4：CSDN 博客（2025-05-14）**
- 评价："Supervision 是面向计算机视觉工程实践推出的全流程开发工具库"
- 亮点：覆盖从数据集预处理、图像增强、推理结果解析到可视化输出的完整工作链
- [来源](https://blog.csdn.net/sinat_28461591/article/details/147939286)

**来源 5：知乎"告别重复造轮子"深度解析（2026-04-02）**
- 评价："它不是一个模型，而是一个模型无关的工具箱，旨在把复杂的 CV 流程封装成几行优雅的 Python 代码"
- 亮点：强调 VLM 集成（零样本检测器）、Detections 标准化、标注器智能避让
- 独家提示：2026 年 YOLO26 已经可用，Supervision 紧跟最新模型
- [来源](https://zhuanlan.zhihu.com/p/2022957903376647427)

### 7.2 英文社区反馈（3 条）

**来源 6：The Menon Lab Blog（2026-02-28）**
- 将 Supervision 定位为"Post-Processing Layer"
- 评价："Supervision doesn't run models — it processes their output"
- 与 x.infer、FiftyOne、OpenVINO、CVZone 等工具形成互补关系
- [来源](https://themenonlab.blog/blog/computer-vision-python-toolkit-comparison)

**来源 7：Text Matrix 深度评测（2026-05-14）**
- 评价："计算机视觉工具链的瑞士军刀"
- 独家分析：详细对比了 torchvision/detectron2/Supervision 的后处理能力，指出 Supervision 的差异化在于模型无关
- 提示 0.28.0 追踪接口变更的注意事项
- [来源](https://txtmix.com/posts/tech/supervision-cv-toolkit-guide/)

**来源 8：GitTrending 首次贡献者视角（2026-06-18）**
- 评价："Supervision 树立了计算机视觉工具库的新标杆"
- 从贡献者视角评价代码质量：详细的类型提示、完整 Docstrings、强大的单元测试
- 直接对比传统 OpenCV 样板代码与 Supervision 的声明式 API
- [来源](https://www.gittrending.com/article/beyond-boilerplate-opencv-why-supervision-is-the-new-standard-for-computer-vision-pipelines-zh)

### 7.3 负面与局限性 (独家整理)

- **纯 Python 后处理瓶颈**：Text Matrix 指出，单帧检测目标数量极大（数千个框）时，标注器绘制开销会显著上升
- **同步视频处理**：`process_video` 逐帧串行处理，没有内置并行或流式处理能力（Text Matrix）
- **追踪器废弃风险**：ByteTrack 在 0.28.0 标记 deprecated，用户需要关注新的 trackers 包（来源 7）
- **模型依赖**：Supervision 本身不做推理，仍需依赖外部模型框架（多个来源均指出）

---

## 8. 竞品对比

### 8.1 对比矩阵

| 维度 | Supervision | OpenCV + 手写逻辑 | FiftyOne | Detectron2 | CVZone |
|------|------------|------------------|----------|------------|--------|
| **定位** | 模型无关后处理工具箱 | 通用 CV 库 | 数据集探索与调试平台 | 端到端检测训练框架 | 初学者快速原型 |
| **模型适配** | 15+ 框架 Connector | 需手写 | 加载已有结果 | 绑定 Detectron2 | 绑定 MediaPipe |
| **标注器数量** | 20+ 可组合 | cv2 原生基础 | 基础可视化 | Visualizer 绑定 | cornerRect 等简易 |
| **区域计数** | PolygonZone + LineZone 内置 | 手写几何判断 | 无内置 | 无内置 | 无 |
| **目标追踪** | ByteTrack 集成 | 自己实现 | 无内置 | 无内置 | HandDetector 等 |
| **数据集转换** | COCO/YOLO/VOC 互转 | 手写解析器 | 加载+可视化 | 注册表格式 | 无 |
| **指标评估** | mAP/Precision/Recall/F1/ConfusionMatrix | 手写 | 内置评估器 | 内置 | 无 |
| **学习曲线** | 低（pip install + 5行代码） | 中 | 中高（需理解 App 界面） | 高（需理解 config 系统） | 极低 |
| **生产可用** | 是（类型注解 + 单元测试 + CI/CD） | 取决于实现 | 是（企业级） | 是（FB 出品） | 否 |
| **GitHub Stars** | 45,863 | N/A | 9,000+ | 30,000+ | 4,000+ |
| **许可证** | MIT | BSD | Apache 2.0 | Apache 2.0 | MIT |

### 8.2 选择建议

- **选 Supervision 当**：你需要的是模型输出后的标准化处理（可视化+追踪+区域计数+数据集转换），且未来可能换模型
- **选 OpenCV 当**：你需要的是底层图像处理（滤波、形态学操作、特征匹配），而非 CV 后处理管道
- **选 FiftyOne 当**：你需要的是交互式数据集探索、标注质量审核、模型失败的根因分析
- **选 Detectron2 当**：你需要训练和部署自家的检测模型，且愿意绑定 Facebook 生态
- **选 CVZone 当**：你是初学者，只想用 5 行代码跑一个手势识别 demo

---

## 9. 核心研判

### 9.1 核心优势

1. **模型无关性是最佳解耦**：Supervision 不绑定任何模型框架，这使其在一个模型快速迭代的时代（YOLOv8→v10→v26、DETR、SAM、RF-DETR...）具有天然的生命力。用户不会因为换模型而需要重写后处理代码。
2. **API 设计的"苹果级别"**：多个独立评测（Text Matrix、GitTrending、知乎深度解析）一致赞扬其 API 优雅性。声明式标注器、链式调用、NumPy 原生数据，这些设计选择使学习成本极低。
3. **Roboflow 生态加持**：与 Autodistill（自动标注）、Inference（推理服务器）、Maestro（多模态提示）形成闭环。虽然 Supervision 可独立使用，但融入生态后效率更高。

### 9.2 风险与局限

1. **Python 性能天花板**：纯 Python + NumPy 实现，无法利用 GPU 加速后处理。在高通量实时场景（>30 FPS、数千框）可能成为瓶颈。
2. **追踪器接口迁移风险**：ByteTrack 在 0.28.0 标 deprecation，用户需要关注新 trackers 包的稳定性。
3. **Roboflow 公司产品风险**：作为 Roboflow 旗下开源项目，未来可能面临商业化的优先级调整。目前 MIT 许可证不可撤销，但社区资源和维护方向可能受母公司影响。
4. **不参与训练**：如果想做端到端的训练-评估，需要额外搭配训练框架。

### 9.3 适用场景

- **最适合**：视频分析管道（追踪+区域计数+可视化）、多模型切换的研发项目、需要数据集格式转换的工程化团队
- **不适合**：底层图像处理、端到端模型训练、对后处理延迟有极端要求的场景（<1ms）

### 9.4 趋势判断

- Supervision 正在从"检测后处理工具"演变为"全类型 CV 后处理平台"—— 2026 年的版本已深度集成 VLM（视觉语言模型）、Zero-shot 检测器、OBB（旋转框）支持
- 45,863⭐ 的规模使其已经成为 CV 开源生态中的基础设施级项目，类似 lodash 对 JavaScript 的影响
- 预计后续方向：更丰富的追踪器支持（替换 ByteTrack）、实时流处理支持、更多数据集格式、更完善的 VLM 集成

---

## 10. 关键文件路径速查

| 文件 | 核心内容 | 行数范围 |
|------|---------|---------|
| `supervision/__init__.py` | 公共 API 导出（30+ 类） | 全部 |
| `supervision/detection/core.py` | `Detections` 数据类 + 全部 Connector | 1-450+ |
| `supervision/annotators/core.py` | 20+ 标注器（Box/Mask/Label/Trace/HeatMap 等） | 1-800+ |
| `supervision/tracker/byte_tracker/core.py` | ByteTrack 追踪主逻辑 | 1-200+ |
| `supervision/detection/line_zone.py` | 穿线计数 LineZone + Annotator | 1-200+ |
| `supervision/detection/tools/polygon_zone.py` | 多边形区域 PolygonZone | 1-150+ |
| `supervision/detection/tools/inference_slicer.py` | 大图切片推理 | 1-200+ |
| `supervision/dataset/core.py` | DetectionDataset 加载/拆分/合并/保存 | 1-300+ |
| `supervision/metrics/detection.py` | ConfusionMatrix + MeanAveragePrecision | 1-300+ |
| `supervision/utils/video.py` | VideoInfo + VideoSink + process_video | 1-200+ |
| `supervision/config.py` | 全局常量（仅 2 行） | 全部 |
| `supervision/draw/color.py` | Color + ColorPalette | 1-200+ |
| `test/detection/test_core.py` | Detections 核心单元测试 | 全部 |
| `pyproject.toml` | 项目元数据、依赖、工具配置（ruff/mypy/pytest） | 全部 |

---

## 附：调研数据源汇总

| 来源类型 | 来源 | 日期 |
|---------|------|------|
| GitHub API | 仓库元数据（Stars/Issues/Topics） | 2026-06-30 |
| 源码分析 | `supervision/` 全目录 | 2026-06-30 |
| 中文博客 | 知乎专栏（AI开源） | 2024-08-24 |
| 中文博客 | 腾讯云开发者社区 | 2025-08-22 |
| 中文博客 | 阿里云开发者社区 | 2025-08-22 |
| 中文博客 | CSDN 技术博客 | 2025-05-14 |
| 中文深度评测 | 知乎"告别重复造轮子" | 2026-04-02 |
| 英文深度评测 | Text Matrix | 2026-05-14 |
| 英文对比分析 | The Menon Lab Blog | 2026-02-28 |
| 英文贡献者视角 | GitTrending | 2026-06-18 |
| 中文评测 | 博客园（氿痕） | 2024-10-23 |
| 中文评测 | xugj520.cn 高效码农 | 2025-07 |
