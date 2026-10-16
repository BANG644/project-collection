# android/skills 深度调研

> 调研日期：2026-10-17 ｜ 星标：7,987 ⭐（GitHub Trending 日榜，当日 +35）｜ 语言：Kotlin / Markdown 技能包 ｜ 许可：Apache-2.0 ｜ 默认分支：main ｜ 定位：Google 官方出品的 Android 开发 Agent Skills 仓库（遵循 open-standard agent skills，SKILL.md 格式），把 developer.android.com 的官方最佳实践按需喂给 coding agent

## 一、项目亮点（差异化）

- **第一方权威背书**：仓库挂在 `android` 组织下、作者署 `Google LLC`，内容直接搬运 `developer.android.com` 的官方指南——这是 **Google 亲自下场用 SKILL.md 规范给 LLM 当"官方陪练"**，可信度远非社区拼凑的 awesome-list 可比。
- **只补 LLM 的短板，不凑数**：官方明确"只在评测显示 LLM 表现不佳的场景做 skill"，刻意跳过 Jetpack Compose 基础用法等模型已经很熟的部分——每个 skill 都有"存在理由"，不是把文档全量灌进上下文。
- **遵循开放标准、跨 harness 通用**：全部 skill 是纯 `SKILL.md` + `references/`，符合 `agentskills.io` 开放规范；同一份仓库能被 Claude Code、Codex、Gemini CLI、Cursor、Antigravity 等任意支持该标准的 agent 直接消费，不做厂商锁定。
- **配套 Android CLI 做分发**：`android skills add/update` 一条命令按 `--agent`（claude/codex…）或 `--project` 安装/升级；也支持 `/plugin install android-skills --marketplace android/skills`（Claude Code）与 `codex plugin marketplace add`（Codex），并自动探测已装 agent 目录。
- **渐进披露的结构化内容**：每个 skill 是 `SKILL.md`（何时用 + 工作流）+ `references/`（官方文档/检查清单/迁移笔记）两层，需要时再展开，避免常驻占用上下文。

## 二、核心架构（克制）

仓库是"技能市场 + plugin 清单"结构，无运行时代码，纯指令/文档资产；`plugin.json` 是当前版本的权威技能清单（v1.0.15，列出 **33 个 skill，横跨 11 个领域**）：

```
build-system/agp/agp-9-upgrade     # AGP 9 升级
camera/camerax                      # CameraX 迁移与硬件互操作
cars/android-for-cars-parked-apps   # Android for Cars 驻车应用
device-ai/{appfunctions,litert/litert-runtime,ml-kit-genai-prompt-api}
devtools/android-cli                # Android CLI 使用指南
identity/{restore-credentials,verified-email}
jetpack-compose/{adaptive, jetpack-compose-performance, migration/*, theming/styles}
media/media3-cast-integration
navigation/{navigation-3, navigation-event}
performance/r8-analyzer             # R8 规则分析
play/{engage-sdk-integration, play-billing-library-version-upgrade, play-policy-insights}
profilers/android-profiler
security/{android-intent-security, android-permissions-security}
system/{edge-to-edge, glance-canonical-layouts}
testing/testing-setup
tv/leanback-to-compose-tv-migration
wear/{wear-compose-m3, wear-widgets}
xr/display-glasses-with-jetpack-compose-glimmer
```

**分发双轨**：`.claude-plugin/plugin.json` + `.codex-plugin/plugin.json` 给 Claude Code/Codex 当 plugin market；`.agents/plugins/marketplace.json`（接口 `AGENTS.md` 规范）给 Antigravity 等 `.agents` 体系当 marketplace（`installation: AVAILABLE, authentication: ON_INSTALL`）。README 明示"当前不接受公开代码贡献"，反馈走 issue——典型的 Google 官方"只读开源 + issue 驱动"。

## 三、应用场景与启发

- **给 coding agent 配"官方领域知识"**：当任务触及 Android 的尖角（R8 keep 规则、edge-to-edge 适配 target SDK 35、Navigation 3、XML→Compose 迁移、Play Billing 升级、Perfetto trace 分析、Android XR）时，agent 自动加载对应 skill 拿到当前官方指引，而不是靠训练数据里的"半记忆"。官方配套 Android CLI 的卖点是"比标准工具集少 ~70% token、任务快 ~3×"——本质就是"用按需 skill 替代把整本文档预灌进上下文"。
- **对"s kills 作为一等分发格式"趋势的定调**：Google 在 Cloud Next 2026 推出 `google/skills`（BigQuery/GKE/Firebase/Cloud Run/ Gemini API 共 13 个），又推出 Android Skills——**平台方亲自把最佳实践做成开放标准 skill 包**，与用户 WorkBuddy 的 skill 体系（agentskills.io 同构）是同一个范式。参照价值：自建设 skill 库时，应遵循"只在模型易错处建 skill + references 渐进披露 + 跨 harness 标准格式"三原则。
- **活文档检索互补**：仓库之外还有 Android Knowledge Base，agent 可通过关键词检索 Android/Firebase/Kotlin Docs 的实时文档——与 skill 静态打包形成"动态检索 + 静态任务手册"两层 grounding。

## 四、源码深度解读（选 3 个代表性 skill）

**1. 入口骨架 `devtools/android-cli/SKILL.md`**
YAML frontmatter 给出 `name/description/license/metadata(author: Google LLC, last-updated, keywords)`；正文是"何时装 CLI + 各子命令怎么用"的指令流。值得抄的是它的 metadata schema——`last-updated` 字段让 skill 有过期可审计的元数据，比纯散文 SKILL.md 更适合规模化治理。

**2. 领域工作流 `camera/camerax/SKILL.md`**
聚焦 CameraX 的**不可变 builder 模式**这类"模型极易写错"的细节，并用 Kotlin 正反例说明"必须接收链式返回的新实例，否则 audio 等设置被静默忽略"：
```kotlin
// WRONG: withAudioEnabled() 返回新实例被忽略
val pending = recorder.prepareRecording(ctx, opts)
pending.withAudioEnabled()
// CORRECT: 链式接收
val pending = recorder.prepareRecording(ctx, opts).withAudioEnabled()
```
这正是"只在 LLM 易错处做 skill"理念的落地样本。

**3. 市场清单 `.claude-plugin/plugin.json`**
`skills` 数组逐条列相对路径（`./camera/camerax` 等 33 项），version 1.0.15、license Apache-2.0、keywords `[android, kotlin, jetpack-compose, skills]`——agent 安装器据此把目录内的 SKILL.md 注册进对应 harness，是"仓库即市场"的最小可行契约。

## 五、全网口碑

- **势头**：2026-09 末首推、约一个月即近 8k star / 523 fork；被 daily.dev、AndroidDevKit、zendot 等多家技术媒体解读为"Google 把 agent skills 当官方分发格式"的标志性动作，整体评价正面。
- **加分项**：官方身份 + Apache-2.0 宽松许可 + 纯 Markdown 易审计；配套 Android CLI 有"70% 更少 token / 3× 更快"的量化卖点（虽为官方口径，但方向可信）。
- **争议/限制**：当前"不接受公开代码贡献"，只走 issue 反馈，社区共建受限；skill 依赖 `developer.android.com` 内容时效性，需靠 `android skills update` 保持新鲜；SKILL.md 本身不含可运行测试，质量依赖 Google 自评。

## 六、竞品对比 + 核心研判

| 维度 | android/skills | Cursor 自带 Rules | 社区 awesome-android 笔记 | 通用 coding-prompt |
|------|---------------|------------------|---------------------------|-------------------|
| 权威来源 | Google 官方 | 用户自写 | 社区拼凑 | 无来源 |
| 标准格式 | agentskills.io | 厂商私有 | 散文 | 无 |
| 跨 agent | Claude/Codex/Gemini/Cursor | 仅 Cursor | 复制粘贴 | — |
| 覆盖深度 | 33 skill / 11 域，官方指引 | 视个人 | 浅 | 浅 |

**核心研判**：android/skills 不是"又一个 Android 教程仓库"，而是 **Google 把"官方知识"重新封装成 agent 可消费的开放标准资产**——它的护城河是 first-party 权威 + 标准格式 + 跨 harness 通用。对同类需求（给 agent 配领域权威知识）的启发：①优先用开放 skill 标准而非私有 prompt 片段；②只在模型易错领域建 skill，别全量灌文档；③用 `references/` 渐进披露 + `last-updated` 元数据做治理。它印证了与用户 WorkBuddy skill 体系一致的行业方向：**skill 正成为平台级的知识分发单元**。

## 七、关键文件速查

- 技能市场清单：`.claude-plugin/plugin.json`、`.codex-plugin/plugin.json`、`.agents/plugins/marketplace.json`
- 33 个 skill 目录：`build-system/ camera/ cars/ device-ai/ devtools/ identity/ jetpack-compose/ media/ navigation/ performance/ play/ profilers/ security/ system/ testing/ tv/ wear/ xr/`（均含 `SKILL.md` + `references/`）
- 官方文档：`https://developer.android.com/tools/agents/android-skills`、`https://developer.android.com/tools/agents/android-cli`
- 安装：`android skills add <name> --project=.` ｜ Claude Code `/plugin install android-skills --marketplace android/skills` ｜ Codex `codex plugin marketplace add android/skills`
- 开放规范：`https://agentskills.io/home`
