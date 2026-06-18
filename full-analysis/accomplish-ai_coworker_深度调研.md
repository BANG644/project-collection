# accomplish-ai/coworker 深度调研

> **调研日期**: 2026-06-19 | **Stars**: ★ Trending | **语言**: TypeScript | **许可**: MIT

## 项目定位

**Coworker 是一个开源的 AI 桌面助手（Desktop Agent）**，在用户本地机器上运行，可自动执行文件管理、文档创建和浏览器任务。用户自带 API Key（OpenAI、Anthropic、Google、xAI 等）或通过 Ollama 运行本地模型。

核心承诺：**你的文件留在你的机器上** — 隐私优先、本地运行、MIT 许可。

## 核心架构

### 技术栈
- **桌面框架**: Electron 或 Tauri（跨平台桌面应用）
- **前端**: 支持 macOS (Apple Silicon + Intel)、Windows 11、Ubuntu (ARM64 + x64)
- **AI 集成**: 支持 15+ 模型提供商

### 支持的模型提供商

| 类别 | 提供商 |
|------|--------|
| 商业 API | Anthropic Claude、OpenAI GPT、Google Gemini、xAI Grok |
| 中国厂商 | DeepSeek、Moonshot Kimi、Z.AI GLM、MiniMax |
| 聚合平台 | OpenRouter、LiteLLM |
| 聚合云 | Amazon Bedrock、Azure Foundry |
| 本地模型 | Ollama、LM Studio |
| 特殊 | Venice.ai |

### 核心功能

| 功能 | 描述 |
|------|------|
| **📁 文件管理** | 按内容或规则排序、重命名、移动文件 |
| **✍️ 文档写作** | 撰写、摘要、重写文档和报告 |
| **🔗 工具连接** | 与 Notion、Google Drive、Dropbox 等连接 |
| **⚙️ 自定义技能** | 定义可重复的工作流，保存为技能 |
| **🛡️ 完全控制** | 用户审批每个操作，可查看日志，随时停止 |

## 安装与使用

```bash
# 开发环境
pnpm install
pnpm dev

# 前置条件: Node.js 20+, pnpm 9+
```

### 使用流程（4 步完成）

1. **安装应用** — 下载对应平台的安装包（DMG/EXE/AppImage/deb）
2. **连接 AI** — 使用自己的 API Key 或登录 ChatGPT（Plus/Pro），无订阅
3. **授权访问** — 选择 AI 可访问的文件夹
4. **开始工作** — 要求它摘要文档、整理文件夹或创建报告，用户审批每个操作

## 社区与口碑

- 来自 accomplish-ai，与之前被星标的 accomplish 项目同团队
- 支持 10+ 语言（中文、日文、韩文、俄文、西班牙文等）
- 活跃的 Discord 社区
- MIT 许可，完全开源可商用
- 多平台支持（Mac/Windows/Linux）

## 竞品对比

| 特性 | Coworker | Screenpipe | Open-Interpreter | AutoGPT |
|------|---------|-----------|-----------------|---------|
| 运行方式 | 桌面应用 | 桌面守护进程 | CLI | CLI/Web |
| 隐私策略 | ✅ 本地运行 | ✅ 本地运行 | ✅ 本地运行 | API 调用 |
| 模型支持 | 15+ 提供商 | 本地+API | 多种 | GPT-4 |
| 文件管理 | ✅ 原生 | ❌ | ✅ 脚本 | ❌ |
| 文档创建 | ✅ 原生 | ❌ | ✅ | ❌ |
| 浏览器自动化 | ✅ | ✅ | ❌ | ❌ |
| 技能系统 | ✅ 自定义 | ❌ | ❌ | ✅ 插件 |
| 用户审批 | ✅ 每个操作 | ❌ | ✅ 可配置 | ❌ |
| 许可 | MIT | MIT | MIT | MIT |
| 跨平台 | ✅ Win/Mac/Linux | ✅ Win/Mac/Linux | ✅ 任意 | ✅ 任意 |

## 核心研判

**价值**: ⭐⭐⭐⭐ (高)
- 隐私优先的本地 AI 桌面代理，满足企业级安全需求
- 模型提供商支持范围极广（15+），灵活性高
- 用户审批机制降低了自动化风险
- 技能系统支持自定义工作流，可扩展性强
- MIT 许可，开源社区友好

**适用场景**:
- 需要本地运行、数据不出机器的企业用户
- 希望用自有 API Key 而非订阅 AI 服务的开发者
- 需要文件管理 + 文档创建 + 浏览器自动化一体化的用户
- 希望自定义 AI 工作流的高级用户

**风险**:
- 与 Screenpipe、Open-Interpreter 等已有桌面 Agent 产品竞争激烈
- 需要用户自带 API Key，对非技术用户门槛较高
- 项目仍在早期（v0.5.17），功能成熟度待验证

## 关键文件路径

- `src/` — 前端源码
- `README.md` — 主文档
- `README.zh-CN.md` — 中文文档

---

*报告由 AI 自动生成，基于 GitHub README、项目文档和社区反馈*
