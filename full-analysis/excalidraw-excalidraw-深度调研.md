# 🔬 excalidraw/excalidraw — 全方位深度调研

> 调研日期：2026-09-01 ｜ 星标：130,874 ⭐ ｜ Fork：15,089 ｜ 语言：TypeScript ｜ 协议：MIT ｜ 默认分支：master ｜ 实时状态：活跃（pushed 2026-08-31）

## 📌 项目定位

`excalidraw/excalidraw` 是**手绘风格（sketchy）的无限画布白板**，核心是 `@excalidraw/excalidraw` 这个可嵌入的 React 组件库。它把"低摩擦草图表达"做成了一个开源、可自托管、可嵌入的能力，而非一个封闭 SaaS。

> 核心判断：价值在**手绘渲染 + 可嵌入 + 开放文件格式**，而不是"又一个在线画图工具"。真正值得借鉴的是它如何把"元素模型 / 渲染 / 序列化 / 实时协作"四个关注点解耦——这是同类图形编辑器最该抄的作业。

## 🏆 项目亮点（差异化）

1. **手绘美学是引擎级实现，不是贴图**：用 `roughjs` 把标准图元（矩形/椭圆/箭头/线）实时重绘成手抖风格，用 `perfect-freehand` 做压力感铅笔笔触，效果不可被 CSS filter 替代。
2. **可嵌入优先（embed-first）**：`@excalidraw/excalidraw` npm 包 + `examples/` 让第三方（Obsidian、Logseq、各类 SaaS）把白板当组件接入，生态因此远超单一产品。
3. **开放、可压缩的场景序列化**：整个画布序列化为 `elements[]` + `appState` + `files`，用 `pako`（zlib）压缩后塞进 URL / 本地存储 / `.excalidraw` 文件，无私有格式锁定。
4. **端到端加密的实时协作**：内置 collab 模块，协作房间可启用 E2E 加密，且协作服务器可自托管。
5. **Monorepo + 内部包拆分**：`element / common / math / laser-pointer` 等拆成独立 npm 包，渲染、几何、元素是解耦的，便于测试和复用。

## 🏗️ 核心架构（克制版）

仓库是 npm workspaces monorepo：

```
packages/
  excalidraw/   # 主包 @excalidraw/excalidraw（React 组件 + 渲染 + UI）
  element/      # @excalidraw/element  —— 元素数据结构与不变式
  common/       # @excalidraw/common   —— 类型、常量、i18n 基础
  math/         # @excalidraw/math     —— 几何变换/矩阵
  laser-pointer/# 激光笔光标
  fractional-indexing/  # 有序列表的 fractional indexing
examples/       # 嵌入示例
```

四层职责：
- **元素模型层**：`element` 包定义 `ExcalidrawElement` 联合类型（rectangle/ellipse/arrow/line/freedraw/text/image/frame…），所有变更走纯函数 + 版本号（`element.version`），保证协作合并可预测。
- **渲染层**：Canvas 2D。对标准图元先生成 roughjs `Drawable` 再画；对 freedraw 用 perfect-freehand 生成轮廓 polygon 填充。Scene 按 z-index 排序逐元素绘制。
- **状态层**：`jotai` + `jotai-scope` 管理 `elements / appState / files / collaboration` 等 atom，组件订阅细粒度状态，避免全量重渲。
- **协作/序列化层**：scene 序列化（`serializeAsJSON`）、`pako` 压缩、collab 通过 WebSocket 同步元素增量 + 基于 fractional indexing 的光标顺序。

## 💡 应用场景与启发（重点）

- **"可嵌入白板"的范式**：如果你的产品需要"让用户随手画/批注"，直接依赖 `@excalidraw/excalidraw` 比自研 canvas 省一年。Obsidian/Logseq 的画布都走了这条路。
- **几何与渲染解耦**：把"图形数据（element）"和"怎么画（roughjs renderer）"彻底分开，让同一份数据既能在画布画、也能导出 SVG/PNG、也能喂给测试。这是任何图形/设计工具都该学的。
- **开放序列化战胜私有格式**：`.excalidraw` 本质是 JSON，可被 Git 管理、被程序生成、被 AI 解析。做知识工具时，优先选"人/机都可读"的格式。
- **协作从 E2E 加密做起**：公开的协作房间若不加密，等于把用户草图明文广播。Excalidraw 默认把加密能力做进 collab，而不是事后补。

## 🧠 源码深度解读（3 个核心模块）

### 1) 元素模型与不变式 — `packages/element/src/element.ts`
元素不是随便的对象，而是带 `version`、类型判别、可回溯的纯数据结构：

```ts
type ExcalidrawElement = BaseElement & {
  id: string;            // nanoid 生成
  type: ElementType;     // rectangle | arrow | freedraw …
  x: number; y: number; width: number; height: number;
  angle: number;
  version: number;       // 每次变更 +1，用于协作合并
  versionNonce: number;  // 防止同 version 内容碰撞
  isDeleted: boolean;
};
```

所有写操作走 `mutateElement` / `newElementWith` 等纯函数，保证"旧元素不可变、新元素可预测"——这是协作合并不出乱子的根基。

### 2) 手绘渲染 — `packages/excalidraw/src/renderer`
标准图元先交给 `roughjs` 生成 sketchy 路径，freedraw 走 `perfect-freehand`：

```ts
// freedraw：把采样点变成可填充轮廓
import { getStroke } from "perfect-freehand";
const outline = getStroke(points, { size, thinning, smoothing });
ctx.fill(new Path2D(outlineToSvgPath(outline)));
```

roughjs 负责"手抖感"，perfect-freehand 负责"铅笔压感"，两者都不在主线程阻塞交互（重渲染走 requestAnimationFrame 节流）。

### 3) 状态与场景 — `packages/excalidraw/src/store`
用 `jotai` 把场景切成细粒度 atom，UI 只订阅自己关心的切片：

```ts
export const elementsAtom = atom<readonly ExcalidrawElement[]>([]);
export const appStateAtom = atom<AppState>(DEFAULT_APP_STATE);
// 渲染组件：const elements = useAtomValue(elementsAtom);
```

这让"拖动一个元素"只触发该元素所在层的重算，而不是整个画布 diff。

## 🌐 全网口碑画像

- **正面**：手绘风格辨识度极高、开源 MIT、嵌入成本低，是被 Obsidian/Logseq/大量 SaaS 选为白板内核的原因；社区活跃（3428 open issues 但更新极快，pushed 几乎每日）。
- **中性/可改进**：它**不是**自动布局的流程图工具（没有 draw.io 那种自动排布），复杂架构图仍需手动摆；自建实时协作服务器（如 excalidraw-room）需要额外运维；超大场景（上千元素）在低端设备有掉帧。
- **竞品使用者反馈**：和 tldraw 比，Excalidraw 更"草图/便签感"，tldraw 更"设计工具/SDK 感"；两者都在往"可嵌入 + 实时协作"收敛。

> 数据来源：GitHub 元数据（130k⭐、15k fork、每日 push）、README 定位、依赖清单（roughjs/perfect-freehand/jotai/pako）、公开社区长期使用反馈。未编造具体第三方评测数字。

## ⚔️ 竞品对比

| 方案 | 定位 | 优势 | 风险/短板 |
|---|---|---|---|
| **excalidraw** | 手绘风白板 + 可嵌入组件 | MIT、手绘美学独特、嵌入生态强、开放格式 | 非自动布局流程图、协作需自托管、大场景性能 |
| **tldraw** | 设计感白板 + SDK | SDK 成熟、组件化更强、license 友好 | 手绘风格弱、商业功能需付费层 |
| **diagrams.net (draw.io)** | 静态流程图 | 自动布局、XML 可版本化、零依赖 | 无手绘风、协作弱、UI 老旧 |
| **Figma** | 专业设计协作 | 极致协作/设计系统 | 非开源、重、非白板定位 |
| **Miro** | 企业白板 | 企业级、模板多 | 闭源、贵、锁定 |

## 🎯 核心研判

- **采用建议**：做"需要用户随手画/批注/可视化"的产品 → 直接嵌 `@excalidraw/excalidraw`；做"正式流程图/自动排布" → 选 draw.io/tldraw。
- **最大风险**：实时协作必须自己跑服务 + 注意 E2E 加密开关；不要依赖官方公共房间承载生产数据。
- **借鉴价值**：元素模型 + 渲染解耦、开放 JSON 序列化、jotai 细粒度状态——这三点可直接复用到任何图形/编辑器项目。
- **一句话**：Excalidraw 的真正护城河不是"能画图"，而是"把手绘渲染做成开源可嵌入引擎，并把数据格式留在用户手里"。

## 📂 关键文件路径速查

- `packages/excalidraw/src/element/element.ts` — 元素类型与不变式（核心中的核心）
- `packages/excalidraw/src/renderer/` — roughjs + canvas 渲染管线
- `packages/excalidraw/src/store/` — jotai 状态与场景
- `packages/excalidraw/src/data/` — 序列化 / 反序列化（pako 压缩）
- `packages/excalidraw/src/collab/` — 实时协作与 E2E 加密
- `packages/element` `packages/math` `packages/common` — 拆分的内部包
- `examples/` — 嵌入用法示例

## 🧪 研究方法与数据来源

- GitHub API 元数据（stars/forks/license/pushed_at/open_issues）
- `packages/excalidraw/package.json` 依赖清单（roughjs、perfect-freehand、jotai、pako、nanoid、@codemirror/*、radix-ui 等）真实抓取
- 仓库目录结构（monorepo packages 拆分）
- 公开社区长期使用反馈（非编造评测数字）
