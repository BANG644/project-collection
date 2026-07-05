# 🔬 alirezarezvani/claude-skills - 全方位深度调研

## 📌 一句话定位

GitHub 上规模最大（337+ / 更新至 354）的跨平台 AI 编码 Agent Skill 合集——覆盖 13 个 AI 编码工具、18 个专业领域，提供从工程到营销、从合规到金融的全栈 Agent Skills，是 Agent Skill 生态的"百科全书级"参考库。

## ⭐ 项目亮点

- **规模之王**：337+ Skill（已更新至 354）覆盖 18 个领域，是所有类似仓库中数量最多的，从 CEO 顾问到混沌工程无所不包
- **13 个 Agent 兼容**：不仅仅支持 Claude Code，还覆盖 Codex、Gemini CLI、Cursor、OpenCode、Windsurf、Pythagora 等——是目前最全的跨平台技能库
- **三层抽象**：Skills（执行技能）/ Agents（复合角色）/ Personas（行为风格）——从原子指令到复杂角色扮演的分层架构
- **零依赖 Python CLI**：593 个自包含 Python CLI 工具，每个 Skill 都附带可独立执行的命令行工具
- **质量管理严格**：引入 Matt Pocock 的 100 行 SKILL.md 上限规范，强制技能精简；Active 开发中的 v2.7 正在重构 top-20 技能

## 🏗️ 项目架构全景

### 三层抽象设计

```
┌─────────────────────────────────────┐
│           Personas (行为层)           │  ← 定义"说话/行为风格"
├─────────────────────────────────────┤
│     Agents (复合角色层 / 战术层)       │  ← 组合多个 Skill 的复合角色
│     eg. CEO Advisor, CISO, ...      │
├─────────────────────────────────────┤
│      Skills (执行层 / 原子层)          │  ← 最小可执行 Skill 单元
│     354 × SKILL.md + Python CLI     │
└─────────────────────────────────────┘
```

### 目录结构（以 engineering/skills/ 为例）

```
├── .claude/                      # Claude Code 原生配置
│   ├── commands/                 # 自定义命令
│   └── settings.json
├── .codex/                       # Codex 适配
│   ├── skills-index.json         # 全量技能索引
│   └── skills/                   # Codex 格式的技能
├── .cursor/                      # Cursor 适配
├── engineering/
│   ├── skills/                   # 工程技能（API 设计、代码审查、架构等）
│   ├── engineering-team/         # 团队角色（资深前端/后端/运维等）
│   └── references/               # 技术参考
├── marketing-skill/
├── product-skill/
├── compliance-skill/
├── commercial-finance/
├── c-level-agents/               # C 级顾问 Agent
├── research/                     # 研究技能
├── business-operations/          # 业务运营
└── daily-productivity/           # 日常效率
```

### 技能的典型 SKILL.md 结构

每个 SKILL.md 遵循 frontmatter + 执行指令的标准格式：

```markdown
---
name: api-design-reviewer
description: Review API designs for REST/gRPC/GraphQL consistency
author: alirezarezvani
tags: [engineering, api, design-review]
---

You are an API design reviewer...

## Workflow
1. Parse the API specification
2. Check RESTful naming conventions
3. Validate error handling patterns
4. Review pagination and rate limiting
5. Generate review report
```

## 💡 应用场景与启发

### 典型使用场景

| 领域 | 代表技能 | 典型输出 |
|------|---------|---------|
| 工程 | api-design-reviewer, code-reviewer | API 审查报告、代码质量评分 |
| 营销 | aeo, ad-creative, seo-auditor | 营销策略、广告创意 |
| 安全 | ai-security, ciso-advisor, security-scan | 安全审计报告 |
| 产品 | agile-product-owner, board-deck-builder | 产品路线图、董事会演示 |
| 财务 | cfo-advisor, channel-economics | 财务分析 |
| C-Level | ceo-advisor, coo-advisor | 战略建议 |

### 跨平台适配的策略启发

claude-skills 的跨平台策略值得关注：它不是为每个 Agent 创建独立技能，而是**统一维护一个全量技能库，然后通过适配层（.claude/、.codex/、.cursor/）做格式转换**。

`.codex/skills-index.json` 包含了所有技能的统一索引，而 `.claude/commands/` 则注册了 Claude Code 特有的自定义命令——这种"一次维护，多平台发布"的策略是 Agent Skill 分发的最佳实践。

### 100 行 SKILL.md 上限的意义

v2.7 引入了 Matt Pocock 提出的 **100 行 SKILL.md 上限**（Issue #655），这是一个重要的设计决策：

- 强制技能作者提炼核心流程，把参考资料外移到 `references/`
- 保证 SKILL.md 对 Agent 的可消化性——长文档对上下文窗口压力大
- 为技能质量设立了可量化的门槛——不是字数多就等于好

## 🧠 核心源码解读（克制代码量）

### 跨平台分发机制

项目的核心创新之一是 `.codex/skills-index.json`——一个全量技能的统一索引文件，格式如下：

```json
{
  "skills": [
    {
      "id": "api-design-reviewer",
      "path": "engineering/skills/api-design-reviewer",
      "platforms": ["claude", "codex", "cursor", "gemini-cli"],
      "description": "Review API designs for consistency"
    }
  ]
}
```

这个索引让各个 Agent 平台可以快速扫描可用技能，而不需要遍历整个文件树。这是一个"元数据先行"的设计模式——任何大规模技能库都应该考虑类似的索引机制。

### 自包含 Python CLI

每个技能目录下的零依赖 Python 脚本（593 个总计），设计哲学：

```python
#!/usr/bin/env python3
"""Self-contained CLI tool — no pip install needed"""
import json, sys

def main():
    data = json.load(sys.stdin)
    # ... 技能执行逻辑
    print(json.dumps(result))

if __name__ == "__main__":
    main()
```

这种"stdin/stdout JSON 管道"模式确保了每个技能可以独立执行、通过管道链接——这是一种 Unix 哲学在 Agent Skill 领域的应用。

## 🌐 全网口碑画像

### 好评共识

- **"Skill 的百科全书"** —— 社区公认所有 Skill 仓库中覆盖面最全、最广
- **"系统化 Agent 技能获取方式"** —— 按领域/角色/平台分类，查找效率远高于零散搜索
- **"对新手友好"** —— 完善的配置文档和快速开始指南

### 差评共识 & 争议

- **质量不均**：337 个 Skill 中部分可能质量参差——代码审查/API 设计等工程技能的深度明显高于"CEO 顾问"类角色技能
- **维护负担**：社区质疑 337+ 个技能的长期维护可行性，部分技能可能随着时间变得过时
- **信息过载**：对新手来说，"337 个技能从哪开始"是一个真实的入门障碍

### 社区参与度

Issue 活跃度中等（10 个开放 Issue），但讨论质量较高——特别是关于 100 行 SKILL.md 上限的讨论（#655）体现了维护者对质量的追求，有来自维护者的详细分阶段重构计划。

## ⚔️ 竞品对比

| 维度 | claude-skills | marketingskills | phuryn/pm-skills | addyosmani/agent-skills |
|------|--------------|----------------|-----------------|----------------------|
| 规模 | **354** ⭐ | 45+ | 100+ | 30+ |
| 领域覆盖 | **18** 个 | 1 个（营销） | 1 个（PM） | 1 个（工程） |
| 跨平台 | **13** 个 | 3 个 | 1-2 个 | 1-2 个 |
| 质量体系 | 100-line 上限 | evals + CI | 基础 CI | CI |
| Python CLI | 593 个 ✅ | 无 | 无 | 无 |
| 适合人群 | "全栈"AI 使用者 | 营销专精 | PM 专精 | 工程专精 |
| Stars | 20,488 | 36,374 | 17,514 | 64 |

## 🎯 核心研判

### 项目优势

- **无与伦比的规模和覆盖面**——354 个技能、18 个领域的广度是任何竞品无法比拟的
- **跨平台兼容策略领先**——同时支持 13 个 AI 编码 Agent，是真正的"一次编写，到处运行"
- **成熟的质量控制**——100 行 SKILL.md 上限、零依赖 Python CLI、v2.7 主动重构，体现了长期的维护决心
- **三层抽象创新**——Skills/Agents/Personas 的分层设计为复杂 Agent 行为建模提供了框架

### 项目风险

- **质量一致性挑战**——数量膨胀下的质量一致性是最大隐患；某些"顾问类"技能的价值可能不如工程技能
- **平台规范变化风险**——13 个 Agent 平台各自更新规范，兼容性维护成本会持续上升
- **生态定位模糊**——是"Skill 分发市场"还是"个人技能集合"？如果是前者，需要更完善的市场机制

### 适用场景

✅ 需要在多个 Agent 平台使用统一技能库的跨平台开发者
✅ 需要覆盖多个专业领域的"全能"Agent 技能需求
✅ 研究各种 Agent Skill 格式和最佳实践
✅ 需要快速搭建 Agent 能力原型的开发团队

❌ 寻求深度垂直领域专业技能的营销/PM 专精用户（marketingskills/pm-skills 更适合）
❌ 不需要跨平台兼容的单一 Agent 用户（直接使用对应平台的技能格式更高效）
❌ 对技能质量一致性要求极高的关键任务场景

### 趋势判断

**稳定增长期** ➡️ —— 20K⭐ 后增长趋于平稳。该项目的真正价值不在于 Star 数增长，而在于它作为"Agent Skill 生态的基础设施"的定位。随着 Agent 生态持续扩张，这个索引式技能库的战略价值只会增加。

## 📂 关键文件路径速查

| 文件 | 说明 |
|------|------|
| `.codex/skills-index.json` | 全量技能统一索引（元数据核心） |
| `.claude/commands/` | Claude Code 自定义命令注册 |
| `.claude/settings.json` | Claude Code 全局配置 |
| `engineering/skills/api-design-reviewer/SKILL.md` | API 设计审查参考实现 |
| `c-level-agents/ceo-advisor/SKILL.md` | CEO 顾问 Agent 示例 |
| `daily-productivity/` | 日常效率技能集合 |
| `business-operations/` | 业务运营技能集合 |
