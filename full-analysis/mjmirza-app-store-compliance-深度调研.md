# 🔬 mjmirza/app-store-compliance — 全方位深度调研

> 调研日期：2026-11-21 ｜ 数据源：GitHub API 实时抓取（v2.4.0 / 2026-11-15）+ README + AGENTS.md + 核心数据文件 + 源码 + 30+ Issue + 中英文口碑检索
> 归属编号：#610 ｜ 一句话类别：把"应用商店审核"从玄学变成可机检、可拦截、可追溯的合规工程

## 📌 一句话定位

这不是又一份"提审注意事项清单"，而是把 Apple App Store / Google Play 的拒审知识 **编译成一套可执行、可拦截、可追溯的合规子系统**：123 条机器可读拒审模式库 + 一个 128KB 的预提交扫描 guard（可作为 13 种 AI 编码工具的 PreToolUse hook 阻断 `fastlane`/`eas submit`）+ 107 条带法律出处的全球监管截止日期库 + 一套"引用完整性"验证机制，目标是让 AI 编码工具"拒绝帮你提交一个会被拒的包"。

## ⭐ 项目亮点

1. **"Shift-left 拒审"落到 hook 层，而非文档层**：guard 直接作为 PreToolUse hook 挂进 Claude Code / Codex / Cursor 等 13 种工具，在 `fastlane` / `eas submit` / `gradle bundleRelease` / `xcrun altool` 执行前扫描，命中 critical 就 exit 2 阻断上传——把"审核员拒你"变成"你自己的 agent 不让你提交"。这是同类清单/文档项目普遍没做到的执行闭环。
2. **知识库是真结构化的，不是 Markdown 列表**：`data/rejection-patterns.json` 123 条模式（apple 61 / google 43 / both 13 / web 6，critical 38 / high 65 / medium 20），每条带 `id/platform/guideline/severity/detection/signals/fix`；`detection-recipes.json` 给 113 条模式配了可直接执行的检测命令（如用 `plutil -extract` 逐个查 5 种 `UsageDescription`）。规则与检测分离，是可维护性的关键设计。
3. **引用完整性（citation integrity）是真正的差异化护城河**：`verify-citations.py` 不是检查 HTTP 200 就完事——它针对 Apple "任意未知 article id 都返回字节相同的资讯索引页"这一反爬特性，**先抓一个故意伪造的对照 id，再对每条引用做内容指纹比对**，命中对照指纹即判为伪造；同时区分 4xx（反爬）与 5xx（宿主故障）。加上 AGENTS.md 的五级来源信任层级（官方监管机构 > 通讯社 > 学术 > 行业博客 > 社交媒体/AI 摘要）和"延期/撤回的截止日期只能就地更新、永不删除"的治理规则，这是把"事实真实性"当工程问题来解决的罕见实践。
4. **合规范围从"过审核"扩展到"持续合法"**：107 条监管截止日期覆盖 EU AI Act / DSA / COPPA / 各国年龄法，`ruling-register.json` 为 14 条要求记录法律 standing、生效日、proof 和出处；9 个 monitor 脚本跟踪 Apple 开发者要求（25 个 track）、Android、AI 政策、隐私、安全等变化，能生成迁移任务和 PR 草稿。这已经超出"提审工具"，是合规运营的早期形态。
5. **对"扫不到的项"诚实留白**：README 与 SKILL.md 反复强调——审核备注、demo 账号、隐私表单是否与运行时一致等代码看不到的项，guard 不假设通过，而是显式提示人工核对。Reddit 实测开发者评价这种"看似误报"恰恰让他们对真正致拒项保持警觉（详见口碑节）。`CLEAR.` 明确不等于"批准"。

## 🏗️ 项目架构全景

### 目录结构 + 设计哲学

仓库是"数据 / 规则执行 / 知识文档 / Agent 集成"四层解耦的：

```
mjmirza/app-store-compliance/
├── data/                        # ① 单一事实源（机器可读）
│   ├── rejection-patterns.json  # 123 条拒审模式（v2.4.0, 2026-11-15）
│   ├── detection-recipes.json   # 113 条可执行检测命令，按 pattern id 索引
│   ├── regulatory-deadlines.json# 107 条全球监管截止日期（含 source_url/verified_on）
│   └── ruling-register.json     # 14 条法律要求 + standing + proof
├── agent-os/                    # ② AI Agent 集成层
│   ├── hooks/app-store-compliance-guard.sh  # 128KB 核心扫描器（PreToolUse）
│   ├── hooks/*-test.sh
│   ├── skill/SKILL.md           # 跨平台 Agent Skill（5 步审计工作流）
│   └── commands/app-store-audit.md          # /app-store-audit 斜杠命令
├── scripts/                     # ③ 独立可执行工具集
│   ├── install.sh / install_harness.py      # 13 种工具的 hook/skill 安装器
│   ├── validate.py / verify-citations.py    # 规则校验 + 引用反伪造
│   ├── deadline-checker.py / monitor*.py    # 监管追踪（9 个 monitor）
│   ├── metadata-audit.py / release-audit.py # 商店文案与发布门禁
│   └── generate-references.py / generate-timeline.py  # 从数据生成文档
├── references/                  # ④ AI 可直接加载的结构化规则树
│   ├── guidelines/by-app-type/  # 按 App 类型（游戏/医疗/金融/儿童...）分诊
│   └── rules/                   # privacy/payments/design/export/safety... 分类
├── docs/                        # 人类可读的知识层（APPLE.md/GOOGLE-PLAY.md/申诉手册...）
├── evals/gold-cases.json        # 评测用黄金用例
├── AGENTS.md                    # 贡献者/AI 的来源信任与 PR 红线
└── .github/workflows/ci.yml     # 引用/规则/CI 校验
```

**设计哲学**：数据是唯一事实源，`docs/` 和 `references/` 部分由 `generate-*.py` 从数据生成，`validate.py` 反向校验一致性。这样可以"改一处数据、处处生效"，并用 CI 防止文档与数据漂移——这是它区别于静态 checklist 仓库的根本。

### 技术栈 & 依赖图谱

- **核心扫描器**：纯 Bash（128KB），配合 jq → python3 → 反斜杠感知 regex 三级 JSON 解析降级链；只在需要时调用 python3，Claude Code 场景"只需 git + bash"。
- **辅助脚本**：Python 3（stdlib 为主），覆盖元数据审计、监管监控、引用验证、发布门禁。
- **安装器**：Bash + Python（install_harness.py 处理 13 种工具的配置格式）。
- **许可**：OpenRoots Agent License 2.3（`LicenseRef-OpenRoots-ORA-2.3`，非 MIT，详见研判节）。

### 核心配置一览

| 文件 | 作用 | 关键字段/规模 |
|---|---|---|
| `data/rejection-patterns.json` | 拒审模式主库 | id / platform / guideline / severity / detection / signals / fix；123 条 |
| `data/detection-recipes.json` | id → 检测命令映射 | 113 条，如 `APPLE-5.1.1-MISSING-USAGE-DESCRIPTION` |
| `data/regulatory-deadlines.json` | 监管截止库 | effective/grace/mandatory/enforcement 四段日期 + absorbed_into + source_url + verified_on |
| `data/ruling-register.json` | 法律要求登记 | standing / takes_effect / proof_items / check；14 条 |
| `VERSION` / `CHANGELOG.md` | 版本 | v2.4.0（2026-11-15） |

## 💡 应用场景与启发（重点章节）

### 典型使用场景

- **独立开发者 / 小团队提审前自检**：不装任何东西，两条命令（clone + 对 app 目录跑 guard）即可拿到按严重程度排序、带文件行号的风险清单，官方称小项目约 1 秒、大项目约 1 分钟。
- **AI 编码 Agent 的发布闸门**：用 `install.sh --tool all` 把 guard 装成 hook，让 agent 在调用 `eas submit` / `fastlane` / `xcrun altool` 时被自动拦截。对"一下午用 AI 搓出一个 App、提交就被拒"的新人尤其对症。
- **被拒后的申诉与根因定位**：`docs/MISTAKE-PATTERNS.md` 的申诉手册 + 按 App 类型分诊的 `references/guidelines/by-app-type/*.md`，把一行拒审邮件映射到具体条款与修复。
- **跨地区合规运营**：面向 EU/UK/US 等市场的团队用 monitor + deadline-checker 跟踪 AI Act、DSA、COPPA、各州年龄法，把"合规"从一次性检查变持续监控。

### 可借鉴的解决方案模式

1. **"规则数据化 + 检测配方化"的分离架构**：把"什么算违规"（patterns.json，人读的语义）与"怎么检测违规"（recipes.json，机器执行的命令）拆开。这是任何规则引擎（代码规范、安全扫描、内容审核）都适用的范式——规则变更不动扫描器，扫描器升级不动规则。
2. **反伪造引用验证的"对照 id 指纹法"**：当目标站点对不存在的资源返回与真实资源字节相同的页面时，HTTP 200 毫无意义。本项目的做法——先探测一个故意伪造的 id 拿到"假页面指纹"，再对每条引用比对指纹——可以移植到任何"反爬返回统一页面"的站点（大量政府/企业网站如此）。这是 README 之外最值得偷师的工程技巧。
3. **"不能验证就显式暴露，而非默认通过"的保守语义**：guard 把代码无法确认的项也列为待人工核对，宁可多提示也不漏报。这个 fail-visible 而非 fail-silent 的设计，对一切"自动检查 + 人工兜底"系统（医疗、金融、合规）都是正确默认值。
4. **hook 安装的"可验证 + 可回滚 + 不碰凭证"三原则**：每次 install 结束会用该工具自身的 payload 格式喂一条 submit 命令、确认真的被拦才打印 `Install verified.`；保留原配置的带日期备份；对 JSON 无效或有重复 key 的配置拒绝改写；对 Kimi 的 config.toml 只追加标记块、绝不读取/打印可能含 API key 的其余内容。这是"给 AI 工具装第三方 hook"的安全范本。

### 同类需求的可参考思路

- 如果你要做"某平台规则的 AI 合规 skill"，直接可参考它的三层结构：`data/`（机读规则）→ `agent-os/skill/SKILL.md`（agent 工作流）→ `scripts/`（确定性工具），并用 `AGENTS.md` 约束贡献者与 AI 的来源可信度。
- 如果你想给自家 CI 加"发布前门禁"，可抄它的退出码语义：0=CLEAR、2=BLOCKED（critical/high）、3=INCOMPLETE（扫描失败或未审计）——把"不确定"与"通过"严格区分。
- 如果你在评估"AI 生成代码的合规风险"，它对 AI 时代新规的覆盖（发给外部 AI 无同意弹窗即拒、EU AI Act 第 50 条告知义务、隐私清单）是一份现成的风险清单。

### 可复用片段

- `release_string_has()`：只在 RELEASE 可达源码的**字符串字面量**里匹配 URL/标识，先剥掉 `#if DEBUG` 区域、跳过注释与标识符——避免把注释里的 localhost 误报为"硬编码后端"。这是静态扫描降噪的教科书写法。
- `build_blob()` + `grep_has()`：把所有文本文件读进一个 blob 做一次 grep，而不是每个文件 grep 一次（源码注释明确标注"issue #612"优化），是大规模文件扫描的性能技巧。

## 🧠 核心源码解读（克制代码量）

### 入口与主流程：guard 的模式解析（hook 模式）

guard 首先要判断自己是被"独立调用"还是作为 hook 被 AI 工具触发，并从工具各自的 JSON payload 里抽出被执行的命令。源码用 jq → python3 → regex 三级降级，任一级解析器拒绝 payload 就保持沉默（绝不误放行也不误阻断）：

```bash
# agent-os/hooks/app-store-compliance-guard.sh 节选
if [ "$#" -ge 1 ] && [ -d "$1" ]; then
  DIR="$1"                                   # standalone：显式路径
elif [ "$#" -ge 1 ] && [ ! -d "$1" ]; then
  echo "$1 is not a directory. Nothing was scanned." >&2; exit 1  # 拼错路径绝不判通过
elif [ ! -t 0 ]; then
  STDIN_JSON="$(cat 2>/dev/null || true)"    # hook：stdin 收 payload
  [ -z "$STDIN_JSON" ] && exit 0             # 空 payload 无可判定的命令
fi
```

**为什么这样设计**：拼错路径直接 exit 1（"一个没被读到的路径永远不等于通过"）；空 hook payload 直接 exit 0 而不是退化成扫描工作目录（否则每次工具调用都会慢几分钟）。这两处体现了对"检查范围"的严格语义。

### 关键模块一：多工具 payload 的命令抽取（真正的工程难点）

13 种 AI 工具的事件格式各不相同（Claude Code 用 `tool_input.command`，Codex 可能用 `toolInput.command` 或 `toolArgs`，Cursor 用 `beforeShellExecution` 且 stdout 必须输出 permission JSON）。guard 用 jq 一次性归一化：

```bash
# payload_command() 内的 jq 表达式（节选，line 51）
if .tool_name? // .toolName? as $t |
   (["Bash","PowerShell","bash","run_shell_command","shell","execute_cmd",...] | any(. == $t))
then (.tool_input.command? | strings) //
     (.toolInput.command? | strings) //
     (.toolArgs? | ...) // (.command? | strings) // empty
```

`cursor_reply()` 则专门处理 Cursor 的许可协议：blocked 时打印 `{"permission":"deny",...}` 并把 critical 数量写进 agent_message。README 对 Kiro/Cline/Amp 等"未确认格式"的工具明确给出手工接线步骤而非猜测——这种"不确定就不自动做"的克制在热蹭 AI 工具热点的项目里少见。

### 关键模块二：检测精度——注释剥离与 RELEASE 可达性

静态扫描最大的敌人是误报。guard 用三个不同语义的 grep 层解决：

| 函数 | 读取内容 | 用途 |
|---|---|---|
| `grep_has()` | 所有文本文件的原始行 | 宽松信号探测 |
| `impl_has()` | 剥掉注释的源码/HTML | 证明"真的实现了"，`.strings`/plist/json 里的提及不算 |
| `release_string_has()` | 仅 RELEASE 可达源码中的字符串字面量 | 判 hardcoded backend URL 等，避开注释和 DEBUG 分支 |

```bash
# release_string_has 的设计注释（line 538-542）
# True only if a STRING LITERAL containing the regex appears in RELEASE-reachable source.
# For Swift, #if DEBUG / #if !RELEASE debug-only regions are stripped first, so a URL only
# a debug build compiles is not flagged. The string-literal requirement skips comments
# and identifiers. This is what makes the backend check precise instead of matching
# a localhost mentioned in a comment or guarded behind DEBUG.
```

**为什么值得借鉴**：多数"AI 代码审计"工具直接全文 grep，噪音大到用户关闭告警；本项目把"信号出现"和"实现存在"分开判定，并区分编译配置可达性，是把误报率当一等公民来设计的少见案例。

### 隐藏功能 & 未文档化特性

- `docs/COMPETITIVE-GAP-ANALYSIS.md`、`docs/GAP-ANALYSIS-2026-09.md`、`docs/GAP-ANALYSIS-2026-11.md` 暴露了作者自己的竞品差距分析与月度补漏记录——这是 README 完全没有对外强调、但对评估项目成熟度极有价值的元信息。
- `.github/scripts/no-ai-attribution.sh` + `close-unknown-bot-prs.yml`：仓库有 CI 规则检测并关闭"未知 bot PR"，反映了对 AI 生成内容污染贡献的防御姿态。
- `evals/gold-cases.json` 说明作者在搞规则检测的黄金用例评测，不只是堆规则。

## 📐 架构决策与设计哲学

### 设计红线（AGENTS.md + CONTRIBUTING）

- **来源信任五级制**：官方监管机构（EC/EUR-Lex/ENISA/EDPB/FTC/NIST/CISA/ICO…）> 通讯社（Reuters/AP/Bloomberg）> 学术 > 行业博客 > 社交媒体/AI 摘要。禁止用 P4/P5 来源直接生成合规 PR，除非有 P1 官方来源可追溯佐证。
- **日期不可删除**：被延期/撤回/收窄的截止日期必须就地更新并在 `history` 里保留旧日期与原因；已过期的条目必须填 `absorbed_into` 指向承接条款，`validate.py` 会在 7 天后判定缺失为失败。这是把"监管变动的可审计性"写进数据模型。
- **可验证性门槛**：每条 deadline 必须带 `source_url` + `verified_on`，经镜像/档案/二手摘要读取的必须在 `source_note` 声明，不得冒充一手；`verified_on` 超 180 天告警。

### 版本演进中的哲学转变

从 CHANGELOG 和 Release 看，v2.0（2026-10-16）之后进入高速迭代：v2.1 跟进 10 月 App Review Guidelines 修订、v2.2 引入 Fleet Sweep 与 Ruling Register、v2.3 加截止日期溯源、v2.4 加上传路径/iOS 13 下限/IPv6/debuggable/64 位 ABI 检查。演进方向清晰：**从"静态清单"→"可执行扫描"→"动态合规运营"**，且每次监管事件都在 1-2 周内反映到数据层。

## 🌐 全网口碑画像

### 好评共识

- **真实一次过审案例**：README 引用 Reddit 开发者原话——"It noticed some weaknesses in my submission that I was able to fix. [...] My app was approved on first try!"；另一位开发者在社区分享 App Store Connect 批准邮件并点名感谢该项目（德语原话："I just got the mail from the Apple Store that my app is 'finally' approved! [...] Thanks for your compliance repo."）。作者自己也在 README 强调这些案例来自社区而非自吹。
- **"诚实误报"反而收获好评**：Reddit 同一帖里，开发者指出 guard 标记了它无法自行确认的项（review notes、ASC 里声明的数据用途）看似误报，但作者设计的"不假设通过"让他保持警觉——第三方解读（ExplainX、twstalker 中文推文）都把这一点列为该项目最实在的设计。
- ** Trending 爆发式增长**：多家科技媒体（Hamidun News、控场AI、myaitemplate）报道其单日涨 377~542⭐，一周内从约 2000 冲到 2594⭐（抓取时点）。中文科技社区（推特 @lxfater）也做了要点梳理，认可"2026 新规 + 出处可查 + 免安装提示词"的组合。
- **数据化的价值被认可**：dev.to/gittrending 的技术评估称其"117 条模式 + 隐私清单/数据安全检查显著降低拒审概率"，并点出 v2.4.0 增强的扫描能力。

### 差评共识 & 踩坑高发区

- **Windows 兼容性是当前集中爆发的 bug 区**：抓取时点 open issue 里 #2333（`release-audit.py` 硬调 `python3`，Windows 直接 WinError 2，什么都没审）、#2332（`check-docs.py` 因路径与 CRLF 误报 install.sh 语法错误）、#2330（监管数据库按平台编码读取，Windows 崩溃或静默全清）——三个都是 2026-11-19 提交，说明 Windows 用户刚开始涌入、问题尚未修复。
- **静态扫描的天然边界**：ExplainX 直接指出——CLEAR 不等于批准；guard 读不到 ASC 里的状态、商店文案、截图，也判断不了 demo 后端审核那天是否还活着；无障碍审计是静态的，不算图标对比度、不查自定义控件的焦点顺序，仍需 VoiceOver/TalkBack 手测。dev.to 也指出非标准目录结构可能得到 `NOT CHECKED.`。
- **许可不是 MIT**：OpenRoots ORA 2.3 对个人/非营利/学校/政府和年营收 ≤2000 万美元的企业免费，超过阈值按超出部分的 0.5% 收版税（年上限 25 万美元），且**用仓库训练 AI 模型需要单独 Compute 许可**。有大公司合规部门会觉得麻烦。
- **bus factor = 1**：ExplainX 明确提示单人维护、README 明着要 star/follow，支持与长期维护无保证（但 81 commits + CHANGELOG 说明目前仍活跃）。

### 争议焦点

- **拒审/发布统计的可验证性**：README 引用"Apple 审 777 万拒 193 万（近 1/4）""Google 2025 拦 175 万次"等宏大数字，Hamidun News 明确写"这些数字来自仓库自身，我们未对一手来源核验"，ExplainX 也说"treat the numbers as claims"。 irony 的是，项目以"引用完整性"为卖点，但其宣传数字本身依赖读者信任它对官方来源的转述（不过它确实提供了 TechCrunch / Apple / Google 的链接）。
- **"合规即代码"与平台的关系**：myaitemplate 的评论提出一个尖锐判断——如果开发者用自动化绕过常见拒审，平台会反过来收紧专有审核规则，形成"开源合规工具 vs 平台守门基础设施"的军备竞赛，规则本身是移动靶。

### 维护者响应风格

Issue 流显示维护者以"工程化方式"关闭 issue：#842（finding 排序改为 critical 优先 + 标文件名）、#837（识别 Unity/.NET MAUI/Tauri/KMP）、#836（提交命令藏在 package script 后绕过扫描）、#834（无障碍审计误报）等 bug/enhancement 都有具体修复并 close；同时把 Issue 模板拆成 citation-problem / pattern-contribution / tooling-bug 三类，PR 有来源可信度约束。呈现"高纪律、重溯源、快速跟进"的维护风格。

**口碑来源链接**：[Reddit 一次过审案例（README 转述截图）](https://github.com/mjmirza/app-store-compliance) · [Hamidun News：单日涨 542⭐](https://news.hamidun.com/en/news/16380/a-github-script-catches-app-store-and-google-play-rejection) · [ExplainX：许可/局限深度评估](https://explainx.ai/blog/app-store-compliance-playbook-pre-submission-guard-claude-code-github-trending-2026) · [dev.to 技术评估](https://dev.to/gittrending/how-app-store-compliance-addresses-app-store-rejections-594c) · [控场AI 中文报道](https://kongchang.com/en/articles/app-store-submission-pitfall-guide-open-source-tool-helps-you-avoid-117-rejection-patterns) · [twstalker 中文社区点评](https://www.twstalker.com/lxfater) · [myaitemplate 合规瓶颈评论](https://www.myaitemplate.com/en/news/the-compliance-bottleneck-why-app-store-gatekeeping-needs-open-source-mwni2q70) · [TechCrunch AI 发布激增](https://techcrunch.com/2026/04/18/the-app-store-is-booming-again-and-ai-may-be-why/)

## ⚔️ 竞品对比

| 维度 | mjmirza/app-store-compliance | RevylAI/greenlight | ShipLint | @spectreet/ascdoc (ASC Doctor) | fastlane precheck |
|---|---|---|---|---|---|
| 定位 | 拒审知识库 + hook + 合规运营 | 离线源码/二进制合规扫描 | iOS 配置文件快速 lint（2 秒） | ASC 上线就绪审计（只读 API） | 商店元数据预检 |
| 覆盖范围 | iOS+Android+跨平台+全球法规 | iOS+Android+IPA/APK/AAB | 主要 iOS（Info.plist/entitlements） | 仅 App Store Connect 侧数据 | 仅 metadata |
| 执行形态 | Bash guard + Python 脚本 + 13 工具 hook/skill | CLI + AI skill + 预编译二进制 | npm CLI | npm CLI + CI | Ruby（fastlane 子命令） |
| Hook 阻断 Agent 提交 | ✅ 核心能力 | ✅ skill 形式 | ❌ | ❌ | ❌ |
| 监管截止/法律层 | ✅ 107 条 + 出处溯源 | ❌ | ❌ | ❌ | ❌ |
| 引用反伪造验证 | ✅ 独有 | ❌ | ❌ | ❌ | ❌ |
| 离线/不上报 | ✅ 本地脚本 | ✅ 离线零上传 | ⚠️ 有匿名统计（可关） | ✅ 只读 ASC API | ✅ |
| 许可 | OpenRoots ORA 2.3（大企业有版税） | MIT | 专有 | MIT | MIT |

**选择建议**：
- 要"agent 不能帮你提交被拒的包"+全球合规运营 + 可溯源规则 → 本项目的组合最完整，但注意许可与 Windows bug。
- 只要快扫 iOS 配置（purpose string / privacy manifest / ITMS-90683）且跨平台 CI 友好 → ShipLint（2 秒，Node 18，Windows 可用）。
- 要扫已编译的 IPA/APK/AAB、完全离线零上传 → RevylAI/greenlight（2,442⭐，MIT）。
- 要审计 ASC 里的元数据/截图/URL/多语言遗漏（本地代码看不到的一侧）→ ASC Doctor 或 AuditStore（macOS，读 ASC API）。
- 这几类实际互补：本项目的 guard 管"代码侧 + 监管侧"，ASC Doctor 类管"账号/文案侧"，理想流水线是 ShipLint（文件）→ 本项目 guard（代码 + 规则 + 法规）→ ASC Doctor（线上数据）→ 提交。

**竞品来源**：[RevylAI/greenlight](https://github.com/RevylAI/greenlight)（2,442⭐/MIT，[产品页](https://xiry.app/resources/greenlight)）· [ShipLint](https://npmjs.com/package/shiplint) · [@spectreet/ascdoc](https://socket.dev/npm/package/@spectreet/ascdoc) · [AuditStore](https://nativlab.app/auditstore) · [app-store-review topic 全景](https://githubhelp.com/topic/app-store-review)

## 🎯 核心研判

### 项目优势（不可替代的价值点）

- **唯一的"执行层 + 知识层 + 治理层"三合一**：既有能拦 hook 的 guard，又有 123 条结构化拒审模式和 107 条带出处的法规库，还有反伪造引用与来源信任治理。竞品各占一层，它全做。
- **把 AI 工具链当作第一公民**：13 种工具的安装器 + 工具原生 payload 解析 + 可验证安装 + 卸载回滚，是对"agent 帮你发布代码"这一新范式的正面回应，而不是把 CLI 硬塞进 agent。
- **对事实真实性的工程化投入**：对照 id 指纹反伪造、来源五级制、日期不可删除、180 天过期告警——这在"AI 生成内容泛滥、幻觉引用遍地"的 2026 年极其稀缺，也构成内容可信度的护城河。

### 项目风险（潜在隐患和局限性）

- **Windows 支持未成熟**：#2330/#2332/#2333 三个 2026-11-19 的 open bug 直接导致 Windows 上"静默全清"—这是最危险的失败模式（用户以为 CLEAR 实际没审），在修复前不建议 Windows 用户依赖其自动门禁。
- **许可的商业摩擦**：ORA 2.3 对 >2000 万美元营收企业收版税、AI 训练需单独授权，可能阻碍企业采纳与被 IDE 内置。
- **静态扫描天花板 + 单点维护**：读不到线上状态、bus factor=1、统计数字依赖自报——它降低拒审概率但绝不消除，需要人工 checklist 兜底。
- **规则维护的长期成本**：监管是移动靶（EU AI Act 等逐年修订），107 条日期 + 123 条模式的持续溯源需要长期人力，单人维护的可持续性是最大问号。

### 适用场景 & 不适用场景

- ✅ 适合：用 AI 工具做移动 App 的个人/小团队、被拒过想定位根因的开发者、面向 EU/UK/US 的合规运营、需要给 agent 加发布闸门的团队。
- ❌ 不适合：Windows 为主且需要自动门禁的团队（等 bug 修复）、营收 >2000 万美元又不接受版税的企业（许可）、指望它替代人工审核与 Apple/Google 最终判断的场景、想要 GUI 的非技术用户（需 CLI/bash）。

### 趋势判断（上升期）

抓取时点 2,594⭐、168 fork、v2.4.0（2026-11-15）、近 1 个月 5 个 Release、Issue 高活跃、单日涨 377~542⭐ 登上 Trending——处于爆发上升期。催化剂是"AI 让 App 泛滥 + 商店审核收紧"的结构性矛盾。中期风险不在需求而在供给：单人维护 + 许可摩擦 + 规则维护成本，能否转成社区治理或基金会模式决定其寿命。

## 📂 关键文件路径速查

| 路径 | 作用 |
|---|---|
| `agent-os/hooks/app-store-compliance-guard.sh` | 128KB 核心扫描器（PreToolUse hook，standalone 双模式），payload 解析/检测精度逻辑集中在此 |
| `data/rejection-patterns.json` | 123 条拒审模式主库（v2.4.0） |
| `data/detection-recipes.json` | 113 条 id → 检测命令映射 |
| `data/regulatory-deadlines.json` | 107 条全球监管截止日期（带 source_url/verified_on） |
| `data/ruling-register.json` | 14 条法律要求 + standing/proof |
| `scripts/verify-citations.py` | 引用反伪造验证（对照 id 指纹法） |
| `scripts/install.sh` / `install_harness.py` | 13 种 AI 工具的 hook/skill 安装与卸载 |
| `scripts/release-audit.py` / `metadata-audit.py` | 发布门禁（exit 0/2/3）与商店文案审计 |
| `scripts/monitor*.py`（9 个） | Apple/Android/AI 政策/隐私/安全/监管追踪 |
| `agent-os/skill/SKILL.md` | 5 步审计工作流 Skill（含"两个最重要的检查"与输出契约） |
| `AGENTS.md` | 五级来源信任 + 数据不删除/可验证性红线 |
| `docs/MISTAKE-PATTERNS.md` | 根因分类 + 申诉手册 + 真实拒审案例 |
| `docs/COMPETITIVE-GAP-ANALYSIS.md` / `GAP-ANALYSIS-2026-11.md` | 作者自曝的竞品差距与月度补漏记录（独家发现） |
| `evals/gold-cases.json` | 规则检测黄金用例（评测基础设施） |

---

**数据采集说明**：本报告基于 2026-11-21 实时抓取的 GitHub API（仓库 metadata / README / AGENTS.md / SKILL.md / 4 个数据文件 / guard 源码 / 30+ Issue / 5 个 Release / LICENSE）+ 中英文网络检索（Reddit 案例转述、Hamidun News、ExplainX、dev.to、控场AI、twstalker 中文社区、githubhelp 竞品页）。所有 Issue 编号、文件行号、Star 数、统计数字均来自上述真实来源；未能独立验证的第三方转述已标注"声称/自报"。
