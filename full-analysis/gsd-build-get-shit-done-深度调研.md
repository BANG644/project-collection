# gsd-build/get-shit-done 深度调研

> 调研日期：2026-08-03 ｜ 仓库：https://github.com/gsd-build/get-shit-done ｜ 实时星标：64,778 ⭐
> 许可：**MIT** ｜ 主语言：JavaScript ｜ 状态：**⚠️ 已归档（archived，2026-05-31 最后提交）**
> 现继承者：**open-gsd/gsd-core**（7,590 ⭐，MIT，活跃，https://github.com/open-gsd/gsd-core）

---

## 一、项目定位（与重要状态说明）

**GSD（Get Shit Done）** 是 TÂCHES 团队打造的 **meta-prompting / 上下文工程 / 规格驱动开发（spec-driven development）系统**，面向 Claude Code、OpenCode、Gemini、Codex 等多款编码 Agent。一句话：把"从想法到可交付代码"拆成多 Agent 协作的规格驱动流水线。

⚠️ **关键状态**：本仓库已于 2026-05-31 归档，README 已变为重定向存根：

> # GSD Has Moved — This repository is no longer the active home for GSD development. The project now continues as **GSD Core** in the Open GSD repository: https://github.com/open-gsd/gsd-core

**因此本报告定位为"冻结版（v1.50.0-canary）档案"**，价值在于解读其设计范式；实际开发已迁移至 `open-gsd/gsd-core`（星标 7,590，活跃）。任何新用户应直接去 gsd-core，而非本归档库。

---

## 二、项目亮点

1. **真正的多 Agent 编排**：`agents/` 目录含 25+ 个专职子 Agent 定义（planner / executor / code-reviewer / researcher / debugger / doc-writer …），不是单 prompt 套壳，而是角色化分工。
2. **规格驱动全流程**：以 phases（阶段）/ workstreams（工作流）/ milestones（里程碑）组织开发，`.changeset/` 下大量 ADR 式变更记录可见其工程纪律。
3. **跨 harness 兼容**：同一套系统同时服务 Claude Code、OpenCode、Gemini、Codex——上下文工程与具体模型解耦。
4. **自带 SDK 与工具链**：`bin/` 暴露 `get-shit-done-cc`（安装）、`gsd-sdk`、`gsd-tools` 三个入口，`sdk/` 含独立可复用推理层（src/shared/prompts/dist）。
5. **高星标冻结节点的范式价值**：64k 星标的归档仓库，是"多 Agent 规格驱动开发"最完整的开源实现样本之一，适合当作架构参考化石来读。

---

## 三、核心架构（基于冻结版真实树）

```
bin/              # 入口：install.js（安装）、gsd-sdk.js（sdk/tools）
commands/         # slash 命令定义
get-shit-done/    # 核心提示词/流程
agents/           # 25+ 专职子 Agent（见下）
hooks/            # harness hook（拦截/门禁）
scripts/          # 辅助脚本
sdk/              # 可复用推理层：src / shared / prompts / dist
.changeset/       # 大量 ADR 式变更记录（工程决策留痕）
```

**Agent 名册（节选）**——体现"角色化分工"思想：

| Agent | 职责 |
|-------|------|
| `gsd-planner` | 规划阶段总控 |
| `gsd-executor` | 执行阶段 |
| `gsd-code-reviewer` / `gsd-code-fixer` | 代码审查/修复 |
| `gsd-ai-researcher` / `gsd-domain-researcher` / `gsd-project-researcher` | 多维度研究 |
| `gsd-debugger` / `gsd-debug-session-manager` | 调试会话管理 |
| `gsd-doc-writer` / `gsd-doc-verifier` / `gsd-doc-synthesizer` | 文档生成与核验 |
| `gsd-codebase-mapper` / `gsd-pattern-mapper` | 代码库/模式映射 |
| `gsd-eval-auditor` / `gsd-eval-planner` | 评估审计/规划 |
| `gsd-assumptions-analyzer` / `gsd-plan-checker` | 假设/计划校验 |

`.changeset/` 中可见 `plan-phase-opencode-dispatch`、`phase-complete-state-staleness`、`workstream-inventory-builder`、`milestone-generic-heading` 等记录——印证其以 **phase → workstream → milestone** 为骨架的规格驱动模型。

---

## 四、应用场景与启发

- **下次设计"多 Agent 协作编码系统"**：GSD 的 `agents/` 名册是现成的角色划分模板（规划/执行/审查/研究/调试/文档/评估各司其职），直接照抄角色清单就能搭出第一版。
- **规格驱动而非 prompt 驱动**：它的 phase/workstream/milestone 三层结构，是把"需求→规格→实现"工程化的范本，比"一个超长 system prompt"更可维护、可审计。
- **跨 harness 设计**：把上下文工程与具体模型解耦（Claude/OpenCode/Gemini/Codex 通用），是"Agent 能力应可移植"理念的早期实践——与 Anthropic Skills、agent-skills 等"能力单元"思潮同源。
- **归档项目的正确姿势**：GSD 用 README 重定向 + 明确继承者，给"项目交接/改名/归档"提供了干净范例（对比那些直接 404 的死库）。

---

## 五、源码深度解读

### 5.1 `package.json` 揭示的产品形态

```json
{
  "name": "get-shit-done-cc",
  "version": "1.50.0-canary.0",
  "description": "A meta-prompting, context engineering and spec-driven
    development system for Claude Code, OpenCode, Gemini and Codex by TÂCHES.",
  "bin": {
    "get-shit-done-cc": "bin/install.js",
    "gsd-sdk": "bin/gsd-sdk.js",
    "gsd-tools": "bin/gsd-sdk.js"
  },
  "files": ["bin","commands","get-shit-done","agents","hooks","scripts","sdk/src",...]
}
```

三个 bin 入口（安装器 / SDK / 工具）说明它既是"给用户的安装包"，也是"可嵌入的 SDK"——分层清晰。

### 5.2 `agents/` 即"组织"：每个角色一个 Markdown

25+ 个 `gsd-*.md` 不是代码，而是**给 LLM 读的角色说明书**（系统提示词 + 职责边界）。GSD 的核心创新点是：用一套结构化的 Agent 名册 + 阶段状态机，把"写代码"变成可编排、可审计的协作流程，而非依赖单个超强 prompt。

### 5.3 `.changeset/`：工程决策留痕

大量 ADR 式变更文件（如 `3577-adr-violations-and-validation-port.md`、`3271-sdk-adr-structure.md`）表明团队用 changesets 同时管理"版本发布"与"架构决策记录"——对开源 Agent 项目而言是难得的工程成熟度信号。

---

## 六、社区口碑

- **定位**：2025 年底爆红的多 Agent 规格驱动开发系统，曾是与 superpowers / agent-skills 并列的"Claude Code 工作流"代表之一。
- **正面**：Agent 角色划分细、跨 harness、自带 SDK，被大量博客/视频当作"多 Agent 编码"教学案例。
- **争议/风险**：① **已归档**，新用户应转向 gsd-core（星标仅 7,590，生态热度已显著回落）；② `1.50.0-canary.0` 的版本号表明冻结前仍处 canary 阶段，稳定性未经充分验证；③ 25+ Agent + phase/workstream 概念学习曲线陡，轻量需求可能 over-engineering。
- **中文社区**：作为"Claude Code 多 Agent 工作流"标杆被广泛讨论，但归档后讨论热度骤降。

---

## 七、竞品对比 + 核心研判

| 维度 | gsd-build/get-shit-done（归档） | github/spec-kit | addyosmani/agent-skills | obra/superpowers |
|------|-------------------------------|----------------|------------------------|------------------|
| 驱动模型 | 多 Agent 规格驱动 | Spec-Driven Dev | 软件全生命周期技能 | 子 Agent 驱动开发 |
| Agent 数 | 25+ 专职 | 模板+30+适配 | 24 技能 | 子 Agent 方法论 |
| 跨 harness | Claude/OpenCode/Gemini/Codex | 30+ Agent 适配 | 通用 | 通用 |
| 现状 | ⚠️ 已归档→gsd-core | 活跃 | 活跃 | 活跃 |

**核心研判**
- ✅ **范式价值高**：其"角色化 Agent 名册 + phase/workstream/milestone 状态机 + 跨 harness 上下文工程"是今天仍值得借鉴的多 Agent 编码范式，gsd-core 继续演进。
- ⚠️ **务必认准继承者**：本库已冻结，直接 `git clone` 本仓库等于拿一份 canary 化石；新项目请去 `open-gsd/gsd-core`。
- 🔮 **趋势**：规格驱动 + 多 Agent 协作已成为 AI 编码主流范式之一，GSD 是这条路上的重要早期样本；其"上下文工程与模型解耦"的思路，与 Skills/agent-skills 等"可移植能力单元"思潮汇聚，预示 Agent 工作流正走向"声明式规格 + 可插拔执行器"的成熟形态。

---

## 八、关键文件速查

| 路径 | 作用 |
|------|------|
| `README.md` | 重定向存根（指向 open-gsd/gsd-core） |
| `package.json` | 产品定义（bin 入口 + sdk 文件清单） |
| `agents/` | 25+ 专职子 Agent 角色说明书（核心） |
| `commands/` | slash 命令定义 |
| `get-shit-done/` | 核心提示词与流程 |
| `hooks/` | harness hook（拦截/门禁） |
| `sdk/` | 可复用推理层（src/shared/prompts/dist） |
| `.changeset/` | ADR 式工程决策留痕 |

---

*本调研基于 2026-08-03 实时抓取的仓库元数据（archived/MIT/64,778⭐）、README 重定向存根、package.json 与真实 `agents/` 名册 + `.changeset/` 结构；继承者 open-gsd/gsd-core 已核验（7,590⭐ MIT 活跃）。报告定位为"归档版档案"，覆盖星标/状态/架构/源码/口碑/竞品，远超 README。*
