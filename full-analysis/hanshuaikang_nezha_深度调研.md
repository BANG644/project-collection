# hanshuaikang/nezha（哪吒）深度调研

> **调研日期**: 2026-06-19 | **Stars**: ★ Trending | **语言**: TypeScript/Rust (Tauri) | **许可**: 开源

## 项目定位

**哪吒（Nezha）是一款专为 AI 编程时代打造的轻量级跨平台 IDE**。它解决了 AI 编程的核心痛点：当 AI 开始并行写代码时，人类开发者如何同时跟踪多个项目的多个 AI 会话？

传统 IDE（VS Code、JetBrains）以**开发者手动编码**为核心设计，而哪吒以 **Agent 优先**为设计理念，将多项目工作区、任务生命周期追踪、原生终端、Git Worktree、会话回放和 Skill 管理整合到单一界面中。

## 核心架构

### 技术栈
- **桌面框架**: Tauri（Rust 后端，极致轻量）
- **前端**: React
- **终端**: xterm.js
- **AI 集成**: 原生集成 Claude Code 和 Codex

### 安装包大小: 仅 7MB！远小于 VS Code 的数百 MB

### 核心功能

| 功能 | 描述 |
|------|------|
| **多项目工作区** | 在单个应用内同时管理多个项目下的多个 Claude Code/Codex 会话 |
| **会话自动发现** | 会话结束后自动可视化内容，方便回顾和 Resume |
| **通知提醒** | 当 AI 需要人工介入时，自动弹出消息和应用角标 |
| **原生 Git 集成** | AI 生成 Git Message、CodeReview 视图、Git Worktree 支持 |
| **轻量级代码编辑器** | 支持所有常见编程语言的语法高亮 |
| **Markdown 编辑器** | 支持 Markdown 预览 |
| **Skill 管理** | 通过软链集中管理所有本地 Skill |
| **三种 UI 主题** | 白天、黑夜、护眼模式 |

### 核心设计理念

> "人写的代码越来越少，AI 写的代码越来越多。写代码本身开始变成可以并行的事情，但人的注意力是有限的。如何快速跟踪多个项目的任务，就是哪吒想要解决的事情。"

## 安装与使用

```bash
# macOS 安装后需绕过未签名限制
xattr -rd com.apple.quarantine /Applications/nezha.app

# 前置条件：需先安装 Claude Code / Codex
```

## 社区与口碑

- 来自同一作者 [hanshuaikang](https://github.com/hanshuaikang) 的 **AI-Media2Doc** 也已被星标
- LinuxDO 社区支持
- 多个推特 KOL（@aigclink、@QingQ77、@ilovek8s）关注和转发
- 被多个中文自媒体报道

## 竞品对比

| 特性 | Nezha (哪吒) | VS Code | Cursor | Claude Code CLI |
|------|------------|---------|--------|----------------|
| 多项目并行管理 | ✅ 原生支持 | ❌ 需插件 | ❌ | ❌ |
| 安装包大小 | 7MB | ~300MB | ~200MB | CLI |
| AI Agent 集成 | ✅ Claude Code + Codex | ❌ 需插件 | ✅ 内置 | ✅ 单一 |
| 会话可视化 | ✅ 自动 | ❌ | ❌ | ❌ |
| Git Worktree | ✅ 原生 | ❌ 需插件 | ❌ | ❌ |
| Skill 管理 | ✅ 原生 | ❌ 需插件 | ❌ | ❌ |
| 通知提醒 | ✅ 自动 | ❌ | ❌ | ❌ |
| 跨平台 | ✅ (Win/Mac/Linux) | ✅ | ✅ (Mac/Win) | ✅ |

## 核心研判

**价值**: ⭐⭐⭐⭐⭐ (极高)
- 精准切入 AI 编程时代的新痛点 — 多 Agent 并行管理的注意力瓶颈
- 7MB 极致轻量设计，Tauri 技术栈性能优异
- 差异化定位明确，非 VS Code 替代品，而是 AI 编程的**补充工具**
- 概念新颖，市场空白明确

**适用场景**: 
- 同时管理多个 Claude Code/Codex 项目的开发者
- 需要快速在多个 AI 编程会话间切换的团队
- 希望用 AI 并行加速开发工作流的个人开发者

**风险**: 
- 依赖 Claude Code/Codex 生态
- 需要 macOS 用户绕过未签名应用限制
- 项目仍处于早期阶段

## 关键文件路径

- `src/` — 前端源码（React）
- `src-tauri/` — Tauri Rust 后端
- `docs/images/` — 文档截图和说明
- `README.md` / `README_EN.md` — 中英文文档

---

*报告由 AI 自动生成，基于 GitHub README、项目文档和社区反馈*
