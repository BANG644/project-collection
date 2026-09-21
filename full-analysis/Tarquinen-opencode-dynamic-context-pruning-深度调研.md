# Tarquinen/opencode-dynamic-context-pruning 深度调研

> 调研日期：2026-09-22 ｜ 定位：OpenCode V2 的"动态上下文裁剪"插件，用模型驱动的压缩降低 token 消耗 ｜ Stars：4,244 ｜ 语言：TypeScript ｜ 许可：AGPL-3.0 ｜ 默认分支：master ｜ 最近活跃：2026-09-21

## 一、项目定位（一句话）

DCP（Dynamic Context Pruning）是 Tarquinen 为 **OpenCode V2** 写的插件：不修改会话历史本身，而是在发往 LLM 前把"已关闭/过时"的对话内容替换成高保真技术摘要，从而压缩上下文、省 token——本质是一个"比 OpenCode 原生 compaction 更聪明"的压缩工具。

## 二、项目亮点（差异化）

- **模型自主触发压缩**：暴露 `compress` 工具给模型，由它按"任务完成度"决定何时压、压哪几段，而不是到上下文上限才整段静态压缩。
- **两种压缩模式**：`range`（把连续对话段压成块摘要）与实验性 `message`（逐条独立压缩，更外科手术式）。
- **嵌套摘要保信息**：新压缩与旧压缩重叠时，旧摘要被嵌进新摘要，信息"分层保留"而非被稀释。
- **保护语义**：受保护的工具输出（subagent、skill）与受保护文件模式（`protectedFilePatterns`）在摘要中保留；可选 `protectUserMessages` 保留用户原话。
- **配套自动策略**：deduplication（重复 tool call 只留最新输出）、purgeErrors（N 轮后删出错 tool 的输入、保留错误文本）。

## 三、核心架构

```
OpenCode 会话
   └─ DCP hooks（lib/hooks.ts）拦截每次取上下文
        ├─ lib/compress/        压缩引擎
        │    ├─ range.ts         range 模式（段→摘要）
        │    ├─ message.ts       message 模式（实验）
        │    ├─ pipeline.ts      压缩流水线
        │    ├─ protected-content.ts  保护 subagent/skill/文件
        │    ├─ state.ts / range-utils.ts / search.ts
        ├─ lib/commands/        /dcp 面板与命令
        │    ├─ compression-targets.ts / sweep.ts / recompress.ts / stats.ts / decompress.ts
        ├─ lib/messages/        注入与裁剪
        │    ├─ inject/（subagent-results 等）· prune.ts · query.ts · reasoning-strip.ts · shape.ts
        └─ lib/config.ts（dcp.jsonc：global→$OPENCODE_CONFIG_DIR→project 三级覆盖）
```

- **配置 `dcp.jsonc`**：全局 `~/.config/opencode/dcp.jsonc` → 项目 `.opencode/dcp.jsonc`，项目优先；`compress.minContextLimit/maxContextLimit`（默认 50k/100k）控制压缩触发软阈值，`nudgeFrequency` 控制提示频率。
- **默认受保护工具**：`task, skill, todowrite, todoread, compress, batch, plan_enter, plan_exit, write, edit`——保证关键上下文不被误删。
- **TUI + 命令**：`/dcp` 面板看上下文/统计；`/dcp-compress [focus]` 手动触发一轮。
- **可编辑 prompt**：`experimental.customPrompts` 开启后，`system/compress-range/compress-message/context-limit-nudge` 等 prompt 可在 `dcp-prompts/` 覆盖。

## 四、应用场景与启发

- **长会话/小上下文模型救星**：用 Claude Haiku 或上下文窗口小的本地模型跑 OpenCode 时，调低 `min/maxContextLimit` 即可显著延长可工作轮次。
- **给"上下文管理"的通用启发**：DCP 的"模型自主挑压缩点 + 嵌套摘要 + 保护集"三件套，是可移植到其他 agent 框架（Claude Code / Codex）的上下文压缩范式，不只是 OpenCode 专属。
- **prompt cache 权衡教材**：它明确标注"裁剪会变消息 → 使前缀缓存失效 → 可能增加 cache miss"，是理解"压缩 vs 缓存"trade-off 的好样本。

## 五、源码深度解读（关键片段）

`compress` 工具的核心决策在 `lib/compress/range.ts`：把若干连续消息压成一段摘要并就地替换；重叠时调用 `lib/compress/range-utils.ts` 把旧摘要嵌进新摘要。受保护内容由 `lib/compress/protected-content.ts` 识别（按 `protectedTools` 与 `protectedFilePatterns`）。

`lib/messages/prune.ts` 在每次 inject 前执行去重与错误输入清理；`lib/messages/reasoning-strip.ts` 可选剥离推理 token 以进一步瘦身；`lib/hooks.ts` 是 OpenCode V2 插件入口，把上述逻辑挂到上下文获取钩子上。

## 六、全网口碑

- **正面**：OpenCode 社区高频推荐，npm 包 `@tarquinen/opencode-dcp` 持续更新；README 配置详尽、demo 直观；作者另有本地代理 [Sleev](https://sleev.ai)（面向 Claude Code/Codex/OpenCode 的上下文管理）形成生态。
- **风险/注意**：**AGPL-3.0**（强 copyleft，商用/改源码分发需注意）；部分功能标 `experimental`（message 模式、subagent 处理、customPrompts）；压缩会改变消息、与 prompt caching 存在天然张力。

## 七、竞品对比与核心研判

| 维度 | DCP | OpenCode 原生 compaction | Claude Code 自动压缩 | ccref/contextcompact |
|------|-----|--------------------------|----------------------|---------------------|
| 触发方式 | 模型自主 + 阈值提示 | 到上限整段压 | 到上限自动 | 规则/摘要 |
| 信息保真 | 嵌套摘要 + 保护集 | 一般 | 一般 | 一般 |
| 可配置 | ✅ 极细 | 中 | 低 | 中 |

**核心研判**：⭐⭐⭐⭐ — 长 OpenCode 会话的**实用必备插件**，其"模型驱动选择性压缩 + 嵌套摘要 + 保护语义"明显优于静态 compaction；许可 AGPL 是唯一的商用顾虑。若要移植思路，重点抄 `compress/range.ts` 的嵌套摘要与 `protected-content.ts` 的保护判定。注意评估自身场景的 cache 失效成本。

## 八、关键文件路径速查

- `lib/hooks.ts` — OpenCode V2 插件入口
- `lib/compress/`（`range.ts` `message.ts` `pipeline.ts` `protected-content.ts` `state.ts`）— 压缩引擎
- `lib/commands/`（`compression-targets.ts` `sweep.ts` `recompress.ts` `stats.ts`）— `/dcp` 命令
- `lib/messages/`（`prune.ts` `query.ts` `reasoning-strip.ts` `shape.ts` `inject/`）— 注入与裁剪
- `lib/config.ts` + `dcp.schema.json` — 配置 schema
- 安装：`opencode plugin add @tarquinen/opencode-dcp@latest` ｜ 关联：[Sleev](https://sleev.ai)
