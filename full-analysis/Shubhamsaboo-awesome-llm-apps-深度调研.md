# Shubhamsaboo/awesome-llm-apps 深度调研报告

> **调研日期**: 2026-06-27  
> **项目地址**: https://github.com/Shubhamsaboo/awesome-llm-apps  
> **当前指标**: ⭐ 115,829 Stars | 🍴 17,227 Forks | 👀 1,177 Watchers | 仅 5 Open Issues  
> **协议**: Apache-2.0 | **主语言**: Python | **创建于**: 2024-04-29

---

## 一、一句话定位

**100+ 开箱即用的 AI Agent 与 RAG 应用模板库 —— 不是收藏夹，而是"跑得起来、改得动、发得了"的实战级代码集市。**

由 Google Cloud AI 产品经理 Shubham Saboo 维护，以"Code-First"理念打造，每个模板都是原创的、端到端可运行的独立应用。它定位为 LLM 应用开发的"乐高积木桶"——开发者能在 3 条命令内完成克隆、跑通、定制的全流程。

---

## 二、项目亮点

### 1. 超大规模实战模板矩阵（100+ 可跑应用，254+ 源文件）

在一个仓库中集中了从单文件 Agent 到完整多 Agent 协作团队的庞大模板集合：
- `starter_ai_agents/` — 20 个 .py 文件，单文件就能跑的入门模板
- `advanced_ai_agents/` — 254 个 .py 文件，覆盖生产级 Agent、MCP、多 Agent Teams
- `rag_tutorials/` — 32 个 .py 的完整 RAG 教程
- `voice_ai_agents/`、`mcp_ai_agents/`、`always_on_agents/` 等共计 12 个一级分类

单个仓库承载了 **15 个品类**、覆盖 LLM 应用开发全栈（Agents·RAG·MCP·Voice·Fine-tuning），在模板数量和质量上均为 GitHub 同类项目之最。

### 2. 源码级可复现，"3 命令上手" 真正落地

项目克服了行业内普遍存在的"收藏即吃灰"问题——每个模板都附有独立的 `requirements.txt`、完整的 Streamlit 前端、明确的 `.env.example`。以 AI Travel Agent 为例：

```bash
git clone https://github.com/Shubhamsaboo/awesome-llm-apps.git
cd awesome-llm-apps/starter_ai_agents/ai_travel_agent
pip install -r requirements.txt
streamlit run travel_agent.py
```

这在 GitHub LLM 项目中极罕见，绝大多数类似项目只提供代码片段或 README-only 的架构说明。

### 3. 紧追技术前沿，热点响应极快

从项目 Issues 和目录可以清晰看到响应速度：
- **MCP (Model Context Protocol)** 爆发后，`mcp_ai_agents/` 立刻上线
- **DeepSeek R1** 本地部署很快有对应 Demo
- **Voice AI Agents** 板块紧跟 Gemini Live 和实时语音
- Issues 列表中社区持续提交新模板提案（如 FlintAPI、VORTEXRAG、BuyWhere），维护者审核并合并速度快 —— 典型的社区驱动节奏

### 4. 供应商无关，框架无关的设计哲学

支持 Claude·Gemini·OpenAI·xAI·Qwen·Llama，底层框架同时兼容 **Agno**（前 Phidata）、**AutoGen**（AG2）、**LangChain**、**LlamaIndex**、**ADK**。这意味着开发者可以在一个项目里对比学习多种框架的实现差异，这在市面上几乎找不到第二家。

### 5. 低 Issue 积压 + 高活跃度的健康社区信号

115k Star 级别的项目居然只有 **5 个 Open Issues**，且最近推送日期为 2026-06-15，说明维护者活跃且社区贡献规范良好。对比许多"百万 Star、Issue 也过万"的项目，其维护质量令人印象深刻。

---

## 三、项目架构全景

```
awesome-llm-apps/
├── starter_ai_agents/        # 入门级 - 单文件、单 API Key 即可运行
│   ├── ai_travel_agent/      # 搜索+规划+日历导出
│   ├── ai_music_generator/   # 音乐生成
│   ├── ai_medical_imaging/   # 医学影像分析
│   ├── ai_meme_generator/    # 表情包生成（Browser Use）
│   ├── mixture_of_agents/    # 多模型混合推理
│   └── ... 共 15 个子模板
│
├── advanced_ai_agents/       # 进阶 - 生产级 Agent 与多 Agent 团队
│   ├── single_agent_apps/    # 单 Agent 深度应用
│   │   ├── ai_customer_support_agent/  # 含 Mem0 持久记忆
│   │   ├── ai_deep_research_agent/     # 深度研究 Agent
│   │   ├── ai_investment_agent/        # 投资分析
│   │   └── ... 10+ 模板
│   ├── multi_agent_apps/     # 多 Agent 协作团队
│   │   ├── agent_teams/      # 行业 Agent 团队
│   │   │   ├── ai_finance_agent_team/  # 金融分析团队
│   │   │   ├── ai_legal_agent_team/    # 法律协作组
│   │   │   ├── ai_recruitment_agent_team/ # 招聘团队
│   │   │   ├── ai_sales_intelligence_agent_team/ # 销售洞察
│   │   │   ├── ai_seo_audit_team/     # SEO 审计团队
│   │   │   └── ... 15+ 行业团队
│   │   ├── ai_news_and_podcast_agents/ # 新闻+播客全栈 Beifong
│   │   ├── devpulse_ai/     # 开发者信号情报系统
│   │   └── product_launch_intelligence_agent/
│   └── autonomous_game_playing_agent_apps/ # 游戏 Agent
│       ├── ai_chess_agent/
│       ├── ai_tic_tac_toe_agent/
│       └── ai_3dpygame_r1/
│
├── always_on_agents/         # 7 x 24 常驻 Agent
│   ├── always_on_hn_briefing_agent/
│   └── ...
│
├── voice_ai_agents/          # 语音 AI Agent
│   ├── insurance_claim_live_agent_team/  # Gemini Live 实时理赔
│   └── ...
│
├── mcp_ai_agents/            # MCP 协议 Agent
│   └── ...
│
├── rag_tutorials/            # RAG 教程体系（32 文件）
│   ├── chat_with_pdf/
│   ├── local_rag/            # 离线 RAG（Ollama + Llama3）
│   └── ...
│
├── generative_ui_agents/     # 生成式 UI / Agentic 前端
├── awesome_agent_skills/     # Agent 技能包（Skill 体系）
├── ai_agent_framework_crash_course/ # 框架速成课
├── docs/                     # 文档与素材
└── .github/workflows/        # CI/CD
```

### 架构分层逻辑

项目本质上是一个 **三层金字塔** 结构：

| 层级 | 目录 | 定位 | 适用人群 |
|------|------|------|----------|
| **基础层** | `starter_ai_agents/` | 单文件、单 Key、30 秒上手 | 初学者、产品经理做原型 |
| **进阶层** | `advanced_ai_agents/` | 多 Agent、记忆、工具链 | 进阶开发者、创业团队 |
| **前沿层** | `mcp_ai_agents/`, `voice_ai_agents/`, `always_on_agents/` | 最新技术范式的实验场 | 技术探索者、架构师 |

---

## 四、应用场景与启发

### 场景 1：初创团队快速搭建 AI MVP

**痛点**：创业团队想快速验证 AI 产品理念，但开发 Agent 需要同时搞定 LLM 接入、工具链、状态管理。

**方案**：直接在 `starter_ai_agents/` 中找到最接近的场景模板，替换 API Key 即可跑通 Demo。例如想做"AI 旅行规划"的产品，直接克隆 AI Travel Agent，把 SerpAPI 换成自有数据源，把 Streamlit UI 改成移动端即可。

**启发**：每个模板本质上是一个"领域对象"的 Agent 封装。开发者不应停留于"跑通它"，而应该关注 **模板的输入/输出抽象层** —— 比如 Travel Agent 的 `generate_ics_content()` 函数（将文本行程转成 .ics 日历文件）就是一个很好的输出端适配器模式。

### 场景 2：企业客服系统的记忆增强

**痛点**：基础 RAG 只能回答"当前文档"的问题，无法记住用户的历史偏好。

**方案**：`ai_customer_support_agent/` 展示了如何用 **Mem0 + Qdrant** 实现持久记忆层，代码结构清晰：

```python
class CustomerSupportAIAgent:
    def __init__(self):
        self.memory = Memory.from_config(config)  # Mem0 + Qdrant
        self.client = OpenAI()

    def handle_query(self, query, user_id=None):
        relevant_memories = self.memory.search(query=query, user_id=user_id)
        context = "Relevant past information:\n"
        for memory in relevant_memories["results"]:
            context += f"- {memory['memory']}\n"
        response = self.client.chat.completions.create(...)
        self.memory.add(query, user_id=user_id, ...)
        return answer
```

**启发**：这段代码暴露了一个重要的架构决策 —— **记忆层不是 LLM 的附属品，而是 Agent 的一等公民**。在企业落地时，可以将此模式推广到 CRM 集成、工单系统对接等场景。

### 场景 3：多 Agent 协作处理复杂任务

**痛点**：单 Agent 领域知识有限，信息收集与分析分离困难。

**方案**：`multi_agent_researcher/` 展示了基于 **Agno Team** 的多角色分工：

```python
hn_researcher = Agent(name="HackerNews Researcher", tools=[HackerNewsTools()])
web_searcher = Agent(name="Web Searcher", tools=[DuckDuckGoTools()])
article_reader = Agent(name="Article Reader", tools=[Newspaper4kTools()])

hackernews_team = Team(
    name="HackerNews Team",
    members=[hn_researcher, web_searcher, article_reader],
    instructions=[
        "First, search hackernews for what the user is asking about.",
        "Then, ask the article reader to read the links...",
        "Then, ask the web searcher to search for each story...",
        "Finally, provide a thoughtful and engaging summary.",
    ],
    show_members_responses=True,
)
```

**启发**：**Agent Team 本质上是"带工具的微服务编排"**，每个 Agent 是独立的"能力单元"，通过声明式指令实现协作。企业可以把这个模式映射到业务岗位上（如市场调研员+数据分析师+文案写手的 AI 版本）。

### 场景 4：离线/本地 RAG 数据安全

**痛点**：金融、医疗等行业要求数据不出本地。

**方案**：`rag_tutorials/local_rag/` 演示了用 **Ollama + Llama3** 完全离线运行 RAG，量化版模型使内存占用降低 58%。这在医疗影像 Agent（已实现胸片初筛 9 秒/例）等场景中直接可用。

### 场景 5：实时语音 + AI Agent 客服

**痛点**：IVR（交互式语音应答）系统体验差，用户需要自然语言对话。

**方案**：`insurance_claim_live_agent_team/` 展示用 **Gemini Live + ADK** 构建实时语音理赔流程，这在保险、银行等场景有直接商业化价值。

### 场景 6：MCP 协议集成工具

**痛点**：Agent 如何统一接入外部工具？

**方案**：`mcp_ai_agents/` 板块展示了 MCP 协议的 Agent 集成方式，这意味着任何 MCP 兼容工具（文件系统、数据库、Web API）都可以零摩擦接入 Agent。

---

## 五、核心源码解读

### 5.1 AI Travel Agent — 双 Agent 协作模式 (travel_agent.py)

这是项目最热门的入门模板，展示了"研究员 + 规划师"双 Agent 模式。关键架构在于用两层 Agent 实现搜索、分析、规划、导出的完整链路：

```python
researcher = Agent(
    name="Researcher",
    role="Searches for travel destinations...",
    model=OpenAIChat(id="gpt-4o", api_key=openai_api_key),
    tools=[SerpApiTools(api_key=serp_api_key)],
)

planner = Agent(
    name="Planner",
    role="Generates a draft itinerary...",
    model=OpenAIChat(id="gpt-4o", api_key=openai_api_key),
)
```

**架构启示**：将"搜索"和"规划"解耦为两个独立 Agent，各自有明确的 role 和 tools，再组合成 Workflow。这个模式可以复用到任何"信息收集、决策输出"类场景（如竞品分析、学术综述）。

### 5.2 Customer Support Agent — 记忆层设计 (customer_support_agent.py)

这个模板的核心价值在于 **Mem0 持久记忆的工程化封装**。通过 `handle_query()` 统一封装了记忆搜索、上下文构建、LLM 推理、记忆存储的完整循环：

```python
class CustomerSupportAIAgent:
    def __init__(self):
        config = {
            "vector_store": {
                "provider": "qdrant",
                "config": {"host": "localhost", "port": 6333},
            }
        }
        self.memory = Memory.from_config(config)
        self.client = OpenAI()
        self.app_id = "customer-support"

    def handle_query(self, query, user_id=None):
        relevant_memories = self.memory.search(query=query, user_id=user_id)
        context = "Relevant past information:\n" + ...
        response = self.client.chat.completions.create(...)
        self.memory.add(query, user_id=user_id, ...)
        return answer
```

**关键设计要点**：
- 用 `user_id` 隔离不同用户的记忆空间，这是生产级必须的
- 支持 `generate_synthetic_data()` 生成模拟用户数据用于测试
- 异常处理覆盖了内存初始化失败、查询超时等边界情况

### 5.3 Multi-Agent Researcher — 工具编排模式 (research_agent.py)

展示了 Agno Team API 的多 Agent 编排，核心设计是 **声明式指令驱动 + 成员响应可见**：

```python
hackernews_team = Team(
    name="HackerNews Team",
    model=OpenAIChat(id="gpt-4o-mini"),
    members=[hn_researcher, web_searcher, article_reader],
    instructions=[
        "First, search hackernews...",
        "Then, ask the article reader to read the links...",
        "Then, ask the web searcher to search...",
        "Finally, provide a thoughtful summary.",
    ],
    markdown=True,
    debug_mode=True,
    show_members_responses=True,
)
```

**架构启示**：`show_members_responses=True` 暴露了 Agent 团队的"思考链"，解决了 LLM 应用的最大痛点 —— **黑盒问题**。在企业落地时可以把这个开关当作审计日志来用。

---

## 六、架构决策与设计哲学

### 6.1 "Code-First" 而非 "Link-Collection"

与传统的 Awesome List（只收集链接）形成根本区别。项目中的所有模板都是 **原创编写、端到端可运行** 的，而非从别处搬运。每个子目录自包含全套代码 + `requirements.txt` + 独立的 README。

### 6.2 Streamlit 统一 UI 层

几乎所有模板都基于 **Streamlit** 构建交互界面。这一决策带来三大好处：
- **零前端成本**：不需要学 React/Vue，纯 Python 就能做 Web UI
- **一键分享**：`streamlit run` + `streamlit share` 即可部署
- **学习曲线最低**：初学者把注意力放在 Agent 逻辑而非 UI 上

### 6.3 框架无关的开放生态

这是该项目区别于 `openai-cookbook` 和 `langchain templates` 的核心差异点。项目内同时存在以下框架的实现：
- **Agno**（原 Phidata）— 大量 starter 和 multi-agent 使用
- **ADK**（Google Agent Development Kit）— always_on_agents 板块
- **AutoGen/AG2** — 部分多 Agent 团队
- **mem0** — 记忆层
- **Browser Use** — 浏览器自动化 Agent

这种"多框架共存"的设计看似杂乱，实则给学习者提供了 **横向对比框架能力的绝佳机会**。

### 6.4 学习路径的三级金字塔

```
入门 -> starter_ai_agents/     (单文件，30秒跑通)
进阶 -> advanced_ai_agents/    (多Agent，生产级设计)
前沿 -> mcp/voice/always_on/   (最新范式实验场)
```

这不像教学课程那样有前后依赖，而是允许开发者**按需取材**。

### 6.5 从 Issues 看社区治理

从 Issues 分析可以观察到项目健康度：
- 只有 1 个 open issue（建议添加 FlintAPI）
- 关闭的 Issues 中有大量社区提交的新模板（VORTEXRAG、BuyWhere、OpenAgent）
- 维护者批量关闭旧 Issue，并用标准回复快速处理 PR
- 但同时也意味着 **Issue 作为新模板提交渠道的噪音较高**，缺乏正式贡献指南

---

## 七、全网口碑画像

### 中文社区反馈汇总

**正面评价（高频关键词）**：

1. **"实战圣经"** — CSDN 多篇文章称其为"LLM 应用开发的实战圣经"或"活的代码教科书"
2. **"乐高积木桶"** — 形容开发者可自由组合模板中的代码片段
3. **"从调包侠到应用架构师"** — 认为项目能帮助开发者完成能力跃迁
4. **"全网最好的 LLM 应用开发资源"** — 多个中文技术博客给予极高评价
5. **"代码质量高、更新速度快"** — 知乎文章指出其紧跟 MCP、DeepSeek R1 等热点

**中文技术媒体的评价（引自 CSDN 和知乎）**：

- "你不应该每次都从零开始重建同样的 RAG 流水线、Agent 循环或 MCP 集成。"（项目README 翻译，被中文媒体广泛引用）
- "不是一份简单的链接收藏夹，而是一本活的代码教科书"
- "对求职者或学生，建议 Clone 下来，把 API 调用改为本地 Ollama 调用，把英文提示词改为中文提示词，针对国内场景集成"

**建设性意见**：
- 部分中文开发者反映仓库缺少 **中文 README 和中文注释**（虽然提供了中文翻译链接，但代码内注释仍为英文）
- 一些模板的 `.env.example` 不够完善，初次上手可能遇到 API Key 格式问题
- 项目体量快速膨胀，新手可能不知从何入手

---

## 八、竞品对比

| 维度 | awesome-llm-apps | openai-cookbook | langchain-templates |
|------|-----------------|-----------------|---------------------|
| **Star 数** | 115k | 60k+ | 3.5k |
| **模板量** | 100+ | ~50 个notebook | ~30 个模板 |
| **是否可独立运行** | 是（Streamlit UI） | 否（仅 Notebook） | 部分（需 langserve） |
| **框架绑定** | 无（多框架共存） | 强绑定 OpenAI | 强绑定 LangChain |
| **UI 层** | Streamlit 内置 | 无 UI | LangServe API |
| **多 Agent 覆盖** | 15+ 行业团队 | 无 | 有限 |
| **MCP/Voice 覆盖** | 有专用板块 | 无 | 无 |
| **学习曲线** | 低（3 命令上手） | 中（需懂 Jupyter） | 中（需懂 LangChain） |
| **生产级考虑** | 记忆、工具链齐全 | 偏教学 | 偏 API 展示 |

### 关键差异分析

1. **vs openai-cookbook**: openai-cookbook 本质是 OpenAI 官方的 Jupyter Notebook 集合，重在"教学概念"而非"可以部署的应用"。awesome-llm-apps 则强调"可以跑、可以改、可以上线"。

2. **vs langchain-templates**: LangChain Templates 是 LangChain 官方的部署模板，学习曲线陡峭（需懂 LangServe、LangGraph），且强绑定 LangChain 生态。awesome-llm-apps 的框架无关性使其更通用。

3. **项目独特优势**: 
   - **唯一自带完整 UI 的模板集合**
   - **唯一支持多框架对比学习**
   - **唯一覆盖从 RAG 到 MCP 到 Voice 全栈**
   - **模板数量最多、细分场景最全**

---

## 九、核心研判

### 优势

1. **信息密度极高**：一个仓库 = 100 个可运行的 AI 应用，对学习者和开发者都有极大参考价值
2. **维护质量惊人**：115k Star 仅 5 个 Open Issue，活跃维护是长期价值的重要保障
3. **技术前瞻性强**：从 MCP 到 Gemini Live 实时语音，热点出现后几天内就有对应模板
4. **零门槛上手**：Streamlit + requirements.txt 的"三命令方案"几乎消除了所有入门障碍
5. **开源友好**：Apache-2.0 协议允许商业使用，社区贡献活跃

### 局限性

1. **规模膨胀风险**：项目从 30k Star 时的几十个模板膨胀到 100+，新手"不知道从哪看起"的问题越来越突出，缺少一个"场景匹配问卷"或"路径推荐"
2. **深度不及广度**：每个模板多为"概念验证"级别，在错误处理、日志、监控、生产部署方面覆盖不足
3. **框架混杂可能困扰初学者**：Agno/ADK/AutoGen 等框架混用，对只想学某个框架的初学者来说干扰较大
4. **缺少系统化的贡献指南**：虽然社区贡献活跃，但从 Issues 看缺乏正式的 CONTRIBUTING.md 和模板开发规范

### 综合评价

**这是一本"活的" LLM 应用开发百科全书，而不是一本读完就扔在书架上的技术书。** 它是目前 GitHub 上覆盖面最广、可运行性最强的 AI Agent 实战资源。对于想快速上手 AI 应用开发的团队和个人，这几乎是"绕不开"的项目。

但需要注意：模板的核心价值不在于直接"复制到生产"，而在于 **作为架构参考和快速原型工具**。真正的生产级落地还需要在可靠性、可观测性、成本控制等方面做大量补充工作。

---

## 十、关键文件路径速查

### 入门级模板

| 路径 | 核心文件 | 一句话功能 |
|------|----------|-----------|
| `starter_ai_agents/ai_travel_agent/` | `travel_agent.py` | 搜索+规划+日历导出的双 Agent 旅行规划 |
| `starter_ai_agents/ai_data_analysis_agent/` | `data_analysis_agent.py` | 自然语言驱动的数据分析 |
| `starter_ai_agents/ai_medical_imaging_agent/` | `medical_imaging_agent.py` | Vision Transformer 医学影像诊断 |
| `starter_ai_agents/ai_music_generator_agent/` | `music_generator_agent.py` | AI 音乐生成 |
| `starter_ai_agents/ai_meme_generator_agent_browseruse/` | `meme_generator_agent.py` | Browser Use 表情包生成 |
| `starter_ai_agents/xai_finance_agent/` | `finance_agent.py` | xAI Grok 驱动的金融分析 |
| `starter_ai_agents/mixture_of_agents/` | `mixture_of_agents.py` | 多模型混合推理（MoA 架构） |
| `starter_ai_agents/web_scraping_ai_agent/` | `web_scraping_agent.py` | AI 驱动的智能网页爬虫 |

### 高级 Agent 模板

| 路径 | 核心文件 | 一句话功能 |
|------|----------|-----------|
| `advanced_ai_agents/single_agent_apps/ai_customer_support_agent/` | `customer_support_agent.py` | 基于 Mem0 记忆的客服系统 |
| `advanced_ai_agents/single_agent_apps/ai_deep_research_agent/` | `deep_research_openai.py` | 深度研究 Agent |
| `advanced_ai_agents/single_agent_apps/ai_investment_agent/` | `investment_agent.py` | 投资分析与建议 |
| `advanced_ai_agents/single_agent_apps/ai_fraud_investigation_agent/` | `fraud_investigation_agent.py` | AI 反欺诈调查 |
| `advanced_ai_agents/single_agent_apps/ai_meeting_agent/` | `meeting_agent.py` | AI 会议助理 |

### 多 Agent 团队模板

| 路径 | 核心文件 | 一句话功能 |
|------|----------|-----------|
| `advanced_ai_agents/multi_agent_apps/multi_agent_researcher/` | `research_agent.py` | HackerNews 研究团队 |
| `advanced_ai_agents/multi_agent_apps/agent_teams/ai_finance_agent_team/` | `finance_agent_team.py` | 金融分析多 Agent 团队 |
| `advanced_ai_agents/multi_agent_apps/agent_teams/ai_legal_agent_team/` | `legal_agent_team.py` | 法律协作 Agent 组 |
| `advanced_ai_agents/multi_agent_apps/agent_teams/ai_recruitment_agent_team/` | `ai_recruitment_agent_team.py` | AI 智能招聘团队 |
| `advanced_ai_agents/multi_agent_apps/agent_teams/ai_sales_intelligence_agent_team/` | `agent.py` | 销售情报多 Agent 系统 |
| `advanced_ai_agents/multi_agent_apps/agent_teams/ai_travel_planner_agent_team/` | `backend/agents/*.py` | 旅行规划多 Agent（含 Docker） |
| `advanced_ai_agents/multi_agent_apps/agent_teams/ai_real_estate_agent_team/` | `ai_real_estate_agent_team.py` | 房地产分析团队 |
| `advanced_ai_agents/multi_agent_apps/agent_teams/ai_teaching_agent_team/` | `teaching_agent_team.py` | AI 教学团队 |

### 前沿技术模板

| 路径 | 核心文件 | 一句话功能 |
|------|----------|-----------|
| `always_on_agents/always_on_hn_briefing_agent/` | — | 7x24 HackerNews 监控简报 |
| `voice_ai_agents/insurance_claim_live_agent_team/` | — | Gemini Live 实时语音理赔 |
| `mcp_ai_agents/` | — | MCP 协议 Agent 集成示例 |
| `advanced_ai_agents/multi_agent_apps/ai_news_and_podcast_agents/` | `beifong/` | 新闻聚合+AI 播客全栈系统 |
| `advanced_ai_agents/multi_agent_apps/devpulse_ai/` | `main.py` | 开发者信号情报（多源聚合） |
| `advanced_ai_agents/autonomous_game_playing_agent_apps/` | — | 自主游戏 Agent |

### RAG 教程

| 路径 | 核心文件 | 一句话功能 |
|------|----------|-----------|
| `rag_tutorials/chat_with_pdf/` | — | PDF 对话 RAG |
| `rag_tutorials/local_rag/` | — | Ollama + Llama3 离线 RAG |
| `rag_tutorials/chat_with_gmail/` | — | Gmail 数据 RAG |
| `rag_tutorials/chat_with_github/` | — | GitHub 仓库 RAG |

### 重要配置文件

| 路径 | 说明 |
|------|------|
| `README.md` | 项目首页（带完整目录和快速开始） |
| `LICENSE` | Apache-2.0 协议 |
| `.github/workflows/claude.yml` | CI 自动化工作流 |

---

*本报告基于 GitHub API 实时数据、项目源码分析及中文社区评测综合撰写。指标数据采集于 2026-06-27。*
