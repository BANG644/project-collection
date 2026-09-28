# Done-0/fuck-u-code 深度调研

> 调研日期：2026-09-29 ｜ 数据源：gh API（README / 目录树 / package 元数据）｜ 定位：代码"祖传屎山"检测器 + AI 代码审查

## 一、项目定位（一句话）

**fuck-u-code** 是一个用 TypeScript 写的多语言代码质量"毒舌"检测器：用 tree-sitter 做 AST 分析，给代码打 0–100 总分与逐文件"Shit-Gas Index"，并可接 LLM 做 AI 代码审查，输出终端/Markdown/JSON/HTML 报告。

## 二、项目亮点（差异化）

1. **14 种语言全覆盖**：Go / JS / TS / Python / Java / C / C++ / Rust / C# / Lua / PHP / Ruby / Swift / Shell，靠 tree-sitter 统一 AST 解析，而非各语言单独适配。
2. **七维质量检查**：Complexity / Size / Comments / Error handling / Naming / Duplication / Structure，比单一 linter 更"体检式"。
3. **离线优先 + 可选 AI**：代码分析完全本地（"your code never leaves your machine"），AI 审查才需要外部 API 或本地 Ollama——隐私边界清晰。
4. **多模型审查**：OpenAI-compatible / Anthropic / DeepSeek / Gemini / Ollama 通吃，命令行一条 `ai-review` 即可。
5. **既是 CLI 也是 MCP**：`src/mcp` 提供 MCP server，且 `skills/fuck-u-code-analysis` 是现成的 agent skill，可被 Claude Code / Cursor 等直接调用。

## 三、核心架构

- **入口**：`src/index.ts` + `src/cli`（基于命令式 CLI：`analyze` / `ai-review` / `config` / `update` / `uninstall`）。
- **分析管线**：
  - `src/parser` — tree-sitter 多语言 AST 解析，把源码转成语法树。
  - `src/analyzer` — 七维检查器实现，产出 per-file 指标。
  - `src/metrics` — 复杂度/规模等底层度量。
  - `src/scoring` — 把指标聚合成 0–100 总分与"Shit-Gas Index"。
  - `src/config` — `.fuckucoderc.json`（兼容 JSON/YAML/JS/package.json 字段），项目级 + 全局级。
  - `src/i18n` — en/zh/ru/zh_TW 多语言输出。
  - `src/ai` — LLM 审查适配器（provider 抽象）。
  - `src/mcp` — MCP server 暴露分析能力。
- **发布**：npm 包名实际为 `eff-u-code`（README 安装命令 `npm install -g eff-u-code`，与仓库名 `fuck-u-code` 不一致，属历史命名遗留，需注意）。

## 四、应用场景与启发

- **场景**：CI 前本地自检、PR 前代码体检、团队"技术债可视化"、教学演示坏代码长什么样、AI agent 在改动后做质量门禁。
- **启发（对同类需求）**：
  - 想做"代码质量门禁"，本项目的**七维拆分 + 离线 AST + 可选 LLM 增强**是极简可复用的范式，且 `src/analyzer` 按维度独立，扩展新检查只需加一个 analyzer。
  - 它同时提供 CLI + MCP + agent skill 三种形态，正好印证"一个工具多入口分发"的趋势（与 vercel-labs/skills、Remotion skills 同构），值得在用户自己的 skill 体系里借鉴。

## 五、源码深度解读（核心模块）

**1. 解析层 `src/parser`（tree-sitter）**
不使用正则或各语言 SDK，而是统一走 tree-sitter 生成 AST。这是支持 14 语言且保持"离线、零网络"的关键——所有语法分析都在本地完成。

**2. 评分层 `src/scoring` + `src/metrics`**
`metrics` 算原始度量（如圈复杂度、函数长度、重复块），`scoring` 加权聚合成 `Overall Score`(0~100，越高越好) 与逐文件 `Shit-Gas Index`(越高越烂)。加权逻辑集中在 scoring，便于调参。

**3. AI 审查 `src/ai` + `src/mcp`**
`ai` 用 provider 抽象统一 OpenAI/Anthropic/DeepSeek/Gemini/Ollama；`mcp` 把"分析最差 N 个文件"包装成 MCP 工具，让 agent 能主动调用做质量把关——这是它比传统 linter 更"agent-native"的地方。

## 六、社区口碑

- 7.3k⭐、328 fork、24 open issues，星标增长快（pushed 2026-09-07，近期仍有提交）。
- 多语言文档（简中/繁中/俄文 README），国际化做得到位。
- "毒舌 + 幽默"人设传播力强，README 自带 meme 传播力，利于口碑扩散。
- 定位清晰：纯本地分析免费，AI 审查按需接 key，商业友好（MIT）。

## 七、竞品对比 + 核心研判

| 维度 | fuck-u-code | SonarQube | gitleaks/semgrep | 传统 linter |
|---|---|---|---|---|
| 多语言 AST | ✅ 14 种 | ✅(更重) | 部分 | 单语言 |
| 离线 | ✅ | 需服务端 | ✅ | ✅ |
| AI 审查 | ✅ 多模型 | ❌/付费 | ❌ | ❌ |
| MCP/agent | ✅ | ❌ | ❌ | ❌ |
| 上手成本 | 低(npm -g) | 高 | 中 | 低 |

**研判**：在"轻量、本地优先、可当 agent 工具"的代码质量赛道，fuck-u-code 填补了 SonarQube（重、需服务）和单语言 linter（窄）之间的空档。最大短板是**深度不及专业 SAST**（无数据流/污点分析），定位本就是"快速体检 + 趣味性"，不宜当作安全审计工具。整体值得作为"CLI+ MCP+ skill 三位一体"的样板参考。

## 八、关键文件路径速查

- 仓库根：`https://github.com/Done-0/fuck-u-code`
- 入口与分发：`src/index.ts`、`src/cli/`
- 解析/分析：`src/parser/`、`src/analyzer/`、`src/metrics/`、`src/scoring/`
- 配置/国际化：`src/config/`、`src/i18n/`
- AI 与 MCP：`src/ai/`、`src/mcp/`
- Agent skill：`skills/fuck-u-code-analysis/`
- 配置示例：`README.md` 中 `.fuckucoderc.json` 完整字段
- npm 包：`eff-u-code`（注意与仓库名不一致）
