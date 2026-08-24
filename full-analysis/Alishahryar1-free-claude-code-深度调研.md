# Alishahryar1/free-claude-code 深度调研

> 调研日期：2026-08-25 ｜ 星标：48,778 ⭐ ｜ 语言：Python ｜ 协议：MIT ｜ 默认分支：main ｜ 最后推送：2026-08-24
> 定位：本地代理（proxy），让 9 个编码 Agent 共用 50 个 ToS-friendly 免费模型（每月 1.3B+ 免费 token）

## 一、项目亮点（差异化）

1. **50 提供商 / 1.3B+ 免费 token / 月**：从一个可搜索 UI 使用免费、付费、订阅、本地模型，且不把账户置于风险（FCC 遵循各提供商条款，违规集成会被移除）。
2. **9 个编码 Agent，一套模型目录**：Claude Code、Codex、Pi、OpenCode、Cline、Hermes、DeepSeek Harness、Grok Build、Muse Code 都能指向 FCC 的模型。
3. **跨客户端故障转移**：重试耗尽后自动切到下一个配置模型，**不重启 turn**，跨所有客户端生效。
4. **终端 token 大幅节省**：可选 RTK 过滤常见命令输出 + 5 项 FCC 优化（配额探测/命令前缀检测/标题/建议/文件路径），省最多 90% 终端输出 token。
5. **多端入口 + 语音**：终端/桌面/IDE（VS Code/JetBrains）/手机（Discord/Telegram）+ 本地 Whisper/NVIDIA NIM 语音转写。

## 二、核心架构

FCC 是「本地 FastAPI 代理 + CLI 启动器 + 可选消息桥」三层结构（详见 `ARCHITECTURE.md`）：

- **三个运行时面**：
  1. **HTTP 代理**：FastAPI 暴露 Anthropic-compatible、Responses-compatible、health、model-listing、stop、admin 端点。
  2. **CLI 启动器**：`fcc-claude` / `fcc-codex` / `fcc-pi` 等包装入口，把对应 Agent 会话指向本地代理。
  3. **消息桥（可选）**：Discord / Telegram 适配器把聊天消息变成受管的客户端 CLI 会话。
- **包边界（clean architecture，least-privilege 依赖）**：
  - `api/`：HTTP 适配器（FastAPI app、routes、handlers、model-catalog、错误映射、Admin 端口）
  - `application/`：依赖叶应用层（不可变路由/模型元数据、ModelRouter、ProviderExecutor、consumer-facing `ProviderPort`、请求租约端口）
  - `core/`：provider-neutral 协议逻辑（线格式请求/响应模型、Anthropic↔OpenAI 转换、SSE 构造、失败语义、token 计数）
  - `config/`：设置、provider 元数据、provider ID 目录
  - `cli/`：控制台入口、客户端启动器、进程/会话管理
  - `providers/`：provider 构造、共享 OpenAI-chat provider、专用适配器、重试恢复策略、限流、模型列表
  - `runtime/`：进程组合根（启动/关闭、provider 生成、Admin 运行时、API↔providers↔messaging↔CLI 接线）
  - `messaging/`：可选平台适配器、入站消息处理、树队列、transcript 渲染、持久化、命令、语音
- **请求流**：Client → ProxyAPI → Handlers → Router(`ModelRouter`) → Executor(`ProviderExecutor`) → Lease(`Provider Generation Lease`) → Providers(`ProviderRuntime`) → OpenAIChat / OpenAIResponses / NativeProviders。

## 三、应用场景与启发

- **免费/低成本跑通编码 Agent**：学生、独立开发者、预算敏感团队可用免费 tier 跑 Claude Code/Codex 等，免去订阅费。
- **统一模型治理**：企业/个人把 9 个 Agent 的模型来源收敛到一个目录，便于限流、故障转移、成本观察。
- **架构启发**：
  - 「**协议保留型代理**」是让异构客户端共享受同一后端的优雅范式——FCC 不改造客户端，而是用 FastAPI 同时实现 Anthropic Messages 与 OpenAI Responses 两套线格式，并做双向转换（`core/` 的 Anthropic conversion / OpenAI Responses conversion）。
  - 「**Router → Executor → Lease → Runtime**」的分层把「选哪个模型 / 怎么执行 / 这次生成的租约 / 具体 provider 运行时」职责解耦，重试与故障转移只在 Lease 层发生，调用方无感。
  - 「**least-privilege 依赖**」在 Python 项目里难得：每层只依赖配置与协议中立类型，避免循环依赖，利于测试与替换 provider。
- **伦理提醒**：项目靠各 provider 免费 tier 聚合 token，属 ToS 灰区；生产/商用需审慎评估各 provider 条款与可持续性，勿把「免费」当长期基础设施假设。

## 四、源码深度解读

### 1. 请求流与分层（`ARCHITECTURE.md` + `src/free_claude_code/api/handlers/`）
`api/handlers/messages.py`（Anthropic Messages 处理）与 `api/handlers/responses.py`（OpenAI Responses 处理）是两套线格式的入口；它们把请求交给 `application.ModelRouter` 选路，再经 `ProviderExecutor` 拿到 `Provider Generation Lease`，最终由 `providers/` 里的具体 adapter 执行。`handlers/token_count.py` 与 `optimization_handlers.py` 则承载「省 90% token」的本地优化（配额探测、命令前缀检测等），这些是**不调 provider 即可完成的本地计算**，体现「把能离线做的都离线做」。

### 2. Provider 抽象与恢复（`src/free_claude_code/providers/`）
`providers/` 拥有 provider 构造、共享 OpenAI-chat provider、专用适配器、SDK/HTTP 失败分类、重试恢复策略、限流、模型列表。其设计关键是：把「失败分类」与「重试恢复策略」从 `core/`（协议中立，永不该知道 provider SDK 异常）剥离到 `providers/`，使 `core/` 保持可测试、provider-agnostic。`Lease` 模式让一次生成获得稳定的运行时租约，故障转移在 Lease 边界内透明发生。

### 3. Web 工具与出口治理（`src/free_claude_code/api/web_tools/`）
`web_tools/` 下 `egress.py` / `outbound.py` / `request.py` / `streaming.py` / `parsers.py` / `automatic_search.py` 组成一个受控的 Web 访问层（含自动搜索）。这说明 FCC 不止转发模型流量，还内建了 Agent 常用的联网能力，并以 `egress` 显式命名「出口」——呼应其 README 对「出口是显式决策」的治理态度。

## 五、全网口碑

- **星标与热度**：48k ⭐，MIT，Python 3.14 + uv 工具链，活跃维护（CI 含 tests/validate-bug-report）。
- **定位认知**：社区视其为「免费跑编码 Agent 的网关」，对预算敏感用户吸引力强；AGENTS.md / CLAUDE.md / ARCHITECTURE.md 齐全，工程成熟度高于一般 Trending 玩具。
- **客观短板（社区常见质疑）**：① 依赖各 provider 免费 tier，聚合 token 的可持续性存疑，provider 收紧条款即受影响；② ToS 灰区，规模化/商用有合规风险；③ 作为本地代理增加一层故障面（代理本身可用性）。
- **数据来源**：来自仓库 README、ARCHITECTURE.md、CLAUDE.md 及公开定位；逐条社区长帖口碑本次未抓取，标注为「社区普遍认知」。

## 六、竞品对比 + 核心研判

| 维度 | Free Claude Code | OpenClaw（代理类） | 直接订阅官方 | 本地模型（Ollama） |
|---|---|---|---|---|
| 编码 Agent 覆盖 | 9 个 | 广 | 单厂商 | 视客户端 |
| 免费 token | 1.3B+/月（聚合） | 各异 | 否 | 免费（自跑） |
| 协议保留 | Anthropic+Responses 双线 | 部分 | 原生 | 原生 |
| 故障转移 | 跨客户端 | 部分 | 否 | 否 |
| 风险 | ToS 灰区 | 灰区 | 低 | 低（但需算力） |

**核心研判**：
- ✅ **工程价值明确**： FCC 的「协议保留型本地代理 + 清晰分层 + 本地 token 优化」是高质量实现，对「想统一多家 Agent 模型后端」的用户直接可用，且 MIT 可改。
- ⚠️ **可持续/合规风险是最大变量**：其价值底座（免费 tier 聚合）受 provider 条款摇摆影响，不宜作为生产关键路径的单一依赖。
- 🔮 **趋势**：「模型网关 / LLM router」赛道升温，FCC 的差异化在「agent-native + 协议零改造」；若 provider 免费 tier 收紧，此类项目可能转向更强调 BYOK/本地模型的定位。
- 💡 **启发迁移**：做 LLM 网关类产品时，① 同时实现多套线格式并做双向转换，比要求客户端改造更易推广；② Router/Executor/Lease 分层是处理「多 provider + 故障转移」的稳健范式；③ 把离线可算的优化（token 计数、输出压缩）前置到代理层，能显著降低上游成本。

## 七、关键文件路径速查

| 路径 | 作用 |
|---|---|
| `ARCHITECTURE.md` | 维护者视角的运行时边界与请求流地图 |
| `src/free_claude_code/api/app.py` | FastAPI app 与路由装配 |
| `src/free_claude_code/api/handlers/messages.py` | Anthropic Messages 处理 |
| `src/free_claude_code/api/handlers/responses.py` | OpenAI Responses 处理 |
| `src/free_claude_code/api/model_catalog.py` | 模型目录响应 |
| `src/free_claude_code/application/` | ModelRouter / ProviderExecutor / ProviderPort |
| `src/free_claude_code/core/` | 协议中立转换 / SSE / token 计数 |
| `src/free_claude_code/providers/` | provider 构造 / 重试恢复 / 限流 |
| `src/free_claude_code/runtime/` | 进程组合根 |
| `src/free_claude_code/messaging/` | Discord/Telegram 桥 + 语音 |
| `scripts/install.sh` / `install.ps1` | 跨平台安装器 |
