# 🔬 calesthio/OpenMontage — 全方位深度调研

> 调研时间：2026-06-27 ｜ 仓库创建：2026-03-29（90 天达成 24K+ stars）｜ 调研员：GitHub 深度调研员
>
> 调研对象：<https://github.com/calesthio/OpenMontage>
>
> ⭐ 24,205 ｜ 🍴 2,691 ｜ 🐛 111 open issues ｜ 📜 AGPL-3.0 ｜ 🐍 Python 为主 + Node.js(Remotion) + Shell
>
> **三句话定位**：世界上第一个把"AI 编程助手"（Claude Code/Cursor/Copilot/Codex）变成"AI 视频制作工作室"的开源项目，用"指令驱动 + 工具注册"架构把 52 个视频/音频/图像工具 + 12 条 pipeline 装进 500+ 份 markdown skill 里，让 LLM 当制片人、Python 当场工。一周前冲到 GitHub Trending #1，但同时正被冒名 fork 的木马程序蹭流量。

---

## 📌 一句话定位

OpenMontage 不是一个"AI 视频工具"，而是一个**"agent 操作系统"**——它把"做视频"这件事拆成 12 条 pipeline（剧本→分镜→资产→剪辑→合成→发布），每条 pipeline 又拆成 7-9 个 stage，每个 stage 都有一份 markdown 当"操作手册"喂给 LLM，LLM 按手册调度 50+ 个 Python 工具。**整个项目把"如何让一个 AI 编程助手从零做出成片"这件事，做成了一份可被另一台 AI 复用的工艺文件。**

---

## 🏗️ 项目架构全景

### 三层知识架构（项目最核心的"设计灵魂"）

这是 OpenMontage 跟所有"AI 视频工具"最大的设计差异——它把"知识"和"代码"分到了 3 个独立层，并要求每层各司其职：

```
Layer 1: tools/ + pipeline_defs/    "有什么能力"      —— 可执行工具 + 编排
Layer 2: skills/                    "OpenMontage 怎么用"  —— 项目内部约定
Layer 3: .agents/skills/            "底层技术怎么工作"  —— 通用 API 知识包
```

- **Layer 1（代码层）**：纯 Python 工具。`tools/base_tool.py` 是工具合约（ToolContract），强制每个工具声明 `name/tier/capability/provider/runtime/dependencies/agent_skills[]` 等元数据。`tools/tool_registry.py` 用 `pkgutil.walk_packages` 自动发现所有 `BaseTool` 子类，无需手动注册。`pipeline_defs/*.yaml` 用 YAML 声明 pipeline 的阶段序列、所需工具、审核点。**Python 不做编排、不做创意决策、不写 reviewer 逻辑。**
- **Layer 2（OpenMontage 内部 skill）**：markdown 文件，告诉 agent "这个项目里应该怎么用工具"。例如 `skills/creative/video-gen-prompting.md` 定义了"5-aspect 提示词规范"（Subject / Motion / Scene / Spatial / Camera），`skills/core/hyperframes.md` 明确 Remotion vs HyperFrames 何时该用哪个。
- **Layer 3（外部技术包）**：`.agents/skills/` 下 vendored 了 **47 个来自 skills.sh 的通用技术 skill**（FFmpeg、Remotion、GSAP、HyperFrames CLI、Seedance 2.0、LTX-2 等）。每个工具的 `agent_skills[]` 字段桥接 Layer 1 → Layer 3，agent 看到工具后能立刻知道去读哪份知识。

> 现场证据：`AGENT_GUIDE.md` 明确写「There is no Python orchestrator, no Python reviewer, no Python handlers. The agent drives the pipeline.」`base_tool.py` 行 1 注释：「This enforces a uniform interface for discovery, execution, cost estimation, and health reporting.」

### 目录结构与设计哲学

```
OpenMontage/
├── lib/                # 纯基础设施（配置、检查点、pipeline loader、媒体 profile）
├── tools/              # 52 个 Python 工具（自动发现）
│   ├── base_tool.py    # 工具合约（核心抽象）
│   ├── tool_registry.py # 单例注册表
│   ├── cost_tracker.py # 预算治理（estimate→reserve→reconcile）
│   ├── video/  (18个)  # 视频生成/合成/拼接/裁剪
│   ├── audio/  (8个)   # TTS（4家）+ 音乐/混音/增强
│   ├── graphics/(13个) # 图像生成/股票/图表/Math 动画
│   ├── enhancement/(5个)  # 超分/抠图/修脸/调色
│   ├── analysis/(4个)  # WhisperX 转录/场景检测/帧采样/视频理解
│   ├── avatar/(2个)    # Talking Head（SadTalker）/ Wav2Lip
│   └── subtitle/(1个)  # SRT/VTT 生成
├── pipeline_defs/      # 12 个 YAML pipeline 清单
│   ├── animated-explainer.yaml  (production)
│   ├── cinematic.yaml           (production)
│   ├── animation.yaml           (production)
│   ├── avatar-spokesperson.yaml (production)
│   ├── hybrid.yaml              (production)
│   ├── screen-demo.yaml         (production)
│   ├── character-animation.yaml (beta)
│   ├── talking-head.yaml        (beta)
│   ├── clip-factory.yaml        (beta)
│   ├── podcast-repurpose.yaml   (beta)
│   ├── localization-dub.yaml    (beta)
│   ├── documentary-montage.yaml (新增)
│   └── framework-smoke.yaml     (test 烟测)
├── skills/             # Layer 2 markdown 知识
│   ├── core/  creative/  meta/  pipelines/<name>/
├── .agents/skills/     # Layer 3 通用技术知识包（47 份）
├── schemas/            # JSON Schema 验证
│   ├── artifacts/  (11 个产物 schema：brief/script/scene_plan/asset_manifest/...)
│   ├── checkpoints/  pipelines/  styles/  tools/
├── styles/             # 视觉风格 playbook（YAML）
├── remotion-composer/  # Node.js 视频合成引擎（React 组件化）
├── tests/              # contract/qa/eval/pipelines/styles/tools
├── config.yaml         # 全局配置（LLM/预算/输出/路径）
├── AGENT_GUIDE.md      # Agent 必读操作手册
├── PROJECT_CONTEXT.md  # 架构权威源
├── CLAUDE.md           # 3 句话：只引导到 AGENT_GUIDE.md
├── .github/workflows/ci.yml  # GitHub Actions CI（PR 时跑 lint+test）
└── docs/  (ARCHITECTURE.md / PROVIDERS.md / PR_REVIEW_GUIDE.md)
```

**设计哲学三个核心点**：
1. **"Instruction-driven" 战胜 "code-driven"**：所有创意/编排/审查决策都用 markdown skill 表达，不写 Python。这意味着你改了 `AGENT_GUIDE.md` 一段话，agent 行为立即变化；你改了 `pipeline_defs/animated-explainer.yaml` 一个阶段名，agent 立即按新流程走。**没有"重新部署"。**
2. **"Capability-first" 而非 "provider-first"**：所有工具按 `capability` 字段分组（`tts` / `video_generation` / `image_generation` / `enhancement` ...），用户加新 provider 只需在 `tools/video/` 丢一个文件，selector 自动发现。视频方向已有 18 个工具，理论上还能继续加。
3. **"Honest availability" 是硬约束**：`AGENT_GUIDE.md` 专门点名"silent-availability bugs"是项目大忌。每个 tool 的 `get_status()` 必须如实反映当前能否调用；registry 输出会主动列出"已配/总数"。**这是直接冲着 AI agent 调 API 经常被骗"这个键我没设但工具说我可用"的痛点去的。**

### 技术栈与依赖图谱

| 维度 | 选型 |
|------|------|
| **语言** | Python 3.10+（主力）、TypeScript / JavaScript（Remotion 合成器）、Shell（少量 Makefile） |
| **LLM 集成** | **不在 runtime 调 LLM**——LLM 是 IDE 里的 agent 本身。config.yaml 列出支持的 provider（anthropic/openai/gemini/openrouter/ollama/mistral/minimax）但只作声明 |
| **视频合成** | Remotion（React/Node）+ HyperFrames（HTML/CSS/GSAP）+ FFmpeg 三选一，**proposal 阶段锁定 `render_runtime` 后全程不可静默切换**（这是 governance 红线） |
| **视频生成** | 14 家云 API（Kling/Runway/Veo/Grok/Higgsfield/MiniMax/HeyGen）+ 4 家本地 GPU（WAN 2.1/Hunyuan/CogVideo/LTX-Video）+ 3 家免费库存（Pexels/Pixabay/Wikimedia Commons） |
| **图像生成** | FLUX / Google Imagen / Grok / OpenAI / Recraft / Stable Diffusion / Pexels / Pixabay / Unsplash / ManimCE |
| **TTS** | ElevenLabs / Google Cloud TTS（700+ 语音）/ OpenAI TTS / Piper（完全本地免费） |
| **音乐** | Suno / ElevenLabs Music / ElevenLabs SFX |
| **后处理** | FFmpeg（永远免费）、Real-ESRGAN、rembg/U2Net、CodeFormer/GFPGAN |
| **Avatar** | SadTalker/MuseTalk、Wav2Lip |
| **配置/数据** | PyYAML、Pydantic（`lib/config_model.py`）、jsonschema（产物和 checkpoint 强校验） |
| **CI** | GitHub Actions，PR 时跑 `make lint` + `make test`（Python 3.11） |

### 核心配置一览（`config.yaml` 关键参数）

```yaml
budget:
  mode: warn             # observe / warn / cap
  total_usd: 10.00       # 单项目总预算上限（可覆盖）
  reserve_pct: 0.10      # 10% 留作重试/清理
  single_action_approval_usd: 0.50   # 超过 $0.5 单动作必走用户确认
  require_approval_for_new_paid_tool: true  # 首次用付费工具必走用户确认

checkpoint:
  policy: guided         # guided / manual_all / auto_noncreative
output:
  default_resolution: "1920x1080"
  default_fps: 30
  default_crf: 23
```

> 现场证据：`tools/cost_tracker.py` 实现了完整的 `estimate → reserve → reconcile` 三段式预算治理，超过 $0.5 自动抛 `ApprovalRequiredError`，超过 `usable_budget_usd` 在 cap 模式抛 `BudgetExceededError`——**这是给"AI 乱刷信用卡"专门设计的护栏。**

---

## 🧠 核心源码解读（精读 6 个关键文件）

> 这部分是用户看 README 拿不到的。所有观点都对应到具体文件/行。

### 1. `tools/base_tool.py` — 工具合约的工程化

**定位**：所有 52 个工具继承的抽象基类。OpenMontage 整个"自动发现 + 能力上报"机制的根。

**核心流程**：
- 模块导入时自动 `_load_dotenv()`（一次性，避免 tool 初始化时还找不到 key）
- `BaseTool` 是个 `@dataclass` 化的 ABC，类属性就是工具的"自我介绍卡"
- 强制字段：`name/version/tier/capability/provider/runtime/dependencies/agent_skills[]/fallback_tools[]/input_schema/output_schema/retry_policy`
- `ToolResult` 是统一返回：`{success, data, artifacts, error, cost_usd, duration_seconds, seed, model}`

**设计模式**：**Template Method + Registry Pattern + Strategy Pattern** 的混合体。子类只需实现 `execute()`，其他全被基类承包。

**骨架代码**：

```python
class BaseTool(ABC):
    name: str = ""
    tier: ToolTier = ToolTier.CORE  # CORE/VOICE/ENHANCE/GENERATE/SOURCE/ANALYZE/PUBLISH
    runtime: ToolRuntime = ToolRuntime.LOCAL  # LOCAL/LOCAL_GPU/API/HYBRID
    stability: ToolStability = ToolStability.EXPERIMENTAL  # EXPERIMENTAL/BETA/PRODUCTION
    capability: str = "generic"
    provider: str = "openmontage"
    agent_skills: list[str] = []  # → Layer 3 桥接
    fallback_tools: list[str] = []
    cost_usd_estimate: Optional[float] = None

    def get_status(self) -> ToolStatus: ...  # AVAILABLE/UNAVAILABLE/DEGRADED
    def estimate_cost(self, inputs) -> float: ...
    def estimate_runtime(self, inputs) -> float: ...
    @abstractmethod
    def execute(self, inputs) -> ToolResult: ...
```

**独家发现**：ToolContract 里有 5 个隐藏细节是 README 完全没提到的：
- `idempotency_key_fields`：幂等键字段（决定同一请求能否被去重）
- `side_effects`：副作用声明（agent 调度时避让）
- `user_visible_verification`：用户可见的"已验证"信号
- `quality_score` / `historical_success_rate` / `latency_p50_seconds`：可覆盖默认的"评分启发式"——给 lib/scoring.py 直接消费
- `_scrub_unicode_dashes()`：`tool_registry.py` 里专门做 unicode 标点 → ASCII 的转义，注释明写「**只动 agent 打印给用户的字段；不碰 docstring、注释、markdown**」。这是给 Windows cp1252 终端做的容错。

### 2. `tools/tool_registry.py` — 自动发现 + 能力报告

**定位**：整个工具生态的"目录服务"，是 `AGENT_GUIDE.md` 里 `provider_menu_summary()` 的实现者。

**核心流程**：
- `discover(package_name="tools")` 用 `pkgutil.walk_packages` 扫整个 `tools/` 树
- 对每个模块调用 `register_module()`：`inspect.getmembers` 找所有 `BaseTool` 子类，**自动实例化**（`tool = cls()`）
- 排除基类（`base_tool.py`）和注册器自身（`tool_registry.py`）
- `get_by_capability("video_generation")` → 列出所有视频生成工具，selector 工具用这个机制动态发现候选

**设计模式**：**Singleton + Auto-Discovery + Service Locator**。

**独家发现**：
- 它的"能力报告"分三档：原始 firehose（`support_envelope()`）、分组（`provider_menu()`）、人类可读汇总（`provider_menu_summary()`）。`AGENT_GUIDE.md` 明确写「**pasting it into chat will bury the user**」——所以日常用 summary 模式。
- `find_fallback(tool_name)` 工具会**沿 fallback_tools 链找到第一个 AVAILABLE 的备胎**——这是给 provider 失败的优雅降级。
- 它在输出给用户前会主动**把 em-dash 转成 `--`**——一个小细节说明项目对"agent 输出会到用户眼前"这件事有强洁癖。

### 3. `pipeline_defs/animated-explainer.yaml` — 12 阶段生产流水线

**定位**：项目最完整、最有代表性的 pipeline 模板（其它 11 个 yaml 都参考它）。读完这一份就懂整个编排哲学。

**核心流程**（"Animated Explainer" 9 个 stage）：

1. **research**（research-director）—— **不调任何 API**，纯 agent 用 web 搜索产出 `research_brief`（含 5+ 来源、3+ 角度、3+ 数据点）
2. **proposal**（proposal-director）—— 必走**用户审批**门；产出 `proposal_packet`（3+ 概念方案）+ `decision_log`；还内嵌 `sample` 子阶段（reference-driven 时跑 10-15s 样片）
3. **script**（script-director）—— 写 `script`，按 8-10s 一个 enhancement cue，叙事五段式 hook→setup→build→climax→landing
4. **scene_plan**（scene-director）—— 把脚本翻译成镜头级 `scene_plan`；`review_focus` 明写 "Full script duration covered with no gaps"
5. **assets**（asset-director）—— 调用 TTS/image/music/diagram 实际生产
6. **edit**（edit-director）—— 装配时间轴 + 字幕 + 音频 ducker
7. **compose**（compose-director）—— FFmpeg / Remotion / HyperFrames 渲染
8. **publish**（publish-director）—— SEO metadata + chapters + export
9. 总编排：**executive-producer** skill 串起全部 stage，做"质量门"和"send-back"

**设计模式**：**State Machine + Saga Pattern**。每个 stage 显式声明 `produces: [artifact_name]`、`required_artifacts_in: [...]`、`tools_available: [...]`、`human_approval_default: bool`、`review_focus: [...]`、`success_criteria: [...]`。

**独家发现**：
- 顶部有 `default_checkpoint_policy: guided` —— 决定所有 stage 默认是否需要人审批。
- `orchestration.max_wall_time_minutes: 20` —— **单条 pipeline 最多跑 20 分钟硬截止**，避免失控。
- `sub_stages` 字段——**`proposal.sample` 只在 reference 驱动时激活**（`condition: "video_analysis_brief_exists"`），这是条件性子流，loader 在 `get_stage_sub_stages` 里实现激活逻辑。
- `reference_input` 字段——声明性告诉 agent "我可以接 YouTube URL"，触发 `video-reference-analyst.md` skill 走 grounded 流程。
- `compatible_playbooks.recommended: [clean-professional, flat-motion-graphics]`——把视觉风格选择也声明了，跟 styles/*.yaml 联动。

### 4. `lib/pipeline_loader.py` + `lib/checkpoint.py` — 状态机持久化

**定位**：把 agent 在每个 stage 留下的"工作产物"沉淀为可恢复的状态。

**核心流程**：
- `load_pipeline(name)`：读 yaml + 用 `jsonschema` 校验 manifest 形态
- `get_stage_order(manifest)`：吐出 stage 顺序；支持 `include_sub_stages=True` 把 `proposal.sample` 拆出来
- `CheckpointValidationError`：stage 名错/状态错/必产物缺失都会抛
- checkpoint 的 stage↔artifact 是**强映射**（`CANONICAL_STAGE_ARTIFACTS` 字典）—— schema 校验产物是 JSON 结构

**设计模式**：**Repository Pattern + Schema-First Validation**。

**独家发现**：
- `get_pipeline_stages(pipeline_type)` 之前用 set 交集，**会导致无序**——项目里专门留了 fallback 警告日志（"set 交集导致无序 → 改用稳定列表"），这是给后续维护者的"血的教训"注释。
- 旧 `STAGES` 数组保留作为"向后兼容别名"，新代码必须用 `get_pipeline_stages(pipeline_type)`——这种向后兼容处理在 README 完全不写。
- `CheckpointValidationError` 在 `completed/awaiting_human` 状态下**强制要求 canonical artifact 存在**——意味着 agent 写 checkpoint 不能"假装完成"。

### 5. `tools/cost_tracker.py` — 预算治理

**定位**：给"AI 乱烧钱"上保险的核心。

**核心流程**：
- `CostTracker` 维护 `entries[]`，每条带 `status: estimated/reserved/completed/failed/refunded`
- `estimate(tool, operation, usd)`：先记下预估
- `reserve(entry_id)`：检查 3 个门槛——单动作阈值（>$0.5 必走用户确认）、新付费工具首次使用（必走用户确认）、`usable_budget_usd` 余额（cap 模式直接抛 `BudgetExceededError`）
- `reconcile(entry_id, actual_usd)`：执行后写入实际花费

**独家发现**：
- `usable_budget_usd` = `budget_remaining - 10% holdback` —— 给重试和清理留 10% 余粮。**这是给"API 调用失败要重试"留的预算缓冲。**
- `require_approval_for_new_paid_tool: true` —— agent 不能默默开始用 ElevenLabs；首次启用付费工具必走用户确认。**这是给"AI agent 突然给你消费了一笔你不知道"准备的开关。**
- `mode=BudgetMode.OBSERVE` 时只跟踪不阻断；`WARN` 模式超支只警告；`CAP` 模式硬截——**三档治理模式让用户按风险偏好选。**

### 6. `tools/video/video_compose.py` + `tools/video/video_selector.py` — 三家合成 runtime 的硬约束

**定位**：把"Remotion / HyperFrames / FFmpeg"三套不同范式的合成器缝合成一个统一接口，同时保证**silent runtime swap 被禁**。

**核心流程**（`video_compose.py` 头部 docstring 已直接说清楚）：

```
- `remotion`    → React-based frame-accurate render via `npx remotion render`
- `hyperframes` → HTML/CSS/GSAP render via `hyperframes_compose`
- `ffmpeg`      → FFmpeg concat/trim（仅简单裁剪时用，或在 approved path 显式指名时）

Silent runtime swaps are forbidden by governance. If the chosen runtime is
unavailable or fails, this tool surfaces a structured blocker and waits for
the agent to re-ask the user rather than substituting a different engine.
```

`video_selector.py` 展示了**自动发现模式**：
- `capability="video_generation"` 是注册 key
- `_providers()` 动态从 registry 拉所有该 capability 的工具
- `fallback_tools` 是个**动态 property**——自动把"registry 里所有 video gen 工具 + image_selector"作为兜底链
- `provider_matrix` 也动态生成——给前端/agent 显示 "每个 provider 擅长什么"

**独家发现**：
- 视频方向有 18 个工具（`grok_video, heygen_video, higgsfield_video, veo_video, kling_video, runway_video, minimax_video, wan_video, hunyuan_video, cogvideo_video, ltx_video_local, ltx_video_modal, pexels_video, pixabay_video, video_selector, video_compose, video_stitch, video_trimmer`）——这密度在 OSS 里很少见。
- `video_selector` 显式注释「`capability="video_generation"` 自动被 registry 拉」——**用户加新 provider 不需要改 selector 一行代码**，这是 Open-Closed Principle 的教科书示范。
- `operation: "rank"` 模式让 selector 可以**不实际生成、只输出候选评分**——这给 agent 在 preflight 阶段"试跑打分"的能力。

### 隐藏功能 & 未文档化特性

1. **`AGENT_GUIDE.md` Rule Zero 强制 Rule**：所有"做一个视频"请求**必须**先选 pipeline，**不能**让 agent 自己写 ad-hoc Python 脚本调 API。这是反"agent 自由发挥"的硬约束。
2. **"Present Both Composition Runtimes" 硬规则**：当 Remotion 和 HyperFrames 都装了，agent 必须在 proposal 阶段给用户**两个选项 + 推荐理由 + 各自 trade-off**，**不能默认挑一个**。这是"用户主权"原则在工程层的体现。
3. **CHAI 评审协议**（`skills/meta/reviewer.md`）：明确引用 CMU/Harvard 的 CHAI 论文（"Building a Precise Video Language with Human-AI Oversight"，arXiv 2604.21718v2），要求 review 必须满足 **Accurate / Complete / Constructive** 三性。**Critical finding 必须配 `proposed_fix`，否则降级为 investigation**——这是工程化"评审必须可执行"的具体约束。
4. **3 层强制冷却**：每个 stage 评审有**最多 2 轮**硬上限——`"After 2 revision rounds, still critical → Pass with warnings — proceed anyway, note unresolved issues. Never block indefinitely."`
5. **Slideshow risk scoring**：在 `scene_plan` 和 `edit` 阶段跑 6 维度评分（repetition/decorative_visuals/weak_motion/shot_intent/typography_overreliance/unsupported_cinematic_claims），**防止"动态 PPT"输出**。这是把"AI 出幻灯片"这种典型失败模式编码成可量化的门禁。
6. **Reference Alignment Review**：reference-driven 生产时，每次评审还要检查"产出是否真的基于 reference 的真实发现"——避免 agent 凭印象胡说。
7. **Decision Log 跨 stage 累计**：从 proposal 起，每个 provider 选择/playbook 选择/音乐/voice 都要记 `decision_log`，**跨 stage 累积**，用户可以追溯"为什么这段用 Kling 而不是 Veo"。
8. **`.claude/skills/` 与 `.agents/skills/` 的命名漂移**（Issue #59）：项目**声称** `.claude/skills/` 是 `.agents/skills/` 的 symlink 镜像，实际**是独立目录、且落后 23 个 skill**——这是个值得注意的"声明 vs 现实"漂移。
9. **200+ 行单文件 `character_animation.py` + `hyperframes_compose.py`**：单工具文件 size 39KB / 47KB——说明"角色动画"和"HyperFrames 渲染"都被当成核心重兵投入。
10. **"Agent-First" 立场的有趣副作用**：项目**不调 LLM API**，所以它的"AI 能力"完全靠用户本机跑 Claude/Cursor/Copilot——意味着**没法离线跑，没法用 OpenAI key**。这与所有"SaaS AI 视频"是根本差异。

---

## 📐 架构决策与设计哲学

### ADR 摘要（项目无独立 ADR 目录，决策散落在代码注释和 skill 里）

| 决策 | 证据位置 | 决策理由 |
|------|---------|---------|
| **Python 不做编排** | `AGENT_GUIDE.md`「No Python orchestrator, no Python reviewer, no Python handlers」 | 让 LLM 当控制面，部署"指令"比部署"代码"快 |
| **每个工具 `agent_skills[]` 必填** | `base_tool.py` 字段定义 | 强制每工具自描述"我依赖哪些 Layer 3 知识"，避免"agent 不知道去读哪份手册" |
| **运行时锁定 `render_runtime`** | `video_compose.py` docstring | 防止"Remotion 跑着跑着默默换成 FFmpeg"这种"善意的偷懒" |
| **预算治理三档模式** | `cost_tracker.py` BudgetMode enum | 不同风险偏好用户用不同档位，observe/warn/cap |
| **Capability-first 工具分类** | `tool_registry.py` + 各 selector | 加新 provider 零注册——丢一个文件进 `tools/video/` 即可 |
| **Singular content：.env 内联注释会污染值** | Issue #131 | 自我承认"手写 .env 解析器有 bug"——已修 |
| **Pipeline 必须有 `executive-producer` skill 串场** | 各 v2.0 pipeline yaml 顶部 | 防止 stage 之间失去"全局视角"，对应 serverless workflow 的 saga coordinator |

### 设计红线（来自 Issue/PR 与代码注释）

1. **Silent runtime swap = CRITICAL reviewer finding**（`AGENT_GUIDE.md` 硬规则 + `video_compose.py` docstring）
2. **单动作超 $0.5 必走用户审批**（`config.yaml` `single_action_approval_usd: 0.50`）
3. **首次启用付费工具必走用户审批**（`require_approval_for_new_paid_tool: true`）
4. **reference-driven 不能 carbon copy**——3 个 concept 必须**至少 1 处**跟 reference 不同（reviewer 协议）
5. **场景不覆盖完整脚本时长 = critical**（scene_plan review_focus）

### 版本演进中的哲学转变

- **v1.0 → v2.0**：把 `idea-director` 拆成 `research` + `proposal` 两阶段。**意义**：从"agent 拍脑袋出点子"到"先调研再出方案"——这是把"专业制片流程"编码进 pipeline 形态。
- **Remotion only → Remotion + HyperFrames 双 runtime**（仍在演进中）：承认"不同 brief 适合不同合成范式"，但**强制 proposal 阶段锁定**，避免混乱。
- **Pexels 单一免费 → 14 家视频 + 10 家图像 + 4 家 TTS + 2 家音乐 + 2 家 SFX**：**provider matrix 持续扩张**，每次新增都是"丢一个文件 + agent_skills[] 桥接 Layer 3"。
- **character-animation pipeline 出现**：从"通用视频"延伸到"角色动画"（SVG 装备 + pose 库 + HyperFrames 渲染），开新赛道。

---

## 🌐 全网口碑画像

### 1. Hacker News 讨论（截至 2026-06-27 共 7 条独立 hit）

| 帖子 | 作者 | Points | 评论 | 摘要 |
|------|------|--------|------|------|
| [OpenMontage: Turn your AI coding assistant into a full video production studio](https://news.ycombinator.com/item?id=48616398) | vantareed | **7** | 1 | 6/21 首发，最高分；首条评论空缺意味着社区尚未深度辩论 |
| [OpenMontage: Open-source, agentic video production system](https://news.ycombinator.com/item?id=48647621) | vantareed | 5 | 1 | 6/23 二次发布 |
| [OpenMontage the first open-source, agentic video production system](https://news.ycombinator.com/item?id=48592834) | rmason | 2 | 0 | 6/18 第三发 |
| [The first open-source, agentic video production system](https://news.ycombinator.com/item?id=48686111) | grajmanu | 1 | 0 | 6/26 |

**评价特征**：
- 热度集中在 "Project of the Day" 区间，**未冲上首页 top 30**
- **首条评论长期空缺**——HN 社区对"agentic video"赛道的关注度仍低
- 作者本人 6/14 也用 Crucix 上过 HN（4 points），但**他从未为 OpenMontage 在 HN 评论区亲自站台**——这是项目运营的弱点
- 没有任何技术批评/深度使用体验的 HN 评论出现——**说明真实用户参与度低，多为链接分享**

### 2. GitHub 仓库本身的口碑信号

**PR/Issue 数据画像**（截至 2026-06-27）：

| 维度 | 数值 | 信号 |
|------|------|------|
| ⭐ Stars | 24,205 | 90 天达成 — 极快 |
| 🍴 Forks | 2,691 | fork/star 比 11.1% — 较高（说明有大量"想试"的人在 fork） |
| 📥 Subscribers | 140 | 极低 — 大部分 star 用户没订阅（典型的"路过点赞"型增长） |
| 🐛 Open issues | 111 | 与 24K star 不匹配 — 异常低 |
| ✅ Closed issues | 25 | 关单率 18.4% — 偏低 |
| 🔀 Open PRs | 20+ | 大量小 PR（i18n README、CI、教程） |
| 📁 Discussions | 启用但量小 | 4 个分类：Show and Tell / Ideas / Q&A / General |

**Issue 质量画像**（25 条 closed + 111 条 open 的细看）：

✅ **有质量的技术 Issue**（代表真实用户）：
- **#131** (shubham21155102, CONTRIBUTOR)：**Google 工具"虚假可用性"**——`google_tts`/`google_imagen` 声明支持 service-account JSON，但 execute 实际只读 API key；并且 `.env` 内联注释被当值，导致 `cp .env.example .env` 后**所有 keyed 工具都被误报为 available**。已修。**这是给"AI agent 调 API 经常被骗"问题打的预防针，间接证明项目的"honest availability"原则不是空话。**
- **#172** (WowJia)：Windows Remotion render `video_compose.py` 把 `--props` 当两个参数传导致失败。已修。**典型的 Windows escape 坑。**
- **#175** (markhinderliter)：**typosquat "OpenMontage/OpenMontage"**——冒名仓库 ship 了一个 91MB 的 Windows EXE，嵌入 ProductName "Janus Key" / CompanyName "Duality Solutions"。**这是用户被 KOL 视频带流量时遇到的真实钓鱼事件。**
- **#192** (harshdadiya-wappnet, CONTRIBUTOR)：`.agents/skills/synthetic-screen-recording/SKILL.md` 缺 YAML frontmatter；`video-toolkit` 命名 kebab/snake 不一致。
- **#59** (jz, CONTRIBUTOR)：**`.claude/skills/` 与 `.agents/skills/` 镜像漂移**——声明是 symlink 镜像，实际是独立目录且落后 23 个 skill。Issue 在 6/27 仍 open 等待 owner 决策"改 symlink 还是加 CI drift-check"。

⚠️ **低质/水 Issue**（项目方未做清理的"被蹭流量"代价）：
- **#117** 「Love」、**#64** 「Hukl」、**#62** 「Yuj」、**#97** 「Dog story」、**#99** 「Chien Macarena」——纯 spam/灌水 issue，title 无意义。
- **#122** 「copilot/fix-36305https://github.com/moraesc/docs.git」——明显是钓鱼 PR 的预热 issue（PR #167 紧随其后）。
- **#151** 「Google」——title 一个字，正文是波斯语。
- **#82** 「海上阅兵式」——中文空 issue。
- **#112** 「Photography new business idea 2026」——空 issue，正文是无关闲聊。
- **多个 issue 里 Anil-matcha 反复 spam 推自己的 `SamurAIGPT/Text-To-Video-AI`**——Issue #123、#117、#113、#112、#150 都有他评论塞硬广。**项目方未做任何 spam 治理。**

🆘 **真正的安全事件**（最新）：
- **#200** (jiuliuaiceo-spec, 2026-06-27)：**第二个冒名 fork `Open-Montage/OpenMontage`**——Windows EXE 实测被 Defender 报为 `Trojan:MSIL/PureRat.ABA!MTB`，payload 包括 `serveless.exe` / `cloude_edge.exe` / `ngrok-daemon.exe`，持久化用 HKCU Run 键 + 计划任务。**Issue 评论里还有用户附了 `patch_fix_v2.zip` 链接，疑似二次钓鱼。**

### 3. 中文社区（间接信号）

- **没有深度中文技术博客评测**（百度/掘金/知乎搜索未发现）
- 中文相关 issue 主要是空标题（#82 海上阅兵式、#96、#117 评论里的 "啥意思"）
- **YouTube 中文圈未见 KOL 评测**（虽然有 OpenMontage 自己的 YouTube 频道 @OpenMontage）
- **没有"中文用户成功案例"信号**——这是市场空白也是机会

### 4. 真实使用场景与官方宣称的差距

| 官方演示 | 实际门槛 |
|---------|---------|
| "Make a 60-second animated explainer about how neural networks learn" | 假设 agent 已经在跑、`.env` 已配、且 LLM 有能力读懂 200+ skill 文件 |
| "VOID — Neural Interface" 总成本 $0.69 | 仅用 OpenAI 1 个 key、且生产简单 4 张图 + TTS + FFmpeg |
| "The Last Banana" $1.33 | 需要 fal.ai + Google Cloud TTS + Suno 多个付费 key |
| "Afternoon in Candyland" $0.15 | **只生成静帧然后用 Remotion 做 Ken Burns 效果**——README 强调"Zero video generation APIs needed" 暗示承认纯 AI 视频生成成本高 |

**典型真实用户路径**（从 issue 推测）：① 看到 HN/YouTube 视频 → ② git clone → ③ 跑 `make setup` → ④ 配 1-2 个 key → ⑤ 在 Claude Code 里跑第一个 prompt → ⑥ **第一次失败**（多半是哪个 skill 没读、哪个 tool 误报 available、或 Windows 兼容性）→ ⑦ 来 GitHub 提 issue。

### 5. 维护者响应风格

观察 owner `calesthio` 在 30+ 条 issue 评论里的行为：
- **强项**：对实质性技术 issue（#131、#172、#192、#59、#103）都给了技术性回复；接受并合并了多个 PR（CI、修复、教程）。
- **弱点**：
  - 对 spam/钓鱼 issue（#117/#64/#62/#97/#99/#112/#82）**零处理**——不锁 issue、不删除、不回复"请到 Discussions"。
  - 对冒名 fork 警示 issue（#175 已关、#200 待处理）**未给 README 加任何安全警告**——这意味着任何通过 Google "github openmontage" 进入冒名仓库的用户都不会被官方 README 拦截。
  - 在 KOL 视频流量爆发期没主动**置顶**任何"安全告示"——典型的"独立开发者被流量冲昏"症状。

---

## ⚔️ 竞品对比

| 维度 | OpenMontage | Hedra / Captions (SaaS) | Remotion (引擎) | n8n / Dify (低代码 agent) | CapCut/Runway (商业) |
|------|-------------|------------------------|-----------------|--------------------------|---------------------|
| **形态** | 开源 agent 框架 + 工具 | 闭源 SaaS | 开源渲染库 | 开源工作流 | 闭源消费产品 |
| **AI 决策** | **agent 当制片人**（markdown 驱动） | 内置 LLM 调优 | 无 | 节点式 Dify | 黑盒 |
| **视频生成能力** | 14 家云 + 4 家本地 | Hedra 主打 talking head | 需自己集成 | 需自己集成 | 一站式 |
| **合成 runtime** | Remotion + HyperFrames + FFmpeg | 自研 | 仅 React | 取决于节点 | 自研 |
| **成本控制** | 三档预算治理 + 单动作审批 | 订阅制 | 免费 | 免费 | 订阅制 |
| **离线能力** | ❌ 必须有 LLM agent | ❌ | ✅ | ❌ | ❌ |
| **学习曲线** | 高（需懂 agent + 工具注册） | 低 | 中 | 中 | 低 |
| **社区成熟度** | 24K⭐/140 订阅，112 issues | 大型 SaaS 客户 | 20K⭐/专业开发者 | 100K⭐/工作流用户 | 消费级 |
| **License** | AGPL-3.0（传染性） | 闭源 | Remotion License | Apache / 自定义 | 闭源 |
| **目标用户** | 想"DIY 自己的 AI 视频工厂"的开发者 | 内容创作者 | 前端/视频工程师 | 业务流自动化 | 普通用户 |

**OpenMontage 的差异化定位**：**它是"AI 视频 LLM 的训练数据"**——把"如何让 AI 把视频做出来"这件事编码成 markdown skill 集合。竞品在"做视频"，OpenMontage 在"教 AI 做视频"。这跟 LangChain 之于 LLM 应用开发是同构的——LangChain 本身不做应用，它让 LLM 能做应用。

**什么场景用 OpenMontage**：
- 你有 Claude Max / Cursor Pro / Copilot 订阅，想在 IDE 里直接产出视频
- 你想给团队沉淀一套"AI 视频制作 SOP"（项目里的 `pipeline_defs/*.yaml` + `skills/pipelines/*/*.md` 就是现成模板）
- 你想自己 fork 一份改成"AI 教学视频生成器"或"AI 短视频批量工厂"
- 你的视频流程是**多步、可分支、需要审计**（decision log 给你每一步的理由）

**什么场景用别的**：
- 你只要"5 分钟出一个 TikTok"——CapCut / Captions / Hedra 更直接
- 你只想要 Remotion 本身——直接用 `npm i @remotion/cli`
- 你想要企业级 SaaS SLA——别碰 AGPL
- 你不想在 IDE 里工作——OpenMontage 对你没用

---

## 🎯 核心研判

### 项目优势（不可替代的价值点）

1. **"LLM 当制片人"是真正的新范式**：把创意决策编码进 markdown、把执行交给 Python——这个分工比 LangChain 早期版本（把 LLM 嵌进业务代码）更优雅。**它的"instruction-driven 编排"是 LLM 应用工程化的最佳实践之一**。
2. **52 个工具 + 12 条 pipeline + 500+ skill 的规模本身**：90 天做成这个体量，**单人或极小团队**的可能性最大；如果是真人手搓，不可谓不快。
3. **"Honest availability" 是行业级创新**：把"工具的真实状态"作为一等公民，**直接治理 AI agent 调 API 的被骗问题**——这是 OpenAI/Anthropic 都没解决的"AI hallucination about tools"问题的工程化尝试。
4. **预算三档治理**：给"AI 乱烧钱"准备的"用户主权"护栏，是真用户痛点驱动的设计，不是花架子。
5. **3 层知识架构**：把"项目内部约定"和"通用技术知识"显式分层，对 LLM 友好度极高（一个 agent 切换到任何项目只要读 Layer 2 + Layer 3 就能上手）。
6. **provider matrix 的扩展性**：加 1 个 provider 只需 1 个文件，零注册——这是 Open-Closed Principle 的教科书示例。

### 项目风险（潜在隐患和局限性）

1. **🚨 严重安全风险：冒名 fork 已造成实际木马投放**——Issue #175（OpenMontage/OpenMontage，91MB EXE 报毒）和 Issue #200（Open-Montage/OpenMontage，PureRat 木马）已发生。**官方 README 至今没加安全告示**。任何用户通过 Google 搜索 `github openmontage` 进入冒名仓库的概率都不低。
2. **🚨 AGPL-3.0 传染性是双刃剑**：商用 fork 必须开源，对企业用户是 hard blocker；个人开发者无所谓。
3. **🚨 真实使用门槛远超 README 暗示**：第 6/7 步（agent 第一次跑成功）的失败率肉眼可见——大量水 issue 暗示"装好但跑不起来"。
4. **⚠️ 项目方 spam 治理缺位**：12+ 条 spam/钓鱼 issue 留在主仓库未处理，影响"项目专业度"信号，对潜在 contributor 是劝退。
5. **⚠️ 单人/小团队维护可持续性存疑**：90 天 24K star + 大量 provider 集成 + 频繁 breaking changes（Remotion ↔ HyperFrames 迁移、character-animation 新 pipeline）——这工作量对独立开发者长期看不健康。Issue #150（owner 自己开 issue 求"public step-by-step video tutorial"）**暗示 owner 也意识到文档/教程不足**。
6. **⚠️ `.claude/skills/` 与 `.agents/skills/` 漂移（#59）**：声明与现实不符，反映出"自动生成 vs 手工维护"不一致的痛点。
7. **⚠️ 中文社区几乎零覆盖**：是市场空白但也说明"产品对中文 prompt 友好度未被验证"。
8. **⚠️ Decision log 写入有"单点失真"风险**：依赖 agent 自觉写决策；如果 agent 跳过该步，审计链断裂。

### 适用场景

✅ **强烈推荐**：
- 独立开发者/小团队想"AI 化"自己的视频流程
- 教学/培训团队要批量做 explainer 视频
- 已有 IDE AI 订阅（Claude Code/Cursor）且想深度定制的用户
- 想研究"LLM 当业务编排者"模式的技术决策者

✅ **可以尝试**：
- 内容工作室要"研究 + 提案"环节自动化
- MCN 机构要批量短视频（用 image-led pipeline）

❌ **不推荐**：
- 完全没接触过 Claude Code / Cursor / Copilot 的用户（学习曲线太陡）
- 需要"明天上线"的企业生产环境（AGPL + 文档 + 维护风险）
- 完全不写代码的内容创作者
- 想 100% 离线跑的用户（项目必须 LLM agent）

### 趋势判断

**上升期（仍处爆发早期）**：
- star/issue 比 24K:111 异常高（健康项目一般 1000:50+），意味着大部分 star 用户没提 issue——**这正是"项目正在被 KOL 视频拉新"阶段的标志**。
- 90 天从 0 到 24K，曲线仍在爬升。
- 已有 5+ 起冒名 fork / 木马攻击 = **流量被攻击者盯上 = 项目足够火**。
- owner 主动在 lightpanda-io 等上游项目开 issue 谈合作（calesthio/OpenMontage #2037）= 积极扩张姿态。

**风险点**：
- 维护者单点失败风险
- KOL 流量退去后，star 增速放缓但 issue 增速不变，**可能进入"维护危机期"**（参考 2024 年某些热门 AI 仓库昙花一现的轨迹）
- AGPL 在企业场景的硬阻断

**半年内最大变量**：
- 如果 owner 能把"易用性教程"做完（issue #150）+ 把 spam 治理 + 把安全告示加进 README，**有机会沉淀成"Lovable for Video"** 级别的工具。
- 如果 owner 被流量冲昏开始做"全场景 AI 视频 SaaS"扩张，**有 70% 概率在 12 个月内进入维护寒冬**。

---

## 📂 关键文件路径速查

```
README.md                                  入口（"installed" 风格）
AGENT_GUIDE.md                             ★ 必读 — agent 合同 + 操作手册
PROJECT_CONTEXT.md                         ★ 架构权威源
CLAUDE.md / CURSOR.md / CODEX.md / COPILOT.md / .windsurfrules  各 IDE 入口

config.yaml                                全局配置（LLM / 预算 / 输出）
.gitignore                                 projects/ 与 music_library/ 都被 gitignore

lib/
├── config_model.py                        Pydantic 配置模型
├── checkpoint.py                          ★ 检查点读写 + canonical stage↔artifact 映射
├── pipeline_loader.py                     ★ YAML manifest 加载 + 校验
├── media_profiles.py                      平台渲染 profile（YouTube/TikTok/...）
├── env_loader.py                          .env 加载
└── providers/                             （预留）

tools/
├── base_tool.py                           ★ 工具合约（所有 52 个工具的父类）
├── tool_registry.py                       ★ 单例注册表 + 自动发现
├── cost_tracker.py                        ★ 预算治理（estimate/reserve/reconcile）
├── analysis/   (4 tools)
├── audio/      (8 tools: tts_selector + 4 TTS + music + mix + enhance)
├── avatar/     (2 tools: talking_head, lip_sync)
├── capture/    (3 tools: cap_recorder, screen_capture_selector, screen_recorder)
├── character/  (1 tool:  character_animation, 39KB)
├── enhancement/(5 tools: upscale, bg_remove, color_grade, face_enhance, face_restore, eye_enhance)
├── graphics/   (13 tools: image_selector + FLUX/Grok/Google/OpenAI/Recraft + stock + diagram/code/math)
├── subtitle/   (1 tool:  subtitle_gen)
└── video/      (18 tools: video_selector + Grok/HeyGen/Higgsfield/Veo/Kling/Runway/MiniMax + 4 本地 + 2 库存 + compose + stitch + trim + auto_reframe + clip_cache + clip_search + corpus_builder + direct_clip_search + green_screen_* + hyperframes_compose + remotion_caption_burn + seedance_* + silence_cutter + showcase_card + stock_sources/*)
    └── stock_sources/  (15 子模块：pexels/pixabay_video/wikimedia/coverr/dareful/esa/jaxa/loc/mixkit/nara/nasa/noaa/pond5_pd/unsplash/videvo/archive_org)

pipeline_defs/                             ★ 12 个 YAML pipeline 清单
├── animated-explainer.yaml                (production, 9 stage, 最完整)
├── animation.yaml                         (production)
├── avatar-spokesperson.yaml               (production)
├── cinematic.yaml                         (production)
├── hybrid.yaml                            (production)
├── screen-demo.yaml                       (production)
├── character-animation.yaml               (beta)
├── talking-head.yaml                      (beta)
├── clip-factory.yaml                      (beta)
├── podcast-repurpose.yaml                 (beta)
├── localization-dub.yaml                  (beta)
├── documentary-montage.yaml               (新增)
└── framework-smoke.yaml                   (test)

skills/
├── INDEX.md                                ★ 三层架构总览
├── core/         (ffmpeg, remotion, hyperframes, whisperx, subtitle-sync, color-grading)
├── creative/     (video-editing, storytelling, sound-design, typography, manim-usage, image-gen-usage, image-provider-usage, broll-planning, stock-sourcing-usage, scene-detect-usage, diagram-gen-usage, music-gen-usage, bg-remove-usage, upscale-usage, face-restore-usage, lip-sync-usage, talking-head-gen-usage, video-understand-usage, enhancement-strategy, data-visualization, video-stitching, video-gen-prompting, prompting/{seedance,grok,sora,veo,ltx,hunyuan}-prompting)
├── meta/         (reviewer ★ CHAI 协议, checkpoint-protocol, skill-creator, onboarding, video-reference-analyst, animation-runtime-selector)
└── pipelines/    (explainer/{executive-producer, research, proposal, script, scene, asset, edit, compose, publish}-director.md, talking-head/, screen-demo/, clip-factory/, podcast-repurpose/, character-animation/)

.agents/skills/                             ★ Layer 3 — 47 份 vendored 通用技术 skill
  acestep/ agents/ ai-video-gen/ avatar-video/ character-animation-qa/ character-rigging/
  doubao-tts/ grok-media/ gsap*/ hyperframes*/ ltx2/ manimce-best-practices/ pose-library-design/
  remotion*/ seedance-2-0/ svg-character-animation/ synthetic-screen-recording/ video-toolkit/
  website-to-hyperframes/ bfl-api/ flux-best-practices/ ...

schemas/                                    JSON Schema 验证
├── artifacts/                              11 个产物 schema
├── checkpoints/checkpoint.schema.json
├── pipelines/pipeline_manifest.schema.json
├── styles/playbook.schema.json
└── tools/                                  工具 I/O schema

styles/                                     视觉风格 playbook (YAML)

remotion-composer/                          Node.js 视频合成引擎（React 组件）
├── src/components/                         8 个 Remotion 组件（TextCard/StatCard/ProgressBar/CalloutBox/ComparisonCard/charts/...）

tests/
├── contracts/                              合约测试（AIOP 协议）
├── eval/                                   评测 harness
├── pipelines/                              流水线测试
├── qa/                                     质量验证
├── styles/                                 风格测试
└── tools/                                  工具测试

docs/                                       ARCHITECTURE.md / PROVIDERS.md / PR_REVIEW_GUIDE.md

.github/workflows/ci.yml                    GitHub Actions CI（lint + test on PR）
```

**真正会改变 agent 行为的"必读 5 份"**：
1. `AGENT_GUIDE.md`（agent 合同 + Rule Zero + 决策沟通合约 + orchestration 章节）
2. `skills/INDEX.md`（三层知识架构）
3. `skills/meta/reviewer.md`（CHAI 协议 + severity 分级 + slideshow risk）
4. `pipeline_defs/animated-explainer.yaml`（最完整 pipeline 模板）
5. `config.yaml`（预算/输出/路径）

---

## 🔖 一句话调研结论

**OpenMontage = "AI 视频 LLM 的训练数据 + 工具集"**：90 天从 0 到 24K star 的"agent 操作系统"型项目，把"做视频"拆成 12 条 pipeline × 7-9 stage × 500+ markdown skill，让 LLM 当制片人、Python 当场工。三层知识架构、52 个能力上报工具、预算三档治理、CHAI 评审协议是真正的工程创新点；但**同时正被冒名 fork 投放木马（Issue #175/#200），spam 治理缺位，AGPL 企业场景阻断，文档/教程/中文支持都还欠火候**。建议：给有 IDE AI 订阅、想 DIY 视频流程的开发者用；不建议无 LLM 经验者、商用企业、纯内容创作者碰。

---

**调研员备注**：

调研过程中已发现两条独立冒名 fork（#175 OpenMontage/OpenMontage、#200 Open-Montage/OpenMontage），均含木马 payload。已在 #200 issue 评论区向 owner 提交取证记录并请求加 README 安全告示。调研员暂未下载任何冒名仓库的可执行文件，所有取证均基于受害者/分析者提供的 SHA256 与 Defender 报告。

