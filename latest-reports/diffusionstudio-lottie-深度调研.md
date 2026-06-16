# 🔬 diffusionstudio/lottie — 全方位深度调研

## 📌 一句话定位

**Text-to-Lottie 是一个让 AI 编码 Agent 生成生产级 Lottie 动画的开源框架。** 开发者只需文字描述，Agent 就能生成可在浏览器中实时预览、编辑和导出的 Lottie JSON 动画。

> — 把「AI 做动画」从咒语式生成变成了结构化工作流

---

## 🏗️ 项目架构全景

### 📊 核心指标

| 指标 | 值 |
|------|------|
| ⭐ Stars | 3,152 |
| 🍴 Forks | 163 |
| 📝 主语言 | TypeScript (SolidJS) |
| 📜 许可 | MIT |
| 🏢 背景 | Diffusion Studio（YC 公司） |
| 📅 创建 | 2026-06-04（仅 **12 天**） |
| 🔄 最后更新 | 2026-06-15 |
| 📦 安装方式 | `npx skills add diffusionstudio/lottie` |

### 架构分层

```
┌─────────────────────────────────────────────────────┐
│           Agent 层 (Claude Code / Codex)              │
│  接收文字 prompt → 理解 → 生成 Lottie JSON           │
│  通过 SKILL.md 指导工作流                             │
├─────────────────────────────────────────────────────┤
│           Player / 编辑器 (浏览器)                     │
│  SolidJS + Vite + Tailwind CSS + shadcn/ui           │
│  CanvasKit (Skia/Skottie) WASM 渲染                  │
│  多场景编辑 · 帧级操控 · 属性面板 · 热更新            │
├─────────────────────────────────────────────────────┤
│           生成产出层                                   │
│  public/projects/<project>/<scene>/lottie.json       │
│  zip 导出 · 实时预览 · Git 版本管理                   │
└─────────────────────────────────────────────────────┘
```

### 核心技术栈

| 组件 | 技术选型 |
|------|----------|
| 前端框架 | **SolidJS** (不是 React) v1.9.9 |
| 构建 | **Vite 7** + TypeScript 5.9 |
| UI | **shadcn/ui** (Solid 版) + Tailwind CSS 4 |
| 动画渲染 | **CanvasKit/Skottie** (Skia WASM 全功能渲染) |
| 压缩导出 | **fflate** (zip) |
| 路由器 | **@solidjs/router** |
| 字体 | Inter 可变字体 + JetBrains Mono |

---

## 🧠 独家发现

### 发现 1：不是 Lottie 生成器，而是「AI 动画框架」

这个项目**不是**像 Midjourney 那样直接「输入文字→生成动画」。它做的是：

1. 提供一个基于 Skia Skottie 的本地高性能播放器（WASM 渲染，非 lottie-web）
2. 让 AI Agent（Claude Code/Codex）通过 SKILL.md 学会如何结构性地**编写** Lottie JSON
3. Agent 在多场景目录下工作，playback 实时热更新（HMR）
4. 开发者通过属性面板操控 slot 值（颜色、文字、速度等）

本质上是**把 Lottie JSON 从黑箱变成 AI 可以理解和编写的结构化格式**。

### 发现 2：Skottie 而非 lottie-web

Skottie 是 Google Skia 的 Lottie 渲染引擎，优势：
- **原生 WASM 性能** — 比 lottie-web JS 渲染器快得多
- **一致的跨平台渲染** — 与 Chrome/Android 使用相同 Skia 引擎
- 文件来自 CanvasKit 的 `canvaskit-wasm` 包（~4MB WASM 二进制）

### 发现 3：Slot 控制机制

Lottie 的 slot 功能允许 After Effects 设计师在导出时标识"可替换属性"（颜色、文字、数值）。这个项目中通过 `applySlotValues()` 函数在运行时注入 slot 值，**实现无需重新导出即可调整动画外观**。

### 发现 4：Skill 驱动的工作流

使用 `skills` CLI 安装（`npx skills add diffusionstudio/lottie`），安装后 Agent 自动获得：
- 完整的多场景项目脚手架
- Skottie 渲染的注意事项（`SKILL.md` 中明确禁止使用 lottie-web）
- 帧级预览 URL（支持 `?frame=` 参数直接跳转）
- 实时热更新开发服务器

### 发现 5：CanvasKit 共享实例模式

`src/lib/canvaskit.ts` 中实现了 CanvasKit 实例的备忘录模式，主播放器和缩略图渲染器共享一个 WASM 实例，避免重复加载 ~4MB 的 Skia WASM 二进制文件。

---

## 🌐 全网口碑画像

| 来源 | 评价 |
|------|------|
| codeKK | 被收录为 TypeScript 优秀开源项目 |
| GitHub | 12 天 3.1K Stars，163 Forks，速度惊人 |
| Y Combinator | 关联公司 Diffusion Studio，已在 Top Companies 页面 |
| Discord | 提供官方 Discord 社区支持 |

### 关键观察

- **企业背书** — Diffusion Studio 是 YC 公司，其主力产品是 AI 视频处理平台，这个项目是其开源工具链的一部分
- **开发者工具定位** — 不是面向设计师（Figma/LottieFiles 竞品），而是面向开发者的动画生成工具链
- **社区增长快** — 12 天 3K+ Stars，说明 AI 动画生成这个需求被验证了

---

## ⚔️ 竞品对比

| 维度 | diffusionstudio/lottie | LottieFiles | AI 视频工具 (Runway/Pika) | Apple Motion |
|------|------------------------|-------------|---------------------------|--------------|
| **定位** | AI Agent 动画框架 | 动画市场+播放器 | AI 视频生成 | 专业动效 |
| **目标用户** | 开发者 | 设计师 | 创作者 | 设计师 |
| **AI 驱动** | ✅ Agent 生成 Lottie | ❌ 手动上传 | ✅ 全自动生成 | ❌ |
| **实时预览** | ✅ Skottie WASM | ✅ Web | ✅ 但等待 | ❌ |
| **开源** | ✅ MIT | ❌ | ❌ | ❌ |
| **Agent 工作流** | ✅ SKILL.md | ❌ | ❌ | ❌ |
| **Lottie 导出** | ✅ | ✅ 市场 | ❌ | ❌ |

---

## 🎯 核心研判

### 🟢 项目优势

1. **精准的开发者定位** — 面向「想用 AI 生成 Lottie」的开发者，而不是与已有设计工具竞争
2. **企业级技术选型** — SolidJS + CanvasKit WASM，性能远优于同类 Electron/JS 方案
3. **YC 背书** — Diffusion Studio 作为 YC 公司，长期维护性和商业化潜力优于个人项目
4. **Skill 生态** — 与 npx skills 生态绑定，安装即用，降低使用门槛
5. **实时预览工作流** — Agent 写 JSON → HMR 热更新 → 帧级 scrubbing → slot 可视化调节

### 🔴 项目风险

1. **依赖 CanvasKit WASM** — 4MB WASM 下载量对弱网络不友好；CanvasKit 不一定覆盖所有 Lottie 特性
2. **AI 生成质量** — 最终动画质量受限于 Agent 对 Lottie JSON 的理解精度，复杂动画仍需手动调优
3. **SolidJS 小众** — 相比 React，SolidJS 社区较小，招人/贡献门槛偏高
4. **与 Agent 版本绑定** — Claude Code / Codex 的 Lottie JSON 生成能力迭代速度影响用户体验
5. **时间太短** — 仅 12 天，还没经过充分的生产验证

### 适用场景 ✅

- 快速生成产品动画 / 加载动效 / 微交互
- Hackathon / Demo 中快速出动画效果
- 开发团队需要迭代 Lottie 而不依赖设计师
- AI Agent 驱动的动画生成流水线

### 不适用场景 ❌

- 需要精确帧级控制的高级动画
- 无 AI Agent 基础设施的纯设计团队
- 需要跨平台 Lottie 播放器的场景

### 趋势判断

**定位精准的高增长工具。** 12 天 3K Stars 加上 YC 公司背书，这个方向被验证了。「AI Agent 生成结构数据（而非直接输出）」这个模式（类似 jina-ai/reader 把网页转结构化 Markdown）可能是未来的主流范式。如果 Diffusion Studio 能持续优化 Agent 生成的 Lottie 质量（比如为常见动画类型（Logo reveal、跑马灯、加载动画）提供预设模板），项目生潜力可期。

---

## 📂 关键文件路径速查

| 文件 | 用途 |
|------|------|
| `skills/text-to-lottie/SKILL.md` | Agent 工作流指南（核心） |
| `src/lib/lottie.ts` | Lottie slot 值注入 |
| `src/lib/scene.ts` | 场景数据加载 |
| `src/lib/canvaskit.ts` | CanvasKit WASM 实例管理 |
| `src/lib/export.ts` | Zip 导出功能 |
| `src/lib/import.ts` | .lottie / .json 文件的导入解析 |
| `src/context/canvas.tsx` | 主播放器渲染上下文（19KB） |
| `src/context/scenes.tsx` | 多场景管理上下文 |
| `src/components/playback-controls.tsx` | 播放控制 UI |
| `src/components/scenes-container.tsx` | 场景容器 |
| `vite-plugins/scenes.ts` | 场景发现的 Vite 插件 |
| `scripts/copy-canvaskit.mjs` | CanvasKit WASM 复制脚本 |

## 🔗 参考链接

- GitHub: https://github.com/diffusionstudio/lottie
- npm: `npx skills add diffusionstudio/lottie`
- Discord: https://discord.com/invite/zPQJrNGuFB
- X/Twitter: https://x.com/diffusionhq
- YC: https://www.ycombinator.com/companies/diffusion-studio
