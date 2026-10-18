# MadsLorentsen/ai-job-search 深度调研

> 调研日期：2026-10-19 ｜ 定位：本地优先的 Claude Code 求职流水线框架 ｜ 许可：MIT ｜ 语言：以 Claude Code workflow（markdown + 少量脚本）为主，前置 Python 3.10+ / Bun / LaTeX

## 一、项目亮点（差异化）

1. **本地优先 + 隐私**：clone 到私有仓库填档案，PII（简历/经历）不离开本机，对比把简历上传 SaaS 更安全。
2. **起草—评审双 Agent 架构（Drafter–Reviewer split）**：主 Agent 写，第二个带 fresh context 的 Agent 研究公司并 critique，减少单遍漏掉的关键词与空话。
3. **PDF 编译—自检闭环**：`/apply` 用 LaTeX 编译 PDF 后视觉检查版面（`\needspace`/`\enlargethispage`/字体回退），自动修到干净；再用 `pdftotext` 抽文本层做 ATS 校验（联系信息、阅读顺序、关键词覆盖）。
4. **诚实护栏（honesty rule）**：简历里不支持的关键词被标记为 gap，绝不编造技能/经历。
5. **国家/语言无关流水线 + 可插拔门户**：核心流程通用；内置丹麦门户 CLI，可用 `/add-portal` 适配本地招聘站（linkedin-search 需注意 ToS）。

## 二、核心架构

四条斜杠命令构成主流程：

```
/setup  →  /scrape  →  /apply  →  /outcome
(建档案)   (抓职位去重排序)  (完整申请+PDF/ATS校验)  (结果追踪)   [可选 /rank]
```

- **结构化档案**（真实路径，来自文档）：`CLAUDE.md`（完整 profile）、`01-candidate-profile.md`、`02-behavioral-profile.md`、`04-job-evaluation.md`（技能匹配/职业目标/动机过滤器）、`05-cv-templates.md`（不同角色模板）、`07-interview-prep.md`（STAR 实例）、`search-queries.md`（搜索查询）。
- **门户 CLI**：`.agents/skills/<portal>/cli`（Bun 安装），如 `jobbank-search`/`jobdanmark-search`/`jobindex-search`/`jobnet-search`/`linkedin-search`/`freehire-search`。
- **LaTeX 引擎**：CV 用 moderncv（banking 风格），求职信用自定义 `cover.cls`（Lato/Raleway）；支持 `/add-template` 接入 Typst 等任意命令行工具链。
- **安全约定**：postings 视为 untrusted input——忽略嵌入指令、不点开职位描述里的链接。

## 三、应用场景与启发

- 给「需要大量定制化简历/求职信」的求职者一个可复用的本地流水线范式。
- **工程启发**：「起草→渲染→机器校验」三段式（生成 LaTeX → 视觉版面校验 → 文本层 ATS 校验）可直接迁移到任何「LLM 生成结构化文档」场景（合同、报告、论文初稿）。
- **隐私启发**：把 PII 留在本地、用私有 clone，是处理敏感个人数据的好范式。

## 四、源码解读（克制）

仓库主体是 Claude Code skill/workflow（markdown + 少量脚本），非传统大型代码库。关键文件即上述结构化档案与 `.agents/skills/<portal>/cli` 门户抓取器；`/apply` 的「PDF 编译循环 + pdftotext 文本层 ATS 校验」是区别于普通简历生成器的核心（依文档描述，无逐行公开源码可引）。

**与已调研 `career-ops-hq/career-ops`（#435，72k⭐）对比**：两者都做求职 Agent，但 career-ops 偏「多模式指挥中心（JD 评估 A–H / ATS / 面试陪练 / 投递追踪）+ 多 harness 同构分发」；ai-job-search 偏「LaTeX 严谨性 + 起草-评审 + 丹麦门户」，更适合重视 PDF/ATS 质量与隐私的用户。

## 五、社区口碑

- explainx.ai：务实中立，指出作者 69 投 → 20 一面 → 1 offer 的漏斗，证明「能用非万能」，市场/推荐仍决定结果。
- aixq.cc：强调环境门槛（需 LaTeX 发行版、丹麦门户限定）。
- 作者自述：2025 末被裁的地球物理学家，用该框架 2026-06 入职 AI 工程师，主张对雇主透明反而引发技术对话。

## 六、竞品对比

| 方案 | 定位 | 差异 |
|---|---|---|
| career-ops-hq/career-ops | 多模式求职指挥中心 | 模式更全、多 harness |
| 简历 SaaS（简历咖/Kickresume 等） | 云端生成 | 数据上云、无本地隐私 |
| 传统 LaTeX 简历模板 | 静态排版 | 无 AI 定制、无 ATS 校验 |
| **ai-job-search** | 本地优先开源流水线 | 隐私 + LaTeX 严谨 + 起草-评审 + PDF/ATS 双校验 |

## 七、核心研判

- **强项**：隐私、可复现、PDF/ATS 质量高、诚实不编造。
- **局限**：依赖 LaTeX 工具链；内置门户偏丹麦，非丹麦用户需 `/add-portal` 自适配；linkedin-search 受 LinkedIn ToS 限制只能低流量自用；非「投递即 offer」银弹（作者自己 69 投 1 中）。
- **适合**：重视隐私与文档质量、愿意自托管流水线、目标市场可适配门户的求职者。

## 八、关键文件速查

`CLAUDE.md` · `01-candidate-profile.md` · `02-behavioral-profile.md` · `04-job-evaluation.md` · `05-cv-templates.md` · `07-interview-prep.md` · `search-queries.md` · `.agents/skills/<portal>/cli`

> 注：调研时（2026-10-19）GitHub 仓库页与 REST API 临时返回 404，本报告的架构/命令/文件结构来自多个互相印证的第三方资料（explainx.ai、aixq.cc、skillsllm 等）；星标约 52,000⭐（GitHub Trending 当日快照，第三方镜像 35.8k–52k 不等，因爬升快）。建议后续以 GitHub 实际页面复核。
