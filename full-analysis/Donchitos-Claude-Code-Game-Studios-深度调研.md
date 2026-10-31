# Donchitos/Claude-Code-Game-Studios 深度调研

> 索引编号：#551 ｜ 调研日期：2026-11-01 ｜ 报告类型：GitHub 仓库深度调研

## 一、项目定位（一句话）

把**单个 Claude Code 会话**变成一家结构化的游戏开发工作室——49 个专职 Agent、74 个 Slash Skill、15 个事件 Hook、14 条路径作用域规则，让 AI 单人开发也有"导演把关愿景、主程守住领域、专人落地执行"的团队纪律。

- **仓库**：https://github.com/Donchitos/Claude-Code-Game-Studios
- **协议**：MIT
- **语言**：Shell（模板壳 + Bash Hook）+ Markdown/YAML（Agent/Skill 定义）
- **数据**：⭐ 31,005 ｜ Fork 4,249 ｜ Open Issues 71 ｜ Releases 10（最新 v1.2.0）｜ 贡献者 1 ｜ 创建 2026-02-12 ｜ 末次推送 2026-10-19

## 二、项目亮点（差异化）

1. **"工作室层级"而非"一堆 agent 文件"**：49 个 agent 分三级（导演→部门负责人→专家），每个都有明确职责、升级路径与质量门禁，而非扁平的 prompt 堆砌。
2. **可量化的流程档位 `modes.rigor`**：`minimal / standard / full` 一个开关控制 6 个底层旋钮（GDD 必填章节、文档密度、QA 级别、故事粒度、评审模式、团队规模），`/start` 问一次顶六次。
3. **Hook 即护栏**：15 个事件 Hook 在每次 Bash/Read/Write/Edit 时静默校验（硬编码值、JSON 合法性、设计文档章节、注册表重排、资产命名），把"纪律"写进工具链而非靠自觉。
4. **路径作用域规则**：`src/gameplay`、`src/ai`、`src/networking`、`design/gdd` 等目录各有专属编码标准，AI 改错文件会被警告。
5. **罕见的自省 README**：作者亲自做了对照实验——`standard` 档位在首行游戏代码前写了 30 份文档，盲测却排名垫底，用数据论证"更重的流程≠更好的游戏"，并据此把 `minimal` 设为默认。

## 三、核心架构

```
CLAUDE.md                  # 主配置入口
project.yaml               # 唯一事实源：engine / 命名规范 / modes 块
.claude/
  settings.json            # Hooks 接线 + 危险操作 deny 规则
  agents/                  # 49 个 agent 定义（md + YAML frontmatter）
  skills/                  # 74 个 slash 命令（每技能一子目录）
  hooks/                   # 18 个脚本（15 事件 Hook + 2 helper + 1 诊断）
  rules/                   # 14 条路径作用域编码标准
  docs/                    # workflow-catalog.yaml（7 阶段流水线）
src/                       # 游戏源码（引擎相关：Godot/Unity/Unreal）
design/ production/ docs/ tests/   # GDD / 冲刺计划 / ADR / 测试
studio-tests/              # 对"框架自身"做 QA（不是对你的游戏）
```

**三级 Agent 层级**（对应真实工作室编制）：

| 层级 | 成员 |
|------|------|
| Tier 1 导演 | creative-director、technical-director、producer |
| Tier 2 部门负责人 | game-designer、lead-programmer、art-director、audio-director、narrative-director、qa-lead、release-manager、localization-lead |
| Tier 3 专家 | gameplay/engine/ai/network/tools/ui-programmer、systems/level/economy-designer、technical-artist、sound-designer、writer、world-builder、ux-designer、prototyper、performance/devops/analytics/security-engineer、qa-tester、accessibility-specialist、live-ops-designer、community-manager |

- **模型分配写在 frontmatter**：三位导演用 Opus，lead-programmer 等 16 位专家用 Sonnet，其余 30 个继承会话模型——把层级当"资历"而非"账单"。
- **引擎专家集**：Godot 4 / Unity / Unreal 5 各有专门 agent 子集（如 `godot-gdscript-specialist`、`unity-dots-specialist`、`ue-gas-specialist`）。

**协调模型**（5 条铁律）：① 垂直委派（导演→负责人→专家）② 同层只能协商、不能跨域拍板 ③ 冲突升级到共同上级 ④ 跨部门的变更由 producer 协调 ⑤ 不越界改他人领域文件。

**协作而非自治**：每个 agent 遵守 Ask→Present 2-4 选项→你拍板→Draft→Approve 协议，作者始终掌权。

## 四、应用场景与启发（重点）

**这套模板的真正价值不在"做游戏"，而在它把"通用编码 Agent 变成结构化团队"的方法论可迁移到任意需要角色分离 + 质量门禁的领域**：

- **跨领域复用**：同样的"导演/负责人/专家"层级 + 路径规则 + 档位配置，可直接套用到写论文（调研/写作/审稿三角色）、做产品（设计/研发/运营）、写文档（架构/实现/校对）。换掉 `src/` 和 `design/` 的目录约定即可。
- **`modes.rigor` 配置范式**：用一个 front-door 旋钮展开多个独立开关，是"渐进式过程重量"的优雅实现——新手用 `minimal` 快速出活，项目长大后再一键升 `full`。任何脚手架/模板项目都该借鉴这种"默认轻、按需重"的开关设计。
- **Hook 即纪律**：把"不准硬编码魔法数、不准删注册表条目、改设计文档要走章节校验"做成 PreToolUse/PostToolUse 拦截，比写在 CLAUDE.md 里让 AI"自觉"可靠得多。这是给任何 AI 编程工作流加固的可复制模式。
- **给你的项目参考**：如果你在搭"错题归因"这类多角色 AI 协作链路，CCGS 的"角色分层 + 升级路径 + 质量门禁 + 配置化流程重量"四件套，正是把单 Agent 升级为多 Agent 团队的结构蓝本。

## 五、源码解读（核心模块）

### 1. Agent 定义：`creative-director.md` 的协作协议

frontmatter 声明角色约束，正文是一套可执行的决策工作流：

```yaml
---
name: creative-director
tools: Read, Glob, Grep, Write, Edit, WebSearch
model: opus
maxTurns: 30
memory: project
disallowedTools: Bash          # 导演不碰 Bash，只做决策
---
```

正文给出 5 步战略决策流（理解上下文→框定问题→给 2-3 个选项含取舍/风险/先例→明确推荐→支持用户决定），并有一处**精巧的"有界例外"**：当本 agent 由编排者（orchestrator）派生、且派生命令**显式指名了产物落盘路径**时，可直接写文件而无需二次征求同意——但仅限 `production/`、`docs/`、`tests/` 下的**新**产物，绝不改既有源码/配置，也绝不写自己选的路径。这把"自治提速"和"用户主权"用一条规则精确切分。

### 2. 配置真相源：`project.yaml`

```yaml
schema_version: 1
framework:
  version: 1.2.0
  last_upgraded: 2026-10-19
# 注意：本模板出厂不带 modes: 块；/start 才会写入 modes.rigor 与
# modes.automation。但 6 个底层旋钮（review_mode / workflow / docs.density /
# qa.level / story_granularity / team.size）绝不在此种子化，否则会"钉死"
# 取值、遮蔽 rigor 的展开逻辑。
```

配置解析有清晰优先级：`project.yaml`（团队共享）< `project.local.yaml`（gitignored，个人覆盖）。`/settings modes.rigor=full` 写共享；`/settings --local ...` 写个人。这种"共享配置 + 个人覆盖 + 解析顺序文档化"的写法，是多人 AI 协作项目的配置治理样板。

### 3. 安全护栏：`settings.json` 的 deny 规则

```json
"deny": [
  "Bash(rm -rf *)", "Bash(git push --force*)", "Bash(git reset --hard*)",
  "Bash(git clean* -f*)", "Bash(sudo *)", "Bash(chmod 777*)",
  "Read(**/.env*)", "Edit(**/.env*)",
  "PowerShell(Remove-Item *-Recurse*)", "PowerShell(git push *--force*)"
]
```

deny 用通配把 `git push -f`、`git clean -df`、`rm -rf` 的各种空格/连字符变体全堵死（含提交信息里出现 `push + pull` 这类文本也要拦），并在 Bash 与 PowerShell 双通道一致生效。Hook 则按 `SessionStart / PreToolUse / PostToolUse / Notification / PreCompact / Stop / SubagentStart / SubagentStop` 八类事件接线——`validate-commit.sh` 在每次 Bash 调用时校验硬编码值、TODO 格式、JSON 合法性、设计文档章节，命中才拦截、否则 `exit 0` 早退，不影响性能。

## 六、全网口碑

- **GitHub Trending 常客**，单维护者但 **4,249 Fork** 极反常——反映大家普遍"clone 下来改自己用"，契合它"模板而非锁定框架"的定位。
- README 以**可测量的实验**论证设计取舍（standard 档位 30 份文档反而盲测垫底），这种自省式文档在 prompt 模板类项目里罕见，可信度高。
- 71 个 open issue，多为功能请求与引擎适配讨论，社区活跃但规模小、维护依赖单人。
- 外部第三方评测数据「数据不可用」（新兴模板项目，长文评测少）；口碑主要来自 Trending 与 fork 行为本身。

## 七、竞品对比 + 核心研判

| 维度 | CCGS | 普通 agent 合集（如 awesome-claude-*） | Anthropic 原生 subagent |
|------|------|------|------|
| 结构 | 三级工作室层级 + 升级路径 | 扁平文件堆 | 单层 subagent |
| 护栏 | 15 Hook + 14 路径规则 | 无 | 依赖手写 prompt |
| 流程重量 | `modes.rigor` 6 旋钮可配 | 无 | 无 |
| 领域专精 | 游戏（含三引擎专家集） | 通用 | 通用 |

**核心研判**：
- ✅ **强项**：把"团队纪律"工程化为可 clone 的模板，层级/Hook/配置范式都可迁移到任意需要多角色 AI 协作的场景；默认 `minimal` + 渐进加重的设计克制且务实。
- ⚠️ **风险**：单维护者（1 contributor）、最近推送停在 10-19，Claude Code 与引擎 API 变动快，模板有"跟丢版本"的维护风险；本质是 prompt/配置工程，深度依赖 Claude Code 平台，跨平台/跨模型迁移成本高。
- 🎯 **结论**：它不是"又一个 agent 列表"，而是**多 Agent 协作的结构化范本**——值得任何想从单 Agent 升级到团队链路的人（包括你的"错题归因"多角色归因链路）作为架构蓝本精读，而非逐文件抄。重点学它的"层级 + 门禁 + 配置化流程重量"三件套，而非具体游戏词汇。

## 关键文件速查

| 文件 | 作用 |
|------|------|
| `CLAUDE.md` | 主配置入口 |
| `project.yaml` | 唯一事实源，引擎/规范/modes 块 |
| `.claude/settings.json` | Hook 接线 + deny 危险操作清单 |
| `.claude/agents/creative-director.md` | 导演级 agent 范例（含有界例外协议） |
| `.claude/agents/*.md` | 49 个角色定义（frontmatter 声明模型/工具/权限） |
| `.claude/hooks/validate-commit.sh` | 提交前校验硬编码/JSON/设计文档章节 |
| `.claude/hooks/validate-write.sh` | 写操作时按规则软警告（不阻断） |
| `.claude/rules/*` | 14 条路径作用域编码标准 |
| `.claude/docs/workflow-catalog.yaml` | 7 阶段流水线定义（被 `/help` 读取） |
| `studio-tests/` | 对框架自身（74 skill + 49 agent）做 QA |
