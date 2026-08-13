# Obsidian Skills 深度调研（kepano/obsidian-skills）

> 调研日期：2026-08-14 ｜ 星标：45,579 ⭐ ｜ 语言：无（技能包，含 Shell/JS）｜ 协议：MIT ｜ 默认分支：main ｜ 创建：2026-01-02

## 一、项目定位（一句话）

kepano/obsidian-skills 是一组**遵循 Agent Skills 规范、让任意兼容 Agent（Claude Code / Codex / OpenCode）学会使用 Obsidian** 的技能包——覆盖 Markdown、Bases、JSON Canvas、CLI 与网页去噪提取（Defuddle）。

## 二、项目亮点（差异化，开篇呈现）

- 📐 **规范兼容、跨 Agent 通用**：遵循 [agentskills.io](https://agentskills.io/specification) 规范，Claude Code / Codex / OpenCode 开箱即用，不被单一 harness 锁定。
- 🧩 **5 个精准技能**：`obsidian-markdown`（OB 风味 MD）、`obsidian-bases`（.base 视图/筛选/公式）、`json-canvas`（.canvas 节点/边/组）、`obsidian-cli`（插件/主题开发）、`defuddle`（网页→干净 MD）。
- 🧹 **Defuddle 去噪提取**：用 kepano/defuddle 把网页 HTML 抽成干净 Markdown，**移除导航/广告/侧栏，显著省 token**——是「省 token 的网页清洗」可复用范式。
- ⚡ **多安装方式**：`/plugin marketplace add`、`` npx skills add ``、手动克隆到 `.claude` / `~/.codex/skills` / `~/.opencode/skills`。
- 👑 **权威作者背书**：kepano 即 Obsidian 创始人，格式与开放标准深度对齐。

## 三、核心架构

仓库极简：`skills/` 下 5 个技能目录，每目录一个 `SKILL.md`（技能说明 + 触发条件 + 操作指引）+ 可选 `scripts/`、`references/`。`obsidian-cli` 技能调用官方 Obsidian CLI；`defuddle` 技能封装 kepano/defuddle 库。外层 `.claude-plugin/` 提供 marketplace 元数据。本质是「**用自然语言技能把 Obsidian 开放格式暴露给 Agent**」。

## 四、应用场景与启发

- **知识管理 Agent 化**：让 Agent 直接读写你的 Obsidian vault（wiki 链接、callouts、properties、Bases 数据库视图）。
- **本地结构化知识库当 Agent 存储**：把个人 vault 当作 Agent 可操作、人类可读的持久记忆层。
- **Defuddle 模式可迁移**：任何「喂给 LLM 的网页」都先用 Defuddle 清洗再送，省 token 且提质量——可复用于 RAG 抓取、 research Agent。
- 💡 **启发**：① 技能包是 Agent 能力分发的标准载体；② 把常用工具的开放格式封装成 SKILL.md，是「工具 Agent 化」最快路径；③ 本地优先知识库（Obsidian）与 Agent 双向打通，是个人 AI 工作流的高价值拼图。

## 五、源码深度解读

### 1. `skills/obsidian-markdown/SKILL.md`
教 Agent 写 Obsidian Flavored Markdown：wikilinks（`[[ ]]`）、embeds、callouts（`> [!note]`）、properties（YAML frontmatter）、OB 特有语法。Agent 据此生成可被 OB 原生渲染的笔记。

### 2. `skills/defuddle/SKILL.md`
把任意网页 URL 经 Defuddle 转为干净 Markdown，去除导航/侧栏/广告/脚本，保留正文。输出直接可作为 Agent 上下文，避免把整页噪声塞进上下文。
```text
# 概念流程
URL → Defuddle.extract() → 干净 Markdown → 送 LLM 上下文（token 显著下降）
```

### 3. `skills/obsidian-cli/SKILL.md`
通过官方 Obsidian CLI 操作 vault：插件/主题开发、命令执行。让 Agent 能「改设置、装插件、跑命令」而不只是读写文件。

## 六、全网口碑

- 发布即获 Obsidian 社区与 Agent Skills 生态关注；趋势榜 45.6k⭐（2026-08）。
- 2026 年是 Agent Skills 爆发年：前有 `anthropics/skills`（165k⭐）、`google/skills`、`` ComposioHQ/awesome-claude-skills ``（策展 1000+）、`github/spec-kit`。本仓库是「垂直工具技能」的代表作。
- MIT 协议，无商用限制，易二次分发。

## 七、竞品对比 + 核心研判

| 维度 | obsidian-skills | anthropics/skills | google/skills | awesome-claude-skills |
|---|---|---|---|---|
| 定位 | Obsidian 垂直 | 官方通用合集 | Google 通用 | 策展清单 1000+ |
| 独特能力 | Defuddle 网页清洗 | 官方权威 | 一键装多 harness | 量大面广 |
| 适用 | 知识管理 Agent | 通用工作流 | 通用工作流 | 探索式 |

- **核心研判**：
  - ✅ 优势：权威作者、规范兼容、Defuddle 去噪独树一帜、MIT 易用。
  - ⚠️ 风险：功能面窄（仅 Obsidian 生态）、`obsidian-cli` 依赖外部 CLI 可用性。
  - 🔮 趋势：技能即产品（skills-as-a-product），垂直工具技能会大量涌现。
  - 💡 启发：把你的核心工具封装成 `SKILL.md`，是让 Agent「会用你的工具」成本最低的方式。

## 八、关键文件路径速查

- `skills/obsidian-markdown/SKILL.md`
- `skills/obsidian-bases/SKILL.md`
- `skills/json-canvas/SKILL.md`
- `skills/obsidian-cli/SKILL.md`
- `skills/defuddle/SKILL.md`
- `.claude-plugin/`（marketplace 元数据）· `LICENSE`（MIT）
