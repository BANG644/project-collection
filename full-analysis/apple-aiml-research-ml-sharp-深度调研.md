# SHARP (apple-aiml-research/ml-sharp) — 单图 <1 秒的逼真新视角合成

> 调研日期：2026-09-27 ｜ 定位：Apple 官方研究——单张照片前向回归 3D Gaussian，实时新视角渲染
> 数据源：gh api 真实抓取 README.md / pyproject.toml / src/sharp/cli/predict.py / src/sharp/models/predictor.py

## 一、项目全景

| 项 | 值 |
|---|---|
| 仓库 | `apple-aiml-research/ml-sharp`（默认分支 `main`） |
| 星标 | 8,918 ⭐ |
| 语言 | Python（PyTorch，CLI 用 click + gsplat 渲染） |
| 许可 | 代码 `NOASSERTION`；模型单独 `LICENSE_MODEL`（研究/非商用，需自查） |
| 论文 | arXiv 2512.10685《Sharp Monocular View Synthesis in Less Than a Second》 |
| 最后提交 | 2026-09-11 |

**一句话**：给定一张照片，SHARP 用单次神经网络前向传播回归出该场景的 3D Gaussian 表示（含绝对尺度），<1 秒完成，随后可实时渲染出邻近视角的高清逼真图。论文称在多个数据集上 LPIPS 降 25–34%、DISTS 降 21–43%，合成时间比前 SOTA 低 **三个数量级**。

## 二、项目亮点

1. **单前向、即时 3D**：无需多视图、无需优化/训练，单图直接出 Gaussian 场。
2. **度量空间（metric, absolute scale）**：表示带绝对尺度，支持"度量级相机运动"（绕场景走位），不是仅相对视角。
3. **强零样本泛化**：跨数据集鲁棒，论文宣称新 SOTA。
4. **开箱 CLI**：`sharp predict` / `sharp render`，首次运行自动 `torch.hub` 下载 checkpoint 并缓存。
5. **工业级代码组织**：`sharp` 包（cli/models/utils 分层）、pyproject 规范、pyright/ruff/pytest 齐全。

## 三、核心架构

```
src/sharp/
  cli/        predict.py（predict_cli + predict_image）, render.py
  models/     predictor.py（RGBGaussianPredictor 主图）, monodepth.py,
              composer.py（GaussianComposer）, blocks/encoders/decoders/presets
  utils/      gaussians.py（Gaussians3D / unproject_gaussians / save_ply）,
              camera.py, gsplat.py, io.py, linalg.py, math.py
```
**推理链**：图像 → `monodepth` 估深（对齐 GT，可选）→ `init_model` 出 base Gaussians + global scale → `feature_model`（image2image，注入 monodepth 特征）→ `prediction_head` 出 delta → `gaussian_composer` 把 delta 加到 base 并还原尺度 → 度量空间 Gaussians。

## 四、源码深度解读

**① CLI 入口（`cli/predict.py`）**——设备自适应 + NDC→度量反投影：
```python
if torch.cuda.is_available(): device = "cuda"
elif torch.mps.is_available(): device = "mps"
else: device = "cpu"
# 内部固定 1536×1536，先在前向输出 NDC 空间高斯，再反投影到度量空间
gaussians_ndc = predictor(image_resized_pt, disparity_factor)
gaussians = unproject_gaussians(gaussians_ndc, torch.eye(4).to(device),
                                intrinsics_resized, internal_shape)
save_ply(gaussians, f_px, (height, width), output_path / f"{stem}.ply")
```
关键点：模型在 **NDC 空间**预测，最后用相机内参 `unproject` 回度量坐标——这样高斯场带真实尺度，渲染时相机可"走位"。

**② 主网络（`models/predictor.py`）**——`RGBGaussianPredictor.forward` 的计算图（源码注释直接给出）：
```
monodepth ─┐
           ├─ depth_alignment(局部 scale map) → monodepth(aligned)
depth ─────┘
   → init_model(image, monodepth) → base gaussians + global scale
   → feature_model(init_output.feature_input, encodings=monodepth features)
   → prediction_head → delta_values
   → gaussian_composer(delta, base_values, global_scale) → gaussians(metric)
```
值得注意的工程细节：`DepthAlignment` 被单独包成一个 `nn.Module`，**仅为让 predictor 在 symbolic tracing（导出）时计算图静态**——条件逻辑（是否对齐 GT）被隔离进子模块，训练/推理路径统一。这是把"研究代码可导出"考虑进架构的范例。

## 五、社区口碑

- Apple 官方研究账号发布，arXiv 预印本 + 项目页（`apple.github.io/ml-sharp`）含多段视频对比，社区关注度高（8.9k⭐）。
- 定位偏**研究原型**：渲染视频需 CUDA（gsplat），CPU/MPS 仅能做预测；模型许可（`LICENSE_MODEL`）需单独确认，通常限制商用。
- 与近年 "3D Gaussian / 单图重建" 浪潮（如 LRM、GS-LRM、triposplat）同赛道，SHARP 的卖点是"速度 + 度量尺度"。

## 六、竞品对比

| 项目 | 输入 | 速度/特性 | 差异 |
|---|---|---|---|
| `VAST-AI-Research/TripoSplat`（已入库） | 单图 → 可变数量 3D 高斯 | 物体级重建 | 物体中心、可变高斯数；SHARP 是场景级新视角合成 |
| GS-LRM / LRM 类 | 多/单图 → 3D | 需 transformer 大前向 | SHARP 更轻、单图即时 |
| 传统 NeRF/MVS | 多图 | 慢、需优化 | SHARP 单图、秒级 |

## 七、核心研判

- **方向代表**："单前向 + 度量 3D Gaussian"是**即时 3D / 数字人商品预览 / AR 贴地**的优质技术底座；比慢优化方案更适合交互场景。
- **对用户启发**：若做"图片→可旋转预览"类功能（如商品、讲义插图），SHARP 的"模板即度量场 + 实时渲染"思路比训练 NeRF 务实得多；可关注其 checkpoint 是否开放商用。
- **风险**：模型许可未明，商用前必须查 `LICENSE_MODEL`；CUDA 渲染依赖对纯 CPU 环境不友好。

## 八、关键文件路径速查

| 路径 | 作用 |
|---|---|
| `src/sharp/cli/predict.py` | `sharp predict` 入口，设备选择 + NDC→度量反投影 |
| `src/sharp/models/predictor.py` | `RGBGaussianPredictor` 主图 + `DepthAlignment` 可导出封装 |
| `src/sharp/models/composer.py` | `GaussianComposer`：delta 合成 |
| `src/sharp/utils/gaussians.py` | `Gaussians3D` / `unproject_gaussians` / `save_ply` |
| `src/sharp/models/monodepth.py` | 单目深度估计（含编码适配器） |
| `pyproject.toml` | `sharp` CLI 入口（`sharp.cli:main_cli`）、依赖 |
