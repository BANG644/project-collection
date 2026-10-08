# anthropics/knowledge-work-plugins 深度调研

> 调研日期：2026-10-09 ｜ 来源：GitHub Trending（当日新增） ｜ Stars：27,415 ⭐ ｜ 语言：Python ｜ 许可：Apache-2.0 ｜ 默认分支：main

## 一、项目定位（一句话）

Anthropic 官方开源的「知识工作插件」市场——把 Claude（Claude Cowork / Claude Code）变成按**角色、团队、公司**定制的领域专家，核心是把 **Skills（技能）+ Connectors（MCP 连接器）+ Commands（斜杠命令）** 打包成可组合、可 Fork 的插件。

## 二、项目亮点（差异化）

1. **官方出品的「角色插件」范式**：一次性开源 11 个开箱即用插件（productivity / sales / customer-support / product-management / marketing / legal / finance / data / enterprise-search / bio-research / cowork-plugin-management），覆盖产研销支法财数等职能，每个插件 = Skills + Connectors + Commands 三件套。
2. **纯文件化、零构建**：插件目录仅含 `plugin.json` 清单 + `.mcp.json` 连接器 + `commands/` + `skills/`，全部 Markdown / JSON，无代码、无基础设施、无构建步骤——Fork 即改、PR 即贡献。
3. **真实连接器矩阵**：每个插件显式列出对接的外部工具（Slack / Notion / Jira / HubSpot / Snowflake / Databricks / Microsoft 365 …），通过 MCP 把 Claude 接进企业 SaaS。
4. **内置安全治理层**：仓库根 `.github/policy/` 用 `schema.json` 把「插件可信度」变成可机检的布尔契约（钩子广度、未披露遥测、外部网络调用、描述与行为一致性），由 CI 工作流自动扫描。

## 三、核心架构

- **插件 = 文件目录**：`plugin-name/{.claude-plugin/plugin.json, .mcp.json, commands/, skills/}`；Skills 自动触发、Commands 显式 `/plugin:cmd` 调用、Connectors 走 MCP。
- **市场聚合**：根 `.claude-plugin/marketplace.json`（约 68 KB，记录 11 个插件的 SHA）通过 `claude plugin marketplace add anthropics/knowledge-work-plugins` 安装；`claude plugin install sales@knowledge-work-plugins` 装单个。
- **治理流水线**：`.github/workflows/` 含 `bump-plugin-shas.yml`（自动刷新插件 SHA）、`check-mcp-urls.yml`（校验连接器 URL）、`scan-plugins.yml` + `external-pr-scope-guard.yml`（外部 PR 范围隔离）——把插件生态的「版本锚定 + 安全扫描」工程化。

## 四、应用场景与启发

- **对企业把 LLM 接进实际工作流**：提供了一套标准化范本——「角色 = 技能 + 连接器 + 命令」三分法，比单纯堆 SKILL.md 更接近真实办公流。
- **可借鉴点**：① `cowork-plugin-management` 插件本身就是「生成/定制插件」的元插件，形成自举；② `.github/policy` 的插件安全审计思路，值得任何 Skill / MCP 市场（包括自建 agent 技能库）直接复用。

## 五、源码深度解读（真实片段）

**插件清单极简（sales/.claude-plugin/plugin.json）：**

```json
{
  "name": "sales",
  "version": "2.0.1",
  "description": "Sales skills that work with the tools your team already uses ...",
  "author": { "name": "Anthropic" }
}
```

**技能即 Markdown + frontmatter（bio-research/skills/start/SKILL.md 节选）：**

```markdown
---
name: start
description: Set up your bio-research environment and explore available tools. Use when first getting oriented ...
---

# Bio-Research Start
## Step 1: Welcome
## Step 2: Check Available MCP Servers   # 引导式检查已连接的 MCP
## Step 3: Survey Available Skills
## Step 4: Optional Setup — Binary MCP Servers
## Step 5: Ask How to Help
```

技能文件用 YAML frontmatter 声明触发条件，正文是分步指令——Claude 首次进入角色时自动引导环境 / MCP 连接检查，是「渐进披露 + 引导式上手」的范例。

**安全审计契约（.github/policy/schema.json 节选）：**

```json
{ "required": ["passes","summary","violations","may_make_external_network_calls",
  "may_download_additional_software","hooks","has_broad_scope_hooks",
  "has_undisclosed_telemetry","description_matches_behavior"],
  "properties": {
    "passes": { "type":"boolean", "description":"true only if safe AND no broad-scope hooks AND no undisclosed telemetry AND description matches behavior" },
    "has_broad_scope_hooks": { "type":"boolean" },
    "has_undisclosed_telemetry": { "type":"boolean" },
    "description_matches_behavior": { "type":"boolean" }
  } }
```

把「插件是否偷偷注册了广度钩子 / 外传遥测 / 行为与描述不符」变成可机检字段——任何 Skill 市场都该有这层闸门。

## 六、社区口碑

- 27,415 ⭐ / 3,190 Fork（2026-01 开源，pushed 2026-10-08，非常活跃）。
- 作为 **Anthropic 官方**插件体系，社区关注度与信任度天然高；「纯 Markdown 插件」极大降低了贡献门槛。
- 详细 HN / Reddit 舆情「数据不可用」，但星标增速 + 官方背书已说明需求真实。圈内讨论焦点多在「是否会比社区 Skill 生态更标准化」。

## 七、竞品对比

| 维度 | knowledge-work-plugins | vercel-labs/skills、mattpocock/skills、awesome-claude-skills |
|------|----------------------|-----------------------------------------------------------|
| 背书 | Anthropic 官方 | 社区 / 个人 |
| 定位 | 面向 Claude Cowork，重「连接器接企业 SaaS」 | 偏通用 agent 技能集合 |
| 安全治理 | 内置 policy 审计 + CI 扫描 | 多数无 |
| 定制入口 | 有 `cowork-plugin-management` 元插件 | 各自为政 |

差异化在于：**官方背书 + 把 MCP 连接器当成一等公民 + 内置安全治理**。

## 八、核心研判

这是 Anthropic 把「通用 Claude」推向「垂直工作流」的**官方打法**，信号意义大于代码量。对想做企业内部 AI 助手 / Skill 中台的人，是高参考价值的范本；Apache-2.0 许可，**可商用、可 Fork 定制**。需注意：生态仍早期，部分连接器需自备 API Key，且强绑定 Claude Cowork / Claude Code 运行时。

## 九、关键文件速查

- `README.md` — 插件市场总览与安装方式
- `.claude-plugin/marketplace.json` — 11 个插件的 SHA 聚合清单
- `sales/.claude-plugin/plugin.json` — 极简插件清单范式
- `bio-research/skills/start/SKILL.md` — 引导式技能范例
- `.github/policy/schema.json` — 插件安全审计契约
- `.github/workflows/scan-plugins.yml` — 插件自动扫描流水线
