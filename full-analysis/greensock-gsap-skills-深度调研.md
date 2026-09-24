# 🔬 greensock/gsap-skills - 全方位深度调研

## 📌 一句话定位
`greensock/gsap-skills` 是 **GreenSock 官方出品的 GSAP AI 编程技能包**——一组面向 AI 编码 agent 的 `SKILL.md`，教大模型「正确地」用 GSAP（GreenSock Animation Platform）写动画，覆盖 core / react / scrolltrigger / plugins / performance / frameworks 六大技能，并附带 React/Vue/vanilla 多框架示例。

## ⭐ 项目亮点
- **官方背书 + 可信**：GSAP 是老牌动画库（Webflow Interactions 的底层引擎），官方亲自下场发 skill，等于把"十年动画最佳实践"沉淀成 agent 可消费的指令。
- **6+ 技能分而治之**：`gsap-core`（API 基础）、`gsap-react`（useGSAP）、`gsap-scrolltrigger`（滚动驱动）、`gsap-plugins`（Flip/Draggable 等）、`gsap-performance`（性能）、`gsap-frameworks`（框架集成）——按需加载、渐进披露。
- **多 harness 原生适配**：仓库根含 `AGENTS.md` / `CLAUDE.md` / `GEMINI.md`，`.github/instructions/` 给 Copilot 发 `react.instructions.md` / `scrolltrigger.instructions.md`，`.claude-plugin` / `.cursor-plugin` 提供 marketplace 分发。
- **示例即教材**：`examples/` 给 React / Vue / vanilla / Nuxt 四种可直接跑的样板（`useGSAP.ts`、`App.jsx`、`main.js` 等），让 agent 给出可运行而非臆造的代码。

## 🏗️ 项目架构全景
### 仓库结构（main 树）
- `skills/`：每个子技能一个目录，内含 `SKILL.md`（YAML frontmatter `name`/`description`/`license: MIT` + Markdown 指令）；可能含 `references/`。
- `examples/`：`react` / `vue` / `vanilla` / `nuxt` 四种框架的可运行项目（vite 配置 + 入口 + 组合式封装）。
- `.github/instructions/`：Copilot 专用指令文件。
- `.claude-plugin` / `.cursor-plugin`：`marketplace.json` + `plugin.json` 分发清单。
- 根 `README.md` + `assets/`（GSAP 品牌 SVG）。

### 设计模型
- frontmatter 的 `description` 用第三人称写「何时用 + 关键词触发」，便于 agent 在任务匹配时检索。
- 技能间用「Related skills」互链（core←timeline←scrolltrigger←react←plugins←performance），形成导航图。

## 💡 应用场景与启发
- **给前端 AI 工作流注入「动画正确姿势」**：大模型常写出性能差/跨浏览器不一致的动画（如直接 `transform` 字符串、用 `opacity` 而非 `autoAlpha`、`delay` 链动画）。这套 skill 把"不要做什么"也写进指令，显著降低 agent 产出的动画 bug。
- **「框架厂商发 Skill」范式样本**：与 `vercel-labs/skills`、`remotion-dev/skills` 同脉——库作者亲自维护 agent 技能，比社区零散 snippet 更权威、更与时俱进。
- **对自研体系的借鉴**：多 harness marketplace 分发（`.claude-plugin`/`.cursor-plugin`）+ `examples/` 可运行样板 + `instructions/` 给 Copilot，是 skill 包"好用、可发现、可审计"的标准做法，可参考到 WorkBuddy 的 skill 生态。

## 🧠 核心源码解读
### 1. transform 别名优先于原始 transform（性能 + 跨浏览器一致）
```javascript
// 推荐：GSAP 按 平移→缩放→旋转X/Y→skew→rotation 固定顺序应用，更高效可靠
gsap.to(".box", { x: 100, rotation: "360_cw", duration: 1 });
gsap.to(".fade", { autoAlpha: 0, duration: 0.5, clearProps: "visibility" });
```
`autoAlpha` 在值为 0 时同时设 `visibility:hidden`，避免不可见元素挡点击——这是手写 CSS 容易漏的细节。

### 2. 响应式 + 无障碍（matchMedia 自动 revert）
```javascript
let mm = gsap.matchMedia();
mm.add({ isDesktop: "(min-width: 800px)", reduceMotion: "(prefers-reduced-motion: reduce)" },
  (context) => {
    const { isDesktop, reduceMotion } = context.conditions;
    gsap.to(".box", { rotation: isDesktop ? 360 : 180, duration: reduceMotion ? 0 : 2 });
    return () => { /* 条件不再匹配时自动清理 */ };
  });
```
GSAP 3.11+ 的 `matchMedia()` 在媒体查询失配时**自动 revert** 该次创建的所有动画/ScrollTrigger，原生支持 `prefers-reduced-motion`。

### 3. immediateRender 叠加坑（多 from 同属性）
`from()` / `fromTo()` 默认 `immediateRender: true`，会对同一元素同属性渲染起始态——多个叠加时需给后发的设 `immediateRender: false`，否则后者覆盖前者起始态导致不可见。

## 🌐 全网口碑画像
- **定位共识**：被视为「官方教 AI 用 GSAP」的权威资源；GSAP 底层驱动 Webflow Interactions，因此调试 Webflow 动画时这套 skill 的相关性被 README 明确点出。
- **社区信号**：15.6k⭐ / 924 fork，发布即进入热门；官方维护保证与时俱进（2026-07 仍有更新）。
- **生态坐标**：属于「库作者亲自发 Skill」浪潮，与 `vercel-labs/skills`、`remotion-dev/skills` 互为印证。

## ⚔️ 竞品对比
| 维度 | gsap-skills | framer-motion/motion | anime.js | 纯 CSS 动画 |
|------|-----------|---------------------|----------|------------|
| 框架无关 | ✅（任意 JS） | 偏 React | ✅ | ✅ |
| 滚动驱动 | ScrollTrigger | 有限 | 有限 | 无 |
| timeline 控制 | ✅ 强 | ✅ | 中 | 弱 |
| agent 技能化 | 官方 6 技能 | 社区零散 | 社区零散 | 无 |

## 🎯 核心研判
- **优势**：官方、权威、覆盖核心场景、多框架示例可直接跑；把「动画反模式」写进指令，直接提升 agent 产出质量。
- **风险**：仅覆盖 GSAP 自身，不替代通用动画知识；依赖 agent 能正确匹配 `description` 触发对应子技能。
- **适用**：所有用 AI 写前端动画的开发者；**特别契合**本仓库调研者的 WorkBuddy skill 体系——其 marketplace 分发与示例样板值得借鉴。

## 📂 关键文件路径速查
- `skills/gsap-core/SKILL.md` — 核心 API 与最佳实践
- `skills/gsap-react/SKILL.md` — `useGSAP` 与 React 集成
- `skills/gsap-scrolltrigger/SKILL.md` — 滚动驱动
- `examples/react/App.jsx`、`examples/vue/app.vue`、`examples/vanilla/main.js` — 可运行样板
- `.github/instructions/react.instructions.md` — Copilot 指令
- `.claude-plugin/marketplace.json` — 分发清单
- 仓库：`https://github.com/greensock/gsap-skills`
