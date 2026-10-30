# wheresryan22/anatomy 深度调研

> 调研日期：2026-10-31 ｜ 数据来源：GitHub API（README / `SKILL.md` / `examples/` 源码树）
> 许可证：**MIT** ｜ 形态：给 Claude Code / Antigravity / OpenCode / Codex / MiniMax Code 用的 Agent Skill（Node 内置模块，零依赖）

## 项目亮点（差异化）

- **「物体即解释」的核心思想**：不讲概念画框加箭头，而是**发明一台真实、精密、可动的物理机器**，其运作方式恰好就是概念本身——缓存键跳过重复工作 = 弹子锁（每根针都对齐才转动）；单一 GPU 上下文服务多画布 = 龙门绘图仪（一个打印头走访 16 个井）。
- **零依赖 + 框架无关**：只用 Node 内置模块（Node ≥ 20.10），无需 `npm install`，可产出独立 HTML/SVG，也支持 React/Next.js（`kit/react/`）。
- **几何自证（audit）**：`kit/audit.mjs` 用 `A.auditOrExit` 在静止/拆解/爆开每一帧做射线求交，证明「任何管道不穿任何东西、每端落在真实支座、无弯曲夹扁、深度顺序正确」，`node build.mjs --audit` 必须 `audit passed` 才能交付。
- **真实 WebGL 着色器**：火焰/排气/水/焦散/灯光等效果活在 SVG 同一等距相机里（`kit/gl.mjs`），统一世界空间、包络驱动、无突跳。
- **可出版**：一键导 A4 PDF（海报/绘图/讲义），并可选发布到社区画廊。

## 项目定位（一句话）

Anatomy 是一个**让 Agent 把技术概念「建成一台会动的真实机器」的技能**——用几十到上百个精密小零件拼出等距 SVG/WebGL 图解，靠几何审计保证正确，用来替代「盒子+箭头+标签」式的平庸示意图。

> **22.9k⭐**（2026-10-08 创建、10-18 仍活跃，当日 Trending 上榜），MIT，JavaScript，**最近推送 2026-10-18**，1.9k fork / 70 open issues。

## 核心架构

- **入口 `SKILL.md`**：定义 `name/description/license/compatibility/metadata`，把「何时用、怎么建」一行化；核心是「10 步工作流」——先定尺寸（Figure/Hero/Epic 三档，40–150+ 零件）、truth first 收集真实数值、invent the object、写 ≥40 零件清单、规划世界坐标与相机（azimuth 45°、elevation 30°）、几何只建一次、画家算法 back-to-front、装进带 `Fig n`/标题/提示/实时读数的卡片、calm eased motion、critic 式自检。
- **`kit/` 工具库（核心）**：`iso-kit.ts/.mjs`（相机+实体+零件库+SVG 渲染器+卡片/页构建器+CSS，单文件核心）、`lathe.mjs`（任意轴回转体，平滑着色自启）、`tube.mjs`（管道/线缆按深度切片）、`audit.mjs`（几何证明）、`gl.mjs`（WebGL 着色器层）、`turn.mjs`/`turn-build.mjs`/`turn-audit.mjs`（可选 3D 模式）、`scripts/`（capture/drive/lines/print 等 headless Chrome 校验与 PDF 导出）。
- **`examples/` 8 个完整样例**：`dial-indicator`（最小，~300 行）、`desk-computer`、`arcade-cabinet`（~240 实体+15 线缆，投币机制真实物理）、`raptor-engine`（11 组件爆开+WebGL 羽流，审计标杆）、`ripple-tank`（双 WebGL 层+真实光学模型）、`test-rig`、`spot-plate`、`turning-dial`（3D）。
- **`agents/openai.yaml` + `evals/evals.json`**：跨 Agent 兼容与评测。

## 源码深度解读（核心模块：几何审计与等距工具库）

**1. 几何审计是交付硬门槛（`SKILL.md` 工作流第 7、10 步 + `kit/audit.mjs`）**

```js
// kit/audit.mjs 由 SKILL.md 描述的契约
recorder(P, { order, spring })   // 收集实体/形状/路线（随绘制记录真实形状）
settle(R, P)                     // 对所有重叠对射线求交取真实深度，静止/拆解/爆开三态
auditOrExit(R, P)                // 跑全部检查：clearances / terminals / looseEnds /
                                 //   folds / selfOverlaps / crowding / coverage / wobble /
                                 //   seats / depthOrder，任一不过 → 非零退出
```
`node build.mjs --audit` 必须打印 `audit passed`、失败行全为 0；`scripts/lines.mjs` 再把「每条线必须落在描边/点/轮廓上」（`line ends: 0`）作为第二道审计。这是把「美术正确性」固化为可机器检查不变量的典型做法——**修复在几何里，永不在视觉偏移（key bias）里**。

**2. 工具库把等距渲染拆成可组合原语（`kit/iso-kit.ts`）**

`slabOf` / `cylinder` / `extrude` / `planOutline` / `topTicks` / `knurl` / `coil` / `radialTicks` 等原语，加上 `lathe.mjs` 的 `frameAlong`/`lathe`/`solidOf` 与 `tube.mjs` 的 `tubePieces`/`tubeSvg`，让「一个打印头走访 16 井」这类概念能被程序化重建且自动深度排序。React 侧 `kit/react/draw.tsx`（`Solid`/`Line`/`Wire`/`FaceText`/`IsoFigure`）做服务端安全组件，`live.tsx`（`useReadout`/`useLoop`/`useEased`/`useInView`/`useStillness`）做客户端动效——**几何留纯 `.ts` 模块、动效留 `"use client"` 组件**的分工值得借鉴。

## 应用场景与启发

- **文档/博客/落地页的「解释性图解」**：需要讲清楚一个算法、组件、系统如何运作时，用 Anatomy 生成可交互等距图，比静态框图信息密度高一个量级，且每个数字都来自驱动零件运动的同一个模型。
- **「概念→隐喻物体」的设计方法论**：把抽象机制映射成可识别机器的思路，可直接迁移到教学动画、产品原理演示、API 文档。
- **「美术正确性可机器审计」范式**：用 `auditOrExit` + `lines.mjs` 把「图对不对」变成 CI 可跑的硬检查，任何生成式视觉产物都可套用这道闸门。
- **零依赖 + 跨 Agent 分发**：`npx skills add` 一键装到 5 种 Agent，纯 Node 内置模块，对离线/受限环境友好。

## 社区口碑

- **增长极快**：2026-10-08 才创建，不到一个月冲到 **22.9k⭐** 并登上 GitHub Trending，说明「AI 生成高质量技术图解」需求强烈；MIT、零依赖、跨 Agent 兼容，口碑以「惊艳/细节控」为主。
- **质量标杆明确**：官方以 `test-rig`（绘图质量）与 `raptor-engine`（着色器质量）为双标杆，`--audit` 强制几何正确，社区反馈普遍认可其「拼装感、体积感、4× 放大仍有细节」。
- **采用摩擦**：需要 Chrome/Chromium 跑 headless 校验与 PDF；超大 Epic（6h+）需人工确认才启动；纯 SVG 非照片级，写实渲染不是目标。
- **主观满意度数据不可用**：精确 NPS 无第三方统计；上述基于 README 自述与 Trending 表现。

## 竞品对比

| 维度 | Anatomy | Excalidraw / tldraw | Mermaid / 框图 | 手绘 SVG（D3） |
|------|---------|---------------------|----------------|----------------|
| 产物 | 可交互等距机器（SVG+WebGL）+ PDF | 手绘风白板 | 文本生成框图 | 自写代码 |
| 信息密度 | 极高（零件+动效+读表） | 中 | 低 | 取决于作者 |
| 正确性保障 | `auditOrExit` 几何审计 | 无 | 无 | 无 |
| 真实感 | 体积感强、4× 有细节 | 扁平手绘 | 扁平 | 看手艺 |
| 自动化 | Agent 一键生成 | 需手画 | 文本驱动 | 需写代码 |

## 核心研判

- **价值清晰**：在「要解释清楚一个系统/算法、还要好看可交互」的场景里几乎没有对等物；其「物体即解释」+「几何可审计」的组合是生成式技术图解的高水位。
- **边界明确**：它是**示意图（diagram）的升级，不是插画/写实渲染工具**；超大图耗时长、需人工确认，照片级不是目标。
- **采用建议**：写技术博客、API 文档、教学材料时优先试；引入前确认宿主环境有 Chrome（跑 `--audit`/PDF）；把 `auditOrExit` 思路带回任何「视觉产物需可信」的 agent 工作流。

## 关键文件路径速查

- `SKILL.md` — 入口路由器（10 步工作流 + 尺寸分档 + 核心思想「物体即解释」）
- `kit/iso-kit.ts` · `kit/iso-kit.mjs` — 等距核心（相机/实体/零件库/SVG 渲染/卡片）
- `kit/lathe.mjs` · `kit/tube.mjs` — 回转体 / 管道线缆（深度切片）
- `kit/audit.mjs` — 几何审计（`recorder`/`settle`/`auditOrExit`）
- `kit/gl.mjs` — WebGL 着色器层（`GLSL_ISO`/`glLayer`）
- `kit/turn.mjs` · `turn-build.mjs` · `turn-audit.mjs` — 可选 3D 模式
- `scripts/capture.mjs` · `drive.mjs` · `lines.mjs` · `print*.mjs` — headless 校验与 PDF 导出
- `examples/{dial-indicator,arcade-cabinet,raptor-engine,ripple-tank,test-rig,...}` — 8 个完整样例（质量标杆）
