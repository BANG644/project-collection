# google-labs-code/design.md - 全方位深度调研

> 调研日期：2026-06-27 | Stars: ~21,000 | 语言：TypeScript (CLI) + Markdown (格式规范)
> GitHub: https://github.com/google-labs-code/design.md

## 一句话定位

**DESIGN.md 是 Google Labs 开源的一套给 AI Coding Agent 描述视觉设计系统的格式规范**——它以"YAML 设计令牌 + Markdown 叙事散言"的双层结构，让 AI 不是拿到一堆 RGB 值和 px 数字，而是理解一个设计"应该是什么"。

---

## 项目架构全景

### 目录结构

```
design.md/
├── PHILOSOPHY.md              ← 设计哲学（必读，非典型文档）
├── docs/spec.md               ← 格式规范正文
├── packages/cli/              ← TypeScript CLI 工具
│   ├── src/
│   │   ├── index.ts           ← CLI 入口
│   │   ├── commands/          ← diff / export / lint / spec 子命令
│   │   └── linter/            ← 核心：DTCC 合规检查 + 自动修复
│   │       ├── dtcg/          ← Design Token Community Group 规范校验
│   │       ├── linter/        ← 通用规则引擎（broken-ref / contrast-ratio 等）
│   │       └── fixer/         ← 自动修复器
│   └── scripts/
├── examples/                  ← 三个完整设计示例
│   ├── atmospheric-glass/     ← 大气玻璃风格
│   ├── paws-and-paths/        ← 动物救助品牌
│   └── totality-festival/     ← 日全食音乐节
├── .agents/skills/            ← 4 个 Agent Skill（含 ink/TDD/contracts）
└── bun.lock                   ← 使用 Bun 管理依赖
```

### 技术栈

- **CLI 工具**：TypeScript，通过 Bun 运行
- **格式规范**：纯 Markdown + YAML Front Matter
- **核心引擎**：自研 Linter（DTCC Conformance Checker）
- **测试**：Vitest（每个规则有对应 `.test.ts`）
- **CI/CD**：GitHub Actions (`test.yml`)

### 设计哲学（来自 PHILOSOPHY.md）

PHILOSOPHY.md 是这份规范的灵魂——它不定义语法，它定义"为什么要这样做"。5 个核心原则：

1. **Prose, not Tokens, is the focus** — 令牌只是上下文，散言才是设计的居所
2. **A specific reference carries more than a list of adjectives** — "一份 1970 年代老牌大学讲座讲义" 比 "现代、干净、可信" 传递更多信息
3. **Negative Constraints define character** — 命名的东西自带否定；不需要列出 20 条 "不要做什么"
4. **The format grows through its users** — 规范只定义结构最小集（name + 几个通用类别），其余开放
5. **Token values are context, not instructions** — 令牌值不是渲染指令，是给散言引用的上下文

---

## 核心源码解读

### DESIGN.md 格式的双层结构

这是整个项目的核心创新——DESIGN.md 不是 YAML 配置文件，不是 Figma Tokens JSON，而是一种**混合体**：

```markdown
---
name: Technical Handout
---

## Colors

```yaml
colors:
  paper: '#F4F0E4'
  ink: '#1E1A14'
  vermilion: '#C3402A'
```

A single-ink-plus-accent system.
- **Paper** {colors.paper} is the canvas — warmed xerox stock, never pure white.
- **Ink** {colors.ink} is graphite-warm and carries all typography...
- **Vermilion** {colors.vermilion} is the single accent and appears only inside diagrams...
```

**关键设计洞察**：
- YAML 层提供**机器可读的精确值**
- Markdown 散言层提供**人类和 AI 可读的设计语义**
- `{colors.paper}` 语法实现令牌到散言的**双向引用**
- 散言里写的不是 "主色是 #F4F0E4"，而是 "Paper is the canvas — warmed xerox stock, never pure white"

### CLI 工具核心：Linter 系统

CLI 工具的核心价值是**自动化质量检查**，确保 DESIGN.md 文件符合规范：

```
packages/cli/src/linter/
├── index.ts              ← Linter 主入口
├── lint.ts               ← 执行 lint 逻辑
├── dtcg/                 ← Design Token Community Group 合规
│   ├── spec.ts           ← DTCG 规范定义
│   ├── handler.ts        ← 检查处理器
│   └── conformance.test.ts
├── linter/
│   ├── handler.ts        ← 通用 lint 处理器
│   └── rules/
│       ├── broken-ref.ts ← 检测断裂的 {token} 引用
│       └── contrast-ratio.ts ← 检测颜色对比度
└── fixer/                ← 自动修复引擎
    ├── handler.ts
    └── spec.ts
```

**设计模式**：策略模式 + 规则引擎。每个 lint 规则是独立模块，通过 handler 注册到 lint pipeline。fixer 可以自动修复部分问题。

### CLI 命令体系

| 命令 | 功能 | 设计意图 |
|------|------|---------|
| `spec` | 验证 DESIGN.md 符合格式规范 | 保证格式正确性 |
| `lint` | 检查设计令牌的一致性 | 防止令牌引用断裂 |
| `diff` | 对比两个版本的 DESIGN.md | 追踪设计演变 |
| `export` | 导出为其他格式（如 CSS 变量、Tailwind 配置） | 桥接到实际工程 |

### 设计令牌的类型系统

从 spec.md 和 examples 中提取的 5 个标准类别：

| 类别 | 示例 | 在散言中的语义 |
|------|------|-------------|
| `colors` | `paper`, `ink`, `accent` | 不是 "primary-500"，而是有语义的命名 |
| `typography` | `body`, `heading`, `mono` | 字体家族 + 尺寸层级 |
| `spacing` | `unit`, `gutter`, `margin` | 空间节奏 |
| `rounded` | `card`, `button`, `input` | 圆角语义 |
| `components` | 自由定义 | 任何额外类别 |

---

## 全网口碑画像

### 好评共识

1. **解决了 AI Coding Agent 的"设计遗忘症"** — 每次新对话 AI 都从零开始理解你的品牌，DESIGN.md 相当于一个永久的视觉身份文件（sotasync.com 评测）
2. **负向约束的自带效应** — 命名"老牌大学讲义"后，AI 自动知道不加渐变、不放大标题，20 条否定规则被一句话替代
3. **Tokens 是上下文而非指令** — 这个设计决策让格式高度灵活，每个团队可以定义自己的类别（如 Motion 的动画曲线或音频域的时间常数）
4. **已有实际落地** — Google Stitch（Google 的 AI 设计工具）已在生产中使用，三个公开 example 证明可行性

### 差评共识与争议

1. **学习曲线存在** — 写好 DESIGN.md 需要"设计品味"和"命名能力"，不像 CSS 变量那样可以机械定义
2. **格式太新** — 2026 年 4 月才开源，生态工具链几乎为零（只有 CLI 和 bun 生态系统）
3. **AI 支持参差不齐** — Claude Code 通过 .agents/skills 有直接支持，但 Cursor/Copilot/GitHub Copilot 需要手动集成
4. **中文设计语境适配不足** — 示例全是英文设计风格（xerox stock、Substack register），中文排版（行距、字重、中英混排）缺乏参考

### 典型使用场景

- **AI 生成 UI** — 在项目根目录放 DESIGN.md，AI 生成的组件自动符合品牌设计
- **设计系统文档** — 取代传统 Figma 导出，用散言解释为什么用这个颜色而不是那个
- **多项目品牌一致性** — 公司级 DESIGN.md 确保所有子项目的 AI 生成都遵循同一视觉语言

---

## 竞品对比

| 维度 | DESIGN.md | Figma Tokens JSON | CSS 变量/Tailwind Config | 纯 Prompt 描述 |
|------|-----------|-------------------|--------------------------|---------------|
| **AI 友好度** | ★★★★★ 散言+令牌 | ★★★ 纯数值 | ★ 数值无语义 | ★★★★ 纯语义无精确值 |
| **人类可读** | ★★★★★ 写作文档 | ★★ JSON 难读 | ★★ 文件名即语义 | ★★★★★ |
| **工程集成** | ★★ 只有 CLI export | ★★★★★ Figma Plugin | ★★★★★ 直接可用 | ★ 零集成 |
| **精确度** | ★★★★ 有数值 | ★★★★★ 精确值 | ★★★★★ 精确值 | ★ 全靠 AI 心算 |
| **传递设计意图** | ★★★★★ 核心优势 | ★ 只有值 | ★ 只有值 | ★★★ 缺乏精确值 |
| **生态成熟度** | ★ 极新 | ★★★★★ 成熟 | ★★★★★ 成熟 | ★★ 无生态 |

**选择建议**：
- 用 DESIGN.md 当你的 AI Coding Agent 是你的主要前端开发者
- 用 Figma Tokens 当你是成熟设计团队需要自动化设计→代码 pipeline
- 用 Tailwind Config 当你的项目已经建立在 Tailwind 上
- 用纯 Prompt 当你的项目很简单或只是想快速尝试

---

## 核心研判

### 项目优势（不可替代的价值）

1. **"散言 + 令牌"是真正的格式创新**——不是 YAML 替代 JSON，不是 Markdown 替代 Figma，而是创造了一个新品类：既是人类可读的设计故事，又是机器可解析的精确规范
2. **Google Labs 背书 + 生产验证**——Stitch 已在使用，不是实验室玩具
3. **格式扩展性极强**——标准类别只是建议，任何团队可以定义自己的类别（Motion、Iconography、Elevation），不需要等规范更新
4. **"负面约束自带"的设计哲学深刻**——命名 = 约束（"1970 年代讲义"自带 "不要渐变"），这是和传统设计系统文档的根本区别

### 项目风险

1. **Google 内部项目开源的典型风险**——如果 Stitch 团队转向，这个格式可能变成孤儿项目
2. **生态几乎为零**——CLI 只有 lint/diff/export，没有 IDE 插件、没有 Figma 导入、没有 AI Agent 之外的消费端
3. **需要"设计品味"的门槛**——写好 DESIGN.md 需要理解"具体参照 vs 形容词列表"的哲学，这不是每个团队都能做到的
4. **Token 引用的 `{color.paper}` 语法有脆弱性**——改名会断裂所有引用（CLI lint 能检测，但修复需手动）

### 趋势判断

**上升期早期**。21K Stars 在不到两个月内积累（2026-04 开源），Google 品牌效应明显。但能否从 "Google 做的酷东西" 变成 "行业标准" 取决于：
- 至少 2-3 个大型开源项目公开采用
- 出现 Figma → DESIGN.md 的转换工具
- Claude/Cursor/Copilot 官方支持（而不是靠 .agents/skills 手工集成）

### 适用场景
- 用 AI Coding Agent 做前端开发的团队
- 需要在多项目间保持视觉一致性的组织
- 想用文字替代 Figma 来传递设计意图的设计师

### 不适用场景
- 不需要 AI 生成 UI 的传统前端项目
- 设计系统已经在 Figma + Token Studio 中成熟运作的团队
- 短期内需要工程化设计 tokens 到代码的项目（等生态成熟）

---

## 关键文件路径速查

| 文件 | 用途 | 重要度 |
|------|------|--------|
| `PHILOSOPHY.md` | 设计哲学——理解"为什么"的入口 | ⭐⭐⭐⭐⭐ |
| `docs/spec.md` | 格式规范——定义结构最小集 | ⭐⭐⭐⭐⭐ |
| `packages/cli/src/index.ts` | CLI 入口 | ⭐⭐⭐ |
| `packages/cli/src/linter/index.ts` | Linter 主逻辑 | ⭐⭐⭐⭐ |
| `packages/cli/src/linter/dtcg/conformance.test.ts` | DTCC 合规测试 | ⭐⭐⭐ |
| `packages/cli/src/linter/linter/rules/broken-ref.ts` | 断裂引用检测 | ⭐⭐⭐ |
| `packages/cli/src/commands/export.ts` | 导出为其他格式 | ⭐⭐⭐ |
| `examples/atmospheric-glass/DESIGN.md` | 完整设计示例 | ⭐⭐⭐⭐ |
| `examples/totality-festival/DESIGN.md` | 第二个示例（日全食音乐节） | ⭐⭐⭐⭐ |
| `.agents/skills/ink/SKILL.md` | Agent Skill——DESIGN.md 使用指南 | ⭐⭐⭐⭐ |
