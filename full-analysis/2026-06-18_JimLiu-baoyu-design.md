# 🔍 深度调研报告：JimLiu/baoyu-design

> **调研日期**: 2026-06-18
> **Stars**: 516 ⭐ (2026-06-09 Trending)
> **语言**: JavaScript
> **简介**: Run Claude Design locally as an Agent Skill — 将 Claude 的 UI 设计能力搬进本地编辑器

---

## 一、项目概述

baoyu-design 是一个 Agent Skill，它将 [claude.ai/design](https://claude.ai/design) 背后的设计引擎封装为可移植的技能包。用户可以在本地 Agent（Cursor、Claude Code、Codex 等）中直接生成精美的 UI 线框图、交互式原型、落地页、仪表盘、移动应用甚至幻灯片——所有输出都是独立的 HTML 文件。

**核心理念**: 脱离网站束缚，在编辑器内完成全部设计工作流。

## 二、核心架构

```
skills/baoyu-design/
├── SKILL.md                    # 入口 — 编排整个流程
├── system-prompt.md            # 设计方法论与工艺标准（真相源）
├── references/
│   ├── claude.md               # Claude Code 工具映射
│   ├── cursor.md               # Cursor 工具映射
│   └── codex.md                # Codex Agent 工具映射
├── built-in-skills/            # 专用提示词（幻灯片、移动端、导入、导出……）
└── starter-components/         # 设备框架、幻灯片舞台、画布、动画引擎……
```

### 设计流程
1. **引导式提问** → 2. **收集设计上下文** → 3. **生产 HTML 交付物** → 4. **预览验证**

### 内置技能清单

| 领域 | 能力 |
|------|------|
| 核心设计 | 高保真设计 · 交互式原型 · 线框图 · 前端视觉方向 |
| 幻灯片 | 制作幻灯片 · 演讲者备注 |
| 移动与动效 | 移动端原型 · 动画视频 · 音效 |
| 设计系统 | 创建设计系统 · 使用设计系统 · 可调教组件 |
| 导入源 | Figma .fig 离线解析 · GitHub 仓库 · 已有 HTML/CSS |
| 导出与交接 | 独立 HTML · PDF · 可编辑 PPTX · 截图 PPTX · 视频 MP4 · 发送到 Figma/Canva |
| AI 资源 | Gemini 图像生成 · 从原型调用 Claude · 读取 PDF |

## 三、技术亮点

1. **零构建步骤** — 全部是纯 Markdown + JSX/JS scaffold，无构建工具、无运行时依赖
2. **迭代方式创新** — 通过内置浏览器预览直接指向输出元素，而非用语言描述修改
3. **最佳搭配 Opus 4.8** — 该技能是一个长而详细的设计简报，模型越强效果越好
4. **所见即所得循环** — Cursor Browser / Claude Preview / Codex Browser 直接预览标注

## 四、安装方式

```bash
# 一键安装到当前项目
npx skills add JimLiu/baoyu-design

# 全局安装
npx skills add JimLiu/baoyu-design -g
```

## 五、同类项目对比

| 特性 | baoyu-design | claude.ai/design | Figma |
|------|-------------|----------------|-------|
| 本地运行 | ✅ | ❌ | ❌ |
| 编辑器内集成 | ✅ | ❌ | ❌ |
| 无需订阅 | ✅ | ❌ | 免费版有限 |
| 输出 HTML | ✅ | ✅ | ❌ |
| 协作 | ❌ | ❌ | ✅ |

## 六、适用场景

- **个人开发者**：快速生成原型、落地页、仪表盘
- **Agent 工具链**：作为 Agent 的设计能力补充
- **UI/UX 设计师**：快速迭代前端可视化方案
- **产品经理**：快速产生可演示的交互原型

## 七、核心结论

baoyu-design 填补了一个重要的空白：让 Agent 拥有独立的设计输出能力。它不只是"把 Claude Design 抄下来"，而是针对本地编辑器环境重新设计了工作流——通过内置浏览器预览+元素标注实现"指哪打哪"的迭代方式。对于脱离 web UI、完全在本地工作的开发者来说，这是一个实用的设计工具链补充。

**局限**: 需要较强的模型（Opus 4.8 效果最佳）；目前不支持多人实时协作；部分高级导出功能依赖外部工具。
