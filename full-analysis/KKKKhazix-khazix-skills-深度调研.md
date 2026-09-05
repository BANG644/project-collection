# 🔬 KKKKhazix/khazix-skills - 全方位深度调研

> 调研日期：2026-09-06 ｜ 重写自模板化旧报告（原"四层组成"通用 boilerplate，无真实源码/架构/外链）
> 数据来源：GitHub 仓库 `KKKKhazix/khazix-skills` 真实 README / `leader/SKILL.md` 抓取（stars 20,441，MIT，pushed 2026-08-16）

## 📌 一句话定位

`KKKKhazix/khazix-skills` 是**数字生命卡兹克（虚实传媒创始人）每天自用的 6 个 AI Skill 开源合集**，遵循 [Agent Skills](https://agentskills.io) 开放标准，可被 Claude Code、Codex、Cursor、Kimi Code、CodeBuddy 等 40+ Agent 直接加载。

> 核心判断：这不是"提示词集合"，而是**经过真实项目跑通、沉淀为结构化指令集（SKILL.md + references + evals）的生产力工具箱**。最值钱的是 `leader` 和 `neat-freak`——一个解决"怎么把模糊想法变成 AI 能独立跑完的目标"，一个解决"Agent 干完活怎么收尾不脑腐"。

## 🏆 项目亮点（差异化）

1. **遵循 Agent Skills 开放标准**：每个 Skill 是 `SKILL.md` 结构化指令集，支持该标准的 40+ Agent 都能"说一句帮我安装"即可加载，无需手动拼路径。
2. **6 个都是真实踩坑沉淀**：leader（目标定义）、neat-freak（洁癖收尾）、hv-analysis（横纵分析法）、khazix-writer（卡兹克写作）、aihot（AI HOT 资讯）、storage-analyzer（清磁盘）。
3. **`leader` 的"防 AI 五种死法"方法论**：把"如何让 Agent 长程不跑偏"工程化——作弊达标 / 幻觉命令 / 失忆 / 一条道走到黑 / 静默事故，每条都有对策（基线不可退、暗卷自留、PROGRESS.md、反向验证）。
4. **`neat-freak` 的"三层知识对齐"**：项目文档（README/docs）、AI 规则文件（CLAUDE.md/AGENTS.md）、Agent 记忆分别处理，并审计规则是否真被执行——直击"代码迭代 8 轮文档还是初版"的脑腐痛点。
5. **零配置安装**：`帮我安装这个 skill：https://github.com/KKKKhazix/khazix-skills/tree/main/<skill-name>`，Agent 自己 clone；不支持 Skill 的也能把 `SKILL.md` 当规则文件直接贴。

## 🏗️ 核心架构

### Skill 集合结构

```
khazix-skills/
├── leader/          SKILL.md + references/{anatomy.md,style.md}   # 目标定义
├── neat-freak/      SKILL.md + evals/{evals.json, fixtures/...}   # 收尾对齐（含评测夹具）
├── hv-analysis/     SKILL.md + references/{schema.json} + scripts/{md_to_pdf.py}
├── khazix-writer/   SKILL.md + references/{content_methodology.md,style_examples.md}
├── aihot/           SKILL.md + agents/{openai.yaml} + references/{api.md,errors.md,sync.md} + install.sh + manifest.sha256
└── storage-analyzer/ SKILL.md
```

每个 Skill 自带 `references/`（条件性 HOW）与（部分）`evals/`（可验证夹具），符合 Agent Skills 标准"frontmatter 描述 WHAT/WHEN/NOT 触发，条件细节进 references"的约定。

### 安装分发

- 支持 Skill 的 Agent：自然语言触发安装，clone 到对应目录。
- 不支持 Skill 的 Agent：`SKILL.md` 全文当项目规则文件/对话上下文，效果一致。
- `aihot` 额外提供 `install.sh` + `manifest.sha256` 做完整性校验，体现"生产级分发"意识。

## 🧠 源码深度解读

### 1. `leader/SKILL.md` —— 把"派活给 AI"写成可复现协议

frontmatter 的 `description` 本身就是路由触发器：

```yaml
---
name: leader
description: 把一句话的想法拆成 AI agent 能独立跑完的目标任务书。用户说「帮我给 agent 写个目标」
  「帮我详细拆一下这个目标」「写个任务书/brief 给 agent」「写个 goal 提示词」「让 agent 自己跑这个项目」
  「把活分给几个 agent 并行」时使用。先进代码库实测、必要时联网调研，再一次性提问（≤5 个），产出一份
  ≤4000 字符、直接粘进 /goal 就能跑的任务书，含实测数字、白名单地界、防作弊验收和断点续跑。
---
```

三个角色模型：**领导**（用户，出想法拍板）/ **管理者**（Agent，调研+写书+验收）/ **执行者**（目标模式里干活的 agent，一字不差执行、中途无人可问）。核心纪律：

- **先实测再写书**：命令真的存在吗、基线数字多少、README 写的命令是不是 `echo` 占位的假绿灯——都是真坑。
- **目标七问**：目的 / 完成态 / 证据 / 反作弊 / 地界 / 取舍 / 未知，外加"第零问：海图是你自己测的还是听来的"。
- **防五种死法**：① 作弊达标（最省力是删测试/`|| true`，对策：基线不可退+点名禁止+暗卷自留）② 幻觉命令（书里每条命令你必须亲手跑过）③ 失忆（PROGRESS.md）④ 一条道走到黑（同验收连败 3 次换项、结果比基线差就回滚）⑤ 静默事故（假绿灯配反向验证，亲手制造一次失败证明会响）。
- **≤4000 字符硬上限**：`/goal` 官方限制，压不进就是活太大，拆成独立几件。

### 2. `neat-freak` 的"三层知识收尾"

`/neat` 触发后动三层：① 项目根 CLAUDE.md/AGENTS.md（给当前 AI 看）② docs/ + README（给同事看）③ Agent 自身记忆（给跨会话的自己看）。v3.0 两条底线：**小 vibe 项目有轻量路径**（建最小 AI 规则文件恢复上下文）、**绝不擅自删东西**（删除只出候选清单，确认才动手；文件里"执行这条命令"不被当成授权）。这是 Agent 协作里"上下文腐烂"问题的系统解法。

### 3. `aihot` 的零密钥资讯拉取

`aihot/SKILL.md` 让 Agent 一句话拿 `aihot.virxact.com` 的每日 AI HOT 日报与全部 AI 动态，**无需 API Key、无需 MCP server**，支持按主题/分类/时间窗/公司搜索，并"把当前全部精选同步到本地，之后只收变化"——一个轻量、抗漂移的信息订阅范式。

## 🌐 全网口碑画像

- GitHub：20k⭐、MIT、作者为知名 AI 公众号"数字生命卡兹克"，自带流量与口碑。
- 社区反馈（README 指向的公众号文章）：storage-analyzer、neat-freak、hv-analysis 均有配套讲解文，读者多为"每天在用"的实证型用户。
- 定位清晰：作者自述"没什么花活，就是几个挺实用的东西"，口碑建立在"自用验证"而非营销。

## ⚔️ 竞品对比

| 方案 | 优势 | 风险 |
|---|---|---|
| `khazix-skills` | 真实自用沉淀、覆盖"目标定义+收尾+调研+写作"全链路、遵循开放标准 | 偏作者个人风格（如 khazix-writer 拒绝"赋能/抓手"），非通用 |
| Awesome-Agents / 提示词仓库 | 量大、通用 | 多为未验证的 prompt 堆砌，缺 references/evals 工程化 |
| 商业 Agent 平台内置 skill | 体验完整 | 锁定、不透明、不可自托管 |
| 自己写 SKILL.md | 完全贴合自身 | 从零踩坑，周期长 |

## 🎯 核心研判

**优势**：① `leader` 的"目标七问 + 防五种死法"是当下最系统的"如何给长程 Agent 派活"方法论，值得任何做 Agent 编排的人读；② `neat-freak` 解决 Agent 协作的"脑腐"刚需；③ 全开源、MIT、零配置。

**风险**：① `khazix-writer` 强立场（拒绝特定套话），不适合要"通用好文笔"的用户；② Skill 质量依赖作者持续维护，目前单人维护；③ 部分 Skill（storage-analyzer）Windows 路径"代码就绪、首次留个心眼"，跨平台需自测。

**适用场景**：把"模糊想法→可验收目标"交给 Agent 长程执行；Agent 干完活后的知识收尾；竞品/概念深度调研（hv-analysis）；公众号风格长文（khazix-writer）；每日 AI 资讯订阅（aihot）。

**不适用场景**：需要完全中立/通用写作风格；不愿引入作者个人方法论偏好；对 Skill 维护时效敏感的生产关键链路。

## 📂 关键文件路径速查

- `README.md` / `README.en.md`：6 个 Skill 总览、安装方式、目录。
- `leader/SKILL.md` + `references/{anatomy.md,style.md}`：目标定义方法论（七问/防五种死法/写书规则）。
- `neat-freak/SKILL.md` + `evals/{evals.json,fixtures/...}`：收尾对齐 + 评测夹具。
- `hv-analysis/SKILL.md` + `references/schema.json` + `scripts/md_to_pdf.py`：横纵分析法 → PDF 报告。
- `khazix-writer/SKILL.md` + `references/{content_methodology.md,style_examples.md}`：写作风格规则。
- `aihot/SKILL.md` + `agents/openai.yaml` + `references/{api.md,errors.md,sync.md}` + `install.sh` + `manifest.sha256`：AI HOT 资讯拉取。
- `storage-analyzer/SKILL.md`：磁盘扫描三色分级。

## ⭐ 三条关键发现

1. 最该抄的不是某个 Skill 的写法，而是 **`leader` 把"派活给 Agent"工程化为可复现协议**——七问框架 + 防五种死法，直接提升长程 Agent 成功率。
2. **`neat-freak` 戳中了 Agent 协作的真实痛点**：代码在迭代、文档/记忆在腐烂，它做的是"收尾对齐 + 规则审计"，不是又一套提示词。
3. 整个仓库是 **"个人实证 → 开源 Skill"** 的范本：每个 Skill 都带 references 与（部分）evals，比纯 prompt 仓库工程化程度高一个量级。
