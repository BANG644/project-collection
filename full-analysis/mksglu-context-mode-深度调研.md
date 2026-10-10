# mksglu/context-mode 深度调研

> 调研日期：2026-10-11 | 星标：26,204⭐ | 语言：TypeScript | 许可：NOASSERTION（README 标注 Elastic License 2.0 / ELv2，源码可见非 OSI）| 默认分支：main | 最近提交：活跃（pushed 2026-10-10）| 趋势：GitHub Trending（当日新增）

## 一句话定位

Context Mode 是面向 AI 编码 Agent 的「上下文问题另一半」解决方案——一个 MCP 服务器 + 跨 17 个客户端平台的 hooks 层，把工具原始输出沙箱化（98% 压缩）、用 SQLite+FTS5 持久化会话记忆、并强制「用代码分析而非读原始数据」的范式。

## 项目亮点

- **四侧同时治理上下文**：① Context Saving（沙箱工具，把 315KB 原始数据压到 5.4KB）；② Session Continuity（SQLite 索引事件，compact 时不把数据倒灌回上下文，而是 BM25 检索回 relevant 片段）；③ Think in Code（强制模型写脚本 `ctx_execute` 而非读 50 个文件计数）；④ 不强制口吻（只管数据去哪，不管模型怎么说话）。
- **11 个 MCP 工具 + 6 类 hooks 跨 17 平台**：6 个沙箱工具（ctx_batch_execute / ctx_execute / ctx_execute_file / ctx_index / ctx_search / ctx_fetch_and_index）+ 5 个 meta 工具（ctx_stats / ctx_doctor / ctx_upgrade / ctx_purge / ctx_insight）；hooks 覆盖 PreToolUse / PostToolUse / UserPromptSubmit / PreCompact / SessionStart / Stop。
- **分发能力强**：Claude Code 走 plugin marketplace 全自动安装（SessionStart hook 运行时注入路由指令），其余平台（Codex / Cursor / Gemini CLI / Copilot CLI / Kirom / OpenClaw / Antigravity / Kimi 等）各有 `configs/` 与 `src/adapters/` 适配；也可纯 MCP 安装（`npx -y context-mode`）。
- **数据主权清晰**：`--continue` 不手动触发则上一会话索引立即删除；FTS5 本地库可 `ctx purge` 彻底清空。

## 核心架构

- **MCP Server + Hook 双引擎**：hooks 在工具调用前后拦截，把 Read/Bash/WebFetch 等「可能污染上下文」的调用重定向到沙箱 MCP 工具；MCP 工具执行后只回传精炼结果。
- **SQLite + FTS5 持久层**：每次文件编辑 / git 操作 / 任务 / 错误 / 用户决策都被记录为事件，compact 时不倒灌，而是建 FTS5 索引，模型用 BM25 检索相关片段。
- **跨平台 adapter 层**：`src/adapters/<platform>/`（claude-code / codex / cursor / openclaw / kimi / gemini-cli / jetbrains-copilot / copilot-cli / antigravity / omp / kiro …）各自实现 hooks 注入与配置生成；`hooks/core/` 放平台无关纯逻辑。
- **路由决策归一化**：`routePreToolUse` 返回标准化决策对象，再由各平台 adapter 翻译成对应 hook 响应格式。

## 应用场景与启发

- 「长会话 Agent 上下文膨胀」是真实痛点——30 分钟后 40% 上下文被工具原始输出吃掉，compact 后又遗忘在编辑什么文件。Context Mode 给出了工程化答案。
- **「让模型写代码分析而非读数据」范式值得借鉴**：与其把 50 个文件读进上下文计数，不如让模型写一段 `ctx_execute` 脚本只 `console.log` 结果——一个脚本替代十个工具调用、省 100 倍上下文。这是把 LLM 当「代码生成器」而非「数据处理器」的方法论。
- 对构建自有 coding-agent 工具链的团队：hooks + MCP 双通道 + 本地 FTS5 记忆是可复用的架构模板。

## 源码深度解读

**路由核心（`hooks/core/routing.mjs`）——PreToolUse 决策归一化**

```js
/**
 * Pure routing logic for PreToolUse hooks.
 * Returns NORMALIZED decision objects (NOT platform-specific format).
 * Decision types:
 * - { action: "deny", reason: string }
 * - { action: "ask" }
 * - { action: "modify", updatedInput: object }
 * - { action: "context", additionalContext: string }
 * - null (passthrough)
 */
function mcpRedirect(result, mcpToolsAvailable = true) {
  if (!mcpToolsAvailable) return null;
  if (!isMCPReady()) return null;   // MCP 未就绪时 passthrough，避免 agent 卡死
  return result;
}
```

**引导节流（`hooks/core/routing.mjs`）——跨进程去重**

```js
// Guidance throttle: show each advisory type at most once per session.
//   - In-memory Set for same-process (OpenCode ts-plugin, vitest)
//   - File-based markers with O_EXCL for cross-process atomicity
//     (Claude Code, Gemini, Cursor, VS Code Copilot)
// Session identity: 1) sessionId from caller  2) process.ppid fallback
const _guidanceShown = new Set();
```

两个设计要点：① `mcpRedirect` 在 MCP 工具不可用时不返回重定向动作，防止 agent 因「被要求用 MCP 但 MCP 没起」而卡住（#230）；② 引导提示用「内存 Set + 文件 O_EXCL 原子标记」双轨做跨进程去重，并显式处理 Windows+Git Bash 下 ppid 不可靠的退化路径（#298）——这是真实多平台踩坑后的工程化补丁。

## 全网口碑

- Hacker News #1、570+ points；README 自称被 Microsoft / Google / Meta / Amazon / NVIDIA / ByteDance / Stripe / GitHub / Red Hat 等团队使用（**自我宣称，需打折**）。
- npm 包 `context-mode`；Discord 社区活跃。争议点：ELv2 是 source-available 而非 OSI 开源，对「开源」敏感的用户需注意。

## 竞品对比 + 核心研判

- **竞品**：Claude Code 内置上下文管理、mem0-mcp / context7 等记忆类 MCP、各类「工具输出压缩」钩子脚本。
- **差异化**：唯一把「沙箱压缩 + SQLite FTS5 记忆 + 跨 17 平台 hooks + think-in-code 范式」打包成开箱即用分发的方案；路由层是平台无关纯函数，扩展新平台只需写 adapter。
- **研判**：真实解决长会话上下文膨胀痛点，分发与工程化成熟度高于同类。注意三点——① ELv2 非真开源；②「被大厂使用」为自我宣称未独立验证；③ 每个工具调用都过 hook 有可观测延迟。适合重度 coding-agent 用户，但不适合对许可证敏感的场景。

## 关键文件路径速查

- `hooks/core/routing.mjs` — PreToolUse 路由决策核心（deny/ask/modify/context 归一化）
- `hooks/` — 各平台 `pretooluse/posttooluse/sessionstart/stop` 等钩子
- `src/adapters/` — 17 平台 adapter（claude-code / codex / cursor / openclaw / kimi …）
- `configs/` — 各平台 `hooks.json` / `mcp_config.json`
- `.claude-plugin/plugin.json` · `.codex-plugin/` · `.cursor-plugin/` · `.openclaw-plugin/` — 多 harness 插件清单
- `BENCHMARK.md` · `CLAUDE.md` — 基准与项目约定
