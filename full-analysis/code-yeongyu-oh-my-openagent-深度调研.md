# code-yeongyu/oh-my-openagent 深度调研

> 调研日期：2026-07-27 | 星标：66,620⭐ | 协议：SUL-1.0（自定义） | 语言：TypeScript | 状态：极活跃（pushed 2026-07-26）
> 定位：「编码 Agent 的 oh-my-zsh」—— 把 OpenCode/Codex 武装成 11 Agent 编排团队的一体化 harness 配置

## 项目亮点（差异化）

- 🧩 **「oh-my-zsh 式」Agent harness 封装**：一条 `bunx oh-my-openagent install`，把 11 个 Agent、54+ 生命周期 hook、5 个内置 MCP、Team Mode 全塞进 OpenCode/Codex，用户只打一个 `ultrawork` 就全员开工。
- 👥 **原生 Team Mode 多 Agent 编排**：Lead Agent + 最多 8 个并行成员，tmux 实时可视化，专用于 `hyperplan`（5 个对抗评审）与 `security-research`（3 猎手 + 2 PoC 工程师）。
- 🔗 **Hash-Anchored Edit Tool（哈希锚定编辑）**：用 `LINE#ID` 内容哈希校验每次修改，杜绝「行号漂移导致的陈旧行错误」—— 直接回应学术界「The Harness Problem」。
- 🛠️ **IDE 级精度**：内置 LSP（诊断/跳转/符号/重命名）+ AST-Grep（25 语言模式感知改写），让 Agent 拥有 IDE 般的代码理解力。
- 🤖 **由 AI 自维护**：项目由 AI 助手「Jobdori/Dori」实时公开构建（Discord building-in-public），是「AI 维护开源项目」的极端样本。

## 项目全景

oh-my-openagent（简称 OmO，npm 包名曾为 `oh-my-opencode`）是面向 **OpenCode / Codex CLI** 的编码 Agent harness 增强套件。它的核心主张是：**你不用再手动调 Claude Code / Codex / 各种开源模型的工作流**——OmO 已经帮你测好、留好能真正跑起来的部分。

它发行两个版本：
- **Ultimate（omo for OpenCode）**：完整体 —— 11 个 Agent、54+ hook、5 内置 MCP、全部 slash command、Team Mode、`ultrawork`、`hashline` 编辑。
- **Light（omo for Codex CLI）**：可塞进 Codex 插件系统的便携组件（rules / comment-checker / git-bash / lsp / ultrawork / ulw-loop 等 8 个组件 + 插件级 MCP）。

License 为自定义 **SUL-1.0**（Sisyphus Ultimate License），非标准开源协议，商用需留意。

## 核心架构

Monorepo（bun workspace），`packages/` 下清晰的能力分层：

```
packages/
├─ agents-md-core / omo-config-core   ← Agent 定义与配置核心
├─ delegate-core                       ← 多 Agent 委派/编排
├─ model-core                          ← 多模型路由（11 agent × 多 provider 匹配矩阵）
├─ hashline-core                       ← Hash-Anchored 编辑工具核心
├─ lsp-core / lsp-daemon / lsp-tools-mcp  ← LSP 集成（诊断/跳转/重命名）+ MCP 暴露
├─ ast-grep 相关                       ← 模式感知代码搜索改写
├─ mcp-client-core / mcp-stdio-core / git-bash-mcp  ← MCP 客户端与 Git-Bash MCP
├─ comment-checker-core                ← 评论洁净度检查（拒 AI slop）
├─ claude-code-compat-core             ← Claude Code hook/command/skill/MCP 兼容层
├─ omo-opencode / omo-codex / omo-senpi  ← 各 harness 适配入口
├─ boulder-state / oh-my-opencode-*    ← 状态管理 + 各 OS/arch 预编译二进制
└─ .omo/ (evidence, rules)             ← 规则注入目录（AGENTS.md / .omo/rules/**）
```

**运行时编排模型**：
```
ultrawork (触发)
   └─ Sisyphus (Lead) 编排
        ├─ Hephaestus  (实现)
        ├─ Oracle      (规划/检索)
        ├─ Librarian   (知识/文档)
        └─ Explore     (探索/验证)
   └─ Team Mode: Lead + ≤8 成员并行（tmux 可视化）
   └─ 每次编辑经 hashline 校验 → LSP 诊断回环 → Todo Enforcer 防闲置
```

`AGENTS.md` / `.omo/rules/**` 在每次 prompt 自动注入上下文（Rules Injection）；`Goal`/`ulw-loop` 在 idle 时重注 continuation prompt 直到完成审计通过（Todo Enforcer 防「Agent 摸鱼」）。

## 源码深度解读

三个最具借鉴价值的设计：

1. **Hash-Anchored Edit（`hashline-core`）**：编辑工具不再用「行号」定位，而是 `LINE#ID` + 该行内容哈希。Agent 提交修改时校验哈希，若源行已被改动则拒绝（零陈旧行错误）。这是对「Agent 改代码行号漂移」这一经典痛点的工程解，思路源自 `oh-my-pi`。

2. **分层 harness 适配（`*-core` + `omo-*`）**：纯 TS 核心逻辑（delegate/model/hashline/lsp）与 harness 适配层（opencode/codex/senpi/claude-code-compat）解耦。ROADMAP 明确要把核心逻辑、MCP server、skills、adapter shim 拆成独立层，使同套逻辑跨 harness 复用 —— 这正是它从「OpenCode 专属」走向「多 harness Agent OS」的架构基石。

3. **Discipline Agents + Todo Enforcer**：不是「一个聪明 Agent」，而是「一个 Lead 编排多个专职 Agent + 一个强制收尾机制」。`Todo Enforcer` 在 Agent 闲置时把它拽回任务，配合 `Goal` 持久目标重注，保证「不停止直到做完」—— 直接回应「Agent 容易半途而废」的工程现实。

## 应用场景与启发

- **个人/小团队「AI 开发组」**：用 Team Mode 把大功能拆给 8 个并行 Agent，tmux 实时看板监控。
- **对抗式评审**：`hyperplan` 用 5 个敌对评审、`security-research` 用猎手+PoC 工程师，适合高可靠场景。
- **🔧 给同类需求的启发**：
  - 「**harness 配置即产品**」：与其造新 Agent 运行时，不如把现有 OpenCode/Codex 武装成团队 —— 边际成本低、兼容生态。
  - 「**哈希锚定编辑 + LSP 回环**」应成为任何代码 Agent 的标配，否则大模型改代码必然踩行号漂移坑。
  - 「**Discipline（纪律 Agent + 防闲置）**」比「更聪明的模型」更能决定交付成败。
  - 自定义协议（SUL-1.0）+ 匿名遥测（PostHog，SHA256 机器标识）是「开源但控商业化」的常见取舍。

## 社区口碑

- 66k⭐、极活跃（昨日仍推送），X/Discord 口碑爆棚：有用户称「取消 Cursor 订阅」「把 45k 行 Tauri 应用一夜转 SaaS」「8000 eslint warning 一天清完」。
- 叙事强：「Anthropic 因我们封了 OpenCode」「Claude Code 是座漂亮的监狱」—— 反锁定、多模型编排的立场获得大量共鸣。
- 槽点：自定义协议 SUL-1.0 商用边界模糊；安装涉及多 provider 认证，官方建议「直接让 LLM Agent 帮你装」。

## 竞品对比

| 项目 | 星标 | 差异 |
|------|------|------|
| **oh-my-openagent（本品）** | 66k | OpenCode/Codex 的「团队化 harness 封装」+ hashline + Team Mode |
| github/spec-kit | 120k | Spec-Driven 开发工具包（规范→产物），不同层 |
| ComposioHQ/awesome-claude-skills | 70k | 技能策展清单，非 harness 编排 |
| earendil-works/pi | 72k | 自研终端 Agent 运行时（4 层抽象），更底层 |
| affaan-m/ECC | 226k | Agent Harness 性能优化系统，更偏 benchmark/适配 |
| mattpocock/skills / obra/superpowers | — | 单 Agent 工作流技能方法论 |

> 本品的独特位置是「**在成熟 harness 之上做团队编排与纪律层**」，而非再造运行时或写技能；可与 spec-kit（规范驱动）互补使用。

## 核心研判

- **价值**：把「多 Agent 团队协作 + 防摸鱼 + 哈希锚定编辑 + IDE 级 LSP」打包成开箱即用的 harness 配置，是「编码 Agent 工程化」的高成熟度样本；其分层适配架构正走向「多 harness Agent OS」，前瞻性强。
- **风险**：① 自定义协议 SUL-1.0 商用合规性不清；② 强绑定 OpenCode/Codex 生态，harness 变更需紧跟；③ 11 Agent 编排 token 成本高，依赖多 provider 订阅。
- **趋势**：「harness 配置即产品」「多模型编排对抗单点锁定」是明确方向；未来竞争在「编排智能 × 防错机制（hashline/LSP）× 跨 harness 可移植性」。
- **给开发者启发**：做 Agent 工具，**优先在成熟 harness 上做编排与纪律层**（兼容生态、低边际成本），并把「编辑可靠性（hashline）+ IDE 精度（LSP）」当成一等公民。

## 关键文件速查

- `packages/delegate-core/` —— 多 Agent 委派/编排核心
- `packages/hashline-core/` —— Hash-Anchored 编辑工具（防行号漂移）
- `packages/lsp-core/` `lsp-daemon/` `lsp-tools-mcp/` —— LSP 集成与 MCP 暴露
- `packages/model-core/` —— 多模型路由（11 agent × provider 矩阵）
- `packages/omo-opencode/` `omo-codex/` `omo-senpi/` `claude-code-compat-core/` —— 各 harness 适配层
- `packages/comment-checker-core/` —— 评论洁净度（拒 AI slop）
- `.omo/rules/` + `AGENTS.md` —— 规则注入（每次 prompt 自动加载）
- `ROADMAP.md` —— 多 harness Agent OS 重构计划
