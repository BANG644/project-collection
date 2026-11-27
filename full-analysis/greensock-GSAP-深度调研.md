# 🔬 greensock/GSAP - 全方位深度调研

> 调研日期：2026-11-28｜本次为**全文重写旧账**（原稿停留在 README 转述 + 空口碑，无任何真实源码引用）

## 📌 一句话定位

GSAP（GreenSock Animation Platform）是 Web 动画领域的事实标准级 JavaScript 库：它用**时间轴（Timeline，可理解为"动画的剪辑台"，把多段动画按时间排布、暂停、倒放、嵌套）**把 CSS、SVG、Canvas、React/Vue 组件属性统一到一个高性能控制模型里。2025 年 4 月被 Webflow 收购后，全部插件（含过去收费的 SplitText/MorphSVG）100% 免费商用。

> 核心判断：GSAP 的护城河不是"能让元素动起来"，而是**复杂动画编排的确定性 + 跨浏览器兜底**。它真正稀缺的是二十年积累的"动画状态机 + 属性补间引擎"，而不是几行 CSS transition 能替代的东西。

## 🌟 项目亮点（差异化）

1. **单一 ticker 驱动全局**：整个库只有一个全局"心跳"（ticker），所有动画共享同一个时钟，天然避免多个 `requestAnimationFrame` 互相打架导致的抖动。默认按 **240fps 的时间粒度**计算而非 60fps，在 120Hz/144Hz 高刷屏上依然平滑。
2. **lagSmoothing（卡顿平滑）**：页面卡顿或标签页切后台时，GSAP 不会"补帧追进度"让动画突然跳一大截，而是主动吞掉超长间隔——这是它区别于手写 rAF 动画的关键工程细节（源码 `gsap-core.js:886-949`）。
3. **插件即属性处理器**：CSSPlugin、Flip、ScrollTrigger、Draggable 不是外挂，而是共享同一套 `PropTween` 链表的"属性渲染器"，因此能无缝混用与嵌套。
4. **2025-04 全部免费**：Webflow 收购后 Club GSAP 收费墙拆除，连调试工具与 SplitText 重写版都进公共 npm，商业使用零成本（[官方 3.13 公告](https://gsap.com/blog/3-13/)）。
5. **框架无关的底层模型**：绑定的是"属性随时间变化"这一底层抽象，React（`gsap.context()`）、Vue、Svelte、原生 JS 都能用，不随前端框架兴衰而失效。

## 🏗️ 项目全景 / 核心架构

| 维度 | 观察（2026-11-28 核实） |
|---|---|
| 仓库 | `greensock/GSAP`，https://github.com/greensock/GSAP |
| Stars / Forks | **31,373 / 2,483**（旧稿 25.9k 已过时） |
| Open issues | 仅 6（如此规模的库极低，说明 issue 非主要支持渠道） |
| 语言 / 分支 | JavaScript / `master`；最近推送 2026-11-04 |
| License | 仓库 metadata 未标注 SPDX（收购后改为 [标准免费许可](https://gsap.com/standard-license/)，商用免费，需阅读条款） |
| 生产采用 | 官方称 1100 万+ 生产网站使用（[tycp 评测](https://www.tycp.xyz/3082.html)转述） |

### 三层抽象

```text
Tween（单个属性从 A 到 B 的变化）
  └─ Timeline（把多个 Tween 编成一条时间轴：编排/暂停/倒放/嵌套）
       └─ Plugin（CSSPlugin / Flip / ScrollTrigger / Draggable ... 负责"具体属性怎么插值"）
                    ↑ 全部由同一个全局 ticker 心跳驱动
```

**架构关键点**：GSAP 不绑定任何 UI 框架，它绑定的是"对象的某个数字/字符串属性随时间变化"。所以 React 组件、SVG path、Canvas 对象、乃至普通 JS 对象都能被 tween——这也是它能活过 Flash 时代、jQuery 时代、React 时代的原因。

## 💡 应用场景与启发（重点）

- **营销页 / 滚动叙事**：ScrollTrigger 把滚动位置映射为时间轴进度，是"滚动到某处元素依次出现"这类效果的工业级解法。自己用 IntersectionObserver 写能跑，但要处理 scrub 平滑、pin 占位、resize、刷新时机，成本远高于用一个成熟插件。
- **复杂 UI 状态过渡（FLIP）**：Flip 插件实现 First-Last-Invert-Play——先记录元素位置，改 DOM，再用 transform 把元素"视觉上拉回原位"然后播放到新位置。这是列表重排、卡片展开这类动画的正确解法（手写极易布局抖动）。
- **给同类需求的思路**：如果你要做"编辑器 / 可视化 / 数据仪表盘"的动画层，不要自己造时间轴系统——直接把 GSAP 当**动画状态机内核**，业务层只负责声明"什么时候播哪段时间轴"。它的 `autoSleep`（无监听时自动停心跳）还给了移动端省电的现成答案。
- **反面启发**：`prefers-reduced-motion`（系统"减少动态效果"偏好）必须主动用 `gsap.matchMedia()` 接入；SplitText 拆出的文字若未写回 DOM，搜索引擎可能读不到原文（[tycp 评测](https://www.tycp.xyz/3082.html)）。**工具越强，团队越需要动效治理规范**。

## 🔍 源码深度解读（3 个核心模块，精炼）

### 1. 全局心跳与卡顿平滑 —— `src/gsap-core.js:886-949`

```js
_lagThreshold = 500, _adjustedLag = 33, _gap = 1000 / 240,
_tick = v => {
  let elapsed = _getTime() - _lastUpdate, manual = v === true, ...;
  (elapsed > _lagThreshold || elapsed < 0) && (_startTime += elapsed - _adjustedLag);
  ...
  manual || (_id = _req(_tick)); // 先排下一帧再派发，避免本帧耗时被计入帧间隔
  ...
},
lagSmoothing(threshold, adjustedLag) {
  _lagThreshold = threshold || Infinity;
  _adjustedLag = Math.min(adjustedLag || 33, _lagThreshold);
},
```

三个独家细节：① `_gap = 1000/240` 说明调度精度是 240fps 粒度；② 超过 500ms 的间隔（例如切后台回来）会被替换成 33ms，动画"跳过卡顿"而非"疯狂追帧"；③ 注释明确解释"先请求下一帧再派发"——否则本帧处理耗时会被叠加进下一次帧间隔，造成 16.7ms 变 31.7ms 的连锁延迟。这是 README 绝不会告诉你的工程决策。

### 2. 属性渲染器与单位切换 —— `src/CSSPlugin.js:26-48, 1061`

```js
_renderCSSProp = (ratio, data) => data.set(data.t, data.p,
  (Math.round((data.s + data.c * ratio) * 10000) / 10000) + data.u, data),
_renderCSSPropWithBeginning = ... ratio ? ... : data.b,   // ratio=0 时回退到原单位原值
_renderCSSPropWithBeginningAndEnd = ... ratio === 1 ? data.e : ...,
transformPropTween = this._pt = new PropTween(..., cache.renderTransform, cache, 0, -1);
```

`PropTween` 是一个链式链表（每新增渲染器插到表头），`-1` 这个优先级参数保证 transform 渲染器**最后执行**——因为 x/y/rotation/scale 必须聚合成一个 matrix 一次性写入，否则互相覆盖。三个渲染器变体专门处理"起点和终点单位不同"（如 `0` → `50vw`）时 ratio 恰为 0 或 1 的边界，这是无数动画库踩过的坑。

### 3. 自动休眠 —— `src/gsap-core.js:1989-1998`

```js
if (_ticker.frame >= _nextGCFrame) {
  ...
  if (!child || !child._ts) if (_config.autoSleep && _ticker._listeners.length < 2) {
    ... child || _ticker.sleep();
  }
}
```

没有活跃动画时直接 `cancelAnimationFrame` 停掉心跳，而不是空转。对移动端续航与后台标签页是实打实的收益——这是"为什么 GSAP 在复杂页面仍然省电"的源码级答案。

## 🌐 社区口碑画像（真实外链，非编造）

| 来源 | 关键信号 |
|---|---|
| [GSAP 官方 3.13 发布公告](https://gsap.com/blog/3-13/) | 100% 免费，原 Club 插件全部进公共 npm；SplitText 重写体积减半 + 14 项新特性，含 `aria-label`/`aria-hidden` 无障碍支持与 `autoSplit` 响应式重排 |
| [kevan.tv 老用户长评（2025-04-29）](http://kevan.tv/posts/2025-04-29-gsap-is-now-free/) | 正面："从 Flash 时代用到现在，异常稳定、功能完整"；担忧："被收购后不再需要为用户竞争，可能变成服务于 Webflow 的需求"；并指出 Rive 等新工具正在争夺注意力，遗憾"没做一个好 GUI" |
| [ToolTrim 评测](https://tooltrim.com/en/tool/gsap/reviews) | **3.8/5（Very good）**：适合复杂流畅动画；明确"只做简单 CSS 动画的人应另寻他处"，并提示"Webflow 生态可能影响路线图" |
| [tycp.xyz 中文实战评测](https://www.tycp.xyz/3082.html) | 核心约 25KB gzip + ScrollTrigger 约 10KB；Safari 的 `xPercent/yPercent` 需实测；React 中动画被 re-render 覆盖时用 `gsap.context()` 包裹；SEO 需注意 SplitText 文本是否入 DOM |
| [Webflow 收购官方说明（经 k 转载）](http://kevan.tv/posts/2025-04-29-gsap-is-now-free/) | 原班人马 Jack/Cassie/Rodrigo 继续维护，并与 Webflow 团队协作下一代原生 Interactions |

**口碑结论**：2025 年免费化几乎是单边利好，唯一的持续性争议是"独立性丧失后路线图是否向 Webflow 倾斜"。收费墙时代"插件值不值"的争论已彻底消失。

## ⚔️ 竞品对比

| 方案 | 定位 | 相对 GSAP 的优势 | 相对 GSAP 的劣势 |
|---|---|---|---|
| **CSS Transition/Animation** | 浏览器原生 | 零依赖、最简单 | 无法做复杂时间轴编排、运行时控制（倒放/跳转/seek）弱 |
| **Web Animations API (WAAPI)** | 浏览器标准 | 原生、可被浏览器优化 | 跨浏览器行为差异、缺高级抽象与滚动/拖拽插件 |
| **Framer Motion / Motion** | React 生态 | 与 React 声明式心智契合、API 简洁 | 强绑定 React；非 React 场景基本不可用；复杂编排能力弱于 Timeline |
| **Anime.js** | 轻量动画库 | API 简洁、体积小 | 插件生态与复杂场景（ScrollTrigger/Flip/Draggable）差距明显 |
| **Rive** | 设计师导向的交互动画工具 | 有 GUI、设计师可独立产出、"Rive 正在争夺 mindshare"（kevan.tv） | 需专有运行时与 .riv 资产，代码侧动态生成不如 GSAP 灵活 |

**研判**：GSAP 与 Rive 是"两条路线"——前者代码驱动、动态性强；后者设计工具驱动、可交付性强。二者可共存，不构成替代。

## 🎯 核心研判

- **优势**：① 全局 ticker + lagSmoothing + autoSleep 构成的"调度内核"二十年打磨，不是新库能短期复制的；② 插件生态覆盖真实商业网站的绝大多数动效需求；③ 免费化后采用门槛归零，1100 万+ 生产站点形成庞大的经验库（Stack Overflow 上问题几乎都有答案）。
- **风险**：① 体积——核心约 25KB gzip，全插件引入需 tree-shaking；② 动效治理——`gsap.context()` 清理、`prefers-reduced-motion`、SplitText 的 SEO 都要团队主动做；③ 独立性——Webflow 收购后的路线图倾斜是社区公认的长期观察点。
- **一句话结论**：**只要你的动画需求超过"淡入淡出"，GSAP 就是最省心的默认选择；但不要把它当"一键美化"工具——它给你的是确定性，不是审美。**

## 📂 关键文件路径速查

| 路径 | 作用 |
|---|---|
| `src/gsap-core.js` | 全局 ticker、lagSmoothing、autoSleep、Timeline/Tween 内核（约 3200 行） |
| `src/CSSPlugin.js` | CSS 属性补间、transform matrix 合成、单位边界处理（约 1100 行） |
| `src/Flip.js` | FLIP 布局过渡插件 |
| `src/ScrollTrigger.js` | 滚动触发动画（README 重点推荐） |
| `src/Draggable.js` / `src/Observer.js` | 拖拽与统一输入事件 |
| `src/SplitText.ts` / `src/MorphSVGPlugin.js` | 2025 免费化后进入公共仓库的明星插件 |
| `types/` | TypeScript 类型定义（支持现代 TS/React/Vue 工程） |

## 🧪 研究方法与数据来源

- GitHub API 元数据（2026-11-28 实时抓取：stars 31,373 / forks 2,483 / open issues 6 / pushed 2026-11-04）。
- 源码实读：`src/gsap-core.js`、`src/CSSPlugin.js`、`src/Flip.js`（抓自 `master` 分支），报告中的行号与代码片段均来自真实文件。
- 口碑：GSAP 官方博客、kevan.tv、ToolTrim、tycp.xyz 四条真实外链，含正反面观点。
- 未执行任何仓库代码；参数与体积数字均标注来源，无法独立验证的（如"1100 万站点"）注明为官方/第三方转述。
