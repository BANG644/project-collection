# 🔬 anomalyco/opencode — 全方位深度调研

## 📌 一句话定位

**anomalyco 出品、180k⭐ 的开源 AI 编码 Agent**——终端原生 TUI 体验 + 双 Agent（Build/Plan）架构 + 40+ 语言 LSP 原生集成 + 75+ 模型自由切换 + 客户端/服务器分离架构，是目前增长最快的开源 AI 编程代理。

## ⭐ 项目亮点

1. **LSP 原生集成，实现自动"自修正循环"**——这是 OpenCode 对 Claude Code、Aider 等所有终端 AI 编码工具的**降维打击**：代理写完代码后，LSP 实时分析类型错误并自动修正，无需手动跑 `tsc` 或 linter（实测 TypeScript 重构可自动修复 40+ 文件的下游类型错误）
2. **双 Agent 架构（Build + Plan）**：`Tab` 键一键切换——Plan 只读分析不写文件，Build 全权限执行。同一个对话上下文，先分析后执行，流畅度超过 Claude Code 的单一 Agent 模式
3. **完全模型无关（75+ 提供商）**：Claude、OpenAI、Google、Ollama 本地模型——`opencode --model` 一键切换，复杂编码用 Sonnet，快速探索用 GPT-4o Mini，敏感代码用本地 Llama，**零供应商锁定**
4. **客户端/服务器架构**：Agent 运行时在服务器端独立运行，TUI / Desktop / IDE 扩展都是客户端实现——可远程驱动、团队共享同一 Agent 会话，这是大多数单体架构的 AI 编码代理做不到的
5. **细粒度权限系统（按命令级别）**：不像 Claude Code 只能按大类（bash 全许/全禁），OpenCode 可以细到 `git status: allow` 但 `git push: ask`，`rm -rf *: deny`

## 🏗️ 项目架构全景

### 目录结构

```
opencode/
├── packages/
│   ├── opencode/       ← 核心 Agent 运行时（主体）
│   ├── opencode-app/   ← 桌面应用（Tauri）
│   ├── docs/           ← 文档
│   └── ...
├── apps/
│   └── desktop/        ← 桌面客户端（macOS/Win/Linux Beta）
├── config/             ← 配置模板
└── scripts/            ← 安装脚本
```

### 技术栈

- **核心语言**：TypeScript（60.2%）+ Rust（0.4%，原生模块）
- **构建系统**：Turborepo Monorepo
- **包管理**：Bun
- **桌面端**：Tauri（非 Electron，更轻量）
- **基础设施**：SST
- **文档**：MDX（36.2%）
- **代码检查**：Oxlint + Prettier
- **版本节奏**：每 2-4 天一个 Release（极速迭代）

### 核心架构设计

```
┌─────────────────┐     HTTP     ┌──────────────────┐     ┌─────────────────┐
│    客户端层      │◄───────────►│   代理服务器       │◄───►│    外部工具      │
│                  │  端口 4096  │                  │     │                 │
│ • 终端 TUI       │             │ • Agent 运行时     │     │ • LSP 服务器    │
│ • Desktop (Tauri)│             │ • 工具执行引擎     │     │ • MCP 服务器    │
│ • IDE 扩展       │             │ • 会话/上下文管理  │     │ • Git, Docker   │
│ • Web 界面       │             │ • 75+ 模型路由     │     │ • 75+ 大模型    │
└─────────────────┘             └──────────────────┘     └─────────────────┘
```

**关键设计决策**：客户端层可以完全无状态——服务器跑在性能强的工作站上，笔记本/手机轻量连接。支持 mDNS 局域网自动发现。这意味着**团队协作调试**和**远程驱动**成为默认能力。

## 💡 应用场景与启发

### 典型使用场景

1. **日常 AI 编码伴侣**——替代 Claude Code 但没有供应商锁定。`/init` 自动检测项目语言并启动 LSP，开箱即用
2. **TypeScript/Python 大型重构**——LSP 自修正在重命名/改签名时自动修复所有下游文件，比手动 `tsc` + 喂回错误给 AI 高效 10 倍
3. **多模型按任务路由**——快速探索用 Gemini，复杂实现用 Claude，安全审计用本地 Ollama
4. **远程开发**——服务器跑在云端或工作站，笔记本 TUI 或手机远程连接
5. **安全审计**——自定义安全审计 Agent（只读 + 仅 `npm audit` 允许），绝不可能误改生产代码

### 可借鉴的解决方案模式

- **LSP 驱动的自修正循环**：任何 AI 编码工具都可以接入 LSP 实现自动纠错——这比"写完代码跑测试看结果"的反馈循环快了一个数量级
- **按 Agent 的细粒度权限模型**：用 YAML/MD 文件定义 Agent，每 Agent 配置独立的工具白名单——安全审计 Agent 的权限与开发 Agent 完全分离
- **客户端/服务器分离的 Agent 架构**：前端只是 UI 实现，运行时完全在服务端——天然支持远程、协作、多端使用

### 同类需求的可参考思路

OpenCode 的**双 Agent 设计（Tab 切换 Plan ↔ Build）** 是所有编码工具的教科书级设计模式：先理解再执行，同一个上下文无缝过渡。Claude Code 直到最近才加入类似的 plan mode，说明这个设计的正确性已被市场验证。

## 🧠 核心源码解读（克制代码量）

### 双 Agent 架构

两个独立的 Agent 实例，共享同一个对话上下文：

- **Build Agent**：默认，全权限——读/写文件、执行命令、安装依赖
- **Plan Agent**：只读——阅读代码、搜索文件、理解架构，**拒绝文件写入**，Bash 操作需要用户逐条审批

`Tab` 键在两者之间切换，上下文完全共享——这是一个"先分析后执行"的丝滑工作流。

### LSP 自修正循环

```
Agent 写代码 → LSP 实时分析 → LSP 报告诊断 → Agent 自动修正 → LSP 确认无误 → 继续下一任务
```

```json
{
  "lsp": {
    "typescript": {
      "command": "typescript-language-server",
      "args": ["--stdio"],
      "filetypes": ["typescript", "typescriptreact", "javascript"],
      "root_markers": ["tsconfig.json", "package.json"]
    }
  }
}
```

**隐藏约束**（从社区反馈提炼）：LSP 支持目前标记为实验性，TypeScript 和 Python 表现很好，但冷门语言偶有问题。启用 LSP 后内存占用增加 200-500MB。

### 权限系统（比 Claude Code 细两个级别）

```json
{
  "permission": {
    "edit": "allow",
    "write": "allow",
    "bash": {
      "*": "ask",
      "git status": "allow",
      "git diff": "allow",
      "git push *": "ask",
      "rm -rf *": "deny"
    },
    "webfetch": "deny"
  }
}
```

三个级别：`allow`（不问）→ `ask`（每次确认）→ `deny`（完全禁止）。可以在单条命令级别配置——Claude Code 的按大类划分与之相比显得粗放。

## 📐 架构决策与设计哲学

- **客户端/服务器分离 > 单体架构**：这既是优势（远程/协作/多端）也是风险（CVE 级别的未认证 RCE 漏洞曾因此产生）
- **Tauri > Electron**：Desktop 端用 Tauri（Rust），更轻量、更安全
- **LSP 原生 > 文本模式**：理解代码用 AST/语义分析（LSP）而非字符串匹配，质量提升巨大但开销也大
- **权限显式 > 默认宽松**：[CVE-2025-XXXXX](https://github.com/anomalyco/opencode/issues/6355) 级别的漏洞说明：本地开发工具的 C/S 架构天然比单体多出一个攻击面

## 🌐 全网口碑画像

### 好评共识

- "LSP 自修正太香了，改个接口类型，40+ 文件全部自动修好"（知乎，[2026-05-20](https://zhumengzhu.github.io/2026/05/opencode-deep-research/)）
- "模型自由是真的自由，复杂编码用 Sonnet，探索用 GPT-4o Mini，绝不锁死"（头条，[2026-06-05](https://www.toutiao.com/article/7647698196777239055/)）
- "160k 星开源项目，迭代比很多商业产品还快"（iDao）
- "自定义安全代理的细粒度权限模型绝了，绝对不让 Agent 碰生产代码"（知乎）
- "终端体验拉满——多行编辑、斜杠命令、流式工具输出，Neovim 用户狂喜"（Tinyash）

### 差评共识 & 踩坑高发区

- **严重安全前科**：曾爆出未认证 RCE 漏洞（Issue [#6355](https://github.com/anomalyco/opencode/issues/6355)，CVSS 约 10 分），本地服务器无认证，任意网站可执行任意代码
- **长会话退化**：10 万 token 后响应变慢、质量下降，自动压缩不如 Claude Code 顺滑
- **补丁偶尔失败**：三天内两次补丁无法正确应用，重试后更乱——Claude Code 的编辑系统更可靠
- **文档严重缺失**：大量配置选项只在 GitHub Issue 里提过，没有正式文档
- **内存大户**：TypeScript LSP 启动后约 1.2GB 内存占用（Claude Code 约 400MB）
- **命名争议**："OpenCode"名字原属另一个项目（Go 语言写的终端 AI 工具，1.1 万星），原版被迫改名"Crush"——社区有争议

### 争议焦点

OpenCode 的增长速度（280 天从 0 到 180k⭐）引发了一些质疑——是否因为"OpenCode"这个名字让用户误以为是原版项目？这个争议从未完全消失。

## ⚔️ 竞品对比

| 维度 | OpenCode | Claude Code | Cursor | Aider |
|------|----------|-------------|--------|-------|
| **开源** | ✅ MIT | ❌ 闭源 | ❌ | ✅ Apache 2.0 |
| **模型灵活性** | 75+ 提供商 | 仅 Anthropic | 多模型 | 多模型 |
| **界面** | TUI + Desktop + IDE | 终端 | IDE | 终端 |
| **LSP 集成** | ✅ 原生（~40 语言） | ❌ 无 | 通过 IDE | ❌ 无 |
| **双 Agent** | ✅ Build + Plan | 内置子 Agent | 有限 | ❌ |
| **MCP 支持** | ✅ 有 | ✅ 生态更大 | ❌ | ❌ |
| **权限粒度** | 按命令级别 | 按大类 | 基础 | 每次确认 |
| **桌面端** | Tauri（轻量） | Electron | IDE 自身 | 无 |
| **内存** | ~1.2GB (LSP) | ~400MB | 视 IDE 而定 | <100MB |
| **安全记录** | 曾有严重 RCE | 无重大问题 | 无重大问题 | 无重大问题 |
| **文档** | 缺失 | 完善 | 完善 | 完善 |
| **版本节奏** | 2-4 天 | 月更 | 月更 | 周更 |

### 核心研判

OpenCode 的差异化护城河是 **LSP 原生集成 + 模型自由**。但在安全性和稳定性上付出了代价——它的定位更适合**愿意接受一定风险的先行者**，而非追求稳定可靠的生产环境。

## 🎯 核心研判

**项目优势**：
- LSP 自修正是真正的杀手级特性，目前无竞品做到
- 180k⭐ 的社区信任 + 2-4 天迭代速度，生态很快会赶上
- 模型无关 + C/S 分离，架构前瞻性远超竞品

**项目风险**：
- **严重安全前科**（RCE）是悬在头顶的达摩克利斯之剑——C/S 架构需要更完善的安全设计
- 长会话稳定性和补丁可靠性不如 Claude Code，影响重度用户信任
- 文档缺失 + 更新过快导致用户落地成本高
- "OpenCode"命名争议在社区留下阴影

**适用场景**：TypeScript/Python 程序员、多模型使用者、远程开发爱好者和愿意尝试新工具的先行者
**不太适用**：安全敏感环境、需要长会话稳定生产工具、文档驱动的企业团队

**趋势判断**：🔥 极速上升期——280 天从 0 到 180k⭐，LSP 自修正尚无竞品做到，但必须解决安全信任问题才能成为主流

## 📂 关键文件路径速查

| 文件/目录 | 说明 |
|-----------|------|
| `packages/opencode/` | 核心 Agent 运行时 |
| `packages/opencode-app/` | 桌面应用（Tauri） |
| `config/` | 权限/LSP 配置模板 |
| `scripts/` | 安装脚本 |
| `packages/docs/` | 文档（MDX） |
| `apps/desktop/` | 桌面客户端 |
| **默认配置路径** | `~/.config/opencode/` |
| **自定义 Agent 路径** | `~/.config/opencode/agents/*.md` |
