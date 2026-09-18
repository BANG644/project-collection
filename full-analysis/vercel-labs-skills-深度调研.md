# 🔬 vercel-labs/skills - 全方位深度调研

## 📌 一句话定位
`vercel-labs/skills` 是 Vercel Labs 开源的 **Agent Skills 生态 CLI（`npx skills`）**——它把"可复用的 agent 指令包（SKILL.md）"做成跨 75+ 编码 agent 的安装/发现/更新层，被社区称为"AI agent 能力的 npm"。

## ⭐ 项目亮点
- **跨 agent 可移植性**：一个 `npx skills add owner/repo` 自动把技能装到 Claude Code / Cursor / Codex / Copilot / OpenClaw 等 75+ agent 各自的 `skills/` 目录（README 的 supported-agents 表），团队再不用为每个 agent 重复配置。
- **开放规范而非 Vercel 私有**：技能遵循公开的 [Agent Skills 规范](https://agentskills.io)——一个 `SKILL.md`（YAML frontmatter + Markdown 指令），无构建、无编译、无供应商锁定。Vercel 只是"发行层"。
- **发现机制双层**：常规按"容器目录向上最多 3 层"的 bounded walk（flat / `skills/<cat>/<name>` / 两级分类），浅层 `SKILL.md` 遮蔽深层；另支持 `.claude-plugin/marketplace.json` 清单声明，突破深度限制。
- **安装即 symlink 或 copy**：默认用符号链接指向 canonical 副本（单一真相、易更新），遇到不支持 symlink 的平台再 `--copy`；`--global` 装到用户目录、`-a` 指定 agent、`--skill` 精装。

## 🏗️ 项目架构全景
### 仓库结构（main 树）
- `src/` + `packages/`：CLI 实现（TypeScript，pnpm workspace）
- `skills/`：示例/自带的技能容器（如 `find-skills/SKILL.md`）
- `scripts/`、`tests/`、`AGENTS.md`、`build.config.mjs`：工程化与贡献指南
- **注意**：真正的"技能内容"在姊妹仓库 `vercel-labs/agent-skills`（独立发布），本仓库是**工具链**。

### 命令面
`add`（安装）/`use`（不安装只生成 prompt）/`list`/`find`（fzf 式搜索）/`remove`/`update`/`init`（生成 `SKILL.md` 模板）。`skills use` 把选中技能写入临时目录并只打印 prompt，配合 `--agent` 可直接拉起对应 agent。

### 源码解析能力
- 私有库/多源认证回退：HTTPS → `gh` clone → SSH；token 用 `gh api` 返回、绝不打印或读入 Node 进程（README 安全段）。
- 下载上限：单文件 10 MiB、解压 25 MiB、压缩包 1000 文件，可用 `SKILLS_*` 环境变量放宽（仅信任源时）。

## 💡 应用场景与启发
- **给 agent 装"专业能力包"**：如 `react-best-practices`（40+ 规则 8 类）、`web-design-guidelines`（100+ 可访问性/动效/暗色规则）、`vercel-deploy-claimable`——把团队最佳实践沉淀为可版本化、可审计的指令块。
- **"npm 化 agent 知识"范式**：和 MCP（连工具）、Skills 目录（分发层）一起，构成 agent 从"聪明补全"到"可扩展开发平台"的基础设施层（arkin-dev 博客）。
- **对自研 agent 系统的启发**：本仓库调研者的 WorkBuddy 专家/skill 体系与该规范高度同构——可参考其"深度 3 的目录遍历 + frontmatter 仅解析 name/description 的渐进披露（progressive disclosure）"来优化本地 skill 发现。

## 🧠 核心源码解读
### 1. SKILL.md 格式（开放规范）
```markdown
---
name: my-skill
description: 何时用、做什么（第三人称、聚焦触发条件）
---
# My Skill
## When to Use
## Steps
```
`metadata.internal: true` 可隐藏技能（仅 `INSTALL_INTERNAL_SKILLS=1` 可见），用于 WIP/内部工具。

### 2. 渐进披露发现
agent 启动时**只解析 frontmatter 的 name+description**；任务匹配后再加载完整 `SKILL.md` 及其 `scripts/`、`references/`、`assets/`——用最小上下文换最大可扩展性。

### 3. 多 agent 路径映射表
CLI 内置一张"agent → 项目路径 / 全局路径"表（如 `.claude/skills/`、`.cursor/skills/`、`.agents/skills/`、`.codebuddy/skills/`），安装时自动落位，这是"装一次、处处用"的关键。

## 📐 架构决策与设计哲学
- **规范开放、实现收敛**：规范归 agentskills.io，Vercel 只做最顺手的 CLI，避免重蹈"每家 agent 私有技能格式"的碎片化。
- **Symlink 优先**：单一真相、更新零成本，而非每 agent 一份拷贝漂移。
- **安全默认**：token 不进进程内存、下载有硬上限、私有库复用既有 Git 凭证。

## 🌐 全网口碑画像
- **好评共识**：被视为"agent 能力的 npm"（arkin-dev、thetechbriefs）；跨 agent 可移植解决了"换 agent 从零配"的痛点；`react-best-practices`/`web-design-guidelines` 被赞"把十年优化规则结构化"。
- **差评共识**：生态仍早期；技能质量参差、需要甄别；部分 agent（如 Kiro/Cursor 旧版）对 `allowed-tools`/Hooks 支持不一致（README 兼容表）。
- **争议焦点**：Skills（Markdown 知识）vs MCP（功能工具）vs Plugin（打包）的边界；Vercel 是否借规范"收编"生态。
- **增长信号**：发布即 15.5k⭐ climbing（arkin-dev），`skills.sh` 目录已聚合 Microsoft Azure（4.4M+ 安装）等大量社区技能。

## ⚔️ 竞品对比
| 维度 | vercel-labs/skills | skillsmp.com | Claude Code 原生 | Antigravity/插件市场 |
|------|-------------------|-------------|-----------------|---------------------|
| 定位 | 跨 agent 安装 CLI | 7万+ 技能目录 | 单 agent 内置 | 插件捆绑（skill+mcp+agent）|
| 规范 | 开放 Agent Skills | 自索引 GitHub | 自有 | 自有/兼容 |
| 可移植 | 75+ agent | 依赖各 agent 支持 | 仅 Claude | Google 系 |

## 🎯 核心研判
- **优势**：开放规范 + 最大 agent 覆盖面 + Vercel 品牌背书，最有可能成为"技能分发标准层"。
- **风险**：规范控制权与生态主导权仍在早期博弈；技能质量无强制审核。
- **适用**：多 agent 团队、想把最佳实践模板化复用的开发者；**不适用**只需单一 agent 且不愿引入额外抽象的用户。
- **趋势**：上升期，npm 式增长曲线明显，与 MCP 共同构成 agent 基础设施。

## 📂 关键文件路径速查
- `README.md` — 完整命令、supported-agents 表、skill 发现规则
- `skills/find-skills/SKILL.md` — 自带示例技能
- `src/` + `packages/` — CLI 实现（TS）
- `AGENTS.md` — 贡献指南
- 关联仓库 `vercel-labs/agent-skills` — 官方策展技能内容
- 规范站 `https://agentskills.io`、目录 `https://skills.sh`
