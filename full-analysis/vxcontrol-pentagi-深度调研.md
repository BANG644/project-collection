# vxcontrol/pentagi — 深度调研

> 调研日期：2026-10-15 ｜ 星标：29,137 ⭐ ｜ 语言：Go（backend）+ React/TypeScript（frontend）｜ 协议：**核心代码 MIT**（另含 `EULA.md` 附加条款，企业版/商业使用需注意）｜ 默认分支：master ｜ 创建：2025 ｜ 厂商：VXControl（迪拜安全工程公司）｜ 标签：Trending 日榜

> ⚠️ **合规边界（必读）**：PentAGI 定位为**授权渗透测试（authorized penetration testing）**工具，README 明确声明"for authorized testing only"。本报告仅做架构/定位/竞品研究，**不提供任何攻击步骤或利用方法**；任何使用必须在你拥有书面授权的目标上进行。

## 1. 项目定位（一句话）
**开源、自托管的自主渗透测试多智能体系统**：用自然语言描述目标与目的，一支专业 AI agent 团队便会规划任务、在隔离 Docker 沙箱内运行 20+ 专业安全工具（nmap、Metasploit、sqlmap 等）、记忆已学知识，并交付一份漏洞报告。

## 2. 项目亮点（差异化，开篇呈现）
- **隔离沙箱执行**：所有操作在隔离 Docker 环境内完成，主机不直接暴露（"Giving agents Docker without giving away the host"）。
- **20+ 专业工具内置**：nmap、Metasploit、sqlmap 等，由 agent 自主编排调用。
- **智能记忆系统**：成功路径与研究结果长期存于 **PostgreSQL + pgvector**；可选 **Graphiti/Neo4j 知识图谱**追踪主机/服务/发现之间的语义关系。
- **团队化专家 agent**：研究/开发/基础设施等专项 agent 的委派系统，配"执行监控 + 智能任务规划"提升小模型可靠性。
- **多 LLM 提供商 + 本地模型**：10+ 云厂商（OpenAI/Anthropic/Gemini/Bedrock/DeepSeek/GLM/Kimi/Qwen/Mistral/xAI）+ OpenRouter/OpenAI 兼容网关 + Ollama/vLLM 本地；并附 vLLM+Qwen3.5-27B-FP8 生产部署指南。
- **完整可观测与 API**：Grafana/Prometheus/Langfuse/Jaeger 监控，REST + GraphQL 双 API（Bearer token），Docker Compose 一键安装（Linux/macOS/Windows）；Enterprise 版含 agent profiles、plugins、MCP servers、实时攻击链视图。
- **外部情报聚合**：Tavily/Firecrawl/SearXNG/Sploitus/Perplexity/DDG/Google CSE 等搜索源 + 内置 scraper 浏览器，用于信息收集。

## 3. 核心架构
**技术栈**：backend = Go（cmd/ · pkg/ · gqlgen 代码生成 GraphQL · sqlc 类型化 SQL · migrations/ · fern/ API 规范）；frontend = React + TypeScript；编排 = Docker Compose 微服务。

```
Core Services:    UI(React+TS) → API(Go+GraphQL) → VectorStore(PostgreSQL+pgvector)
                  → TaskQueue(异步) → Multi-Agent System
Knowledge Graph:  Graphiti API + Neo4j
Monitoring:       Grafana / VictoriaMetrics / Jaeger / Loki / OpenTelemetry
Analytics:        Langfuse / ClickHouse / Redis / MinIO
Security Tools:   Scraper(隔离浏览器) + 20+ PenTest 工具(沙箱执行)
```
- **Agent Supervision（高级 agent 监管）**：执行监控 + 智能任务规划，让小模型也能稳定跑长链路；多 agent 委派生（research/development/infrastructure）。
- **数据流**：pentester →(HTTPS) PentAGI →(测各种协议) target；PentAGI →(HTTPS) LLM / Search；→(HTTPS 上报) Langfuse / Grafana。
- **当前能力边界（README 明示）**：PentAGI 是"自主 + 助手引导"的渗透平台，**不是** CALDERA 式的 Breach-and-Attack-Simulation（BAS）/ 对手模拟产品（无预定义战役/攻击计划）；agent 编写的攻击脚本属"概念性/未来工作"。

## 4. 应用场景与启发
- **授权红队 / 安全研究的"自主助手"**：在自有基础设施上跑授权测试，把信息收集→利用→报告全程 agent 化，契合安全团队提效。
- **与本地 RE/审计工具链的互补**：本仓库已调研 `morluto/rea`（agent 逆向工程）、`NSA/ghidra`（逆向框架）、`perplexityai/bumblebee`（供应链扫描）——PentAGI 补齐"自主多 agent 编排渗透"这一环，构成"侦察/逆向/审计/渗透"的安全工具矩阵。
- **可迁移架构范式**：「隔离沙箱 + 向量记忆 + 知识图谱 + 多 agent 委派 + 完整可观测」这套自托管 agent 编排骨架，对非安全场景的多 agent 系统（如用户的错题归因链路）也有参考价值——尤其"执行监控 + 任务规划护栏小模型"的思路。

## 5. 源码深度解读
backend 的工程化成熟度值得注意：
- `gqlgen/` + `sqlc/`：GraphQL 与 SQL 均经**代码生成 + 类型化**，是生产级而非脚本级实现；`migrations/` 用迁移管理 schema。
- `CLAUDE.md` 存在 → 仓库本身 agent-ready，便于二次开发；`fern/` 维护对外 API 规范。
- 前端 React+TS 提供 Web UI 管理与实时监控；`docker-compose*.yml`（observability / langfuse / graphiti / e2e）表明**可插拔的可观测套件**设计。

> 源码仅做骨架级走读（遵循"代码呈现克制"铁律），不展开任何工具调用/利用逻辑。

## 6. 社区口碑
- 29k⭐、Trendshift 上榜、Discord/Telegram 社区活跃；由专业安全公司 VXControl 背书，更新频繁。
- 风险点：**强双用途（dual-use）**——能力强大，必须严格限定在授权场景；`EULA.md` 对商业/企业使用有附加约束，生产采用前需审条款；非 BAS 产品（边界已自述）。

## 7. 竞品对比 + 核心研判
| 维度 | PentAGI | MITRE CALDERA（BAS/对手模拟） | HackingBuddyGPT | Metasploit（底层工具） |
|---|---|---|---|---|
| 自主多 agent 编排 | ✅ | 部分（原子式） | 单 agent | ❌（非 agent） |
| 自托管 + 隔离沙箱 | ✅ | ✅ | ✅ | ✅ |
| 知识图谱记忆 | ✅ Graphiti/Neo4j | ❌ | ❌ | ❌ |
| 定位 | 自主渗透平台 | 对手模拟/BAS | 红队研究 | 利用框架 |

**研判**：PentAGI 是"自主渗透 agent 编排"赛道的开源代表，工程化（Go+GraphQL+类型化 SQL+完整可观测）程度高于多数同类脚本项目。价值在**授权安全研究的自动化**，但**强双用途属性要求使用者严守授权边界**；作为安全工具矩阵的一环适合持续观察，不建议超出授权范围使用。

## 8. 关键文件路径速查
- `README.md`（架构图 + 能力边界）· `CLAUDE.md`（agent 二次开发指引）
- `backend/`（Go 后端：cmd/ · pkg/ · gqlgen/ · sqlc/ · migrations/）· `frontend/`（React+TS）
- `docker-compose.yml` + `docker-compose-observability.yml` / `-langfuse.yml` / `-graphiti.yml`
- `EULA.md`（商业/企业使用附加条款，必读合规）
- `examples/guides/vllm-qwen35-27b-fp8.md`（本地大模型生产部署指南）
