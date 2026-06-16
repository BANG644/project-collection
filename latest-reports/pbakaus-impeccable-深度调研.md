# 🔬 pbakaus/impeccable - 全方位深度调研

## 📌 一句话定位

**Impeccable 是 AI 编码助手的「设计灵魂注入器」** — 它给 Claude Code、Cursor、Gemini CLI 等工具装上了一套完整的 UI/UX 设计语言系统，让 AI 生成的前端代码不再千篇一律地「AI 感」，而是具备专业设计师级别的视觉品味和一致的设计系统。

> 不是提示词模板，不是设计规范文档，而是一个**可执行的、可编程的设计技能包**。

---

## 🏗️ 项目架构全景

### 四大组件（v3.0.2）

```
impeccable/
├── skill/           ← AI 设计技能（23 个命令 + 7 个领域参考模块）
├── cli/             ← 反模式检测引擎（27 条确定性规则 + LLM 评审）
├── extension/       ← 浏览器扩展（实时注入 + 对比视图）
├── site/            ← Astro 官网（impeccable.style）+ 交互 Demo
└── .agents/*/       ← 多 AI 工具适配层（Cursor/Claude/Gemini/Trae 等 15+ 工具）
```

### 设计哲学

| 原则 | 体现 |
|------|------|
| **反向思维** | 先定义「什么不该做」（27 条反模式检测），再定义「该做什么」 |
| **注册表双轨制** | **Brand**（以设计为产品：营销/品牌站）vs **Product**（设计服务产品：App UI）两条独立设计参考路径 |
| **渐进增强** | CLI 检测器可本地跑，也可在 CI/CD 中集成；浏览器扩展可实时注入对比 |
| **命令即 API** | 23 条斜杠命令构成了一套「设计 DSL」，每个命令有独立的参考文档和上下文 |

### 核心配置一览

```
型号：v3.0.2 (CLI) / v3.7.0 (Skill)
许可：Apache-2.0
语言：JavaScript (ESM)
构建：Bun + Astro
测试：~200 个测试用例，覆盖 CLI/检测器/Live 模式/端到端
发布：每天 1-3 个版本，极其活跃
```

---

## 🧠 核心源码解读

### 1. 反模式检测引擎 — `cli/engine/registry/antipatterns.mjs`

**核心定位**：项目的技术灵魂。它不是一个「设计建议生成器」，而是一个**确定性规则引擎**。

**架构设计**：
- 所有反模式定义在 `ANTIPATTERNS` 常量数组中，每个条目含：`id`（唯一标识）、`category`（分类：slop/visual/typography/color/layout/a11y/interaction）、`description`、`severity`（warning/error）、`skillSection`（关联的设计域）
- 当前 ≤ 27 条确定性规则，附带一条 LLM 评审（12 条补充规则）
- 与 Skill 系统松耦合：CLI 可独立运行，不加 Skill 也能用 `npx impeccable detect`

**设计模式**：
- **策略模式**：检测引擎分 4 种引擎（Browser/Regex/StaticHTML/Visual），各引擎独立实现 `detect()` 接口
- **注册表模式**：ANTIPATTERNS 是一个中央注册表，所有引擎通过 `getAntipattern(id)` 获取反模式定义
- **工厂模式**：`createDetectorProfile()` 根据配置创建检测器实例

### 2. CLI 主流程 — `cli/engine/cli/main.mjs`

**核心流程**：`walkDir()` 扫描目录 → `buildImportGraph()` 构建导入图 → 针对 HTML/CSS/JS 文件依次调用各引擎 → `formatFindings()` 输出

**未被 README 文档化的特性**：
- 支持 **stdin 管道输入**（`handleStdin()`）：可用于 CI 流水线
- 支持 **Live 模式**下的实时检测：在页面上注入 overlay，实时标记反模式位置
- 框架自动检测（`detectFrameworkConfig`）：自动识别 Next.js/Nuxt/Astro 等框架配置

### 3. 设计系统模块 — `cli/engine/design-system.mjs`

**隐藏的价值**：这是 Impeccable 区别于纯检测工具的关键。

它能在项目中**发现已有的 CSS tokens**（`parseFrontmatter()`），将其规范化并和应用规则对比（`checkSourceDesignSystem()`），然后输出「偏离度」报告。这意味着：
- 你不需要手动告诉 AI 「我们的设计系统是什么样的」
- AI 自动从项目中已有的 CSS/Less/Sass/变量中逆向工程设计系统
- 然后在此基础上做设计建议，而不是从头开始

### 4. 发现服务 — `cli/engine/findings.mjs`

**极简但有深意**：只有 ~30 行的 `finding()` 工厂函数。但它将每个发现的**反模式 ID**、**文件路径**、**行号**、**代码片段**结构化打包，为后续可视化工具（浏览器扩展的 overlay 视图）提供标准数据格式。

### 5. PROFILE 性能分析 — `cli/engine/profile/profiler.mjs`

**隐藏功能**：`createDetectorProfile()` 和 `summarizeDetectorProfile()` 能分析检测过程的性能瓶颈，适合在大型代码库中优化检测效率。

---

## 🔬 独家发现（READEME 之外的深度洞察）

### 发现 1：「反模式优先」的设计哲学

Impeccable 的架构决策体现了一种**独特的设计哲学反转**：它不是先定义「什么是对的」，而是先定义「什么是错的」，然后反向推导应该怎么做。

- CLI 检测器（确定性规则）→ 打标记：「这里有 AI 味」
- Skill 命令（DSL 修复）→ 给解决方案：「用 /typeset 替换字体层级」
- 设计参考（领域知识）→ 提供上下文：「为什么这样更好」

这种三层递进结构（检测 → 修复 → 理解）在整个 AI 工具生态中独树一帜。

### 发现 2：15+ 适配层揭示了 AI 工具生态的管窥

项目支持 15+ 种 AI 编码工具（Cursor、Claude Code、Gemini CLI、Codex CLI、Windsurf、Trae、OpenCode、Rovodev 等），每种工具都有独立的 `.agents/` 适配目录。这说明：
- AI 编码工具的**本质差异很大**（文件系统约定、Skill 加载机制、Hook 系统都不兼容）
- 但「需要设计质量」是**跨平台的共性痛点**

### 发现 3：Live 模式是技术亮点

`extension/` 目录和 `site/` 中展示了基于 **Neo Mirai 粒子背景** 的交互式现场设计评审。UI 元素被注入到页面上，实时代码变更可以被 AI 实时检测和标记。这不是简单的「截图+分析」，而是**在真实浏览器环境中做实时设计审计**。

### 发现 4：Kinpaku 设计语言 = 自噬性设计

项目的设计语言（Kinpaku = 金箔）本身就是对「AI 默认审美」的彻底反叛：
- 黑漆底色 + 金箔点缀 + 铜绿辅色
- 拒绝紫色渐变、霓虹点缀、玻璃拟态
- 用真实的材质感（金箔纹理、漆面反光）替代虚拟设计特效
- 是一个 **dogfooding 的绝佳案例**：自己的工具先过自己的检测

---

## 🌐 全网口碑画像

### 好评共识

| 好评点 | 来源 | 原话 |
|--------|------|------|
| **解决核心痛点** | CSDN 用户实测 | "AI 写的代码功能没问题，但界面看起来总有点「AI 味」…Impeccable 解决了两个很实际的问题" |
| **降低设计沟通成本** | 前端社区 | 「能说「垂直节奏感」，不说「这个字大一点」」 |
| **安装无痛** | 多名用户 | "一行命令搞定：npx skills add pbakaus/impeccable" |
| **命令直观** | 用户反馈 | "/polish、/audit、/critique 都是开发者能立刻理解的命令" |
| **CI 集成价值** | Issues | `detect` CLI 适合 pre-commit hook，自动化设计质量检查 |

### 差评共识 & 踩坑高发区

| 差评点 | 具体 | 严重程度 |
|--------|------|---------|
| **「教科书化」的建议** | /typeset 在所有场景都推荐 clamp()，不适合固定尺寸页面 | 🟡 中等 |
| **小众工具兼容性** | 部分本地/小众 AI 工具需手动调整适配层 | 🟢 轻 |
| **zip 安装问题** | 多个 Bug 报告提及 `npx impeccable install` 在特定 Node 版本失败（Issue #250, #246） | 🔴 严重（但已修复） |
| **中文翻译不一致** | "visual hierarchy" 时而译「视觉层次」时而「视觉层级」 | 🟢 轻微 |
| **设计自由度限制** | 对已有成熟 Design System 的团队，边际效益递减 | 🟡 中等 |

### 争议焦点

**设计风格 vs 设计自由度**：部分用户觉得 Impeccable 的建议偏向「正确但保守」——它推荐的「好设计」是在避免「AI 坏设计」的前提下，可能限制了更冒险的视觉探索。这是工具定位本身带来的取舍。

### 维护者响应风格

Paul Bakaus（前 Google 开发者布道师）非常活跃。每天多个 Release，Bug 在数小时内响应和修复。Issue #227（off-by-one bug）在提交后 22 分钟内即被修复。社区讨论质量较高，维护者回复有技术深度。

### 真实用户画像

多为**独立开发者和小型团队的非设计出身前端工程师**，主力工具是 Cursor/Claude Code，主要诉求是「快速原型做得足够好看能见人」。

---

## ⚔️ 竞品对比

### 对比矩阵

| 维度 | Impeccable | Anthropic frontend-design | 自定义 Prompt 模板 | Visual Copilot |
|------|------------|-------------------------|-------------------|----------------|
| **形态** | Skill 包 + CLI | Skill 包 | 文本提示词 | Figma 插件 |
| **反模式检测** | ✅ 27 条确定性规则 | ❌ 无 | ❌ | ❌ |
| **CI/CD 集成** | ✅ CLI 可独立跑 | ❌ | ❌ | ❌ |
| **Live 模式** | ✅ 浏览器扩展 | ❌ | ❌ | ✅ 实时预览 |
| **设计参考深度** | 7 个领域模块 | 单一提示词 | 取决于用户知识 | 设计稿解析 |
| **多工具支持** | 15+ 工具 | 仅 Claude | 通用 | 仅 Figma |
| **更新频率** | 每日 | 偶尔 | 无 | 月更 |
| **学习成本** | 中等（23 命令） | 低（单命令） | 高（需设知识） | 低（可视化） |

### 选择建议

- **用 Impeccable 当：** 你在多个 AI 编码工具之间切换，想要统一的「设计方言」
- **用 Anthropic frontend-design 当：** 只在 Claude 生态，要最低的认知负荷
- **用自定义 Prompt 当：** 你本身就是设计师，有明确的设计审美
- **用 Visual Copilot 当：** 你有现成 Figma 设计稿，需要精确 1:1 还原

---

## 🎯 核心研判

### 🟢 项目优势（不可替代的价值点）

1. **唯一具备确定性检测引擎的设计 Skill** — 其他方案都是「建议」，Impeccable 是「检测+建议+修复」三位一体
2. **跨工具生态锁定** — 支持 15+ 种 AI 工具，一旦团队建立设计词汇，切换工具的迁移成本很低
3. **快速迭代和高质量维护** — 30 天内从 v2.x 到 v3.7.0，每日发布，Bug 修复以小时计
4. **Dogfooding 验证** — 项目自己的网站和设计语言（Kinpaku）就体现其理念，证明设计系统输出的可行性
5. **CLI 可独立使用** — 反模式检测器不依赖 Skill，可作为前端代码质量工具独立使用

### 🔴 项目风险

1. **规模增长后的维护成本** — 23 个命令 + 27 条规则 + 15+ 适配层，架构复杂度会随增长指数级上升
2. **对 LLM 能力的依赖风险** — 部分规则（LLM critique pass）依赖底层模型的设计判断力，模型变化可能影响一致性
3. **生态脆弱性** — 各 AI 工具频繁变更 API/Skill 加载方式，适配层需要持续更新
4. **语言本地化** — 中文支持目前只有基础翻译，术语一致性有待提升

### 适用场景 ✅

- 独立开发者快速做 MVP 且不想太丑
- 非设计出身的前端工程师提升 AI 输出质量
- 小团队需要统一设计语言但没设计师
- 在 CI pipeline 中做自动化设计质量门禁

### 不适用场景 ❌

- 有成熟 Design System 团队（边际效益递减）
- 需要极度定制化/实验性视觉风格
- 非前端 UI 场景（后端/REST API 等）

### 趋势判断 📈

**上升期 — 快速增长。** 创立不到 7 个月（2025-11 → 2026-06），Stars 从 0 到 38K+。随着 AI 编码工具继续普及，「设计质量」成为下一波核心竞争力，Impeccable 有很好的卡位优势。核心风险是竞品可能会推出类似功能的原生方案（如 Cursor 直接内置设计能力）。

---

## 📂 关键文件路径速查

| 文件 | 用途 |
|------|------|
| `cli/engine/registry/antipatterns.mjs` | 27 条反模式规则注册表（核心知识库） |
| `cli/engine/detect-antipatterns.mjs` | 检测器入口（ESM + Browser） |
| `cli/engine/cli/main.mjs` | CLI 主流程（导入图构建 + 多引擎调度） |
| `skill/SKILL.src.md` | Skill 源文件（23 命令路由 + 设计法则） |
| `skill/reference/audit.md` | 设计审计参考模块 |
| `skill/reference/critique.md` | UX 深度评审参考模块 |
| `cli/engine/design-system.mjs` | 设计系统逆向工程模块 |
| `.agents/` | 15+ AI 工具适配层 |
| `extension/` | 浏览器扩展（Live 模式注入） |
| `site/` | impeccable.style 官网（Astro + Kinpaku 设计语言） |
| `tests/` | ~200 个测试用例 |
