# ChatLab/ChatLab 深度调研

> 调研日期：2026-09-30 ｜ 数据源：gh API（README / AGENTS.md / 源码 agent.ts）｜ 定位：本地优先的 AI 聊天记录分析桌面应用

## 一、项目定位（一句话）

**ChatLab** 是一个开源桌面应用（AGPL-3.0）：把你从 WhatsApp / LINE / QQ / Discord / Telegram / Instagram / iMessage / Google Chat 等导出的聊天记录，在**本机**用「SQL 引擎 + AI Agent（24+ 工具）」探索、提问、提取洞察——你的聊天数据默认不出本机。

## 二、项目定位（差异化亮点）

1. **本地优先 + 隐私**：原始聊天数据、索引、设置都留在设备，无强制云端上传；流式解析 + 多 worker，百万级消息规模也能流畅导入分析。
2. **跨平台归一化**：不同平台导出格式映射到统一数据模型（ChatLab Format），一致地分析。
3. **AI 能真正操作数据**：Agent + Function Calling（24+ 工具）可搜索、汇总、分析聊天记录，而非只做问答。
4. **工程化架构**：pnpm monorepo（Electron + Vue3 + Nuxt UI + Tailwind），核心逻辑抽到 `@openchatlab/core`、`node-runtime`、`tools` 共享包，桌面端与 CLI 服务共用——同时有桌面 GUI 与可独立运行的 CLI/API（`chatlab-cli`）。

## 三、核心架构

- `packages/core` — 平台无关的核心模型、查询、导入去重、图表、AI 静态定义。
- `packages/node-runtime` — Node.js 运行时能力：SQLite 适配、数据库迁移、AI 管理、导出、缓存、数据目录。
- `packages/tools` — AI 工具定义、工具 registry、数据访问 provider。
- `packages/parser` — 聊天导出格式解析器与格式识别；`packages/parser-native` — napi-rs Rust 原生解析内核（未构建时自动回退 TS 实现）。
- `packages/http-routes` — Electron 与 CLI Web 复用的 HTTP route。
- `apps/desktop`（Electron 主进程 / preload / 平台能力适配）、`apps/cli`（CLI + HTTP API + CLI Web 运行时 + 导入命令 + 本地服务入口）、`src/`（共享前端页面/组件/状态/服务/i18n）。

## 四、应用场景与启发

- **场景**：个人隐私地分析自己的微信/QQ/Discord 聊天（找某段对话、统计互动频率、时间规律、关系图谱），替代把记录上传给云端 AI。
- **启发**：
  - 「多端复用」的工程纪律值得抄：把业务逻辑放 `packages/node-runtime/src/services/`，严禁在路由/IPC handler 里绕过 core 直接写 SQL——避免桌面与 CLI 两套逻辑分叉。
  - 「Rust 原生解析内核 + TS 回退」是用 napi-rs 给 TS 项目做性能关键路径加速的成熟范式；对大文件导入/解析场景尤其有用。

## 五、源码深度解读（核心模块）

**1. `apps/cli/src/ai/agent.ts` 的 `runServerAgent`：Agent 编排干净样板**

```typescript
// apps/cli/src/ai/agent.ts (节选)
await initTokenizer();                                  // 压缩/agent 都依赖 tokenizer
const piModel = buildPiModel(llmConfig);
const systemPrompt = buildSystemPrompt({ t, chatType, ownerInfo, locale, skillCtx, ... });
// 上下文压缩（编辑分支跳过）
const compressionResult = await checkAndCompress(aiChatId, DEFAULT_CONTEXT_COMPRESSION_CONFIG, ...);
// 路由 LLM 判断走「计划执行」还是直接回答
const routeDecision = await decideRequestRoute(routeInput, { llmRouter: createLlmRouteDecider({ piModel, apiKey }) });
if (routeDecision.route === 'planned_execution') {
  const planner = createAnalysisPlanner({ piModel, apiKey, onPlanDelta, onThinkingDelta, ... });
  const plan = await planner(routeInput, abortSignal);
  if (plan) { effectiveSystemPrompt = `${systemPrompt}\n\n${buildPlanGuidance(plan)}`; onEvent({ type: 'plan', plan: createPlanContentBlock(plan) }); }
}
const result = await runAgentCore({ piModel, apiKey, systemPrompt: effectiveSystemPrompt,
  tools: effectiveTools, history, userMessage, maxToolRounds: DEFAULT_MAX_TOOL_ROUNDS, ... });
```

整条链路：**初始化 tokenizer → 构建 system prompt → 上下文压缩 → 路由决策 →（可选）生成计划注入 → runAgentCore 工具循环 → 流式事件回传**，是「带规划/压缩的 Agent 服务编排」的高质量参考实现。

**2. `AGENTS.md` 体现的工程纪律**：明确「禁止在路由/IPC handler 绕过 core 直接写 SQL」「优先在 `packages/node-runtime/src/services/` 实现多端复用」「测试只为防真实用户可见回归而加」——这套约束对 monorepo 多端项目尤为关键。

## 六、社区口碑

- 7.4k⭐、1.5k fork，AGPL-3.0；活跃（2026-09-28 仍有提交），支持 8 大聊天平台，文档站 `docs.chatlab.fun`（含标准化格式规范、导出指南、路线图）。
- CLI `chatlab-cli` 可独立部署为 API/Web 服务（`clb web --daemon` 守护进程 + 自动重启），社区有自托管讨论。

## 七、竞品对比 + 核心研判

| 维度 | ChatLab | 把记录上传 ChatGPT/NotebookLM | 自写脚本解析 | 各平台官方导出工具 |
|---|---|---|---|---|
| 本地优先/隐私 | ✅ 本机 | ❌ 上传云端 | ✅ | ✅ |
| 多平台归一化 | ✅ 8 平台 | ❌ | 需自写 | ❌ |
| AI 能操作数据（工具调用） | ✅ 24+ 工具 | ⚠️ 仅问答 | ❌ | ❌ |
| 桌面 + CLI/API 双形态 | ✅ | ❌ | ⚠️ | ❌ |

**研判**：对「想本地、隐私安全地分析自己聊天记录」是稀缺且成体系的解法——既有多端共享架构，又有 Rust 加速解析。风险：AGPL-3.0 对闭源 SaaS 化有传染性；多平台导出格式解析维护成本高（各 App 导出格式常变）；AI 分析质量依赖用户自有 LLM Key。整体是「隐私优先的本地 AI 数据分析」优秀范式。

## 八、关键文件路径速查

- 仓库根：`https://github.com/ChatLab/ChatLab`；文档：`https://docs.chatlab.fun`
- Agent 编排：`apps/cli/src/ai/agent.ts`（`runServerAgent`）、`apps/cli/src/ai/agent-stream-runner.ts`
- 工程规约：`AGENTS.md`、`CLAUDE.md`、`README.zh-CN.md`
- 共享包：`packages/{core,node-runtime,tools,parser,parser-native,http-routes}/`
- 应用：`apps/desktop/`（Electron）、`apps/cli/`（CLI/API/Web）；前端：`src/`
- CLI：`npm i chatlab-cli -g`，命令 `clb web/--daemon/--status`
