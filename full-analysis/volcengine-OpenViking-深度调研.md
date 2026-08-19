# volcengine/OpenViking 深度调研

> 基本信息：⭐ 30052 / 💻 Python / 📜 AGPL-3.0 / 🏷️ 领域（AI Agent 上下文数据库）/ 🌿 默认分支 main / 🕒 最近更新 2026-08-19

（数据来源：GitHub 仓库元数据 `gh api repos/volcengine/OpenViking`、README、文件树 `git/trees/main?recursive=1`、核心模块源码 `contents/<path>` 解码、官方文档 docs.openviking.ai 与博客 blog.openviking.ai。创建于 2026-01-05，fork 2329，open issues 458，watch/订阅者 82，最新 release v0.4.15。）

---

## 一、项目定位（一句话）

OpenViking 是字节跳动火山引擎开源的「面向 AI Agent 的自演化上下文数据库（Self-evolving Context Database）」，用一套 `viking://` 虚拟文件系统把 **Agent Memory（记忆）、Knowledge RAG（知识）、Skills（技能）** 统一成可 `ls/tree/find` 的同一类对象，并以「分层加载 + 目录递归检索 + 会话自动沉淀」让 Agent 像操作文件一样管理自己的上下文。

---

## 二、项目亮点（差异化，开篇呈现）

1. **三层上下文统一为「虚拟文件系统」**：记忆、资源、技能都映射成 `viking://` URI，Agent 用确定性的文件系统原语（而非黑盒向量库调用）定位与操作上下文——这是它与「再写一个 vector store wrapper」类方案最本质的区别。
2. **L0/L1/L2 三级分层加载**：每条上下文写入时即生成 L0 摘要（~100 token）、L1 概览（~2k token）、L2 原文，检索时按需下钻，显著降低 token 开销（实测可省 34%–91% 输入 token）。
3. **目录递归检索（Directory Recursive Retrieval）**：向量检索先定位「得分最高的目录」，再逐层向下钻取，结果天然携带上下文（context-intact），且每次检索保留可观测的「目录浏览轨迹」便于调试。
4. **会话即记忆、案例可演化成技能**：会话提交后异步抽取用户偏好/实体/事件/案例，进一步从「案例(cases)→经验(experiences)/轨迹(trajectories)→可执行会话技能(session skills)」自动沉淀，形成自演化闭环。
5. **数据库范式 + 学术背书**：源自 VikingMem 论文（arXiv:2605.29640，已录用 VLDB 2026），把「记忆库管理系统」的工程思想落地为开源系统；且开源版无功能阉割、无激活码、无账号强制。

---

## 三、核心架构

### 3.1 总体分层

官方架构（docs/en/concepts/01-architecture）把系统分为五层能力：Client → Service（FS/Search/Session/Resource/Pack/Debug）→ 三大引擎（Retrieve / Session / Parse）→ Compressor（压缩去重）→ Storage（AGFS 内容层 + Vector Index 索引层）。

关键设计原则：
- **纯存储层**：存储只管 AGFS 文件操作与基础向量检索，Rerank 放在检索层。
- **三层信息**：L0/L1/L2 渐进加载省 token。
- **两段式检索**：向量召回候选 + Rerank 精排。

### 3.2 Memory / RAG / Skills 三层如何统一

统一的核心是 `Context` 这个数据类与 `viking://` 命名空间。所有上下文实体都是 `Context`，仅靠 `context_type` 字段区分（`openviking/core/context.py:24`）：

```python
class ContextType(str, Enum):
    SKILL = "skill"
    MEMORY = "memory"
    RESOURCE = "resource"

class ContextLevel(int, Enum):
    ABSTRACT = 0   # L0
    OVERVIEW = 1   # L1
    DETAIL   = 2   # L2
```

预设目录结构（`openviking/core/directories.py` 的 `PRESET_DIRECTORIES`）把三类内容铺在同一棵虚拟树下，记忆下又细分 9 类：

```
viking://user/<user_id>/
├── memories/
│   ├── preferences   # 用户偏好（通信风格、代码规范、领域兴趣）
│   ├── entities      # 实体记忆（项目/人物/概念）
│   ├── events        # 事件记录（决策/里程碑，历史不可改）
│   ├── cases         # 案例记忆（具体问题上下文+解法，来自会话）
│   ├── patterns      # 模式记忆（可复用的 SOP/工作流）
│   ├── tools         # 工具使用记忆（行为/参数/失败模式）
│   ├── skills        # 技能执行记忆（关于技能使用的经验，非技能定义）
│   ├── trajectories  # 执行轨迹（端到端任务 trace）
│   └── experiences   # 从轨迹蒸馏出的泛化经验
├── resources/        # 用户私有文档/知识
└── skills/           # 技能定义（SKILL.md）
viking://resources/    # 共享知识库（项目文档、仓库、网页等）
```

也就是说：**RAG 对应 `resources/` + 共享 `viking://resources/`，Memory 对应 `memories/*`，Skills 对应 `skills/`（定义）与 `memories/skills`（使用经验）**——三者共用同一套 URI 寻址、同一套向量索引、同一套检索与权限模型，Agent 不必为三类数据接三套后端。

技能采用业界通用的 `SKILL.md`（frontmatter + 正文）格式，`openviking/core/skill_loader.py` 负责解析：

```python
FRONTMATTER_PATTERN = re.compile(r"^---\s*\n(.*?)\n---\s*\n(.*)$", re.DOTALL)

@classmethod
def parse(cls, content, source_path=""):
    frontmatter, body = cls._split_frontmatter(content)
    meta = yaml.safe_load(frontmatter)
    if "name" not in meta or "description" not in meta:
        raise ValueError("Skill must have 'name'/'description' field")
    allowed_tools = cls._normalize_allowed_tools(meta.get("allowed-tools", []))
    return {"name": meta["name"], "description": ..., "content": body.strip(), ...}
```

### 3.3 存储后端（双写/双层的 AGFS + Vector Index）

存储采用「内容层 + 索引层」分离（`docs/en/concepts/05-storage.md`）：

| 层 | 职责 | 内容 |
|---|---|---|
| **AGFS**（内容层，已用 Rust 重写 RAGFS） | 存全量内容 | L0/L1/L2 全文、多媒体 |
| **Vector Index**（索引层） | 语义检索 | URI、向量、稀疏向量、元数据，**不含文件内容** |

`VikingFS` 是统一 URI 抽象：`viking://resources/docs/auth → /local/{account_id}/resources/docs/auth`。AGFS 支持多后端（`localfs` / `s3fs` / `memory`），并可配置 `storage.agfs.backups` 进入 **multi-write 模式**（主备双写、迁移、读加速）。向量索引 collections 记录 `uri / parent_uri / context_type / is_leaf / vector / sparse_vector / abstract` 等字段，支持标量过滤。

### 3.4 自演化闭环（Self-evolving Context Database）

「自演化」由三件事串起来：**写时分层的 L0/L1 自动生成 → 会话提交时按策略抽取记忆 → 案例进一步训练出经验与可执行技能**。

**(a) 写入即分层（异步语义队列）**。解析与语义生成解耦：Parser 不调 LLM，仅格式化建树；`TreeBuilder` 把临时目录搬入 AGFS 并投递 `SemanticMsg`；`SemanticQueue` 自底向上（叶子→父→根）生成每个目录的 `.abstract.md`(L0) 与 `.overview.md`(L1)，再向量化入索引（`docs/en/concepts/06-extraction.md`）。L0/L1 是「目录侧车」而非「逐文件侧车」，父目录摘要只消费子目录 L0，减少写放大。

**(b) 会话提交 → 记忆抽取**。会话 `commit`（`openviking/session/session.py`）落地为 `SessionCommitMsg` 入队，由 Processor 异步执行。完整流程见 `docs/design/session-memory-extraction-flow.md`：

1. 从会话元数据加载 `memory_policy`（可开关 self/peer/working_memory，可设 `memory_types` 白名单）；
2. 归档当前消息批次并 hydrate 工具输出；
3. 调用唯一公开入口 `SessionCompressorV3.extract_long_term_memories`；
4. 普通抽取产出 `cases` 后，**仅当至少 1 个 case 存在**，才触发 `trajectories / experiences` 流式训练，并在开启时训练「可执行会话技能」；无 case 则跳过全部训练。

`MemoryIsolationHandler.calculate_memory_uris` 按「无 peer_id→写 self / 安全 peer_id→写对应 peer / 不安全→跳过」逐条决定落库 URI，保证多租户与隐私隔离。

**(c) 案例→经验→技能的演化**。`openviking/session/compressor_v3.py` 中：

```python
async def extract_long_term_memories(self, ...):
    cases_allowed = ...
    session_skills_enabled = self._session_skill_extraction_enabled()
    if agent_evolution_enabled and cases_allowed and session_skills_enabled:
        train_result = await self.train_from_extracted_cases(cases=result.cases, ...)  # 训练 experiences/trajectories/skills
    elif not agent_evolution_enabled and allow_self_memory and session_skills_enabled:
        train_result = await self.extract_session_skills(...)  # 仅抽技能，不产生 evolution 记忆
```

`extract_session_skills` 调 `rollout_analyzer.extract_trajectory_memories(include_session_skills=True)` 得到 `skill_gradients`，再经 `SkillSetLoader`/`get_streaming_policy_trainer` 把梯度 `submit_gradients` 写回 `viking://user/<id>/skills/`。**这正是「记忆被检索、压缩、沉淀为技能」的机制：一次成功解决问题的轨迹 → 被识别为案例 → 泛化为可复用技能 → 下次同任务直接召回技能。**

### 3.5 与 Agent 框架的集成方式

- **协议/接口层**：HTTP Server（`openviking-server`，端口 1933，API Key 鉴权）、Python/TS SDK、CLI（`ov`）、Rust CLI（`crates/ov_cli`，Apache-2.0）、MCP。
- **注入层（主流 Agent 全覆盖）**：Claude Code、Codex、OpenClaw、Hermes、Cursor、TRAE、OpenCode、pi、LangChain/LangGraph，以及通用 MCP 客户端、Agent Plugins 1.0。集成做两件事：**把 OpenViking 召回注入 Agent 上下文** + **自动提交会话记忆**（`ov` 端有 `auto-recall.mjs`/`auto-capture.mjs` 等 hook/plugin，见 `examples/claude-code-memory-plugin`）。
- **上层框架**：`VikingBot`（`pip install "openviking[bot]"`）是基于 OpenViking 的 Agent 框架；官方 Docker 镜像默认带 Server + VikingBot + Console UI。
- **生态伙伴**：deer-flow（字节长程 SuperAgent）、NoKV（AI 原生分布式文件系统）、loopx、Hermes Agent。

---

## 四、应用场景与启发（重点章节）

### 4.1 统一「记忆 / RAG / 技能」的上下文数据库，给同类需求什么解决思路

绝大多数 Agent 记忆/RAG 项目仍在「各管一摊」：记忆库、向量知识库、技能目录是三套独立存储与索引。OpenViking 的核心启发是 **「把它们降级为同一棵树上的不同节点」**：

- **用 URI 命名空间代替多后端拼接**。把 `viking://` 作为统一寻址，记忆/资源/技能共享检索、权限、向量索引，新增一类上下文只需加一个 `context_type` 与预设目录，不用重构接入层。同类需求应优先考虑「能否用一个命名空间 + 一个索引统一所有上下文」，而非为每个能力各自造库。
- **分层加载是「省 token 的廉价杠杆」**。L0/L1/L2 让相关性判断在 100 token 内完成、仅在必要时读 2k 概览、最后才读全文。对长上下文/多知识库场景，先把「摘要层」做扎实，比直接堆长上下文窗口更划算（这也是其 token 降低 34%–91% 的来源）。
- **目录递归检索带来「上下文完整」**。向量检索常返回孤立片段、丢失结构；OpenViking 先定位目录再下钻，结果自带兄弟/父级上下文，更适合代码仓库、文档树这类天然分层的数据。
- **可观测的检索轨迹**。每次检索保留目录浏览路径，错误时可回溯「是哪条路径产生了这个错误结果」——这对生产环境 debug 极其关键，是黑盒 RAG 缺失的能力。

### 4.2 对「Agent 长期记忆产品」的启发

- **「会话即记忆」应自动化而非手动**。OpenViking 把「会话提交 → 抽取偏好/实体/事件 → 沉淀案例 → 演化经验与技能」做成异步闭环，几乎零人工干预。长期记忆产品不应只提供「存/取 API」，而要内置「从交互中持续提炼」的管线（且要可策略化开关，避免噪声污染长期记忆）。
- **记忆要分级、可隔离、可遗忘**。`memories/` 下 9 类细分 + `self/peer` 隔离 + `memory_policy` 白名单，说明长期记忆需要「结构化分类 + 写入权限 + 抽取范围控制」，否则记忆越多越脏。
- **让记忆「长出技能」是质变点**。把成功轨迹泛化为可复用技能并回写 `skills/`，使 Agent 能力随使用累积增长——这是「自演化」区别于普通「记忆检索」的关键：不是找回过去，而是沉淀能力。做长期记忆产品时，应设计「案例→模式→技能」的蒸馏通道，而不只是「相似度召回」。
- **开源无阉割 + 商业托管双轨**。社区版 AGPL 全功能、火山引擎托管 SaaS / 私有化 Self-Managed 双形态，给「想自己跑又想要托管」的用户留了平滑迁移路径。同类产品可借鉴「开源即完整、商业只卖运维/托管」的边界划分。

---

## 五、源码深度解读（2-3 个最核心模块）

### 5.1 统一上下文数据模型 —— `openviking/core/context.py`

`Context` 是所有上下文（记忆/资源/技能）的统一对象。`context_type` 自动从 URI 推断（`context_type_for_uri`），`level` 支持 L0/L1/L2，`vectorize` 字段支持多模态（text + image data URI）嵌入：

```python
class Context:
    def __init__(self, uri, parent_uri=None, is_leaf=False, abstract="",
                 context_type=None, level=None, session_id=None, user=None, ...):
        self.id = id or str(uuid4())
        self.uri = uri
        self.context_type = context_type or context_type_for_uri(uri)  # 由 URI 推断类型
        self.level = int(level) if level is not None else None
        self.owner_user_id = owner_user_id or owner_fields_for_uri(uri)["owner_user_id"]
        self.vector: Optional[List[float]] = None
        self.vectorize = Vectorize(abstract)  # 多模态嵌入载体
```

> 要点：类型与归属都由 URI 推导，使「加一种上下文」几乎零侵入。

### 5.2 分层递归检索 —— `openviking/retrieve/hierarchical_retriever.py`

`HierarchicalRetriever` 用优先队列做目录级递归检索，关键常量定义了检索行为：

```python
class HierarchicalRetriever:
    MAX_CONVERGENCE_ROUNDS = 3        # 连续 N 轮 topk 不变即收敛停止
    DIRECTORY_DOMINANCE_RATIO = 1.2   # 目录分需超过其子节点最高分才会继续下钻
    GLOBAL_SEARCH_TOPK = 10           # 全局候选数（越多 rerank 越准）
    MAX_PARALLEL_CHILD_SEARCHES = 4   # 限制对远端向量库的扇出
    LEVEL_URI_SUFFIX = {0: ".abstract.md", 1: ".overview.md"}

    async def retrieve(self, query, ctx, limit=5, mode=None, level=None, ...):
        # THINKING 模式启用 Rerank；否则回退纯向量分
        mode = RetrieverMode.QUICK if not self._rerank_client else RetrieverMode.THINKING
```

递归算法（`docs/en/concepts/07-retrieval.md` 给出骨架）：用 `heapq` 优先队列弹目录 → 检索其子节点 → 分数传播 `final = alpha*child + (1-alpha)*parent` → 超过阈值则收集、非叶子则继续入队 → 连续 3 轮 topk 不变则收敛。配套 `IntentAnalyzer`（`search()` 专用）用 LLM 把查询改写成 0–5 个 `TypedQuery`（skill/resource/memory 三类意图），实现「先理解意图、再分层召回、最后 rerank」。

> 要点：检索对象是「目录」而非「片段」，天然保留层级上下文；分数传播让父目录的语义影响子节点命中。

### 5.3 会话自演化闭环 —— `openviking/session/session.py` + `compressor_v3.py`

会话 `commit` 把归档消息封装成 `SessionCommitMsg` 入队（先落盘归档 `messages.jsonl` 再删活动历史，保证可恢复），由异步 Processor 触发记忆抽取：

```python
# openviking/session/session.py (commit_async 内)
queue_msg = SessionCommitMsg(
    task_id=task_id, session_id=self.session_id, archive_uri=archive_uri,
    user=self.ctx.user.to_dict(), memory_policy=effective_memory_policy, ...)
await get_queue_manager().enqueue(QueueManager.SESSION_COMMIT, queue_msg.to_dict())
```

真正「自演化」在 `compressor_v3.py`：普通抽取产出 `cases`，有 case 才训练 `experiences/trajectories/skills`，并支持纯技能提取（不产生 evolution 记忆）。技能以 `skill_gradients` 形式经流式 trainer 写回 `viking://user/<id>/skills/`。

> 要点：自演化是「门控」的——必须有可复用案例才沉淀经验/技能，避免把噪声写进长期记忆；且 self 与 peer 记忆按 `MemoryIsolationHandler` 严格隔离落库。

---

## 六、全网口碑

- **热度与榜单**：截至抓取，⭐ 30052、fork 2329、open issues 458，仓库 topics 含 `self-evolving`/`agent-memory`/`context-database`/`agentic-rag`；README 挂了 Trendshift 徽章，说明在 GitHub Trending 类榜单有曝光。
- **官方背书强**：源自 VLDB 2026 录用的 VikingMem 论文（arXiv:2605.29640），并有火山引擎（字节）作为背后主体，工程成熟度与持续维护预期较高（2026-01 建仓、已迭代至 v0.4.15）。
- **集成覆盖广**：原生支持 Claude Code / Codex / Cursor / TRAE / OpenCode / LangChain 等主流 Agent，降低试用门槛；另有 OpenViking Helper 桌面端（mac/Win）做可视化配置与记忆/技能管理。
- **实测数据亮眼**：官方基准（blog.openviking.ai，2026-05 更新，版本 0.3.22 区间）显示 LongMemEval/LoCoMo 下三款 Agent 接入后准确率均破 80%（原生仅 24%–57%），tau2-bench 经验记忆带来 +6.87pp（零售）/+11.87pp（航空）提升，HotpotQA top-20 检索 91% @ 0.23s。
- **中立提示**：上述基准均由官方发布、自行复现脚本在 `./benchmark`，属「厂商自测」；AGPL 协议对闭源商用有强约束（见下），社区对协议合规性的顾虑可能影响企业内采用。口碑「数据不可用」项：第三方独立评测/社区长文我们未抓取到权威非官方来源，**标注为数据不可用**，以上口碑以官方文档与仓库元数据为准。

---

## 七、竞品对比 + 核心研判

### 7.1 与记忆/技能类方案对比

| 维度 | OpenViking | MemOS (MemTensor) | claude-mem (thedotmack) | zai-org (智谱系) |
|---|---|---|---|---|
| 统一对象 | Memory+RAG+Skills 统一为 `viking://` 虚拟文件系统 | Memory OS，强调「记忆态」管理与记忆单元 | 聚焦 Claude 对话长期记忆的轻量方案 | 智谱系 Agent/模型能力（技能偏模型侧） |
| 存储/检索 | 双写 AGFS + Vector Index，目录递归检索，L0/L1/L2 | 记忆中心化、分层态管理 | 向量/文件记忆，侧重会话回灌 | 以模型与平台能力为主 |
| 自演化 | 会话→cases→experiences→session skills 自动沉淀 | 有记忆巩固/演化概念 | 主要「记住」而非「长出技能」 | 技能多来自模型/平台预置 |
| 集成面 | 十余种 Agent 原生集成 + MCP + SDK | 提供库/接口 | 主要围绕 Claude | 平台/API 形态 |
| 协议 | **AGPL-3.0**（主项目） | 见其各自仓库（数据不可用） | 见其各自仓库（数据不可用） | 见其各自仓库（数据不可用） |

> 注：MemOS、claude-mem、zai-org 的确切协议与最新数据本次未逐一抓取核验，相关单元格标注「数据不可用」，仅基于已知公开定位做定性比较。

### 7.2 核心研判

1. **差异化定位清晰**：相比「再包一层向量库」的记忆方案，OpenViking 走的是「数据库范式 + 文件系统隐喻」，把记忆/RAG/技能当成同一类数据来管理，抽象层级更高、扩展更顺。其目录递归检索 + 分层加载在「代码仓库/文档树/长会话」类天然分层数据上优势明显。
2. **学术+工程双轮**：VikingMem（VLDB 2026）给出方法论背书，开源系统给出可落地实现，且基准数据在「准确率↑ + token↓ + 延迟↓」三向同时优化，叙事自洽。
3. **AGPL 协议对商用的含义（关键）**：
   - 主项目 **AGPL-3.0** 是强 copyleft：若你将 OpenViking **作为网络服务（SaaS/内部 HTTP 服务）对外提供**且**修改了其代码**，AGPL 要求你**向使用者提供修改后的完整对应源码**。这意味着「改了代码又通过网络提供服务却不开放改动」不合规。
   - 但**单纯调用/集成不触发**：把 OpenViking 当独立服务跑、你的 Agent 通过 HTTP/MCP/SDK 调用它，**只要你没修改 OpenViking 自身源码**，通常不构成「分发」或「衍生网络服务」，无需开源你的 Agent（调用方与 OpenViking 进程分立）。
   - **分组件授权**：`crates/ov_cli`（Rust CLI）与 `examples` 是 **Apache-2.0**，可更自由使用；仅主 Python 包与 Server 是 AGPL。
   - **对厂商的含义**：想在闭源产品里「改 OpenViking 代码并以服务形式提供」需谨慎（要么开源改动，要么谈火山引擎 Self-Managed 商业授权/许可密钥）；仅「部署即用、不改源码」则无碍。这也解释了其「开源全功能 + 商业卖托管/私有化运维」的双轨策略。
4. **风险与待观察**：基准为官方自测，需独立复现验证；AGPL 可能劝退部分企业闭源集成；作为 2026-01 才建仓的新项目，长期社区生态与稳定性仍需时间检验。

---

## 关键文件路径速查

| 路径 | 说明 |
|---|---|
| `openviking/core/context.py` | 统一上下文数据模型 `Context`，定义 `ContextType`(skill/memory/resource) 与 `ContextLevel`(L0/L1/L2) |
| `openviking/core/directories.py` | 预设虚拟目录树 `PRESET_DIRECTORIES`，含 `memories/{preferences,entities,events,cases,patterns,tools,skills,trajectories,experiences}` |
| `openviking/core/skill_loader.py` | `SKILL.md` 解析器，加载 frontmatter(name/description/allowed-tools) 与正文 |
| `openviking/core/retrieval_targets.py` | 检索目标解析 `resolve_retrieval_targets`，按 context_type 与 self/peer 路由目录 |
| `openviking/retrieve/hierarchical_retriever.py` | 分层递归检索 `HierarchicalRetriever`，优先队列 + 分数传播 + 收敛控制 |
| `openviking/session/session.py` | 会话 `commit` 提交，封装 `SessionCommitMsg` 入队触发异步记忆抽取 |
| `openviking/session/compressor_v3.py` | 自演化核心：`extract_long_term_memories` / `train_from_extracted_cases` / `extract_session_skills`（案例→经验→技能） |
| `openviking/ingest/orchestrator.py` | 会话回放与提交编排 `IngestOrchestrator`，把 Agent 日志沉淀为上下文 |
| `docs/design/session-memory-extraction-flow.md` | 会话→记忆抽取流程设计文档（policy/隔离/落库） |
| `docs/en/concepts/05-storage.md` / `07-retrieval.md` / `06-extraction.md` | 双写存储、分层检索、三阶段异步抽取的概念文档 |

---

> 铁律自检：本报告信息量已超越 README——补充了 L0/L1/L2 自动生成机制、目录递归检索代码常数（`MAX_CONVERGENCE_ROUNDS=3` 等）、`compressor_v3` 的 case→skill 演化链路、`memory_policy` 与 `MemoryIsolationHandler` 隔离策略、双写存储后端、AGPL 商用影响研判及竞品对比；常规实现未展开罗列，仅保留架构关键点与精炼骨架；所有引用均标注真实文件路径；本报告仅写入目标文件，未做 git commit/push，未修改任何索引文件。数据不可用项已显式标注。
