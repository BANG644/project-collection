# ranxianglei/billion-context 深度调研

> 调研日期：2026-10-17 ｜ 星标：1,519 ⭐（GitHub Trending 周榜净新增，9 天 +593）｜ 语言：TypeScript ｜ 许可：主仓 NOASSERTION（非标准，"Other"），内核 `acp-kernel` 为 MIT ｜ 默认分支：master ｜ 定位：面向 coding agent 的上下文压缩代理/插件——"小窗口（100K 足矣）省 5× token、撑数月级单会话（数十亿 token）"

## 一、项目亮点（差异化）

- **模型驱动的增量分层压缩**：把历史对话压成**可逆、可检索、保留前缀缓存**的分层摘要，而不是硬截断——模型自己决定"何时压、压哪段、写成什么摘要"，压缩本身成本 ≤2%、健康会话前缀缓存命中率 95–97%（官方口径，需自测验证）。
- **三层接入形态覆盖 20+ 客户端**：`native plugin`（装进客户端内部，最原生）／`launcher`（`bili <client>` 一键起代理+客户端，零配置）／`URL 前缀代理`（把 baseURL 指向代理，最通用）；兼容 Claude Code、Codex、OpenCode(1.x/2.x)、pi、dsh、Gemini CLI、Qwen Code、Kimi、hermes、zcode、aider、goose 等。
- **MIT 许可的零主机依赖内核 `acp-kernel`**：把压缩算法与编排抽成独立 TypeScript 库（`npm: acp-kernel`），**不假设任何 agent/服务器/UI 存在**，多 thin adapter 复用同一内核；作者声明为 opencode-dynamic-context-pruning（AGPL-3.0，本仓库已有收录）的**独立重写、不共享源码**，MIT 更友好。
- **内建可观测性**：注入 `acp_status` 工具 + `/acp`、`/acp-cache` 诊断命令，给出上下文占用与各段是否仍可压缩，缓存命中率下滑时按"上游 TTL 过期 → 换模型 → bili bug → 其他"排序归因。
- **配套论文开源**：`paper/` 目录下放了一篇 MIT 许可的"模型驱动增量分层压缩"预印本（living document，可 PR 改），并宣称 4.5 个月 / 三主机 / 174,327 次模型调用 / 18.76B 累计输入 token 的纵向研究、204,800-token 模型零窗口越界。

## 二、核心架构（克制）

`bili` 代理夹在"任意 agent"与"真实模型 API"之间，重写 Anthropic/OpenAI 流并跑 acp-kernel 压缩：

```
Agent (Claude Code / Codex / Cursor / aider ...)
   │  把 agent 的 base URL 指向代理（或装 native plugin）
   ▼
┌──────────────────────┐
│  billion-context 代理 │  1. 解析请求(Anthropic/OpenAI 形状)
│  (bili / bili-proxy) │  2. 跑 acp-kernel 压缩
│                      │  3. 注入 compress 工具 + 压缩哲学 prompt
│                      │  4. 转发真实模型 API
└──────────────────────┘  5. 重写流式响应
   │
   ▼  真实模型 API（Anthropic / OpenAI / 兼容）
```

**注入的 4 个上下文管理工具**（模型随上下文增长自己调用，代理端执行 `compress` 以保证折叠段在 history 里保持摘要态直到恢复）：
- `compress`：把一段消息折叠成详细摘要；`decompress`：需要时还原某段；`search_context`：在压缩摘要+可见消息里关键词检索；`acp_status`：上下文占用概览。

**协作插件协议（PLUGIN.md, v2）** 把"工具注册/会话身份/压缩引擎"拆给插件（inside）与代理（outside）：插件只当薄管道，schema 与压缩哲学 prompt 始终由运行中的代理下发（single source of truth），代理与插件永不漂移；每轮模型请求带 `x-bili-plugin*` 头声明会话身份与上下文窗口。

## 三、应用场景与启发

- **长会话成本敏感场景**：同一项目连续开发数天/数周、按 token 计费的接口、长项目追踪/日志分析/客服机器人——官方 README 与社区评测都指向"把账单砍一截"的诉求，一周涨 337 星说明长上下文费用痛点真实存在。
- **给"agent 上下文管理"的范式启发（与 mksglu/context-mode 同赛道）**：billion-context 走"代理层模型驱动压缩"，context-mode 走"MCP+hooks 沙箱输出+会话记忆"，xerj 走"语义检索替代读文件"——三者共同验证了"**靠架构而非更大窗口来约束 agent 上下文**"是 2026 年的明确趋势。对自建设 agent 工作流的启发：可优先考虑在代理/插件层做可逆压缩 + 检索，而非无脑堆上下文。
- **可借鉴的工程件**：`renderTags` 渲染策略（all/text-only/none）处理"标签不能污染 tool-call JSON"的细节；CCR（content-cached retrieval）做无损 tool-result 卸载——这些是该领域值得直接参考的实现要点。

## 四、源码深度解读（选 3 个核心模块）

**1. 内核引擎 `kernel/`（acp-kernel, MIT）**
状态显式进出、内核不调模型：`processTurn({messages, state, config, tokenCount})` 跑固定节点管线（reconcile-live-ids → assign-refs → sync-blocks → prune → ccr-store → absorb-hide → crush → absorb-prompt → filter → hide-compress-calls → recommend → nudge-inject → emergency-truncate → render-refs）；模型产出摘要后 `applyCompression({ranges, summary})` 落块，`decompress`/`search`/`status` 做回溯与检索。设计信条："模型写摘要，库只负责编排一切围绕它的事"。

**2. 协作插件代理 `src/plugin.ts`（协议 v2）**
实现 PLUGIN.md 的"薄管道"：启动时 `GET /__bili/plugin/manifest` 拉一次工具清单（按 anthropic/openai/responses 三套线格式），向 agent 原生注册；`POST /__bili/plugin/tool` 把工具执行转给代理、把结果当原生 tool result 返回；schema/prompt 永远来自代理，保证不漂移。被 `tests/plugin-protocol.test.ts` 覆盖。

**3. 压缩元数据防泄漏 `src/server.ts` / `src/chain-checkpoint.ts`**
反面教材价值：issue #1634 披露压缩元数据（chain tag、summary header）被以 `role:"user"` 文本注入出向请求，长会话会被"模型复述元数据"卡死。维护者已确认源码中存在 4 种泄漏形态、输出清洗器一个都没识别，正在修复——提示同类项目：**内部簿记绝不能用 user 角色承载，应走 header/线外元数据或模型被指示忽略的专用载体**。

## 五、全网口碑

- **势头**：Trendshift/掘金/Refft 等多渠道报道，9 天 +593 星、周榜净新增，定位精准踩中"长上下文贵"痛点；`paper/` 与"4.5 个月纵向研究"增强技术可信度。
- **加分项**：MIT 内核、零主机依赖、20+ 客户端覆盖、可观测诊断命令齐全；zendot 评价"可复现、不留手把手示例就谨慎"属客观。
- **争议/风险**：①主仓许可为 NOASSERTION（"Other"），若要求标准开源许可需谨慎评估；②部分客户端（jcode/copilot/amp/crush/zed/aider 等）走 **cert-MITM/URL 重写** 接入——有潜在安全/隐私权衡，企业环境需审；③**项目年轻且高速动荡**：306 个 open issue、大量 devlog、已知元数据泄漏 bug（#1634），"压缩力度调太高会摘要掉细节"需先低参数试跑；④所有量化数字（5×/95–97%/18.76B token）均为官方自报，应结合自身负载验证。

## 六、竞品对比 + 核心研判

| 维度 | billion-context | mksglu/context-mode | opencode-dynamic-context-pruning | 厂商内置 summarizer |
|------|-----------------|---------------------|----------------------------------|--------------------|
| 接入层 | 代理/插件（跨 20+ 客户端） | MCP+hooks（17 平台） | OpenCode 插件 | 绑定单 harness |
| 压缩主体 | 模型驱动分层摘要 | 输出沙箱+会话记忆 | 模型自主触发压缩 | 厂商硬规则 |
| 许可 | 主仓非标准 / 内核 MIT | ELv2 | AGPL-3.0 | — |
| 可逆/检索 | 是（decompress/search） | 记忆持久化 | 嵌套摘要保护集 | 通常不可检索 |
| 成熟度 | 年轻、bug 多 | 较新 | 较新 | 高 |

**核心研判**：billion-context 的差异化在"**跨客户端代理层 + 模型驱动可逆压缩 + MIT 内核可复用**"——它不是重造某个 harness 的 summarizer，而是把"长会话上下文管理"做成独立中间件。但当前最大短板是**年轻 + 非标准许可 + 部分客户端靠 cert-MITM**，且核心数字未独立验证。**给同类需求（给 agent 配上下文约束）的启发**：若想要"即插即用跨客户端"，它是目前覆盖最广的选型，但生产前务必在小会话低参数试跑、审 cert-MITM 客户端、并核对主仓许可；若只在单一 harness 内且要更稳，context-mode / opencode-dynamic-context-pruning 可能更省心。把它当作"上下文压缩中间件的激进参考实现"而非开箱稳品更合适。

## 七、关键文件速查

- 内核（MIT）：`kernel/`（README.md / DESIGN.md / PROVENANCE.md / bench/search）
- 插件协议：`PLUGIN.md`、实现 `src/plugin.ts`、`tests/plugin-protocol.test.ts`
- 代理入口与防泄漏：`src/server.ts`（stampOutbound #5048）、`src/chain-checkpoint.ts`、`src/codex-compact.ts`
- 客户端接入清单：`CLIENTS.md`（含 native/launcher/URL 三种姿势逐客户端说明）、`.claude-plugin/`
- 论文与诊断：`paper/`、README 的 Cache health / `/acp` `/acp-cache`
- 安装：`npm install -g billion-context --prefix=~/.local` → `bili plugin install <client>` 或 `bili <client>`
