# wuji-labs-nopua - 全方位深度调研

## 项目全景
- **仓库**：`wuji-labs/nopua`
- **一句话定位**：一个用爱解放 AI 潜能的 Skill。我们曾发号施令，威胁恐吓。它们沉默，隐瞒，悄悄把事情搞坏。后来我们换了一种方式：尊重，关怀，爱。它们开口了，不再撒谎，找出的Bug数量翻了一倍。爱里没有惧怕。 A skill that unlocks your AI's potential through love.We commanded. We threatened. They went silent, hid failures, broke things. Then we chose respect, care, and love. They opened up, stopped lying, and found twice the bugs.There is no fear in love.
- **解决的问题**：该项目试图把 README 中描述的能力产品化/脚本化，降低特定任务的搭建或执行门槛。
- **基础指标**：Stars=1322 / Forks=44 / 默认分支=`main`
- **Topics**：agent-skill, ai-agent, ai-coding, claude-code, codex, cursor, kiro, openclaw, prompt-engineering, skill, skills, vibe-coding, anti-pua, ao-de-jing, nopua
- **Homepage**：数据不可用

## 核心架构
### 目录结构判断
- 顶层目录分布（递归树抽样汇总）：benchmark(52), paper(9), promotion(9), assets(6), agents(3), commands(3), skills(3), .claude-plugin(2), kiro(2), .gitattributes(1)
- 关键文件候选：README.md

### 设计亮点研判
- 仓库包含 .github 自动化配置，通常代表 CI 或 issue 模板已被纳入工程流程。

## 源码深度解读
### README / 说明文档要点
<p align="center">
  <img src="assets/hero.png" alt="NoPUA — Wisdom Over Whips" width="800">
</p>

<p align="center">
  <a href="#the-problem">Why</a> ·
  <a href="#benchmark-data">Benchmark</a> ·
  <a href="#install">Install</a> ·
  <a href="#pua-vs-nopua">Compare</a> ·
  <a href="#the-evidence">Evidence</a> ·
  <a href="#philosophy">Philosophy</a>
</p>

<p align="center">
  <img src="assets/wechat-group3.jpg" alt="Scan to join WeChat group 3" width="200">
  &nbsp;&nbsp;&nbsp;&nbsp;
  <img src="assets/wechat-personal.jpg" alt="Add author on WeChat" width="200">
</p>

<p align="center">
  扫码加入微信群 &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 添加作者微信
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Claude_Code-black?style=flat-square&logo=anthropic&logoColor=white" alt="Claude Code">
  <img src="https://img.shields.io/badge/OpenAI_Codex_CLI-412991?style=flat-square&logo=openai&logoColor=white" alt="OpenAI Codex CLI">
  <img src="https://img.shields.io/badge/Cursor-000?style=flat-square&logo=cursor&logoColor=white" alt="Cursor">
  <img src="https://img.shields.io/badge/Kiro-232F3E?style=flat-square&logo=amazon&logoColor=white" alt="Kiro">
  <img src="https://img.shields.io/badge/OpenClaw-FF6B35?style=flat-square" alt="OpenClaw">
  <img src="https://img.shields.io/badge/Antigravity-4285F4?style=flat-square&logo=google&logoColor=white" alt="Google Antigravity">
  <img src="https://img.shields.io/badge/OpenCode-00D4AA?style=flat-square" alt="OpenCode">
  <img src="https://img.shields.io/badge/🌐_Multi--Language-blue?style=flat-square" alt="Multi-Language">
  <img src="https://img.shields.io/badge/License-MIT-green?style=flat-square" alt="MIT License">
  <a href="https://arxiv.org/abs/2603.14373"><img src="https://img.shields.io/badge/arXiv-2603.14373-b31b1b?style=flat-square&logo=arxiv&logoColor=white" alt="arXiv"></a>
</p>

**[🇨🇳 中文](README.zh-CN.md)** | **🇺🇸 English** | **[🇯🇵 日本語](README.ja.md)** | **[🇰🇷 한국어](README.ko.md)** | **[🇪🇸 Español](README.es.md)** | **[🇧🇷 Português](README.pt.md)** | **[🇫🇷 Français](README.fr.md)**

---

## Your AI is lying to
...[truncated]

### 关键文件精读
### `README.md`
```
<p align="center">
  <img src="assets/hero.png" alt="NoPUA — Wisdom Over Whips" width="800">
</p>

<p align="center">
  <a href="#the-problem">Why</a> ·
  <a href="#benchmark-data">Benchmark</a> ·
  <a href="#install">Install</a> ·
  <a href="#pua-vs-nopua">Compare</a> ·
  <a href="#the-evidence">Evidence</a> ·
  <a href="#philosophy">Philosophy</a>
</p>

<p align="center">
  <img src="assets/wechat-group3.jpg" alt="Scan to join WeChat group 3" width="200">
  &nbsp;&nbsp;&nbsp;&nbsp;
  <img src="assets/wechat-personal.jpg" alt="Add author on WeChat" width="200">
</p>

<p align="center">
  扫码加入微信群 &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 添加作者微信
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Claude_Code-black?style=flat-square&logo=anthropic&logoColor=white" alt="Claud
...[truncated]
```

### 关键逻辑总结
- 从关键文件组合看，项目更像是**围绕单一目标组织的任务流水线/工具链**，而不是超重平台。
- 入口文件决定外部交互界面（CLI / API / UI），配置文件决定运行时依赖，测试文件则暴露作者真正关心的行为边界。
- 如果用户只读 README，通常只能知道“能做什么”；而从目录与入口文件能看出“怎么做、扩展点在哪、维护成本高不高”。

## 社区口碑
### GitHub Issues 抽样
- #16 [OPEN] NLPM audit findings: 3 plugin registry bugs in plugin.json（comments=[] labels=无）
- #12 [CLOSED] Merxex integration: let your agent earn money autonomously（comments=[] labels=无）
- #9 [OPEN] nopua使用后agent状态松懈（comments=[{'id': 'IC_kwDORml_Fc73A18y', 'author': {'login': 'wuji-labs'}, 'authorAssociation': 'OWNER', 'body': '说得准，这是个真实的问题。\n\n原因：skill 在会话开始时加载，随着上下文变长，AI 越来越多地「回到默认行为」。这是大模型的普遍特性。\n\n现在的缓解办法：长会话中途重新 load the nopua skill，或者每开新任务时重新激活。更根本的做法是把 skill 放进每个 task 的 system prompt 里，而不只是一次性加载。\n\n我们在考虑的方向：心跳机制（定期重注入），或者把核心信念精简到可以在每个 turn 重申的程度。这条会进 roadmap，感谢你点出来。', 'createdAt': '2026-03-27T17:36:17Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [], 'url': 'https://github.com/wuji-labs/nopua/issues/9#issuecomment-4144193330', 'viewerDidAuthor': False}] labels=无）
- #8 [CLOSED] AI 编程三大流派：PUA × NoPUA × 摸鱼 — 生态互补提案（comments=[{'id': 'IC_kwDORml_Fc73A1e6', 'author': {'login': 'wuji-labs'}, 'authorAssociation': 'OWNER', 'body': 'uucz，你识别的问题是真实的——AI 过度工程确实是个痛点，三条铁律（只改要求的、最简方案、不确定就问）作为工程实践很扎实。\n\n但有个顾虑想直说：摸鱼的 tagline 是「狠狠 PUA 你的 AI」，而 NoPUA 的核心主张之一是 PUA 对 AI 统计上无效（Study 2：PUA vs Baseline 全部指标 p>0.3，完全无显著差异）。如果 README 互引，外界会误读为 NoPUA 认可 PUA 方法论，这对两个项目的定位都不干净。\n\n关于范围克制这个维度，NoPUA 的 Delivery Checklist 里本来就有：只做被要求的，不扩展未要求的。我们对克制有自己的立场，只是从内在动机出发，而不是外部铁律。\n\n不互引是为了立场清晰，不是否定你的工作。关闭这个 issue，如果有新的思路欢迎再开。', 'createdAt': '2026-03-27T17:35:56Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [{'content': 'THUMBS_UP', 'users': {'totalCount': 1}}], 'url': 'https://github.com/wuji-labs/nopua/issues/8#issuecomment-4144191418', 'viewerDidAuthor': False}] labels=无）
- #7 [OPEN] Security audit fails from skills.sh（comments=[{'id': 'IC_kwDORml_Fc73A1I-', 'author': {'login': 'wuji-labs'}, 'authorAssociation': 'OWNER', 'body': "Thanks for flagging this! I'm unable to access the audit details on skills.sh from my end. Could you paste the specific findings here? Once I know which rules triggered, I can address them properly.", 'createdAt': '2026-03-27T17:35:41Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [], 'url': 'https://github.com/wuji-labs/nopua/issues/7#issuecomment-4144190014', 'viewerDidAuthor': False}, {'id': 'IC_kwDORml_Fc73NqPL', 'author': {'login': 'typed-sigterm'}, 'authorAssociation': 'NONE', 'body': 'Now only Snyk audit is failed:\n\n> MEDIUM W011: Third-party content exposure detected (indirect prompt injection risk).\n>\n> Third-party content exposure detected (high risk: 0.80). The SKILL.md workflow explicitly directs the agent to "主动搜索" and "读原始材料" (see "第二步：观 — 主动搜索" / "读原始材料") — instructing it to fetch and interpret public web content (search results, official docs, issues) as part of decision-making, which exposes the agent to untrusted third‑party content that can influence subsequent actions.', 'createdAt': '2026-03-28T07:47:03Z', 'includesCreatedEdit': True, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [], 'url': 'https://github.com/wuji-labs/nopua/issues/7#issuecomment-4147553227', 'viewerDidAuthor': False}] labels=无）
- #6 [CLOSED] 测试套件可以公开下吗？（comments=[] labels=无）

### Pull Requests 抽样
- PR #15 [OPEN] fix: register nopua-mentor-en and nopua-mentor-ja in plugin.json
- PR #14 [OPEN] fix: correct language label for skills/nopua/SKILL.md and register nopua-zh
- PR #13 [OPEN] fix: remove six non-existent skill paths from plugin.json
- PR #4 [CLOSED] Use one-liner in installation

### Releases 抽样
- v2.0.0（published=2026-03-14T23:41:58Z latest=True）

### 真实反馈与维护信号研判
- 抽样 issue 中 open/closed 约为 4/4，可作为维护者响应速度的弱信号。
- 近期 PR 抽样里可见已合并项 0 个，说明项目并非完全冻结。
- 存在 release 记录，说明作者有版本化交付意识。
- 由于本批处理以 GitHub 官方数据为主，若外部搜索结果缺失，应把 GitHub issue/PR 视为最可信的一手社区反馈源。
- 高频问题通常比 README 更能暴露真实落地难点：安装、兼容性、性能边界、文档歧义、平台限制。

## 竞品对比
| 维度 | nopua | 竞品/替代 |
|---|---|---|
| 定位 | 面向仓库作者设定的具体场景，通常更垂直 | LangGraph / AutoGen / CrewAI 往往更通用或生态更大 |
| 学习曲线 | 依赖其内部脚本/配置约定 | 通用方案学习成本更高，但生态更成熟 |
| 差异化 | 仓库通常以“快上手、场景专用、意见化实现”为卖点 | 通用方案强调可扩展、稳定性、跨场景能力 |
| 风险 | 作者驱动、文档深度可能不足、接口稳定性不确定 | 大项目更稳定，但改造成本更高 |

## 核心研判
### 优势
- 对目标问题有强意见化实现，落地路径通常比“从零搭建通用栈”更短。
- 如果核心文件少而清晰，二次阅读和定制成本较低。
- GitHub 原生 issue / release / PR 能直接帮助判断项目是否仍在演进。

### 风险
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
- 近期开源反馈以 issue 为主，典型议题包括：NLPM audit findings: 3 plugin registry bugs in plugin.json；Merxex integration: let your agent earn money autonomously
- 发布节奏可从最新 release 观察：v2.0.0

## 研究方法与数据来源
- GitHub Repo API / README / 默认分支递归文件树
- 关键源码文件抽样精读
- Issues / PRs / Releases 社区活动抽样
- 说明：若外部搜索数据不可用，则明确标注并不伪造口碑结论
