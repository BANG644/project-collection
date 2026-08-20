# Tencent/AI-Infra-Guard — 深度调研

> 调研日期：2026-08-21 ｜ 星标：4,878 ⭐ ｜ 协议：Apache-2.0 ｜ 语言：Python/Go/TypeScript ｜ 趋势：GitHub Trending 日榜 ｜ 团队：腾讯朱雀实验室

## 一、项目定位（一句话）

A.I.G（AI-Infra-Guard）是腾讯朱雀实验室开源的 **AI 红队（Red Teaming）平台**，整合 ClawScan（OpenClaw 安全扫描）、Agent Scan、MCP/Skills 扫描、AI Infra 漏洞扫描（2000+ CVE）、Jailbreak 越狱评估，为 AI 系统提供最全面的安全风险自检。

## 二、项目亮点（差异化）

- **全栈 AI 安全自检**：覆盖 AI 基础设施漏洞（Ollama/ComfyUI/vLLM/n8n 等 100+ 组件、2000+ CVE）、MCP Server、Agent Skills、Agent 工作流、LLM 越狱五大维度，单平台整合。
- **Skills 专用扫描对齐事实标准**：`aig-skill-scan` 对齐 SkillTrustBench T01–T09 九类风险（指令劫持/记忆投毒/远程载荷/权限提升/工具劫持…），Claude Opus 4.6 上 F1=0.9848；可独立 `pip install` 嵌入 CI/CD。
- **企业级可用形态**：多语言（中/英/日/西/德/法/韩/葡/俄）、Web UI（`http://localhost:8088`）、完整 Swagger API、ClawHub Agent 插件（EdgeOne ClawScan / Skill Scanner / AIG Scanner），即插即用到任何 Agent 工作流。
- **学术与实战背书**：Black Hat EU 2025 Arsenal 亮相、19 篇论文引用、朱雀实验室（2019 成立，曾帮 NVIDIA/Google/Microsoft 修复高危漏洞）；v4.5.2 持续高频迭代。

## 三、核心架构（克制呈现）

模块化**插件框架**是架构基石，规则以声明式 YAML 扩展：

```
data/fingerprints/  # AI 组件指纹 YAML（识别 Ollama/ComfyUI 等版本）
data/vuln/          # CVE / GHSA 漏洞扫描规则
data/mcp/           # MCP Server 安全扫描规则
data/eval/          # Jailbreak 越狱评估数据集
skill-scan/  mcp-scan/  agent-scan/   # 各自独立 CLI
cmd/cli/main.go     # Go 后端 → ai-infra-guard 统一 CLI
services/api_checker/  # Python 模型/API 中继检查服务
```

- **后端**：Go（`go build -o ai-infra-guard ./cmd/cli/main.go`）提供统一 CLI 与 API；Python `services/api_checker` 做模型指纹/签名校验/中继黑盒审计。
- **前端**：TypeScript Web 界面，提供一键扫描与实时进度。
- **部署**：`docker-compose.images.yml` 拉预构建镜像；另有 `docker.sh` 一键脚本。
- **独立 CLI**：`aig-skill-scan`、`mcp-scan`、`agent-scan` 可脱离 Web 单独集成进企业流水线。

## 四、应用场景与启发（重点）

- **场景 1 — 企业 AI 上线前安全自检**：在把 vLLM/Ollama 服务暴露内网前，用 AI Infra 扫描指纹匹配 2000+ CVE。
- **场景 2 — MCP/Skills 供应链审计**：对引入的 MCP Server 或 Agent Skills 做源码/远程 URL 双模扫描，识别工具投毒、凭证外泄、命令注入。
- **场景 3 — Agent 工作流红队**：Agent Scan 多智能体自动扫描框架，评估 Dify/Coze 等平台上的 Agent 失控风险。
- **启发**：① "**可插拔 YAML 规则 + 独立 CLI**"的安全扫描范式极易被社区扩展，比把规则硬编码进二进制更可持续；② **SkillTrustBench 九类 taxonomy（T01–T09）** 正在成为 Agent Skills 安全评估的事实标准，任何做 Skills 市场/分发平台的项目都应直接对齐。

## 五、源码解读（核心模块）

来自真实仓库结构与文档：

- `data/fingerprints/` + `data/vuln/`：组件指纹与漏洞规则分离，新增组件只需加 YAML，无需改代码——这是 A.I.G 能快速把漏洞库扩到 2000+ CVE 的工程关键。
- `skill-scan/`、`mcp-scan/`、`agent-scan/` 三个独立子目录各自有独立 CLI，体现"单平台、多可插拔扫描器"的设计，便于单独集成进不同 CI 阶段。
- `cmd/cli/main.go` 是 Go 后端的入口，统一 CLI 形态让 `ai-infra-guard <subcommand>` 成为所有能力的门面。

## 六、全网口碑

- 赞誉：安全圈高度认可（Black Hat 亮相、Trendshift 收录、8 语言文档）；腾讯朱雀实验室的实战 Red Team 积累使其规则质量高于纯学术工具；多语言与 Web/API/Agent 三形态齐备。
- 注意：官方明确**当前无鉴权机制，不应部署在公网**——仅适合企业内部/个人本地使用；Pro 版（aigsec.ai）走邀请码闭源化，社区需关注核心能力是否会向 Pro 倾斜。

## 七、竞品对比 + 核心研判

| 维度 | A.I.G | mcp-scan(Invariant) | PyRIT(Microsoft) | Garak |
|------|-------|---------------------|------------------|-------|
| AI Infra CVE 库 | ✅ 2000+ | ❌ | ❌ | ⚠️ |
| MCP 扫描 | ✅ | ✅ | ❌ | ❌ |
| Skills 扫描 | ✅(T01–T09) | ⚠️ | ❌ | ❌ |
| Agent 工作流 | ✅ | ⚠️ | ✅ | ⚠️ |
| 越狱评估 | ✅ | ❌ | ✅ | ✅ |
| 全栈整合 | ✅ | ❌ | ❌ | ❌ |

**核心研判**：A.I.G 是当前**最全面的 AI 安全红队开源平台之一**，尤其 MCP/Skills 专用扫描 + 2000+ CVE 库是稀缺能力。**强烈推荐安全/合规团队纳入工具链**，用于 AI 系统上线前自检与 MCP/Skills 供应链审计。主要风险是无鉴权不可公网部署、Pro 版闭源化倾向。对做 Agent/Skills 平台的团队，其 SkillTrustBench 九类 taxonomy 是必读的对齐基准。

> 关键文件速查：`data/fingerprints/`、`data/vuln/`、`data/mcp/`、`data/eval/`、`skill-scan/`、`mcp-scan/`、`agent-scan/`、`cmd/cli/main.go`、`services/api_checker/`、`docs/ARCHITECTURE.md`
