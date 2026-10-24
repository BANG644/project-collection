# makecindy/cindy 深度调研

> 调研日期：2026-10-25 ｜ Stars：3,978 ｜ 语言：TypeScript ｜ 许可：Apache-2.0 ｜ 创建：2026-07-22 ｜ 默认分支：main ｜ 定位：开箱即用的开源 AI Agent 客户端（桌面+移动）

## 一、项目定位（一句话）

makecindy 出品的**「开箱即用」开源 AI Agent 客户端**——把 Claude Code / Codex 等多 harness、多模型、多工具统一到一个能在你电脑上真正干活的本地 agent；仓库是 pnpm monorepo 的客户端（Electron 桌面 + Expo 移动 + 共享 packages），后端在独立仓。

## 二、项目亮点（差异化，开篇呈现）

1. **harness × model 自由混用、可中途切换**：Claude Code / Codex 等 harness 与模型自由组合，任务进行中可换组合，而工作区、记忆、技能、工具保持连续；一个任务可由不同 harness×模型分别"规划 / 执行 / 复核"。
2. **开箱即用 + 可被塑造**：首次启动即可干活；记忆跨 harness 共享、技能可复用并团队分发、定时自动化、MCP 接入内部系统、插件市场（建设中）——" ready out of the box, never boxed in"。
3. **Orca 多 Agent 编排**：内置多 agent 协作（见 `docs/dev-rules/orca-team-architecture.md`），可把任务拆给一组 agent 并行/复核。
4. **工程宪法级 `AGENTS.md`**：根 `AGENTS.md` 是一份"按模块进入"的规则正本，约束 DCO 强制签名、双模式 UI（Light/Dark 必须都实现）、插件兼容红线、Pi 原生非退化红线、日志脱敏不变量——对"AI agent 协作开发大型客户端"是难得的纪律样本。
5. **多端 + IM 入口**：桌面/移动/手机远控，能从 IM 与定时任务接活，驱动浏览器/电脑/手机。

## 三、核心架构（克制代码量）

pnpm monorepo，按"客户端只管桌面/移动及其共享包、后端独立仓"切分：

- **`apps/desktop`**：Electron 桌面客户端（main / renderer / preload / DB / IM hook）。
- **`apps/mobile`**：Expo / React Native 移动端。
- **`packages/*`**：共享能力——`auth`、`device-link`（跨电脑远控）、`maker-core`（**Agent 编排 / prompt / 工具 / translator / 用量**）、model providers 等。
- **`apps/*-bin`**：随桌面发布的工具二进制（claude-code / codex / ripgrep 由 `pnpm install` 按平台下载，Android platform-tools 校验 sha256）。

`AGENTS.md` 的"按模块进入"表把改动范围映射到规则入口与架构正本（desktop / mobile / maker-core 各有专属 `AGENTS.md`），并在触碰系统提示词、更新器、协议兼容、权限边界、用户数据前强制先读专项规则——把"风险入口"前置成硬约束。

## 四、应用场景与启发（重点）

- **「普通人也能用的 agent 客户端」范式**：把多 harness 抽象成统一层、记忆/技能跨 harness 连续，降低了"想用 agent 但不想折腾环境"的门槛；与用户关注的 WorkBuddy 多专家/多 agent 协作方向同构。
- **对 agent 产品工程的借鉴**：`AGENTS.md` 的"插件兼容红线（升级后已装插件必须照旧可用，绝不要求重装/重确认）""Pi 原生非退化红线（Cindy 不得比同版本原生 Pi 更难用）""日志脱敏三条不变量"——都是"agent 系统做产品化时最容易踩的坑"，可直接迁移到任何 agent 客户端/插件平台的设计评审清单。
- **对用户的借鉴**：用户在搭论文伴读/错题归因等 agent，cindy 的"harness 抽象 + 记忆连续 + 定时自动化 + MCP 接入"是可复用的产品化思路；但其"后端独立且未开源"是自建时的边界考量。

## 五、源码深度解读（2 个核心模块）

**1. 根 `AGENTS.md` —— 模块入口与红线（节选）**

> 修改插件基座（运行时/沙箱/批准状态/能力 slot/ manifest 契约…）的 PR 一律走白名单确认门，需放行人明确 Approve 才能合并，不看 diff 大小。
> **存量插件兼容是红线**：用户升级后什么都不做，已装、已批准、已启用的插件必须照旧可用——漏迁移 = P0。
> **Pi 原生能力非退化是红线**：Cindy 不得以静态分析/宿主审批/安全增强为由，让 Cindy Pi 比同版本原生 Pi 更难用；显式用户命令即授权。

把"用户已存状态不可因升级而丢失""上游能力不可因包装而退化"写成不可协商的红线，是长周期 agent 产品最该学的纪律。

**2. `packages/maker-core`（Agent 编排正本）**

`packages/maker-core/AGENTS.md` 是 agent 行为正本，`docs/dev-rules/maker-core-and-agent-behavior.md` 管"任何进入模型 system 段的提示词"——即所有模块的 system prompt 改动都先读这份规则。结合 `docs/dev-rules/orca-team-architecture.md`（Orca 多 agent 协作），编排与提示词治理被显式分离并各有正本。

## 六、全网口碑

相对年轻（2026-07 创建）、3.9k stars，产品完成度高（桌面/移动/IM/定时/技能/MCP 一应俱全），文档与 `AGENTS.md` 工程水位突出。主要讨论点：① 官方客户端**默认连接 Cindy 云端服务**（endpoint 在 `config/endpoint.json` 与 `endpoint.global.json`，auto-update 走官方 CDN）；② 官方发行版含 TapDB 用量分析（README 说明：聊天/文件/工作区内容**不采集**，仅设备/OS/版本元数据，且从源码构建可剥离）。自托管后端未开源，是隐私/可控性上的核心权衡点。

## 七、竞品对比 + 核心研判

| 维度 | cindy | stablyai/orca（多 agent fleet） | Claude Code / Codex | opencode |
|---|---|---|---|---|
| 形态 | 开箱即用客户端（桌+移） | 多 agent 调度台 | 单 harness CLI | 开源 coding agent |
| harness 抽象 | 多 harness 统一层 | 多 coding agent | 单一 | 单一/可换核 |
| 记忆/技能 | 跨 harness 连续 | 舰队级 | harness 内 | harness 内 |
| 后端 | 官方云（独立仓，未开源） | 桌面/移动/远端 | 厂商 | 本地 |

**核心研判**：差异点在"开箱即用的统一 agent 客户端 + 多 harness 抽象 + 跨 harness 记忆/技能连续"，对"想让普通人用上 agent"是务实的产品化样本，工程纪律（AGENTS.md 红线体系）尤值借鉴。限制：① 后端独立且未开源，强依赖官方云；② 官方版含遥测（可剥离）；③ 年轻项目，生态/稳定性待观察。适合作为"agent 客户端产品化"的参考架构，而非可直接自托管的 agent 内核。

## 八、关键文件路径速查

- 工程宪法：`AGENTS.md`（根）· `apps/desktop/AGENTS.md` · `apps/mobile/AGENTS.md` · `packages/maker-core/AGENTS.md`
- Agent 行为正本：`docs/dev-rules/maker-core-and-agent-behavior.md` · `docs/dev-rules/orca-team-architecture.md`
- monorepo 清单：根 `package.json`（pnpm workspaces，`apps/*` + `packages/*`）
- 客户端入口：`apps/desktop/`（Electron）· `apps/mobile/`（Expo/RN）
- Agent 编排：`packages/maker-core/`（编排/prompt/工具/translator/用量）
- 端点与区域：`config/endpoint.json` · `config/endpoint.global.json` · `docs/product-rules/region-and-editions.md`
- 隐私/遥测：`README.md`（TapDB 剥离说明）· `apps/desktop/src/renderer/analytics/`
