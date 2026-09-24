# 🔬 NoeFabris/opencode-antigravity-auth - 全方位深度调研

## 📌 一句话定位
`NoeFabris/opencode-antigravity-auth` 是一个 **OpenCode 插件**，让 OpenCode 通过 OAuth 接入 Google 的 Antigravity（IDE）网关，从而用你的 Google 账号白嫖 Gemini / Claude（如 gemini-3-pro、claude-opus-4-5-thinking）模型额度——核心是「请求/响应拦截 + 格式转换 + 鉴权 + 故障恢复」。

## ⭐ 项目亮点
- **蹭上 Antigravity/OpenCode 生态热点**：11.0k⭐ / 102 fork（2025-12 创建，2026-08 仍有更新），精准卡位"OpenCode 多后端统一"需求（与 `awesome-opencode` 同源热度）。
- **健壮的请求转换**：把 OpenCode 的 Claude/Gemini 原生请求改写成 Antigravity 网关格式（Gemini `contents[].parts[]`、thinking 剥离、tool 归一化 `functionDeclarations`、Schema 清洗、ID 分配、包装 `{project,model,request}`）。
- **多账号负载均衡 + 自动故障转移**：sticky 选择（同账号直到限流，保缓存）、按模型族分别计限额、429 自动切下一账号；配置存 `~/.config/opencode/antigravity-accounts.json`。
- **会话恢复（强项）**：自动修复 `tool_use` 无 `tool_result`（注入合成 `tool_result`）、thinking 顺序错误（关闭坏 turn 重开），靠 `session.error` 事件 + `client.session.messages()` 拉取重放。
- **文档极其完善**：`docs/` 下 ARCHITECTURE / ANTIGRAVITY_API_SPEC / CONFIGURATION / MODEL-VARIANTS / MULTI-ACCOUNT / TROUBLESHOOTING 一应俱全，外加 `assets/antigravity.schema.json`。

## 🏗️ 项目架构全景
### 模块结构（src/ 树）
```
index.ts                 # 导出 AntigravityCLIOAuthPlugin / GoogleOAuthPlugin / authorize* / exchange*
src/plugin.ts            # 主入口，fetch 拦截器
src/constants.ts         # 端点、Header、配置
src/antigravity/oauth.ts # OAuth token 交换
src/plugin/
  auth.ts                # token 校验与刷新
  request.ts             # 请求转换（主逻辑）
  request-helpers.ts     # schema 清洗、thinking 过滤
  thinking-recovery.ts   # turn 边界检测、崩溃恢复
  recovery.ts            # 会话恢复（tool_result_missing）
  quota.ts               # 配额检查（API 用量）
  cache.ts / cache/signature-cache.ts  # 鉴权 + 签名磁盘缓存
  config/{schema,loader}.ts            # Zod 配置 schema + 加载
  accounts.ts            # 多账号管理
  server.ts              # OAuth 回调服务器
  debug.ts               # 调试日志
```

### 运行模型
`plugin.ts` 拦截所有到 `generativelanguage.googleapis.com` 的 `fetch()` → `isGenerativeLanguageRequest()` → `prepareAntigravityRequest()`；端点按 `daily → autopush → prod` 回退；响应用 `TransformStream` 逐行 SSE 流式处理。

## 💡 应用场景与启发
- **OpenCode 用户的"额度扩展器"**：不想单独买 API key 的用户，可用 Google 账号的 Antigravity 免费/含额度模型；适合个人开发者与实验性项目。
- **「API 网关适配层」范式**：把"上游格式不兼容"用一层拦截器抹平，是 LLM 路由/代理类工具的经典解法；其 thinking 剥离 + schema allowlist 清洗策略对写任何"转发到不同模型网关"的适配器都有参考价值。
- **对自研的启发**：会话恢复的"合成 tool_result 注入"与"turn 边界检测"是对 agent 长会话脆断点的鲁棒化处理，可借鉴到 WorkBuddy 的会话/重连机制。

## 🧠 核心源码解读
### 1. 请求转换（request.ts，Claude→Gemini 格式）
| 步骤 | 动作 |
|------|------|
| 模型检测 | 从 URL 判断 Claude/Gemini |
| thinking 剥离 | 移除所有 thinking 块（Claude），避免签名损坏 |
| tool 归一化 | 转成 `functionDeclarations[]` |
| schema 清洗 | 移除 `const`/`$ref`/`$defs`/`default`/`examples` 等 |
| ID 分配 | 给 tool call 分配 ID（FIFO 匹配） |
| 包装 | `{ project, model, request: {...} }` |

### 2. thinking 注入策略（v2.0）
```text
Turn 2 Request: Plugin STRIPS all thinking blocks
Claude API:    Generates fresh thinking
```
缓存签名 thinking（`lastSignedThinkingBySessionKey`），仅在该 turn 的**首个 assistant 消息**前注入（非每条）；`thinking-recovery.ts` 判定"turn 始于真实 user 消息（非 tool_result）"。

### 3. Schema 清洗 allowlist
保留 `type/properties/required/description/enum/items`；`const: "x"` → `enum: ["x"]`；空对象 schema 补占位 `reason` 属性——直接规避 Claude 拒收不支持的 JSON Schema 字段。

### 4. 会话恢复（recovery.ts）
检测 `session.error` → `client.session.messages()` 取失败消息 → 提取 `tool_use` ID → 注入 `{ type:"tool_result", tool_use_id, content:"Operation cancelled" }` → `client.session.prompt()` 续跑（可带 `auto_resume` + `resume_text:"continue"`）。

## 🌐 全网口碑画像
- **社区信号**：11.0k⭐，文档完成度在同类"模型网关适配"项目里罕见地高（6 份 docs + schema），CI/release/issue-triage 工作流齐全，说明作者在认真维护。
- **定位共识**：被视为"让 OpenCode 用上 Antigravity 额度的关键插件"，与 `awesome-opencode` 生态强相关。
- **注意点**：强依赖 Antigravity（Google）可用性与账号策略；Google 政策/模型名（gemini-3-pro 等）变动会直接打破适配。

## ⚔️ 竞品对比
| 维度 | opencode-antigravity-auth | 直接用 Gemini CLI | Claude Code 原生 |
|------|--------------------------|------------------|-----------------|
| 后端统一 | OpenCode 多后端 + 白嫖 Antigravity | 仅 Gemini | 仅 Claude |
| 恢复能力 | 会话/思考自动修复 | 有限 | 官方 |
| 多账号 | ✅ 轮询 + 429 转移 | 单账号 | 单账号 |
| 依赖 | 需 Antigravity 账号 | Google 账号 | Anthropic 账号 |

## 🎯 核心研判
- **优势**：把"OpenCode + 免费模型额度 + 健壮性恢复"三件事一次解决，文档与工程质量都高；对用 OpenCode 又想试 Gemini-3-Pro/Claude-Opus 的用户价值直接。
- **风险**：政策/可用性依赖 Google Antigravity，随时可能因条款或接口变动失效；跨 Google 账号的合规与使用边界需用户自担。
- **趋势**：随 OpenCode 生态扩张，此类"网关适配 + 额度聚合"插件需求会持续，但本质是"站在上游 API 之上的薄适配层"，需持续跟进上游。

## 📂 关键文件路径速查
- `index.ts` — 插件导出入口
- `src/plugin.ts` — fetch 拦截主逻辑
- `src/antigravity/oauth.ts` — OAuth 交换
- `src/plugin/request.ts` / `request-helpers.ts` — 请求/响应转换与 schema 清洗
- `src/plugin/thinking-recovery.ts` / `recovery.ts` — 会话/thinking 恢复
- `docs/ARCHITECTURE.md`、`docs/ANTIGRAVITY_API_SPEC.md`、`assets/antigravity.schema.json`
- 仓库：`https://github.com/NoeFabris/opencode-antigravity-auth`
