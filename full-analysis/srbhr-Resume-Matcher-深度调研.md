# 🔬 srbhr/Resume-Matcher - 全方位深度调研

## 📌 一句话定位

**本地运行、100+ LLM 支持的 AI 简历构建 + 职位匹配优化平台**——不只是一次性匹配打分，而是覆盖从简历创建（Wizard）、解析、关键词提取、ATS 模拟、针对性优化到求职跟踪的完整求职工作流。核心差异在于：**AI 不只是分析简历，而是直接生成优化后的版本并与原文做 diff 展示**。

## ⭐ 项目亮点

- **Resume Diff 优化展示**：不是简单给个分数或建议，而是用 AI 直接生成优化版简历，并通过行级 diff（`ResumeFieldDiff`）精确展示"删了什么、加了什么、改了哪里"。用户可以逐条审计 AI 的修改，这是同类工具中极其少见的设计（[improver.py DiffConfidence](https://github.com/srbhr/Resume-Matcher/blob/main/apps/backend/app/services/improver.py)）。
- **100+ LLM 提供商支持**：基于 `litellm.Router`，只需一个配置就能接入 OpenAI/Claude/Gemini/Ollama/DeepSeek 等所有主流 LLM。router 层自带超时、重试、降级策略（`RetryPolicy`）——甚至支持本地 Ollama 零成本运行。
- **完整求职工作流而非单点功能**：Resume Wizard（向导式简历创建）、PDF 生成（MarkItDown 解析 + Playwright 渲染）、ATS 模拟、职位描述导入、求职申请追踪、AI 求职信生成。从上手到投递的全链路覆盖。
- **Prompt Injection 防护**：`improver.py` 内置正则注入检测（LLM-011），对 `"ignore all previous instructions"` 等 8 种注入模式进行 REDACTED 处理，保护 LLM 在用户输入中的调用链不被劫持。
- **TinyDB → SQLite 数据迁移**：启动时自动检测旧 TinyDB 数据库并迁移到 SQLite，无损兼容历史数据。这个细节体现了作者对用户数据持续性的重视（[main.py lifespan](https://github.com/srbhr/Resume-Matcher/blob/main/apps/backend/app/main.py)）。

## 🏗️ 项目架构全景

```
Resume-Matcher/
├── apps/
│   ├── backend/                          # FastAPI 后端
│   │   ├── app/
│   │   │   ├── main.py                   # FastAPI 入口 + lifespan 管理
│   │   │   ├── config.py                 # 配置（加密存储 API Keys）
│   │   │   ├── database.py               # SQLite 数据库
│   │   │   ├── llm.py                    # LiteLLM Router 封装（100+ 提供商）
│   │   │   ├── pdf.py                    # PDF 渲染（Playwright）
│   │   │   ├── models.py                 # SQLAlchemy 模型
│   │   │   ├── schemas/                  # Pydantic schemas
│   │   │   ├── routers/                  # API 路由
│   │   │   │   ├── resumes.py            # 简历 CRUD
│   │   │   │   ├── enrichment.py         # AI 增强端点
│   │   │   │   ├── jobs.py               # 职位管理
│   │   │   │   ├── applications.py       # 求职申请
│   │   │   │   └── resume_wizard.py      # 简历向导
│   │   │   └── services/                 # 业务逻辑层
│   │   │       ├── parser.py             # PDF/DOCX 解析（MarkItDown + LLM）
│   │   │       ├── improver.py           # AI 简历优化（核心引擎）
│   │   │       ├── refiner.py            # 简历精炼（针对特定 JD）
│   │   │       ├── cover_letter.py       # AI 求职信生成
│   │   │       └── resume_wizard.py      # 向导式简历创建
│   │   └── e2e_monitor/                  # 端到端监控（agent playbook）
│   └── frontend/                         # Next.js 前端
│       ├── app/(default)/
│       │   ├── builder/                  # 简历构建器（拖拽组件）
│       │   ├── tailor/                   # 简历优化（Resume Diff）
│       │   ├── tracker/                  # 求职申请跟踪器
│       │   ├── dashboard/                # 仪表盘
│       │   └── settings/                 # LLM 配置
│       └── components/                   # UI 组件
├── Dockerfile                            # Docker 部署
└── README.md                             # 多语言文档
```

### 三层架构

1. **FastAPI 后端** — 业务逻辑 + AI 调度 + 数据持久化
2. **Next.js 前端** — 用户界面 + 拖拽式简历编辑器 + Diff 对比 UI
3. **LiteLLM Router** — 统一的 LLM 提供商抽象层

### 加密配置系统（config.py）

API Keys 通过 Python 的 `cryptography` 库加密存储在 `config.json` 中（而不是明文存储或环境变量）。启动时通过 `migrate_legacy_keys()` 将旧的明文 key 自动折叠到加密存储后删除明文。这是 README 没提但值得关注的安全设计。

## 💡 应用场景与启发

### 典型使用场景

| 场景 | 描述 | 推荐指数 |
|------|------|---------|
| **求职简历针对优化** | 导入目标 JD → AI 分析关键词差距 → 自动修改简历并展示 Diff | ⭐⭐⭐⭐⭐ |
| **ATS 通过率提升** | 模拟 ATS 解析结果 → 修正格式/关键词覆盖率 | ⭐⭐⭐⭐ |
| **批量求职投递** | 下载多份 JD → 每份生成的优化简历 + 求职信 | ⭐⭐⭐⭐ |
| **学生/转行简历创建** | Resume Wizard 引导式创建，无需排版基础 | ⭐⭐⭐ |
| **HR 内部简历审核** | 对内测简历做一致性评分和盲审 | ⭐⭐⭐ |

### 可借鉴的解决方案模式

1. **LLM 调用的统一 Router 模式**：`llm.py` 用 `litellm.Router` 做了一层封装，定义了三种超时（health check=30s, completion=120s, JSON=180s），并设置 `drop_params=True` 让 LiteLLM 自动忽略模型不支持的参数。这种"配置驱动 + 统一降级"的 LLM 调用模式值得任何需要多 LLM 支持的项目参考。

2. **Resume Diff 审计机制**：AI 生成的修改不是直接覆盖原文，而是通过 `SequenceMatcher` → `ResumeFieldDiff` → `diff_strategy` 分步生成结构化 diff，用户可以逐条接受或拒绝。这种"AI 辅助 + 人工审核"的设计比"AI 全自动"更适合求职场景——因为简历修改有"事实准确性"红线（`CRITICAL_TRUTHFULNESS_RULES`）。

3. **Prompt Injection 防护层**：`_sanitize_user_input()` 在用户输入进入 LLM 前进行注入模式匹配（8 种正则模式），直接 REDACTED 处理。这是 LLM 应用的安全基线，很多项目却忽略了。

### 同类需求的可参考思路

- **「分析→生成→Diff→审核」四步流程**：不是让 AI 直接修改用户的简历（风险太高），而是分析 → 生成建议 → 展示差异 → 用户手工确认。这种设计哲学可以推广到任何需要 AI 修改用户内容的场景（如文档审阅、代码重构）。
- **MarkItDown 作为文档标准输入层**：使用微软的 `markitdown` 库（161K⭐）做 PDF/DOCX 的初始解析，再用 LLM 做结构化提取。parser.py 中还有 `restore_dates_from_markdown()` 函数——当 LLM 解析丢失月份信息时，从原始 Markdown 中找回完整日期（正则匹配）。这是"LLM 输出后处理"的优雅示范。

## 🧠 核心源码解读

### LiteLLM Router 封装（llm.py）

```python
litellm.drop_params = True
litellm.modify_params = True

class LLMConfig(BaseModel):
    provider: str
    model: str
    api_key: str
    api_base: str | None = None
    reasoning_effort: Literal["low", "medium", "high"] | None = None
```

`drop_params=True` 是关键一行——不同 LLM 提供商支持的参数不同（如 Anthropic 不支持 `reasoning_effort`），LiteLLM 默认会抛 `UnsupportedParamsError`。打开 `drop_params` 让 Router 自动忽略不支持的参数，避免每次切换模型时都要修改代码。

### Resume Diff 引擎（improver.py 的核心）

```python
@dataclass(frozen=True)
class DiffConfidence:
    added: str
    removed: str
    modified: str

_INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"disregard\s+(all\s+)?above",
    r"forget\s+(everything|all)",
    r"new\s+instructions?:",
    r"system\s*:",
    ...
]

def _sanitize_user_input(text: str) -> str:
    sanitized = text
    for pattern in _INJECTION_PATTERNS:
        sanitized = re.sub(pattern, "[REDACTED]", sanitized, flags=re.IGNORECASE)
    return sanitized
```

`DiffConfidence` 用 `@dataclass(frozen=True)` 确保不可变，`_sanitize_user_input` 用 8 条正则做注入检测。安全 + 数据完整性是 improver 模块的两大设计要点。

### PDF 解析流水线（parser.py）

```python
from markitdown import MarkItDown

_MD_DATE_RE = re.compile(
    r"(?:(?:Jan(?:uary)?|...)\.?\s+\d{4})"
    r"(?:\s*[-–—]\s*"
    r"(?:(?:Jan(?:uary)?|...)\.?\s+\d{4}"
    r"|Present|Current|Now|Ongoing))?",
    re.IGNORECASE,
)

def _extract_markdown_dates(markdown: str) -> list[str]:
    return _MD_DATE_RE.findall(markdown)

def restore_dates_from_markdown(parsed_data, markdown):
    md_dates = _extract_markdown_dates(markdown)
    # Build lookup: "2020 - 2021" → "Jun 2020 - Aug 2021"
    year_to_full = {...}
    # Replace year-only dates with month-inclusive versions
    ...
```

MarkItDown 做 PDF→Markdown 转换 → 正则提取所有含月份的完整日期 → LLM 解析结构化的 ResumeData → 如果 LLM 遗漏了月份信息（只输出"2020 - 2021"），用 `restore_dates_from_markdown` 从原始 Markdown 中找回完整日期并替换。**这个后处理步骤精巧地弥补了 LLM 在日期解析上的常见错误。**

## 🌐 全网口碑画像

### 好评共识

1. **"完整的求职工作流，不只是匹配打分"** — HelloGitHub 评测指出它覆盖了从创建到追踪的全流程，而不仅仅是简历匹配（[hellogithub.com](https://hellogithub.com/repository/fc771aa425d5489c8f1a1d71beb256f1)）。
2. **支持本地 Ollama 运行** — 知乎用户称赞"完全本地部署，数据不离开自己的电脑"，对隐私敏感用户有吸引力（[知乎](https://zhuanlan.zhihu.com/p/28735254019)）。
3. **Diff 对比功能是亮点** — 中文技术博客的评测认为"AI 直接展示修改了哪些内容，用户可以逐条审核"是区别于其他简历工具的核心差异。
4. **部署友好** — Docker 一键部署 + 多语言文档（中/英/日/西）降低了使用门槛。

### 差评共识

1. **安装过程需要多个组件** — 虽有一键 Docker，但本地运行需要 Node.js + Python + Playwright 浏览器等依赖，Setup 文档对非技术用户仍有门槛。
2. **LLM 解析准确率波动** — 解析简历时，复杂的格式（多列、表格内嵌、图形化简历）可能导致解析结果不准确。虽然 `restore_dates_from_markdown` 做了后处理，但非标准格式简历的解析仍是问题。
3. **AI 生成内容可能不准确** — 有用户反馈 AI 在优化简历时"添加了不存在的项目经验"——虽然 `CRITICAL_TRUTHFULNESS_RULES` 提示词试图约束，但 LLM 的幻觉问题无法完全消除，需要用户审计。
4. **前端编辑器的拖拽体验** — 部分用户反映简历构建器的拖拽组件在复杂布局下响应不够流畅。

### 社区状态

- 27K⭐ / 4.9K Fork，社区贡献活跃（Issue 响应较快）
- 维护者 srbhr 持续发布新版本（FastAPI + Next.js 全栈架构，2026 年仍在活跃开发）
- 有完备的测试基础设施（`apps/backend/tests/` 包含 unit + integration 测试）

## ⚔️ 竞品对比

| 维度 | Resume-Matcher | Reactive Resume | Novoresume (付费) | FlowCV (付费) |
|------|---------------|----------------|-------------------|--------------|
| 开源 | ✅ MIT | ✅ MIT | ❌ | ❌ |
| AI 增强 | ✅ 多 LLM 支持 | ❌ 纯手动 | ✅ 封闭模型 | ✅ 封闭模型 |
| 本地运行 | ✅ Docker/源码 | ✅ 自托管 | ❌ SaaS | ❌ SaaS |
| 简历解析 | ✅ MarkItDown + LLM | ❌ | ❌ | ❌ |
| 职位匹配 | ✅ Diff 展示 | ❌ | ✅ 分数 | ✅ 分数 |
| 求职信生成 | ✅ AI 生成 | ❌ | ✅ 模板 | ✅ 模板 |
| 拖拽编辑器 | ✅ Next.js | ✅ Vue | ✅ 自有 | ✅ 自有 |
| 数据隐私 | ✅ 完全本地 | ✅ 完全本地 | ❌ 云端 | ❌ 云端 |
| Stars | 27,615 | 30K+ | — | — |

### 选择建议

- **AI 优先 + 求职优化** → **Resume-Matcher**（唯一不牺牲 AI 能力的开源方案）
- **纯手动排版 + 隐私优先** → Reactive Resume（更成熟的编辑器体验）
- **不想折腾部署** → Novoresume / FlowCV（付费 SaaS，开箱即用）
- **企业批量简历处理** → 自建或 Resume-Matcher Docker 部署

## 🎯 核心研判

### 项目优势

- **开源 AI 简历品类的唯一成熟选手**：在"开源 + AI + 简历"交叉品类中，Resume-Matcher 是 Star 最多、功能最完整的。竞品要么不开源（付费 SaaS），要么没有 AI 能力。
- **隐私优势 vs SaaS**：所有数据本地存储 + 可选本地 Ollama 运行，对金融/法律/政府等受监管行业的求职者有不可替代的吸引力。
- **Diff 审计机制是设计标杆**：AI 不直接修改用户简历，而是生成结构化 Diff 供审核——这个设计理念在"AI 辅助创作"类应用中值得广泛借鉴。
- **工程代码质量扎实**：有单元测试（`test_resume_api.py`、`test_resume_diff.py`）、Claude.md 配置、完整的 E2E 监控（`e2e_monitor/AGENT_PLAYBOOK.md`）、注入防护、数据迁移，远超一般 27K⭐ 项目的代码组织。

### 项目风险

- **AI 幻觉在求职场景的敏感度极高**：AI 添加不存在的项目经验 = 简历造假。虽然 `CRITICAL_TRUTHFULNESS_RULES` 和 Diff 机制试图缓解，但核心风险无法根除。
- **非技术用户门槛**：依赖 Docker / Node / Python 的环境配置，对"只是想优化简历"的普通求职者来说，安装成本过高。
- **SaaS 化压力**：开源项目缺乏商业模式，维护者的长期投入动力存疑。同时 GitHub Copilot / ChatGPT 等通用工具也在逐步覆盖简历优化功能。
- **PDF 渲染稳定性**：Playwright 渲染（`pdf.py`）在 Linux 服务器上需要额外的系统依赖（字体、Chromium），Docker 中虽然已配置，但仍有偶尔的渲染偏差。

### 趋势判断：稳定增长期

作为开源 AI 简历工具的事实标准，Resume-Matcher 会随着 LLM 能力提升和求职市场活跃而持续获取用户。面临的主要挑战是：如何平衡"AI 自动化的便利性"和"简历修改的真实性红线"。

## 📂 关键文件路径速查

| 文件 | 路径 | 作用 |
|------|------|------|
| 应用入口 | `apps/backend/app/main.py` | FastAPI 启动 + 数据库迁移 + PDF 渲染初始化 |
| LLM Router | `apps/backend/app/llm.py` | LiteLLM 封装，100+ 提供商 + 超时/重试/降级 |
| 简历解析 | `apps/backend/app/services/parser.py` | MarkItDown 解析 + LLM 结构化提取 + 日期修复 |
| 简历优化 | `apps/backend/app/services/improver.py` | AI Diff 引擎 + 注入防护 + 真实性规则 |
| 求职信生成 | `apps/backend/app/services/cover_letter.py` | AI 求职信生成器 |
| 配置加密 | `apps/backend/app/config.py` | API Key 加密存储 + 旧 key 迁移 |
| 前端入口 | `apps/frontend/app/(default)/page.tsx` | Next.js 首页 |
| 简历构建器 | `apps/frontend/app/(default)/builder/page.tsx` | 拖拽式简历编辑器 |
| 简历优化页 | `apps/frontend/app/(default)/tailor/page.tsx` | Resume Diff 对比 UI |
| 求职跟踪器 | `apps/frontend/app/(default)/tracker/page.tsx` | 申请进度看板 |
| 多语言 README | `README.zh-CN.md` | 中文文档 |
| Docker 部署 | `Dockerfile` | 一键部署配置 |
