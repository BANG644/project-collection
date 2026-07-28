# 🎮 mshumer/Claude-of-Duty — 单个 prompt 生成的浏览器 FPS（Three.js + 多 Agent）

> 深度调研日期：2026-07-29 ｜ 数据来源：gh api 实时抓取 + `ARCHITECTURE.md` / `prompt.md` 走读
> 一句话：Matt Shumer（HyperWrite）用**一条 prompt** 让子 Agent 扇出协作，做出"达到现代 Call of Duty 质感"的浏览器 FPS——全程序化生成、零外部素材、Three.js r180 + WebGL2，是"AI 原生游戏工程"的标杆样本。

## 一、项目亮点（差异化）

- **一条 prompt 生成整款游戏**：`prompt.md` 全文仅 11 行，要求"做到最新 CoD 级别的 AAA 质感，扇出子 Agent 各自负责、各自用严苛批评者盲测对比 CoD 直到满意"——是"ultracode / 多 Agent 协作"最出圈的产物之一。
- **零外部素材 + 全程序化**：所有纹理/网格/动画/音频在加载时程序生成，无 CDN、无图片/HDRI/模型/音频文件，游戏完全离线可跑。
- **OVERWATCH 引擎契约**：`ARCHITECTURE.md` 定义了严格的子系统所有权模型（`你拥有你的目录，永不改别人的文件`）、运行时依赖注入（`ctx.get('fx')`）、确定性 RNG（`ctx.rng`，禁止 `Math.random`），把"多 Agent 并行写代码不互相踩"工程化。
- **电影级质量护栏**：明确"无平直未贴图表面、无均匀光照、物理合理值、无完美直线"等硬指标，并用"对抗性 critic 对照真实 CoD 帧"验收。
- **性能纪律严苛**：`update()` 内禁止 `new THREE.Vector3()`、预分配复用、显式 dispose——把 GC 抖动挡在帧循环外。

## 二、项目全景

| 维度 | 数据 |
|------|------|
| 🌐 GitHub | https://github.com/mshumer/Claude-of-Duty |
| 📦 Stars | ⭐ 1,527（抓取日 2026-07-25） |
| 🏷️ 语言 | JavaScript（Three.js r180 + Vite） |
| 📜 License | MIT |
| 🗓️ 创建 / 推送 | 2026-07-25 / 2026-07-25 |
| 🔧 形态 | 浏览器 FPS 游戏（单 prompt 多 Agent 生成） |

**定位**：它既是"游戏"，更是**多 Agent 软件工程的案例研究**——证明"把一个严苛引擎契约 + 一个扇出 prompt"交给编码 Agent，能产出传统单人难以短期完成的复杂交互系统。

## 三、核心架构（OVERWATCH 引擎契约）

子系统所有权表（来自 `ARCHITECTURE.md`）：

| id | 目录 | 负责 |
|----|------|------|
| `render` | `src/render/` | WebGLRenderer, HDR 管线, 后处理, CSM 阴影, 合成 |
| `materials` | `src/materials/` | 程序化 PBR 纹理, 共享材质库, triplanar/detail |
| `sky` | `src/sky/` | 物理天空, 日夜, IBL, 体积雾/光轴 |
| `world` | `src/world/` | 关卡几何, 模块化建筑套件, 静态碰撞 |
| `physics` | `src/physics/` | 宽相, 射线, 角色控制器, 刚体, 布娃娃 |
| `player` | `src/player/` | 移动状态机, 镜头手感, 冲刺/滑铲/攀越/倚靠 |
| `weapons` | `src/weapons/` | 武器网格, 机瞄, 后坐, 弹道, 换弹/检视动画 |
| `fx` | `src/fx/` | GPU 粒子, 枪口火光, 弹道, 弹着, 弹壳 |
| `ai` | `src/ai/` | 敌人, 导航, 感知, 掩体选择, 战斗行为 |
| `ui` | `src/ui/` | HUD, 准星, 命中标记, 击杀信息, 菜单 |
| `audio` | `src/audio/` | 合成武器/脚步音, 空间化, 混响 |

核心约束：
- **运行时依赖注入**：`const fx = ctx.get('fx')` —— 子系统互不 `import`，靠 `ctx` 取，这是并行安全的关键。
- **确定性 RNG**：`ctx.rng` / `ctx.rng.fork()`，禁用 `Math.random()`，保证可复现。
- **事件总线**：`ctx.events` 跨子系统通信（`weapon:fire` / `bullet:impact` / `damage:dealt` 等规范事件）。

## 四、应用场景与启发

- **AI 原生游戏生产**：证明"非程序员也能用一条 prompt 产出可玩 AAA 质感 demo"，对独立游戏/原型验证有颠覆性。
- **给同类需求的启发**（硬价值）：
  1. **多 Agent 协作的成败在"契约"不在"模型"**：OVERWATCH 用"目录所有权 + 运行时注入 + 确定性 RNG + 跨系统事件表"把并发写冲突消于设计，比事后 merge 可靠得多。
  2. **质量护栏要可验收**："对照真实 CoD 盲测"把主观"AAA 质感"变成可执行判据——任何 AI 生成内容都该有这种 critic 闭环。
  3. **性能纪律前置**：`update()` 内禁分配、预分配复用，是"AI 写的交互系统不卡"的底线规则，值得写进任何前端 AI 生成项目的 contract。

## 五、源码深度解读

### 5.1 `ARCHITECTURE.md` — 子系统接口契约

```js
export class MySystem {
  static id = 'mysystem';     // 唯一；他人如何找到你
  static deps = ['render'];   // 必须在你之前 init 的依赖
  async init(ctx) {}          // 建资源；可 await
  fixedUpdate(h, ctx) {}      // 可选，120Hz 确定性玩法
  update(dt, ctx) {}          // 可选，每帧一次
  dispose() {}                // 可选，释放几何/材质/纹理
}
```
`ctx` 提供 `scene/camera/get(id)/peek(id)/rng/time/events` 等；`config.q` 是质量预设（`q.taa/q.gtao/q.ssr/q.volumetrics`），任何系统不得超预算。

### 5.2 `prompt.md` — 生成的种子

```text
I want you to build a first-person shooter at the level of the most recent
Call of Duty games... Fan out sub-agents... have a separate sub-agent check
it visually... if it doesn't look triple A, keep going... /loop until perfect.
```
全文即"扇出 + 严苛 critic + 循环直到完美"——这是整个工程的种子，也是"ultracode"工作流的浓缩。

### 5.3 `src/main.js` + `src/core/` — 引擎核心

`main.js` (4KB) 是引导；`src/core/` 拥有 `rng.js`（确定性随机）、`config.js`（质量预设）、`prewarm.js`（首帧前编译所有材质，避免运行时卡顿）。`prewarm` 的坑："编译时必须绑定 render target，否则 warms 错变体"——体现作者对 Three.js 内部机制的深透。

## 六、社区口碑

- **正面**：发布即病毒传播，"一条 prompt 做出 CoD 级 FPS"成为多 Agent 编码能力的标志性 demo；OVERWATCH 契约被多家团队当作"AI 协作写复杂项目"的参考模板。
- **争议 / 局限**：
  - 项目最后一次推送即创建日（2026-07-25），疑似"一次性生成 demo"，后续维护/扩展未知。
  - 浏览器 WebGL2 性能上限决定它无法真正达到原生 CoD 的复杂度，定位仍是 demo/范式而非产品。
  - 完全程序化生成意味着美术风格高度依赖 critic 迭代质量，可控性弱于传统管线。

## 七、竞品对比

| 项目 | 生成方式 | 引擎 | 素材 | 定位 |
|------|---------|------|------|------|
| **Claude-of-Duty** | 单 prompt + 多 Agent | Three.js/WebGL2 | 全程序化 | AI 原生游戏范式 |
| 传统游戏（CoD 等） | 人工团队 | 自研/Unity/UE | 美术资产 | 商业产品 |
| 其他 AI 游戏 demo | 单 Agent | 各异 | 混合 | 实验 |
| 3D Gaussian / 生成式资产 | 模型生成 | — | 生成资产 | 资产侧 |

**判断**：CoD 的独特性在"多 Agent 协作契约 + 严苛 critic 闭环"，而非游戏本身；它是"AI 如何写复杂软件"的样本，类比价值高于游戏价值。

## 八、核心研判

- **优势（Moat）**：OVERWATCH 契约把"多 Agent 写复杂交互系统"工程化，是可复用的元方法论；全程序化 + 离线可跑降低分发成本。
- **风险**：单次生成、无持续维护、WebGL2 性能天花板；作为"产品"脆弱，作为"范式"才持久。
- **趋势**：与 Kimi Code / Claude Code 等编码 Agent 成熟同步，"一条 prompt → 可玩复杂系统"会从噱头变常规；关键基础设施会是"引擎契约 + critic 闭环"而非更强模型。
- **启发**：下次让 Agent 协作写任何复杂前端/游戏，先写一份 OVERWATCH 式契约（目录所有权 + 运行时注入 + 确定性 RNG + 事件表 + 质量护栏），远比调 prompt 有效。

## 九、关键文件速查

| 路径 | 作用 |
|------|------|
| `ARCHITECTURE.md` (9KB) | OVERWATCH 引擎契约（最佳阅读起点） |
| `prompt.md` (941B) | 生成种子 prompt |
| `src/main.js` (4KB) | 引导入口 |
| `src/core/` | rng / config / prewarm 等引擎核心 |
| `src/render/` `src/materials/` `src/sky/` | 渲染 / 材质 / 天空 |
| `src/world/` `src/physics/` `src/player/` `src/weapons/` | 关卡 / 物理 / 玩家 / 武器 |
| `src/fx/` `src/ai/` `src/ui/` `src/audio/` | 特效 / AI / UI / 音频 |
| `vite.config.js` `package.json` `index.html` | 构建与入口 |
