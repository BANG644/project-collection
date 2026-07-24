# 🔬 ComposioHQ/awesome-claude-skills — Claude Skills 千库策展清单

> **调研日期**：2026-07-26 | **数据来源**：GitHub API + README 走读
> **实时数据**：⭐ 69,947（Trending +662/日）| 协议 Apache-2.0 | 语言 Markdown/Python 混合 | 组织 Composio

## 一、项目定位（一句话）

一份 **1000+ 生产级 Claude Skills / 插件策展清单**，覆盖 Document / Dev / Data / Business / Writing / Media / Productivity / Collab / Security / SaaS 自动化十大类，定位是「AI Agent 技能黄页」而非代码库。

## 二、项目亮点（3-5 条差异化，开篇呈现）

- 📚 **广度碾压**：1000+ Skills + 78 个 SaaS App 的 Composio 预构建自动化技能（CRM/PM/沟通/邮件/DevOps/存储/表格/日历/社交/营销/支持/电商/设计/分析/HR/自动化平台/会议），单一清单难以匹敌。
- 🧩 **清晰的三层模型**：README 明确界定 **Skills ≠ MCP ≠ Tools**——MCP 管「接入」（auth/transport/发现）、Tools 管「动作」、Skills 管「行为/工作流」，三者生产环境协同。
- ⚡ **渐进式加载（架构基石）**：agent 启动时仅看每个 skill 的 `name+description`（约 100 token），命中任务才加载完整 `SKILL.md`（<5000 token），`scripts/references` 再按需——单 agent 可托管数百技能而不爆上下文。
- 🔌 **紧跟开放标准**：对齐 Anthropic 2025-10 推出的 Skills 开放标准，覆盖 Claude.ai / Claude Code / Claude API / OpenAI Codex / Cursor / Gemini CLI / Antigravity / Windsurf。
- 🛠️ **自带可运行子技能**：`./skill-creator/`、`./mcp-builder/`、`./connect/`（连 1000+ App 的 Composio 插件）、`./changelog-generator/` 等是仓库内真实 skill 目录，不只是外链堆砌。

## 三、核心架构

仓库主体是 **Markdown 索引 + 少量可运行 skill 子目录**（并非编译型代码）：

```
awesome-claude-skills/
├── README.md                 # 分类索引 + Skills 规范说明
├── CONTRIBUTING.md           # 收录标准 / PR 流程
├── skill-creator/            # 可运行：教你写 skill
├── mcp-builder/              # 可运行：教建 MCP server
├── connect/                  # 可运行：连 Composio 1000+ App
├── changelog-generator/       # 可运行
└── ...（大量外链条目）
```

分类树（来自 README 目录）：Document Processing / Development & Code Tools / Data & Analysis / Business & Marketing / Communication & Writing / Creative & Media / Productivity & Organization / Collaboration & Project Management / Security & Systems / App Automation via Composio。

每个外部 skill 的标准形态：一个文件夹 + `SKILL.md`（YAML frontmatter 含 `name`/`description`）+ 可选 `scripts/`、`templates/`、`resources/`。

## 四、应用场景与启发

- **选型检索入口**：要找「XX 场景有没有现成 Claude skill」时，先扫这份清单避免重复造轮子。
- **自建 skill 模板**：直接复用 README 的 *Basic Skill Template* 与「When to Use」显式触发条件写法——好的 skill 必须有清晰触发边界。
- **工作流设计框架**：其「MCP（接入）/ Tools（动作）/ Skills（行为）」三层分离，是设计 agent 系统时的好心智模型。
- **Composio 集成套路**：`./connect/` 展示「skill 描述 how，MCP Gateway 提供带鉴权的 tools」的分工，可作为私有 agent 接入企业 SaaS 的参考。

## 五、源码解读（核心模块精读）

这不是代码库，真正值得读的「源码」是 **SKILL.md 规范本身**（README 的 *Basic Skill Template*）：

```markdown
---
name: my-skill-name
description: A clear description of what this skill does and when to use it.
---
# My Skill Name
## When to Use This Skill
- Use case 1 / 2 / 3
## Instructions
[Detailed instructions for Claude on how to execute this skill]
```

**关键架构洞察**：渐进式加载是 Skills 生态能规模化的根本。若每次会话都加载全部 skill 正文，上下文会瞬间爆炸；而「名称+描述常驻、正文命中才载」使「技能库」在成本上可行。任何自建 skill 体系都应照搬这一分层。

## 六、全网口碑

- Composio 官方维护，背靠其商业产品 **MCP Gateway**（1000+ 集成、团队鉴权、审计日志），清单本身承担引流角色。
- Trending 日增 ~662⭐，增长强劲；社区对其「列表越来越长、外链质量参差」有讨论，使用者普遍会自行甄别。
- 与 `anthropics/skills`（官方规范参考）、`mattpocock/skills`（个人实战）形成互补生态。

## 七、竞品对比 + 核心研判

| 维度 | awesome-claude-skills | mattpocock/skills | anthropics/skills | VoltAgent/awesome-openclaw-skills |
|------|----------------------|-------------------|-------------------|-----------------------------------|
| 量级 | 1000+ | 数十（个人 .agents） | ~30（官方示例） | OpenClaw 生态 |
| 定位 | 广度策展 + Composio 集成 | 真实工程师工作流 | 官方规范参考 | OpenClaw 技能集散 |
| 商业化 | Composio 引流 | 个人 | Anthropic | VoltAgent |
| 质量保障 | 收录标准 + 社区 PR | 作者自用 | 官方 | 社区 |

**核心研判**：
- ✅ **优势**：覆盖面无人能及，是「找技能」最高效的单一入口；规范说明质量高。
- ⚠️ **风险**：本质是链接索引，信息密度低，外链 skill 质量需自担；随规模扩大策展质量有下滑趋势。
- 🎯 **启发**：把它当「检索黄页」而非深度资料库；真正落地时优先看其自带的可运行子技能（skill-creator 等）。护城河不在清单本身，而在 Composio 的 MCP Gateway 变现闭环。

## 八、关键文件速查

- `README.md` — 分类索引 + Skills 三层模型 + SKILL.md 模板
- `CONTRIBUTING.md` — 收录标准与质量门禁
- `./skill-creator/`、`./mcp-builder/`、`./connect/`、`./changelog-generator/` — 仓库内真实可运行 skill
- GitHub：`https://github.com/ComposioHQ/awesome-claude-skills`
