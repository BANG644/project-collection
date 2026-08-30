# THU-MAIC/OpenMAIC — 深度调研

> 调研日期：2026-08-31 ｜ 星标：23,639 ⭐ ｜ 协议：MIT（v0.3.0 从 AGPL-3.0 改为 MIT）｜ 语言：TypeScript ｜ 默认分支：`main` ｜ 最新版本：v1.0.0（2026-08-27）｜ 来源：GitHub Trending 日榜（+907/日，当日增速榜首）

## 一、项目定位（一句话）

OpenMAIC（**Open Multi-Agent Interactive Classroom**）是清华大学 KEG/MAIC 团队开源的**多智能体互动课堂平台**——输入一个主题或一份资料，自动产出含幻灯片、测验、可交互仿真、PBL（项目式学习）的完整课程，并由会说话、会在白板上画图、会彼此讨论的 AI 教师与 AI 同学实时授课。

## 二、项目亮点（差异化）

- **不是"AI 生成 PPT"，而是"AI 生成一节可运行的课"**：产物不是静态文件，而是一个**可播放的课堂状态机**——AI 教师讲解、AI 同学插话提问、圆桌辩论、白板逐步推导公式、随堂点名，学生可随时打断。`lib/action/` 实现 **28+ 种动作类型**（speech、whiteboard draw/text/shape/chart、spotlight、laser…），`lib/playback/` 是驱动这一切的状态机。
- **学术背书 + 工程完成度罕见地同时具备**：论文《From MOOC to MAIC: Reimagine Online Teaching and Learning through LLM-driven Agents》发表于 **JCST 2026**（DOI 10.1007/s11390-025-6000-0），作者含 Juanzi Li、Zhiyuan Liu、Maosong Sun 等清华 NLP 核心团队。但仓库**不是论文附属 demo**——2822 个源文件、671 个测试文件、完整 CI、Docker/Vercel 双部署、npm 发布的 `@openmaic/*` SDK 家族。
- **v1.0.0 的关键转向：从"一键生成"到"可操舵的 Agent 工作台"**（2026-08-27）。新增 Pro workbench：与 agent 对话来规划课程大纲、逐页构建与修订；**session 落库、进程重启后可续跑**（leased execution + resume/steer）；20 个内置 skill（`skills/agent-runtime/` 下含 curriculum-planner、deep-research、feynman-learning、fact-check、k12-core-literacy-planning、pptx-import 等）。
- **彻底的 provider 中立**：模型、TTS/ASR、搜索、图像/视频生成、存储后端全部可插拔。已接入 OpenAI / Anthropic / Azure OpenAI / Amazon Bedrock / Ollama / Atlas Cloud、SearXNG / Brave / Baidu / Bocha、ComfyUI、VoxCPM2（含声音克隆）、FunASR（本地 ASR）、MinerU / AliDocMind（文档解析）、Lemonade（本地 AI）。
- **国际化投入超规格**：`packages/i18n` 之外，README 提及的 locale 已含 zh-CN / zh-TW / en / ko-KR / pt-BR 等多语言，`lib/i18n` 独立成模块。
- **licence 从 AGPL 转 MIT**（v0.3.0，2026-06-28）——对想拿它做商业产品的团队是决定性利好，也是这个项目星标能冲到 2.3 万的重要原因之一。

## 三、核心架构（克制呈现）

Next.js 16 + React 19 + TypeScript 5 + Tailwind 4 + **LangGraph 1.1**，单仓 monorepo。2822 个文件的分布本身就说明了重心：

```
lib/          668 文件  ← 真正的业务内核（不是 app/ 路由层）
packages/     689 文件  ← @openmaic/{dsl,renderer,editor,generation,importer,storage} 六个 SDK
tests/        671 文件  ← 测试量与业务代码 1:1
components/   365 文件
app/           86 文件  ← Next.js App Router，只是薄薄的 API 层
skills/        50 文件  ← 20 个 agent skill（Markdown + JSON 约束）
render-service/ 38 文件 ← 独立的 MP4 导出微服务（Docker）
eval/          39 文件  ← 独立评测套件（vitest.eval.config.ts）
```

`lib/` 的模块划分是理解这个系统的钥匙（40+ 子模块），最关键的六层：

| 层 | 位置 | 职责 |
|---|---|---|
| 生成流水线 | `@openmaic/generation` | 两阶段：outline 生成 → scene 内容生成 |
| Agent 运行时 | `lib/server/agent-runtime/` + `lib/agent-runtime/` | PostgreSQL 落库的会话，**leased execution**、resume/steer、skills、materials、受校验的 course tools |
| 多智能体编排 | `lib/orchestration/` | **LangGraph 状态机**（`director-graph.ts`）管理发言轮次与讨论 |
| 播放引擎 | `lib/playback/` | 驱动课堂播放与实时互动的状态机 |
| 动作引擎 | `lib/action/` | 执行 28+ 动作类型 |
| 持久化 | `@openmaic/storage` | document / runtime / KV / asset / agent-session / material / user-skill 七类 store 全可换 |

另外两个独立子系统：`render-service/`（Node 服务，chunk-executor + chunk-worker 分块渲染 MP4）、`lib/choreography/`（课堂"运镜"——cursor / laser / spotlight / timeline / timing 描述符）。

## 四、应用场景与启发（重点）

- **场景 1 — 教育机构 / 高校的 AI 课程工厂**：把讲义、PDF、录音、录像丢进去，产出可交互课堂 + 可编辑 `.pptx` + 自包含 `.html` + 课堂 ZIP（离线备份）。MIT 协议 + 自托管 + provider 中立 = **数据不出校、模型自选**，对国内高校与培训机构几乎是量身定制。
- **场景 2 — 企业内训 / 知识沉淀**：`skills/agent-runtime/` 里的 curriculum-planner + deep-research + pptx-import 组合，实际是"把已有的散乱材料变成结构化培训课程"的流水线。已有 PPT 可保留版式导入。
- **场景 3 — 多智能体系统的参考实现**：如果你要做的不是教育，而是**任何"多角色 agent 按剧本协作 + 有可视化舞台 + 支持人类随时插入"的系统**（虚拟直播、模拟面试、剧本演绎、协作评审），这个仓库是目前开源里最完整的样板。
- **场景 4 — 从聊天软件调起长任务**：内置 OpenClaw 集成，可从飞书 / Slack / Telegram / Discord 等 20+ IM 直接生成课堂，官方还发布了对应 skill（`.github/workflows/publish-openmaic-skill.yml` 自动发布到 ClawHub）。这是"IM 作为 AI 应用入口"的完整落地案例。

**核心启发（架构层面，值得抄的四件事）**：

1. **把"内容"设计成带 schema 的 DSL，而不是自由文本或直接 HTML**。`@openmaic/dsl` 用 `validate.ts` + `guards.ts` + `normalize.ts` + `scripts/gen-schema.mjs` 把课程内容定义为可校验、可 diff、可增量 patch 的结构。**LLM 生成结构化 DSL → 校验 → 渲染**这条链路，比"让 LLM 直接吐 HTML"可控一个数量级。它带来的直接红利：AI 编辑功能可以做成 **validated JSON Patch**（v0.3.1 的 "Edit with AI"），单场景原子化修改而不重生成全课。
2. **长任务必须落库 + 可租约执行（leased execution）**。v1.0.0 最重要的工程升级不是新功能，而是**会话服务端持久化**：进程重启不丢、可取消、可恢复、可中途改方向。任何"跑几分钟到几十分钟的 AI 任务"都该照这个模式做，而不是塞在一个 HTTP 请求或内存里。
3. **能力做成 skill 目录，而不是硬编码 prompt**。`skills/agent-runtime/<name>/SKILL.md` + `outline-constraints.json` 的组合——自然语言指令 + 机器可读约束——让"新增一种课程风格"变成加一个文件夹，且约束由 JSON 强制而非靠 prompt 祈祷。
4. **多智能体编排要显式建模"上下文摘要"**。`lib/orchestration/summarizers/` 单独有 6 个摘要器（conversation-summary、peer-context、state-context、whiteboard-ledger、whiteboard-conflicts、code-line-budget）——**多 agent 系统真正的难点不是让它们说话，而是让每个 agent 只看到该看的上下文**。这个目录是整个仓库最有借鉴价值的地方之一：连"白板上谁改了什么、有没有冲突"都做成了独立 ledger。

## 五、源码深度解读（核心模块）

### 5.1 `packages/@openmaic/dsl/` — 全系统的契约层

20 个文件定义了整套内容模型，切分方式很讲究：

```
src/
├── stage.ts          # 舞台（一节课的顶层容器）
├── slides.ts         # 幻灯片场景
├── interactive.ts    # 可交互 HTML 场景
├── pbl.ts            # 项目式学习场景
├── action.ts         # 28+ 动作类型的类型定义
├── validate.ts       # 校验入口
├── guards.ts         # 类型守卫
├── normalize.ts      # 归一化（容错 LLM 输出的不规范）
├── schema-roots.ts   # schema 根节点声明
├── asset-manifest.ts # 资产清单（图片/音频/视频引用）
├── slide-media-slots.ts   # 媒体插槽（先占位、后填充）
├── storage.ts / runtime.ts
└── legacy-line-geometry.ts  # 历史版本几何数据兼容
```

三个细节体现成熟度：
- **`normalize.ts` 与 `validate.ts` 分离** ——先尽力修正 LLM 输出的小毛病，再严格校验；只有 validate 才是硬门槛。这是生产级 LLM 应用的标准两段式。
- **`slide-media-slots.ts` 的插槽机制** ——内容生成与媒体生成解耦：文本先出，图/音/视频异步填进插槽。这让"生成一节课"从串行长链变成可并行、可部分失败重试。
- **`legacy-line-geometry.ts` 的存在** ——说明 DSL 已经历过破坏性变更并保留了向后兼容层。一个开源半年的项目愿意背兼容包，意味着已有真实用户数据要保。

### 5.2 `lib/orchestration/` — LangGraph 驱动的课堂导演

```
director-graph.ts      # LangGraph 状态机：谁在什么时候发言
director-prompt.ts     # 导演提示词
prompt-builder.ts      # 组装每个 agent 的最终 prompt
registry/agent-selection.ts + store.ts + types.ts   # agent 花名册与选择策略
summarizers/*          # 6 个上下文摘要器（见上文）
tool-schemas.ts        # agent 可调用工具的 schema
ai-sdk-adapter.ts      # 适配 Vercel AI SDK
stateless-generate.ts  # 无状态生成路径（不需要会话时的快路径）
```

**设计要点**：把"导演"（决定发言顺序与讨论走向）和"演员"（具体 agent 的回复生成）彻底分开。`director-graph.ts` 只管调度状态，`prompt-builder.ts` + `summarizers/` 负责给每个演员喂定制化上下文。同时保留 `stateless-generate.ts` 快路径——不是所有请求都要走状态机，这种"重路径 + 轻路径并存"的设计避免了为了架构一致性牺牲简单场景的性能。

### 5.3 `lib/choreography/` — 课堂"运镜"系统

```
cursor.ts / timeline.ts / timing.ts
descriptors/{laser, spotlight, types}.ts
```

这是很多人做 AI 课堂时会漏掉的一层：**光有内容和语音不够，还需要视觉引导**。激光笔指向、聚光灯高亮、光标移动都被抽象成带时间轴的 descriptor，和 `@openmaic/renderer/src/effects/{LaserOverlay, SpotlightOverlay, HighlightOverlay, ZoomWrapper}.tsx` 一一对应。**内容层产出"要强调哪里"，编排层决定"什么时刻、用什么效果"，渲染层只负责画** —— 三层分离，任何一层可独立替换。

### 5.4 `render-service/` — 视频导出为什么必须独立成服务

```
src/chunk-executor.ts / chunk-worker.ts   # 分块并行渲染
src/capped-stream.ts                      # 有上限的流（防 OOM）
src/artifact-store.ts                     # 产物存储
Dockerfile + docker-entrypoint.sh
scripts/egress-smoke.sh                   # 出网连通性冒烟测试
```

MP4 导出是典型的重 CPU + 长耗时 + 易 OOM 任务，塞进 Next.js 进程必然拖垮主服务。这里的处理很标准：独立 Docker 服务 + 分块 worker + capped stream 限流 + CPU 资源档位（README 提到 v0.3.2 加了 "CPU resource profiles"）。`egress-smoke.sh` 这种"部署后先测出网"的脚本也值得抄——渲染服务常常因为拉不到远程素材而静默失败。

### 5.5 测试与评测双轨

`tests/` 671 文件（与 `lib/` 668 文件几乎 1:1）、`e2e/` 23 文件、`eval/` 39 文件配独立的 `vitest.eval.config.ts`。**把"功能测试"和"AI 效果评测"用两套配置分开**是 LLM 应用的必要做法：前者要快要确定，后者慢且有随机性，混在一起 CI 会崩。另有 `.github/workflows/storage-pg-contract.yml` —— 为可插拔存储层单独跑**契约测试**，确保换后端不破功能。

## 六、全网口碑（真实信号）

- **增速**：调研当日 GitHub Trending **+907 stars/日**，为当日日榜增速最高项目之一；累计 23,639 ⭐。
- **迭代节奏**（从 CHANGELOG/News 实抓）：v0.1.0（2026-03-26）→ v0.1.1（04-14）→ v0.2.0（04-20）→ v0.2.1（04-26）→ v0.2.2（06-02）→ v0.3.0（06-28）→ v0.3.1（07-21）→ v0.3.2（08-14）→ **v1.0.0（08-27）**。**五个月九个版本**，且每版都有实质功能而非补丁——这个节奏在学术团队开源项目里极为罕见。
- **社区渠道**：Discord + 飞书社群 + 中英文双体验指南（飞书 wiki）+ Live Demo（open.maic.chat）+ 一键 Vercel 部署按钮。**中英双轨社区运营**，明显在同时争取国内外用户。
- **企业化信号**：README 有 "Partnerships" 章节；`.github/workflows/publish-packages.yml` 持续发布 npm 包；`packages/@openmaic/*` 六个 SDK 已上 npm。说明团队在把它做成生态而非单体应用。
- **值得注意的取舍**：仓库 vendor 了 `packages/pptxgenjs` 和 `packages/mathml2omml`（含 `lib/agent/VENDOR.md`）——为了 `.pptx` 导出的公式保真度选择内嵌改造第三方库，而非等上游。这是务实但会带来长期维护成本的决定。
- **潜在门槛**：完整功能需要 LLM + TTS + ASR + 搜索 + 图像/视频生成 + PostgreSQL + 渲染服务，**要全跑起来配置量不小**（README 光"Optional"小节就有 8 个）。对个人用户，一键 Vercel + 单一 provider key 是现实起点。

## 七、竞品对比 + 核心研判

| 维度 | OpenMAIC | NotebookLM | Gamma / Tome | Khanmigo | 开源 AI PPT 工具（PPTAgent 等） |
|---|---|---|---|---|---|
| 开源 | ✅ MIT | ❌ | ❌ | ❌ | ✅ 多为 MIT/Apache |
| 产物形态 | **可播放课堂 + pptx + html + zip** | 音频概览 + 笔记 | 幻灯片/网页 | 对话式辅导 | 幻灯片 |
| 多智能体互动 | ✅ 教师+同学+辩论+白板 | ❌ 双主播播客 | ❌ | ⚠️ 单导师 | ❌ |
| 实时打断/提问 | ✅ | ❌ | ❌ | ✅ | ❌ |
| 自托管 | ✅ Docker/Vercel | ❌ | ❌ | ❌ | ✅ |
| 模型可换 | ✅ 全 provider 中立 | ❌ 锁 Gemini | ❌ | ❌ | ⚠️ 部分 |
| PBL / 项目式学习 | ✅ v2 + 课堂 UI | ❌ | ❌ | ⚠️ | ❌ |
| 学术论文 | ✅ JCST'26 | ❌ | ❌ | ❌ | ⚠️ 部分有 |
| 工程完成度 | ✅ 671 测试/CI/SDK | 商业级 | 商业级 | 商业级 | ⚠️ 多为原型 |

**核心研判**：

OpenMAIC 是**目前开源世界里"AI 生成教育内容"这条赛道上完成度最高的项目**，而且它的价值有两个层次：

- **对教育场景**：它填的是一个真空。商业产品（NotebookLM / Gamma）只做单向内容生成，不做"课堂"；教育 SaaS（Khanmigo）做辅导但闭源不可自托管；开源 AI PPT 工具停在"生成幻灯片"。**只有 OpenMAIC 把"生成 + 多角色演绎 + 学生可介入 + 可导出"做成了闭环，并且是 MIT 协议。** 高校、职教、企业内训场景可以直接落地。
- **对非教育开发者（更重要）**：把它当成**多智能体 + 结构化内容生成 + 长任务运行时**的参考架构。具体来说，这四块可以直接迁移到任何领域：
  - `@openmaic/dsl` 的 "LLM 生成受校验 DSL → normalize → validate → 渲染 + JSON Patch 增量编辑" 模式；
  - `lib/server/agent-runtime/` 的 "PostgreSQL 落库 + leased execution + resume/steer" 长任务模式；
  - `lib/orchestration/summarizers/` 的 "为每个 agent 定制上下文摘要"（含 whiteboard-ledger 这种共享状态账本）；
  - `skills/agent-runtime/` 的 "SKILL.md + outline-constraints.json" 能力包格式。

- **风险点**：① 依赖面极广，全功能部署复杂度高，运维成本不低；② 教育内容质量最终受底层 LLM 能力约束，项目本身无法兜底；③ 学术团队主导的开源项目长期维护存在人员流动风险（但九个版本的节奏与 npm SDK 发布、Partnerships 章节说明团队有产品化意图，风险相对可控）；④ vendor 第三方库（pptxgenjs / mathml2omml）的长期同步成本。
- **给同类需求的一句话建议**：要做"AI 把资料变成课/演示/演绎"的产品，**先读它的 `@openmaic/dsl` 和 `lib/orchestration/summarizers/`，能省掉三个月的踩坑**。

> **关键文件速查**：
> - 内容契约层（最有借鉴价值）→ `packages/@openmaic/dsl/src/{stage,slides,interactive,pbl,action,validate,normalize,guards,slide-media-slots}.ts`
> - 多智能体编排 → `lib/orchestration/director-graph.ts`（LangGraph）、`prompt-builder.ts`、`registry/agent-selection.ts`、`summarizers/{conversation-summary,peer-context,state-context,whiteboard-ledger,whiteboard-conflicts}.ts`
> - Agent 运行时（长任务落库）→ `lib/server/agent-runtime/`、`lib/agent-runtime/{lifecycle,stage-writer-tools}.ts`、`lib/agent/runtime/{build-agent,quota,tool-timeout,allowlist,run-native-child}.ts`
> - 播放 / 动作 / 运镜 → `lib/playback/`、`lib/action/`、`lib/choreography/{timeline,timing,cursor}.ts` + `descriptors/{laser,spotlight}.ts`
> - 渲染层 → `packages/@openmaic/renderer/src/{SlideCanvas,SlideElement}.tsx` + `effects/{LaserOverlay,SpotlightOverlay,HighlightOverlay,ZoomWrapper}.tsx`
> - 能力包（skill）格式 → `skills/agent-runtime/*/SKILL.md` + `outline-constraints.json`（curriculum-planner / deep-research / deep-interactive / feynman-learning / fact-check / k12-core-literacy-planning / lecture-style / page-clone / pptx-import / build-personal-skill）
> - 视频导出微服务 → `render-service/src/{chunk-executor,chunk-worker,capped-stream,artifact-store}.ts`
> - API 入口一览 → `app/api/agent/sessions/`、`app/api/generate-classroom/`、`app/api/pbl/v2/`、`app/api/export-video/`
> - 存储契约测试 → `.github/workflows/storage-pg-contract.yml`；AI 效果评测 → `eval/` + `vitest.eval.config.ts`
> - 论文引用 → JCST'26，DOI `10.1007/s11390-025-6000-0`
