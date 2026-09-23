# yzfly/Awesome-MCP-ZH 深度调研

> 调研日期：2026-09-24 | 星标：7,680⭐ | 语言：null（Markdown 中文策展） | 许可：未声明（内容含外链，作者云中江树） | 默认分支：main | 最近活跃：2026-09-20

## 一、项目定位

**专为中文用户打造的 MCP（Model Context Protocol，模型上下文协议）资源合集**。它不是代码库，而是迄今最系统的中文 MCP 入门到进阶"知识地图"——覆盖 MCP 概念科普、客户端、服务器精选、开发教程、行业动态，适合"想搞懂 MCP 但英文资料门槛高"的国内开发者。

> 关联背景：用户长期在 agent/MCP/skill 生态中工作（WorkBuddy/OpenClaw），本仓库是中文语境下快速补齐 MCP 全景、挑选可用 server 的高效入口。

## 二、项目亮点

1. **中文第一手行业动态**：独家梳理 2025–2026 MCP 关键进展（中立治理移交 Linux 基金会 AAIF、2026-07-28 无状态规范大改、MCP Apps 交互式 UI、各大宿主原生支持），信息密度高于多数英文聚合。
2. **服务器分类极细**：30+ 分类（浏览器自动化、开发执行、CLI、桌面 GUI、Git、数据库、云、搜索、通讯、金融、文件、数据分析、效率、多媒体、社交媒体、电商、知识/RAG、安全、地理、体育游戏、艺术、硬件 IoT 等），每类下罗列具体 server。
3. **客户端 + 开发双覆盖**：不只列 server，还讲客户端（Claude Desktop、Cherry Studio 等）与"如何自己写 MCP server"（含 LLM 辅助构建）。
4. **本土化推荐**：明确建议国内用户用 Cherry Studio + 阿里 Qwen 免费组合，给出 LLM 选型体感排序（Claude4.5 > GPT-5 > Gemini-2.5 > Qwen3-Max > DeepSeek）。
5. **持续活跃**：2026-09 仍在更新，README 达 321KB，是同类中文 MCP 列表中体量最大者之一。

## 三、核心架构：概念 → 客户端 → 服务器 → 玩法 → 开发

```
Awesome-MCP-ZH/
├── MCP 是什么 / 能干什么      # 比喻化科普（"外卖员"梗）
├── MCP 客户端                 # Claude Desktop / Cherry Studio / 等
├── MCP 服务器精选列表（30+ 类）
│   ├── 浏览器自动化 / 开发执行 / CLI / 桌面GUI / Git
│   ├── 数据库 / 云 / 搜索 / 通讯 / 金融 / 文件
│   ├── 数据分析 / 效率 / 多媒体 / 社交媒体 / 电商
│   └── 知识RAG / 安全 / 地理 / 体育游戏 / 艺术 / 硬件IoT
├── MCP 更多玩法（亲测优质 Server）
├── MCP 资源 / MCP Server 开发
└── Star History / 贡献指南 / 许可证
```

## 四、应用场景与启发

1. **MCP 选型速查表**：用户要给 agent 接新能力（如"连数据库""抓网页""管 GitHub"）时，先来这里按分类挑成熟 server，避免重复造轮子。
2. **MCP 入门教材**：概念章节用生活化比喻 + 架构图，适合团队内做 MCP 科普培训材料。
3. **协议演进跟踪**：2026-07-28 无状态化大改（去掉 initialize 握手、引入 MRTR 多轮往返、Mcp-Method 路由、授权加固）直接影响"自建 MCP server 的兼容策略"——做 MCP 开发的人必须关注。
4. **与 Agent Skills 互补认知**：仓库明确指出"MCP 负责连工具与数据，Agent Skills 负责教 agent 怎么做"，这对用户"MCP + Skill 双标准"的工作流是权威佐证。

## 五、源码/内容深度解读

### 1. 2025–2026 关键进展（README 真实摘录）
> - 中立治理：2025-12 Anthropic 将 MCP 捐给 Linux 基金会旗下 Agentic AI Foundation（AAIF，Anthropic/OpenAI/Block 共发起），OpenAI 捐出 AGENTS.md。
> - 2026-07-28 新版规范：核心改为**无状态**请求/响应（去 initialize 握手与 Mcp-Session-Id），引入 MRTR、Mcp-Method/Mcp-Name 头部路由、可缓存 list、授权加固（RFC 9207、CIMD）、正式扩展框架。
> - MCP Apps：server 可返回可交互 UI（表单/可视化），Claude/ChatGPT 等已支持。
> - 普及：Claude Code、ChatGPT & Codex、Gemini CLI、Cursor、VS Code、DeepSeek dsh 全部原生支持；官方 Registry + Glama(19,000+)/mcp.so(16,000+) 收录数万。

### 2. 服务器分类节选（30+ 类，节选 10 类）
```
🌐 浏览器自动化与网页交互
💻 开发与代码执行
🖥️ 命令行与 Shell 交互
🖱️ 桌面与 GUI 自动化
🔄 版本控制 (Git/GitHub/GitLab)
🗄️ 数据库交互
☁️ 云平台与服务集成 (AWS/Cloudflare/Azure/K8s)
🔍 搜索
💬 通讯与协作 (Slack/Email/Calendar)
🧠 知识、记忆与 RAG
```

### 3. 上手建议（README 真实推荐）
```
国内免费体验组合：Cherry Studio（客户端）+ 阿里 Qwen（大模型）
LLM 选型体感：Claude4.5 > GPT-5 > Gemini-2.5 > Qwen3-Max > DeepSeek
```

## 六、全网口碑

- 作者"云中江树"为国内 AI 科普知名作者（微信公众号同号），内容可信度与传播力强，7.7k⭐ 在中文 MCP 垂直领域属头部。
- 被广泛转载于国内技术社区，是许多团队内部 MCP 入门的"指定读物"。
- 局限：体量庞大（321KB）导致单文件阅读负担重；部分 server 链接随生态快速迭代可能失效，需读者自行核验。

## 七、竞品对比与核心研判

| 维度 | Awesome-MCP-ZH | 官方 modelcontextprotocol.io | mcp.so / Glama |
|---|---|---|---|
| 语言 | 中文 | 英文 | 多语言 |
| 定位 | 科普+精选目录 | 规范权威源 | 服务器注册市场 |
| 更新 | 社区维护，较快 | 官方，权威 | 自动聚合，实时 |
| 适合 | 中文入门/选型 | 查规范原文 | 搜具体 server |

**核心研判**：
- ✅ 中文 MCP 入门与选型的"首选地图"，尤其适合做团队培训、快速补齐协议演进认知。
- ⚠️ 是"指向外部 server 的索引"，自身不含代码；具体 server 质量需回原仓核验，且大文件需配合搜索阅读。
- 📌 建议用户：把它作为"MCP 能力黄页 + 协议动态追踪器"定期翻阅，但落地开发时以官方规范（2026-07-28 版）为准，避免被旧教程误导。

## 八、关键文件路径速查

- 仓库根：`https://github.com/yzfly/Awesome-MCP-ZH`
- 官方规范（2026-07-28）：`https://modelcontextprotocol.io/specification/2026-07-28`
- 官方博客：`https://blog.modelcontextprotocol.io/posts/2026-07-28/`
- 服务器市场：mcp.so（16,000+）、Glama（19,000+）、官方 Registry
- Agent Skills 标准：`https://agentskills.io/`

> 数据来源：gh API 仓库元数据 + README 全文（30+ 分类目录、2025–2026 进展、客户端/开发章节、选型建议）。超出 README 部分为架构抽象、竞品研判与应用启发。
