# rohitg00/ai-engineering-from-scratch 深度调研

> 调研日期：2026-08-25 ｜ 星标：48,185 ⭐ ｜ 语言：Python（含 TS/Rust/Julia 示例）｜ 协议：MIT ｜ 默认分支：main ｜ 最后推送：2026-08-23
> 定位：511 课、20 阶段、~329 小时的开放 AI 工程课程——每课产出可复用 artifact（prompt / skill / agent / MCP server），「Build it by hand」

## 一、项目亮点（差异化）

1. **规模与结构**：511 lessons、20 phases、~329 小时，覆盖数学基础→ML→LLM 工程→Agent 工程→MCP→Agent Skills→认证，四语言（Python/TypeScript/Rust/Julia）实现。
2. **每课 ship 可运行 artifact**：不是「读文章」，而是每课交付一个 prompt / skill / agent / MCP server，学完即拥有可复用资产——直击「84% 学生用 AI 但仅 18% 自信用其专业」的落差。
3. **证据驱动学习（evidence-first）**：每课要求保留「命令、工作目录、退出码、有意义输出、改动的 artifact」作为证据，能解释输出才继续——反「把代码块当装饰」的速成风气。
4. **零门槛入口 + 多语言**：`npx skills add rohitg00/ai-engineering-from-scratch` 30 秒装好 AI 导师；课程页与 GitHub 同构，同一 lesson code；11 种语言 landing page。
5. **开放与可持续**：MIT，由 `agentmemory`（同名作者、#1 持久记忆库）作者打造，配 ROADMAP / certifications / i18n / 网站 stats 自动生成（`build.js` 读 `site/stats.json`）。

## 二、核心架构

课程仓库本身是「可执行的课程体系」而非静态文档：

- **阶段目录（`phases/00-19`）**：`phases/00-setup-and-tooling`（环境/工具）、`phases/01-math-foundations`（线性代数直觉等）、…`phases/11-llm-engineering`（提示工程）、`phases/13-tools-and-protocols`（含 MCP 路径、Agent Skills 快路径）、`phases/14-agent-engineering`（Agent Loop）、… 直至 `phases/19`。每阶段下是 `NN-<topic>/NN-<lesson>/`，含 `docs/en.md`（核心讲解）、`code/`（可运行代码）、`verify.py` 等自检脚本。
- **Skill 体系（`.claude/skills/`）**：`start-learning`（安置导师/placement）、`course-guide`、`learn`、`learn-mcp`、`learn-agent-skills`、`claude-certification`（含 `agents/openai.yaml`）、`check-understanding`、`find-your-level`——把「选路线 / 学 MCP / 学 Agent Skills / 考证 / 测理解 / 定级」做成可调用 Skill，使课程本身可被 Agent 驱动。
- **可复用机制**：`LESSON_TEMPLATE.md` 规定统一证据格式；`FORKING.md` / `CONTRIBUTING.md` / `CHANGELOG.md` 支撑社区共建；`.github/workflows/`（build-book / curriculum / translate）自动化出书、课程校验、翻译。
- **多端一致性**：GitHub 与网站 `aiengineeringfromscratch.com` 用同一 lesson code；`translations` 分支机翻各语言页，`docs/i18n.md` 说明。

## 三、应用场景与启发

- **系统性自学 AI 工程**：零基础到能 build 生产级 LLM 应用 / Agent / MCP / Agent Skills，适合学生、转岗工程师、自学型开发者。
- **团队内训骨架**：511 课 + 证据格式可直接改造成公司内部的「AI 工程能力地图」。
- **架构启发**：
  - 「**课程即可执行仓库**」：把 lesson 变成「docs + code + verify 脚本 + skill」，学习产出即工程资产，比视频/文章更易沉淀与复用。
  - 「**artifact-per-lesson**」：每课交付 prompt/skill/agent/MCP，符合当下「Agent Skills 即新编程语言」的趋势，学完立刻能用进自己的 Agent 工作流。
  - 「**evidence-first 评估**」：用「命令+退出码+输出」替代「看懂了」，把学习质量变成可验证的，值得任何教学/培训系统工程化借鉴。
- **对同类需求（AI 学习路径）**：它证明「动手 build + 每步留证据 + 产出可复用 artifact」比「收藏教程」更能弥合「会用」与「专业用」的鸿沟。

## 四、源码深度解读

### 1. 阶段化课程骨架（`phases/` 目录）
`phases/00-setup-and-tooling/01-dev-environment/code/verify.py` 是入门自检（如 `--route beginner`），`phases/01-math-foundations/01-linear-algebra-intuition/code/vectors.py` 是零依赖 lesson，末尾演示「矩阵乘向量 = 神经网络层内的运算」。整个 `phases/` 用「目录即阶段、子目录即课、code/ 即可运行证据」的约定，让 511 课保持可导航、可机器校验（`curriculum.yml` 工作流可全量跑 verify）。

### 2. 课程即 Skill（`.claude/skills/`）
`start-learning/SKILL.md` 是 placement tutor，`learn-mcp/SKILL.md` 与 `learn-agent-skills/SKILL.md` 分别给出 MCP 与 Agent Skills 的聚焦快路径，`claude-certification/SKILL.md` + `agents/openai.yaml` 提供认证陪练。这表明作者把「导航/教学/测评」本身 Agent 化——课程仓库同时是给编码 Agent 用的 Skill 包，呼应 `npx skills add` 的一键安装。

### 3. 证据模板与自动化（`LESSON_TEMPLATE.md` + `build.js`）
`LESSON_TEMPLATE.md` 固化「读→手写代码→运行→留证据→能解释才继续」的五步；根 `build.js` 读 `site/stats.json` 自动注入 README 的读者/浏览量（150k+ 读者、近 30 天 241k 浏览）。课程不是静态快照，而是带指标反馈、可自动出版的活文档。

## 五、全网口碑

- **星标与热度**：48k ⭐，MIT，150k+ 读者、近 30 天 241k 页面浏览（README stats 块，截至 2026-06-07）；由 `agentmemory` 作者打造，天然自带「持久记忆 #1」背书。
- **定位认知**：社区视其为「最完整、最动手的开放 AI 工程课程」，区别于 fast.ai / deeplearning.ai 等「偏理论/偏单点」的课程。
- **客观短板（社区常见质疑）**：① 511 课体量大，初学者易在广度中迷失（作者用 `start-learning` 安置导师缓解）；② 部分 lesson 翻译为机翻（`translations` 分支），细节准确度参差；③ 课程更新快，个别阶段可能滞后于最新框架版本。
- **数据来源**：来自仓库 README、stats 块、LESSON_TEMPLATE 及公开定位；逐条社区长帖口碑本次未抓取，标注为「社区普遍认知」。

## 六、竞品对比 + 核心研判

| 维度 | ai-engineering-from-scratch | fast.ai / deeplearning.ai | fullstackdeeplearning | 官方框架 docs/tutorial |
|---|---|---|---|---|
| 规模 | 511 课 / 20 阶段 | 单点课程 | 中等 | 碎片化 |
| 动手 | 每课 build + 证据 | 中 | 高（项目制） | 低 |
| artifact 产出 | prompt/skill/agent/MCP | 否 | 项目 | 片段 |
| Agent 化 | 课程即 Skill | 否 | 否 | 否 |
| 许可 | MIT 开放 | 各异 | 各异 | 各异 |

**核心研判**：
- ✅ **差异化强且稀缺**：在「AI 工程」教学赛道，它用「511 课 + 每课 artifact + 证据驱动 + 课程即 Skill」组合，填补了「理论课」与「碎片化文档」之间的系统动手空白，价值确定。
- ⚠️ **风险**：体量与更新频率带来「保鲜」压力；机翻章节质量不一；对自律要求高（证据驱动对速成心态不友好）。
- 🔮 **趋势**：「课程即可执行 Skill 包」「artifact-per-lesson」会成技术教学新范式，尤其契合 Agent Skills 生态崛起；其 `npx skills add` 分发方式预示「学习资源 Agent 化」方向。
- 💡 **启发迁移**：做教学/培训/内部知识库时，① 把内容拆成「docs + 可运行 code + verify 脚本」三件套；② 每单元交付可复用 artifact 而非笔记；③ 用「命令+退出码+输出」做学习质量门禁——比考试更贴近工程真实能力。

## 核心结论（给用户）
- 这不只是一份课程，而是「把 AI 工程能力拆成 511 个可 build、可验证、可复用 artifact 的体系」，适合想系统打基础的在校生/转岗者。
- 对调研者（你）而言，它的「课程即 Skill 包 + 证据驱动」工程化思路，可直接迁移到你正在打磨的 paper-companion / 灵感闪记等专家 Skill 的设计中。

## 七、关键文件路径速查

| 路径 | 作用 |
|---|---|
| `phases/00-setup-and-tooling/01-dev-environment/code/verify.py` | 入门环境自检 |
| `phases/01-math-foundations/01-linear-algebra-intuition/code/vectors.py` | 零依赖线性代数直觉 lesson |
| `phases/11-llm-engineering/` | 提示工程 / LLM 应用生产化 |
| `phases/13-tools-and-protocols/` | MCP 路径 + Agent Skills 快路径 |
| `phases/14-agent-engineering/` | Agent Loop 等 |
| `.claude/skills/start-learning/SKILL.md` | 安置导师（placement） |
| `.claude/skills/learn-mcp` / `learn-agent-skills` | MCP / Agent Skills 聚焦路径 |
| `.claude/skills/claude-certification/` | 认证陪练（含 agents/openai.yaml） |
| `LESSON_TEMPLATE.md` | 统一证据格式（五步法） |
| `build.js` | 读 site/stats.json 自动注入 README 指标 |
| `ROADMAP.md` / `FORKING.md` / `CONTRIBUTING.md` | 路线 / 复刻 / 共建说明 |
