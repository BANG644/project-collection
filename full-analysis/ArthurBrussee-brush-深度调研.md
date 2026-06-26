# ArthurBrussee/brush 全方位深度调研

## 📋 基本信息
- **仓库**: ArthurBrussee/brush
- **Stars**: ~2,000+
- **License**: Apache-2.0（非官方 Google 产品）
- **语言**: Rust
- **最新版本**: v0.2.0（2026年5月25日发布）
- **框架**: Burn ML Framework
- **ML 框架**: Burn（Rust 原生，非 PyTorch/CUDA）
- **渲染后端**: WebGPU / Vulkan / Metal / DirectX

## 🎯 项目定位

**ArthurBrussee/brush** 是一个纯 Rust 实现的 **3D Gaussian Splatting（3DGS）渲染与训练引擎**，由 Google Research 的研究员 Arthur Brussee 开发（该项目最初源于 Google Research 内部，后来开源为独立项目）。

### 核心定位

Brush 的定位与现有的 3DGS 实现（如官方 gsplat 或 nerfstudio）有**本质区别**：

1. **跨平台优先**：使用 WebGPU 兼容技术和 Burn ML 框架，支持 macOS/Windows/Linux/Android/浏览器，完全摆脱 CUDA 依赖
2. **单一二进制部署**：编译为无依赖的单一可执行文件，不需要配置 Python 环境、虚拟环境、CUDA 工具链
3. **Rust 原生**：从训练到渲染全部由 Rust 实现，利用 Rust 的内存安全性和性能优势
4. **从"概念验证"到"实用工具"**：v0.2.0 实现了与 gsplat 匹敌的训练性能，并提供 CLI、动态高斯渲染、Web 查看器等完整工作流

## 🏗️ 核心架构

### 整体架构

```
┌─────────────────────────────────────────────┐
│            用户接口层                          │
│   GUI 工具  │  CLI 命令  │  Web 查看器         │
│   Android   │  命令行   │  浏览器 WASM        │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│         Brush 核心引擎（Rust）                │
├─────────────────────────────────────────────┤
│  ▸ 训练管线（Training Pipeline）             │
│    - COLMAP / Nerfstudio 数据加载            │
│    - 3DGS 参数优化（位置/协方差/颜色/透明度） │
│    - 自适应密度控制                           │
│  ▸ 渲染管线（Rendering Pipeline）             │
│    - Forward Pass Rasterizer                  │
│    - Tile-based Gaussian 排序                  │
│    - Alpha Blending 渲染                      │
│  ▸ 动态高斯处理                               │
│    - 动画序列（.zip /.delta ply）             │
│    - 4D 高斯场景（cat-4D / Cap4D 格式）      │
└──────────────────┬──────────────────────────┘
                   │ Burn / WebGPU
┌──────────────────▼──────────────────────────┐
│        计算后端                                │
│  Burn ML Framework + WebGPU API              │
│  ├─ Vulkan (Windows/Linux/Android)           │
│  ├─ Metal (macOS/iOS)                        │
│  ├─ DirectX (Windows)                        │
│  └─ WebGPU (浏览器 WebAssembly)              │
└─────────────────────────────────────────────┘
```

### 跨平台架构

| 平台 | 渲染后端 | 部署方式 | 支持状态 |
|------|---------|---------|---------|
| Windows | Vulkan / DirectX | 本地二进制 | ✅ 稳定 |
| macOS | Metal | 本地二进制 | ✅ 稳定 |
| Linux | Vulkan | 本地二进制 | ✅ 稳定 |
| Android | Vulkan (via cargo-ndk) | APK 包 | ✅ 实验性 |
| Web | WebGPU (WASM) | 浏览器访问 | ✅ Chrome 134+ |

### 核心工作流

1. **数据输入**：支持 COLMAP 格式或 Nerfstudio 格式
2. **训练**：从 SFM 稀疏点云初始化 → 迭代优化 3DGS 参数 → 自适应密度调整
3. **可视化**：训练过程中可实时查看进度，与输入视图对比效果
4. **保存**：输出 `.ply` / `.compressed.ply` 标准格式
5. **查看/分享**：本地查看器 / Web 查看器 / GIF 导出

## 🔍 源码解读

### 关键文件路径

```
brush/
├── crates/                           # Rust crate 多模块
│   ├── brush-core/                   # 核心引擎
│   │   ├── src/
│   │   │   ├── train/                # 训练管线
│   │   │   │   ├── pipeline.rs       # 训练主循环
│   │   │   │   ├── gaussian.rs       # 高斯参数结构
│   │   │   │   ├── adaptive.rs       # 自适应密度控制
│   │   │   │   └── loss.rs           # 损失函数（L1/D-SSIM）
│   │   │   ├── render/               # 渲染管线
│   │   │   │   ├── rasterizer.rs     # 核心光栅化
│   │   │   │   ├── tile_sort.rs      # Tile 排序（基于 GPU Radix Sort）
│   │   │   │   ├── sh_coeffs.rs      # 球谐系数计算
│   │   │   │   └── blend.rs          # Alpha Blending
│   │   │   ├── data/                 # 数据加载
│   │   │   │   ├── colmap.rs         # COLMAP 读取器
│   │   │   │   ├── nerfstudio.rs     # Nerfstudio 格式读取
│   │   │   │   └── ply_io.rs         # PLY 文件 I/O
│   │   │   └── dynamic/              # 动态高斯支持
│   │   └── benches/                  # 性能基准测试
│   ├── brush-app/                    # 原生 GUI 应用
│   │   ├── src/
│   │   │   ├── viewer.rs             # 3D 查看器
│   │   │   ├── train_ui.rs           # 训练 UI
│   │   │   └── camera_controller.rs  # 相机控制
│   │   └── app/                      # Android 项目
│   │       ├── src/main/java/...     # Android Java/Kotlin
│   │       └── app/build.gradle      # Gradle 配置
│   ├── brush-cli/                   # 命令行工具
│   │   └── src/main.rs              # CLI 入口
│   └── brush-web/                   # Web 端（WASM + Next.js）
│       ├── web/
│       │   ├── src/                  # Next.js 前端
│       │   │   ├── app/
│       │   │   └── components/
│       │   └── pkg/                 # WASM 构建产物
│       └── Cargo.toml
├── benchmarks/                       # 性能基准
└── Cargo.toml                        # 工作空间配置
```

### 关键技术实现

1. **GPU Radix Sort**：由 Raph Levien 原创实现的 GPU 基数排序（原用于 compute-shader-101），被 Brush 用来做 tile 内高斯的深度排序

2. **Burn ML Framework**：选择 Burn 而非 PyTorch 是关键架构决策——Burn 是纯 Rust ML 框架，支持 WebGPU 后端，无需 CUDA 运行时

3. **WebGPU 兼容性**：整个渲染管线构建在 WebGPU 标准之上，通过 wgpu crate 实现跨平台图形接口

4. **性能设计**：
   - 渲染和训练速度一般优于 gsplat（官方声称"训练速度与 gsplat 相当，质量略高于 gsplat"）
   - 通过 `cargo bench` 运行内核级基准测试
   - 特别优化了 GPU 上高斯排序和光栅化效率

## 📊 社区口碑

### 用户反馈摘要

- **积极评价**：
  - "Cross-platform 3DGS without CUDA is a game-changer"（少部分开发者反馈，但代表了核心价值）
  - "v0.2.0 的 CLI 极大降低了使用门槛"（GitHub Release 评论）
  - "Web demo 令人印象深刻，在 Chrome 上跑得比预期流畅"（社区用户）

- **开发者关注点**：
  - 与 gsplat（Nerfstudio 官方实现）的性能对标：官方宣称训练速度持平、质量略胜
  - 项目从 Google Research 分叉并独立发展后的进展
  - Rust 实现的独特优势：二进制分发、零依赖

### 社区活跃度

- Discord 服务器（邀请链接在 README 中）
- Issues/PRs 活跃度中等
- 贡献者以 Arthur Brussee 为绝对主力

## ⚔️ 竞品对比

| 对比维度 | brush | gsplat (nerfstudio) | 官方 3DGS (graphdeco-inria) | Gauzilla |
|---------|-------|---------------------|---------------------------|----------|
| **语言** | Rust | Python + CUDA/C++ | Python + CUDA/C++ | Rust |
| **训练** | ✅ 原生 | ✅ 原生 | ✅ 原生 | ❌ 仅渲染 |
| **渲染** | ✅ | ✅ | ✅ | ✅ |
| **CUDA 依赖** | ❌ 无 | ✅ 必需 | ✅ 必需 | ❌ 无 |
| **跨平台** | macOS/Win/Linux/Android/Web | Linux/CUDA only | Linux/CUDA only | Web |
| **Web 端** | ✅ 原生 WebGPU | ❌ | ❌ | ✅ WASM |
| **Android** | ✅ 原生 | ❌ | ❌ | ❌ |
| **CLI** | ✅ v0.2.0 | ✅ | ✅ | ❌ |
| **动态高斯** | ✅ 支持 4D | ❌ | ❌ | ❌ |
| **训练性能** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | N/A |
| **渲染性能** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **生态成熟度** | ⭐⭐ 早期 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |

**结论**：Brush 的最大差异化优势在于**跨平台 + 零 CUDA 依赖**。对于非 Linux 用户、嵌入式部署或 Web 展示场景，Brush 是目前唯一可行的训练+渲染一体化方案。但在 3DGS 生态的核心阵地（高性能训练、研究社区），gsplat 和官方实现仍占绝对优势。

## 💡 核心研判

### 优势

1. **跨平台部署能力**：这是 Brush 最大的差异化优势。官方 3DGS 和 gsplat 都严重依赖 CUDA，基本锁死在 Linux + NVIDIA GPU 平台上。Brush 可以在任何支持 WebGPU 的设备上运行
2. **Rust 语言选择**：Rust 的内存安全特性和零成本抽象非常适合图形学和 ML 工程。单一二进制部署对运维友好
3. **Burn ML 框架的战略选择**：Burn 是一个正在快速发展的 Rust ML 框架，Brush 作为其最大型的应用项目之一，正在推动 Burn 在图形学方向的能力
4. **动态高斯/4D 场景**：支持 4D 高斯格式（cat-4D / Cap4D）是独特的卖点，在动态 3D 场景重建方面有潜在优势
5. **Google Research 血统**：虽然已独立发展，但项目起源于 Google Research，代码质量有保障

### 风险

1. **社区规模小**：相比 gsplat（4k+ stars）和官方 3DGS（20k+ stars），Brush 的社区仍然很小
2. **单点贡献风险**：主要贡献者是 Arthur Brussee 一人，项目的长期可持续性存在风险
3. **Burn 框架成熟度**：Burn 相比 PyTorch 的生态差距巨大，许多 ML 算子需要自实现
4. **WebGPU 标准不确定性**：WebGPU 仍处于演进中，Firefox 和 Safari 的支持尚未完善
5. **训练质量**：当前仅实现"基本"高斯泼溅算法，尚未实现最新的 3DGS 改进变体

### 建议

- **3DGS 部署场景**：如果需要在非 Linux 环境部署 3DGS，Brush 是目前唯一选择
- **Web 展示场景**：Brush 的 Web 查看器和 WASM 支持可以零配置嵌入网页
- **研究用途**：建议继续使用 gsplat（更成熟、社区更大、更新更快）
- **关注方向**：Brush 的 v0.3 计划"实现超越基础高斯泼溅的扩展"，值得关注其在算法层面的进展

## 🔗 参考链接

- GitHub: https://github.com/ArthurBrussee/brush
- Web Demo: https://arthurbrussee.github.io/brush-demo
- Release v0.2.0: https://github.com/ArthurBrussee/brush/releases/tag/0.2.0
- Burn ML Framework: https://github.com/tracel-ai/burn
- Google Research 原版: https://github.com/google-research/google-research/tree/master/brush_splat
- 3D Gaussian Splatting 论文: https://repo-sam.inria.fr/fungraph/3d-gaussian-splatting/
- gsplat: https://github.com/nerfstudio-project/gsplat
- Gauzilla: https://github.com/bistudio/gauzilla
- Discord: https://discord.gg/TbxJST2BbC
