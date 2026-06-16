# 🔬 vorpus/performativeUI - 全方位深度调研

## 📌 一句话定位

**performativeUI 是 AI 创业公司 Landing Page 的「梗百科」** — 一个把"AI 网站看起来都一个样"这个行业现象做成 React 组件库的讽刺项目。

> — 不是严肃设计系统，而是一个包裹在 npm 包里的互联网文化 meme

---

## 🏗️ 项目架构全景

### 📊 核心指标

| 指标 | 值 |
|------|------|
| 创建时间 | 2026-06-07（**仅 9 天**） |
| ⭐ Stars | 710（9 天爆发增长） |
| 🍴 Forks | 19 |
| 📝 语言 | TypeScript (React 19) |
| 📜 许可 | MIT |
| 🔄 最后更新 | 2026-06-13 |
| 📦 版本 | v0.6.0 |
| 📏 Bundle Size | **30KB**（实测轻量） |
| 📰 媒体报道 | Gigazine（日本科技媒体） |

### 组件目录

| 类别 | 组件 | 梗点 |
|------|------|------|
| **Atoms** | `Sparkle` | 名词旁边加个 ✦，发布速度翻倍 |
| | `GradientText` | 紫蓝渐变文字，立显"十亿美元公司"气质 |
| | `StatusDot` | 永远是绿色，即使不该是 |
| | `QuestText` | 文字逐个浮现的"任务感" |
| **Primitives** | `Button` | glow/shimmer/ghost/so... 多种发光变体 |
| | `StickyBanner` | 顶部固定广告条 |
| | `EyebrowPill` | 小标签："New"、"Hot"、"3x faster" |
| **Heroes** | `Rotator` | 多个文案轮流展示的旋转传送带 |
| | `WordRoll` | 文字逐个滚动替换 |
| | `PromptHero` | 页面中央巨大输入框 + "Send" |
| | `AsciiHero` | ASCII 艺术大字 Hero |
| | `Goldeneye` | 鼠标悬停时揭示大字标题的特效 |
| **Backgrounds** | `Aurora` | 极光流动背景 |
| | `NodeGraphBackground` | 神经网络节点图背景 |
| | `FloatingSparkles` | 漂浮星星粒子 |
| **Surfaces** | `GlassCard` | 毛玻璃卡片 |
| | `MockIDE` | 假装 AI 在写代码的假编辑器 |
| **Conversation** | `ChatBubble` | AI 对话气泡 |
| | `TokenStream` | 逐字流式输出的文本动画 |
| | `WibblingSpinner` | **186 个动词轮播**的 Claude Code 风格 spinner |
| | `ChatFAB` | 右下角浮动聊天按钮 |
| **Business** | `PricingCard` | 三栏定价表，中间那栏高亮 |
| | `LogoMarquee` | 合作方 logo 流动条（懂的人都懂） |
| | `WaitlistForm` | Waitlist 注册表单 |
| | `CommunityBadge` | Discord/Slack 社群徽章 |
| **Marketing** | `BeforeAfter` | 前后对比滑块 |
| | `StatCounter` | 数字递增动画计数 |
| | `SlippyWords` | 文字滑动入场 |
| | `StickyBanner` | 底部固定提示条 |

---

## 🧠 独家发现

### 发现 1：这本质上是一个**文化批评**作品

performanceUI 不是工具库——它是**以 React 组件为媒介的讽刺漫画**。每个组件都精准对应一种 AI 创业公司 Landing Page 的原型设计模式：

- 紫色渐变 + 发光按钮 = "我们是 AI Native 公司"
- 中间那栏高亮的定价卡 = "是的，我们希望你选 Pro 版"
- 播放中的伪代码编辑器 = "AI 在写代码，相信我"
- 轮播动词 spinner = "你知道我们很认真，因为我们的 spinner 有 186 个动词"

这种"把讽刺做成可安装 npm 包"的思路非常互联网原生。

### 发现 2：代码质量出乎意料地好

虽然是讽刺项目，但代码质量远超"玩票"水准：

- **TypeScript strict mode** — 完整类型定义，`forwardRef` 支持
- **30KB bundle** — 实际的工程优化意识
- **完善的文档网站** — Vite 构建，GitHub Pages 部署，每个组件独立页面 + 交互演示
- **AGENTS.md** — 完整的技术文档，包括如何贡献组件、代码组织原则
- **CI 构建** — GitHub Actions Pages 自动部署
- **npm publish** — v0.6.0，已公开发布到 npm

### 发现 3：186 个动词的 WibblingSpinner 是亮点

`WibblingSpinner` 组件直接打包了 Claude Code 的完整 186 个动词表（从 "Accomplishing" 到 "Zigging"），模拟 Claude Code CLI 的旋转动画效果。这在 GitHub 上引发了大量转发和讨论。

### 发现 4：Research 目录坦诚揭露了抄袭来源

`research/` 目录包含了组件设计的灵感来源调研，以 Markdown 文件形式记录：
- `00_source_companies.md` — 调研了哪些 AI 公司的网站
- `01_typewriter_hero.md` — 打字机效果
- `02_logo_walls.md` — Logo 墙模式
- `03_node_graph_backgrounds.md` — 节点图背景
- `04_ascii_hero_art.md` — ASCII 艺术
- `05_aiified_ui_elements.md` — AI 化 UI 元素

这种"公开解剖"的创作风格是这个项目的隐藏亮点。

---

## 🌐 全网口碑画像

| 来源 | 评价 |
|------|------|
| **Gigazine（日本）** | "面向AI Startup网站的React组件库，把'所有AI公司网站看起来都一样'这个现象做成了梗" |
| GitHub 社区 | 9 天 710 Stars，病毒式传播 |
| 开发者 Twitter | "终于有人把这件事做成组件库了" |
| Hacker News | 已被广泛讨论（AI startup landing page cliché 话题） |

---

## ⚔️ 竞品对比

| 维度 | performativeUI | Tailwind UI | shadcn/ui | Acernity UI |
|------|---------------|-------------|-----------|-------------|
| **定位** | 讽刺 / 文化批评 | 专业模板 | 实用组件 | 实用组件 |
| **严肃可用** | ❌ 纯娱乐 | ✅ | ✅ | ✅ |
| **AI 主题** | ✅ 核心主题 | ❌ | ❌ | ❌ |
| **Bundle** | 30KB | 很大 | 按需导入 | 按需导入 |
| **开源** | ✅ MIT | ❌ | ✅ MIT | ✅ MIT |
| **npm** | ✅ v0.6.0 | ❌ | ✅ | ✅ |
| **文化价值** | 👍 极高 | ❌ | ❌ | ❌ |

**差异化**：没什么好比的——performativeUI 不是竞争对手，它是整个 AI UI 行业的**镜子**。

---

## 🎯 核心研判

### 🟢 项目优势

1. **病毒式传播** — 9 天 710 Stars，被 Gigazine 报道，说明切中了时代痛点
2. **代码扎实** — 虽然内容戏谑，但代码本身是可用的、高质量的 React 组件
3. **文化意义** — 它记录了"2026 年 AI 创业公司 Landing Page"这个特定历史时期的 UI 美学
4. **npm 可装** — `npm install performative-ui` 就能获得一套"嘲讽版"组件

### 🔴 项目局限

1. **不是生产级工具** — 你不可能在严肃产品里用这个——但这也是它的设计意图
2. **时效性** — 当 AI 创业公司的设计风格进化后，这个项目的引用价值会降低
3. **单人/小团队项目** — 作者 vorpus 个人项目，长期维护不确定

### 适用场景 ✅

- **演示 / 黑客松** — 快速搭建一个"看起来很 AI"的 Landing Page
- **教育 / 培训** — 用来展示"为什么不要这样做设计"
- **娱乐 / 社交媒体** — 发推特的素材库
- **文化记录** — 保留 2026 年 AI 网站设计的历史样本

### 不适用场景 ❌

- 任何正经的产品级场景

### 趋势判断

**短期爆发型文化作品。** 像大多数网络梗一样，生命周期很短（可能 2-4 周热点期），但会成为互联网文化档案中的一份有趣记录。项目本身可能不会持续更新，但"performativeUI"这个概念（形容 AI Startup 网站的浮夸设计）可能会成为设计圈的一个常用词。

---

## 📂 关键文件路径速查

| 文件 | 用途 |
|------|------|
| `src/index.ts` | 组件出口（全量 re-export） |
| `src/styles.css` | 统一样式（`.pui-*` 前缀） |
| `src/components/*.tsx` | 30+ 组件源码 |
| `src/hooks/*.ts` | 行为 hooks（useTypewriter, useTokenStream 等） |
| `docs/pages/Home.tsx` | 文档网站首页 |
| `docs/lib/meta.tsx` | 组件目录配置 |
| `research/*.md` | 设计灵感调研文档 |
| `AGENTS.md` | 贡献指南 |
| `vite.lib.config.ts` | 构建配置 |

## 🔗 参考链接

- GitHub: https://github.com/vorpus/performativeUI
- 文档: https://vorpus.github.io/performativeUI/
- npm: https://www.npmjs.com/package/performative-ui
- Gigazine: https://gigazine.net/news/20260609-performative-ui/
