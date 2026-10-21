# wshobson/agents 深度调研

> 调研日期：2026-10-22 ｜ 星标：41,442 ⭐ ｜ 语言：Python ｜ 许可：MIT ｜ 默认分支：main
> 定位：**一套跨 7 个 AI 编码 harness 的 agent / skill / command 插件市场与适配框架 —— 单一 Markdown 源，多 harness 产物**

## 一、项目亮点（差异化）

1. **单一真源、七端同构**：94 个插件（92 本地 + 2 外部）含 202 agents / 185 skills / 105 commands，全部以 Claude Code 原生插件格式的 Markdown 维护一份；通过适配层生成 Claude Code、OpenAI Codex、Cursor、OpenCode、Antigravity CLI、GitHub Copilot、Pi 共 7 种 harness 的产物。
2. **Adapter 框架做"翻译"而非"重写"**：模型别名（`opus`/`sonnet`/`haiku`/`fable`/`inherit`）映射到各 harness 的模型设置，工具名与权限按 harness 能力翻译，skill 体受 8 KB（Codex 硬上限）体积约束自动裁剪——作者无需为每个工具写一份。
3. **渐进披露贯穿到底**：根 `AGENTS.md` 限 ~150 行、skill 体限 ~8 KB，细节下沉到 `docs/` 与 `references/details.md`，按需加载而非预注入。
4. **机械式校验带修复提示**：`make validate` / `make garden` / `plugin-eval` 的每个 lint/校验发现都附带可直接套用的修复字符串，遵循 OpenAI harness-engineering 模式。

## 二、核心架构

- **Source of Truth**：`plugins/<name>/` 下维护源文件（`.claude-plugin/plugin.json` + `agents/*.md` + `commands/*.md` + `skills/<n>/{SKILL.md,references/,assets/}`）。生成物（`.codex/`、`opencode/`、`copilot/`、`antigravity/`、`pi/`）由 adapter 产出并 gitignore；只有少量原生注册表（`.agents/plugins/marketplace.json`、`.cursor-plugin/`、`plugins/*/.codex-plugin/plugin.json`）被提交，且只指向源 `plugins/`。
- **唯一上下文文件**：根 `AGENTS.md` 是唯一手写的上下文文件；`CLAUDE.md` 是其 symlink，Codex/Cursor/OpenCode/Copilot/Pi 原生读取 `AGENTS.md`。
- **适配层**：`tools/adapters/` 是每-harness 适配框架——`base.py`（解析器 + `HarnessAdapter` ABC + 辅助）、`capabilities.py`（能力矩阵，被每个 adapter 消费）、`codex.py`/`cursor.py`/`opencode.py`/`antigravity.py`/`copilot.py`/`pi.py`（各自生成器）、`cursor_rules/`（手搓 `.mdc`）。

## 三、应用场景与启发

- **给自己维护"跨 harness 的 agent/skill 资产"提供范本**：不要为每个编码工具写一份 skill，而是写一份"便携 Markdown"，用 adapter 生成各端产物。这与用户 WorkBuddy skill 体系（SKILL.md 开放标准、`npx skills` 分发）同构，是可直接借鉴的工程范式。
- **多 harness 团队落地**：在一个组织内混合使用 Claude Code / Codex / Cursor / Copilot 时，用一份插件源统一治理 agent 行为、命令与 hook，避免各端配置漂移。
- **"渐进披露 + 体积上限"纪律**：对长 skill 体（>8KB）自动拆分引用文件，是应对 Codex 等硬限制的成熟做法，写自有 skill 时应复用。

## 四、源码深度解读

**1) `tools/adapters/base.py` —— 无外部依赖的容错 frontmatter 解析器**
仓库刻意不引入 YAML 库，自己实现 `parse_frontmatter(content) -> (fields, body)`，兼容标量、inline/block 列表、一级映射、`>`/`|` 块标量与 2 空格续行；并定义 `HarnessAdapter` ABC 作为所有 per-harness 生成器的基类。关键片段：

```python
def parse_frontmatter(content: str) -> tuple[dict, str]:
    """Return (fields, body). Tolerant YAML-ish parser; no external dep.
    Supports: scalar / inline+block lists / one-level mappings /
    YAML block scalar `>` `|` / 2-space continuation."""
    fields: dict = {}
    if not content.startswith("---"):
        return fields, content
    end = content.find("\n---", 3)
    if end == -1:
        return fields, content
    # ...逐行解析 current_key / in_list / in_block_scalar...
```

**2) `tools/adapters/capabilities.py` —— 能力矩阵**
消费方是每一个 adapter：它声明各 harness 支持的模型别名、工具权限、hook、安装差异，adapter 据此把源里的 `opus`/`inherit` 等别名与权限翻译成目标 harness 的设置（部分 `inherit` 有固定默认值）。

**3) `plugins/python-development/.claude-plugin/plugin.json` —— 插件清单**
极简结构，仅为市场与生成器提供元数据：

```json
{
  "name": "python-development",
  "version": "1.2.3",
  "description": "Modern Python development with Python 3.12+, Django, FastAPI, ...",
  "author": { "name": "Seth Hobson", "email": "seth@major7apps.com" },
  "license": "MIT"
}
```

## 五、社区口碑

- 41.4k ⭐，Star History 曲线陡峭增长（2026 年快速起量）；README 与 `docs/` 极其详尽，含能力矩阵、安装路由、eval 指南。
- 遵循 agentskills.io 开放标准，`gh skill` / `npx skills` 均可免克隆安装单个 skill；社区采用"原生市场注册表指向源"的轻量分发模式。

## 六、竞品对比 + 核心研判

| 项目 | 覆盖 harness | 核心差异 |
|---|---|---|
| **wshobson/agents** | 7（最广） | 含 adapter 生成层，单一源多端产物 |
| anthropics/claude-plugins-official | Claude 生态 | 官方插件市场，不跨 harness |
| vercel-labs/skills / android/skills | 单/少 harness | 厂商按场景发 skill，无生成框架 |
| awesome-opencode | 列表型 | 策展合集，非工程化分发 |

**研判**：在"skill 作为一等分发格式"的趋势里，这是社区侧**覆盖 harness 最广、且带真实 adapter 生成层**的最完整实践，对多 harness 团队有标杆价值。主要风险是维护成本随 harness 数量近似线性增长、生成物与源可能漂移（用 `make garden` 漂移检测缓解）；LLM judge / Monte Carlo 评分层为实验性、未对齐人工标签，引用其分数需打折。

## 七、关键文件速查

- `plugins/` —— 94 个插件的**单一真源**（agents/skills/commands）
- `tools/adapters/base.py` —— `HarnessAdapter` ABC + 容错 frontmatter 解析
- `tools/adapters/capabilities.py` —— 各 harness 能力矩阵
- `tools/adapters/{codex,cursor,opencode,antigravity,copilot,pi}.py` —— 每端生成器
- `ARCHITECTURE.md` / `docs/architecture.md` —— 顶层与细节架构
- `AGENTS.md`（= `CLAUDE.md` symlink）—— 唯一手写上下文文件
- `docs/harnesses.md` —— 安装路由、模型映射、工具权限差异
- `plugins/plugin-eval/` —— 免模型调用的静态 skill 评分
