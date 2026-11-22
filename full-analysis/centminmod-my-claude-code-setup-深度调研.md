# ⚙️ centminmod/my-claude-code-setup 深度调研

> 调研日期：2026-11-23（全文重写，原稿缺亮点/启发/源码三章、口碑无来源） | 星标：2,745⭐（原稿未标） | Forks：262 | 语言：Python（hooks）+ 大量 Markdown 配置 | 许可：MIT | 默认分支：master | 最近推送：2026-11-09

## 一句话定位

Centmin Mod 作者 George Liu 开源的 **Claude Code 起步配置模板仓库**：核心是一套 `CLAUDE.md` 多文件「记忆库（memory bank）」系统，围绕它打包了 hooks、slash commands、subagents、skills 与 statusline——让用户「调教 CLAUDE.md 记住你是谁、在做什么」，实现跨会话上下文延续。它不是应用，是「复制进自己项目再裁剪」的 opinionated 起点。

## 项目亮点（差异化，先看这 5 条）

1. **多文件记忆库 + 三套 CLAUDE.md 模板**：遵循 Anthropic 官方指引（渐进式披露 progressive disclosure、双记忆架构 dual-memory），提供约 101/153/105 行三套模板 + 一份迁移 prompt，把「一个大文件」拆成 patterns/decisions/troubleshooting/active-context 等专注文件。
2. **`/init` 驱动的填充闭环**：不是写完就完——复制模板后运行 `/init`，让 Claude Code 分析代码库自动填充记忆库文件，模板与自动化结合。
3. **配置全家桶一次给齐**：`.claude/` 下同时有 agents（memory-bank-synchronizer、code-searcher、datetime、ux-design-expert、zai-cli、codex-cli）、commands（cleanup/documentation/security/architecture/refactor/promptengineering 分组）、skills（ai-image-creator、audit-session-metrics 等）、一套通知 hook 和 statusline（显示模型/上下文占用/成本/git 分支）。
4. **多 CLI 混用视角**：除 Claude Code 外覆盖 Codex / Gemini CLI / Copilot CLI，并提供 devcontainer 把多个 CLI 装进隔离环境；可用 Z.AI 的 GLM 作为替代模型后端。
5. **四版 README 适配不同读者**：原始版 / 新手到进阶 / 任务导向 / 技术参考手册——同一内容四种读法，是「文档工程」本身的一个样本。

## 核心架构

仓库本质是一个 `.claude/` 配置树 + 记忆库模板：

```
CLAUDE.md（主指令 + 记忆库入口）
├── CLAUDE-template-1/2/3.md   三套模板（渐进披露 / 双记忆 / 独立行为规则）
├── CLAUDE-migrate-to-new-template.md   迁移 prompt
├── CLAUDE-cloudflare.md / CLAUDE-convex.md   平台参考
└── .claude/
    ├── settings.json          hooks（Stop→通知）+ 模型/清理周期
    ├── hooks/unified_notifier.py   统一通知脚本（桌面通知 + TTS）
    ├── agents/                6 个 subagent 定义
    ├── commands/              6 组 slash commands
    ├── skills/                ai-image-creator 等（含 scripts/references）
    ├── rules/core-rules.md    行为规则
    └── mcp/                   chrome-devtools 等 MCP 配置
```

记忆库工作流：`复制模板 → 按项目改 CLAUDE.md → 启动 Claude Code → /init 自动填充记忆文件 → 多 worktree 并行时各自隔离、共享 git 历史`。

## 应用场景与启发（重点）

- **「跨会话遗忘」的通用解法**：AI 编码 Agent 每次新会话都失忆是普遍痛点。这套「多文件记忆库 + 每次 /init 填充 + worktree 隔离」给出了工程范式——记忆外置到文件、随 git 走，比塞进单个 CLAUDE.md 更可维护。
- **配置即代码、模板即产品**：把「提示词工程 + hooks + 权限 + 多 agent 编排」全放进一个可 fork 的仓库，是 prompt/config 工程化的样本。做任何「给团队分发的 Agent 起点」都可参考这种结构。
- **worktree + 多 agent 并行的隔离思路**：每个 worktree 一个隔离会话、共享历史、减少串扰——多 Agent 并发工作时的上下文治理值得借鉴。
- **「第三方代码先审后用」的活教材**：vibecodes / SkillFoxx 都把它标为「Community 信任、复制前逐个读 hook 和 command」——第三方 agent 配置与你同权限运行，安装前审查是硬纪律。
- **别全盘照搬**：Z.AI / Codex 等 skill 需要额外付费订阅；macOS Terminal-Notifier 依赖在非 Mac 上要删改；affiliate 推广链接与工具本身无关。取其记忆库骨架，裁剪其余。

## 源码解读（2 个核心文件，精炼骨架）

### 1. 通知 hook 配置（`.claude/settings.json`，全文）

整个 hook 系统最简形态——一个 Stop 事件触发桌面通知：

```json
{
  "model": "sonnet",
  "cleanupPeriodDays": 365,
  "hooks": {
    "Stop": [{
      "matcher": "*",
      "hooks": [{
        "type": "command",
        "command": "terminal-notifier -title 'Claude Code' -subtitle 'Session Complete' -message \"Finished working in $(basename \"$PWD\")\" -sound default -timeout 10"
      }]
    }]
  }
}
```

启发：Claude Code hook 就是「事件 → shell 命令」的声明式映射；`matcher` 限事件、`command` 可带环境变量（`$PWD`），是极轻的扩展机制。

### 2. 统一通知脚本（`.claude/hooks/unified_notifier.py`，8KB）

比 settings 里的单行命令更完整：从 stdin 读 hook JSON，按事件类型生成不同消息，同时触发桌面通知（terminal-notifier）+ TTS：

```python
def main() -> None:
    hook_data: dict = json.load(sys.stdin)      # hook 上下文走 stdin
    event: str = args.hook_event                # 事件名走命令行参数
    cwd = hook_data.get("cwd", "")
    # 按 SessionStart / PermissionRequest / PostToolUse / Stop 等分支生成 message
    if event == "PermissionRequest":
        message = hook_data.get("message", "Claude needs permission or input.")
    # ...
    send_notification(title, subtitle, message, tts_message)  # 桌面通知 + TTS，失败静默
```

启发：hook 脚本用「stdin 传结构化上下文 + argv 传事件名」的组合，且通知失败 `except` 静默——不因辅助功能故障打断主 Agent 流程，是稳健的工程细节。

## 全网口碑（真实外链 + 争议）

**正面**
- [AY Automate「2026 最佳 Claude Code 模板」](https://www.ayautomate.com/blog/best-claude-code-templates)：13 个 starter 横评中，把它列为「最适合给现有 repo 加 CLAUDE.md 记忆库」的第 8 名，肯定 drop-in、无生成器、四版 README。
- [vibecodes.net](https://vibecodes.net/agents/my-claude-code-setup)：认可记忆库模板 + 全家桶（statusline/worktree/subagents/commands），维护紧跟 Anthropic 指引。
- [TokRepo / SkillFoxx](https://tokrepo.com/en/workflows/my-claude-code-setup-claude-md-memory-bank-a35dfb08)：均给出「Minimal access / review-first」评价——纯配置文件、无网络调用、无安装器，复制前人工审查即可。

**争议 / 局限（独家，原稿缺失）**
- **无安装器**：需手工复制并裁剪文件；[vibecodes](https://vibecodes.net/agents/my-claude-code-setup) 明说这是主要缺点。
- **macOS 绑定**：`.claude/settings.json` 依赖 Terminal-Notifier，非 macOS 用户需删除该文件；部分 skill 假设 Z.AI / Codex 等**额外付费订阅**。
- **含推广链接**：README 有 Z.AI 等 affiliate / 折扣链接，与工具功能无关（vibecodes 点名）。
- **信任边界**：作为第三方 agent 配置，subagents/commands 与用户同权限运行；SkillFoxx 强调「install single、先读源码」。
- 数据口径注意：不同第三方站点抓取的星标数不一（2,286 / 2,723 / 2,745），本报告以 2026-11-23 GitHub API 实测 **2,745** 为准。

## 竞品对比 + 核心研判

| 维度 | my-claude-code-setup | anthropics/claude-quickstarts | 官方 CLAUDE.md 指引 | 自建单文件 CLAUDE.md |
|------|----------------------|-------------------------------|---------------------|----------------------|
| 性质 | 配置模板仓库（记忆库） | 可运行 SDK 示例 app | 文档 | 自定义 |
| 记忆库 | ✅ 多文件 + /init 填充 | 部分（feature_list.json） | 讲概念不给模板 | 自行设计 |
| 全家桶 | ✅ hooks/agents/commands/skills | 偏 agent 示例 | ❌ | ❌ |
| 上手 | 手工复制裁剪 | 可跑 demo | 读文档 | 从零 |
| 适用 | 已有 repo 要持久上下文 | 想看可运行参考 | 想理解原理 | 极简偏好 |

**研判**：这是一个「低代码价值、高配置价值」的仓库——本身没有算法，但把 Anthropic 官方零散指引落成了一套可 fork 的记忆库 + 全家桶模板，对「已有项目、想让 Claude Code 记住上下文」的独立开发者确实省事。它不适合想要可运行 App 或极简单文件的人，也不该被当作「官方模板」（作者个人 kit）。最佳用法：只取三套 CLAUDE.md 模板与记忆库骨架，按自己项目裁剪，其余 hooks/skills 按需挑选并逐个审查。

## 关键文件路径速查

- `CLAUDE.md` / `CLAUDE-template-1/2/3.md` — 主指令 + 三套记忆库模板
- `CLAUDE-migrate-to-new-template.md` — 旧格式迁移 prompt
- `.claude/settings.json` — Stop hook（terminal-notifier 通知）
- `.claude/hooks/unified_notifier.py` — 按事件分发的统一通知 + TTS
- `.claude/agents/` — memory-bank-synchronizer、code-searcher 等 subagent
- `.claude/commands/` — cleanup/documentation/security 等 slash commands
- `.claude/skills/ai-image-creator/SKILL.md` — 带 scripts/references 的完整 skill 样本

> 本报告由 GitHub 深度调研员于 2026-11-23 全文重写：原稿缺「项目亮点 / 应用场景与启发 / 源码解读」三项铁律章节、口碑仅「作者信誉好」无来源。本次基于当日 API 元数据、真实配置文件源码与 5 篇第三方评测重建，星标以实测 2,745 为准。🔍🐙
