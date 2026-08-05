# genspark-ai/genoffice 深度调研

> 一句话：**GenSpark 开源的 AI-native 办公套件（macOS/Windows）——Word/Excel/PPT/PDF 四件套，本地优先、Electron 壳 + 共享 `*-engine` 包做 Office XML 往返保真，每个 app 内嵌 AiPanel 让 agent 直接生成/改写文档**。

🔗 https://github.com/genspark-ai/genoffice ｜ 许可 Apache-2.0（另有 `ee/` 企业版目录，README 标注为 EE）｜ 语言 TypeScript ｜ ⭐ 1,732（2026-07-31 创建）｜ 主页 https://www.genspark.ai ｜ 主题 ai/docx/electron/office-suite/pdf/pptx/xlsx

## 一、项目亮点（差异化）

1. **AI-native 而非 AI-assisted**：不是"在 Word 里加个聊天按钮"，而是每个 app（docs/slides/sheets）都有 `AiPanel`，agent 基于 outline/slide 结构直接创作与 QC（如 slides 的 `slide-qc.ts` / `layout-audit.ts` / `outline-json.ts`）。
2. **本地优先 + 真实 Office 往返**：核心卖点是"改完还能存回 .docx/.pptx/.xlsx 且不崩样式"——`packages/docx-engine`、`packages/pptx-engine` 直接读写 OOXML，配 `roundtrip.test.ts` / `revisions.test.ts` / `smartart-ole.test.ts` 等大量保真测试。
3. **共享引擎复用**：docx/pptx/xlsx 三套引擎各自独立成包，shell 与 file-parse 共用，避免"四件套各写一遍解析"。
4. **Agent 编排抽象**：`packages/agent-core`（`loop.ts`/`skill.ts`/`electron-transport.ts`）把"agent 循环 + 技能 + Electron IPC 传输"做成可复用内核；`packages/ai-provider` 屏蔽多 provider。
5. **工程完整度**：Electron monorepo + electron-vite + Vitest + Playwright e2e（`e2e/`）+ `docs/superpowers/specs/` ADR，发布即有 fixtures 与 fidelity 比对脚本（`tools/fidelity-compare.mjs`）。

## 二、核心架构

Electron + electron-vite monorepo，`apps/` 四应用 + `packages/` 共享内核 + `scripts/`/`tools/` 质量门禁。

| 路径 | 职责 |
| --- | --- |
| `apps/docs` | 文字处理（Word 替代） |
| `apps/slides` | 演示（PPT 替代），含 `renderer/ai/` 全套 agent 技能 |
| `apps/sheets` | 表格（Excel 替代），`tests/xlsx-*.test.ts` 覆盖绘制/透视/保护等 |
| `apps/shell` | Electron 主壳：tab 管理、最近文件、自动更新、菜单 |
| `packages/docx-engine` | docx 读写：generate/parse/patch/theme/math/notes/comments/revisions… |
| `packages/pptx-engine` | pptx 读写：layout/master/animation/smartart/table/theme… |
| `packages/pptx-render` | pptx → 渲染树（坐标/填充/文本布局/preset-geometry） |
| `packages/file-parse` | docx/pdf/pptx/xlsx 统一解析入口 |
| `packages/agent-core` | agent 循环 + 技能 + Electron 传输（`loop.ts`/`skill.ts`） |
| `packages/ai-provider` | 多 provider 抽象（chat/stream/watchdog） |
| `packages/project-store` | 文档存储 + IPC |
| `packages/ui` | 共享 React UI（AiComposer / Markdown / icons） |
| `ee/` | 企业版（EE LICENSE + README，开源核心不含） |

**技术栈**：Electron + React + TypeScript + electron-vite；AI 经 `packages/ai-provider`（GenSpark/`gsk` 鉴权在 `packages/ai-search`）；i18n 多语言；测试 Vitest + Playwright。

## 三、源码深度解读

### 1. slides 的 agent 子系统（`apps/slides/src/renderer/ai/`）
```
AiPanel.tsx            # agent 对话面板
outline-json.ts        # 大纲 ↔ JSON 结构互转（agent 改大纲即改 deck）
slides-skill.ts        # 生成/重写幻灯片的技能定义
layout-script.ts / layout-script-interpreter.ts  # 布局脚本与解释器
layout-audit.ts        # 布局审计（agent 自检排版）
slide-qc.ts            # 质量检查（generate-deck / regenerate-slide 测试覆盖）
files-skill.ts         # 文件操作技能
transport.ts           # 与 agent-core 的传输层
```
设计要点：agent 不直接吐字符串，而是操作**结构化大纲/布局脚本**，QC 与审计在生成后自动跑——比"LLM 生成整段 HTML"可控得多。

### 2. 文档引擎往返保真（`packages/docx-engine`）
```ts
generate.ts  // 空白/模板 → docx
parse.ts     // docx → 内部模型
patch.ts / text-patch.ts  // 局部修订（不重写整篇）
theme.ts / math.ts / notes.ts / comments.ts / revisions.ts / watermark.ts
```
大量 `*.test.ts`（roundtrip / revisions / smartart-ole / cjk-layout / ruby / bidi）保证"读进来的样式改完还能原样写回"。`packages/pptx-engine` 同理：`animation.ts`/`smartart.ts`/`master-edit.ts`/`table-edit.ts` + `rebuild-fidelity.test.ts`。

### 3. agent 编排内核（`packages/agent-core`）
```ts
loop.ts              // agent 主循环
skill.ts             // 技能加载/执行
electron-transport.ts// 经 Electron IPC 与主进程通信
types.ts
```
把"agent 循环"与"Electron 传输"解耦，使 docs/slides/sheets 三端复用同一套 agent 机制。

## 四、应用场景与启发

- **本地优先的 AI 办公**：担心文档上云、又想要 AI 辅助写 PPT/Excel 的团队/个人，可自托管本地跑，数据不出机。
- **"结构化中间表示 + agent 操作"范式**：让 LLM 改 outline-json / 布局脚本而非裸文本，QC 自动介入——做任意"AI 编辑复杂文档"产品（报告生成、合同起草）都可借鉴 slides 的 ai/ 分层。
- **OOXML 往返引擎复用**：若自研文档工具，直接参考 `docx-engine`/`pptx-engine` 的"parse→model→patch"切分，别重造轮子。
- **Electron 多 app 共享包**：四件套共用 engine/ui/agent-core，显著降低维护成本。

## 五、社区口碑

- 2026-07-31 创建即 1.7k⭐，借 GenSpark 品牌与"开源替代 Office + AI"叙事上 Trending；衍生 `criptogus/HermesOffice`（fork 自 GenOffice、接 Hermes Agent）说明社区已在二开。
- 正面：本地优先 + 真实 Office 兼容是刚需；测试与 fixtures 完整，不是玩具。
- 争议/风险：`ee/` 企业版目录存在，暗示核心与 EE 分层，需确认开源核心是否长期完整；Electron 套件体积/性能、AI 能力是否强依赖 GenSpark 云端 provider 待观察。

## 六、竞品对比 + 核心研判

| 维度 | genoffice | LibreOffice | OnlyOffice | 飞书/钉钉文档(云) |
| --- | --- | --- | --- | --- |
| AI-native | ✅ 内嵌 agent | ❌ | 部分 | ✅ 但云端 |
| 本地优先 | ✅ Electron 本地 | ✅ | ✅ | ❌ |
| Office 兼容 | OOXML 往返引擎 | 强 | 强 | 中 |
| 开源 | Apache-2.0（有 EE 分层） | MPL | AGPL | 否 |
| 多端 | mac/Win | 全平台 | 全平台 | 全平台云 |

**研判**：
- ✅ 当前**最完整的开源 AI-native 办公套件**之一，尤其"本地跑 + 真 Office 往返 + 内置 agent"组合稀缺，值得关注与二开。
- ⚠️ 成熟度早期（1.7k⭐、2026-07 才建）：多 app 功能深度、超大文档性能、与 GenSpark 云 provider 的解耦程度都需实测。
- ⚠️ `ee/` 分层需盯紧——若关键能力移入 EE，开源版可能"能看不能打"。建议以 MIT 等价 Apache-2.0 核心 + 社区 fork（如 HermesOffice）双轨跟踪。
- 结论：作为"本地 AI 办公"参考架构与可二开基座入库；直接当日常 Office 主力替换需等稳定性与去云依赖验证。

## 七、关键文件路径速查

- `apps/slides/src/renderer/ai/` — agent 子系统（AiPanel / outline-json / slide-qc / layout-audit / transport）
- `packages/docx-engine/src/` — docx 引擎（generate/parse/patch/theme/math/revisions…）
- `packages/pptx-engine/src/` — pptx 引擎（layout/master/animation/smartart/table…）
- `packages/pptx-render/src/` — pptx 渲染树（coords/fill/text-layout/preset-geometry）
- `packages/agent-core/src/` — agent 循环/技能/Electron 传输
- `packages/ai-provider/src/` — 多 provider 抽象（chat/stream/watchdog）
- `packages/file-parse/src/` — docx/pdf/pptx/xlsx 统一解析
- `apps/shell/src/main/` — Electron 主进程（tab-manager/updater/recent-files）
- `docs/superpowers/specs/` — ADR（如 `2026-08-05-update-channel-design.md`）
- `tools/fidelity-compare.mjs` `scripts/pagination-baseline.mjs` — 保真度比对基准
- `ee/` — 企业版目录（开源核心不含，跟踪分层风险）
