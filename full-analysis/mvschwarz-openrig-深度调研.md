# OpenRig 深度调研

> 仓库：`mvschwarz/openrig` ｜ 语言：TypeScript（monorepo：daemon/cli/tui/ui/test-system）｜ 许可：Apache-2.0 ｜ Stars：≈6.9k（2026-10-11 抓取，weekly Trending）
> 定位一句话：**在本地用 tmux 把 Claude Code / Codex / Pi 等编码 agent 编排成「持久化多 agent 团队」的开源 harness——YAML 定义拓扑，一条命令拉起，带 TUI / MCP / 守护进程。**

---

## 1. 项目亮点（差异化）

1. **多 harness 同队**：Claude Code 与 Codex 在同一个 rig 里被当成一个系统统一管理（也可加 Pi / Oh My Pi）。
2. **RigSpec 声明式拓扑**：YAML 定义 pods / seats / edges / continuity policies / culture，可版本化、可移植。
3. **持久化与可恢复**：`rig down --snapshot` 抓全拓扑，`rig up <name>` 按节点恢复（resumed / fresh-primed / awaiting-decision…）；`rig discover` + `rig adopt` 接管已有 tmux 会话。
4. **三档团队开箱**：`starter`（builder+reviewer）、`workshop`（lead+builder+QA+reviewer）、`factory`（七 agent：lead/advisor/build/QA/design/双 reviewer）。
5. **权限分层治理**：per-seat 权限（`floor`/`full_bypass`/`inherit`）、`typing-guard` 防误输入、**YOLO 默认关闭**；写 provider hooks/trust 前明确提示备份。
6. **完整人机接口**：CLI（87 命令）+ TUI（拓扑图/表）+ MCP server（18 工具，`rig_up`/`rig_ps`/`rig_send`…）三件套。

---

## 2. 核心架构

本地 **daemon(Hono HTTP) + CLI + TUI + MCP server + SQLite + tmux + runtime adapters** 的分层结构。请求路径：

```
rig (CLI)  /  TUI  /  MCP server(stdio)
        └─ HTTP → daemon (默认 :7433)
              ├─ server.ts: createApp() 中间件 + /healthz + app.route("/api/...")
              ├─ routes/    每域一个 Hono router（67 个，65 个建 router）
              ├─ domain/    services / repositories / orchestrators / event-bus
              └─ SQLite(db/)  +  tmux(adapters/tmux.ts)  +  runtime adapters(*-adapter.ts)
```

- **daemon（`packages/daemon`）**：HTTP 路由 + 领域服务 + SQLite 迁移（**94 个迁移文件**）+ 运行时适配器 + 内置 specs/skills/plugins/context-pack。
- **运行时适配器（6 个）**：`claude-code` / `codex` / `pi` / `omp`(继承 pi) / `terminal` / `stub`（测试桩，零模型成本）。
- **包边界**：CLI/TUI 只经 `packages/daemon/package.json` 的 `exports` 子路径（21 个，如 `@openrig/daemon/attention`）引用 daemon 代码，构建时 `rewrite-daemon-imports.mjs` 改写成打包后的 `daemon/dist` 副本。
- **状态**：`$OPENRIG_HOME`（默认 `~/.openrig`）下的 `openrig.sqlite`；SSE 推送活动事件给 TUI。

---

## 3. 应用场景与启发（重点）

- **个人/小团队「agent 团队化」**：把多个编码 agent 当一支有条理的队伍用（lead 协调、builder 实现、reviewer 审查），而非一堆散落终端。
- **给同类需求的解决思路**：
  - 「**声明式拓扑 + tmux 底层**」是务实组合——YAML 定义团队、tmux 保证每个 agent 都是真人可 attach 的会话，崩了能恢复；
  - 「**守护进程 + HTTP + SQLite**」把「agent 协作状态」当成有 schema 的数据来管（94 个迁移即证据），比脚本拼凑可靠；
  - 「**stub runtime + scenario 测试**」让 CI 用零模型成本跑真实 CLI/daemon/tmux 回归，是可复用的多 agent 系统测试范式。

---

## 4. 源码深度解读

权威入口是 `ARCHITECTURE.md`（核对到 commit `c750304f`，每条路径/计数都可重跑验证）。关键约定：

**包拆分与发布边界**（`packages/`）：

| 目录 | 包 | 作用 |
|---|---|---|
| `packages/daemon` | `@openrig/daemon`(私有) | daemon：HTTP、领域服务、迁移、适配器、specs/skills |
| `packages/cli` | `@openrig/cli` | `rig` 命令、MCP server、daemon 启停（唯一发布包） |
| `packages/tui` | `@openrig/tui`(私有) | 终端 UI |
| `packages/ui` | `@openrig/ui` | React Web UI（维护模式） |
| `packages/test-system` | 无 | stub-agent 场景库 + CI 场景 harness |

**运行时适配器接口**（`domain/runtime-adapter.ts`）只需实现 `runtime / listInstalled / project / deliverStartup / launchHarness / checkReady` 六个方法；最小实现是 `adapters/terminal-adapter.ts`。**数据库迁移**走 `db/migrations/<NNN>_<name>.ts` 导出 `Migration`，`migrate()` 按名排序、记录到 `schema_migrations`，已应用的安装永不再跑——长生命周期实例每次启动自动追平。

---

## 5. 全网口碑

- GitHub ≈6.9k stars（2026-10 冲上 **weekly Trending**），作者 mvschwarz，npm 包 `@openrig/cli`；自称「my AI civilization experiments 的开源系统」。
- 文档成熟度高于一般 side project：`ARCHITECTURE.md` / `docs/reference/`（随包发布）/ `docs/as-built/`（逐模块说明，带 `last-verified-against-source` 提交）/ `ROADMAP.md` / `CHANGELOG.md` 齐全；`rig doctor`、`--dry-run`、权限治理、内部 token 泄漏扫描等工程保障到位。

---

## 6. 竞品对比 + 核心研判

| 方案 | 路线 | 差异 |
|---|---|---|
| **OpenRig** | 自托管 + 多 harness 同队 + 持久拓扑 + 真人权限治理 | tmux 底层、YAML 拓扑、SQLite 状态 |
| Claude Managed Agents | 官方托管多 agent | 闭源、绑定 Claude、无本地 tmux 可 attach |
| AutoGen / CrewAI | 应用层多 agent 框架 | 代码内编排，无「团队/会话/恢复」运维层 |
| 手写 tmux+claude 脚本 | 个人自动化 | 无统一拓扑、权限、恢复 |

**核心研判**：OpenRig 精准击中「想把多个 agent 当团队用、又要可恢复/可治理」的痛点，对 agent/MCP 重度用户（如做 agent 工作流的人）是现成 harness。工程成熟度（测试/迁移/权限/文档/泄漏扫描）明显强于一班个人项目，monorepo 与 `exports` 子路径的包边界设计克制。代价与注意点：仅 macOS/Linux + tmux、需 Node 22/24；学习曲线陡；写 provider hooks 与 trust 设置会改本机文件，**官方已明确提示先备份**；Windows 仅 WSL2 且自动化测试尚未覆盖。适合愿意投入、追求「agent 团队化」可控性的进阶用户。

---

## 7. 关键文件路径速查

- `ARCHITECTURE.md` —— 权威架构地图（含可重跑的计数命令）
- `packages/daemon/src/server.ts` —— `createApp()` 中间件与 `/api/*` 挂载
- `packages/daemon/src/domain/` —— services / repositories / orchestrators / event-bus
- `packages/daemon/src/adapters/` —— 6 个 `RuntimeAdapter`（claude-code/codex/pi/omp/terminal/stub）
- `packages/daemon/src/db/migrations/` —— 94 个 SQLite 迁移
- `packages/cli/src/index.ts` —— `createProgram()` 注册 87 个 `rig` 命令
- `packages/cli/src/mcp-server.ts` —— 18 个 MCP 工具
- `packages/test-system/scenarios/*.yaml` —— stub-agent 回归场景库
- `docs/reference/`（随包发布）、`docs/as-built/`（逐模块说明）
