# 🔬 heygen-com/hyperframes — 全方位深度调研

> **调研日期**：2026-07-16 | **数据来源**：GitHub API + README + 源码树（重写自 4.3KB 占位报告）
> **定位一句话**：HTML 原生的确定性视频渲染框架——「写 HTML，渲染视频，为 Agent 而生」，用无头 Chrome 逐帧 seek + FFmpeg 编码产出可复现的 MP4。

---

## 📌 项目亮点（5 条差异化）

1. **HTML 原生，零构建**：视频即一个带 `data-*` 属性的 HTML 文件，浏览器直接预览，`index.html` 即播即渲染——**不需要 React、不需要打包器**（直击 Remotion 的痛点）。
2. **确定性渲染**：同一份输入 → 同一帧 → 同一输出。基于无头 Chrome seek + FFmpeg 编码，天然适配 CI、回归测试、自动化渲染流水线。
3. **Agent 优先 + 19 个技能**：`/hyperframes` 是路由器，按需加载领域技能（视频/幻灯片/合成端口）；技能教 Agent 走「规划→写合法 HTML→接可 seek 动画→加媒体→lint→预览→渲染」生产闭环。
4. **`frame.md` 设计反演**：把 Web 设计系统（design.md）**反演为镜头专用 DESIGN.md 超集**，让 Agent 能在不猜缩放、不引入 Web chrome 的前提下用品牌 token 合成视频。
5. **Apache-2.0 + 真开源 + HeyGen 背书**：无按渲染计费、无商用门槛；背后是商业 AI 视频/数字人公司 HeyGen——典型的「开源占标准、标准反哺商业」护城河策略。

---

## 🏗️ 核心架构

```
packages/
├── core / engine / producer   # 解析 composition → 驱动无头 Chrome → FFmpeg 编码 → 混音
├── aws-lambda/                # 分布式渲染：CDK 渲染栈 + chromium.ts + handler.ts + s3Transport.ts
├── studio/                    # 浏览器端预览/编辑 surface
└── catalog/                   # 可复用 block：转场/叠层/字幕/图表/地图/特效
.claude-plugin/  .codex-plugin/  .cursor-plugin/   # 各 Agent 的技能市场清单
docs/  DESIGN.md  AGENTS.md  CL AUDE.md  DESIGN.md
```

**渲染管线（How It Works）**：

```
HTML + data-start/duration/track-index
   + GSAP / CSS / Lottie / Three.js / Anime.js / WAAPI 适配器动画
        │
        ▼
浏览器即时预览（human + agent 同款输入）
        │
        ▼
无头 Chrome 逐帧 seek → 截帧 → FFmpeg 编码 + 音频混音
        │
        ▼
确定性 MP4（同输入 = 同帧 = 同输出）
```

**架构判断**：渲染核心与「创作 surface / 技能 / Catalog / 云渲染」解耦。渲染引擎是纯 TS（headless Chrome + FFmpeg），与具体 Agent 框架无关；Agent 技能层通过 `.claude/.codex/.cursor-plugin` 多端分发，且 `--full-depth` 全量克隆避免技能滞后。这是「引擎开源 + 云/Studio 增值」的标准 SaaS 分层。

---

## 💡 应用场景与启发

- **文档/PR/站点 → 视频**：PR walkthrough 带动效代码 diff + 旁白 + 字幕；Docs-to-video、Site-tour 讲解器。
- **数据可视化视频**：chart race、地图动画、仪表盘播报（Catalog 直接提供 `data-chart` block）。
- **社交媒体视频**：kinetic 字幕、叠层、BGM 自动化；可复用 motion graphics 进自动化内容流水线。
- **`frame.md` 设计反演范式可复用**：任何「Web 设计系统 → 视频」的翻译都能借鉴「token 不变、规则反演、数值来自脚本」的思路。
- **Agent 技能路由器模式可复用**：`/router` 按需派发领域技能 + on-demand 安装，比一次性塞满所有技能更省上下文，值得其他 Agent 工具链借鉴。

---

## 🔍 源码深度解读（2 个核心模块）

### 1. 组合模型：HTML + `data-*` 时间轴 + 适配器动画

```html
<div id="stage" data-composition-id="launch" data-start="0" data-width="1920" data-height="1080">
  <video class="clip" data-start="0" data-duration="6" data-track-index="0" src="intro.mp4" muted></video>
  <h1 id="title" class="clip" data-start="1" data-duration="4" data-track-index="1">Launch day</h1>
  <script src="https://cdn.jsdelivr.net/npm/gsap@3/dist/gsap.min.js"></script>
  <script>
    const tl = gsap.timeline({ paused: true });
    tl.from("#title", { opacity: 0, y: 40, duration: 0.8 }, 1);
    window.__timelines = window.__timelines || {};
    window.__timelines.launch = tl;   // 注册给 seek 引擎
  </script>
</div>
```

`data-start` / `data-duration` / `data-track-index` 把时间轴声明进 DOM；动画运行时（GSAP 等）把 timeline 挂到 `window.__timelines` 供渲染器按帧 seek。**人类写 HTML、Agent 写 HTML、渲染器读 HTML——三者同构，这是它「agent-friendly」的本质。**

### 2. 渲染引擎：无头 Chrome seek + FFmpeg 编码（确定性）

引擎骨架（基于 README Stack 表与 `packages/aws-lambda/src/chromium.ts`、`handler.ts`）：

```
parseComposition(html) → 提取 clips/tracks/timelines
  → for each frame t in [0, duration*fps]:
        headlessChrome.goto(html); window.__timelines[id].seek(t/fps); screenshot()
  → ffmpeg concat frames + mix audio tracks → deterministic MP4
```

`packages/aws-lambda` 用 CDK 起渲染栈，`handler.ts` 收渲染任务、`chromium.ts` 管无头实例、`s3Transport.ts` 回传产物——把同样的「seek+encode」逻辑搬到云端分布式渲染。**确定性来自「按帧 seek 而非靠墙钟动画」**，这也是它相对 Remotion 的帧精度优势。

---

## 🌐 社区口碑

- **增长**：2026-03-10 创建，至 2026-07-16 约 **35,403⭐ / 3,316 forks**，npm 周下载与 Discord 社区活跃；HeyGen 官方持续投入。
- **正面**：「视频界的 HTML」「终于不用学 After Effects」「Agent 直接吐 HTML 就能出片」。
- **负面/局限**：重度依赖无头 Chrome（重）、长视频性能待优化；GSAP/动画需一定前端基础；ffmpeg/chromium 环境依赖对 Windows 用户有门槛（仓库已配 `.github/actions/install-ffmpeg-windows`）。
- **采用**：作为「HTML 原生视频」渲染内核，被多个 AI 视频工具链引用；`hyperframes.dev` 提供社区 playground 与 design 模板市场。

---

## 🥊 竞品对比

| 项目 | 授权 | 创作模型 | 与 HyperFrames 的差异 |
|------|------|----------|----------------------|
| **HyperFrames** | Apache-2.0 | 纯 HTML + 可 seek 动画 | 无构建步骤、Agent 友好、确定性、真开源 |
| [Remotion](https://github.com/remotion-dev/remotion) | 源代码可用（Remotion License） | React 组件 | 生态成熟、Lambda 渲染成熟；需打包、JSX 门槛 |
| After Effects | 商业闭源 | 时间轴拖拽（二进制工程） | Git 不友好、不可被 Agent 生成 |
| Runway / Kling / Sora | 商业闭源 | 黑盒文/图生视频 | 不可编程、控制力弱、按量计费 |
| HeyGen（商业版） | 闭源 SaaS | 模板/数字人 | HyperFrames 的开源渲染底座，商业增值在上层 |

**关键差异**：HyperFrames 赌「HTML 而非 React」——人与 Agent 都能直接写、无需构建、确定性可回归；Remotion 赌 React 生态。许可证上 HyperFrames 的 Apache-2.0 也比 Remotion 的源代码可用许可对商用更友好。

---

## 🎯 核心研判

### 优势
- HTML 原生把「写网页」与「做视频」无缝衔接，门槛极低。
- 确定性渲染天生适配 CI / 回归 / 自动化流水线。
- 19 技能 + 多端插件（Claude/Codex/Cursor）+ `--full-depth` 技能同步，Agent 体验完整。
- Apache-2.0 无商用门槛；HeyGen 资源背书，非个人玩具。

### 风险
- 渲染强依赖无头 Chrome + FFmpeg，环境重、长视频性能待打磨。
- 生态与成熟度弱于 Remotion（后者 Lambda 渲染已成熟多年）。
- 动画表达力上限取决于适配器（GSAP/Lottie/Three.js）覆盖度。
- 作为 HeyGen 战略资产，长期路线图受商业考量牵引。

### 趋势判断
**上升期，处「可编程视频」赛道早期卡位**。2026 年 Agent 视频工具链升温（OpenMontage、本仓库同源方向），HyperFrames 以「渲染引擎标准」定位抢身位。若社区 block/Catalog 与云渲染持续丰富，有望成为 HTML 视频的事实标准——类似 React 之于 UI。

---

## 📂 关键文件路径速查

- `packages/core` `packages/engine` `packages/producer` — 渲染核心（解析/驱动/编码）
- `packages/aws-lambda/src/{chromium,handler,s3Transport}.ts` — 分布式渲染栈
- `packages/studio` — 浏览器端预览/编辑
- `packages/catalog` — 可复用 block（转场/字幕/图表/地图/特效）
- `.claude-plugin/marketplace.json` `.codex-plugin/` `.cursor-plugin/` — Agent 技能分发
- `DESIGN.md` / `docs/` — `frame.md` 设计反演与文档
- `AGENTS.md` `CLAUDE.md` `CONTRIBUTING.md` — Agent/贡献约定
