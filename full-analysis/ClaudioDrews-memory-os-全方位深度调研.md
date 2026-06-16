# ClaudioDrews-memory-os - 全方位深度调研

## 项目全景
- **仓库**：`ClaudioDrews/memory-os`
- **一句话定位**：A 7-layer memory operating system for Hermes Agent — persistent memory with Qdrant, structured facts, fabric recall, auto-curated wiki, and surgical context injection. Runs locally, any LLM provider.
- **解决的问题**：该项目试图把 README 中描述的能力产品化/脚本化，降低特定任务的搭建或执行门槛。
- **基础指标**：Stars=1050 / Forks=98 / 默认分支=`main`
- **Topics**：ai-memory, context-injection, docker, ground-truth, hermes-agent, local-first, open-source, persistent-memory, qdrant, rag, self-hosted, vector-database
- **Homepage**：数据不可用

## 核心架构
### 目录结构判断
- 顶层目录分布（递归树抽样汇总）：icarus(16), scripts(13), docker(11), layers(7), .github(6), setup(4), skills(4), templates(3), modifications(2), .dockerignore(1)
- 关键文件候选：requirements.txt, README.md

### 设计亮点研判
- 存在 Python 入口，通常意味着 CLI、服务端或研究型流水线由 Python 主导。
- 仓库包含 .github 自动化配置，通常代表 CI 或 issue 模板已被纳入工程流程。

## 源码深度解读
### README / 说明文档要点
# Memory OS — Hermes Agent Memory Operating System

![Memory OS Banner](assets/banner.jpg)

> **Your agent finally stops forgetting.**  \
> Permanent memory. Local memory infrastructure. API-provider agnostic. Surgically token-efficient.

Seven memory layers. Automatic, intelligent context injection. Structured facts with trust scoring. A self-curating wiki pipeline. Semantic search across **every conversation you've ever had**.

Memory OS turns Hermes Agent into a real long-term collaborator — one that remembers your projects, your decisions, your reasoning, and brings exactly the right context back at exactly the right moment. Like talking to a colleague who was there for every session.

**Memory infrastructure runs entirely on your machine. Works with any LLM provider — OpenRouter, OpenAI, Anthropic, Ollama, or local models. No memory subscription. No vendor lock-in.**

---

## What's New in v0.2.0

**One-command install.** `curl -sSL https://raw.githubusercontent.com/ClaudioDrews/memory-os/main/setup.sh | bash` sets up the entire stack — Docker services, SQLite databases, Icarus plugin, environment — in one shot. The 10-step manual guide is now a fallback for troubleshooting.

**Community infrastructure.** Issue templates (bug report + feature request), PR checklist, and contributing guide. Project is ready for external contributors — and already has them.

**20+ fixes from systematic audit.** Community-driven review across setup, configuration, performance, and resilience. Highlights: provider-agnostic LLM extraction, O(1) path lookups, FTS5-powered session search, semantic dedup at scale, and idempotent database initialization.

**Installation verified on real hardware.** Smoke tests and ingestion tests ship with the repo. The automated installer has been tested end-to-end — including on modest machines where Docker build times exposed UX gaps that are now handled gracefully.

---

## The problem every serious Hermes user knows

You spend hours configuring the agent, teaching it your preferences, solving hard problems together — and in the next session it acts like it's meeting you for the first time.

- Repeating context at the start of every conversation
...[truncated]

### 关键文件精读
### `requirements.txt`
```
# Memory OS — Host Scripts
requests>=2.31.0
aiohttp>=3.9.0
arq>=0.28.0
redis>=5.0.0
python-dotenv>=1.0.0
pyyaml>=6.0
qdrant-client>=1.17.0
httpx>=0.27.0
fastembed>=0.4.0
```

### `README.md`
```
# Memory OS — Hermes Agent Memory Operating System

![Memory OS Banner](assets/banner.jpg)

> **Your agent finally stops forgetting.**  \
> Permanent memory. Local memory infrastructure. API-provider agnostic. Surgically token-efficient.

Seven memory layers. Automatic, intelligent context injection. Structured facts with trust scoring. A self-curating wiki pipeline. Semantic search across **every conversation you've ever had**.

Memory OS turns Hermes Agent into a real long-term collaborator — one that remembers your projects, your decisions, your reasoning, and brings exactly the right context back at exactly the right moment. Like talking to a colleague who was there for every session.

**Memory infrastructure runs entirely on your machine. Works with any LLM provider — OpenRouter, OpenAI, Anthropic, Ollama, or local models. No memory subscription. No vendor lock-in.**

---

## What's
...[truncated]
```

### 关键逻辑总结
- 从关键文件组合看，项目更像是**围绕单一目标组织的任务流水线/工具链**，而不是超重平台。
- 入口文件决定外部交互界面（CLI / API / UI），配置文件决定运行时依赖，测试文件则暴露作者真正关心的行为边界。
- 如果用户只读 README，通常只能知道“能做什么”；而从目录与入口文件能看出“怎么做、扩展点在哪、维护成本高不高”。

## 社区口碑
### GitHub Issues 抽样
- #29 [OPEN] Alternate embeddings（comments=[] labels=enhancement）
- #27 [OPEN] Conversation with Hermes Agent regarding this memory project（comments=[] labels=bug）
- #23 [CLOSED] Hebbian weight vs. query-local relevance tradeoff (collapse v2)（comments=[{'id': 'IC_kwDOStQSpM8AAAABFLojYg', 'author': {'login': 'ClaudioDrews'}, 'authorAssociation': 'OWNER', 'body': 'Resolved in 4dec57e (PR #24).\n\nThe attenuation `boost = min(corro * amplify_gain * bases[i], amplify_cap)` was implemented, tested against real pipeline data, and merged. Key results from the test (query: "como configurar o Qdrant para memory-os"):\n\n- A query-relevant Qdrant usage fact now survives (was pruned in v1)\n- Honcho attenuated from 0.736 → 0.603 (base 0.556 × 1.083 vs old 0.640 × 1.150)\n- Context reduction maintained at 30-33%\n\nFuture tuning, if needed: `ICARUS_COLLAPSE_AMPLIFY_GAIN` (default 0.15). Raise to 0.20 if genuine corroboration feels undervalued in production. Open a new issue with concrete data when that happens.', 'createdAt': '2026-06-07T12:45:09Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [], 'url': 'https://github.com/ClaudioDrews/memory-os/issues/23#issuecomment-4642710370', 'viewerDidAuthor': False}] labels=无）
- #20 [CLOSED] fabric_curate cannot find entries: YAML quote mismatch in state.py（comments=[{'id': 'IC_kwDOStQSpM8AAAABFIf5hw', 'author': {'login': 'ZinkDifferent'}, 'authorAssociation': 'NONE', 'body': 'I have tested and confirmed the fix locally.\n\n**Root cause** in `icarus/state.py` lines 479-480:\n\nThe YAML frontmatter has `id: "f95842e2"` (with surrounding quotes).\nThe regex `r"^id: (.+)$"` captures `"f95842e2"` including quotes.\nComparison `\'"f95842e2"\' != \'f95842e2\'` always fails.\n\n**Fix:**\n```diff\n- if not m or m.group(1).strip() != entry_id:\n+ if not m or m.group(1).strip().strip(chr(34)) != entry_id:\n```\n\nSame fix needed at line 484 for `training_value:` matching.\nAfter fixing and clearing `__pycache__`, `fabric_curate` works correctly.', 'createdAt': '2026-06-06T15:26:36Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [], 'url': 'https://github.com/ClaudioDrews/memory-os/issues/20#issuecomment-4639422855', 'viewerDidAuthor': False}, {'id': 'IC_kwDOStQSpM8AAAABFLRTYg', 'author': {'login': 'ClaudioDrews'}, 'authorAssociation': 'OWNER', 'body': 'Fixed in #21 — good catch. The regex `r"^id: (.+)$"` captures the YAML-quoted string `"f95842e2"` and `.strip()` only removes whitespace, so the comparison always failed.\n\nFix: `.strip().strip(\'"\')` on line 480 to normalize quoted scalars. py_compile + 24 existing tests pass.', 'createdAt': '2026-06-07T11:15:04Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [], 'url': 'https://github.com/ClaudioDrews/memory-os/issues/20#issuecomment-4642329442', 'viewerDidAuthor': False}] labels=无）
- #19 [CLOSED] Recurring leak of internal mechanics into user-facing conversation（comments=[{'id': 'IC_kwDOStQSpM8AAAABFLSdnQ', 'author': {'login': 'ClaudioDrews'}, 'authorAssociation': 'OWNER', 'body': 'Good diagnosis — the root cause is a missing onboarding step, not a model behavior bug.\n\n## Root cause\n\nMemory OS injects context labeled `[fabric]`, `[qdrant]`, `[sessions]`, `[facts]` into every prompt. Without explicit instruction, the agent treats these as *external sources to cite* rather than *prior knowledge to use*. The fix exists in the repo but isn\'t applied automatically:\n\n- [`layers/07-ground-truth.md`](https://github.com/ClaudioDrews/memory-os/blob/main/layers/07-ground-truth.md) — documents the Ground Truth Hierarchy that positions injected memory as Level 2 (above training knowledge, below terminal output)\n- [`modifications/soul-rulebook.md`](https://github.com/ClaudioDrews/memory-os/blob/main/modifications/soul-rulebook.md) — the exact SOUL.md additions needed\n\nWhen applied, the agent\'s system prompt tells it: *"You already know this. Treat it as prior knowledge — use directly when reasoning. Never mention the source."* This eliminates the citation behavior.\n\n## What\'s needed\n\nA setup verification script that checks whether SOUL.md has the Ground Truth Hierarchy configured and warns the user if it\'s missing. Working on this now — will PR shortly.', 'createdAt': '2026-06-07T11:22:50Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [], 'url': 'https://github.com/ClaudioDrews/memory-os/issues/19#issuecomment-4642348445', 'viewerDidAuthor': False}] labels=无）
- #17 [OPEN] Using with non Hermes harnesses（comments=[{'id': 'IC_kwDOStQSpM8AAAABE9-sGA', 'author': {'login': 'ClaudioDrews'}, 'authorAssociation': 'OWNER', 'body': "It's currently Hermes-native — the integration points (Icarus plugin hooks, fabric tools, `pre_llm_call` injection, fact_store/SQLite schema) are designed around Hermes Agent's plugin architecture.\n\nThat said, decoupling the core memory infrastructure from the Hermes-specific integration layer is on the roadmap. The Docker stack (Qdrant + Redis + ARQ worker) is already harness-agnostic — it's the injection hooks that are tightly coupled. With v0.2.0 shipping a reproducible test environment, we can now actually test against alternative harnesses.\n\nI'll post an update here once there's a documented integration path. If you're willing to share details about your harness (language, hook model, how it injects context), that would help prioritize which integration patterns to support first.", 'createdAt': '2026-06-05T05:03:39Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [], 'url': 'https://github.com/ClaudioDrews/memory-os/issues/17#issuecomment-4628392984', 'viewerDidAuthor': False}, {'id': 'IC_kwDOStQSpM8AAAABFLRkAg', 'author': {'login': 'ClaudioDrews'}, 'authorAssociation': 'OWNER', 'body': "Memory OS is designed to be harness-agnostic at the Icarus layer. The integration points are:\n\n**Inbound (memory → agent):** Call `pre_llm_call(user_message)` before each LLM turn. It queries 4 sources in parallel (Fabric, Qdrant, Sessions, Facts) and returns context to inject into the system prompt. See [`layers/04-icarus-fabric.md`](https://github.com/ClaudioDrews/memory-os/blob/main/layers/04-icarus-fabric.md) for the full flow.\n\n**Outbound (agent → memory):** Call `post_llm_call(user_msg, assistant_msg)` to capture decisions, and `on_session_end()` for session archival.\n\nThe hooks are in [`icarus/hooks.py`](https://github.com/ClaudioDrews/memory-os/blob/main/icarus/hooks.py) — they're plain Python functions with no Hermes-specific dependencies beyond the Icarus plugin convention. Any harness that can call a Python function in the agent lifecycle can integrate.\n\nWould a dedicated `docs/harness-integration.md` guide be useful? If so, let me know which harness you're using and I'll write one.", 'createdAt': '2026-06-07T11:16:42Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [], 'url': 'https://github.com/ClaudioDrews/memory-os/issues/17#issuecomment-4642333698', 'viewerDidAuthor': False}] labels=无）

### Pull Requests 抽样
- PR #28 [MERGED] fix: resolve 6 installation bugs in setup.sh and docker-compose
- PR #26 [OPEN] fix(security): use Path.is_relative_to for WIKI_PATH containment in ingest_file
- PR #25 [MERGED] fix: add context_enhancer symlink step and Mandatory Pre-Action Protocol
- PR #24 [MERGED] feat: collapse v2 — non-bijunctive recall with Hebbian cross-source corroboration
- PR #22 [MERGED] feat: add verify_soul_config.py — detect missing Ground Truth in SOUL.md (fixes #19)

### Releases 抽样
暂无 release 或数据不可用

### 真实反馈与维护信号研判
- 抽样 issue 中 open/closed 约为 4/4，可作为维护者响应速度的弱信号。
- 近期 PR 抽样里可见已合并项 5 个，说明项目并非完全冻结。
- 由于本批处理以 GitHub 官方数据为主，若外部搜索结果缺失，应把 GitHub issue/PR 视为最可信的一手社区反馈源。
- 高频问题通常比 README 更能暴露真实落地难点：安装、兼容性、性能边界、文档歧义、平台限制。

## 竞品对比
| 维度 | memory-os | 竞品/替代 |
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
- `requirements.txt`
- `README.md`

## 3 条关键发现
- 代码入口/骨架集中在：requirements.txt, README.md
- 近期开源反馈以 issue 为主，典型议题包括：Alternate embeddings；Conversation with Hermes Agent regarding this memory project

## 研究方法与数据来源
- GitHub Repo API / README / 默认分支递归文件树
- 关键源码文件抽样精读
- Issues / PRs / Releases 社区活动抽样
- 说明：若外部搜索数据不可用，则明确标注并不伪造口碑结论
