# GeminiWatermarkTool（Gemini 水印去除工具）深度调研

> 数据来源：GitHub API 抓取（stars / README / 目录树 / 源码），抓取日期 2026-10-03。许可：MIT。语言：C++20（跨平台：Windows / Linux / macOS / Android）。

## 一、项目定位（一句话）
用**反向 alpha 混合**做「数学精确」的 Gemini 可见水印去除——把被半透明 logo 覆盖的原始像素还原出来，离线、单可执行、GUI+CLI 双形态。

## 二、项目亮点（差异化）
1. **确定性重建**：`original = (watermarked − α·logo) / (1 − α)`，非生成式 inpainting，文字边缘保持锐利。
2. **三阶段 NCC 检测**：空间 NCC(50%) + 梯度 NCC(30%) + 方差分析(20%)，自动跳过无水印图，避免误伤。
3. **AI 去噪**：NCNN + Vulkan 的 FDnCNN 修复重采样/重压缩后的残差（<5ms/区域 GPU）。
4. **双水印 profile**：V1（3.5 前）/ V2（3.5+），CLI 自动 legacy 回退。
5. **Agent 化**：MCP Server + Claude Code Skill，把去水印封装成 4 个 MCP 工具。
6. **极致便携**：单可执行、静态链接、零运行时依赖；另有 `gwt-mini`（~5MB，UPX）。

## 三、核心架构
- `src/core/`：`watermark_engine`（主引擎）、`watermark_detector`（三阶段检测）、`blend_modes`、`ai_denoise`（NCNN 推理）、`ncnn_shim`（Vulkan 加载）、`types`。
- `src/cli/`（`cli_app`）+ `src/gui/`（ImGui + SDL3，D3D11/OpenGL 双后端）+ `src/main.cpp`（CLI/GUI 调度）。
- `external/ncnn`（git submodule）、`vcpkg` 静态链接（OpenCV/fmt/CLI11/spdlog/SDL3/ImGui/volk）。
- `CMakePresets.json` 跨平台构建；`report/synthid_research.md` 说明为何去不掉 SynthID 不可见水印。

## 四、应用场景与启发
- 「确定性逆向算法 + 轻量神经网络后处理」的组合范式，对图像取证/水印研究有参考价值。
- AI Denoise 作为**可选 post-process** 的模块化设计（开关、强度、sigma）值得借鉴。
- MCP 集成是「桌面工具走向 agent 工作流」的范例（4 个工具：`remove_watermark`/`detect_watermark`/`batch_process`/`get_tool_info`）。
- ⚠️ 双刃属性：核心用途是去除生成图水印，宜定位为「水印检测与取证研究」而非批量去水印。

## 五、源码深度解读
**`src/core/watermark_engine.hpp`（引擎核心）**：`WatermarkEngine` 持有 V1/V2 的大小两套 alpha map，对外提供检测与去除/添加：
```cpp
class WatermarkEngine {
public:
    // 三阶段检测：空间 NCC → 梯度 NCC → 方差分析
    DetectionResult detect_watermark(const cv::Mat& image,
        std::optional<WatermarkSize> force_size = std::nullopt,
        std::optional<WatermarkVariant> force_variant = std::nullopt) const;
    // 反向 alpha 混合：original = (watermarked - α·logo) / (1 - α)
    void remove_watermark(cv::Mat& image, ...);
    void add_watermark(cv::Mat& image, ...);          // 也可反向加水印
    void inpaint_residual(cv::Mat& image, const cv::Rect& region,
        float strength = 0.85f, InpaintMethod method = NS, ...) const;
private:
    cv::Mat alpha_map_small_, alpha_map_large_;       // V1
    cv::Mat alpha_map_small_v2_, alpha_map_large_v2_; // V2（3.5+）
};
```
数学本质：`watermarked = α·logo + (1−α)·original`，逆向解出 original；当图被二次缩放/压缩导致不精确时，再用梯度掩码 + NS/TELEA/高斯/AI 去噪修复残差。

**`src/core/watermark_detector.hpp`**：`DetectionResult` 把三阶段分数都暴露出来，便于阈值决策：
```cpp
struct DetectionResult {
    bool detected; float confidence; cv::Rect region;
    WatermarkSize size; WatermarkVariant variant{WatermarkVariant::V2};
    float spatial_score;     // 阶段1 空间 NCC
    float gradient_score;    // 阶段2 梯度 NCC
    float variance_score;    // 阶段3 纹理方差
};
```

## 六、全网口碑
**3123 ⭐**，作者 Allen Kuo 自称反向 alpha blending 原始作者，配套 Medium 深度技术文；Ko-fi/PayPal 赞助；GitHub Actions CI 跨 Win/Linux/macOS/Android 出包。社区规模与完成度都高。

## 七、竞品对比
| 维度 | GeminiWatermarkTool | 生成式去水印网站/扩展 | Stable Diffusion inpaint | 传统 PS 内容识别 |
|------|---------------------|----------------------|--------------------------|-----------------|
| 方法 | 确定性反向混合 | 生成式 | 生成式 | 生成式 |
| 文字保留 | ✅ 锐利 | ❌ 易糊 | ❌ | 一般 |
| 离线/便携 | ✅ 单文件 | ❌ 需云 | 需算力 | 需软件 |
| 批量/脚本 | ✅ CLI + MCP | 中 | 中 | 弱 |

差异化：确定性、保留文字、可脚本/MCP。**风险/伦理**：仅去可见水印、明确不去 SynthID；作者声明「个人与教育用途、遵守法律」，批量去水印涉及版权与平台 ToS 边界，须在合规框架内使用。

## 八、核心研判
工程完成度高、跨平台打磨好、算法有原创性，是「水印逆向」方向质量突出的开源实现；但其核心用途（去除生成图水印）存在版权/合规边界，建议定位为**水印检测与取证研究工具**，而非批量去水印方案。对做图像算法/桌面工具/MCP 化的开发者仍有较高学习价值。

## 关键文件路径速查
- `src/core/watermark_engine.hpp` / `.cpp` — 主引擎（检测/去除/添加/修复）
- `src/core/watermark_detector.hpp` / `.cpp` — 三阶段 NCC 检测
- `src/core/blend_modes.hpp` / `.cpp` — 混合模式
- `src/core/ai_denoise.hpp` / `.cpp` — NCNN + Vulkan FDnCNN 去噪
- `src/core/ncnn_shim.hpp` — Vulkan 动态加载
- `src/cli/cli_app.cpp` — CLI 入口
- `src/gui/` — ImGui + SDL3，D3D11/OpenGL 后端
- `report/synthid_research.md` — 为何去不掉 SynthID 不可见水印
