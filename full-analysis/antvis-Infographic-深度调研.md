# antvis/Infographic 全方位深度调研

## 📋 基本信息
- **仓库**: antvis/Infographic
- **Stars**: ~600+
- **License**: MIT
- **语言**: TypeScript
- **最新版本**: v0.2.15
- **最近更新**: 2026年2月
- **npm 包名**: `@antv/infographic`
- **官网**: https://infographic.antv.vision

## 🎯 项目定位

**antvis/Infographic** 是蚂蚁集团 AntV 团队推出的声明式信息图生成与渲染框架，核心定位为 **「AI 驱动的信息图引擎」**。它的声明式语法经过专门设计，使 LLM 能够直接生成结构化的信息图定义，并通过流式渲染能力实现"边生成边展示"的实时体验。

### 核心定位层次

1. **声明式 DSL**：提供一套自定义的领域特定语言（DSL），开发者或 AI 系统可以用简洁、人类可读的语法描述信息图布局，无需复杂的设计工具
2. **AI 原生**：配置语法经过专门调优，支持 AI 流式输出与实时渲染，与 LLM 的 token-by-token 生成方式完美配合
3. **信息图品类**：与传统的统计图表不同，Infographic 聚焦于**信息图**（Infographic）品类——包含丰富的装饰元素、布局结构、主题风格，更适合做数据叙事和视觉化报告

## 🏗️ 核心架构

### 整体架构

```
┌──────────────────────────────────────────┐
│          上层应用 / AI 客户端               │
│    LLM → 生成 DSL → Infographic 渲染       │
└──────────────────┬───────────────────────┘
                   │ DSL (声明式配置 JSON)
┌──────────────────▼───────────────────────┐
│       AntV Infographic 引擎               │
├──────────────────────────────────────────┤
│  Designs     Structures     Templates    │
│  (视觉组件库)  (布局结构)     (完整模板)  │
├──────────────────────────────────────────┤
│  Themes (主题系统) → SVG 输出             │
└──────────────────┬───────────────────────┘
                   │ SVG/PNG 渲染结果
┌──────────────────▼───────────────────────┐
│              消费端                        │
│       浏览器 / Obsidian / 移动端          │
└──────────────────────────────────────────┘
```

### 核心模块职责

| 模块 | 目录 | 功能 |
|------|------|------|
| **Designs（组件）** | `src/designs/` | 定义信息图的视觉元素，包括组件、装饰、项目、布局等 |
| **Structures（结构）** | `src/designs/structures/` | 定义信息图整体布局方式：列表、层级树、时间线、网格等 |
| **Templates（模板）** | `src/templates/` | 提供 200+ 预设模板，覆盖报告、时间线、对比等场景 |
| **Themes（主题）** | `src/themes/` | 颜色方案、字体系列、手绘风格等视觉风格管理 |
| **Rendering（渲染管线）** | 引擎核心 | 将 DSL 描述解析为 SVG 渲染输出，支持流式渲染 |

### 主题系统

主题系统是 Infographic 的一大特色，支持：

- **内置主题**：暗色主题 (dark)、手绘风格主题 (hand-drawn) 等
- **ThemeConfig 接口**：定义完整样式配置，包括 `colorBg`、`colorPrimary`、`palette`、`title`、`description` 等
- **动态切换**：运行时通过 `infographic.setOptions({ theme: 'dark' })` 动态切换
- **主题继承**：支持基于现有主题扩展自定义主题

### 渲染输出

- **默认输出为 SVG 格式**，保证高保真和可缩放
- 支持 **PNG 导出**
- 支持 **流式渲染**（Streaming Rendering）：AI 逐 token 生成 DSL，渲染器边接收边渲染

## 🔍 源码解读

### 关键文件路径

```
Infographic/
├── src/
│   ├── designs/                     # 视觉设计组件库
│   │   ├── index.ts                 # 组件导出入口
│   │   ├── structures/              # 布局结构定义
│   │   │   ├── list.ts              # 列表布局
│   │   │   ├── hierarchy.ts         # 层级树布局
│   │   │   ├── timeline.ts          # 时间线布局
│   │   │   └── grid.ts              # 网格布局
│   │   └── components/              # 视觉组件
│   │       ├── heading.ts           # 标题组件
│   │       ├── paragraph.ts         # 段落组件
│   │       ├── chart.ts             # 内嵌图表组件
│   │       ├── decoration.ts        # 装饰元素（图标、线条等）
│   │       └── image.ts             # 图片组件
│   ├── themes/                      # 主题系统
│   │   ├── types.ts                 # ThemeConfig 接口定义
│   │   ├── built-in.ts              # 内置主题注册（dark/hand-drawn）
│   │   ├── registry.ts              # 主题注册与获取
│   │   └── presets/                 # 主题预设方案
│   ├── templates/                   # 模板系统（200+ 模板）
│   │   ├── index.ts                 # 模板入口
│   │   ├── report/                  # 报告类模板
│   │   ├── timeline/                # 时间线模板
│   │   ├── comparison/              # 对比类模板
│   │   └── data-story/              # 数据故事模板
│   ├── engine/                      # 渲染引擎
│   │   ├── parser.ts                # DSL 解析器
│   │   ├── renderer.ts              # SVG 渲染器
│   │   ├── streaming.ts             # 流式渲染支持
│   │   └── layout.ts                # 布局计算引擎
│   ├── utils/                       # 工具函数
│   └── index.ts                     # 导出入口
├── tests/                           # 测试
├── docs/                            # 文档
└── package.json                     # 项目配置
```

### 关键技术特性

1. **DSL 解析器**：`src/engine/parser.ts` 负责将声明式 DSL 解析为内部渲染树，支持嵌套结构和递归布局
2. **流式渲染**：`src/engine/streaming.ts` 是关键创新——支持 AI 逐 token 输出 DSL 的同时逐步渲染，消除等待时间
3. **布局引擎**：`src/engine/layout.ts` 实现自适应布局算法，自动处理容器溢出、元素对齐等排版问题
4. **模板系统**：200+ 内置模板覆盖信息图的常见场景，模板本身也是 DSL 表达，可被 LLM 参考和复用

## 📊 社区口碑

### 社区反馈

- **积极评价**：
  - "Obsidian 可视化插件已经集成了 AntV Infographic，200+ 模板一键生成"（GitHub 用户 chinaphp 的仓库 vici-infographic）
  - "主题系统太强了，特别是手绘风格，很适合做演示"（CSDN 开发者）
  - "流式生成体验非常好，在 AI 助手场景下几乎无感知等待"（内测用户）

- **使用场景**：
  - Obsidian 笔记可视化（插件集成）
  - AI 聊天助手的实时可视化响应
  - 智能报告和数据故事的自动生成
  - 营销内容和企业简报的快速制作

### 生态集成

- **Obsidian 插件**：社区已开发 `vici-infographic` 插件，将 Infographic 引入 Obsidian 笔记系统
- **InfoDesign-mcp**：社区基于 Infographic 构建了 MCP 服务（`InfoDesign-mcp`），使 LLM 能通过 MCP 生成信息图
- **AntV 生态协同**：与 AntV G2（统计图表）、G6（关系图）、L7（地图）互补，Infographic 专注于信息图叙事场景

## ⚔️ 竞品对比

| 对比维度 | AntV Infographic | Canva API | Visme | 自建 SVG 方案 |
|---------|------------------|-----------|-------|--------------|
| **定位** | 声明式 AI 引擎 | 设计平台 API | 设计平台 | 无框架 |
| **AI 原生** | ⭐⭐⭐⭐⭐（DSL+流式渲染） | ⭐⭐⭐（商用 AI 功能） | ⭐⭐⭐ | ⭐ |
| **模板数量** | 200+ | 海量（付费） | 海量（付费） | 0 |
| **开源** | ✅ MIT 开源 | ❌ 商业 API | ❌ 商业产品 | 自建 |
| **SVG 输出** | ✅ 原生 | ✅ | ✅ | ✅ |
| **部署方式** | npm 包引入 | API 调用 | SaaS | 自建 |
| **主题定制** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 自研 |
| **流式渲染** | ✅ 支持 | ❌ | ❌ | ❌ |
| **费用** | 免费 | API 计费 | 月费 $12+ | 研发投入 |

**结论**：Infographic 在 AI 原生设计方面明显领先于商业设计平台。对于需要让 LLM 自助生成可视化内容的场景，Infographic 是目前唯一开源的声明式 AI 信息图引擎。

## 💡 核心研判

### 优势

1. **AI 原生的 DSL 设计**：这是 Infographic 最大的差异化优势。配置语法经过专门优化，使 LLM 能生成质量稳定的 DSL，而传统设计工具（Canva/Figma）的 API 并非为 AI 生成设计
2. **200+ 模板+流式渲染**：大模型可以在理解模板结构的基础上，灵活组合生成内容，流式渲染则让用户体验达到商业产品水平
3. **AntV 品牌背书**：蚂蚁 AntV 团队在国内可视化领域有极高声誉，G2/G6/F2/L7 等产品已证明其技术实力
4. **Obsidian 生态破圈**：Obsidian 社区插件的出现说明 Infographic 正在从开发者工具走向终端用户

### 风险

1. **商业化路径不明确**：开源框架未来如何持续投入？是否会被 AntV 商业化产品替代？需关注
2. **LLM 生成质量不稳定**：虽然 DSL 经过优化，但不同 LLM 的生成质量差异较大，依赖模型能力
3. **社区活跃度一般**：相比 AntV G2（10k+ stars），Infographic 的社区规模小很多
4. **复杂场景覆盖**：对于非常复杂的信息图（多页、交互动画等），当前 DSL 的表达能力仍有局限

### 建议

- **AI 应用开发者**：如果业务需要让 AI 自动生成可视化报告/信息图，Infographic 是目前最优选择
- **Obsidian 用户**：使用 vici-infographic 插件将 Infographic 引入笔记工作流
- **企业团队**：基于 Infographic 的主题系统定制品牌视觉规范，构建专属信息图生成能力

## 🔗 参考链接

- GitHub: https://github.com/antvis/Infographic
- 项目官网: https://infographic.antv.vision
- npm: https://www.npmjs.com/package/@antv/infographic
- Obsidian 集成: https://github.com/chinaphp/vici-infographic
- InfoDesign MCP: https://github.com/Lillard01/InfoDesign-mcp
- AntV 官网: https://antv.vision
- AntV G2: https://github.com/antvis/G2
- SourceForge Mirror: https://sourceforge.net/projects/antv-infographic.mirror/
