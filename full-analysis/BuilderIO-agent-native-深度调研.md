# 🔬 BuilderIO/agent-native — 全方位深度调研

> 调研日期：2026-08-07 ｜ 仓库：https://github.com/BuilderIO/agent-native
> 本次为**重写升级**（原报告文件名异常 `github.com-BuilderIO-深度调研.md`，星标笼统写作「4K+」、许可证误标 MIT、缺口碑/竞品/研判/源码四大维度）

---

## 📌 一句话定位

**用一条 `defineAction` 把同一份业务能力同时暴露给 UI、Agent、HTTP、MCP、A2A、CLI 六个调用面的全栈框架**——它主张的不是「给应用加个 AI 侧边栏」，而是「Agent 与人类界面是同一个产品的两张脸，共享同一套 action、同一份数据库状态」。

---

## ⭐ 项目亮点（差异化，README 之外）

1. **单一 Action → 六种调用面**：`defineAction({ schema, run })` 定义一次，框架自动派生 UI 绑定、Agent tool call、HTTP endpoint、MCP tool、A2A skill、CLI 子命令。这是它区别于 LangChain/Vercel AI SDK 的根本抽象。
2. **A2A 协议是一等公民而非贴片**：`packages/core/src/a2a/` 有 **13 个独立模块 + 逐一配套 `.spec.ts`**（agent-card / auth-policy / caller-auth / correlation / task-store / artifact-response…），说明 Agent 间调用的认证、任务生命周期、产物回传都被当作核心工程问题处理，而非 demo。
3. **21 个 workspace 包的重型 monorepo**：不只是库，而是「框架 + 桌面壳 + 移动壳 + VSCode 扩展 + 两套浏览器扩展 + 调度 + 嵌入 + 迁移工具」的完整产品套件。
4. **发版节奏近乎工业级流水线**：`@agent-native/skills` 已到 **0.2.490**，`clips` 模板到 **v0.1.261**——同一天（2026-08-06）多个包连发，这是 CI 自动切版而非人肉发版。
5. **⚠️ 根目录无 LICENSE 文件**：`gh api` 返回 `license: null`，仓库树中也无根级 LICENSE。**旧报告标注的「MIT」是错误的**，这是采用前必须解决的合规风险。

---

## 🏗️ 项目全景

| 维度 | 数据（2026-08-07 实时核验） |
|------|------|
| 仓库 | BuilderIO/agent-native |
| Stars | **4,431** ⭐（旧报告「4K+」，实测已过 4.4k） |
| Forks | 422 |
| 主语言 | TypeScript |
| 许可证 | **null（根目录无 LICENSE 文件）** ⚠️ |
| 创建 | 2026-03-12 |
| 最近推送 | 2026-08-06（本调研前一天，高频活跃） |
| Open Issues | 35 |
| 默认分支 | `main` |
| 仓库文件数 | **15,556** 个 blob（超大型 monorepo） |
| 包管理 | pnpm workspace（`pnpm-workspace.yaml`） |

### 顶层目录形态

```
apps/  packages/  skills/  registry/  examples/  bridge/  docs/  plans/  scripts/
AGENTS.md  CLAUDE.md  PRODUCT.md  DEVELOPMENT.md  agent-native.json  registry.json
.agents/ .claude/ .claude-plugin/ .codex/ .gemini/     ← 四家 Agent 客户端配置并存
```

**值得注意的信号**：`.claude/`、`.codex/`、`.gemini/`、`.agents/` 四套 Agent 配置目录同时存在，说明这个仓库自己就是被 AI Agent 大规模改写的产物（贡献者榜单印证：`builder-io-integration[bot]` 802 次提交、`builderio-bot` 255 次，机器人合计约占前六名贡献量的 30%）。

---

## 🧠 核心架构

### 21 个 workspace 包的职责切分

| 包 | 职责 |
|----|------|
| `core` | Action/A2A/adapters 核心运行时（本体） |
| `dispatch` | 调用分发（把一个 action 路由到六种 surface） |
| `toolkit` | 协作/分享/设置/团队/可观测性的可复用积木 |
| `skills` | Agent 技能包（独立发版，已到 0.2.490） |
| `frame` / `embedding` | 应用嵌入与框架宿主 |
| `desktop-app` / `mobile-app` | Electron 桌面壳 / 移动壳（`eas.json` 表明 Expo EAS 构建） |
| `vscode-extension` | 编辑器内嵌入口 |
| `agent-browser-extension` / `agent-chrome-extension` / `browser-control-extension-core` | **三个浏览器控制包**——Agent 操作真实浏览器的能力层 |
| `scheduling` | 定时/后台任务 |
| `pinpoint` / `recap-cli` / `creative-context` / `code-agents-ui` / `migrate` / `docs` / `shared-app-config` | 周边工具链 |

### Action 抽象（README 官方示例）

```ts
// One action powers every app surface: UI, agent, HTTP, MCP, A2A, and CLI.
export default defineAction({
  schema: z.object({ emailId: z.string(), body: z.string() }),
  run: async ({ emailId, body }) => {
    await db.insert(replies).values({ emailId, body });
  },
});
```

关键在于 **schema 即契约**：Zod schema 同时充当 UI 表单校验、Agent tool 的 JSON Schema、HTTP 请求体校验、MCP tool 定义、CLI 参数解析。一处定义，六处生效——这才是「Agent UI parity」能落地的工程前提。

### A2A 子系统（`packages/core/src/a2a/`，13 模块）

```
agent-card.ts        # 对外声明本 Agent 能力（A2A 规范的 Agent Card）
auth-policy.ts       # 谁能调用哪个 skill
caller-auth.ts       # 调用方身份验证
correlation.ts       # 跨 Agent 调用链路追踪
task-store.ts        # 任务持久化（+ task-store-lifecycle.spec.ts 单独测生命周期）
artifact-response.ts # 产物回传
invoke.ts / client.ts / server.ts / handlers.ts / activity.ts / response-text.ts / types.ts
```

**架构判断**：把 `auth-policy` + `caller-auth` + `correlation` 三件事拆成独立模块并逐一写 spec，是准备迎接「多个组织的 Agent 互相调用」场景的做法。多数同类框架此处只有一个 `a2a.ts`。

### 自带 8 个内建 Skill

`skills/` 下：`assets` `content` `context-xray` `design-exploration` `visual-edit` `visual-plans` `visual-recap` `visualize-repo`

其中 `context-xray`（上下文透视）和 `visualize-repo`（仓库可视化）是**为「Agent 理解自己所在的应用」服务的元技能**——这解释了框架的另一层野心：应用不只是被 Agent 操作，还要能被 Agent 读懂并自我改写。

---

## 💡 应用场景与启发

### 什么时候该去翻这个仓库

| 你遇到的问题 | 去 agent-native 找什么 |
|---|---|
| 「我的 SaaS 要加 AI，但不想做成孤岛聊天框」 | 整套 Action-parity 范式；`packages/dispatch` 的多 surface 路由实现 |
| 「要给产品同时出 MCP server 和 REST API，不想写两遍」 | `defineAction` + `adapters/` 的适配器模式 |
| 「Agent 之间要互相调用，认证和任务追踪怎么做」 | `packages/core/src/a2a/` 的 13 模块拆分是现成蓝本（哪怕不用这框架，照抄模块边界也值） |
| 「想让 Agent 直接操作浏览器」 | 三个 browser-extension 包 |
| 「想学 AI Agent 怎么大规模改写自己的仓库」 | `.claude/` `.codex/` `.gemini/` `AGENTS.md` `CLAUDE.md` + bot 提交历史 |

### 可迁移的三个设计思想

1. **「Schema 即六面契约」**——任何需要同时服务人和机器的系统都适用。不必引入本框架，把「一份 Zod schema 派生多种接口定义」这个模式抄走即可。
2. **「A2A 的认证/追踪/任务存储必须早拆」**——它把这三件事从第一天就做成独立模块，而不是等到出事再重构。
3. **「元技能（context-xray / visualize-repo）」**——给 Agent 提供「看清自己所处环境」的工具，比给它更多业务工具收益更高。

---

## 🔍 源码解读（克制版：只挑最能说明架构的两处）

### 1. adapters 层证明了「surface 是可插拔的」

```
packages/core/src/adapters/cli/index.ts
packages/core/src/adapters/cli/registry.ts        + registry.spec.ts
packages/core/src/adapters/cli/shell-adapter.ts   + shell-adapter.spec.ts
```

CLI 只是众多 adapter 之一，且有独立 `registry`（注册表）与 `shell-adapter`（壳适配）。这意味着新增一种 surface（比如 Slack bot、语音）只需实现一个 adapter，不动 action 本体。这是框架能否长期成立的关键——如果 surface 硬编码在 dispatch 里，六种就是天花板。

### 2. 每个核心文件都有同名 `.spec.ts`

`a2a-claims.ts / a2a-claims.spec.ts`、`action.ts / action.spec.ts`、`action-change-marker.ts / .spec.ts`、`action-type-inference.spec.ts`……

**这是本仓库最强的工程质量信号**：一个 4 个月大、由机器人大量提交的项目，核心层做到了近乎 1:1 的测试覆盖文件配比。对于「AI 大量写代码」的项目，这种 spec 密度是防止腐化的唯一现实手段。

---

## 🌐 全网口碑

| 来源 | 观点 |
|------|------|
| Builder.io 官方博客《Agent-Native: The Next Architecture for Software》 | 提出 5 条原则：agent UI parity、one shared action model、shared state and context、protocol readiness、governed execution；明确区分 **AI-native（AI 是核心）** vs **agent-native（Agent 与 UI 共享全部能力）** |
| Builder.io 设计侧博客 | 自陈动机：「厌倦了 AI 被塞进一个笨拙、脱节、碰不到宿主应用的侧边栏聊天框」；坦承「后端只是战役的一半」，公开邀请设计社区来批评用户流 |
| 腾讯云开发者社区长文 | 评价其「没有只写一篇未来宣言，而是把范式变成可下载、可运行、可定制、可部署的工程现实」；认可 README 那张 SaaS/Raw AI Agents/Internal Tools/Agent-Native 四方对比表「不绕弯子」 |
| txtmix 技术拆解 | 抓住核心：一条 `defineAction` 打通六种入口；指出仓库当时 2,504⭐ 时**许可证已是「未指定」**——即无 LICENSE 是长期状态，非近期疏漏 |
| learncode.college 实测 | 列出 4 项**隐藏成本**：① Drizzle ORM 学习曲线（从 Prisma/TypeORM 切换有适应期）；② Nitro 运行时约束（不能随意用 Node 专有 API）；③ **CRDT 合并冲突调试是噩梦级**，非多人多 Agent 并发编辑同字段建议先关；④ 插件生态相比 LangChain 很年轻，冷门集成需自己写 Adapter |

**口碑综合判断**：中文技术圈对其**范式意义**评价很高，对**工程成熟度**保持警惕。目前没有检索到大规模生产落地案例，讨论多停留在架构鉴赏与模板试用层面。

---

## ⚔️ 竞品对比

| 维度 | agent-native | Vercel AI SDK | LangChain/LangGraph | Mastra | 传统 SaaS + Chat 侧边栏 |
|------|---|---|---|---|---|
| 核心抽象 | **Action（六面派生）** | 流式 UI + tool call | Chain/Graph 编排 | Agent/Workflow | 无（两套系统拼接） |
| UI 与 Agent 状态 | **共享同一 DB 状态** | 分离 | 分离 | 分离 | 完全分离 |
| MCP | 内建 surface | 需自建 | 需适配 | 支持 | 通常无 |
| A2A | **13 模块一等公民** | ✗ | 实验性 | 部分 | ✗ |
| 附带完整应用模板 | **8+ 个可克隆模板** | 示例级 | 示例级 | 示例级 | — |
| 桌面/移动/浏览器扩展 | **全都有** | ✗ | ✗ | ✗ | — |
| 生态成熟度 | 4 个月，年轻 | 成熟 | 最成熟 | 中 | — |
| 许可证 | **无 LICENSE ⚠️** | Apache-2.0 | MIT | Apache-2.0 | — |
| 上手门槛 | 高（Drizzle + Nitro + CRDT） | 低 | 中 | 中 | 低 |

**关键差异**：AI SDK / LangChain 解决的是「怎么调模型、怎么编排」，agent-native 解决的是「一个产品怎么同时长出人脸和机器脸」。二者不在同一层，可以叠加使用——但 agent-native 强绑定 Drizzle + Nitro，替换成本高。

---

## 🎯 核心研判

### 优势
- **范式清晰且可执行**：agent UI parity 不是口号，`defineAction` 是能跑的落地物。
- **A2A 工程化程度罕见**：13 模块 + 逐一 spec，同类框架里的天花板。
- **模板即产品**：Clips（Loom 替代）、Plans（可视化 plan mode）、Design（Figma 替代）、Content（Notion 替代）、Analytics（Amplitude 替代）——每个都是能直接用的完整应用，而不是 hello world。
- **测试密度高**：核心层近 1:1 的 `.spec.ts` 配比，是 AI 大规模参与编码项目里的稀有质量护栏。

### 风险（采用前必须评估）
1. **⚠️ 无 LICENSE = 保留全部权利**：法律上默认「版权全保留」，企业内部使用/二次分发存在实质风险。这是**当前最大的阻断项**，需与 Builder.io 确认后再引入。
2. **强绑定栈**：Drizzle ORM + Nitro 运行时是硬约束，已有 Prisma/Express 体系的团队迁移代价大。
3. **CRDT 是双刃剑**：实时协作听起来美好，但社区实测反馈「调试合并冲突是噩梦级」；非必要建议关闭。
4. **商业化引力**：官方博客明确「个人路径克隆模板 → 团队路径由 Builder.io 提供托管/治理/权限」。开源框架是漏斗上游，长期路线图受商业公司节奏支配。
5. **15,556 文件的 monorepo**：仅 clone 与理解成本就不低，不适合小团队轻量试水。

### 适用 / 不适用
- ✅ **适用**：要把现有 SaaS 改造成「人机双入口」的中大型产品团队；需要同时对外提供 MCP + API + UI 的平台方；想研究 Agent 原生架构范式的技术决策者。
- ❌ **不适用**：只需要「加个聊天框」的项目（杀鸡用牛刀）；对开源许可证有硬合规要求的企业（**无 LICENSE 直接一票否决**）；已深度绑定 Prisma/NestJS 等异构栈的团队。

### 一句话结论
**范式上是 2026 年最值得研究的 Agent 应用架构之一，工程上是「测试写得很好但法律地位未定」的高风险资产。建议：先抄它的架构思想（Action 六面派生、A2A 模块边界），暂缓直接引入代码。**

---

## 📂 关键文件路径速查

| 想看什么 | 路径 |
|---------|------|
| Action 核心抽象 | `packages/core/src/action.ts` + `action.spec.ts` |
| Action 类型推导 | `packages/core/src/action-type-inference.spec.ts` |
| A2A 全套（13 模块） | `packages/core/src/a2a/` |
| A2A 权限声明 | `packages/core/src/a2a-claims.ts` |
| Surface 适配器模式 | `packages/core/src/adapters/cli/{index,registry,shell-adapter}.ts` |
| 多面分发 | `packages/dispatch/` |
| 内建 8 技能 | `skills/{assets,content,context-xray,design-exploration,visual-edit,visual-plans,visual-recap,visualize-repo}/` |
| 可复用积木 | `packages/toolkit/` |
| 浏览器控制 | `packages/{agent-browser-extension,agent-chrome-extension,browser-control-extension-core}/` |
| 产品理念自述 | `PRODUCT.md` / `AGENTS.md` / `CLAUDE.md` |
| 模板注册表 | `registry.json` / `registry/agent-native-app/AGENTS.md` |
| 开发者指南 | `DEVELOPMENT.md` |
| 工作区定义 | `pnpm-workspace.yaml` |
| **⚠️ 许可证** | **根目录不存在 LICENSE 文件** |

---

## 🔗 参考

- 仓库：https://github.com/BuilderIO/agent-native
- 官方站点/文档：https://agent-native.com/docs/actions
- 架构宣言：https://www.builder.io/blog/agent-native-architecture
- 设计视角：https://www.builder.io/blog/designing-generative-ui-in-an-agent-native-world
- 中文拆解：https://txtmix.com/posts/tech/builderio-agent-native-framework-architecture
- 实测隐藏成本：https://www.learncode.college/ai-tools-resources/agent-native
