# multica-ai/multica 深度调研

> 调研日期：2026-08-04 ｜ 调研方式：gh API 元数据 + 真实源码（`server/internal/daemon/poisoned.go`、`server/internal/daemon/execenv/codex_multi_agent.go`、`CLI_AND_DAEMON.md`、`CLAUDE.md`）+ README ｜ 报告类型：修旧账重写（原 6.8KB 薄报告 → 完整 7 维）

## 一、项目定位（一句话）

multica 是一个**自托管式「托管 Agent 平台」**——把 Claude Code / Codex / Copilot 等编码 Agent 变成可分配 Issue、追踪进度、复利沉淀技能的「数字同事」，让小团队靠「人 + Agent 舰队」跑出二十人的吞吐量。

## 二、项目亮点（差异化）

1. **「时间复用（time-sharing）」式 Agent 基建**：命名取自 Multics（1960s 引入多用户时间复用的 OS），隐喻「把系统同时 multiplex 给人类和自主 Agent」。核心抽象是 *Agent × Issue × Task* 三层——每个 Task 天然对应一次 Git 提交，进度可审计、可回放。
2. **毒化会话检测（Poisoned Session）**：服务端在「续跑上一个 Task 的会话」前，主动识别「这段对话已坏、续跑会确定性复现同一失败」的情形，强制下一个 Task 从全新会话开始（见源码解读）。这是长跑多 Agent 稳定性里极少被显性处理的硬骨头。
3. **默认关闭 Codex 原生多智能体**：守护进程向 Codex 的 per-task `config.toml` 注入 `multi_agent = false`，避免「父线程已 `turn/completed` 但子 Agent 还在跑 / 输出没 flush」导致的 premature-completion 丢工作（见源码解读）。
4. **15+ harness 自动适配**：守护进程 `multica daemon start` 后自动探测 PATH 上的编码 CLI（Claude Code / Codex / Copilot / OpenCode / OpenClaw / Gemini / Pi / Cursor / Kimi / Kiro / Qoder / Trae / Grok / Qwen…），每个 CLI 在每个被 watch 的 workspace 注册为一个 runtime——vendor-neutral，不被单一厂商锁定。
5. **完整自托管交付**：Go 后端 + Electron 桌面端 + Next.js Web 端 + Expo 移动端，外加三档自托管文档（`SELF_HOSTING.md` / `_ADVANCED.md` / `_AI.md`），开箱即部署。

## 三、核心架构

multica 是**前后端一体、以本地守护进程（daemon）为调度核心**的平台：

```
┌──────── Web(Next.js) ─────┐   ┌──── Desktop(Electron) ────┐   ┌── CLI(server/cmd) ──┐
└────────────┬──────────────┘   └────────────┬──────────────┘   └─────────┬──────────┘
             └───────────────────────────────┴───────────────────────────┘
                                    │  HTTPS (OAuth 90d token)
                                    ▼
                          ┌──────────────────────────┐
                          │   Multica Server (Go)     │  Chi router · sqlc · gorilla/websocket
                          │   Issue / Agent / Task    │
                          └─────────────┬────────────┘
                                        │  poll 3s / heartbeat 15s
                                        ▼
                          ┌──────────────────────────┐
                          │  multica daemon (本地)    │  探测 harness CLI · 拉起隔离 workspace · 流式回传
                          │  server/internal/daemon   │
                          └─────────────┬────────────┘
                                        │ spawn + 注入 config
                                        ▼
                    ┌────────────────────────────────────┐
                    │  harness 运行时（外部进程）          │
                    │  claude / codex / copilot / …        │
                    └────────────────────────────────────┘
```

- **调度层** `server/internal/daemon/`：维护 Agent 与 harness 的 execenv、决定 Task 是「新会话」还是「续跑上一 Task 会话」、识别毒化会话。
- **execenv 适配层** `server/internal/daemon/execenv/`：每个 harness 一个子包（如 `codex_multi_agent.go`、`codex_sandbox`、`codex_usage_cache` 等），负责注入环境变量与 config。
- **CLI 层** `server/cmd/multica/`：数百个 `cmd_*.go` 子命令（agent / auth / autopilot / chat / config / daemon / attachment / copy…），`multica setup` 一键配置+登录+起守护进程。
- **前端层**：`apps/desktop/`（electron.vite + `worktree-dev-env` 多 worktree 开发）、`apps/web/`（Next 类 Web，Docker 部署）、`apps/mobile/`（Expo/RN）。
- **包边界**（CLAUDE.md 硬约束）：`packages/core`（无 react-dom / localStorage / process.env）、`packages/ui`（仅原子组件）、`packages/views`（业务页面）；依赖方向 `views → core + ui`。状态规则：TanStack Query 管 server state，Zustand 管 client/view state，Workspace 作用域 query key 必须含 `wsId`。
- **语言/许可**：Go 后端 + TypeScript 前端；许可证为 `NOASSERTION`——仓库自带 `LICENSE` 是**自定义 Multica License**（源码可见、带反 SaaS 限制，**非标准 OSI 协议**），自托管/商用需留意条款，不能默认当 MIT/Apache 用。

## 四、应用场景与启发

- **把「编码 Agent」当团队同事用**：研发 leader 给 Agent 开 Issue，Agent 自动认领并提 PR，人在 Issue 评论区 review——这是「AI 同事」工作流最接近落地的形态之一，比纯聊天框更适合真实团队。
- **长跑多 Agent 的稳定性范式**：毒化会话检测 + 默认关 Codex 多智能体，是「让 Agent 连续跑几十个 Task 不雪崩」的关键工程经验。任何做 agentic loop / 多 Agent 编排的人都该借鉴：**会话状态会「中毒」，必须显式检测并重置，而不是无脑续跑**。
- **跨 harness 抽象**：需要同时接 Claude Code / Codex / 自托管模型时，multica 的 execenv 适配层是现成的分层参考。
- **自托管 Agent 中台**：想在公司内搭「内部 Agent 服务平台」，它的三档自托管文档 + Dockerfile 组合可直接抄作业。

## 五、源码深度解读（2 个最具借鉴价值的模块）

### 1. `server/internal/daemon/poisoned.go` — 毒化会话分类器

续跑上一 Task 的会话前，守护进程先判断「这段会话是否已经坏了」。文件把「毒化」分三类，且**刻意宁可漏判也不误判**：

```go
const poisonedOutputMaxLen = 320  // 真实 fallback 只有一句话；长输出即使引用 marker 也当真结论

var poisonedMarkers = []struct {
    Substring string
    Reason    string
}{
    {"i reached the iteration limit", FailureReasonIterationLimit},
    {"put your final update inside the content string", FailureReasonAgentFallbackMsg},
}

func classifyPoisonedOutput(output string) (string, bool) {
    trimmed := strings.TrimSpace(output)
    if trimmed == "" || len(trimmed) > poisonedOutputMaxLen { // 长输出永不判毒化
        return "", false
    }
    lowered := strings.ToLower(trimmed)
    for _, m := range poisonedMarkers {
        if strings.Contains(lowered, m.Substring) {
            return m.Reason, true
        }
    }
    return "", false
}
```

三类毒化来源（注释写得很清楚）：
- **Output-side**：Agent「完成」了，但输出是已知 fallback 终态消息（中途放弃 / 吐了 meta 消息）。
- **Error-side**：LLM API 直接 400 `invalid_request_error`（超大 payload、坏图片）——坏消息已烤进对话历史，每次续跑都撞同一 400。匹配**同时**要求 `"400"` 和 `"invalid_request_error"`，把 429/5xx/工具类错误排除（那些该续跑）。
- **Timeout-side**：Codex 报语义无进展（卡死），续跑会重放卡死态。

> 关键设计哲学：`poisonedOutputMaxLen = 320` + 「长输出永不判毒化」——**宁可漏判（用户手动重试补救），也不要误判（把成功 Task 变成失败 + 系统评论）**。这是生产级 agent loop 极难得的克制。

### 2. `server/internal/daemon/execenv/codex_multi_agent.go` — 默认关 Codex 原生多智能体

Codex 新版本默认开启 `features.multi_agent`，让父线程扇出子 Agent。但 multica 的守护进程**每个 Task 只建模父线程**——父线程 `turn/completed` 就标记 Task 终态，哪怕子 Agent 还在跑、输出没 flush，于是丢工作。解法是用正则注入 config：

```go
const MulticaCodexMultiAgentEnv = "MULTICA_CODEX_MULTI_AGENT"

// 默认关闭；仅当用户显式 MULTICA_CODEX_MULTI_AGENT=1 才保留原生多智能体
func codexMultiAgentEnabled() bool {
    raw := strings.TrimSpace(os.Getenv(MulticaCodexMultiAgentEnv))
    switch strings.ToLower(raw) {
    case "1", "true", "yes", "on":
        return true
    }
    return false
}
```

TOML 注入还要兼容用户已有 `[features]` 表（避免 `table 'features' already exists` 解析失败），所以分「嵌进已有 `[features]`」与「文件根部 dotted-key」两种形态，用 `BEGIN/END multica-managed` 标记包裹以便重生成；且**只改 per-task `CODEX_HOME/config.toml`，绝不碰用户全局 `~/.codex/config.toml`**。

> 借鉴点：**当上游 harness 的生命周期模型与你的 Task 模型不对齐时，不要硬适配，而是用最小侵入的方式「锁死」上游的危险特性**，并用 env 开关把决定权留给用户。

## 六、社区口碑

- 仓库活跃度极高：1,194 open issues、5,524 forks，Issue 模板分 bug/feature 且 PR 模板规范；`docs/` 密度惊人（plans / ideation / RFC / 设计系统 `design.md`），是**产品化导向**而非个人玩具。
- 外部口碑（HN/Reddit）本次未抓取（gh Web/Trending 不可达），数据不可用；但从「托管式 Agent 平台」赛道热度与 Vercel/Anthropic 系 harness 生态扩张看，multica 的 vendor-neutral 定位天然吃到了多 harness 用户的注意力。

## 七、竞品对比 + 核心研判

| 维度 | multica | 纯 harness(OpenCode/Codex) | gstack(garrytan) | 商业 AI 同事(Devin 类) |
|------|---------|------------------------------|------------------|------------------------|
| 定位 | 托管 Agent 平台（调度+审计+自托管） | 单 Agent 运行时 | 多 Agent 工作流编排 | 闭环 AI 工程师（SaaS） |
| 自托管 | ✅ 三档文档 | ✅ | ✅ | ❌ |
| 多 harness | ✅ 15+ 自动探测 | 单一 | 视实现 | 封闭 |
| 会话健壮性 | ✅ 毒化检测 + 默认关多智能体 | 依赖上游 | 依赖上游 | 黑盒 |
| 许可 | 自定义 Multica License（非 OSI） | 各异 | 各异 | 商业 |

**核心研判：**
- **优势**：把「Agent 当同事」的抽象很完整（Issue→Task→Commit 一线贯通），且在「长跑稳定性」上有真实工程沉淀（毒化会话、多智能体生命周期），是多数 agent 框架忽略的硬骨头。
- **风险**：① 许可证 `NOASSERTION`（自定义 Multica License，带反 SaaS 限制），商业自用需法务确认；② 强依赖上游 harness 生命周期语义，上游一变（如 Codex 默认开多智能体）就得跟进 inject，维护面随 harness 数量线性增长；③ 1,194 open issues 说明功能扩张快、债务也在累积。
- **趋势/启发**：「托管式 Agent 平台」正从「CLI wrapper」演进为「带会话治理的企业中台」。multica 的毒化检测范式极可能被后续开源项目抽象成通用库——**下次做多 Agent 长跑，先想清楚「会话什么时候该被丢弃重开」**。

## 八、关键文件速查

| 路径 | 作用 |
|------|------|
| `server/internal/daemon/poisoned.go` | 毒化会话三类检测（output/error/timeout），续跑安全核心 |
| `server/internal/daemon/execenv/codex_multi_agent.go` | 默认关闭 Codex 原生多智能体（TOML 注入 + env 开关） |
| `server/cmd/multica/` | CLI 子命令集合（agent/auth/autopilot/chat/config/daemon…） |
| `server/internal/daemon/` | 守护进程调度核心（Agent/Issue/Task 状态机） |
| `CLI_AND_DAEMON.md` | CLI 安装 / 登录 / 守护进程 / 15+ harness 探测说明 |
| `CLAUDE.md` | 仓库约定（包边界、状态规则、依赖方向） |
| `apps/desktop/` `apps/web/` `apps/mobile/` | Electron / Next.js / Expo 三端 |
| `SELF_HOSTING*.md` | 三档自托管文档 |
| `LICENSE` `NOTICE` `Makefile` | 自定义 Multica License（非 OSI）+ 构建入口 |
| `.agents/skills/` | 复利技能资产目录 |

---
*本地归档：`full-analysis/multica-ai-multica-深度调研.md` ｜ GitHub 远端：`github-project-research-20260614`*
