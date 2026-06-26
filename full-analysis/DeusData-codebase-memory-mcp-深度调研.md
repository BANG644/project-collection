# 🚀 DeusData/codebase-memory-mcp — 高性能代码智能 MCP 服务器

> GitHub: [DeusData/codebase-memory-mcp](https://github.com/DeusData/codebase-memory-mcp)  
> ⭐ 7,023 | 🔄 564 forks | 🏆 今日 2,322 stars  
> 语言: C | 协议: MIT  
> 抓取日期: 2026-06-19

---

## 一、项目概述

**codebase-memory-mcp** 是一个高性能的代码智能 MCP（Model Context Protocol）服务器，能将代码仓库索引为持久化知识图谱。号称是"AI 编程 Agent 最快、最高效的代码智能引擎"——对普通仓库的**全量索引仅需毫秒级**，Linux 内核（28M LOC，75K 文件）也只需 3 分钟。查询响应时间低于 1ms，且相比逐文件搜索可节省 **99% 的 tokens**。

核心卖点：**单一静态二进制文件**，零依赖，开箱即用。

---

## 二、核心能力

### 2.1 极速索引
- **RAM-first 管道**：LZ4 压缩、内存 SQLite、融合 Aho-Corasick 模式匹配
- 索引完成后释放内存
- Linux 内核 (28M LOC) → 3 分钟

### 2.2 158 种语言支持
- 内置 tree-sitter 语法解析器，编译进二进制
- 混合 LSP 语义类型解析 (Hybrid LSP)：Python、TypeScript/JS/JSX/TSX、PHP、C#、Go、C、C++、Java、Kotlin、Rust

### 2.3 知识图谱
- 函数、类、调用链、HTTP 路由、跨服务链接
- **14 个 MCP 工具**：搜索、追踪、架构分析、影响分析、Cypher 查询、死代码检测、跨服务 HTTP 链接、ADR 管理等

### 2.4 Token 节省
- 5 个结构查询 ≈ 3,400 tokens（vs 逐文件搜索 412,000 tokens，节省 120 倍）
- 一个图查询替代数十次 grep/read 循环

### 2.5 即插即用
- 自动检测 11 种 Agent：Claude Code、Codex CLI、Gemini CLI、Zed、OpenCode、Antigravity、Aider、KiloCode、VS Code、OpenClaw、Kiro
- 自动配置 MCP 条目、指令文件、工具前钩子

### 2.6 内置可视化
- 3D 交互式知识图谱 UI（可选 UI 二进制变体）
- localhost:9749 访问

### 2.7 基础设施即代码索引
- Dockerfiles、Kubernetes manifests、Kustomize overlays 均作为图节点索引
- 带交叉引用的资源节点和模块节点

---

## 三、基准测试

根据预印本论文 [Codebase-Memory: Tree-Sitter-Based Knowledge Graphs for LLM Code Exploration via MCP](https://arxiv.org/abs/2603.27277)：

- 在 31 个真实仓库上的评估
- **83% 回答质量**
- **10× 更少 tokens**
- **2.1× 更少工具调用** vs 逐文件探索

---

## 四、安装与使用

**一行安装（macOS/Linux）：**
```bash
curl -fsSL https://raw.githubusercontent.com/DeusData/codebase-memory-mcp/main/install.sh | bash
```

**Windows (PowerShell)：**
```powershell
Invoke-WebRequest -Uri https://raw.githubusercontent.com/DeusData/codebase-memory-mcp/main/install.ps1 -OutFile install.ps1
.\install.ps1
```

**启动后**：重启 Agent，说"Index this project"即可。

---

## 五、安全特性
- 所有处理 **100% 本地**，代码从不离开机器
- 每个发布二进制均有签名、校验和，经 70+ 杀毒引擎扫描
- SLSA 合规

---

## 六、技术栈与依赖
| 组件 | 说明 |
|------|------|
| 语言 | C（核心引擎） |
| 解析器 | vendored tree-sitter 语法 |
| LSP | 混合 LSP 语义类型解析 |
| 存储 | 内存 SQLite + LZ4 |
| 协议 | MCP (Model Context Protocol) |
| 架构 | 单一静态二进制 |

---

## 七、竞品对比

| 特性 | codebase-memory-mcp | 传统 grep/read | 其他 MCP 代码工具 |
|------|-------------------|---------------|-------------------|
| 索引速度 | 毫秒-分钟级 | N/A（逐文件） | 通常分钟级 |
| 语言支持 | 158 种 | 文本级 | 通常 10-30 种 |
| Token 效率 | 120× 节省 | 基线 | 通常 3-10× |
| 知识图谱 | ✅ 函数/类/调用链 | ❌ | 部分支持 |
| 单二进制部署 | ✅ | ✅ | 通常多文件 |

---

## 八、适用场景
1. **AI Coding Agent 增强** — 让 Claude Code / Codex 等 Agent 快速理解大型代码库
2. **遗留系统考古** — 对老项目快速建立调用关系图
3. **代码评审** — 影响分析、死代码检测
4. **跨服务依赖分析** — HTTP 路由链接、微服务架构映射
5. **CI/CD 流水线** — 作为代码理解基础设施集成

---

## 九、关键发现
1. **Token 效率革命性** — 120× 节省意味着大代码库的 Agent 交互成本可以降低两个数量级
2. **零配置体验** — 单二进制 + 自动 Agent 检测，拉低了代码智能工具的使用门槛
3. **开源论文驱动** — 有正式学术论文背书，非"玩具项目"
4. **2.3K stars/day** — 是今日 GitHub Trending 上增长最快的项目之一，说明社区对 MCP 代码工具的需求极大
