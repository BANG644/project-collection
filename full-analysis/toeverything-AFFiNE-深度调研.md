# 🔬 toeverything/AFFiNE - 全方位深度调研

> 调研日期：2026-11-20 ｜ Star：75,010 ｜ 语言：TypeScript + Rust ｜ 许可：MIT（编辑器）/ source-available（后端）｜ 默认分支：canary
> 仓库：https://github.com/toeverything/AFFiNE ｜ 本报告编号 #608

## 📌 一句话定位

**本地优先、可自托管的"知识操作系统"**——把 Notion 的文档/数据库、Miro 的无限画布、Airtable 的多视图表格揉进同一个"everything is a block"的编辑器内核（BlockSuite），文档和白板在同一张画布上自由切换，数据留在你自己的磁盘上。它不是"又一个 Notion 克隆"，而是一个把编辑器内核（BlockSuite）和协作后端（OctoBase）都开源出来、可供二次开发的底座。

## ⭐ 项目亮点

1. **Docs 与白板真正"超融合"（hyper-merged）**：不是文档里嵌个白板，而是同一个 block 可以放到 edgeless 无限画布上——富文本、便签、网页嵌入、多视图数据库、链接页、形状、幻灯片同构共存（README "What is AFFiNE" + 第三方实测）。这是它相对 Notion（block 只能纵向堆叠）和 Miro（文档能力弱）的核心差异。
2. **BlockSuite 是可独立复用的编辑器框架**：`blocksuite/framework/{std,store,sync,global}` 四包 + `blocksuite/affine/{blocks,data-view,gfx,inlines,widgets...}`，第三方可以只拿 BlockSuite 造自己的 block 编辑器——`blocksuite.io` 单独有站。这把"知识 OS"的野心从产品下沉到框架层。
3. **CRDT + 本地优先 + Rust 引擎**：yjs 做 CRDT，自研 `y-octo` 兼容层做高性能本地引擎，后端 OctoBase 用 Rust（Cargo workspace + napi-rs 暴露给 Node），实现"离线全功能 + 冲突无关同步"（来源：README、CSDN 技术解析、tubrief 视频技术段）。
4. **激进的多端 + 每日 canary 发布**：桌面（Electron/Tauri）、Web、iOS/Android 客户端（`packages/frontend/apps/ios/AGENTS.md` 存在）、MCP server（社区 affine-mcp-server 已过 MarketNow L1.5 认证，Issue #15869），默认分支 canary 每日发版（v2026.11.18-canary.905 等）。
5. **双许可结构的诚实商业模式**：编辑器与大部分代码 MIT，后端 server 用 source-available 企业版许可（MakeUseOf 实测确认）——把"开源核心 + 商业后端"的边界摆明，而不是假装全 MIT。

## 🏗️ 项目架构全景

### 目录结构 + 设计哲学

12859 文件的巨型 monorepo，Yarn 4（Berry）+ workspace 覆盖 `blocksuite/**/*`、`packages/*/*`、`packages/frontend/apps/*`、`tools/*`。三大顶层：

| 目录 | 职责 |
|------|------|
| `blocksuite/` | 编辑器内核：`framework/{std,store,sync,global}`（vanilla 框架）+ `affine/{blocks,data-view,gfx,model,rich-text,widgets,ext-loader...}`（AFFiNE 具体 blocks）|
| `packages/frontend/` | 前端应用（含 `apps/ios`）|
| `packages/backend/` | `server`（NestJS 风格 `app.module.ts`/`schema.gql`）+ `native`（Rust 绑定）|

设计哲学：**编辑器内核与产品应用分离**。BlockSuite 是"vanilla framework"，AFFiNE 是构建其上的产品——这让框架可以脱离 AFFiNE 独立使用，也是扩展性的来源。

### 技术栈 & 依赖图谱

- 前端：React + Vite + TypeScript，状态管理 Jotai，跨端 Electron/Tauri（`src-tauri/` 存在），UI 从 Ant Design 逐步迁到自研 `frontend/src/ui/` 原语（见 DESIGN.md App Layer）。
- 编辑器：TypeScript，Yjs CRDT，RxJS（`engine.ts` 的 `Subject`），自研 y-octo 兼容层。
- 后端：NestJS（`.module.ts`/`.gql`）+ Rust（OctoBase，`Cargo.toml`/`Cargo.lock`/`rust-toolchain.toml`，napi-rs 桥接）。
- 工具链刻意保守（CSDN 观察："工具链选择保守稳定，没有追逐小众框架"），降低贡献者上手成本。

### 核心配置一览

- 默认分支 `canary`（不是 main）——所有 canary 版本从此出；beta 版本（v0.27.5-beta.3）并行。
- `package.json` workspaces 通配 + `.yarnrc.yml` + `yarn.lock`，`oxlint`/`oxfmt`（新一代 lint/format 工具）出现在根目录配置。

## 💡 应用场景与启发（重点章节）

### 典型使用场景

1. **个人/团队知识库自托管**：敏感数据不想上第三方云，用 Docker Compose 起一个实例（官方 `docker-compose.yml`），本地模式无限 workspace、无限制编辑。
2. **文档 + 架构图同处一地**：写 Spec 时直接在文档旁的无边画布上手绘架构图、贴 GitHub issue、放 Figma 嵌入——单一事实来源， eliminating context switching（tubrief 实测演示）。
3. **播客/课程笔记的"项目化"**：把研究笔记关联到活跃项目，用 collection 组织、块引用复用（MakeUseOf 实测："AFFiNE better at turning notes into work"）。
4. **二次开发编辑器**：只要块编辑器内核，用 BlockSuite framework 自建带自定义 block 的应用（web component 扩展）。

### 可借鉴的解决方案模式

- **"框架/产品"分层开源**：把可复用内核（BlockSuite）与产品壳（AFFiNE app）分目录、分品牌、分站点运营，让内核成为生态入口而非产品附庸。任何想做"平台型开源工具"的项目都可借鉴。
- **CRDT 多源同步的 main + shadow 模式**：`DocEngine` 不是单点同步，而是一个 main source + 多个 shadow source，先同步 main 完成再起 shadows，之后持续同步（源码 `engine.ts` 注释的 4 步）——这是"本地优先 + 多端 + 冲突愈合"的通用骨架。
- **native ↔ Y 双向桥接的 transform 钩子**：`native2Y`/`y2Native` 都带 `transform(x, original)` 回调——把"业务对象 ↔ CRDT 类型"的转换做成可注入的，而不是写死映射。

### 同类需求的可参考思路

做"本地优先协作应用"时，AFFiNE 的三层答案值得抄：**存储层**（Yjs CRDT 保证合并）→ **响应式层**（reactive proxy/`Boxed` 把 Y types 包装成可观察对象）→ **同步层**（DocEngine 多 source 编排）。痛点不在 CRDT 本身，而在"CRDT 数据如何优雅地喂给 React 渲染"——AFFiNE 用 `reactive/proxy.ts` + `native-y.ts` 回答了这个问题。

### 可复用片段

- `DocEngine` 的 status 状态机（step/main/shadows/retrying）+ `onStatusChange: Subject<DocEngineStatus>`：把同步进度建模成可观察状态，UI 可直接订阅。
- `native2Y`/`y2Native` 的递归转换（Boxed/Text/YArray/YMap 四型分派 + deep 开关 + transform 钩子）：一块可直接拿去用的 CRDT 序列化骨架。
- DESIGN.md 的"克制设计系统"：双主题不是反相而是"重设表面层级 + 强调色提亮 10-15%"——产品级 UI 规范的教科书。

## 🧠 核心源码解读（克制代码量）

### 入口与主流程

默认分支 `canary`；`packages/backend/server/src/{app.module.ts,schema.gql,server.ts}` 是 NestJS 后端入口；`blocksuite/framework/` 是内核。CRDT 同步的主流程在 `blocksuite/framework/sync/src/doc/engine.ts`。

### 关键模块 1：`sync/doc/engine.ts` — DocEngine 多源同步

```typescript
// 源码注释中的结构图（精简）
//   DocEngine → DocPeer(main)
//                 ├→ DocPeer(shadow)
//                 ├→ DocPeer(shadow)
//                 └→ DocPeer(shadow)
// 同步步骤：1 起 main → 2 等 main 完成 → 3 起 shadows → 4 持续同步
export class DocEngine {
  private _abort = new AbortController();
  readonly onStatusChange = new Subject<DocEngineStatus>();
  readonly priorityTarget = new SharedPriorityTarget();
  constructor(readonly rootDoc: Doc, readonly main: DocSource,
              readonly shadows: DocSource[], readonly logger: Logger) { ... }
}
```
设计要点：main 与 shadows 优先级不同（`SharedPriorityTarget`），失败可 `retrying` 状态重试，`AbortController` 统一取消——不是简单的 `yjs`  provider 堆叠，而是有编排语义的同步引擎。

### 关键模块 2：`store/reactive/native-y.ts` — 业务对象 ↔ CRDT 桥

```typescript
export function native2Y<T>(value: T, { deep = true, transform = x => x } = {}): Native2Y<T> {
  if (value instanceof Boxed) return transform(value.yMap, value);
  if (value instanceof Text)  return transform(value.yText.clone(), value);
  if (Array.isArray(value)) { const y = new YArray(); y.insert(0, value.map(...)); return transform(y, value); }
  if (isPureObject(value))  { const m = new YMap(); Object.entries(value).forEach(...); return transform(m, value); }
  return transform(value, value);
}
// y2Native 是镜像：YText→Text, YArray→[], YMap→{}
```
独家细节：`Boxed` 是 AFFiNE 对"一个包装过的 Y 类型"的抽象，`Text` 对 YText 做 clone（避免共享 doc 引用污染）。`_opensre` 式内部标记这里没有，但有 `stash-pop`（响应式栈操作）等配套模块。

### 关键模块 3：`store/yjs/` — Yjs 适配层

`yjs/{index,utils,awareness}.ts` 把 Yjs 的 Doc/awareness 封装为框架内类型，`SubdocEvent`（loaded/removed/added）处理子文档生命周期——AFFiNE 的"每个页面是一个 subdoc"模型在此落地。

### 隐藏功能 & 未文档化特性

- `blocksuite/playground/`：BlockSuite 的独立演练场，验证"框架脱离 AFFiNE 可用"。
- `mcpb/` 目录 + Issue #15869（affine-mcp-server 认证）：官方源代码树里已为 MCP 集成留位置。
- `backend/presets/`、`backend/plugins/`：预设与插件体系的雏形，对应路线图上的"插件社区"。
- `DESIGN.md` 里"App Layer"约定新页面不许直接用 AntD `Card/Tag/Tabs` 搭版面——能看出团队正在做一次大规模 UI 重构，README 完全没提。

## 📐 架构决策与设计哲学

- **ADR 摘要**：无独立 ADR，但 DESIGN.md（`AutoClip 也有同款`——这里是 AFFiNE 的"设计唯一标准"）把字体/颜色/emoji 级细节钉死，属于产品层的"设计决策宪法"。
- **设计红线**：编辑器与前端 MIT、后端 source-available——贡献者能改编辑器，但企业私有化后端要留意许可边界（MakeUseOf 明确提醒"important thing to keep in mind for production deployments"）。
- **版本演进哲学**：canary 日更 + beta 并行，走"快速迭代 + 用户可退回稳定版"路线；README 承认插件系统和第三方 block 是"coming soon"，即扩展性目前主要靠 fork 改源码。

## 🌐 全网口碑画像

### 好评共识

- Better Stack 指南（2026）："unified canvas is the clearest reason to use AFFiNE over alternatives. The CRDT-based sync works reliably on self-hosted instances, and BlockSuite provides a real extensibility path"——明确肯定自托管 CRDT 与扩展路径。
- MakeUseOf 实测："eliminated far more context switching than I expected... handled my drafts, lightweight databases, project dashboards, diagrams, and most active research inside one coherent workspace"——真实用户原话。
- 稀土掘金跨工具对比（2026）：把 AFFiNE 归为"开源 + AI 驱动新一代工具"，自托管/云双部署、内置多模态 AI 是其优势；数据主权维度给"强"。
- tubrief 视频（63K star 时点）："integrated edgeless canvas + BlockSuite gives competitive edge over AppFlowy/Anytype"。

### 差评共识 & 踩坑高发区

- **大画布性能**：多个来源独立复现——"performance on very large canvases can exhibit lag or rendering issues"（Better Stack）、"occasional lag... large canvases and databases can affect performance more than I'd like"（MakeUseOf）。
- **数据库能力不如 Notion**：Notion 的 relation/rollup/formula 更成熟，AFFiNE 尚未追平（Better Stack、MakeUseOf 一致）。
- **移动端粗糙**：早期"无原生 iOS/Android app"（Better Stack，2026），后续虽有 `apps/ios`，Issue #15815（手机上如何导入文件）、#15793（Android列表视图）说明体验仍在打磨。
- **自托管 AI 功能的隐藏门槛**：Issue #15867——"AI image generation always fails on self-hosted filesystem storage: Copilot blob signing is required"；#15866——AI doc_update 在空行/重复行文档上报误导性的 "Doc not found"。
- **资源占用**：Issue #15872（CPU/GPU 占用过高导致电脑发热，2026-11-19 新开）。
- **导出/Mermaid 等细节 bug**：#15818（Markdown/HTML 导出失败却弹"导出成功"）、#15861（Mermaid 流程图标注不渲染）、#15799（暗色模式图形黑底难读）。

### 争议焦点

- **双许可**："MIT for the editor, source-available for the backend"（MakeUseOf）——生产部署者必须看后端许可，这层复杂性在 README "open-source" 口号下不显著。
- **"本地优先"与"云 AI"的天然张力**：CSDN 指出"完全离线使用时 AI 部分不可用，这是本地优先和云 AI 之间的取舍"；README 也承认云端分析会发送字幕/抽帧画面。
- **"替代 Notion"的成熟度**：MakeUseOf 的结论最公允——"Specialized tools still win at the extremes"（极端场景仍需 Miro/Notion/Obsidian），AFFiNE 赢在中间地带。

### 典型实战案例

- MakeUseOf 作者把 Notion/Miro/Obsidian 三合一迁移实测：项目草稿、轻量数据库、项目看板、架构图、活跃研究都搬进 AFFiNE，但 Obsidian 的纯文本归档和成熟插件生态没被替代。
- 掘金/知乎系评测把它列入"程序员/研究者组合方案"：AFFiNE 用于创意前期/项目看板，Obsidian 做主力知识库——说明社区定位偏"协作 + 可视化"而非纯个人笔记。

### 维护者响应风格

Issue 15800+ 的编号体量 + 细粒度标签（story/feature/Bug/question）+ 每日 canary，说明是大规模成熟项目式运作；新 bug（如 #15872 当日开）能快速进入队列，但 841 个 open issue 也意味着 backlog 压力大。

## ⚔️ 竞品对比

| 维度 | AFFiNE | Notion | Obsidian | AppFlowy | Anytype | Miro |
|------|--------|--------|----------|----------|---------|------|
| 开源/许可 | MIT 编辑器 + source-available 后端 | 闭源 | 核心闭源/插件多开源 | 开源(AGPL) | 开源 | 闭源 |
| 数据形态 | Block + Canvas（超融合） | Block + DB（纵向） | 本地 Markdown | Block + DB | Object-based | 白板为核心 |
| 部署 | 自托管 Docker + 云 + 本地 | 仅云 | 本地 + Sync | 自托管/云 | 本地/云 | 仅云 |
| 白板 | 无限画布内置 | 有限 | 靠插件 | 较弱 | 部分 | 核心能力最强 |
| 数据库 | 多视图/看板，relation 等弱于 Notion | 最成熟（relation/rollup/formula） | 靠插件 | 接近 Notion | 对象标签 | 无 |
| 离线 | 全功能 | 有限 | 全功能 | 支持 | 支持 | 无 |
| 扩展 | BlockSuite（coming soon 插件） | API 有限 | 插件生态最成熟 | 有限 | 有限 | API 有限 |
| 内置 AI | 有（多模态，付费额度） | 强（官方） | 靠插件 | 有 | 有 | 有 |

（对比来源：Better Stack 指南、tubrief 视频、稀土掘金 2026 对比、MakeUseOf 实测）

**选择建议**：要"文档+白板+轻量数据库同处一地且数据自持"→ AFFiNE；要"重度数据库/关系型工作流"→ Notion/AppFlowy；要"纯文本、可移植、插件生态"→ Obsidian；要"复杂团队工作坊白板"→ Miro。

## 🎯 核心研判

### 项目优势（不可替代的价值点）

- **文档/白板同构的稀缺性**：真正把 edgeless canvas 做成一等公民且开源，这个组合在 2026 年仍少见。
- **BlockSuite 框架具备平台价值**：即使不用 AFFiNE 产品，编辑器内核值得单独研究与复用——"开源知识 OS 底座"的叙事有真实代码支撑。
- **自托管 CRDT 被第三方实测可用**：Better Stack 确认"CRDT sync works reliably on self-hosted instances"——不是 demo 级。

### 项目风险（潜在隐患和局限性）

- **后端非 MIT**：source-available 企业许可使"完全开源"打折扣，生产/商用前必须读 LICENSE 细则。
- **大画布/大库性能天花板**：多来源独立复现的卡顿问题，规模化使用需评估。
- **841 open issues + 快速迭代**：canary 日更意味着稳定性与特性 churn 并存；AI 功能在自托管上的边缘 bug（#15867/#15866）说明"本地优先 + 云 AI"整合未收敛。
- **移动端与插件系统尚未完成**：README 自承插件社区 coming soon，当前扩展靠 fork。

### 适用场景 & 不适用场景

- ✅ 适合：重视数据主权、需要文档+画布融合、愿意自托管、能接受快速迭代的团队/开发者；想复用编辑器内核造工具的人。
- ❌ 不适合：依赖 Notion 高级数据库公式/rollup 的重度用户；要求极致稳定与原生移动体验的场景；把"全 MIT"当硬约束的合规环境。

### 趋势判断

**稳定增长期/平台化早期**：75K star、canary 日更、BlockSuite 独立生态、MCP server 认证——已从"Notion 替代"进化成"知识 OS 底座"。关键观察点是插件系统落地与后端许可的商业化边界。

## 📂 关键文件路径速查

| 文件 | 价值 |
|------|------|
| `blocksuite/framework/{std,store,sync,global}/` | 编辑器四框架包，内核入口 |
| `blocksuite/framework/sync/src/doc/engine.ts` | DocEngine main+shadow 多源同步状态机 |
| `blocksuite/framework/store/src/reactive/native-y.ts` | 业务对象 ↔ Y types 双向桥 + transform 钩子 |
| `blocksuite/framework/store/src/yjs/` | Yjs/Doc/awareness 适配 + subdoc 生命周期 |
| `blocksuite/affine/{blocks,data-view,gfx,widgets}/` | AFFiNE 具体 block/视图组件 |
| `blocksuite/playground/` | 框架脱离产品独立可用的演练场 |
| `packages/backend/server/src/{app.module.ts,schema.gql}` | NestJS 后端入口 + GraphQL schema |
| `packages/backend/native/` | Rust/OctoBase 绑定层 |
| `packages/frontend/apps/ios/AGENTS.md` | iOS 端开发约定 |
| `DESIGN.md` | 产品级设计规范"宪法"（双主题/字体/组件原语）|
| `docker-compose.yml` | 自托管入口 |
| `LICENSE` / `LICENSE-MIT` | 后端 source-available vs 编辑器 MIT 的边界 |

---

**调研方法**：gh CLI 拉取仓库元数据、canary 分支 12859 文件树、README、BlockSuite framework README、3 个核心源码文件（engine.ts/native-y.ts/yjs utils）、30 条 open issues、8 条 releases；WebSearch 采集 5 个第三方来源（Better Stack、MakeUseOf、稀土掘金、tubrief 视频、CSDN 技术解析）。Star 数为 2026-11-20 抓取时点值。
