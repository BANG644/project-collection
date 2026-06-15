# 🧠 supermemoryai/supermemory — 深度调研报告

> **调研时间**: 2026-06-15  
> **仓库**: [supermemoryai/supermemory](https://github.com/supermemoryai/supermemory)  
> **Stars**: 15,000+（2026-06）  
> **状态**: 活跃开发，v3.x，有 NPM 包和 Python 包  
> **定位**: AI 记忆与上下文引擎  

---

## 一、项目定位

Supermemory 是**为 AI 设计的记忆与上下文层**，在 LongMemEval、LoCoMo、ConvoMem 三大 AI 记忆基准上均位列第一。它的核心使命是解决 AI 的"对话间遗忘"问题：你上次和 AI 聊过的偏好、项目细节、工作上下文，下一次对话时全部丢失。

### 与同类产品的差异

| 维度 | Supermemory | mem0 | Letta | 传统 RAG |
|------|------------|------|-------|---------|
| 自动事实提取 | ✅ 自动 | 半自动 | 手动 | ❌ |
| 时态管理 | ✅ 支持 | ❌ | ✅ | ❌ |
| 冲突解决 | ✅ | ❌ | ❌ | ❌ |
| 自动遗忘 | ✅ | ❌ | ✅ | ❌ |
| 用户画像 | ✅ 自动生成 | ❌ | ❌ | ❌ |
| 基准第一 | ✅ 3项 | ❌ | ❌ | ❌ |

---

## 二、核心功能

### 🧠 记忆引擎
- **自动事实提取**：从对话中自动抽取事实（name、preferences、project context 等）
- **时态管理**：处理时间维度——信息会过时、会变化、会冲突
- **自动遗忘**：过期信息自动淘汰，不给上下文"塞垃圾"
- **冲突解决**：当新信息和旧信息矛盾时，智能判断哪个更可信

### 👤 用户画像
- 自动维护每个用户的上下文（稳定事实 + 近期动态）
- 一次 API 调用，约 50ms 返回
- 按 project（容器标签）隔离，工作/生活/客户/仓库各自独立

### 🔍 混合检索
- 单次查询同时跑 RAG + 记忆检索
- 知识库文档与个性化上下文一起返回
- 不需要用户手动区分"这是知识库问题还是记忆问题"

### 🔌 连接器
- Google Drive、Gmail、Notion、OneDrive、GitHub
- 实时 webhook 自动同步
- 文件变动后自动更新索引

### 📄 多模态抽取
- **PDF**：内容解析与结构化抽取
- **图片**：OCR 文字识别
- **视频**：语音转录
- **代码**：AST 感知的切分（比纯按行切分更准确）

---

## 三、部署方式

### 云端（SaaS）
- 免费版：[app.supermemory.ai](https://app.supermemory.ai)
- 开发者 API：一行代码即可接入
- 控制台：[console.supermemory.ai](https://console.supermemory.ai)

### 本地部署
```bash
curl -fsSL https://supermemory.ai/install | bash
```
一条命令，零配置。支持任何模型，完全离线 + Ollama。

### 包管理安装
- NPM: `npm install supermemory`
- PyPI: `pip install supermemory`

---

## 四、MCP 集成

提供 MCP 服务器，三个核心工具：

| 工具 | 功能 | 触发方式 |
|------|------|---------|
| `memory` | 保存或删除信息 | AI 自动调用 |
| `recall` | 按查询检索记忆 | AI 自动调用 |
| `context` | 注入完整用户画像 | `/context` 命令 |

安装：`npx -y install-mcp@latest https://mcp.supermemory.ai/mcp --client claude --oauth=yes`

### 已支持的 Agent 插件
- **Claude Code** → [claude-supermemory](https://github.com/supermemoryai/claude-supermemory)
- **OpenCode** → [opencode-supermemory](https://github.com/supermemoryai/opencode-supermemory)
- **OpenClaw** → [openclaw-supermemory](https://github.com/supermemoryai/openclaw-supermemory)
- **Hermes Agent** → 内置 Supermemory 作为记忆 provider

---

## 五、架构分析

从产品层面可以归纳为四层架构：

```
应用层：插件 + MCP + Web App
    ↓
API 层：memory / recall / context + 管理 API
    ↓
引擎层：事实提取 → 时态管理 → 冲突解决 → 自动遗忘 → 混合检索
    ↓
存储层：统一记忆结构 + 向量索引 + 关系本体
```

**关键设计决策**：
1. 统一记忆结构：所有类型的信息（事实、偏好、文档、活动）都收敛到同一个模式和本体，而不是分散在多个不通用的存储中
2. 自动优于手动：agent 不应等待用户手动"保存记忆"，而应在对话中自动提取
3. 基准驱动开发：持续在三个公开基准上验证，不做无基准的功能迭代

---

## 六、仓库质量评估

| 维度 | 评分 | 说明 |
|------|------|------|
| 技术深度 | ⭐⭐⭐⭐⭐ | 三大基准第一，有完整论文级工作 |
| 产品完整性 | ⭐⭐⭐⭐⭐ | App + API + 插件 + MCP + 本地部署全覆盖 |
| 文档质量 | ⭐⭐⭐⭐⭐ | 中英双语，快速开始到深度部署都有 |
| 开源生态 | ⭐⭐⭐⭐ | 有专属插件仓库，但外围生态仍在增长 |
| 可接入性 | ⭐⭐⭐⭐⭐ | 5 行代码接 API，一条命令本地部署 |

---

## 七、适用场景

1. **个人 AI 记忆**：给 Claude Code / Cursor 装上持久记忆，告别每次重新介绍自己
2. **Agent 记忆层**：作为 OpenClaw/Hermes 等 Agent 的长期记忆 provider
3. **企业知识管理**：通过连接器自动同步 Google Drive/GitHub，构建团队"大脑"
4. **应用开发**：通过 API 给自己的 AI 应用加上记忆能力，无需自建向量数据库

---

*报告基于 GitHub README、官方文档及基准论文综合整理。*
