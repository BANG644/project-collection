# 🔬 Michaelliv/pi-dynamic-workflows — 全方位深度调研

> 调研时间：2026-11-24（修旧账重写，原稿为 2026-06-19 抽样模板报告）
> 数据来源：`gh api` 实时抓取（仓库元数据 / README / 文件树 / 16 个 Issue / 2 个 Release / `src/index.ts` 源码）

## 📌 一句话定位

给 Pi 编码 Agent 装一个「**工作流编译器**」：模型用几行 JavaScript 写下「先扫仓库 → 并行分析 → 汇总」的脚本，工具在 Node `vm` 沙箱里执行，把任务 fan-out 到多个隔离子 Agent，再回收结构化结果——本质是 Anthropic Claude Code 动态工作流能力的**开源最小复刻**，面向 Pi 这个轻量 Agent harness。

> 核心判断：它不是「又一个 Agent 框架」，而是**一层薄薄的工作原语**（`agent` / `parallel` / `pipeline` / `phase`），设计精华全在「如何用确定性约束驯服不确定性子 Agent」。当前是 prototype，无持久化/续跑，**适合学设计、不适合上生产**。

**实时数据**：1,240⭐ / 75 forks / TypeScript / MIT / 17 open issues / 最后推送 2026-05-31 / 仅 2 个 Release（v1.0.0→v1.0.1，均 5 月）。

## ⭐ 项目亮点

1. **把工作流变成「可编译的脚本」而非 prompt**：`meta` 必须是脚本第一条语句的字面量对象，解析器用 AST 校验（spread / 计算属性 / 模板插值 / 函数调用一律拒绝），保证 `meta` 可被静态解析、运行可复现。这是 README 不会点破的关键设计——它牺牲表达力换确定性。
2. **沙箱里主动阉割不确定性源**：Node `vm` 中禁掉 `Date.now()`、`new Date()`、`Math.random()`、`require/import/fs/网络 API`。一个 fan-out 工具主动禁止随机数和时钟，是相当罕见的「可复现性优先」取舍。
3. **`phase()` 运行时发现机制**：阶段不是预先声明的静态列表，而是脚本跑到 `phase('Scan')` 时才登记。于是条件分支 / 循环产生的阶段自然工作，被跳过的分支不会留下空进度行——这解决了一个真实 UI 痛点。
4. **结构化子输出用 `terminate: true` 省一轮**：给 `agent()` 传 JSON Schema，底层是一个 TypeBox 支撑的 `structured_output` 工具，子 Agent 一调用它就结束，不必多一轮 assistant 回复。
5. **`budget` 一等公民**：全局暴露 `{ total, spent(), remaining() }` token 预算追踪，让脚本自己能根据余量决定 fan-out 规模——把「成本控制」下沉到工作流作者手里。

## 🏗️ 项目架构全景

### 模块骨架（源码文件树实证）

这是一个**极小仓库**（顶层仅 `src/ tests/ extensions/ types/`），核心是 6 个模块，`src/index.ts` 只是 re-export 门面：

| 模块 | 职责（来自 README + index.ts 导出） |
|---|---|
| `src/workflow.ts` | AST 校验解析器 + `vm` 沙箱运行时；导出 `parseWorkflowScript` / `runWorkflow` |
| `src/workflow-tool.ts` | Pi 的 `workflow` 工具：prompt 指引、渲染、abort 处理；导出 `createWorkflowTool` |
| `src/agent.ts` | `WorkflowAgent` 内存子 Agent runner；导出 agent 运行选项/结果类型 |
| `src/structured-output.ts` | `terminate: true` 的结构化输出工具（TypeBox/JSON Schema） |
| `src/display.ts` | 工作流快照与紧凑文本渲染（`renderWorkflowLines` / `recomputeWorkflowSnapshot`） |
| `extensions/workflow.ts` | Pi 扩展入口，注册工具并在会话启动时激活 |

`src/index.ts` 全部内容就是 30 行类型/函数转出，本身无逻辑——这是判断「小仓库」的最快信号：**真正的复杂度集中在 workflow.ts 的解析+沙箱层**。

### 运行链路（README "How it works" 图 + Issue 佐证）

```text
用户自然语言请求
  → Pi 模型生成 workflow 脚本（字面量 meta + agent()/parallel()/pipeline() 调用）
  → workflow 工具 parseWorkflowScript（AST 校验 meta）
  → Node vm 沙箱执行，phase() 运行时登记阶段
  → 每次 agent() 起一个全新内存 Pi 子会话（带标准编码工具）
  → 快照流回父会话做紧凑进度渲染（Esc 可 abort，活跃子 Agent 标记 skipped）
  → 最终结构化结果返回父 Assistant
```

### 技术栈

TypeScript + `biome`（lint/format，见 `biome.json`）+ Node `vm` 沙箱 + TypeBox/JSON Schema。`package.json` 无重型运行依赖——这是一个「靠 harness 而不是靠自己」的极简设计。

## 💡 应用场景与启发（重点章节）

### 典型使用场景

- **代码库审计 / 多视角评审**：fan-out 出「安全视角」「性能视角」「可维护性视角」三个子 Agent，各自独立读仓库，最后汇总——正是它 README 点名的场景。
- **大规模重构前的并行勘察**：`pipeline(items, ...stages)` 让 N 个文件各自流经「定位→分析→出补丁建议」阶段，item 间并行、阶段间串行。
- **fan-out 研究**：一个 prompt 撒出去问多个独立子问题，用 `opts.schema` 保证每份答案结构一致，便于程序化聚合。

### 可借鉴的解决方案模式

1. **「字面量 meta + AST 白名单」作为 LLM 生成代码的安全契约**。当你的系统要让模型生成可执行脚本时，不要试图信任它——像本项目一样：强制第一段是字面量元数据，用 AST 拒绝一切动态构造。这比事后正则校验可靠得多，可直接迁移到「让 Agent 写配置/规则」的任何场景。
2. **主动移除不确定性源以实现可复现**。多数 Agent 系统对随机性听之任之；本项目证明在 fan-out 编排层禁掉时钟/随机数是可行的（子 Agent 内部仍可用工具）。做评测/回归时，这一手能让你「同样的脚本，同样的编排结果」。
3. **`phase()` 的运行时登记思路**。进度条不该由静态 plan 驱动，而应由执行流驱动——分支跳过就不显示。任何做「任务可视化」的产品都能借鉴。
4. **预算作为全局一等公民**。`budget.remaining()` 让脚本自适应规模，比外部硬 kill 优雅。做多 Agent 成本治理时值得抄。

### 同类需求的可参考思路

如果你在用 Claude Code 的 Workflow 但想要「可嵌入自己 harness 的最小实现」，这个仓库就是答案骨架：6 个模块、无外部服务、核心逻辑不到千行。它证明了「动态工作流」的护城河不在编排概念，而在**沙箱安全性 + 进度聚合 UX**。

### 不适用场景（先看边界）

- 需要断点续跑 / 持久化 / 工作流管理（`/workflows`）——README Status 明说**尚未实现**。
- 需要长时间后台运行的任务——in-memory 子会话随进程存活。
- 需要branchness/多模型混合调度——Issue #「Support per-agent model selection」仍 open。

## 🧠 核心源码解读

### 入口与主流程：门面 re-export（`src/index.ts`）

```ts
export { WorkflowAgent } from "./agent.js";
export { parseWorkflowScript, runWorkflow } from "./workflow.js";
export { createWorkflowTool } from "./workflow-tool.js";
export { createStructuredOutputTool } from "./structured-output.js";
```

30 行的门面，把解析/运行、工具、子 Agent、结构化输出四条线暴露出去。**设计信号**：作者刻意把「解析」和「运行」拆成两个导出——解析器可独立单测（`tests/workflow-parser.test.ts` 覆盖 accept/reject 两类脚本形状），这是把「模型生成代码的校验」当成独立安全边界来处理。

### 沙箱与确定性规则（README + Issue 交叉验证）

Node `vm` 里被剥夺的能力清单是本项目最有价值的「负面设计」：禁 `Date.now` / `new Date` / `Math.random` / `require` / `import` / `fs` / 网络。配合 AST 层对 `meta` 的限制（禁 spread、计算键、模板插值、函数调用），形成两层确定性防线。

**独家观察**：Issue 列表里有一条「Mentioning sources of randomness in agent prompts triggers the non-determinism checker」——说明这个 checker 是**文本级扫描**，连 prompt 里提到"randomness"字样都会误报。这是"过度确定性"带来的可用性副作用，README 完全没写。

### 结构化输出：`terminate: true` 的省轮技巧

`agent(prompt, { schema })` 底层是 Pi 的 `structured_output` tool，设置 `terminate: true` 让子 Agent 输出即结束（否则要多一轮 assistant turn 来"确认"结果）。这是 fan-out 场景下省 token/延迟的关键微优化——**每个子 Agent 省一轮，N 个子 Agent 就是 N 轮**。

## 📐 架构决策与设计哲学

- **可复现 > 表达力**：禁随机数/时钟、AST 白名单，都是为了「脚本行为可预测、可单测」。
- **薄原语 > 大框架**：只提供 4 个原语（`agent`/`parallel`/`pipeline`/`phase`），组合能力交给脚本作者。
- **明确的能力边界**：README Status 直白承认 prototype，无持久化/续跑。Issue 里有完整的 epic「persisted/resumable workflows + /workflows + saved registry」——说明作者知道下一步往哪走，只是尚未落地。
- **对标而非抄袭**：灵感来自 Anthropic Claude Code 动态工作流，但落到 Pi 生态；Issue「Audit: faithfulness gaps vs Claude Code's integrated Workflow tool (6 untracked)」显示社区在主动比对两者差距。

## 🌐 全网口碑画像

本项目是 2026-05 才创建的极小众原型，公开第三方长评稀缺，**按诚实原则不编造**。以下为 GitHub 一手信号 + 可核验来源：

- **GitHub 一手**：1,240⭐ / 17 open issues（对 1.2k⭐ 的小项目而言 issue 密度极高，说明用户在真实使用并反馈）。Issue 质量很高——「meta.phases rejects string entries with an opaque error」「#<Promise> could not be cloned」都是具体可复现的 bug 报告，不是灌水。
- **社区诉求集中在「补全生产特性」**：persisted/resumable workflows、per-agent model selection、forked agents（共享父上下文 fan-out）、step-level replay（memoized agent results）、`/workflows` 管理命令——清一色是「从原型走向可用」的诉求。
- **对标讨论**：Issue 明确出现「faithfulness gaps vs Claude Code's integrated Workflow tool (6 untracked)」，说明定位被社区理解为「Claude Code Workflow 的 Pi 版复刻」。
- **设计认可信号**：Issue「Support strong/medium/weak model configuration」说明用户已经在认真考虑成本/质量分层，这是把工具当真用才会有的诉求。
- **透明度**：README 自标 prototype + MIT，无营销夸大；这对早期工具是加分项。

> 口碑结论：处于「早期采用者深度试用」阶段——issue 质量高、诉求集中在补全生产特性，但缺持久化是最大劝退点。尚无中英文技术博客长评，**数据可用性有限，如实标注**。

**可核验来源**：[GitHub 仓库与 Issue](https://github.com/Michaelliv/pi-dynamic-workflows/issues) · [README（设计哲学/沙箱规则）](https://github.com/Michaelliv/pi-dynamic-workflows/blob/main/README.md) · [灵感来源：Claude Code Dynamic Workflows](https://claude.com/blog/introducing-dynamic-workflows-in-claude-code)

## ⚔️ 竞品对比

| 方案 | 定位 | 工作流编排 | 沙箱/确定性 | 持久化续跑 | 生态 |
|---|---|---|---|---|---|
| **pi-dynamic-workflows** | Pi 的最小动态工作流原语 | JS 脚本 fan-out ✅ | AST 白名单 + vm 禁随机 ✅❗ | ❌（prototype） | Pi 专用，1.2k⭐ |
| Claude Code Dynamic Workflows | 官方内置，同灵感来源 | ✅ | 官方实现 | ✅（产品级） | Claude Code 内置 |
| LangGraph / Temporal | 有状态工作流引擎 | 图/代码编排 ✅ | 依赖宿主 | ✅✅ | 通用重型框架 |
| 手写 fan-out prompt | 零依赖 | ❌ | ❌ | ❌ | 无 |

**选择建议**：想学「动态工作流最小实现」或给 Pi 加编排能力 → 本项目；要生产级续跑/管理 → Claude Code 原生或 Temporal；它目前不替代任何成熟引擎。

## 🎯 核心研判

### 优势

1. **设计浓度极高**：几百行代码把「脚本化 fan-out + 确定性沙箱 + 进度聚合」讲透了，是教科书级的参考实现。
2. **取舍清晰**：主动禁随机/时钟、AST 校验、prototype 自标——知道不做什么比做什么更能说明成熟度。
3. **issue 驱动的高质量反馈循环**：17 个具体 issue 指向明确的下一步路线图。

### 风险

1. **prototype 无续跑**：进程一挂、长任务全丢；README 明说未实现。
2. **过度确定性副作用**：non-determinism checker 连 prompt 里提到 randomness 都误报（Issue 佐证），可能误伤正常用法。
3. **单 harness 绑定 + 停在 5 月**：最后推送 2026-05-31，近 6 个月无更新；Pi 生态本身小众。
4. **bus factor 风险**：极小仓库，贡献者集中。

### 适用场景 & 不适用场景

- ✅ 代码库审计、多视角评审、并行研究、重构勘察（短时、可重复、fan-out 型）。
- ❌ 长时后台任务、需要断点续跑、需要多模型混合调度、生产 SLA 场景。

### 趋势判断

**早期原型期**。价值在「设计范本」而非「产品可用」。若作者补齐持久化 + model 分层（issue 路线图已列），有望成为 Pi 生态的编排标配；否则会停留在"精巧的小玩具"。

## 📂 关键文件路径速查

| 路径 | 用途 |
|---|---|
| `src/workflow.ts` | AST 校验解析器 + vm 沙箱运行时（核心中的核心） |
| `src/workflow-tool.ts` | Pi `workflow` 工具、prompt 指引、abort |
| `src/agent.ts` | `WorkflowAgent` 内存子 Agent runner |
| `src/structured-output.ts` | terminate 型结构化输出（TypeBox） |
| `src/display.ts` | 快照与紧凑进度渲染 |
| `extensions/workflow.ts` | Pi 扩展入口 |
| `tests/workflow-parser.test.ts` | 脚本 accept/reject 形状单测 |
| `README.md` → Determinism rules / Available globals | 沙箱禁项与 4 原语权威清单 |
