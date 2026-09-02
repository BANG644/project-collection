# ClaudioDrews/memory-os 深度调研

> 调研日期：2026-09-03 ｜ 星标：1,352 ⭐ ｜ 语言：Python ｜ 协议：MIT ｜ 默认分支：main ｜ 最后推送：2026-06-10
> 定位：Hermes Agent 的「七层记忆操作系统」——本地优先、provider 无关的长期记忆基础设施，带可信度评分、自动 wiki 与「手术式」上下文注入

## 一、项目亮点（差异化）

1. **七层记忆分层，而非单一向量库**：从 L1 工作区文件（MEMORY.md/USER.md）到 L7 Ground Truth 身份层，逐层捕获→存储→注入→强制使用，覆盖「会话全文检索 / 结构化事实 / 跨会话 Fabric / 向量库 / LLM 自策展 wiki / 身份权威」。
2. **Ground Truth 层级（L7）是真正差异点**：多数记忆方案只解决「注入」，agent 却仍用 API 重新检索已注入的内容（memory-zero）。L7（SOUL.md/rulebook.md）显式声明注入记忆为权威，从源头消除重复检索的 token 浪费。
3. **零知识/本地优先**：Qdrant + Redis + ARQ Worker 跑在本地 Docker，兼容 OpenRouter/OpenAI/Anthropic/Ollama 任意 provider，无记忆订阅、无厂商锁定。
4. **工程化检索降级链**：向量库采用「混合检索 → 稠密 → 词典(BM25) → SQLite」四级 fallback；Qdrant 4096 维 Cosine + BM25 稀疏，每周 decay 扫描 + 语义去重（cosine>0.92 自动合并）。
5. **结构化事实带信任评分**：`memory_store.db` 用 HRR + FTS5 + trust scoring，实体解析 + 反馈闭环随时间训练信任分，避免陈腐/错误事实长期污染上下文。

## 二、核心架构

整体是「**pre_llm_call 召回 → LLM 生成 → post_llm_call/on_session_end 抽取**」的闭环，由 Icarus 插件（重度 fork）挂载到 Hermes 的 hook 点：

- **L1 WORKSPACE**（`layers/01-workspace.md`）：MEMORY.md/USER.md/CREATIVE.md，每轮注入 system prompt。
- **L2 SESSIONS**（`state.db` SQLite+FTS5）：全对话历史全文检索。
- **L3 STRUCTURED FACTS**（`memory_store.db` SQLite+HRR+FTS5+trust）：持久事实，实体解析 + 信任反馈闭环。
- **L4 FABRIC**（`icarus/` 插件，16 工具）：`fabric_recall`/`fabric_write`/`fabric_brief` 等跨会话抽取与多源注入。
- **L5 VECTOR**（`Qdrant` 4096d Cosine+BM25）：四级 fallback + decay + 语义去重。
- **L6 LLM WIKI**（`concepts/ entities/ comparisons/`）：`wiki_continuous_ingest` 持续灌入 Qdrant 的自策展知识库。
- **L7 GROUND TRUTH**（`modifications/soul-rulebook.md`）：身份权威层，强制 agent 使用注入记忆。

每张来源都有相关性阈值门控、按会话去重、社交闲聊过滤器（trivial 消息跳过），做到「只给 LLM 刚好需要的」。

## 三、应用场景与启发

- **场景**：长期陪跑型 agent（个人助手、研究协作、项目记忆）、需要在多会话间保持一致偏好的 coding agent、隐私敏感不愿上云记忆服务的用户。
- **启发 1**：「注入 ≠ 使用」——记忆系统真正的护城河在**让 agent 服从注入记忆**，而非检索精度。L7 的 Ground Truth 范式值得所有 agent memory 方案借鉴。
- **启发 2**：「分级 fallback + decay + 语义去重」是把向量库从 demo 拉到生产的关键运维手段，避免误召回误导 agent（原报告已警示的风险）。
- **启发 3**：信任评分 + 实体解析让「事实」可随时间校正，比纯 append 记忆更抗污染。

## 四、源码深度解读

### 1. Hook 挂载点（`icarus/hooks.py`）
Hermes 在 `pre_llm_call` / `post_llm_call` / `on_session_end` 调 Icarus。`pre_llm_call` 从 Fabric+Qdrant+Sessions+Facts 四源做「手术式」召回拼进上下文；`post_llm_call`+`on_session_end` 触发自动学习抽取与落库。这正是 L7 之外的另一根「闭环骨架」——没有它，记忆只进不出。

### 2. 语义去重与衰减（`scripts/semantic_dedup.py` + `scripts/decay_scanner.py`）
`semantic_dedup.py` 对 Qdrant 点做 cosine>0.92 合并，防止同一事实多份冗余；`decay_scanner.py` 每周扫描降权长期未触发的记忆。两者共同维持「注入质量」，直接回应原报告担忧的「误召回误导 agent」。

### 3. 事实信任闭环（`icarus/state.py` + `scripts/reflection_trigger.py`）
`state.py` 管理 `memory_store.db` 的 HRR/FTS5 结构与信任分字段；`reflection_trigger.py` 在合适时机触发反思，把用户反馈回灌进信任评分。这是 L3「结构化事实带信任评分」的实现落点。

## 五、全网口碑

- 1.3k ⭐，2026 年新项目，作者自称「在生产环境撞遍 Hermes 与所有记忆方案局限后构建」。v0.2.0 已有一键 `setup.sh` 安装、Issue/PR 模板、社区贡献者与 20+ audit 修复。
- 定位认知：被视作「给 Hermes Agent 装长期记忆」的标杆方案，差异化在七层 + Ground Truth 身份层 + 本地优先。
- 客观短板（社区与代码均可见）：① 强绑定 Hermes Agent，非通用记忆中间件；② 依赖 Docker(Qdrant+Redis+ARQ)，部署重；③ 单人主导、维护节奏不确定；④ L4 Icarus 为重度 fork，上游变更需手动跟进。
- 数据说明：star/license/结构来自仓库一手元数据与 README；第三方长评未逐条抓取，标注为社区普遍认知。

## 六、竞品对比 + 核心研判

| 维度 | memory-os | Mem0 | Zep | Letta(MemGPT) | LangMem |
|---|---|---|---|---|---|
| 分层模型 | 七层+Ground Truth | 单层事实/向量 | 知识图谱时序 | 操作系统式块存储 | 基于 LangGraph |
| 本地优先 | ✅ Docker 全本地 | 可选 | 可选 | ✅ | 可选 |
| 信任评分 | ✅ HRR+trust | 部分 | 图边权重 | ❌ | ❌ |
| 强绑定宿主 | Hermes Agent | 通用 | 通用 | 通用 | LangChain |
| 注入权威保证 | L7 显式 | ❌ | ❌ | 部分 | ❌ |

**核心研判**：
- ✅ **价值确定**：在「agent 长期记忆」这一明确痛点下，七层 + L7 Ground Truth 是经作者实战打磨的差异化设计，源码结构清晰（layers/、icarus/、scripts/ 职责分明），可精读借鉴。
- ⚠️ **风险点**：Hermes 绑定降低了通用性；单人维护 + fork 上游的可持续性；16 工具 Fabric 层的实际召回质量需实测验证。
- 🔮 **趋势**：「注入权威层」会成 agent memory 标配思路；若抽象出 provider 无关的 hook 接口，memory-os 范式可外溢到 Claude Code/Codex 等宿主。
- 💡 **启发迁移**：做记忆系统时，把预算花在「让 agent 真正用上记忆」与「去重/衰减/信任」运维上，比堆检索精度更值。

## 七、关键文件路径速查

| 路径 | 作用 |
|---|---|
| `layers/01-workspace.md` … `layers/07-ground-truth.md` | 七层记忆定义（L7 身份权威层） |
| `icarus/hooks.py` | pre/post_llm_call + on_session_end 闭环挂载 |
| `icarus/fabric-retrieve.py` / `icarus/collapse.py` / `icarus/tools.py` | Fabric 跨会话召回/合并/16 工具 |
| `scripts/semantic_dedup.py` / `scripts/decay_scanner.py` | 语义去重 + 周衰减扫描 |
| `scripts/wiki_continuous_ingest.py` / `scripts/reflection_trigger.py` | wiki 持续灌入 + 信任反思 |
| `modifications/soul-rulebook.md` | L7 Ground Truth 身份规则 |
| `infrastructure/architecture.md` | 部署架构（Qdrant+Redis+ARQ） |
| `setup.sh` / `requirements.txt` | 一键安装 + 依赖 |
