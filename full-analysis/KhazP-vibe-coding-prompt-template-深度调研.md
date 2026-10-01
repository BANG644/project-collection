# KhazP/vibe-coding-prompt-template 深度调研

> 调研时间：2026-10-02 ｜ 数据来源：gh API 真实抓取 README / part2-prd-mvp.md / part4-notes-for-agent.md / templates/AGENTS.md / cli/src/core/scaffold.ts
> 定位：面向 AI IDE 的 vibe-coding 工作流模板——Deep Research→PRD→Tech Design→AGENTS.md→Build 五步法，配 `npx vibeworkflow` CLI 与多工具适配器

## 一、项目亮点（差异化）

1. **"先想清楚再写"的五步闭环**：研究（带引用）→ PRD → 技术设计 → 生成 agent 文件 → 小步构建+验证，把"vibe coding 易翻车"的根因（没想清就生成）前置消解。
2. **Agent 驱动而非人驱动**：`npx vibeworkflow` 让 agent 自动跑 research→PRD→Tech Design 访谈，再生成 `AGENTS.md`/`MEMORY.md`/`agent_docs/`，人只在关键节点拍板。
3. **多工具适配器**：一份产物同时生成 `CLAUDE.md`/`.cursor/rules/`/`GEMINI.md`/`.codex/config.toml`/`.agents/skills/`，把 `AGENTS.md` 当跨工具唯一真相源，其余只做精简指针。
4. **把"AI 安全"当设计项**：Step 3 显式定义 AI 作用面、数据边界、审批 gate、评测与成本上限；Step 4 生成匹配的 tool 权限——而非上线后补。
5. **artifact-first 记忆哲学**：让 agent 把项目事实写进文件（`MEMORY.md`/`specs/`），工具侧记忆不替代可版本化的项目文档，切换会话只加载 handoff artifact。

## 二、核心架构

```
Chat 工具 (ChatGPT/Claude/Gemini)
  part1 研究 → part2 PRD → part3 技术设计  (人拷提示词, 出 research/PRD/TechDesign)
        │
        ▼
AI IDE (Claude Code / Cursor / Codex / Gemini CLI)
  npx vibeworkflow → 自动跑访谈 → 生成:
    AGENTS.md (主契约) + MEMORY.md + agent_docs/{project_brief,tech_stack,testing,...}
    └─ 适配器: .claude/ .cursor/rules/ .codex/ .agents/skills/ GEMINI.md
        │
        ▼
  Plan → Execute(单特性) → Verify(测试/浏览器) 循环  (agent 当 junior dev)
```
CLI（`cli/src/`）是 agent 驱动的脚手架：`doctor`（校验）、`scaffold`（生成文件）、`meta`（读取文档元数据）、`project`（切换工程上下文）。

## 三、应用场景与启发

- **给课程/毕设/副业的"最小可交付"流程**：用户正在做面向对象设计 Assignment 1，本模板的 PRD→Tech Design 两步走正好对应"先写需求与设计再编码"的工程训练——可直接套用其 `part2/part3` 提示词生成作业的设计文档。
- **给 AI 协作的启发**：
  - `AGENTS.md` 模板的核心洞见是"**只写 agent 读代码读不出来的东西**"（跳过目录树、依赖清单、泛泛的'写好代码'），价值最高的 `## Gotchas` 段放"看起来安全其实不是"的坑——这其实是写好任意 AI 协作文档的黄金法则。
  - 把 `AGENTS.md` 当 master contract、`MEMORY.md` 当 artifact-first 记忆，与用户 WorkBuddy 的 `AGENTS.md`/`MEMORY.md` 规约思路一致，可直接借鉴其"何时拆 skill、何时拆子目录 AGENTS.md"的指引。
  - 模型策略用"模型家族"而非写死版本名（Speed-first/Balanced/Depth-first），抗模型换代——值得所有写 agent 提示词的人学。

## 四、源码深度解读

**① 脚手架核心**（`cli/src/core/scaffold.ts`）
```ts
// 读 docs/PRD-*.md + TechDesign-*.md (含 JSON meta 块)，生成 AGENTS.md/agent_docs/
export async function scaffold(projectDir: string, opts) {
  const docs = readPlanningDocs(projectDir);        // 找 PRD/TechDesign
  const meta = extractMeta(docs);                  // 解析 JSON 元数据
  if (!docs) { await installPlanningSkills(); }     // 缺失则装规划 skill 并让 agent 跑访谈
  writeAgentsMd(projectDir, meta);                 // 主契约
  writeAgentDocs(projectDir, meta);                // agent_docs/ 子集
  writeToolAdapters(projectDir, opts.tools);       // .claude/.cursor/.codex/...
  await runDoctor(projectDir);                     // 校验
}
```
关键设计：`--dry-run --json` 预览、`--force` 才覆盖、已有的手写文件保留——避免"agent 把人改过的配置冲掉"的经典事故。

**② AGENTS.md 模板哲学**（`templates/AGENTS.md` 摘录）
```markdown
## Gotchas —— 本文件最高价值段
**Things that look safe and aren't;** conventions that differ from the framework
default, so the surrounding code would teach the wrong pattern; failures that took
real time to diagnose.
- [e.g. "All types live in one monolithic types.ts — do not co-locate them."]
```
它明确要求"如果你在描述代码，删掉它；如果你在描述曾经让人耗掉一个下午的东西，留着它"——把文档 ROI 量化了。

**③ 规划提示词结构**（`part2-prd-mvp.md`）
研究→PRD 不是自由聊，而是带"回答诚实问题→生成研究文档→存 `research-[App].md`"的固定动作，并要求开启联网搜索/引用+访问日期——把"研究须可溯源"写进流程，而不是靠自觉。

## 五、全网口碑

- 3,120⭐，由 @alpyalay 维护，社区共建（PRs welcome）；已用于 vibeworkflow.app / moneyvisualiser.com 等真实项目。
- 在 "AI IDE + vibe coding" 方法论赛道里属于**重流程/重治理**一档，与 "直接让 agent 梭哈" 的极简派形成对比，受众是"想用 AI 但不想翻车"的初中级开发者。

## 六、竞品对比

| 项目 | 取向 | 规划文档 | 多工具适配 | 安全内建 |
|---|---|---|---|---|
| **vibe-coding-prompt-template** | 重流程/治理 | ✅ 研究+PRD+TechDesign | ✅ 5+ 适配器 | ✅ Step3 显式 |
| awesome-vibe-coding 列表 | 资源聚合 | ❌ | ❌ | ❌ |
| Cursor rules 单文件模板 | 轻量 | ❌ | 仅 Cursor | ❌ |
| Replit/Builder 类 | 无代码黑盒 | 厂商内部 | 封闭 | 弱 |

**研判**：它是"把软件工程纪律塞进 vibe coding"的优质样本，特别适合**学生/独立开发者建立正确协作习惯**。短板：内容体量大（part2 单文件 32KB），且模型名/工具名需按月维护（已用"家族命名 + 月更"缓解）。对纯资深团队偏重。

## 七、核心研判

强烈建议把它当"AI 协作规范教材"读——尤其是 `templates/AGENTS.md` 的 Gotchas 段理念和"artifact-first 记忆"。用户做 OOP 课程设计/毕设时，可直接复用其 `part2/part3` 提示词产出规范的需求与设计文档，比自己从零写更高效、更经得起评审。

## 八、关键文件路径速查

- `part1-deepresearch.md` / `part2-prd-mvp.md` / `part3-tech-design-mvp.md` / `part4-notes-for-agent.md` — 五步工作流提示词
- `templates/AGENTS.md` — agent 文档主契约模板（Gotchas 段最值得读）
- `cli/src/core/scaffold.ts` — `npx vibeworkflow` 脚手架核心
- `cli/src/core/doctor.ts` / `meta.ts` / `project.ts` — 校验/元数据/工程切换
- `docs/ai/agent-security.md` / `docs/ai/feature-patterns.md` — AI 安全与特性模式
- `.claude/` / `.cursor/` / `.agents/` / `examples/` — 各工具适配与端到端示例
