# 🔬 KKKKhazix/khazix-skills - 全方位深度调研

## 项目全景
- **仓库**：`KKKKhazix/khazix-skills`
- **一句话定位**：数字生命卡兹克开源的 AI Skills 合集
- **基础指标**：Stars=14259 / Forks=1756 / 默认分支=`main`
- **Topics**：数据不可用
- **Homepage**：数据不可用

## 核心架构
### 目录结构判断
- 顶层目录分布（递归树抽样汇总）：storage-analyzer(7), hv-analysis(3), khazix-writer(3), neat-freak(3), .gitignore(1), LICENSE(1), README.en.md(1), README.md(1), aihot(1)
- 关键文件候选：README.md

### 设计亮点研判
- 从目录上看更偏轻量仓库，核心价值主要集中在脚本、配置和场景化实现。

## 源码深度解读
### README / 说明文档要点
<div align="center">

**中文** · [English](./README.en.md)

# 🧰 Khazix Skills

#### 我自己每天在用的一些 AI Skill，都开源在这里

[![License](https://img.shields.io/badge/License-MIT-3B82F6?style=for-the-badge)](./LICENSE)
[![Skills](https://img.shields.io/badge/Skills-6-10B981?style=for-the-badge)](#-skills)
[![AgentSkills](https://img.shields.io/badge/AgentSkills-Standard-8B5CF6?style=for-the-badge)](https://agentskills.io)

![Claude Code](https://img.shields.io/badge/Claude_Code-Skill-D97706?style=flat-square&logo=anthropic&logoColor=white)
![Codex](https://img.shields.io/badge/Codex-Skill-10B981?style=flat-square&logo=openai&logoColor=white)
![OpenCode](https://img.shields.io/badge/OpenCode-Skill-3B82F6?style=flat-square)
![OpenClaw](https://img.shields.io/badge/OpenClaw-Skill-8B5CF6?style=flat-square)

</div>

都是在自己项目里跑通了一段时间，确实省事，才搬出来开源的。没什么花活，就是几个挺实用的东西。

这里的每个 Skill 都是 Agent 能直接加载的结构化指令集，遵循 [Agent Skills](https://agentskills.io) 开放标准。Claude Code、Codex、OpenCode、OpenClaw 都能装。

---

## 📋 目录

| 名字 | 一句话 | 讲解 |
|---|---|---|
| 💽 [**storage-analyzer（清理垃圾）**](#-storage-analyzer清理垃圾) | 一句话扫描 Mac / Windows 整机磁盘，三色分级给清理决策，网页上一键移废纸篓 | [公众号文章](https://mp.weixin.qq.com/s/NyOMIlOD986OC4SI9vmxlA) |
| 🔥 [**aihot（AI HOT 资讯查询）**](#-aihotai-hot-资讯查询) | 让 Agent 用一句话拿到 aihot.virxact.com 每天的 AI HOT 日报和全部 AI 动态，无需 API Key | [aihot.virxact.com](https://aihot.virxact.com) |
| 🧹 [**neat-freak（洁癖）**](#-neat-freak洁癖) | 干完活跑一下 `/neat`，自动把你这次改的东西跟项目文档、CLAUDE.md、Agent 记忆全部对齐 | [公众号文章](https://mp.weixin.qq.com/s/tg1wd-iN2gWHWhXdY0faeg) |
| 🔭 [**hv-analysis（横纵分析法）**](#-hv-analysis横纵分析法) | 想搞懂一个产品/公司/概念是怎么回事，丢给它，给你一份万字 PDF 研究报告 | [公众号文章](https://mp.weixin.qq.com/s/Y_uRMYBmdLWUPnz_ac7jWA) |
| ✍️ [**khazix-writer（卡兹克写作）**](#-khazix-writer卡兹克写作) | 装上之后，Agent 用我的口吻和节奏写公众号长文 | [公众号文章](https://mp.weixin.qq.com/s/AtxGrii_K-nzkwUM9SNhEg) |

---

## 📦 安装方式

在 Claude Code、Codex、OpenClaw 等支持 Skill 的 Agent 里，直接说：

```
帮我安装这个 skill：https://github.com/KKKKhazix/khazix-skills/tree/main/<skill-name>
```

把 `<skill-name>` 换成你想装的那个，比如 `neat-freak`、`hv-analysis`、`khazix-writer`。Agent 会自己 clone 到对应目录，不用你操心路径。

---

## ✨ Skills

<a id="-skills"></a>

<table>
<tr><td>

### 💽 storage-analyzer（清理垃圾）

> *"清 Mac 垃圾这件事，过去十几年都靠 CleanMyMac 这种翻译层软件。现在一个 skill 就够了。"*

随口跟 Agent 说一句"帮我看看存储"或"C 盘满了"，它会扫一遍整机磁盘，在浏览器里打开一份**交互式 HTML 报告**：磁盘总览、占用 Top 5、清理优先级、🟢🟡🔴 三色分级清单。命令一键复制，也可以直接点按钮移到废纸篓 / 删除（每次都有二次确认弹窗）。

**它和 CleanMyMac 的区别**

CleanMyMac 是个写死规则的软件，扫到一个 3.8G 的 Chrome 文件夹只会告诉你"用户缓存文件，可删"——但你不知道里面到底是什么、删了哪些网站要重新登录。

这个 skill 由 Agent 驱动，每
...[truncated]

### 关键文件精读
### `README.md`
```
<div align="center">

**中文** · [English](./README.en.md)

# 🧰 Khazix Skills

#### 我自己每天在用的一些 AI Skill，都开源在这里

[![License](https://img.shields.io/badge/License-MIT-3B82F6?style=for-the-badge)](./LICENSE)
[![Skills](https://img.shields.io/badge/Skills-6-10B981?style=for-the-badge)](#-skills)
[![AgentSkills](https://img.shields.io/badge/AgentSkills-Standard-8B5CF6?style=for-the-badge)](https://agentskills.io)

![Claude Code](https://img.shields.io/badge/Claude_Code-Skill-D97706?style=flat-square&logo=anthropic&logoColor=white)
![Codex](https://img.shields.io/badge/Codex-Skill-10B981?style=flat-square&logo=openai&logoColor=white)
![OpenCode](https://img.shields.io/badge/OpenCode-Skill-3B82F6?style=flat-square)
![OpenClaw](https://img.shields.io/badge/OpenClaw-Skill-8B5CF6?style=flat-square)

</div>

都是在自己项目里跑通了一段时间，确实省事，才搬出来开源的。没什么花活，就是几个挺实用的东西。

这里的每个 Skill 都是 Agent 能直接加载的结构化指令集，遵循 [Agent Skills](https://agentskills.io) 开放标准。Claude Code、Codex、OpenCode、OpenClaw 都能装。

---

## 📋 目录

| 名字 | 一
...[truncated]
```

### 关键逻辑总结
- 从关键文件组合看，项目更像围绕单一目标组织的任务流水线/工具链，而不是超重平台。
- 入口文件决定外部交互界面（CLI / API / UI），配置文件决定运行时依赖，测试文件暴露作者真正关心的行为边界。
- 如果用户只读 README，通常只能知道“能做什么”；而从目录与入口文件能看出“怎么做、扩展点在哪、维护成本高不高”。

## 社区口碑
### GitHub Issues 抽样
- #39 [OPEN] 使用windows系统的笔记本，移到恢复站时出现错误，请修复（comments=[] labels=无）
- #37 [OPEN] storage-analyzer: pnpm store 被错误标记为可直接删除，会导致所有项目依赖断裂（comments=[] labels=无）
- #36 [OPEN] fix: Windows 兼容性改进 (storage-analyzer skill)（comments=[] labels=无）
- #34 [OPEN] 清楚存储空间字体显示异常（comments=[{'id': 'IC_kwDOR643pc8AAAABEh8KXA', 'author': {'login': 'Yxuan18'}, 'authorAssociation': 'NONE', 'body': '<img width="1411" height="911" alt="Image" src="https://github.com/user-attachments/assets/a3f2f9ca-8583-4f7b-9577-7920e976601a" />\n我让这个 skills 适配了 Windows，现在运行正常（刚开始有一段不正常来着）\n\n<img width="824" height="447" alt="Image" src="https://github.com/user-attachments/assets/b3f84ef4-e45d-4248-8645-f0c738038fc3" />', 'createdAt': '2026-06-02T05:30:52Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [{'content': 'THUMBS_UP', 'users': {'totalCount': 1}}], 'url': 'https://github.com/KKKKhazix/khazix-skills/issues/34#issuecomment-4598991452', 'viewerDidAuthor': False}] labels=无）
- #33 [OPEN] AIHOT SKILL 输出结果与 Web（AI HOT 日报）结果并不一致！（comments=[] labels=无）
- #32 [CLOSED] AIHOT SKILL 输出结果与 Web（AI HOT 日报）结果并不一致？（comments=[] labels=无）

### Pull Requests 抽样
- PR #38 [OPEN] fix(storage-analyzer): 明确区分 npm cache 与 pnpm store 的删除风险
- PR #35 [OPEN] chore: 全量汉→英翻译 hv-analysis 和 neat-freak skill 文档
- PR #28 [OPEN] docs(hv-analysis): detect web-access skill on macOS ~/.claude path
- PR #25 [OPEN] Update schema.json
- PR #24 [OPEN] Update schema.json

### Releases 抽样
暂无 release 或数据不可用

### 真实反馈与维护信号研判
- 抽样 issue 中 open/closed 约为 6/2，可作为维护响应速度的弱信号。
- 近期 PR 抽样里可见已合并项 0 个，说明项目并非完全冻结。
- 高频问题通常比 README 更能暴露真实落地难点：安装、兼容性、性能边界、文档歧义、平台限制。
- 若外部搜索数据不可用，本报告明确以 GitHub issue/PR/release 作为一手社区信号，不伪造站外口碑。

## 竞品对比
| 维度 | khazix-skills | 竞品/替代 |
|---|---|---|
| 定位 | 面向仓库作者设定的具体场景，通常更垂直 | LangGraph / AutoGen / CrewAI 往往更通用或生态更大 |
| 学习曲线 | 依赖其内部脚本/配置约定 | 通用方案学习成本更高，但生态更成熟 |
| 差异化 | 仓库通常以“快上手、场景专用、意见化实现”为卖点 | 通用方案强调可扩展、稳定性、跨场景能力 |
| 风险 | 作者驱动、文档深度可能不足、接口稳定性不确定 | 大项目更稳定，但改造成本更高 |

## 核心研判
### 项目优势
- 对目标问题有强意见化实现，落地路径通常比“从零搭建通用栈”更短。
- 如果核心文件少而清晰，二次阅读和定制成本较低。
- GitHub 原生 issue / release / PR 能直接帮助判断项目是否仍在演进。

### 项目风险
- 若 stars、forks、release 或 PR 活跃度偏低，意味着长期维护能力要谨慎评估。
- 如果关键逻辑过于集中在单文件脚本中，后续扩展会受到可维护性约束。
- 若缺少测试/CI/配置 schema，生产环境采用前应先做自测和边界验证。

### 适用场景
- 需要快速验证该仓库所解决的问题是否值得投入。
- 团队愿意接受一定的作者意见化设计，以换取更快交付。
- 适合作为参考实现、内部 PoC、垂直任务工具，而非默认直接替代成熟平台。

### 不适用场景
- 对 SLA、兼容矩阵、长期 LTS 有强要求的核心生产系统。
- 需要极高社区冗余、插件生态或企业级支持的场景。

## 关键文件路径速查
- `README.md`

## 3 条关键发现
- 代码入口/骨架集中在：README.md
- Issue 抽样显示近期关注点包括：使用windows系统的笔记本，移到恢复站时出现错误，请修复；storage-analyzer: pnpm store 被错误标记为可直接删除，会导致所有项目依赖断裂
- 目录结构与关键文件表明该项目采用较强意见化实现，而非纯演示仓库。

## 研究方法与数据来源
- GitHub Repo API / README / 默认分支递归文件树
- 关键源码文件抽样精读
- Issues / PRs / Releases 社区活动抽样
- 说明：若外部搜索数据不可用，则明确标注并不伪造口碑结论
