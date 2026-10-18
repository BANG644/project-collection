# Kruk2/jasna 深度调研

> 调研日期：2026-10-19 ｜ 定位：免费 GPU 视频/图片马赛克修复工具 ｜ 许可：AGPL-3.0（代码）；增强模型需 supporter license ｜ 语言：Python（+ C++ native kernel、CUDA/ROCm）｜ 2,332⭐，活跃（2026-10-18 仍有提交）

## 一、项目亮点（差异化）

1. **端到端全 GPU 管线**：从解码到编码都在 GPU（NVIDIA NVDEC/NVENC、AMD AMF），CPU 几乎不碰帧。
2. **两档修复模型**：免费 **BasicVSR++**（快）；付费 **LTX** 扩散模型（慢但细节更多，NVIDIA only）。
3. **只修马赛克区域**：检测→跟踪→按 clip 分组→仅还原遮挡区→blend 回原帧，其余画面不动。
4. **Segment Editor + Video Player**：可交互选区域、实时预览、不落盘看修复效果。
5. **授权分层透明**：核心 AGPL-3.0；增强模型（UNet 4x / SD 1.5 / LTX）需 supporter license（3 台设备/云工作区），作者明示仅从 GitHub 下载、第三方卖 key/改文件是诈骗。

## 二、核心架构

README「How Jasna works」给出的 7 步管线（几乎全在 GPU）：

1. GPU 解码（NVDEC / AMF）
2. 逐帧检测马赛克（默认模型 `rfdetr-v6`）
3. 跨帧跟踪并聚成 clip（≤ Max Clip Size，遇场景切换即断，不混不同镜头）
4. 每 clip 以 BasicVSR++ 还原成 256×256（clip 间重叠，避免跳变）
5. 可选二次修复（UNet 4x / RTX Super Res / Topaz TVAI）放大锐化
6. blend 回原帧（只改马赛克区）
7. GPU 编码（NVENC / AMF），音频直拷（仅输出格式不支持时才重编码）

- 首次运行按本机 GPU 编译模型权重（15–60 min，仅一次，存 `model_weights` 可跨版本复用）。
- LTX 不同：4 遍（找马赛克→准备→扩散还原→保存），更慢更细。
- 支持 VR180 侧-侧、静态图（SD 1.5，supporter）、`--input/--output` 批量 CLI。

## 三、应用场景与启发

- niche 但真实需求：去除影视/二次创作中的 censorship mosaic、旧片轻量修复。
- **工程启发**：①「检测→跟踪→局部修复→blend」的局部化处理范式，可迁移到去水印/去划痕/老片修复；②全 GPU 帧管线（解码-推理-编码零拷贝）是视频 AI 工具的高性能范式；③C++ native kernel + Python 编排的混合架构；④benchmark-as-first-class 文化（每次发布带 CSV 基准，如 RTX 5090 上比 Lada 快 3.4–4.7×）。

## 四、源码解读（真实路径，来自仓库树）

- `jasna/image_restore.py`：图片修复入口
- `jasna/gui/app.py`：GUI 主程序（Py 侧，Qt/自绘组件）
- `jasna/gui/segment_editor.py` / `segment_scan_panel.py` / `segment_timeline.py` / `interactive_image_restore.py`：Segment Editor 交互
- `jasna/gui/video_player.py` / `raw_player.py`：实时预览
- `jasna/ltx/inference.py` / `ltx/blocks.py` / `ltx/compose.py` / `ltx/native/block.cpp` + `aot.py`：LTX 扩散推理 + C++ native kernel
- `jasna/accelerator.py` / `frame_queue.py` / `crop_buffer.py` / `blend_buffer.py` / `engine_compiler.py` / `engine_paths.py`：GPU 加速/帧队列/裁剪/混合/引擎编译
- `jasna/license_api.py`：supporter license 在线/手动激活
- `jasna/benchmark/*`：大量真实基准 CSV/MD
- 受 Codeberg **Lada** 启发，`mosaic_restoration_1.2` 模型由 ladaapp 训练；VR 检测模型来自 ZeLeFans。

## 五、社区口碑

README 详尽、多语言（EN/JA/ZH）、benchmark 透明；license 分层（增强模型付费）在社区有讨论；作者明确提醒仅从 GitHub 下载、第三方卖 key/改文件是诈骗。

## 六、竞品对比

| 方案 | 定位 | 差异 |
|---|---|---|
| Topaz Video AI | 商业通用视频增强 | 贵、非专攻 mosaic |
| waifu2x / Real-ESRGAN | 通用超分 | 不专门检测 mosaic |
| VapourSynth + 脚本 | 专业视频处理 | 门槛高 |
| Lada（Codeberg） | 上游/灵感来源 | Jasna 基于此 |
| **jasna** | 免费专攻 mosaic | 检测+跟踪+局部还原 一体化、零成本、GUI/CLI 易用 |

## 七、核心研判

- **强项**：专攻痛点、全 GPU 高性能、易用、透明基准。
- **局限**：依赖较新显卡（GTX16/RTX20+，compute≥7.5；LTX 要 RTX+8GB VRAM）；路径不能含中文/日文/重音（Windows 坑）；增强模型需付费；非通用视频增强。
- **适合**：有兼容 GPU、需去 mosaic / 做轻量视频修复的用户。

## 八、关键文件速查

`jasna/image_restore.py` · `jasna/gui/app.py` · `jasna/ltx/inference.py` · `jasna/accelerator.py` · `jasna/benchmark/` · `LICENSING.md` · `docs/en/*`
