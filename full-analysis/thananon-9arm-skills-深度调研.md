# 📊 深度调研报告：thananon/9arm-skills

> **仓库**: [thananon/9arm-skills](https://github.com/thananon/9arm-skills)
> **Stars**: 3,089 ⭐ | **Forks**: 417 | **Open Issues**: 4
> **语言**: Shell | **License**: 无（⚠️ 未声明许可证） | **默认分支**: `main`
> **创建**: 2026-05-20 | **最后推送**: 2026-06-14 | **文件数**: 15 blob
> **调研日期**: 2026-08-11（本次为 2026-06-17 版本的**重写升级**：原报告缺源码/口碑/竞品/研判四个维度）

---

## 一、项目定位（一句话）

**一个资深工程师把自己的"工作纪律"编码成 6 个 Agent Skill 的仓库——不是工具集，是把人类的元认知习惯（怎么调试、怎么防走神、怎么向上汇报）灌给 AI。**

---

## 二、项目亮点（差异化）

1. **`qwenchance` 是全仓最高价值资产** — 它解决的是所有 Coding Agent 的头号顽疾：**打转（looping）、过度思考、上下文耗尽**。而且给的不是"注意别打转"这种废话，是**5 条可判定的循环检测信号 + 3 次重试硬上限 + 1000 词思考上限**。
2. **可判定的启发式，不是价值观** — 全仓 Skill 的共同特征：每条规则都能被机器验证。"重读一个本 session 已读且未改动的文件" 是可判定的；"要仔细" 不是。
3. **"背诵咒语"作为强制起手式** — `debug-mantra` 要求 Agent 在调试会话的**第一条回复里逐字复述四句咒语**。这是用输出通道给自己上锚点，对抗注意力漂移，属于罕见但有效的 prompt 工程手法。
4. **六层 bucket 生命周期管理** — `engineering` / `productivity` / `misc` / `personal` / `in-progress` / `deprecated`，且 `CLAUDE.md` 里明文规定后三者**不得**出现在 README 和 plugin.json 里。这是个人 Skill 库长期不腐烂的关键机制。
5. **`link-skills.sh` 里的自引用防御** — 30 行 Shell 里专门写了一段检测"目标目录是不是指回本仓库的符号链接"，防止把符号链接写进自己的 `skills/` 树。**踩过坑的人才写得出这段代码。**
6. **诚实的定位**：这不是产品，是一个工程师公开的私人工作哲学。原始价值在于**模式可抄**，而非"装上就变强"。

---

## 三、核心架构

### 3.1 真实文件树（15 blob，`main` 分支 — 全仓极小）

```
9arm-skills/
├── CLAUDE.md                       ← ⭐ 仓库自身的治理规则（元层）
├── README.md  .gitignore
├── .claude-plugin/plugin.json      ← 插件清单（6 个 skill 显式登记）
├── scripts/
│   ├── link-skills.sh              ← 符号链接安装器（含自引用防御）
│   └── list-skills.sh
└── skills/
    ├── engineering/
    │   ├── README.md
    │   ├── debug-mantra/SKILL.md   ← 四咒语调试纪律
    │   ├── post-mortem/SKILL.md    ← 故障复盘
    │   ├── scrutinize/SKILL.md     ← 端到端代码审查
    │   └── qwen-agent/SKILL.md     ← 子 Agent 委派
    ├── productivity/
    │   ├── README.md
    │   ├── management-talk/SKILL.md    ← 工程师→管理层话术转换
    │   └── qwenchance/SKILL.md         ← ⭐ 上下文预算 / 防打转看门狗
    └── misc/README.md              ← 空桶，占位
```

**注意**：磁盘上只有 6 个 SKILL.md，但 `CLAUDE.md` 描述了 `personal/`、`in-progress/`、`deprecated/` 三个桶——它们**存在于治理规则中但不出现在公开仓库里**。这本身就是设计：私有内容被 `.gitignore` 或本地保留，公开的只有成熟品。

### 3.2 治理层：`CLAUDE.md` 是这个仓库真正的架构

```markdown
Skills are organized into bucket folders under `skills/`:
- `engineering/` — daily code work
- `productivity/` — daily non-code workflow tools
- `misc/` — kept around but rarely used
- `personal/` — tied to my own setup, not promoted
- `in-progress/` — drafts not yet ready to ship
- `deprecated/` — no longer used

Every skill in `engineering/`, `productivity/`, or `misc/` must have a reference in
the top-level `README.md` and an entry in `.claude-plugin/plugin.json`.
Skills in `personal/`, `in-progress/`, and `deprecated/` must not appear in either.
```

**这是一份写给 AI 的仓库维护契约。** 三条硬约束：
1. 成熟桶（3 个）**必须**同时登记在 README + plugin.json；
2. 非成熟桶（3 个）**必须不**出现在两者中；
3. README 中每个 skill 名必须链接到其 SKILL.md，每个 bucket 也要有自己的 README。

**价值点**：当你让 Agent 帮你维护自己的 Skill 库时，最大的风险是它把半成品/私人配置推到公开仓库。这份 CLAUDE.md 把"什么能公开"变成了机器可执行的规则。

---

## 四、应用场景与启发 ⭐

### 4.1 什么时候该想起这个仓库

| 你的问题 | 这个仓库给的答案 |
|---|---|
| **"Agent 在长任务里老是打转怎么办？"** | `qwenchance` 的 5 条循环判定信号 + 3 次重试硬上限。**这是本仓库最该抄的东西** |
| "Agent 思考半天不动手" | 过度思考阈值：推理超 ~1000 词未行动 → 强制按当前最优决策行动，或问用户一个问题 |
| "上下文快满了怎么优雅交接" | Context tight 触发条件（低上下文提醒出现 **或** 2+ 预算信号成立）→ 完成当前步后 handoff |
| "Agent 一上来就猜 bug 原因，不复现" | `debug-mantra` 四步：复现 → 找失败路径 → 证伪假设 → 交叉引用面包屑。**无复现则明确停止，不许假设** |
| "我的个人 Skill 库越攒越乱，半成品混进公开仓库" | 抄它的六桶生命周期 + CLAUDE.md 治理契约 |
| "怎么把 skill 装到 ~/.claude/skills" | `link-skills.sh` 的符号链接方案（含自引用防御 + 排除 deprecated/in-progress/personal） |
| "怎么把技术问题讲给管理层听" | `management-talk` |

### 4.2 可迁移的四个设计模式

**① 把"元认知"编码成可判定的检查表。**
这是本仓库的方法论内核。人类工程师的"经验"往往是模糊的（"感觉不对就停下来"），而这里全部翻译成布尔判定：

> 重读一个本 session 已读**且未改动**的文件 = 循环
> 用相同参数重跑同一命令期待不同结果 = 循环
> 最近 2 步没获得新信息 = 循环
> **但**重读一个刚编辑过的文件 **不是**循环，那是验证

最后那条例外说明作者真的在实践中调过这套规则——**没有这条例外，规则会误伤正常的验证行为**。

**② 硬性数值上限，而非柔性建议。**
- 重试：同一失败命令**绝不跑第 3 次**（即使换了参数变体）
- 思考：~1000 词未行动即强制出手
- 循环：同一子问题打转 2 次以上 → 宣告"暂不可解"，转移或交接

**为什么有效**：模型对"适度""合理"这类模糊限定词几乎无感，但对具体数字有反应。**任何你想约束 Agent 的行为，都该配一个具体数字。**

**③ 强制起手式（Recitation as Anchor）。**
`debug-mantra` 要求逐字复述咒语作为第一条回复的第一件事。把约束写进模型自己的输出，比留在 system prompt 里更抗遗忘——**模型会参考自己刚说过的话**。

**④ 分级公开的个人知识库。**
六桶结构（3 公开 + 3 私有）+ 机器可执行的登记契约。适用于任何"个人积累 → 部分公开"的场景：笔记库、prompt 库、脚本库。

### 4.3 局限提醒

- **⚠️ 无 LICENSE 文件**：仓库未声明任何许可证，法律上默认"保留所有权利"。**公司环境直接复制其内容有合规风险**，建议只借鉴模式、自己重写。
- **高度个人化**：`qwen-agent` 绑定 Qwen 子 Agent 委派，`management-talk` 反映特定公司文化，不一定适配你。
- **无引用文件分层**：所有内容都在 SKILL.md 里，没有 `references/` 惰性加载。Skill 少时没问题，但不是可扩展架构（对比 guard-skills 的三层渐进披露）。

---

## 五、源码深度解读（克制版）

### 5.1 `qwenchance` 的检查表 — 全仓最高杠杆的 10 行

```markdown
## Before each step — run this

| Check | Trigger fires when... | Do this |
|---|---|---|
| **Looping?**      | You're about to repeat an action | Break the loop — pick one fix below |
| **Over-thinking?**| You've reasoned past ~1000 words without acting | Stop. Act on your current
                       best decision, or ask the user one question |
| **Context tight?**| A low-context reminder appeared, **or** 2+ budget signals hold
                                                          | Finish this step, then hand off |

If nothing fires, take the step.
```

**解读**：三行表格覆盖了长任务失败的三种主要死法。设计上的两个精妙处：
1. **"Before each step"** — 不是事后补救，是每步前的固定闸门；
2. **"If nothing fires, take the step."** — 显式声明"没触发就正常干活"，防止检查表本身变成新的过度思考来源。这句话看着废话，实际是防止 Agent 陷入"检查检查表"的元循环。

配套的重试硬上限：

```markdown
**Retry cap:** never run the same failing command a 3rd time. Can't get something
working (a command, a test runner, an import) after ~3 attempts — *even varied ones* —
STOP and ask the user; don't grind through more variations.
```

`even varied ones` 五个字是关键。模型最爱的逃逸方式就是"我换个参数再试一次，这不算重复"——这条把逃逸口堵死了。

### 5.2 `debug-mantra` 的四步咒语与失败路径升级链

```markdown
> **Mantra:**
> 1. **First is reproducibility.** Can the issue be reproduced reliably?
> 2. **Know the fail path.** Debugger first; then source trace + knob enumeration;
>    then in-code instrumentation.
> 3. **Question your hypothesis.** What would disprove it?
> 4. **Every run is a breadcrumb.** Cross-reference all of them.
```

第 2 步展开成一条**严格升级链**（只有前一招失败才升级）：

| 顺序 | 手段 | 原文关键判断 |
|---|---|---|
| 1 | 附加调试器 | "One breakpoint beats ten logs." **且必须在拧任何旋钮之前** |
| 2 | 源码追踪 + 旋钮枚举 | 列出所有能影响结果的旋钮（配置/环境变量/开关/分支条件/输入形状/时序/并发/编译选项），**一次只翻一个** |
| 3 | 代码内埋点 | 每个探针打唯一前缀（如 `[DBG-a4f2]`），**清理时一次 grep 搞定** |

第 1 步对"无法复现"的处理也很硬：

> **No repro at all** → stop. Say so explicitly. Ask the user for env access, captured artifacts (HAR, log dump, core), or permission to instrument. **Do not proceed to hypothesise.**

以及对 flaky 的量化判据：**"50% flake is debuggable; 1% is not."** 目标是 1–5 秒的确定性通过/失败信号（固定时间、播种 RNG、冻结网络、隔离文件系统）。

**为什么值得抄**：这四步是资深工程师的肌肉记忆，但 LLM 天然倾向跳过复现直接猜原因（因为猜测的 token 成本远低于搭复现环境）。**这个 Skill 本质是在对抗模型的"低成本路径偏好"。**

### 5.3 `link-skills.sh` 的自引用防御

```bash
DEST="$HOME/.claude/skills"
# If ~/.claude/skills is a symlink that resolves into this repo, we'd end up
# writing the per-skill symlinks back into the repo's own skills/ tree.
if [ -L "$DEST" ]; then
  resolved="$(readlink -f "$DEST")"
  case "$resolved" in
    "$REPO"|"$REPO"/*)
      echo "error: $DEST is a symlink into this repo ($resolved)." >&2
      exit 1 ;;
  esac
fi

find "$REPO/skills" -name SKILL.md \
  -not -path '*/node_modules/*' -not -path '*/deprecated/*' \
  -not -path '*/in-progress/*'  -not -path '*/personal/*' -print0 |
while IFS= read -r -d '' skill_md; do
  src="$(dirname "$skill_md")"; target="$DEST/$(basename "$src")"
  [ -e "$target" ] && [ ! -L "$target" ] && rm -rf "$target"
  ln -sfn "$src" "$target"
done
```

三个细节值得学：
1. **自引用检测**：如果用户已经把 `~/.claude/skills` 整个软链到本仓库，脚本会**报错退出而非污染工作副本**；
2. **`find` 的排除清单与 CLAUDE.md 治理规则一一对应** — `deprecated`/`in-progress`/`personal` 三个私有桶被硬排除，**治理规则不只是文档，它被脚本强制执行了**；
3. **`-print0` / `read -r -d ''`** — 正确处理含空格路径，加 `set -euo pipefail`。基本功扎实。

---

## 六、社区口碑

- **增长曲线**：2026-06-17 调研时 2,714 ⭐ → 2026-08-11 达 **3,089 ⭐**，两个月 +13.8%。**明显放缓**——典型的"Trending 冲高后进入长尾"曲线，与 guizang（+92%）、guard-skills（+147%）形成对比。
- **Fork/Star 比 13.5%（417/3,089）—— 全仓最高信号**：显著高于同类。原因清晰：这是**个人**工作流仓库，用户必然要 fork 后改成自己的纪律（删掉 qwen-agent、改掉 management-talk 的话术）。**高 fork 比在这里恰恰是"被真实使用"的证据**，而非"被收藏"。
- **Issue 仅 4 个**：纯 Markdown + 30 行 Shell，故障面极小。
- **维护节奏**：2026-05-20 创建 → 2026-06-14 最后推送，**近 8 周无更新**。三者中停更最久。对"个人纪律库"而言可接受（作者的调试哲学不会每周变），但意味着**它不会跟进新模型的行为变化**。
- **⚠️ 治理风险信号**：无 LICENSE。3,089 星、417 fork 的项目未声明许可证，是明显的合规缺口。fork 者严格来说都处于灰色地带。
- **口碑定性**：社区讨论集中在 `qwenchance` 和 `debug-mantra` 两个 Skill 上——这与本次源码分析的价值判断一致，**仓库的实际影响力集中在 6 个 Skill 中的 2 个**。

---

## 七、竞品对比

| 项目 | 定位 | 对比结论 |
|---|---|---|
| **amElnagdy/guard-skills**（1,154 ⭐，本库已收录） | 代码产物质量关卡 | **最直接的互补品**。9arm 管**过程纪律**（怎么调试、别打转），guard-skills 管**产物质量**（代码有没有 AI 病）。建议同装 |
| **addyosmani/agent-skills**（85,658 ⭐，本库已收录） | 生产级工程技能全家桶 | 体量差 28 倍，覆盖面碾压。但 addyosmani 偏"能力扩展"，9arm 偏"行为约束"。9arm 的 `qwenchance` 在前者里没有等价物 |
| **google/skills**（16,143 ⭐，本库已收录） | Google 官方 Skill 合集 | 官方背书、一条命令安装、有 LICENSE。9arm 在规范性上完败，但在"防打转"这个具体问题上更锋利 |
| **centminmod/my-claude-code-setup**（本库已收录） | 个人 Claude Code 配置 | 同为"个人配置公开"类。9arm 更聚焦纪律，前者更偏环境配置 |
| **各类 "awesome-claude-skills" 列表** | 索引聚合 | 只索引不提供内容。9arm 是被索引的对象 |
| **Claude Code / Codex 内置的上下文压缩** | 官方上下文管理 | 官方方案是**被动压缩**（满了才压）；`qwenchance` 是**主动预算管理**（每步前检查，提前交接）。理念不同，可叠加 |

**竞争位置判断**：它不在"最全 Skill 库"赛道竞争。真实生态位是——**在"Agent 行为纪律"这个几乎无人系统化处理的细分方向上，提供了一份可判定、可抄的检查表**。`qwenchance` 解决的"打转"问题，是所有长任务 Agent 用户的共同痛点，而市面上大多数方案还停留在"提示模型注意一下"。

---

## 八、核心研判

**值得抄的（★★★★★）**
`qwenchance` 的三行检查表 + 5 条循环判定信号 + 3 次重试硬上限。**这套东西应该直接进你自己的 Agent system prompt**，不管你用不用这个仓库。它是本次调研三个仓库里"单位字数价值密度"最高的内容。

`debug-mantra` 的失败路径升级链（调试器 → 源码追踪+旋钮枚举 → 埋点）+ "无复现则停止，不许假设" 排第二。

**值得抄的（★★★★☆）**
六桶生命周期 + CLAUDE.md 治理契约 + `link-skills.sh` 的排除清单三者联动——**治理规则被脚本强制执行**，这是个人知识库不腐烂的完整范式。

**要清醒的（⚠️）**
1. **无 LICENSE 是硬伤**。3,089 ⭐ / 417 fork 的项目零许可证，公司环境请**只借鉴模式、自行重写**，不要直接复制文件。
2. **近 8 周未更新**，三个调研对象中停更最久。
3. **6 个 Skill 里只有 2 个有普适价值**（qwenchance / debug-mantra）。`qwen-agent` 绑定特定子 Agent，`management-talk` 绑定特定公司文化，`post-mortem` / `scrutinize` 有更成熟的替代品。**别整包装，挑着抄。**
4. **无 references 分层架构**——不适合作为大型 Skill 库的架构参考，那方面看 guard-skills。
5. **增速放缓（+13.8% vs 同期同类 +92%~147%）**，说明它已过热度期，是"小众但精准"的定位，不是正在崛起的标准。

**一句话结论**
> **一个只有 15 个文件、连 LICENSE 都没有的个人仓库，却给出了目前公开资料里对"Agent 打转"最可执行的解法。** 它的价值不在装机量，而在证明了一件事：**把资深工程师的模糊经验翻译成"可判定的布尔条件 + 具体数字上限"，是让 LLM 真正遵守纪律的唯一有效路径**——"注意别打转"没用，"重读一个本 session 已读且未改动的文件即判定为循环"才有用。

---

## 九、关键文件路径速查

| 路径 | 为什么重要 |
|---|---|
| `skills/productivity/qwenchance/SKILL.md` | **全仓最高价值**：防打转 / 防过度思考 / 上下文预算三合一检查表，含 5 条循环判定 + 3 次重试硬上限 |
| `skills/engineering/debug-mantra/SKILL.md` | 四咒语调试纪律 + 失败路径三级升级链 + flaky 量化判据（50% 可调，1% 不可调） |
| `CLAUDE.md` | 仓库治理契约：六桶生命周期 + 公开/私有登记规则（写给 AI 的维护说明书） |
| `scripts/link-skills.sh` | 符号链接安装器，含自引用防御 + 与治理规则对应的排除清单 |
| `.claude-plugin/plugin.json` | 6 个 skill 的显式清单（治理规则的第二个执行点） |
| `skills/engineering/scrutinize/SKILL.md` | 端到端代码审查 |
| `skills/engineering/post-mortem/SKILL.md` | 故障事后分析 |
| `skills/engineering/qwen-agent/SKILL.md` | 子 Agent 委派模式（个人化程度高） |
| `skills/productivity/management-talk/SKILL.md` | 工程师→管理层沟通转换（个人化程度高） |

---

*调研方法：GitHub API 实时元数据 + `git/trees` 全量 15 文件树 + raw.githubusercontent 源文件直读（CLAUDE.md / plugin.json / link-skills.sh / debug-mantra / qwenchance）；星标/Fork/Issue 为 2026-08-11 实时值。*
