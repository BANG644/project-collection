# 🔬 interviewstreet/hiring-agent — 全方位深度调研

## 📌 一句话定位

**一个将「AI 筛简历」从"问 ChatGPT 一句这人行不行"升级为「PDF → 结构化抽取 → GitHub 信号增强 → 可审计多维评分」的管线化 Agent。** InterviewStreet（HackerRank 母公司）开源，本质上是一条严格的 ETL 管线，而非对话式 AI 工具。

## ⭐ 项目亮点

- **管线化设计而非对话式设计** —— 这是它和市面上大多数"AI 招聘工具"最本质的区别。不是"把简历贴到聊天框里问"，而是一条 `PDF → Markdown → 分节 JSON → GitHub 增强 → 公平评分 → 输出证据` 的显式管线。每条管线的每个节点都有独立的 prompt、独立的数据 Schema、独立的失败处理。
- **GitHub 信号交叉验证** —— 不止是解析简历上写了什么，而是通过 GitHub API 拉取候选人的公开仓库数据，让 LLM 对仓库做分类（个人项目/开源贡献/公司项目），再选出 Top 7 最相关仓库。**这是对"简历自述 + 客观代码证据"的双重验证**——绝大多数同类工具不做这一步。
- **Jinja 模板驱动的全解耦 Prompt 工程** —— 所有抽取和评分 prompt 都放在 `prompts/templates/` 下，Prompt 和 Python 代码完全解耦。调整评分口径不需要改 Python，重新跑一次即可。这是 Prompt 工程的最佳实践示范，比在代码里拼字符串的方式先进一个数量级。
- **Pydantic 强 Schema 保证可审计性** —— `models.py` 用 Pydantic 定义了所有中间产物的 Schema，不符合 JSON Resume 标准的数据根本流不到下一步。这让整条管线的"可审计性"有了类型系统的保障。
- **双重 LLM 后端（Ollama 本地 / Gemini 云端）** —— `.env` 里一个变量切换，完全本地运行（简历不出网）或使用云端模型。这解决了企业对 AI 招聘最大的合规疑虑——数据隐私。

## 🏗️ 项目架构全景

### 目录结构

```
hiring-agent/
├── score.py                  # 🎯 编排器：串起整条管线
├── pdf.py                    # PDF → 分节 JSON（核心抽取）
├── pymupdf_rag.py            # PDF 页 → Markdown（文本化）
├── github.py                 # GitHub 信号增强（交叉验证）
├── evaluator.py              # 公平约束下的严格评分
├── models.py                 # Pydantic Schema + LLM Provider 接口
├── llm_utils.py              # LLM 后端初始化 + 响应清洗
├── prompt.py                 # Prompt 加载器
├── config.py                 # 开发模式标志
├── transform.py              # JSON 归一化（LLM 输出 → JSON Resume）
├── prompts/
│   ├── template_manager.py   # Jinja 模板管理器
│   └── templates/            # 10 个 Jinja 模板（按 section）
│       ├── basics.jinja
│       ├── education.jinja
│       ├── work.jinja
│       ├── skills.jinja
│       ├── projects.jinja
│       ├── awards.jinja
│       ├── github_project_selection.jinja
│       ├── resume_evaluation_criteria.jinja
│       ├── resume_evaluation_system_message.jinja
│       └── system_message.jinja
└── requirements.txt
```

### 数据流

```
resume.pdf
    │
    ▼
pymupdf_rag.py ──── Markdown-like text (无 LLM)
    │
    ▼
pdf.py 分节抽取（4 次并行 LLM 调用）
    ├─ education.jinja → education JSON
    ├─ work.jinja      → work JSON
    ├─ projects.jinja  → projects JSON
    └─ skills.jinja    → skills JSON
    │
    ▼
github.py 增强（2 次 LLM 调用）
    ├─ 仓库分类     → repo categories
    └─ Top 7 选择   → most relevant repos
    │
    ▼
evaluator.py 评分（5-8 次 LLM 调用）
    ├─ technical_depth
    ├─ experience_relevance
    ├─ project_impact
    ├─ communication
    └─ career_trajectory
    │
    ▼
score.py 输出最终报告（CSV in dev mode）
```

单份简历跑完一条完整管线约需 **11-14 次 LLM 调用**。Ollama 本地约 1-3 分钟，Gemini 云端约 30-60 秒。

## 💡 应用场景与启发

### 典型使用场景

| 场景 | 说明 |
|------|------|
| **技术岗位初筛（大批量投递）** | 自动对 1000+ 投递做多维度评分，输出可排序的 CSV |
| **内部转岗评估** | 评估内部员工的 GitHub + 项目历史，做出比"面试表现"更全面的判断 |
| **Prompt 工程教学案例** | 这个项目本身就是"如何把复杂的 AI 任务拆成可管理的 prompt 管线"的最佳教科书 |
| **HR 技术债化解** | 让 HR 团队从"人工一份份看完简历凭感觉打分"升级为"可重复、可审计、可优化的自动化管线" |

### 可借鉴的解决方案模式

**「分节抽取」+「模板驱动」+「Schema 强约束」是 LLM 做结构化数据抽取的最佳实践模式。**

大多数开发者第一次用 LLM 抽数据时，会写一个巨大的 prompt 让 LLM 一次输出所有字段。但 hiring-agent 的做法恰恰相反：一次只抽一个 section（教育/工作/技能/项目），每节一个独立 prompt，可以并行调用。

这样做的好处：
1. 单个 prompt 复杂度降低 → LLM 出错率降低
2. 失败定位精确 → 教育段抽坏了只重跑教育段
3. 可以并发 → 四节并行调用，总延迟 ≈ 最慢一节

### 同类需求的可参考思路

**如果你需要用 LLM 处理自然语言文档中的结构化信息（简历、合同、病历、论文），hiring-agent 的管线设计是所有基准方案中最值得参考的。** 关键可复用的设计要素：
1. 纯文本化层（pymupdf_rag）→ 把 PDF/DOCX 等复杂格式先转成纯文本
2. 分节抽取层（pdf.py）→ 按语义粒度拆成独立 prompt
3. 外部增强层（github.py）→ 引入"简历之外的真实数据"做交叉验证
4. 评分层（evaluator.py）→ 多维度 + 公平性约束 + 证据引用

## 🧠 核心源码解读

### 1. 分节抽取（pdf.py）

```python
# pdf.py（精简骨架）
class PDFHandler:
    def __init__(self, llm_provider: LLMProvider):
        self.llm = llm_provider

    def extract(self, markdown_text: str) -> JSONResume:
        sections = {
            "basics": self._extract_basics(markdown_text),
            "education": self._extract_education(markdown_text),
            "work": self._extract_work(markdown_text),
            "skills": self._extract_skills(markdown_text),
            "projects": self._extract_projects(markdown_text),
        }
        # 每节独立调用 LLM，并行执行
        results = await asyncio.gather(*sections.values())
        return JSONResume(**dict(zip(sections.keys(), results)))
```

**设计关键**：`asyncio.gather` 并行调用，不是串行。这和将整个简历喂给 LLM 让它一次输出全部的做法相比，速度更快（并行）、更准确（每节走独立 prompt）。

### 2. Pydantic Schema 强约束（models.py）

```python
# models.py（精简骨架）
from pydantic import BaseModel, Field
from datetime import date

class Education(BaseModel):
    institution: str = Field(..., description="学校名称，必填")
    degree: str | None = Field(None, description="学位，可选")
    start_date: date | None = None
    end_date: date | None = None
    gpa: float | None = Field(None, ge=0, le=4.0)

class JSONResume(BaseModel):
    basics: Basics | None = None
    education: list[Education] = []
    work: list[Work] = []
    skills: list[Skill] = []
    projects: list[Project] = []
```

**设计关键**：不是宽松的 `dict` 而是强类型 Pydantic Schema。LLM 输出的 JSON 必须匹配这些 Schema 才能继续管线，否则报错重试。这比"让 LLM 自由输出、后续再清洗"的方式更可靠。

### 3. GitHub 信号增强（github.py）

```python
# github.py（精简骨架）
class GitHubEnricher:
    async def enrich(self, resume: JSONResume) -> JSONResume:
        username = self._extract_github_username(resume.basics.profiles)
        if not username:
            return resume  # 没有 GitHub → 跳过增强

        profile = await self._fetch_profile(username)
        repos = await self._fetch_repos(username)

        classified = await self._classify_repos(repos)
        top7 = await self._select_top7(classified, resume)

        resume.projects.github_repos = top7
        return resume
```

**设计关键**：不是盲目地拉所有仓库。在提取 Top 7 时，LLM 被要求考虑"最少作者提交阈值"（minimum author commit threshold）和"与简历的相关度"——这意味着只看候选人真正贡献过的仓库，不把 fork 或只改了 README 的仓库算进去。

## 📐 架构决策与设计哲学

- **为什么用 Jinja 而不是 F-string 拼接 prompt？** 因为 Jinja 模板天然支持继承、嵌套、条件判断——F-string 拼 prompt 在 prompt 超过 10 个时就是灾难。`template_manager.py` 提供了模板加载 + 变量注入的统一入口。
- **为什么选择 JSON Resume 标准？** 因为它是开放标准（jsonresume.org），结构化抽取出的数据直接兼容其他简历工具。这是"用标准打败专用"的工程决策。
- **开发模式缓存设计**：`DEVELOPMENT_MODE=True` 时，每一步的中间产物都落盘到 `cache/` 目录。调试时不需要重复调用 LLM，省 Token 又省时间。这是 Agent 管线开发中"被低估但极其有价值"的工程实践。

## 🌐 全网口碑画像

### 好评共识

- **管线设计清晰**：中文社区评测（txtmix.com、CSDN）普遍认可"不是黑盒，每一步都能看中间产物"的设计理念，认为是"AI 招聘工具中的标杆架构"。
- **本地运行满足合规**：Ollama 后端的支持被高度评价，企业 HR 部门可在完全不联网的环境下运行。
- **Prompt 模板解耦值得学习**：多个评测指出"把 prompt 放在 Jinja 模板里、和代码解耦"的做法值得所有 AI Agent 项目借鉴。

### 差评共识 & 踩坑高发区

- **大规模部署缺多线程/异步优化**：当前实现是逐份简历串行处理，1000 份简历时总耗时不可接受。Issue 中有用户提出"每份简历异步 + 批量并发"的 feature request。
- **非技术岗位评分维度不匹配**：评分 prompt 明显按技术岗位设计，创意/设计/销售类简历评分会失真。需自行修改 `prompts/templates/` 适配。
- **GitHub 信号在候选人无公开仓库时失效**：对于没有公开 GitHub 活动的候选人，`github.py` 增强步骤跳过，评分维度权重偏重"自述内容"。

### 争议焦点

- **LLM 打分的稳定性**：同一个简历在 Ollama（gemma3:4b）上跑 3 次会得到 3 个不完全相同的分数。项目通过 `fairness constraints` 和证据引用机制来限制随机性，但不能完全消除。这是所有 LLM 做评估类任务的固有挑战。
- **评分透明性 vs 幻觉风险**：项目强调"每个 score 必须引用 evidence"——但如果 LLM 在生成 evidence 时产生幻觉（引用不存在的项目），那透明性反而变成假透明。

## ⚔️ 竞品对比

| 维度 | Hiring Agent | 通用 ChatGPT 简历分析 | 商业 ATS AI 评分 |
|------|-------------|---------------------|-----------------|
| **架构** | 显式 ETL 管线 | 单轮对话 | 黑盒 API |
| **可审计性** | ✅ 每步有产物、可重跑 | ❌ 不可复现 | 部分 |
| **GitHub 交叉验证** | ✅ 仓库分类 + Top 7 选择 | ❌ 不自动做 | 通常不做 |
| **公平性约束** | ✅ fairness constraints 显式编码 | ❌ 无 | 有（闭源） |
| **本地运行** | ✅ Ollama 完全离线 | ❌ 需联网 | ❌ |
| **非技术岗位适配** | ❌ 需要改 prompt | ✅ 自由的 chat | ✅ 多维度配置 |
| **批量处理** | ❌ 串行（Issue 中已有 PR） | ❌ 手动 | ✅ 原生支持 |
| **成本** | 0（Ollama） | 按 Token 计费 | 按简历收费 |

**与竞争对手的本质差异**：Hiring Agent 不是"让 AI 帮你打分"，而是"给你一个可重复、可审计、可修改的评分管线"。它把 AI 招聘从"黑盒"变成了"白盒"。

## 🎯 核心研判

### 项目优势

**Hiring Agent 最大的价值不是作为"简历评分工具"（这个功能可以用 ChatGPT 更随意地做），而是作为「如何用 LLM 构建结构化数据管线的模板」——它的架构设计、分节抽取、Schema 约束、模板驱动等设计模式，能直接复用到任何需要从非结构化文本中提取结构化信息的场景（合同解析、病历抽取、论文元数据提取等）。**

### 项目风险

- **单份简历的 LLM 调用量（11-14 次）在批量场景下成本显著**：1000 份简历 × 12 次调用 = 12,000 次 LLM 调用。即使 Ollama 本地运行免费，时间成本也需要考虑。
- **非技术岗位的天然不适应**：评分维度 built for tech，偏离此范围的场景需要较大改造。
- **GitHub 信号的偏差问题**：有活跃 GitHub 的候选人会获得加分（无论代码质量如何），没有的则可能被系统低估——这对资深但不开源的工作者不公平。

### 适用场景 & 不适用场景

**适合**：技术岗位初筛（大批量投递）/ Prompt 工程教学 / 想自己做定制化招聘管线的团队 / 需要完全离线运行的 HR 场景

**不适合**：非技术岗位评估 / 求职量少的场景（管线搭建成本 > 收益）/ 合规禁止 AI 介入招聘的场景 / 候选人没有公开代码活动历史的场景

### 趋势判断

**稳定增长期。** InterviewStreet（HackerRank 母公司）的背书让项目有持续维护的保障。但 3,970⭐ 和有限的社区 PR 说明它目前还是"小而精"的工具，距离企业级大规模部署还有一段路。关键看 InterviewStreet 是否会把它集成到 HackerRank 企业版中。

## 📂 关键文件路径速查

| 文件 | 位置 | 说明 |
|------|------|------|
| 编排器（入口） | `score.py` | 串起整条管线 |
| PDF 文本化 | `pymupdf_rag.py` | PDF 页 → Markdown |
| 分节抽取 | `pdf.py` | Markdown → 结构化 JSON |
| GitHub 增强 | `github.py` | 仓库分类 + Top 7 选择 |
| 公平评分 | `evaluator.py` | 多维评分 + 约束 |
| 数据 Schema | `models.py` | Pydantic + JSON Resume 标准 |
| 模板管理器 | `prompts/template_manager.py` | Jinja 模板加载 |
| 抽取 Prompt 模板 | `prompts/templates/` | 10 个 section 级模板 |
| 评分模板 | `prompts/templates/resume_evaluation_*.jinja` | 评分逻辑模板 |
| 配置（开发模式） | `config.py` | 缓存/CSV 输出控制 |
