# basecamp/omarchy 深度调研

> 调研日期：2026-08-17 | 星标：25,271 | Fork：2,576 | Open Issues：687 | 协议：MIT | 语言：Shell（+ Python/Lua）| 默认分支：**quattro**（非 master）| 最新版：**v4.0.0（2026-08-14）** | 仓库体积：约 185 MB / 1,622 文件

## 一、项目定位

DHH（Rails 之父）亲自维护的**"有主张的（opinionated）现代 Linux 发行版"**——本质不是 ISO 镜像，而是一套把 Arch Linux + Hyprland 编排成完整桌面产品的**配置即代码工程**：1,622 个文件里没有一行内核代码，全是安装脚本、迁移脚本、主题、shell 层与验收测试。

一句话：**它把 Rails 的工程哲学（约定优于配置 + migration + 测试 + 生成器）整体移植到了操作系统发行版上。**

## 二、项目亮点（差异化，README 不会告诉你的）

1. **`migrations/` 用 Unix 时间戳命名的一次性修复脚本** —— `migrations/1786386460.sh`、`1786782461.sh`……79 个。这是 Rails migration 思维在发行版上的直接落地：包管理器（pacman）管不了的用户态状态漂移，用带序号的幂等脚本来收敛。
2. **`test/` 有 201 个文件：发行版自带验收测试** —— `test/acceptance.d/`（apps/base/menu/panels/session/shell-surfaces/system）+ `test/shell.d/` 单元测试。绝大多数 dotfiles / 发行版项目根本没有测试层。
3. **AI Agent 用量是操作系统的一等公民** —— `bin/omarchy-agent-usage-claude` / `-codex` / `-fireworks` 三个 scanner，配套 `test/shell.d/agent-usage-*-test.sh`。顶栏面板直接显示你的 Claude Code / Codex 额度剩余。
4. **命令自带机器可读元数据** —— 每个 `bin/omarchy-*` 脚本头部有 `# omarchy:summary=` / `# omarchy:args=` / `# omarchy:hidden=true` 注释，供 CLI router（`docs/cli-router.md`）自动发现与生成菜单。
5. **双层 Agent Skills** —— `agents/skills/`（7 份给贡献者/AI 的开发规范）+ `default/agents/skills/`（装到用户机器上的 `omarchy`、`diagnose-crash` 技能）。系统自带"怎么给我提 bug 报告"的技能。
6. **硬件修复即代码** —— `install/hardware/` 下针对具体机型：`apple/fix-t2.sh`、`apple/fix-spi-keyboard.sh`、`asus/fix-z13-touchpad.sh`、`fix-yt6801-ethernet-adapter.sh`、`dell-xps-touchpad-haptics.sh`……把"某型号笔记本某个坑"沉淀成可复用脚本。
7. **默认分支叫 `quattro`** —— 配合 `bin/omarchy-branch-set` / `omarchy-channel-set`，发行版有**发布通道**概念（类似 Chrome stable/beta/dev）。

## 三、核心架构

顶层目录即架构分层（按文件数）：

| 目录 | 文件数 | 职责 |
|------|-------|------|
| `bin/` | 425 | **所有能力的唯一入口**：`omarchy-*` 命令族，CLI router 靠元数据注释聚合 |
| `themes/` | 249 | 主题（全局换色，终端/编辑器/浏览器/壁纸联动） |
| `test/` | 201 | 验收测试 + shell 单测 |
| `default/` | 176 | 分发到用户 `~` 的默认配置（bash/hypr/chromium/agents/audio…） |
| `shell/` | 175 | 自研 omarchy-shell（顶栏/面板/菜单，见 `docs/omarchy-shell.md`） |
| `manual/` | 95 | **权威手册源**（镜像到 learn.omacom.io） |
| `install/` | 83 | 安装期脚本，分 `config/` 与 `hardware/` |
| `migrations/` | 79 | 时间戳命名的一次性修复 |
| `config/` `etc/` `applications/` | 41/33/34 | Hyprland 配置、系统级配置、.desktop 条目（含 `hidden/` 隐藏噪声条目） |
| `agents/` `docs/` | 7/9 | AI 技能规范 + 内部设计文档 |

**更新流水线**（来自 `agents/skills/migrations.md`）：

```
omarchy update
  ├─ 包更新（pacman）
  ├─ omarchy-migrate        # 等待活动 pacman 事务结束后，按序跑未完成的 migration
  └─ omarchy-hook post-update
```

migration 的完成状态是 **per-user** 的：`~/.local/state/omarchy/migrations/<migration 文件名>`。这带来一条硬约束——**同一台机器多用户时，每个用户都会各自跑一遍同一个 migration，所以 migration 必须幂等**：若机器级修复已被另一个用户应用过，本次必须检测到并 no-op。这个设计细节在 README 里完全看不到，却是理解 omarchy 升级模型的关键。

## 四、应用场景与启发

**适用场景**
- 想要"开箱即用的 Hyprland 桌面"但不愿从零配 Wayland 生态的开发者（尤其 Rails/Ruby 圈）。
- 需要给团队统一开发机镜像：`install/` + `migrations/` 天然是可版本化的机器基线。
- 研究"如何把一套 dotfiles 长期演进而不腐化"的工程范式。

**给同类需求的解决思路（这才是本仓库最大价值）**
1. **任何"长期演进的用户环境"都该有 migration 层**：dotfiles、CLI 工具配置、团队开发机基线——只要状态在用户侧且包管理器管不了，就复制 `migrations/<timestamp>.sh` + per-user 完成标记 + 幂等约束这套模型。
2. **命令行工具集应把元数据写进脚本头**：`# tool:summary=` 式注释让 router/菜单/文档/补全全部自动派生，避免"新增命令忘记登记"的腐化。单一真相源在脚本自身。
3. **给 shell 脚本写验收测试是可行的**：`test/acceptance.d/*-test.sh` 证明发行版级别的行为也能自动化验证，不必靠人肉点击。
4. **"AI 额度"正在成为系统级资源**：omarchy 把 Claude/Codex/Fireworks 用量做成顶栏指标，是一个强信号——未来 OS 面板显示的可能不只是电量和网速，还有 token 余额。做开发者工具的可以直接抄这个交互位。
5. **面板与数据源解耦的契约写法**：`omarchy-agent-usage-claude` 的 docstring 明确写"面板只读这个命令打印的 JSON，从不直接接触磁盘格式或端点"。这是一条极干净的边界约定，值得任何"UI + 采集器"架构照搬。

## 五、源码深度解读

### 1. `bin/omarchy-agent-usage-claude` —— 跨 harness 的用量聚合器（Python，非 Shell）

```python
#!/usr/bin/python3
# omarchy:summary=Print the Claude Code usage record as JSON
# omarchy:args=[--force] [--limits-only]
# omarchy:hidden=true
"""Collect Claude Code usage into one display-ready JSON record.
...local transcript stats from ~/.claude/projects, the stats-cache and
history fallbacks for machines without transcripts, pi/omp and opencode
sessions that ran on an Anthropic provider, and the authoritative rate
limits from Anthropic's OAuth usage endpoint. The panel itself only ever
reads the JSON this prints; it never talks to disk formats or endpoints.
"""
AGENT_ID = "claude"
USAGE_ENDPOINT = "https://api.anthropic.com/api/oauth/usage"
PROBE_MIN_INTERVAL_SECONDS = 15
```

看点密集：
- **多源合并**：本地 transcript（`~/.claude/projects`）→ stats-cache → history 兜底 → **`pi` / `omp` / `opencode` 会话**（只要跑在 Anthropic provider 上都算进去）→ 最后用 OAuth usage 端点拿权威限额。这意味着它统计的是"你这台机器上的 Anthropic 消耗"，而非"某一个客户端的消耗"。
- **节流**：`PROBE_MIN_INTERVAL_SECONDS = 15` 防止面板刷新打爆远端。
- 用到 `fcntl`（跨进程文件锁）、`sqlite3`（读客户端本地库）、`tempfile` 原子写——一个"面板取数脚本"该有的健壮性全都有。

### 2. `migrations/` + `omarchy-migrate` —— 发行版的 schema migration

关键设计（引自 `agents/skills/migrations.md` 原文要点）：
- 定位："**one-time repair scripts for existing installs**"，用于"包更新需要改动 pacman 无法安全拥有的状态"时；
- 权限模型：以当前用户身份运行，可动 `~/.config`、`~/.local`、user systemd、浏览器/编辑器偏好、DBus/session 状态，必要时也做机器级修复（自行调用提权助手）；
- 时序：`omarchy-migrate` **先等待活动的 pacman 事务结束**再执行——避免与包管理器打架；
- 幂等是硬要求，因为完成标记是 per-user 的。

这套东西解决的是所有"配置分发型项目"的老大难：**老用户的存量状态怎么跟上新版本的假设**。

### 3. `install/hardware/` —— 把硬件坑固化成可审计脚本

`fix-brcmfmac-supplicant.sh`（博通网卡）、`fix-t2.sh`（Apple T2 芯片）、`fix-spi-keyboard.sh`、`fix-asus-ptl-b9406-touchpad.sh`、`fix-surface-keyboard.sh`、`fix-fkeys.sh`……这是社区 issue 的直接沉淀物（对照热门 issue「Macbook Pro 2020 WIFI Issues」33 条讨论）。**一个发行版的真实成熟度，看的就是这个目录有多厚。**

## 六、社区口碑

- **25,271 ⭐ / 2,576 fork**，v4.0.0 于 2026-08-14 发布（迭代极快：v3.8.3 → v3.8.4 → v4.0.0 不到一个月）。
- **687 个 open issue**：数量大但结构健康，绝大多数是硬件适配与功能请求，而非架构争议。热门讨论：`Macbook Pro 2020 WIFI Issues`（33💬）、`Add face unlock via howdy`（27💬）、`add ssh-agent support to store SSH key passphrases`（12💬）、`Add Vivaldi browser support`（11💬）、`Fix unreachable Bluetooth toggle when radio is off`（8💬）。
- 口碑两极是公开事实：拥护者认为它是"Linux 桌面第一次有了产品经理"；批评集中在 **opinionated 到近乎独裁**（DHH 个人审美与技术取向强绑定）以及 **DHH 本人的舆论争议会外溢到项目**。
- 手册（`manual/`，95 篇）质量被普遍称赞，是同类项目里罕见的"文档当产品做"。

## 七、竞品对比

| 维度 | omarchy | Omakub（同作者，Ubuntu） | EndeavourOS / CachyOS | 手工 Hyprland dotfiles（如 end-4/HyDE） |
|------|---------|--------------------------|----------------------|------------------------------------|
| 形态 | Arch + Hyprland 配置工程 | Ubuntu + GNOME 配置工程 | 真 ISO 发行版 | 纯个人配置集合 |
| 升级模型 | **timestamp migration + per-user 标记** | 脚本重跑 | 交给 pacman/系统 | 手动 rebase，易腐化 |
| 测试 | **201 文件的验收 + 单测** | 基本无 | 发行版级 QA | 无 |
| 硬件适配 | `install/hardware/` 机型级脚本 | 少 | 强（安装器层） | 无 |
| AI Agent 集成 | **系统级用量面板 + 内置 skills** | 无 | 无 | 无 |
| 主张强度 | 极强（不可协商的默认值） | 强 | 中（给选择） | 因人而异 |

**关键区分**：EndeavourOS 类是"给你一个干净的 Arch 起点"，omarchy 是"给你一个完成品，别改"。它的竞争对手其实不是发行版，而是**你自己那份维护了三年、越来越乱的 dotfiles 仓库**。

## 八、核心研判

**优势**
- 工程纪律远超同类：migration + 测试 + 元数据 + 文档四件套齐全，这在"配置分发"品类里是断层领先。
- 迭代速度与 DHH 的分发能力（Rails 生态 + omacom.io + 手册镜像）形成飞轮。
- Agent 原生不是贴标签：`agents/skills/` 让 AI 能按规范提交 migration 和安装脚本，`default/agents/skills/diagnose-crash` 让 AI 能按规范收集崩溃信息——这是**把 AI 纳入维护流程**的真实实践。

**风险**
- **opinionated 的另一面是锁定**：你越用它的默认值，越难迁走；`bin/` 425 个命令构成的是一套私有 API 层。
- 687 open issue + 机型级修复脚本意味着**长尾硬件维护成本持续累积**，高度依赖核心维护者精力。
- 默认分支 `quattro` + channel 机制虽灵活，但对第三方脚本/文档不友好（默认 clone 到的不是 `master`/`main`，容易踩坑）。
- 项目与 DHH 个人形象强绑定，非技术风险不可忽略。

**趋势判断**
"发行版即产品 + 配置即代码 + AI 纳入维护流程"这三条会被更多项目模仿。真正值得抄的不是它的审美，而是 **migration 层 + 命令元数据 + 脚本验收测试** 这三件工程基建——它们能让任何长期演进的环境配置项目免于腐化。

## 九、关键文件速查

| 路径 | 用途 |
|------|------|
| `bin/omarchy` | 主入口（CLI router，见 `docs/cli-router.md`） |
| `bin/omarchy-migrate` | 执行未完成的 migration（等 pacman 事务） |
| `bin/omarchy-agent-usage-{claude,codex,fireworks}` | 三家 AI Agent 用量采集器（输出 JSON） |
| `bin/omarchy-agent` / `-agent-crash` / `-agent-prompt` | Agent 相关入口 |
| `bin/omarchy-branch-set` / `-channel-set` | 切换发布通道 |
| `migrations/<unix_ts>.sh` | 一次性幂等修复脚本 |
| `agents/skills/migrations.md` | **migration 编写规范（最有信息量的单文件）** |
| `agents/skills/{acceptance-tests,command-metadata,install-scripts,shell-dev,visual-verification}.md` | 贡献者/AI 开发规范 |
| `default/agents/skills/omarchy/SKILL.md` | 分发到用户机器的 Agent 技能 |
| `default/agents/skills/diagnose-crash/SKILL.md` | 崩溃诊断技能 |
| `install/config/*.sh` `install/hardware/**` | 安装期配置与机型修复 |
| `test/acceptance.d/*-test.sh` `test/shell.d/*-test.sh` | 验收与单元测试 |
| `docs/{cli-router,omarchy-shell,update-process,theming,testing,file-layout}.md` | 内部设计文档 |
| `manual/*.md` | 权威用户手册（镜像 learn.omacom.io） |
| `~/.local/state/omarchy/migrations/` | （运行时）per-user migration 完成标记 |

---

**调研方法**：`gh api` 抓取 `quattro` 分支完整 tree（1,622 blob）、逐目录统计、读取 `agents/skills/migrations.md`、`bin/omarchy-agent-usage-claude`、`README.md` 原文；issue/release 数据取自 GitHub API 实时查询（2026-08-17）。
