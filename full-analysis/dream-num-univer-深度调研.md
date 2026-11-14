# 🔬 dream-num/univer — 全方位深度调研

> 调研日期：2026-11-15 ｜ Stars：24,375 ｜ 语言：TypeScript ｜ 许可：Apache-2.0（Web SDK 核心） ｜ 编号：#596

## 📌 一句话定位
**Univer** 是一个 **Office SDK**——把电子表格、文档、演示、关系表、画布、PDF 的编辑、计算、协同、文件处理做成可嵌入自有产品的 Web SDK，并提出「**Build your own AI office**」：用同一套开源 API 让 Agent 与办公内容协作。Web SDK 核心（内容模型、插件与依赖管理、命令系统、公式与渲染引擎、Facade API）以 Apache-2.0 开源。

## ⭐ 项目亮点
- **微内核 + 插件化 + 统一 Facade API**：70+ 官方插件按需开启，控制前端包体积；同一套内容模型 / 命令 / 计算在浏览器与 Node.js 复用（Headless 处理，无需交互编辑器）。
- **自研 Canvas 渲染引擎**：万行级单元格流畅渲染、不阻塞主线程，相对 DOM 表格在大数据量下有性能优势。
- **公式与表格能力强**：500+ Excel 公式、跨表引用、精细单元格/行列/工作表权限、条件格式、数字格式、筛选、排序、冻结窗格、查找替换。
- **三 SDK 分层**：Web SDK（本仓库，Apache-2.0 核心）、Server SDK（实时协同 + 编辑历史 + 导入导出，商业）、AI SDK（Agent 集成，商业）——开源与商业边界清晰（OSS 文档不得暗示 Pro 能力）。
- **Agent 原生押注**：AI SDK 让 Agent 复用同一套开源 API；官方提出「不发明专有协议，把文档抽象成 Unit，用结构化 API + 截图自检构成闭环，用 Git 式 Worktree 审查流解决『AI 改的东西谁来把关』」。

## 🏗️ 项目架构全景
仓库是 pnpm/turbo monorepo，`packages/` 下 70+ 包，分层清晰：
- `packages/core`：DI 容器、`services`、`observer`（事件分发）、`facade`（应用面 API `univerAPI`）、`bases`/`common`/`sheets`/`types`，`univer.ts`/`skeleton.ts`/`index.ts`——命令系统（统一编辑/撤销/重做）与 Facade 是接入面。
- `packages/engine-formula`：公式引擎（独立包）；`packages/engine-render`：Canvas 渲染引擎（分层/增量）。
- `packages/sheets` / `docs` / `slides`：三大办公能力的编辑实现；`packages/ui` 及大量 feature 包（`data-validation`、`conditional-formatting`、`filter`、`find-replace`、`hyper-link`、`thread-comment`、`sort`、`table`、`numfmt`、`drawing`、`watermark` 等）提供可插拔能力。
- 接入范式是 Preset 模式：`@univerjs/presets` + `@univerjs/preset-sheets-core` → `createUniver({...})` → 返回 `univerAPI`（Facade），应用通过 Facade API 与事件连接内容与 Agent。

## 💡 应用场景与启发
- **典型场景**：① 在 Web 业务系统内嵌入可编辑表格/文档（ERP/CRM/低代码/数据产品）；② 无头处理——在 Node.js 复用内容模型、命令、公式做自动化（生成、快照、批量任务）；③ Agent 应用把办公文档当结构化工作台。
- **可借鉴模式**：**跨 feature 的编辑与 undo/redo 协调**——每个 feature 提供自己的 changes 与 undo data，命令层组合执行与历史；这是插件化办公内核的通用工程范式。
- **同类需求思路**：若产品要内嵌表格/文档且「数据不能出内网」，Univer 比 OnlyOffice 轻量、比 Luckysheet 成熟；做 Agent 办公应用时，其「不发明专有协议 + Unit 抽象 + 结构化 API + 截图自检 + Worktree 审查」是值得参考的人机同文件协作范式。

## 🧠 核心源码解读（克制代码量）
`packages/core/src/facade` 是应用面 API（`univerAPI`），它屏蔽内部命令/服务细节，让上层只面向稳定契约；`packages/core/src/services` 与 `observer` 构成可插拔的服务与事件总线；命令系统（`command`）统一「执行 + 撤销/重做」，是跨插件协作的中枢。README 明确：插入筛选区内的行会同时改基础内容与筛选范围，undo 需两者都恢复——这正是「feature 各自提供 changes/undo data，命令层组合」的设计动机。

公式与渲染被拆成独立引擎包（`engine-formula` / `engine-render`），使「计算」与「绘制」可分别演进、可无头复用；`engine-render` 的 Canvas 分层/增量渲染是万行级流畅的根本。AI 原生能力不在核心仓库重写协议，而是通过 Facade + 事件把既有办公文档暴露给 Agent，把「命令名、鉴权、输出」交给应用自己拥有。

## 📊 社区口碑（外链）
- 趋势上升（搜索时约 18.5K–24K⭐），**原 Luckysheet 团队（myliang）** 打造；npm 周下载稳定 **27 万+**，被称为「当下最火热的国产在线办公 SDK」。
- 多篇中文技术选型对比将其与 OnlyOffice / Luckysheet / Handsontable / WPS Online 并列：结论多为「要嵌入业务系统、二次开发、私有化轻量在线表格/文档，优先 Univer」。
- 定位共识：**「Agent 原生」是差异化押注**——同构运行时 + Worktree 审查流瞄准「人机同文件协作」。
- **边界提醒**：开源 Apache-2.0 仅含 Web SDK 核心；实时协同、编辑历史、xlsx 高保真导入导出、图表、数据透视表等放在商业 Univer Pro，企业选型需看清哪些在 OSS、哪些在 Pro。

## 🥊 竞品对比
| 维度 | Univer | ONLYOFFICE | Luckysheet | Handsontable | WPS Online |
|------|--------|-----------|------------|--------------|-----------|
| 形态 | 可嵌入 SDK（Canvas） | 自托管完整应用 | 纯前端表格 | 纯表格组件 | SaaS |
| 授权 | Apache-2.0（核心） | 自有（体积大） | 已停维护 | 付费公式 | 按调用计费 |
| 差异化 | Agent 原生 + 跨端嵌入 + 插件化 | 功能完整但嵌入难 | 轻量但停更 | 数据网格强 | 开箱即用但数据出第三方 |

## 🎯 核心研判
Univer 是国产在线 Office SDK 赛道中稀缺的 **Canvas 全栈自托管方案**，微内核/插件/Facade 的工程结构优秀，「Agent 原生」是其前瞻押注点。对需要内嵌办公能力且数据敏感（不出内网）的团队，它是比 OnlyOffice 轻、比 Luckysheet 成熟的选型。采用时务必厘清开源/商业边界——把 Web SDK 核心当底座，Pro 能力按需采购。

## 📁 关键文件路径速查
- 入口与架构：`README.md`（架构章节）、`packages/`
- 核心：`packages/core/src/{facade,services,observer,bases,common,sheets,types}`、`packages/core/src/{univer.ts,skeleton.ts,index.ts}`
- 引擎：`packages/engine-formula`、`packages/engine-render`
- 办公能力：`packages/sheets`、`packages/docs`、`packages/slides`、`packages/ui`
- 文档：[docs.univer.ai](https://docs.univer.ai)、[univer.ai](https://univer.ai)
