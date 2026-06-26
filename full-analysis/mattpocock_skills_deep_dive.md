# 🔍 mattpocock/skills — 深度调研报告

> **Skills for Real Engineers — 真实工程师的 AI 编程技能仓库** | 141K ⭐ | MIT | 2026-04 开源

---

## 📌 项目定位

mattpocock/skills 是 TypeScript 生态知名开发者 **Matt Pocock**（Total TypeScript 创始人）开源的个人 Claude Code 技能实战集。副标题直白有力：

> **"Skills for Real Engineers. Straight from my .claude directory."**

这不是概念演示或玩具级项目，而是 Matt 本人 **日常使用的 Claude Code 工作流** 的完整开源。项目核心理念是「真实工程师的工程化 AI 编码」，与当时流行的「vibe coding」式无约束生成形成鲜明对照。

24 小时单日暴增 2,507 ⭐ 冲上 GitHub Trending #1，当前累计 141K ⭐。

---

## 🏗️ 核心架构

### 设计哲学：Real Engineering > Vibe Coding

| 失败模式 | 症状 | 解决方案 |
|----------|------|----------|
| 目标失准 | 生成的内容与需求不符 | 结构化 prompt + 分步验证 |
| 输出冗余 | 代码膨胀，包含大量无关内容 | 窄范围 Skill，每文件聚焦一个任务 |
| 代码失效 | 编译通不过、测试跑不过 | 内置 TDD 驱动 |
| 架构腐化 | 长期 AI 生成后代码难以维护 | 持续 refactor Skill 作为护栏 |

### 核心 Skill 集合

| Skill 名称 | 功能 | 定位 |
|-----------|------|------|
| `/grill-me` | 对当前项目进行严格代码审查 | 最热门，替代传统 Review |
| `/tdd` | 测试驱动开发 | 写测试 → 看失败 → 修复循环 |
| `/to-prd` | 将需求转化为 PRD 文档 | 需求对齐 |
| `/git-guardrails` | Git 操作的安全护栏 | 防止误操作 |
| `/explain` | 代码解释 | 代码理解辅助 |
| `/refactor` | 代码重构 | 保持架构整洁 |
| `/commit` | 智能 Commit 生成 | 规范提交 |
| `/review` | 代码审查 | 工程评审 |
| `/test` | 测试生成 | 自动化测试 |

### 兼容性矩阵

| 平台 | 支持状态 |
|------|----------|
| Claude Code | ✅ 原生 100% |
| Claude Apps 网页版 | ✅ |
| Claude API | ✅ |
| Cursor 0.40+ | ✅ |
| Windsurf 1.2+ | ✅ |
| GitHub Copilot | ✅ (通过 skills.sh) |
| Gemini CLI | ✅ |
| Codex CLI | ✅ |

### 文件结构

```
skills/
├── grill-me/         # 代码审查 Skill
│   └── SKILL.md
├── tdd/              # 测试驱动开发 Skill
│   └── SKILL.md
├── to-prd/           # PRD 生成 Skill
│   └── SKILL.md
├── git-guardrails/   # Git 护栏 Skill
│   └── SKILL.md
├── explain/          # 代码解释 Skill
│   └── SKILL.md
└── ... (共 18+ 个)
```

每个 Skill 就是一个 `SKILL.md` 文件，遵循 **Agent Skills 开放标准**，可以跨平台移植。

---

## 💬 社区口碑

| 维度 | 评价 |
|------|------|
| **Star 增长** | 2026-04 开源，4 个月 → 141K ⭐，最高单日增速 2.5K+ |
| **用户评价** | 「AI 编码的**工程规范圣经**」—「终于有人教 AI 写代码而不是 vibe coding」|
| **采用情况** | skills.sh 平台安装量第一，被数千个工程团队采用为标准配置 |
| **与 Supermaven / Copilot 关系** | 不冲突；skills 是工作流规范层，超车的是 AI 补全层 |

### 竞品对比

| 项目 | 核心差异 | 适用场景 |
|------|----------|----------|
| **mattpocock/skills** | 真实工程标准，TDD 驱动，移植开放标准 | 严肃软件工程，追求代码质量 |
| **gstack (Garry Tan)** | 全生命周期角色化团队，23 个斜杠命令 | 快速交付，团队替代 |
| **addyosmani/agent-skills** | 24 个生产级编码 Skills，跨 10+ 平台 | 通用生产编码 |
| **claude-skill-template** | 无预设技能，仅提供注册框架 | 个人定制开发 |

---

## 🧠 核心研判

1. **「反 Vibe Coding」的范式宣言**：mattpocock/skills 的最大价值不是几个 Skill 本身，而是它确立了 **AI 编码也需要工程规范** 这一行业共识。它是 AI 编程从「玩具」走向「工厂」的里程碑。
2. **标准化的力量**：该项目推动了 Agent Skills 开放标准的广泛采纳。每个 Skill 只是一个 `SKILL.md` 文件 + 可选脚本，这种极简设计使得 **Skill 编写 + 分发 + 安装** 的成本趋近于零，这是病毒增长的根本原因。
3. **开发者信用的杠杆**：Matt Pocock 作为 TypeScript 生态的意见领袖，其「个人 .claude 目录」的公开具有极强的示范效应。不止展示了代码，而是展示了一个信赖的工程流程。
4. **生态价值的溢出现象**：项目从独立仓库 → skills.sh 安装平台 → Agent Skills 标准 → 被 10+ 平台兼容，走出了典型的开源项目价值指数增长曲线。
5. **风险**：随着技能数量膨胀，维护和兼容会成为问题。此外，高度模板化的工作流可能不适合创新性（而非工程性）的编程任务。

---

## 🔗 关键链接

- GitHub: https://github.com/mattpocock/skills
- 安装: `npx skills@latest add mattpocock/skills/grill-me`
- 许可证: MIT
- 兼容平台: Claude Code, Cursor, Codex CLI, Gemini CLI, Windsurf
