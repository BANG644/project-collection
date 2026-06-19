# agentmemory 深度调研报告

> **仓库**: rohitg00/agentmemory  
> **Stars**: 23,361 | **语言**: TypeScript | **许可**: 自定义  
> **标签**: agentmemory, agents, ai, claude, claudecode, codex, copilot, cursor, genai, memory, openclaw  
> **调研日期**: 2026-06-19

---

## 项目全景

agentmemory 是为 AI 编程 Agent（如 Claude Code、Codex CLI、Cursor、OpenClaw 等）提供的**持久化记忆系统**，基于 iii 引擎构建。它让 Agent 在不同会话间记住上下文、偏好、决策历史，号称"再也不用重新解释你的项目"。

### 核心数据
- **23.3K⭐** GitHub Stars（高速增长中）
- 基于真实基准测试：**95.2% retrieval R@5**
- **92% 更少 token 消耗**（通过记忆缓存减少重复上下文）
- **53 个 MCP 工具 + 12 个自动钩子**
- **0 外部数据库依赖**（纯内存 + 文件持久化）
- **1,423+ 测试通过**
- 支持 NPM 全局安装 + npx 零安装

---

## 核心架构

### 架构层级

```
┌──────────────────────────────────┐
│  AI Coding Agent (Claude Code,    │
│  Codex CLI, Cursor, OpenClaw...)  │
├──────────────────────────────────┤
│  Agent ↔ MCP / Hooks / Plugin     │
├──────────────────────────────────┤
│  agentmemory Server (:3111)       │
│  ├── 记忆引擎 (iii engine)         │
│  ├── 知识图谱 (实体关系)           │
│  ├── 混合检索 (语义+关键词)        │
│  ├── 置信度评分                    │
│  └── 生命周期管理                  │
├──────────────────────────────────┤
│  持久化层 (文件系统 / 可选外部)     │
└──────────────────────────────────┘
```

### 记忆引擎 (iii engine)

agentmemory 的核心是 [iii engine](https://github.com/iii-hq/iii) — 一个轻量级、零外部依赖的记忆引擎，核心特性：

1. **置信度评分（Confidence Scoring）**：每条记忆附带置信度分数，低置信度记忆自动衰减
2. **生命周期管理**：记忆可设置 TTL，过期自动清理
3. **知识图谱**：实体之间的关系自动构建和查询
4. **混合检索**：语义相似度 + 关键词匹配双重检索，R@5 达 95.2%
5. **会话管理**：按会话隔离记忆，也可跨会话共享

### MCP 服务器

- 53 个 MCP 工具，几乎覆盖所有记忆操作
- 可通过 `agentmemory connect <agent>` 自动配置
- 支持所有 MCP 兼容的 Agent

---

## 安装与使用

### 快速安装

```bash
npm install -g @agentmemory/agentmemory   # 安装
agentmemory                                # 启动记忆服务器 (:3111)
agentmemory demo                           # 播种示例数据，验证召回
agentmemory connect claude-code            # 接入 Claude Code
npx skills add rohitg00/agentmemory -y     # 安装 15 个原生 skills
```

### 支持的 Agent

| Agent | 集成方式 | 深度 |
|-------|----------|------|
| Claude Code | 原生插件 + 12 Hooks + MCP | ⭐⭐⭐⭐⭐ |
| Codex CLI | 原生插件 + 6 Hooks + MCP | ⭐⭐⭐⭐⭐ |
| GitHub Copilot CLI | MCP + 插件 Hooks/Skills | ⭐⭐⭐⭐ |
| OpenClaw | 原生插件 + MCP | ⭐⭐⭐⭐⭐ |
| Hermes | 原生插件 + MCP | ⭐⭐⭐⭐⭐ |
| pi | 原生插件 + MCP | ⭐⭐⭐⭐⭐ |
| Cursor | MCP 服务器 | ⭐⭐⭐ |
| Gemini CLI | MCP 服务器 | ⭐⭐⭐ |
| OpenCode | 22 Hooks + MCP + 插件 | ⭐⭐⭐⭐⭐ |
| Cline / Goose / Kilo Code / Aider | MCP / REST | ⭐⭐⭐ |

---

## 竞品对比

| 特性 | agentmemory | mem0ai | supermemory | 原生（~/.claude/memory） |
|------|-------------|--------|-------------|--------------------------|
| Stars | 23.3K | ~20K | ~8K | — |
| 零外部依赖 | ✅ | ❌ 需要向量DB | ❌ 需要DB | ✅ |
| 置信度评分 | ✅ | ❌ | ❌ | ❌ |
| 知识图谱 | ✅ | 有限 | ❌ | ❌ |
| MCP 工具数 | 53 | ~10 | ~5 | 0 |
| Agent 支持数 | 12+ | 5 | 3 | 仅 Claude |
| 基准 R@5 | 95.2% | 未公开 | 未公开 | — |
| Windows 原生支持 | 有限(WSL推荐) | ✅ | ✅ | ✅ |
| NPM 生态 | ✅ | ✅ | ❌ | ❌ |

---

## 核心研判

### 优势
1. **零外部依赖**：不依赖任何向量数据库或外部服务，开箱即用
2. **全面 Agent 覆盖**：支持 12 种主流 AI 编程工具
3. **高性能检索**：95.2% R@5 召回率，业界领先
4. **丰富 API**：53 个 MCP 工具覆盖几乎所有记忆操作
5. **活跃社区**：GitHub Gist 设计文档 1.3K⭐

### 不足
1. **Windows 支持有限**：原生引擎设置较复杂，推荐 WSL
2. **自研引擎依赖**：绑定 iii engine，生态风险
3. **许可不明确**：缺少标准开源许可证声明

### 适用场景
- 多 Agent 共享上下文的团队项目
- 需要持久记忆的长期 AI 开发工作流
- 对隐私敏感、不希望依赖外部服务的场景

---

## 关键文件路径

| 文件 | 说明 |
|------|------|
| `README.md` | 主文档 + 安装指南 |
| `INSTALL_FOR_AGENTS.md` | Agent 专用安装指引 |
| `integrations/openclaw/` | OpenClaw 集成 |
| `integrations/hermes/` | Hermes 集成 |
| `integrations/pi/` | pi 集成 |
| `assets/demo.gif` | 演示 GIF |
| `READMEs/README.zh-CN.md` | 简体中文文档 |
| GitHub Gist `2067ab416f7bbe447c1977edaaa681e2` | 设计文档 (1.3K⭐) |
