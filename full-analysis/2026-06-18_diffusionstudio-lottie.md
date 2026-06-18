# 🔍 深度调研报告：diffusionstudio/lottie

> **调研日期**: 2026-06-18
> **Stars**: Trending 2026-06-10
> **语言**: Skill (Markdown + JS)
> **简介**: 使用 Claude Code 或 Codex 生成生产级 Lottie 动画的开源框架

---

## 一、项目概述

Text-to-Lottie 是 Diffusion Studio（YC W25）推出的开源框架，它让 Agent 通过描述直接生成 Lottie 动画。Agent 在本地搭建工作区和播放器，动画作为场景实时预览，Agent 编辑 → 播放器自动更新。

**核心流程**: 输入描述 → Agent 生成 Lottie JSON → 实时预览 → 可用于生产

## 二、核心架构

### 工作区结构
```
public/projects/<project>/<scene>/lottie.json
```

每次动画都是一个场景。场景文件自动加载到内置播放器中，Agent 编辑时播放器实时刷新。

### 跨平台渲染
Lottie 可以在几乎所有现代平台上渲染：

| 平台 | 渲染方式 |
|------|---------|
| Web | lottie-web (lottie.min.js) |
| React Native | lottie-react-native 或 react-native-skia (Skottie) |
| iOS/macOS | LottieAnimationView (Lottie for iOS) |
| Android | LottieAnimationView (Lottie for Android) |
| Flutter | lottie 包 |
| After Effects | 生成的 JSON 可直接导入 |

## 三、最佳实践

### 输入最佳来源
- **提供 SVG、真实数据或截图** → 效果显著更好
- **具体资产 → 更好的输出**

### 动效描述
使用专业动效设计语言描述时序：
- `ease-in`、`ease-out`、`ease-in-out`

### 摄像机运动
专业动态图形依赖摄像机运动。在 prompt 中包含：
- 摄像机推拉、平移、缩放
- 通过组变换模拟摄像机轨运动

### 自定义控制
默认只暴露背景色控制。如需自定义其他属性，需明确要求 Agent 创建对应控件。

### 性能控制
如需特定帧率或时长，在 prompt 中指定 FPS 和总帧数。

## 四、技术特性

1. **实时预览** — Agent 编辑 → 播放器自动刷新，可检查、擦洗、优化
2. **素材智能** — 基于真实 SVG 路径/图标/数据生成，而非凭空创造
3. **矢量化** — 输出为 JSON 格式，无限缩放
4. **跨平台** — Web/Mobile/Native 均支持
5. **After Effects 兼容** — JSON 可直接导入 AE 精调

## 五、使用示例

```bash
# 安装技能
npx skills add diffusionstudio/lottie
```

**示例 prompt**:
> 创建一个基于 SVG 路径的 Lottie 动画，路径按自然方向展示。应用高级苹果风格渐变到路径。使用 ease-in-out 时序、透明背景、保留原始 SVG 几何。

## 六、适用场景

- **UI 动效** — 按钮动画、加载动画、过渡动效
- **徽标动画** — 品牌展示动画
- **数据可视化** — 动态图表的运动渲染
- **产品展示** — 功能讲解动画
- **社交媒体** — 短动画内容

## 七、同类项目对比

| 特性 | text-to-lottie | Adobe After Effects | LottieFiles | Rive |
|------|---------------|-------------------|-------------|------|
| AI 驱动 | ✅ | ❌ | ❌ | ❌ |
| 终端生成 | ✅ | ❌ | ❌ | ❌ |
| 实时预览 | ✅ | ✅ | ✅ | ✅ |
| 轻量 | ✅ | ❌ | ✅ | ✅ |
| 跨平台 | ✅ | ❌ | ✅ | ✅ |

## 八、核心结论

Diffusion Studio 的 text-to-lottie 方案解决了"让 AI 生成可以上线的动效"这个实际问题。Lottie 格式天然适合 AI 生成（JSON 结构、矢量化、经过验证的跨平台渲染能力），而提供 SVG/图标作为输入引导则显著提升了生成质量。作为 YC W25 的项目，这是一个面向 Agent 时代的动画生产工具——不是在 GUI 里拖拽，而是用描述和代码生产动效。

**局限**: 依赖 Agent 对动效概念的理解能力；复杂多场景动画场景的管理较原始；没有可视化的关键帧编辑器（只有 JSON）；需要 Lottie 生态的基础知识才能正确使用输出。
