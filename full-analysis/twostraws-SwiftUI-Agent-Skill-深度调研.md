# twostraws/SwiftUI-Agent-Skill 深度调研

> 调研日期：2026-10-10 | 来源：GitHub Trending（当日新增）| Stars：5,348 | 语言：Markdown/Skill | 许可：MIT | 作者：Paul Hudson（Hacking with Swift）

## 1. 项目定位（一句话）

**SwiftUI Pro**——一套给 AI 编码助手（Claude Code / Codex / Gemini / Cursor）做 SwiftUI 代码审查与现代化改造的 Agent Skill，专攻 iOS 26+ / Swift 6.4+ 现代 API 下 LLM 实际会犯的错。

## 2. 项目亮点（差异化）

- **经验即规则**：由 Swift 社区权威教育者 Paul Hudson（Hacking with Swift）把「多年真实项目踩坑」沉淀成审查规则，直击 LLM 典型错误（VoiceOver 不可见、误用废弃 API、隐性性能陷阱）。
- **渐进披露 + token 纪律**：SKILL.md 只编排流程，细节拆到 `references/` 下 12 个主题文件按需加载；`performance-plus.md` 显式「非例行审查不加载」，尊重 token 预算。
- **多 harness 即装**：兼容 agentskills.io 开放格式，支持 `npx skills add`、Claude Code `/plugin marketplace`、克隆安装，覆盖 Claude/Codex/Gemini/Cursor。
- **可触发式审查**：`/swiftui-pro`、`$swiftui-pro` 或自然语言触发，可带「只查性能」「聚焦无障碍」等局部指令。
- **系列化**：同作者还有 SwiftData Pro / Swift Concise Pro / Swift Testing Pro，形成 Apple 平台 Skill 矩阵。

## 3. 核心架构

标准 Agent Skill 目录（符合 agentskills.io 规范）：

- **`swiftui-pro/skills/swiftui-pro/SKILL.md`**：frontmatter（`name` / `description` / `license: MIT` / `argument-hint` / `metadata.author=Paul Hudson, version=2.0.0`）+ 11 步审查流程，每步映射到 `references/` 文件。
- **`swiftui-pro/references/`**：`api.md`（废弃 API）、`views.md`、`data.md`、`navigation.md`、`design.md`、`resizability.md`、`accessibility.md`、`localization.md`、`performance.md`、`performance-plus.md`、`swift.md`、`hygiene.md`——知识图谱式拆解。
- **`swiftui-pro/agents/openai.yaml`** + **`.claude-plugin/plugin.json` / `marketplace.json`**：多 harness 分发（Claude Code 插件市场 + OpenAI 适配）。

## 4. 应用场景与启发

- **「专家经验 → Skill」范式样板**：把某领域高手的可意会经验显式写成可加载规则，是构建高信噪比领域 Skill 的极佳参考（尤其对用户自有的 UI/UX、diagram-design 类 Skill）。
- **针对 LLM 特定错误模式而非通识**：不重复 LLM 已知内容（README 明确「不要烧 token 讲 LLM 已懂的」），只覆盖 edge case / soft deprecation / 版本假设——值得所有经验型 Skill 借鉴。
- **渐进披露控制成本**：核心知识 SKILL.md 薄、细节下沉 references，避免一次性灌入全部上下文。

## 5. 源码深度解读

**① 审查流程编排（`SKILL.md`）**
11 步流程把一次审查拆成可定位的子检查，每步指向一个 reference 文件，按需加载而非全量注入：

```markdown
# SKILL.md（范式，节选）
1. Check for deprecated API using `${CLAUDE_SKILL_DIR}/references/api.md`.
2. Validate data flow using `${CLAUDE_SKILL_DIR}/references/data.md`.
...
# 输出按文件组织，每条给 rule + before/after 修复
```

**② token 纪律（`references/performance-plus.md`）**
显式标注「Keep out of routine reviews. Load it for a requested deep performance review」——把重负载知识隔离，避免每次审查都付出成本，是 Skill 设计的成本控制范本。

**③ 多 harness 分发（`agents/openai.yaml` + `.claude-plugin/plugin.json`）**
同一份知识通过 plugin manifest 与 agent manifest 同时服务 Claude Code 与 OpenAI 系工具，体现「写一次、多端装」的 Skill 工程化思路。

## 6. 社区口碑

- 作者 Paul Hudson 是 Swift 社区最权威的教育者之一（Hacking with Swift / HWS+），自带高信任流量。
- MIT 许可、遵循 agentskills.io 开放标准，与主流编码助手生态对齐；README 强调「尊重 token 预算」契合 agent 实际痛点。
- 属轻量 Skill 仓库（非重型代码库），价值在知识密度而非代码量。

## 7. 竞品对比 + 核心研判

| 维度 | SwiftUI Pro | 其他 Swift Skill（同作者系列） | 通用代码审查 Skill | IDE 内置规则 |
|------|-----------|-------------------------------|-------------------|-------------|
| 聚焦 | SwiftUI 具体错误模式 | SwiftData/并发/测试 | 泛语言 | 通用 lint |
| 多 harness | ✅ | ✅ | 视实现 | 单一 IDE |
| token 纪律 | ✅ 渐进披露 | ✅ | 弱 | — |

**研判**：作为「经验型 Skill」样板价值高，对用户自建领域 Skill（如 diagram-design、ui-ux-super-optimizer）有直接架构借鉴；轻量、低风险、可立即复用。注意版本假设（iOS 27 / Swift 6.4 / Xcode 27.1）需随 SDK 演进而维护，否则会给出过时建议。

## 8. 关键文件路径速查

- `swiftui-pro/skills/swiftui-pro/SKILL.md`：审查流程与触发定义
- `swiftui-pro/references/*.md`：12 个细分主题（api / views / data / navigation / design / resizability / accessibility / localization / performance / performance-plus / swift / hygiene）
- `swiftui-pro/agents/openai.yaml`：OpenAI 系 harness 适配
- `.claude-plugin/plugin.json` / `marketplace.json`：Claude Code 插件市场分发
- `README.md`：安装与触发说明
