# Archify 深度调研

> 仓库：`tt-a1i/archify` ｜ MIT ｜ 主语言 HTML ｜ 当前版本 v2.16.0-dev.0（2026-08-26 抓取）
> 星标：17,511 ⭐（当日 Trending +1,002）｜ Fork：1,219 ｜ 安装：`npx skills add tt-a1i/archify -g`
> 官方站点：https://tt-a1i.github.io/archify/

## 一、项目定位（一句话）

Archify 是一个 **Agent Skill**（兼容 Raven / Cursor / Claude Code / Codex CLI / OpenCode），把代码库或一段系统描述，直接变成可交互、可验证、可分享的技术架构图——产出是**自包含 HTML + 确定性校验收据**，而不是又一份需要人工排版的 Mermaid 草稿。

## 二、项目亮点（差异化）

1. **5 种图类型 + 4 预设 + 明暗双主题**：architecture / workflow / sequence / data-flow / lifecycle，外加 signal-flow / blueprint / editorial 视觉预设与 finite motion，覆盖几乎全部"技术沟通图"需求。
2. **类型化 JSON IR + 确定性校验（fail-closed）**：每个渲染模式都有 schema 与可复现源；`validate --json` 必须报告全部 9 项 artifact checks、0 composition error、0 warning 才算 showcase 通过，否则返回稳定 rule code + 精确 subject + `supportedFixes` 修复处方。
3. **真实性交互，不臆造拓扑**：节点可标 `SRC n` 并打开 Git 校验过的文件与行号（钉死到单个 public commit）；聚焦/上下游可达性/精确路由/角色对比/引导故事全部复用 authored 节点与关系，绝不"发明"拓扑或声称运行时影响。
4. **Architecture Delta**：对比两个已校验快照的 Before / Delta / After，给出 exact added / removed / changed / moved / rerouted 事实与机器可读 receipt——专为 PR / 设计评审前"先看架构变动"而生。
5. **便携即默认**：结果是一个 HTML 文件，导出 PNG/SVG/WebM 与 1200×630 分享卡，零临时查看器状态、零外部依赖。

## 三、核心架构（克制呈现）

SKILL.md 定义了一条 **fast authoring path**（artifact-first，非先读实现）：

```
选类型 → 读 schemas/<type>.schema.json + examples/ 同类型 JSON → 写 candidate
       → validate（每轮 edit 后必跑）→ deliver（最终原子验收）
```

`archify/bin/archify.mjs` 是一条确定性流水线：`Generate`（agent 产出 typed JSON IR）→ `Validate`（bundled validator + layout rule）→ `Preview`（可选，loopback-only，只绑 127.0.0.1 随机端口，失败保留 last-good）→ `Deliver`（同目录候选渲染并检查，仅当全部 gate 通过才原子替换目标）→ `Iterate`。

- `renderers/shared/geometry.mjs`：自动路由（Automatic Port Spread + outside bridge），保证相邻并行端口不撞、不出现 sub-8px 段 / sub-16px 内角。
- `schemas/`：类型化 IR 契约；`examples/`：11 个 checked-in 场景，每个都附带 JSON 源 + 命名视图 + validation receipt（Proof Lab 可在线复核）。
- 失败即出"修复收据"：`validate --json` / `deliver --json` 永远只吐一个 JSON 对象，读 `diagnostics[]` 改 named subject，且限定**两轮聚焦修正**，不重写整图。

## 四、应用场景与启发（重点）

- **给 Agent 画图提供"artifact-first + 校验闭环"范式**：大多数"AI 画图"工具只管生成不管验收，Archify 把"校验"做成一等公民（9 项 gate + 两轮修正上限），值得任何"agent 产出可验证产物"的场景借鉴（代码生成、配置生成同理）。
- **Diagram-as-Code 进入 Agent 原生时代**：图不再是人画的，而是 agent 从描述/仓库派生、人只做边界确认（"add Redis"、"move auth left"）。这种"agent 起草 + 人聚焦 refine"的模式，比纯对话或纯手写都更适合工程沟通。
- **可复用于"可信 artifact"管线**：其 `SRC n` 溯源 + `deployment-ownership` engineering profile（缺 owner / 单区域 / 私有库范围 / 跨边界即 fail-closed）的思路，可迁移到任何需要"AI 产出 + 人工可审计"的文档/架构评审工具。

## 五、源码深度解读（2 个核心模块）

**① SKILL.md — authoring invariants（agent 行为契约）**
```markdown
# 关键不变量（节选）
- One obvious main path；side branches 离开最近 main-path 节点；先删低价值边再加路由控制
- 默认 omit meta.visual_preset → 每图开 classic；color mode 与 preset 解耦
- 关系标签是语义数据：碰撞先移标签/调路由，只在两端完全蕴含时才删
- Automatic Port Spread 默认开启；单关系/显式 via 跳过
- 绝不让边穿过无关不透明节点 / 共享走廊 / 掩蔽另一路由的标签
```
这段是 Archify 区别于"Mermaid 主题"的根本：它约束的是**语义与几何正确性**，而非视觉风格。

**② `bin/archify.mjs compare` — Architecture Delta**
```bash
node archify/bin/archify.mjs compare architecture base.json head.json architecture-delta.html --json
```
命令接收两份已校验 JSON，输出 added / removed / changed / moved / rerouted 的精确事实与 machine receipt。viewer-only、无运行时影响、不推断 merge 安全性——把"架构评审"从主观审阅变成可机器比对的差分。

## 六、全网口碑

- **Trendshift 上榜**（repository badge #31352），GitHub Trending 当日 +1,002 star，增长健康。
- 官方 Proof Lab（gallery.html）check-in 了 11 个真实场景（含从 `mco-org/mco` 在 `9f1a1cf` 提交派生的 runtime 架构图），用"生成物而非 mockup"自证能力。
- 赞助商含 APINEBULA（多模型 API）与 EverMind（Raven harness 内存基础设施），作者留 QQ 邮箱招商，商业路径偏早期个人/小团队。
- 局限：文档偏英文，中文资料少；项目处 `-dev.0` 阶段，API 仍在演进。

## 七、竞品对比 + 核心研判

| 维度 | Archify | Mermaid | Excalidraw | diagrams-as-code (Terraform/Cloudcraft) |
|---|---|---|---|---|
| 生成方式 | Agent 派生 typed JSON | 人写 DSL | 人手绘 | 人写声明 |
| 可验证性 | 9 项 gate + receipt | 无 | 无 | 有（领域特定） |
| 交互性 | 自包含 HTML（路由/可达性/故事） | 静态 | 手绘交互 | 弱 |
| Agent 原生 | ✅ Skill | ❌ | ❌ | ❌ |
| 溯源 | Git 行号 SRC n | ❌ | ❌ | 部分 |

**核心研判**
- **优势**：agent-native 图生成 + fail-closed 校验 + 真实 Git 溯源 + 交互式 HTML 交付，四者组合在当下几乎是独一份；"图即代码 + 校验闭环"定位清晰。
- **风险**：① 单作者/小团队，生态尚新（v2.16-dev），长期维护与破冰风险；② 图质量高度依赖 agent 的"布局判断"，复杂系统仍需人多轮 refine；③ 明确**不做**通用绘图编辑器 / 自动布局 / 托管分享，边界内功能有限。
- **趋势**：随着 Agent Skills 标准化（agentskills.io），"可验证 diagram-as-code"很可能成为 agent 工作流的标准能力之一；Archify 先发卡位价值明确。
- **启发**：下次遇到"让 AI 画/写/生成某产物且要求可信"的需求，直接借鉴其"typed IR + 确定性 gate + 两轮修正上限"的闭环设计。
