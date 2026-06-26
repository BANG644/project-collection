# My Claude Code Setup 全方位深度调研报告

> **仓库**: [centminmod/my-claude-code-setup](https://github.com/centminmod/my-claude-code-setup)
> **调研日期**: 2026-06-17
> **分类**: Claude Code 配置 / AI 开发工具 / 记忆系统

---

## 1. 项目定位

这是一个**Claude Code 的起步配置和模板集合**，提供 CLAUDE.md 模板、钩子脚本、斜杠命令和记忆库文件系统，帮助用户更好地利用 Claude Code 进行开发。核心是一套 CLAUDE.md 记忆库系统，让 AI 跨多次会话保留上下文。

**一句话定位**：把你的 CLAUDE.md 调教到能记住你是谁、你在做什么。

**目标用户**：
- Claude Code 的新用户
- 需要 AI 跨会话保持上下文的开发者
- 希望优化 Claude Code 行为和输出的用户

---

## 2. 核心架构

### CLAUDE.md 记忆库系统

仓库的核心是一个**多文件记忆库系统**，通过 CLAUDE.md 文件指导 Claude Code 维护一组记忆文件：

```
CLAUDE.md ── 主配置文件
├── CLAUDE-template-1.md     # 渐进式披露模板
├── CLAUDE-template-2.md     # 双记忆架构模板
├── CLAUDE-template-3.md     # 独立行为规则模板
├── CLAUDE-migrate-to-new-template.md  # 迁移指南
├── CLAUDE-cloudflare.md     # Cloudflare/ClerkOS 参考
└── CLAUDE-convex.md         # Convex 数据库参考
```

### 配套文件

| 文件 | 说明 |
|------|------|
| `.claude/settings.json` | 钩子和斜杠命令配置 |
| `CLAUDE.md` | 主记忆库指令 |
| `CLAUDE-template-*.md` | 3 种官方最佳实践模板 |
| `README-v2.md` | 渐进式披露指南 |
| `README-v3.md` | 任务导向指南 |
| `README-v4.md` | 技术参考手册 |

---

## 3. 关键特性

- **双记忆架构** — 短期记忆 + 长期记忆文件系统
- **渐进式披露** — 从新手到高级逐步展开
- **独立行为规则** — 按项目定制的 AI 行为规则
- **迁移指南** — 从旧模板迁移到新模板的 AI 提示
- **Cloudflare/ClerkOS 支持** — 为这些平台定制的参考文档
- **Convex 支持** — Next.js + React + Convex 的参考
- **多格式 README** — 同一内容 4 种不同风格的 README

---

## 4. 使用方式

1. 克隆仓库到项目目录
2. 选择适合的 CLAUDE.md 模板（1/2/3）
3. 运行 `/init` 让 Claude Code 分析代码库并填充记忆库
4. 安装推荐工具：`brew install ripgrep fd jq`
5. 可选：安装 VS Code + Claude Code 扩展

**Z.AI 集成**：支持通过 Z.AI 获得更高 token 配额和 GLM-4.7 模型访问。

---

## 5. 社区口碑

- 由知名的 Centmin Mod 作者维护，技术可靠性高
- 文档极其详尽，有 4 种不同风格的 README
- 持续更新，2026 年 5 月刚更新了 CLAUDE.md 模板
- 生态丰富：包含 Cloudflare、Convex 等框架参考

---

## 6. 竞品对比

| 项目 | 定位 | CLAUDE.md | 记忆库 | 模板 | 多框架 |
|------|------|-----------|--------|------|--------|
| **my-claude-code-setup** | 综合起步配置 | ✅ 核心 | ✅ 双架构 | ✅ 3种 | ✅ |
| **官方文档** | 官方参考 | ❌ 基础 | ❌ | ❌ | ❌ |
| **社区模板** | 单一模板 | ⚠️ | ⚠️ | ❌ | ❌ |

---

## 7. 核心研判

**优势**：
- 最完整的 Claude Code 起步配置之一
- 3 种不同风格的模板适应不同需求
- 记忆库系统解决 AI 跨会话遗忘的问题
- 作者信誉好，持续维护

**劣势**：
- macOS 有特定依赖（Terminal-Notifier）
- 配置较多，新手可能需要时间消化
- 部分功能依赖特定平台（macOS 通知）

**适用场景**：
- Claude Code 新手上路的最佳伴侣
- 需要跨会话记忆的长期项目
- 多框架开发的 Claude Code 配置

---

## 8. 关键文件路径

| 文件 | 说明 |
|------|------|
| `CLAUDE.md` | 主配置/记忆库指令 |
| `CLAUDE-template-1.md` | 渐进式披露模板 |
| `CLAUDE-template-2.md` | 双记忆架构模板 |
| `CLAUDE-template-3.md` | 独立行为规则模板 |
| `CLAUDE-migrate-to-new-template.md` | 迁移指南 |
| `.claude/settings.json` | 钩子和斜杠命令 |
| `CLAUDE-cloudflare.md` | Cloudflare 参考 |
| `CLAUDE-convex.md` | Convex 参考 |
