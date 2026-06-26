# ⚙️ addyosmani/agent-skills — Production-Grade Engineering Skills for AI Coding Agents

> **仓库:** [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills)
> **Stars:** 64,035 ⭐（本周 +7,170）
> **语言:** Shell / Markdown
> **许可:** —
> **关键词:** AI coding agent skills, Claude Code, Cursor, Codex, Gemini CLI, software engineering workflow

---

## 项目定位

Addy Osmani（Google Chrome 团队）出品的 **生产级 AI 编码 Agent 技能集**。将资深软件工程师的工作流、质量门禁和最佳实践编码为结构化 Skills（纯 Markdown），使得 AI Agent 在每个开发阶段都能一致遵循。

核心理念：**不是让 Agent 更聪明，而是让它像高级工程师一样思考和行动。**

---

## 架构与工作流

```
   DEFINE    PLAN     BUILD     VERIFY    REVIEW    SHIP
  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐
  │ Idea │→│ Spec │→│ Code │→│ Test │→│ QA   │→│ Go   │
  │Refine│ │ PRD  │ │ Impl │ │Debug │ │ Gate │ │ Live │
  └──────┘ └──────┘ └──────┘ └──────┘ └──────┘ └──────┘
   /spec   /plan   /build  /test   /review  /ship
```

**7 个斜杠命令** 对应开发生命周期各阶段，每个命令自动激活合适的 Skills：

| 阶段 | 命令 | 核心原则 |
|------|------|----------|
| 定义需求 | `/spec` | 先写规范再写代码 |
| 规划实现 | `/plan` | 小、原子化的任务拆解 |
| 增量构建 | `/build` | 一次一个垂直切片 |
| 验证质量 | `/test` | 测试即证明 |
| 合并前审查 | `/review` | 提升代码健康度 |
| 简化代码 | `/code-simplify` | 清晰胜于技巧 |
| 生产发布 | `/ship` | 快即是安全 |

---

## 24 个 Skills 清单

### 元技能

| Skill | 作用 |
|-------|------|
| **using-agent-skills** | 将用户请求路由到正确的 Skill 工作流，定义共享操作规则 |

### 需求定义阶段

| Skill | 作用 |
|-------|------|
| **interview-me** | 逐一提问式访谈，挖掘用户真实需求（直到 95% 置信度） |
| **idea-refine** | 结构化发散/收敛思考，将模糊想法转为具体方案 |
| **spec-driven-development** | 编写 PRD，覆盖目标/命令/结构/代码风格/测试/边界 |

### 规划阶段

| Skill | 作用 |
|-------|------|
| **planning-and-task-breakdown** | 将规范拆解为小、可验证的任务，标定依赖顺序和验收标准 |

### 构建阶段

| Skill | 作用 |
|-------|------|
| **incremental-implementation** | 薄垂直切片实现 — 实现、测试、验证、提交 |
| **test-driven-development** | Red-Green-Refactor，测试金字塔（80/15/5），Beyonce Rule |
| **context-engineering** | 给 Agent 喂正确信息 — 规则文件、上下文打包、MCP 集成 |
| **source-driven-development** | 每个框架决策都基于官方文档，标注来源 |
| **doubt-driven-development** | 对抗性推理，发现架构假设中的弱点和隐藏风险 |

### 更多 Skills（部分）

| Skill | 作用 |
|-------|------|
| api-and-interface-design | API/接口设计指南 |
| frontend-ui-engineering | 前端 UI 工程化 |
| data-modeling | 数据模型设计 |
| backend-engineering | 后端工程化 |
| error-handling | 错误处理规范 |
| debugging | 调试方法论 |
| refactoring | 重构策略 |
| security-review | 安全审查 |
| performance-optimization | 性能优化 |
| code-review | 代码审查清单 |
| documentation | 文档编写规范 |
| devops-and-infrastructure | DevOps 与基础设施 |

---

## 平台兼容性

| 平台 | 安装方式 |
|------|----------|
| **Claude Code** ✅ | `/plugin marketplace add addyosmani/agent-skills` 或本地 `--plugin-dir` |
| **Cursor** ✅ | 复制 SKILL.md 到 `.cursor/rules/` |
| **Gemini CLI** ✅ | `gemini skills install` |
| **Copilot** ✅ | Copilot 指令文件 |
| **Codex CLI** ✅ | 纯 Markdown，任何 Agent 兼容 |
| **Antigravity CLI** ✅ | `agy plugin install` |
| **Windsurf** ✅ | 规则配置 |
| **OpenCode** ✅ | AGENTS.md + skill 工具 |
| **Kiro IDE** ✅ | `.kiro/skills/` 目录 |
| **Any Agent** ✅ | 纯 Markdown，通用兼容 |

---

## 核心创新点

1. **不锁定平台**：纯 Markdown 格式，理论上兼容所有 Agent
2. **反合理化表**：每个 Skill 内置反自我合理化机制，防止 Agent 跳过验证步骤
3. **自动化构建模式**：`/build` 一次批准后自动运行全流程（测试驱动 + 独立提交），遇失败自动暂停
4. **情境自动触发**：设计 API 时自动激活 api-design 技能，构建 UI 时自动激活 frontend 技能
5. **权威优先**：`source-driven-development` 要求所有框架决策引用官方文档

---

## 社区与生态

- **Stars**: 64K ⭐（本周 +7,170），高热度持续增长
- **作者**: Addy Osmani（Google Chrome 团队，知名性能优化专家）
- **适配生态**: 覆盖所有主流 AI 编码工具
- **更新频率**: 积极维护，持续新增 Skills
- **文档**: 完整的平台特定安装文档（cursor-setup、gemini-setup 等）

---

## 竞品对比

| | addyosmani/agent-skills | anthropics/skills | Claude Code 内置 |
|---|------------------------|-------------------|------------------|
| **Skill 数量** | 24 个，覆盖全生命周期 | 有限 | 内置基础能力 |
| **跨平台兼容** | ✅ 10+ Agent 平台 | ❌ Claude Code 专有 | ❌ Claude Code 专有 |
| **斜杠命令** | ✅ 7 个命令映射阶段流程 | ⚠️ 部分支持 | ✅ 内置命令 |
| **文档完备性** | ✅ 专门文档目录 | ✅ 依赖 Anthropic 文档 | ✅ 官方文档 |
| **社区热度** | ⭐ 64K Stars | ⭐ 12-15K | — |
| **自动化构建** | ✅ /build 全自动 | ❌ | ❌ 半自动 |

---

## 核心研判

| 维度 | 评价 |
|------|------|
| **实用性** | ⭐⭐⭐⭐⭐ 直接可以集成到日常开发流程中 |
| **覆盖完整性** | ⭐⭐⭐⭐⭐ 从需求定义到发布的全生命周期覆盖 |
| **平台兼容** | ⭐⭐⭐⭐⭐ 10+ Agent 平台，极致兼容 |
| **社区影响力** | ⭐⭐⭐⭐⭐ 64K ⭐，Addy Osmani 品牌背书 |
| **创新性** | ⭐⭐⭐⭐ 将工程最佳实践编码为 Agent 可执行的 Skill |

**结论：AI 编码 Agent 领域必装 Skill 集。** Addy Osmani 将其数十年工程经验代理化为可重复、可验证、跨平台的 Skills。对使用 Claude Code、Cursor 或任何 AI 编码 Agent 的开发者来说，这是最值得安装的工程化增强包之一。

---

## 关键文件路径

| 路径 | 说明 |
|------|------|
| `skills/using-agent-skills/SKILL.md` | 元技能入口 |
| `skills/spec-driven-development/SKILL.md` | 规范驱动开发 |
| `skills/planning-and-task-breakdown/SKILL.md` | 任务拆解 |
| `skills/incremental-implementation/SKILL.md` | 增量实现 |
| `skills/context-engineering/SKILL.md` | 上下文工程 |
| `docs/cursor-setup.md` | Cursor 安装指南 |
| `docs/gemini-cli-setup.md` | Gemini CLI 安装指南 |

---

*调研日期: 2026-06-21 02:00 CST*
