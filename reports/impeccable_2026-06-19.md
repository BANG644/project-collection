# Impeccable 深度调研报告

> **仓库**: pbakaus/impeccable  
> **Stars**: 39,471 | **语言**: JavaScript | **许可**: 未明确  
> **标签**: design, ai-coding, skills, frontend  
> **调研日期**: 2026-06-19  
> **作者**: pbakaus（Opera 浏览器前 CEO、Firebug 创始人）

---

## 项目全景

Impeccable 是一个**AI 编程 Agent 的前端设计指导系统**——1 个技能、23 个命令、44 个确定性检测器规则 + 浏览器实时迭代。通过为一个常见问题提供结构化设计指南，Impeccable 帮助 AI 编写的前端代码摆脱典型的"AI 模板感"。

### 起源

从 Anthropic 的 [frontend-design](https://github.com/anthropics/skills/tree/main/skills/frontend-design) 出发，Impeccable 远超前者。

### 核心数据
- **39.5K⭐** GitHub Stars（高速增长中）
- **23 个设计命令**：覆盖从设计到审计到动画的全流程
- **44 个确定性检测器规则**：无需 LLM 即可运行
- **跨平台安装**：Claude Code / Cursor / Codex / Gemini CLI / OpenCode / Pi / Copilot
- **完整网站**：[impeccable.style](https://impeccable.style) 含案例研究

---

## 核心架构

### 三层设计系统

```
┌──────────────────────────────────────────┐
│  用户命令 (/impeccable <command> <target>) │
├──────────────────────────────────────────┤
│  技能核心                                  │
│  ├── init: 项目初始化 (PRODUCT.md + DESIGN.md)│
│  ├── craft: 完整设计流程 (形塑→构建→迭代)    │
│  ├── 21 个专项命令                            │
│  └── live: 浏览器实时迭代                     │
├──────────────────────────────────────────┤
│  检测引擎                                  │
│  ├── 44 个确定性规则 (无 LLM, 无 API Key)   │
│  └── LLM 辅助评审                           │
├──────────────────────────────────────────┤
│  浏览器扩展 / CLI / 子模块                   │
└──────────────────────────────────────────┘
```

### Anti-Patterns（明确需避免的设计模式）

Impeccable 最关键的差异化——它明确列出了 AI 生成的典型反模式：

- ❌ 过度使用 Arial / Inter / 系统默认字体
- ❌ 彩色背景上的灰色文字
- ❌ 纯黑/纯灰色（永远用色调）
- ❌ 全部卡片化、卡片嵌套卡片
- ❌ 弹跳/弹性缓动（过时感）

---

## 23 个命令详解

| 命令 | 功能 | 适用阶段 |
|------|------|----------|
| `craft` | 完整形塑→构建→视觉迭代 | 初期 |
| `init` | 一次设置：写 PRODUCT.md + DESIGN.md | 初始化 |
| `document` | 从现有项目代码生成 DESIGN.md | 中期 |
| `extract` | 提取可复用组件和设计 Token | 中期 |
| `shape` | 写代码前的 UX/UI 规划 | 初期 |
| `critique` | UX 设计评审：层次、清晰度、情感共鸣 | 迭代 |
| `audit` | 技术质量检查（可访问性、性能、响应式） | 终期 |
| `polish` | 最终打磨、设计系统对齐、发布准备 | 终期 |
| `bolder` | 放大平庸设计 | 迭代 |
| `quieter` | 调低过于大胆的设计 | 迭代 |
| `distill` | 剥离到本质 | 迭代 |
| `harden` | 错误处理、国际化、文本溢出、边界情况 | 终期 |
| `onboard` | 首次体验流程、空状态、激活路径 | 迭代 |
| `animate` | 添加有目的性的动效 | 迭代 |
| `colorize` | 引入战略性色彩 | 迭代 |
| `typeset` | 字体选择、层次、大小修正 | 迭代 |
| `layout` | 布局、间距、视觉节奏修正 | 迭代 |
| `delight` | 添加愉悦时刻 | 优化 |
| `overdrive` | 添加技术上非凡的效果 | 优化 |
| `clarify` | 改进不清晰的 UX 文案 | 迭代 |
| `adapt` | 适配不同设备 | 终期 |
| `optimize` | 性能改进 | 终期 |
| `live` | 浏览器可视化变体模式：在浏览器中迭代元素 | 迭代 |

使用 `/impeccable pin <command>` 创建快捷方式（如 `pin audit` 创建 `/audit`）。

---

## 安装方式

### 方式一：CLI 安装器（推荐）

```bash
npx impeccable install
```

自动检测当前工具链（Claude Code / Cursor / Codex 等），选择项目级或全局安装。

更新：`npx impeccable update`

### 方式二：Git 子模块（团队共享）

```bash
git submodule add https://github.com/pbakaus/impeccable .impeccable
npx impeccable link --source=.impeccable --providers=claude,cursor
```

### 方式三：手动复制

```bash
# Cursor
cp -r dist/cursor/.cursor your-project/

# Claude Code
cp -r dist/claude-code/.claude your-project/

# OpenCode / Pi / Gemini CLI / Codex CLI
# 对应复制 dist 目录下的对应文件夹
```

---

## 竞品对比

| 特性 | Impeccable | Anthropic frontend-design | UI-UX-Pro-Max | Shadcn/ui |
|------|------------|--------------------------|---------------|-----------|
| Stars | 39.5K | 部分收录 | ~5K | ~80K |
| 命令数 | 23 | 3-5 | 10+ | — |
| 确定性检测器 | ✅ 44 规则 | ❌ | ❌ | ❌ |
| 浏览器实时迭代 | ✅ live 模式 | ❌ | ❌ | ❌ |
| 完整 DESIGN.md | ✅ | ❌ | ❌ | ❌ |
| 反模式清单 | ✅ 明确 | ⚠️ 有限 | ❌ | ❌ |
| 多 Agent 支持 | 10+ | 仅 Claude | 仅 OpenClaw | 无 Agent |
| 案例研究 | ✅ impeccable.style | ❌ | ❌ | ❌ |
| 创始人背景 | Opera 前 CEO | 团队项目 | 个人 | — |

---

## 核心研判

### 优势
1. **反模式指导**：明确列出 AI 生成的 6 大类典型问题，AI 直接避免
2. **23 个命令覆盖全流程**：从原型到发布再到微调，一站到位
3. **44 个确定性规则**：无需 LLM 即可基础检查，速度快
4. **创始人背书**：pbakaus（Opera CEO / Firebug 创始人）的 UI/UX 深度
5. **跨平台支持**：10+ 主流 AI 编程工具
6. **浏览器实时迭代**：`live` 命令直接在浏览器中显示变体

### 不足
1. **许可不明确**：未标注开源许可证
2. **学习曲线**：23 个命令需要一定学习成本
3. **依赖 CLI**：`npx impeccable install` 需要联网和 npm

### 适用场景
- AI 编程工具用户想获得专业级前端设计
- 讨厌"AI 模板感"的开发者
- 团队需要统一的设计指导规范
- 从零开始到发布的完整 UX/UI 工作流

---

## 关键文件路径

| 文件 | 说明 |
|------|------|
| `README.md` | 主文档 |
| `dist/claude-code/` | Claude Code 分发 |
| `dist/cursor/` | Cursor 分发 |
| `dist/codex/` | Codex CLI 分发 |
| `dist/gemini/` | Gemini CLI 分发 |
| `dist/opencode/` | OpenCode 分发 |
| `dist/pi/` | pi 分发 |
| `dist/agents/` | Vercel Agents 分发 |
| `DETECTORS.md` | 44 个检测器规则文档 |
| `PRODUCT.md` | init 输出 - 产品定义 |
| `DESIGN.md` | init 输出 - 设计规范 |
| https://impeccable.style | 官方网站 + 案例研究 |
