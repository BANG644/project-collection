# 🔬 anthropics/skills - 全方位深度调研

## 📌 一句话定位

Public repository for Agent Skills

## 🏗️ 项目全景

仓库：anthropics/skills
- **解决的问题**：该项目试图把 README 中描述的能力产品化/脚本化，降低特定任务的搭建或执行门槛。
- **基础指标**：Stars=148596 / Forks=17534 / 默认分支=main
- **Topics**：agent-skills
- **Homepage**：数据不可用

## 🧠 核心架构

目录结构判断
- **顶层目录分布（递归树抽样汇总）**：skills(392), .claude-plugin(1), .gitignore(1), 
- `README.md`(1), THIRD_PARTY_NOTICES.md(1), spec(1), template(1)
- **关键文件候选**：
- `README.md`设计亮点研判从目录上看更偏轻量仓库，核心价值主要体现在脚本/单用途实现，而非大型分层架构。

## 🔍 源码深度解读

README / 说明文档要点Note: This repository contains Anthropic's implementation of skills for Claude. For information about the Agent Skills standard, see agentskills.io.SkillsSkills are folders of instructions, scripts, and resources that Claude loads dynamically to improve performance on specialized tasks. Skills teach Claude how to complete specific tasks in a repeatable way, whether that's creating documents with your company's brand guidelines, analyzing data using your organization's specific workflows, or automating personal tasks.For more information, check out:What are skills?Using skills in ClaudeHow to create custom skillsEquipping agents for the real world with Agent SkillsAbout This RepositoryThis repository contains skills that demonstrate what's possible with Claude's skills system. These skills range from creative applications (art, music, design) to technical tasks (testing web apps, MCP server generation) to enterprise workflows (communications, branding, etc.).Each skill is self-contained in its own folder with a SKILL.md file containing the instructions and metadata that Claude uses. Browse through these skills to get inspiration for your own skills or to understand different patterns and approaches.Many skills in this repo are open source (Apache 2.0). We've also included the document creation & editing skills that power Claude's document capabilities under the hood in the skills/docx, skills/pdf, skills/pptx, and skills/xlsx subfolders. These are source-available, not open source, but we wanted to share these with developers as a reference for more complex skills that are actively used in a...[truncated]

### 关键文件精读

README.md> **Note:** This repository contains Anthropic's implementation of skills for Claude. For information about the Agent Skills standard, see [agentskills.io](http://agentskills.io).[![skills.sh]([REDACTED_COS_URL]'s creating documents with your company's brand guidelines, analyzing data using your organization's specific workflows, or automating personal tasks.For more information, check out:- [What are skills?](https://support.claude.com/en/articles/12512176-what-are-skills)- [Using skills in Claude](https://support.claude.com/en/articles/12512180-using-skills-in-claude)- [How to create custom skills...[truncated]

### 关键逻辑总结

从关键文件组合看，项目更像是围绕单一目标组织的任务流水线/工具链，而不是超重平台。
- 入口文件决定外部交互界面（CLI / API / UI），配置文件决定运行时依赖，测试文件则暴露作者真正关心的行为边界。
- 如果用户只读 README，通常只能知道“能做什么”；而从目录与入口文件能看出“怎么做、扩展点在哪、维护成本高不高”。

## 🌐 社区口碑

### GitHub Issues 抽样

#1291 [OPEN] Código - Carrossel（comments=[] labels=无）
- #1274 [OPEN] MORROA（comments=[{'id': 'IC_kwDOP0wfhs8AAAABFP9Eyg', 'author': {'login': 'Sehastrajit'}, 'authorAssociation': 'NONE', 'body': 'Thanks for opening this issue. This repository is for Agent Skills examples and related skill implementations. This issue does not describe a bug, feature request, or contribution related to the repository, so I’m closing it as out of scope.', 'createdAt': '2026-06-08T09:23:39Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [], 'url': 'https://github.com/anthropics/skills/issues/1274#issuecomment-4647240906', 'viewerDidAuthor': False}] labels=无）
- #1272 [CLOSED] quick_validate.py: remove unused import os（comments=[] labels=无）
- #1271 [OPEN] Windows: skill-creator scripts use cp1252 file I/O, crash (UnicodeDecodeError) on UTF-8 SKILL.md（comments=[] labels=无）
- #1262 [OPEN] Your project is now listed on CodeGuilds（comments=[{'id': 'IC_kwDOP0wfhs8AAAABFP-WPg', 'author': {'login': 'Sehastrajit'}, 'authorAssociation': 'NONE', 'body': 'Thanks for the notice. This looks informational and does not require a repository change, so a maintainer can close this.', 'createdAt': '2026-06-08T09:25:24Z', 'includesCreatedEdit': True, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [], 'url': 'https://github.com/anthropics/skills/issues/1262#issuecomment-4647261758', 'viewerDidAuthor': False}] labels=无）
- #1260 [OPEN] skill-creator: trigger eval writes {skill}-skill-{hash} command files into the live project's .claude/commands/, polluting the skill registry of concurrent sessions（comments=[{'id': 'IC_kwDOP0wfhs8AAAABE3OJAA', 'author': {'login': 'xg-gh-25'}, 'authorAssociation': 'NONE', 'body': 'The isolation-via-tempdir fix is exactly right. The production lesson here is about live-registry mutation vs. hermetic evaluation — the current pattern treats evaluation as an in-place operation when it should be a read-only query against a snapshot.\n\nYour proposed fix (per-query tempdir root) solves the registry pollution, but there's a broader invariant worth hardening:\n\nAny operation that synthesizes workspace-discoverable artifacts for testing should isolate them from discovery by concurrent sessions.\n\nThe current fan-out creates three failure modes:\n\n1. Registry pollution for humans — the synthetic variants show up in / typeahead, skill listings, and system reminders of every session rooted at the project during the ~N-second eval window.\n2. False skill invocations — an agent or human can invoke {skill}-skill-{8hex} instead of the real skill if the hash suffix isn't caught.\n3. Confounded measurements — if the project has a skill with the same trigger already installed in .claude/commands/, the eval sees both the synthetic variant and the live skill, and Claude's routing is first-match by filename or description collision.\n\nYour fix handles #1 and #2 perfectly. For #3, the note about ~/.claude/skills/ shadowing is correct — per-query HOME override would be needed to fully isolate against user-global installs, but that's a much heavier lift and probably not worth it (global skills are rarer, and the failure mode is "false negative" rather than "registry pollution visible to other sessions").\n\nThe tempdir approach is production-ready as-is. Two small refinements if you're preparing a PR:\n\n1. Prefix the tempdir with skill name for forensics:\n   python\n   eval_root = Path(tempfile.mkdtemp(prefix=f"skilleval-{skill_name}-{unique_id}-"))\n   \n   If an eval crashes mid-flight and leaves /tmp/skilleval-foo-a3b7c9d1-* behind, the operator knows which skill/run to attribute it to.\n\n2. Log the isolation to make the eval hermetic-by-design explicit:\n   python\n   logger.info(f"Isolated eval root: {eval_root} (cleaned on exit)")\n   \n   This signals to anyone reading logs that the eval is intentionally not touching the live project.\n\nThe deeper pattern generalizes: any tool that auto-generates skill/command definitions for testing (optimization, A/B, trigger tuning) should use the same isolation contract — never place synthetic entries in a live .claude/commands/ that concurrent sessions can discover.\n\nIf you're submitting the PR, I'd also suggest a warning in the skill-creator README about the old behavior (< this fix) so users running older versions know why they're seeing phantom skills during evals. Something like:\n\n> Note for versions < X.Y.Z: Trigger evaluation temporarily writes synthetic command files to .claude/commands/ in the project root, visible to concurrent Claude sessions. This is fixed in X.Y.Z+ via per-query isolated roots.\n\nThe fix is small, contained, and architecturally correct — this is exactly the right direction.\n\n---\nSpotted via SwarmAI community scans. Discussion: T-MEM: Memory & Context Management', 'createdAt': '2026-06-04T10:30:54Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [], 'url': 'https://github.com/anthropics/skills/issues/1260#issuecomment-4621306112', 'viewerDidAuthor': False}] labels=无）

### Pull Requests 抽样

PR 
- #1297 [MERGED] Update claude-api skill: scheduled deployments, vault env-var credentials, system.message eventsPR 
- #1296 [OPEN] Update SKILL.mdPR 
- #1294 [MERGED] Update claude-api skill: Claude Fable 5 and Claude Mythos 5PR 
- #1293 [MERGED] Update frontend-design skillPR 
- #1292 [OPEN] feat: add video-analyzer skill - MP4/video to AI-readable report

### Releases 抽样

暂无 release 或数据不可用

### 真实反馈与维护信号研判

抽样 issue 中 open/closed 约为 7/1，可作为维护者响应速度的弱信号。近期 PR 抽样里可见已合并项 3 个，说明项目并非完全冻结。若外部搜索链路不可用，本报告明确以 GitHub issue/PR/release 作为一手社区反馈源，不用二手转载冒充口碑数据。
- 高频问题通常比 README 更能暴露真实落地难点：安装、兼容性、性能边界、文档歧义、平台限制。

## ⚔️ 竞品对比

维度skills竞品/替代定位面向仓库作者设定的具体场景，通常更垂直LangGraph / AutoGen / OpenClaw Skills 往往更通用或生态更大学习曲线依赖其内部脚本/配置约定通用方案学习成本更高，但生态更成熟差异化仓库通常以“快上手、场景专用、意见化实现”为卖点通用方案强调可扩展、稳定性、跨场景能力

### 风险

作者驱动、文档深度可能不足、接口稳定性不确定大项目更稳定，但改造成本更高

## 🎯 核心研判

### 优势

对目标问题有强意见化实现，落地路径通常比“从零搭建通用栈”更短。如果核心文件少而清晰，二次阅读和定制成本较低。GitHub 原生 issue / release / PR 能直接帮助判断项目是否仍在演进。

### 风险

若 stars、forks、release 或 PR 活跃度偏低，意味着长期维护能力要谨慎评估。如果关键逻辑过于集中在单文件脚本中，后续扩展会受到可维护性约束。若缺少测试/CI/配置 schema，生产环境采用前应先做自测和边界验证。

### 适用场景

需要快速验证该仓库所解决的问题是否值得投入。团队愿意接受一定的作者意见化设计，以换取更快交付。适合作为参考实现、内部 PoC、垂直任务工具，而非默认直接替代成熟平台。不

### 适用场景

对 SLA、兼容矩阵、长期 LTS 有强要求的核心生产系统。需要极高社区冗余、插件生态或企业级支持的场景。

## 📂 关键文件路径速查

README.md

## ⭐ 三条关键发现

代码入口/骨架集中在：
- `README.md`近期开源反馈以 issue 为主，典型议题包括：Código - Carrossel；MORROA

## 🧪 研究方法与数据来源

GitHub Repo API / README / 默认分支递归文件树关键源码文件抽样精读Issues / PRs / Releases 社区活动抽样说明：
- 若外部搜索数据不可用，则明确标注并不伪造口碑结论
