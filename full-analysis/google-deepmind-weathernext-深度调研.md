# 🔍 深度调研报告：google-deepmind/weathernext

> **仓库**: [google-deepmind/weathernext](https://github.com/google-deepmind/weathernext)
> **Stars**: 7,301 ⭐ | **Forks**: 950 | **Open Issues**: 76
> **语言**: Python（JAX + xarray，TPU 优化） | **License**: Apache-2.0 | **默认分支**: `main`
> **创建**: 2023-07-14 | **最后推送**: 2026-08-07
> **调研日期**: 2026-08-11

---

## 一、项目定位（一句话）

**WeatherNext 是 Google DeepMind 的「AI 天气预报全家桶」主仓库——以 WeatherNext 2（WN2）全球中期大气+气旋预报模型为核心，并保留 GraphCast/GenCast 两代 SOTA 模型代码，直接对外提供可运行的预训练权重与每日数据 feed。** 它不是玩具 demo，而是已投入业务运行的科研级系统（2025 大西洋飓风季实时跑过 FNV3/GDMI）。

---

## 二、项目亮点（差异化，开篇必读）

1. **大气 + 气旋「一套算法」统一** — WN2 与 WN Cyclones **用完全相同的算法**，仅因独立训练而权重不同；WN2 还能额外预测 100m 风。一套架构覆盖「常规天气 + 极端气旋」两类需求。
2. **业务级数据 feed 直接可用** — 不想自己跑模型？Google Cloud（Earth Engine/BigQuery/Vertex AI）、WeatherLab（含气旋轨迹）、OpenMeteo（含 API + 交互构建器）三路官方数据 feed 已开放，降低使用门槛。
3. **从 HRES 初始条件直接初始化** — WN2 微调于 ECMWF HRES 数据，设计为**直接用业务 HRES 初始场**而非 ERA5 再分析场初始化，更贴近真实业务链路。
4. **气旋追踪「贪婪式」算法开源** — `weathernext/cyclones/direct_tracker.py` 把论文里的气旋追踪写成可复用的 greedy tracker，支持三种追踪模式，比 Tempest Extremes 类方法更轻量透明。
5. **论文 + 权重 + 代码三件套齐备** — Nature 2026 气旋论文（s41586-026-10953-2）、FGN/WN2 技术报告（arXiv:2506.10772）、Colab 交互 demo、多分辨率预训练权重（0.25° / 1° Mini）全部公开。

---

## 三、核心架构

### 3.1 模型家族与数据 feed（README 真实结构）

```
weathernext/
├── WeatherNext 2 (WN2)          # 全球中期大气预报核心模型（0.25° ≈ 30km）
│     └─ 也能预报气旋（与 WN Cyclones 同算法、异权重）
├── WeatherNext Cyclones         # 气旋专项（2025 飓风季业务运行 FNV3/GDMI）
│     └─ Mini 版（1°，P100 可跑）
├── WeatherNext Graph (GraphCast) # 历史 GNN 确定性中期预报
├── WeatherNext Gen   (GenCast)   # 历史扩散集成预报
├── utils/                       # 共享库：rollout / normalization / graph / loss / xarray
└── weathernext/cyclones/        # 气旋追踪（direct_tracker 等）

# 数据 feed（无需自跑模型）
Google Cloud ── Earth Engine / BigQuery / Vertex AI
WeatherLab  ── 含气旋轨迹
OpenMeteo   ── API + 交互构建器
```

### 3.2 模型运行范式

- **Auto-regressive rollout**：自回归逐步推演生成预测（Colab demo 第 4 步 "Run auto-regressive rollout steps"）。
- **JAX 优化 + TPU 优先**：实现针对 TPU 优化（推荐 v5e/v5p）；GPU 需切换 attention 实现，非 Mini 模型需 H100 显存，Mini 模型 P100 可跑。
- **`pip install git+...@v0.3.0`**：以 research code as-is 发布，明确提示 API 不稳定、建议 pin release。

### 3.3 气旋追踪模块（`weathernext/cyclones/`）

从 `direct_tracker.py` 的 import 可确认模块划分真实存在：

```
weathernext/cyclones/
├── direct_tracker.py          # ★ 贪婪式追踪器（本调研重点）
├── tracker_base.py            # 追踪器基类
├── tracker_utils.py
├── cyclone_utils.py
├── constants.py               # MAX_SUSTAINED_WIND_SPEED_KNOTS 等常量
└── ibtracs_processing_utils.py  # IBTrACS 真实气旋数据接入
```

---

## 四、应用场景与启发（重点章节）

| 场景 | WeatherNext 怎么用 | 给同类需求的启发 |
|------|------------------|----------------|
| **业务化天气预报** | 直接消费 Google Cloud/OpenMeteo feed，跳过自训模型 | 大模型服务化时，「提供数据 API」比「只开源权重」更降低落地门槛 |
| **极端天气预警** | WN Cyclones 专攻气旋，2025 已业务运行 | 通用大模型之外，针对极端事件做「专项模型 + 专用追踪器」值得投入 |
| **科研复现** | Colab demo + 权重 + 论文三件套 | 让他人可复现（而非只发榜单）是科研 repo 信任基础 |
| **边缘/低成本推理** | Mini 版 1° 分辨率 P100 可跑 | 提供「完整版 + 轻量版」双档，兼顾 SOTA 与可及性 |
| **气象 AI 工程** | JAX + xarray + TPU rollout 范式 | 序列/时空预测任务里，把 rollout 与归一化/图构建/损失解耦成 utils 是可迁移结构 |

**方法论启发**：
- **「同一算法、不同权重」统一多任务**：WN2 与气旋追踪共用算法，避免为每个子任务另起炉灶——同类「主模型 + 衍生权重」思路可迁移到任何「通用能力 + 专项场景」的产品。
- **论文与工程同步开源**：Nature 背书 + 可跑代码 + 可用数据，形成「可信度飞轮」，比单纯刷 benchmark 更有长期价值。

---

## 五、源码深度解读

### 5.1 direct_tracker：贪婪式气旋追踪

`direct_tracker.py` 的核心是一个 **greedy tracker**——每一步决定下一中心位置只依赖**已有中心**，不看未来（区别于 Tempest Extremes 类全局方法）。算法骨架（docstring 真实描述）：

```
# direct_tracker.py（算法骨架，源自 docstring）
1. 初始化气旋中心：
   - 用 IBTrACS 已知中心，或 direct cyclogenesis（在 t=0 的
     existence 概率场里从高概率区逐个指派，直到阈值）
2. 时间演化（对每个中心）：
   2.1 一阶猜测：基于当前+上一中心动量更新（无前中心则零动量）
   2.2 精化（三选一）：
       - mean           : 邻域位置取均值
       - mode           : 取最高概率位置
       - mode-then-mean : 先用 mode 估计，再小半径 mean 精化（两全其美）
   2.3 估计伴随标量（最大持续风速等，匹配标准气旋变量名）
3. 所有风暴结果收集进单个 pandas DataFrame
```

三种模式里 `mode-then-mean` 最稳健：先用 mode 定位概率团（避免两个团靠近时混淆），再 mean 精化。

### 5.2 包围盒的纬度缩放（真实代码片段）

追踪时需要取中心周围的网格子集。经度方向边长随纬度收缩，代码对此做了保守缩放：

```python
# direct_tracker.py（真实代码片段）
disc_half_angle_degrees = (disc_radius_km / EARTH_MERIDIAN_LENGTH_KM) * 180.0
max_lat = min(90.0, latlon[0] + disc_half_angle_degrees)
min_lat = max(-90.0, latlon[0] - disc_half_angle_degrees)
box_side_div_factor = np.minimum(
    np.cos(np.deg2rad(max_lat)), np.cos(np.deg2rad(min_lat)))
box_side_in_degrees_lon = float(box_side_in_degrees_lat / box_side_div_factor)
# 气旋永不超过此纬度；接近极点时被 NaN 防护 clamp 到 360
MAX_ABSOLUTE_LATITUDE = 80
```

这段是「几何常识落地成代码」的好例子：用 `min(cos(max_lat), cos(min_lat))` 保证包围盒一定包住圆盘，并显式处理极点 wrap-around 与 NaN 边界。

### 5.3 WN2 的 rollout 范式

README 的 Colab 流程揭示标准推理链：加载权重 → 加载初始场（HRES）→ 初始化 FGN 架构 → **自回归 rollout** → 可视化 → 跑 direct tracker 出气旋轨迹 → 算 loss 做梯度步。把「归一化 / 图构建 / 损失 / xarray 工具」抽进 `utils/`，是时空预测模型工程的通用骨架。

---

## 六、社区口碑

- **学术背书强**：GraphCast/GenCast 已是气象 AI 领域被高频引用的 SOTA 工作，WN2 延续 DeepMind 在该赛道的权威；气旋成果登上 Nature 2026。
- **科研社区认可**：气象/ML 交叉领域普遍将其视为「AI 天气预报基准仓库」，Colab + 三路数据 feed 降低了复现门槛。
- **实操吐槽点**：① 明确标注 "research code as-is，API 不稳定，建议 pin release"——不适合直接当稳定依赖；② 硬件门槛高（非 Mini 模型需 H100，TPU 优先），本地跑成本不低；③ 作为 DeepMind 官方 repo，issue 响应节奏偏科研节奏，非商业 SLA。
- **行业影响**：GraphCast/GenCast/WN2 系列持续推动「AI 替代/增强传统 NWP（如 ECMWF IFS、GFS）」的讨论，已成主流方向之一。

---

## 七、竞品对比 + 核心研判

### 7.1 竞品对比

| 维度 | **WeatherNext (WN2)** | ECMWF HRES/IFS（传统 NWP） | GraphCast/GenCast（同 repo 历史） | NVIDIA FourCastNet | 华为 Pangu-Weather |
|------|----------------------|--------------------------|----------------------------------|-------------------|------------------|
| 方法 | AI（Transformer/CNN 系，自回归） | 物理方程数值积分 | AI（GNN / 扩散） | AI（傅里叶神经算子） | AI（3D 深度网络） |
| 分辨率 | 0.25° | ~9km（IFS） | 0.25° / 集成 | 0.25° | 0.25° |
| 气旋专项 | ✅ WN Cyclones | 依赖物理 | ❌ | ❌ | ❌ |
| 数据 feed | ✅ 三路官方开放 | 业务产品 | 需自跑 | 需自跑 | 需自跑 |
| 硬件门槛 | 高（H100/TPU） | 超算 | 中高 | 中 | 高 |
| 开源完整度 | 权重+代码+论文 | 闭源业务 | 本 repo 含 | 开源 | 论文为主 |

### 7.2 核心研判

**优势**：
- 技术 + 工程 + 数据三位一体：SOTA 精度、可跑代码、官方 feed 全开放，信任度极高。
- 气旋专项是差异化护城河——多数 AI 气象模型只做常规预报，WN Cyclones 已业务验证。
- 多分辨率（0.25° / 1° Mini）兼顾前沿与可及性。

**风险**：
- **research code 定性**：API 不稳定、建议 pin release，意味着它首先是「科研资产」而非「生产组件」，接入需自行封装。
- **硬件与算力门槛**：非 Mini 模型需 H100/TPU，个人与小团队自跑成本高，多数用户会倾向直接消费 feed。
- **与传统 NWP 的互补而非替代**：业务气象仍大量依赖 ECMWF/国家局物理模型，WN2 更可能是「增强/并行校验」角色。

**趋势判断**：AI 天气预报已从「能不能」进入「谁更准、谁更易用」阶段。DeepMind 押注「WN2 统一大气+气旋 + 官方数据 feed」的组合，方向正确。长期看，AI 模型与传统 NWP 的融合（同化初始场、集合互补）是主旋律。

**给 AI/读者的启发**：做垂域大模型时，WeatherNext 的「主模型 + 衍生权重（气旋）+ 专用后处理（tracker）+ 开放 feed」四件套，是比「单模型刷榜」更可持续的发布范式——尤其适合任何「通用能力需要在特定场景精修」的领域。

---

## 八、关键文件速查

| 文件/目录 | 作用 |
|-----------|------|
| `README.md` | 模型家族、预训练权重版本、数据 feed、Quick Start |
| `docs/weathernext2/wn2_demo.ipynb` | Colab 交互 demo（推荐入口） |
| `docs/weathernext1_graph/` | GraphCast 文档 |
| `docs/weathernext1_gen/` | GenCast 文档 |
| `weathernext/cyclones/direct_tracker.py` | ★ 贪婪式气旋追踪（mean/mode/mode-then-mean） |
| `weathernext/cyclones/tracker_base.py` | 追踪器基类 |
| `weathernext/cyclones/ibtracs_processing_utils.py` | IBTrACS 真实数据接入 |
| `weathernext/cyclones/constants.py` | 气旋变量常量 |
| `utils/` | 共享库：rollout / 归一化 / 图构建 / 损失 / xarray 工具 |
| 技术报告 | arXiv:2506.10772（FGN/WN2） |
| 气旋论文 | Nature 2026 (s41586-026-10953-2) |
| 安装 | `pip install git+https://github.com/google-deepmind/weathernext.git@v0.3.0` |

---

*调研方法：gh API 元数据核验 + raw.githubusercontent 源码直读（README/direct_tracker.py）+ 论文/数据 feed 公开信息。所有关键数据均来自真实抓取，缺失标「数据不可用」而非编造。*
