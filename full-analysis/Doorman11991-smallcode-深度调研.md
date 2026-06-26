# SmallCode 全方位深度调研报告

> **仓库**: [Doorman11991/smallcode](https://github.com/Doorman11991/smallcode)
> **调研日期**: 2026-06-17
> **分类**: AI Coding Agent / 本地 LLM 工具

---

## 1. 项目定位

SmallCode 是一个**面向小型本地 LLM（8B-35B 参数）的终端编码代理**。它从零开始设计，专门解决小型模型在编码场景下的痛点——有限的上下文窗口、不可靠的工具调用、易丢失长程状态——而非像 OpenCode 那样假设用户使用 Claude/GPT-5 等前沿模型。

**一句话定位**：让 8B-35B 的本地模型也能干出有用的编码活。

**目标用户**：
- 使用消费级显卡（RTX 3090/4090，24GB 显存）运行本地模型的开发者
- 隐私敏感、不愿将代码发送到云端的用户
- 需要离线开发环境的场景

**推荐模型规模**：8B-35B 参数。≤4B 太小，多步工具调用困难；>35B 不需要 SmallCode 的适配。

---

## 2. 核心架构

```
bin/
├── smallcode.js       入口 + agent loop + TUI 编排 (1570 行)
├── config.js          配置加载、端点检测、认证头
├── executor.js        18 个工具的执行器
└── ...                其他模块
```

### 架构亮点

| 特性 | 说明 |
|------|------|
| **预算管理上下文** | 不倾倒全部上下文，而是按预算管理，自动摘要历史 |
| **宽容多格式解析器** | 不假设可靠的 JSON 工具调用，支持多种输入格式 |
| **TODO 文件分解** | 将任务分解为 TODO 文件的逐步步骤，而非一次性规划 |
| **搜索-替换补丁** | 使用搜索替换方式编辑文件，而非全文件写入 |
| **完全本地** | 无需联网，全部在本地运行 |

### 与 OpenCode 对比

| 维度 | OpenCode | SmallCode |
|------|----------|-----------|
| 目标模型 | Claude, GPT-5 等前沿模型 | 8B-35B 本地模型 |
| 上下文策略 | 全量倾倒 | 预算管理 + 摘要 |
| 工具调用 | 假设可靠 JSON | 宽容多格式解析 |
| 规划策略 | 一次性规划 | TODO 文件逐步分解 |
| 编辑方式 | 全文件写入 | 搜索替换补丁 |
| 隐私 | API 调用上云 | 完全本地无需网络 |

---

## 3. 关键特性

- **终端 TUI**：全屏终端 UI，支持原始模式、鼠标追踪、粘贴括号
- **RAG 引擎**：内置本地 GitHub RAG 数据库，使用 Python 爬虫/索引器
- **FTS5 记忆搜索**：基于 SQLite FTS5 的本地记忆搜索（有 JSON 回退）
- **模型分级路由**：可配置多个模型端点，日常用本地模型，复杂任务自动升级到更强模型
- **预构建二进制**：发布时编译 tarball，无需 Node.js 环境即可运行

---

## 4. 安装与使用

```bash
# npm 全局安装
npm install -g smallcode

# 直接运行
npx smallcode

# 在项目目录启动
cd my-project
smallcode

# 一键安装脚本（无需 Node.js）
bash <(curl -fsSL https://raw.githubusercontent.com/Doorman11991/smallcode/master/install.sh)
```

**配置示例**（`.env`）：

```bash
# 必需
SMALLCODE_MODEL=qwen3:8b
SMALLCODE_BASE_URL=http://localhost:11434/v1

# 可选：故障时自动升级到云端
SMALLCODE_MODEL_STRONG=openai/gpt-4o-mini
SMALLCODE_BASE_URL_STRONG=https://openrouter.ai/api/v1
```

---

## 5. 社区口碑

- **GitHub Stars**: 增长中，定位填补了小型模型编码工具的空白
- **活跃维护**：定期更新，Issue 响应积极
- **BoneScript** 和 **budget-aware-mcp** 作为依赖一并安装
- 社区反馈积极，特别是对运行 Qwen、Llama 等本地模型的用户

---

## 6. 竞品对比

| 工具 | 目标模型 | 本地支持 | 隐私 | 适用场景 |
|------|---------|---------|------|---------|
| **SmallCode** | 8B-35B 本地模型 | ✅ 完全本地 | ✅ 最高 | 消费级显卡本地开发 |
| **OpenCode** | Claude/GPT-5 | ❌ 依赖云 API | ❌ | 前沿模型编码 |
| **Codex CLI** | GPT-5 | ❌ 依赖云 API | ❌ | 微软生态编码 |
| **Claude Code** | Claude 系列 | ❌ 依赖云 API | ❌ | Anthropic 生态 |
| **Continue.dev** | 各种模型 | ✅ 部分 | ⚠️ | IDE 插件形式 |

---

## 7. 核心研判

**优势**：
- 精准定位了小型本地模型编码工具的空白市场
- 架构设计针对小型模型的局限做了系统性的补偿
- 完全本地运行，隐私最佳
- 支持模型分级路由，灵活性强

**劣势**：
- 需要 Node.js 18+ 环境（虽然有预构建二进制）
- RAG 功能依赖 Python 3 + Git
- 小型模型的能力天花板仍然存在

**适用场景**：
- 隐私敏感的代码开发
- 离线环境开发
- 消费级硬件上的 AI 辅助编程
- 学习和实验本地 AI 编码能力

---

## 8. 关键文件路径

| 文件 | 说明 |
|------|------|
| `bin/smallcode.js` | 主入口与 agent 循环 |
| `bin/config.js` | 配置加载模块 |
| `bin/executor.js` | 工具执行器 |
| `docs/rag-harness.md` | RAG 使用文档 |
| `install.sh` | Linux/macOS 一键安装 |
| `install.ps1` | Windows 一键安装 |
