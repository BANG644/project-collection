# 🔬 nexu-io/open-design - 全方位深度调研

> 调研时间：2026-07-03 | Star: 74,675 | Fork: 8,520 | 创建: 2026-04-28 | 许可: Apache-2.0
> 主语言: TypeScript (59.3MB) | 项目地址: https://github.com/nexu-io/open-design

---

## 📌 一句话定位

**Open Design 是一个"AI 设计工作流编排器"**——它不是又一个 AI 画图工具，而是通过本地守护进程将你电脑上已有的 25 种 Coding Agent CLI（Claude Code、Codex、Cursor、Qwen……）接入一套结构化设计 Skill + Design System 体系，把"随便画画"升级为"有品牌约束、有评审门禁、可 Git 管理"的工程化设计流程。

---

## ⭐ 项目亮点（6 条差异化价值）

### 1. 飞轮式增长：2 个月从 0 到 74,675 Star
项目于 2026 年 4 月 28 日创建，在 **不到 3 个月** 内飙升至 74,675 Star。这是 2026 年开发者工具领域增长最快的开源项目之一。起因很简单：Anthropic 在 4 月发布了 Claude Design（订阅 $20/月，Pro 额度 25 分钟耗尽），社区情绪反弹直接催生了这个平替项目。

### 2. "AI 设计"的范式革新：不是设计工具，是设计工作流
Open Design 没有发明新的模型，而是做了一件更聪明的事——它定义了一套 **Skill + Design System + Critique** 的三层协议，把 AI 设计从"随意发一段 prompt"推进到了"有品牌约束、有质量门禁、可版本管理"的结构化工作流。这是它与 v0.dev 或 Claude Design 最本质的区别。

### 3. 25 种 Coding Agent 适配器 + BYOK：不锁定任何模型
支持 Claude Code、Codex CLI、Cursor Agent、Gemini CLI、OpenCode、Qwen、Copilot CLI、Hermes、Kimi、DeepSeek、甚至 OpenClaw、Antigravity 等 25 种 Agent CLI。如果你什么都没装，还可以用 BYOK（自带密钥）模式直接接入 Anthropic/OpenAI/Azure/Google/Ollama/LM Studio 的 API。**你的 CLI 就是设计引擎。**

### 4. 150+ 品牌级 DESIGN.md 系统 + 261 个即装即用插件
每套设计系统是一个 9 维度的 `DESIGN.md`（色彩/字体/间距/布局/组件/动效/语气/品牌/反模式），涵盖 Stripe、Linear、Vercel、Notion、Tesla、Apple、Figma 等品牌的视觉规范。切换设计系统 = 整个视觉语言切换。261 个官方插件覆盖场景编排、图片模板、视频模板、设计系统、UI 原子组件等。

### 5. 五维自评 Critique 系统：AI 设计的"质量门禁"
这是最容易被忽视但最具原创性的设计。Open Design 内置了一套 **基于 SSE 流式评分的五维 Critique 系统**——哲学(Philosophy)、层级(Hierarchy)、细节(Execution)、功能(Specificity)、克制(Restraint)。每次生成后 Agent 自行评分，某维度低于阈值则进入修复循环。代码见 `apps/daemon/src/critique/orchestrator.ts`。

### 6. 本地优先 + 纯文件存储：设计产物可 Git 管理
所有设计产物存储在 `./.od/artifacts/` 目录下，使用纯文件 + JSONL 日志格式，**天然适配 Git 工作流**。设计变更可以走 PR 评审，可以 diff，可以回滚。这和 Figma/Claude Design 的"黑盒保存"形成根本性对立。

---

## 🏗️ 项目架构全景

### 目录结构骨架

```
open-design/
├── apps/
│   ├── daemon/              ← 核心：本地守护进程 (Express + SQLite + agent spawner)
│   │   └── src/
│   │       ├── runtimes/     ← 25 种 Agent CLI 适配器定义
│   │       ├── critique/     ← 五维自评系统（最独特的模块）
│   │       ├── plugins/      ← 插件引擎（安装/应用/发布/搜索）
│   │       ├── brands/       ← DESIGN.md 解析引擎
│   │       ├── design-systems/ ← 设计系统导入/服务
│   │       ├── integrations/ ← 模型提供商集成 (AMR/OpenAI/Azure/Google/本地)
│   │       ├── media/        ← 图片/视频生成管道
│   │       ├── mcp*.ts       ← MCP 协议支持
│   │       └── http/         ← API 路由层
│   └── web/                  ← Next.js 16 前端 (App Router)
├── design-templates/         ← 30+ 设计技能模板 (SKILL.md + assets/)
├── design-systems/           ← 150+ 品牌设计系统
├── plugins/                  ← 261 个插件（官方 + 社区）
│   ├── _official/            ← 官方插件
│   └── community/            ← 社区插件
├── scripts/                  ← 构建/发布/同步脚本
├── deploy/                   ← Docker 部署配置
├── docs/                     ← 架构/协议/适配器文档
├── AGENTS.md                 ← Agent 协作协议（供 AI 贡献者阅读）
└── CONTEXT.md                ← 项目上下文契约
```

### 技术栈 & 依赖图谱

| 层 | 技术选型 |
|---|---|
| 前端 | Next.js 16 (App Router) + React 18 + TypeScript |
| 守护进程 | Node 24 + Express 5.2 + `better-sqlite3` + SSE 流式 |
| 插件运行时 | `@open-design/plugin-runtime` (workspace) |
| 侧车协议 | `@open-design/sidecar` + `@open-design/sidecar-proto` |
| Agent 运行时 | `child_process.spawn` + 25 个适配器定义 |
| 桌面壳 | Electron + 沙箱 IPC (STATUS/EVAL/SCREENSHOT/CONSOLE/CLICK/SHUTDOWN) |
| 遥测 | OpenTelemetry + PostHog + Prometheus 指标 |
| 导出 | PDF (puppeteer) · PPTX (pptxgenjs) · HTML · ZIP · MP4 (HyperFrames) |
| 包管理 | pnpm workspace + TypeScript 5.9 |
| 质量管理 | `pnpm guard` (style/product-neutrality/import-isolation/cross-app-imports 检查) |

### 核心架构图

```
┌────────────────── Browser (Next.js 16) / Electron ──────────────────┐
│  chat · file workspace · iframe preview · settings · import · MCP   │
└──────────────┬──────────────────────────────────────┬──────────────┘
               │ /api/*                               │ /api/proxy/{provider}/stream (SSE)
               ▼                                      ▼
   ┌──────────────────────────────────────────┐   BYOK → 任意 OpenAI 兼容端点
   │      Local Daemon (Express + SQLite)      │   (SSRF 阻止)
   │                                            │
   │  /api/skills    /api/plugins              │
   │  /api/design-systems  /api/chat (SSE)     │
   │  /api/projects/:id/files/*                │
   │  /api/artifacts/{save,lint}               │
   │  /api/import/claude-design (ZIP 导入)     │
   │  /api/proxy/{anthropic,openai,...}/stream  │
   │  MCP stdio server                          │
   └──────────┬─────────────────────────────────┘
              │ spawn(cli, args, { cwd: .od/projects/<id> })
              ▼
   ┌─────────────────────────────────────────────────────────────┐
   │  claude · codex · cursor-agent · gemini · opencode · qwen  │
   │  copilot · hermes · kimi · deepseek · antigravity · ...    │
   │  读取 SKILL.md + DESIGN.md，将产物写入磁盘                  │
   └─────────────────────────────────────────────────────────────┘
```

**数据存储（单一入口点 + `.od/` 目录）：**

```
.od/
├── app.sqlite          ← 项目/会话/消息/标签 (better-sqlite3)
├── artifacts/          ← 一次性保存的设计产物
└── projects/<id>/      ← 每个项目的 Agent 工作目录
```

**设计哲学：** 只有守护进程是特权进程，Agent CLI 在 `cwd` 约束的项目目录内运行，不接触系统敏感目录。所有外部 API 调用走 `/api/proxy/*` 通道，统一做 SSRF 防护。

---

## 💡 应用场景与启发（重点章节）

### 典型使用场景

**场景 1：快速原型验证（最适合的场景）**
产品经理或创始人输入"帮我做一个 SaaS Landing Page"，Open Design 会弹出交互表单（目标受众/调性/品牌），选定方向后生成可运行的 HTML。适合内部工具、MVP、活动页。

**场景 2：品牌视觉系统落地**
如果你有一份设计规范，按 9 维格式写一个 `DESIGN.md`，从此所有 AI 生成的内容都遵循你的品牌约束。这对创业团队和独立开发者来说，是"零成本品牌一致性"。

**场景 3：PPT/演示文稿批量生产**
从 Magazine-Style PPT（guizang-ppt）到产品演示 Deck（replit-deck），团队周报、融资路演、OKR 展示——输入一两句话，30 秒生成一份可导出 PPTX 的演示文稿。

**场景 4：Claude Design 用户的迁移路径**
如果你之前用过 Claude Design 但觉得 $20/月不值、额度不够用、或者对数据上云有顾虑，Open Design 的 Claude Design ZIP 导入功能可以无缝迁移。`POST /api/import/claude-design` 后你把设计方案提回来继续编辑。

**场景 5：CI/CD 中的自动化设计**
通过 `od` CLI 和 `--json` 输出格式，可将设计生成嵌入 CI 流水线。例如：每次 git push 后自动刷新演示环境的设计稿。

### 可借鉴的解决方案模式

1. **"Design System as a Contract"——用文件代替配置中心**
   Open Design 最大的架构智慧是：**用 `DESIGN.md` 文件作为品牌契约**。不是把设计令牌放在 JSON/YAML 配置文件里，而是用一个可读可写、天然支持 Git diffs 的 Markdown 文件。这意味着：
   - 设计师可以直接在 GitHub 上提交 PR 修改品牌规范
   - 一篇文章就能承载"颜色/字体/间距/组件/动效/语气/反模式"9 个维度
   - 评审者可以逐行 review 设计规范变更
   
   这个模式值得任何需要"人机共同维护"的设计规范系统借鉴。

2. **"Skill 即文件夹"——插件模式的一种极简实践**
   每个 Skill 只是一个文件夹（`SKILL.md` + `assets/` + `references/`），丢进去就有了新能力。这种极简主义设计降低了贡献门槛——你不需要学插件 SDK，会写 Markdown 就能写 Skill。
   
   对比 WordPress 的插件 API 和 Figma 的插件 SDK，Open Design 的"文件夹即插件"在轻量场景下更具可操作性。

3. **"问清楚再动手"的交互设计**
   `<question-form>` 机制是 README 没有强调但实际最有价值的设计之一。每次新设计任务，AI 的第一反应不是写代码，而是弹出一个交互表单问清楚。这种"初级设计师模式"来自 huashu-design 的理念，是对抗"AI 生成幻觉"的第一道防线。

### 同类需求的可参考思路

- **如果你在做 AI Coding Agent 工具**：Open Design 的 agent runtime 架构（PATH 扫描 → 适配器注册 → 能力探测 → 标准化 spawn）是一个教科书级的实现。每个 Agent 定义包括 `versionArgs`、`authProbe`、`helpArgs`、`capabilityFlags`（版本探测 → 认证状态 → 能力探测 → 构建命令行），这套模式可以直接复用到其他需要"统一调度多种 CLI"的场景。

- **如果你在做设计协作工具**：Critique 系统的五维评分 + 流式 SSE 通知是一个值得参考的模式。它不是"等生成完了再评分"，而是**边生成边评分边修复**，形成一个实时闭环。

- **如果你在做 MCP 服务**：Open Design 同时提供了 MCP Server（`apps/daemon/src/mcp-live-artifacts-server.ts`）和 MCP Client 集成。同一套 API 既供 Web 前端使用又通过 MCP 开放给外部 Agent 调用，这种"同层双协议"的设计值得借鉴。

### 可复用片段

**Agent 能力探测模式**（`apps/daemon/src/runtimes/defs/claude.ts`）：用一个 `capabilityFlags` Map 做渐进式能力探测，`--help` 输出中匹配到标志字符串就标记为能力存在。这种做法比假设"某个版本一定支持某功能"要稳妥得多，也避免了硬编码版本号导致的兼容性问题。代码 15 行就实现了：

```typescript
const args = ['-p', '--input-format', 'stream-json', '--output-format', 'stream-json', '--verbose'];
if (caps.partialMessages) { args.push('--include-partial-messages'); }
if (options.model && options.model !== 'default') { args.push('--model', options.model); }
// 能力探测 → 渐进式功能启用
if (dirs.length > 0 && caps.addDir !== false) { args.push('--add-dir', ...dirs); }
if (caps.resume) { args.push('--resume', runtimeContext.sessionId); }
```

---

## 🧠 核心源码解读（克制代码量）

### 模块 1：Agent Runtime 注册表（`apps/daemon/src/runtimes/registry.ts`）—— 25 种 CLI 的统一调度

这是整个项目的"调度中心"。它将 25 种不同的 Coding Agent CLI 抽象为统一的 `RuntimeAgentDef` 接口：

```typescript
const BASE_AGENT_DEFS: RuntimeAgentDef[] = [
  amrAgentDef, claudeAgentDef, codexAgentDef, devinAgentDef,
  opencodeAgentDef, byokOpenCodeAgentDef, hermesAgentDef,
  traeCliAgentDef, grokBuildAgentDef, kimiAgentDef, cursorAgentDef,
  qwenAgentDef, qoderAgentDef, copilotAgentDef, ampAgentDef,
  piAgentDef, kiroAgentDef, kiloAgentDef, vibeAgentDef,
  deepseekAgentDef, aiderAgentDef, antigravityAgentDef,
  reasonixAgentDef, codebuddyAgentDef, mimoAgentDef,
];

// + 本地用户自定义配置，动态合并
export const AGENT_DEFS: RuntimeAgentDef[] = [
  ...BASE_AGENT_DEFS,
  ...readLocalAgentProfileDefs(BASE_AGENT_DEFS),
];
```

**设计解读**: 通过 `readLocalAgentProfileDefs()` 支持用户本地配置覆盖，不修改源码也能增加自定义 Agent。这是"核心内置 + 用户扩展"的典型组合模式。

### 模块 2：Critique 五维自评系统（`apps/daemon/src/critique/orchestrator.ts`）—— AI 设计的质量门禁

Critique 系统是 README 一笔带过但源码层面极具原创性的模块。它通过 SSE 流式协议与 Agent 实时交互：

```typescript
export interface OrchestratorParams {
  runId: string;
  projectId: string;
  artifactId: string;
  adapter: string;       // 哪个 Agent 在执行
  cfg: CritiqueConfig;   // 阈值配置
  db: Database.Database;
  bus: CritiqueSseBus;   // SSE 事件总线
}

// 核心：流式解析 <ROUND_END> / <SHIP> 标记，实时计算复合评分
const COMPOSITE_TOLERANCE = 0.01;  // FP 精度控制
// 评分决策：低于阈值 = 进入修复循环
export { computeComposite, decideRound, selectFallbackRound };
```

**设计解读**: 这不是事后评分，而是**流式评分**。Agent 执行过程中实时发出 `<ROUND_END>` 标记，守护进程用 SSE 事件推送到前端。低于阈值就进入下一轮修复，最多 3 轮。这是将 "CI/CD 门禁" 理念引入 AI 设计生成的关键创新。

### 模块 3：Claude Agent 适配器（`apps/daemon/src/runtimes/defs/claude.ts`）—— 代理适配的工程化范例

这是 Claude Code 专属适配器，体现了 Open Design 对"兼容性"的极致追求：

```typescript
export const claudeAgentDef = {
  id: 'claude',
  name: 'Claude Code',
  bin: 'claude',
  // 降级：如果 claude 不在 PATH 上，尝试 openclaude
  fallbackBins: ['openclaude'],
  versionArgs: ['--version'],
  // 认证探测
  authProbe: { args: ['auth', 'status'], timeoutMs: 5000 },
  // 能力标记——通过 --help 输出匹配决定是否启用某功能
  capabilityFlags: {
    '--include-partial-messages': 'partialMessages',
    '--add-dir': 'addDir',
  },
  // 模型列表：fallback + 动态获取
  fallbackModels: CLAUDE_FALLBACK_MODELS,
  fetchModels: async (_resolvedBin, env) => loadMmdRouteModels(env, CLAUDE_FALLBACK_MODELS),
  // prompt 通过 stdin 传递，避免命令行长度限制
  buildArgs: (_prompt, _imagePaths, extraAllowedDirs = [], options = {}, runtimeContext = {}) => {
    const args = ['-p', '--input-format', 'stream-json', '--output-format', 'stream-json'];
    if (caps.partialMessages) args.push('--include-partial-messages');
    // ...
  },
};
```

**设计解读**: 这段代码暴露了 Open Design 架构的关键思考：
1. **`fallbackBins`**：支持开源复刻（openclaude），用户无需写包装脚本
2. **`capabilityFlags`**：渐进式能力探测——不是假设"你支持什么"，而是先问再决定
3. **stdin 传 prompt**：避开 Linux `MAX_ARG_STRLEN`（128KB）和 Windows `CreateProcess`（32KB）的命令行长度限制
4. **流式 JSON**：`--input-format stream-json` 让守护进程可以在一个会话中持续发送多条消息

### 隐藏功能 & 未文档化特性

1. **"Agent 能力探测渐进式升级"**：`capabilityFlags` 机制意味着 Open Design 会随 Agent 版本自动解锁更多能力，而不是写死在版本号上。
2. **社区 Pet 同步**：`apps/daemon/src/community-pets-sync.ts` 和 `scripts/sync-community-pets.ts` 表明项目有自动化的社区插件同步流水线。
3. **Critique 合规测试**：`.github/workflows/critique-conformance.yml` 表明 Critique 系统有自动化的合规回归测试套件。
4. **i18n 覆盖率报表**：`i18n:coverage` 脚本说明项目有自动化多语言覆盖度监控。
5. **"bake-plugin-previews" CI**：自动渲染插件预览图，类似 Vercel 的部署预览。

---

## 📐 架构决策与设计哲学

### 关键架构决策

1. **"守护进程是最小特权进程"** —— 所有 Agent CLI 在 `cwd` 约束的项目目录内运行，守护进程统一管理文件系统访问和网络代理。Agent 不直接接触系统敏感目录。

2. **"文件即 API"** —— `SKILL.md` 和 `DESIGN.md` 用 Markdown 文件作为协议载体，不引入额外的 schema 语言或 DSL。降低贡献门槛的同时，也让文件天然支持 Git diff。

3. **"BYOK 优先，不锁模型"** —— 所有模型通过 `/api/proxy/` 统一代理，即使付费 AMR 服务也是可选而非强制。用户可以把 API Key 放在本地，选择任意模型。

4. **"SSE 流式是唯一通信协议"** —— 前端到守护进程、守护进程到 Agent CLI、Critique 系统的评分数据，全部通过 SSE 流式传输。没有 WebSocket，没有轮询。这简化了架构但限制了双向通信的能力（SSE 是单向的）。

### 设计红线（Out-of-Scope）

从 Issue 和 PR 拒绝记录中可以推断出以下设计红线：

- **不训练自己的模型**：Open Design 不做模型训练，所有能力来自底层 Agent CLI
- **不自建云端服务（AMR 除外）**：核心功能全部本地运行，AMR 是可选的付费增值
- **不替代 Figma**：定位不是像素级编辑器，而是"Agent 时代的 Figma 替代"——输出代码而非画布
- **不做端到端自动化**：Critique 系统的存在=承认 AI 生成需要人工把关

### 版本演进中的哲学转变

项目从 0.8.0 的插件市场基础设施，到 0.9.0 的 AMR 模型路由，再到 0.10.0 的"全窗口 Agentic 设计工作室"，演进路线显示：

- **0.x 阶段**：围绕"如何让 Agent 统一接入"（运行时层）
- **1.0（规划中）**：将转向"如何让社区生态繁荣"（插件 SDK + 发布平台）
- 核心转变：**从"API 工具"到"生态平台"**

---

## 🌐 全网口碑画像

### 好评共识

| 来源 | 评价要点 |
|------|----------|
| LinkedIn (Julian Goldie) | "Flexibility is the main draw — you can customise virtually anything." 推荐大规模使用 |
| 博客园 (itech) | "最聪明的设计之一是交互式问卷，30 秒的表单填写省掉 30 分钟的来回修改" |
| 技术栈 (jishuzhan.net) | "不是一个简单的 AI 画界面工具......把 AI UI 生成从随机 Prompt 推进到结构化工作流" |
| bestaiagentcommunity.com | "Open Design wins for open-source teams, custom design systems, and privacy-first builds" |
| 头条 (toutiao.com) | "Claude Design 的订阅费是真不便宜，开源方案找到了" |
| zhuanlan.zhihu.com | 深度调研文获得大量点赞，社区普遍认可"本地优先"的价值主张 |

### 差评共识 & 踩坑高发区

| 来源/Issue | 吐槽要点 |
|------------|----------|
| #5036（严重 bug，未关闭） | **非 Anthropic 模型在 claude-stream-json 下丢失 tool_use** —— glm-5.2 / MiMo 模型在生成阶段挂了，社区贡献者 bruce-hmz 提供了详细的 event log 分析，维护者确认这是"两个 guard gap"问题 |
| #5035（未关闭） | **中国境内 AMR 登录 409 Conflict** —— Docker 部署在无外网的服务器上，AMR 登录流程卡住。已有人提交 PR #5046 修复 |
| #5120（最新 issue） | **macOS 上 `od` 命令被系统 /usr/bin/od 占用** —— 这是一个"取名诅咒"：Linux/macOS 系统自带的 `od`（octal dump）命令与 Open Design 的 `od` CLI 冲突 |
| 知乎/CSDN 入门指南 | **依赖链条长**：需要 Node 24 + pnpm 10.33.x + 一个 Agent CLI，对新手而言门槛较高 |
| LinkedIn 评测 | "Output speed is slower" (比 Claude Design 慢) 和 "Polish is variable" |

### 争议焦点

1. **"免费 vs 付费"之争**：有人坚持免费开源的价值，也有人认为 Claude Design 的 $20/月如果节省 2 小时/周就物超所值。核心分歧在对"时间成本"的定价。
2. **"本地 vs 云端"之争**：本地优先意味着用户要自己维护计算资源。Docker 部署在无外网环境（如中国境内服务器）成了高频问题。
3. **生态包容性代价**：支持 25 种 CLI 带来了极高的灵活性，但也意味着要维护 25 种传输协议（claude-stream-json / json-event-stream / acp-json-rpc / copilot-stream-json / pi-rpc / plain）。Issue #5036 表明某些非主流模型可能被遗漏在适配之外。

### 典型实战案例

**中文社区案例**：知乎上有开发者用 Open Design + Qwen + Ollama 在本地完全离线运行，成功生成了产品 Landing Page。验证了"无外网环境下也能用"的使用场景。但该案例也暴露了本地小模型（Qwen 7B）输出质量明显不如 Claude Opus 的问题。

**英文社区案例**：Julian Goldie（LinkedIn 评测者）在生产中同时使用 Open Design 和 Claude Design 处理不同任务——批量设计和设计系统用 Open Design，一次性抛光用 Claude Design。他认为两者是互补而非竞争关系。

### 维护者响应风格

从 Issue #5035、#5036 的交互来看：
- **响应速度极快**：贡献者/用户的问题通常在数小时内收到回复
- **技术深度高**：维护者 `lefarcen` 能识别出 "post-execution reporting bug vs missing-tool-use bug" 的微妙区别，定位到具体代码行
- **多语言回复**：Issue #5035 中同时用中文和英文回复（用户是中文用户）
- **Contributor Card 机器人**：`open-design-bot` 会自动为新贡献者生成排名卡片，社区建设意识强

但 Issue #5036 作为严重 bug（模型挂起/无声失败）已开放超过 24 小时仍未修复，说明 **项目处于高频迭代期，稳定性还未到 v1.0 级别**。

---

## ⚔️ 竞品对比

### 对比矩阵

| 维度 | Open Design | Claude Design | v0.dev | Lovable |
|------|-------------|---------------|--------|---------|
| **核心定位** | AI 设计工作流编排器（开源） | Anthropic 闭源设计助手 | 前端代码生成器 | 全栈应用生成器 |
| **是否开源** | ✅ Apache-2.0 | ❌ 闭源 | ❌ 闭源 | ❌ 闭源 |
| **部署方式** | 本地 / Docker / Vercel | 仅云端 | 仅云端 | 仅云端 |
| **Agent 选择** | 25 种 CLI + BYOK | 仅 Claude | 仅 v0 自己的模型 | 仅 Lovable 后端 |
| **设计系统** | 150+ DESIGN.md 可自定义 | 固定系统 | 无设计系统概念 | 无设计系统概念 |
| **输出类型** | HTML/PDF/PPTX/MP4/ZIP | 原型+代码 | React/Next.js 代码 | 全栈 Web 应用 |
| **插件生态** | 261 官方 + 社区 | 仅官方 | 无 | 无 |
| **质量门禁** | ✅ 五维 Critique 自评 | ❌ | ❌ | ❌ |
| **Git 原生** | ✅ 纯文件存储 | ❌ 云端存储 | ❌ | ❌ |
| **成本** | 免费 + 自付模型费用 | $20-100+/月 | 免费+付费额度 | $20+/月 |
| **数据隐私** | 本地，用户完全掌控 | 云端 | 云端 | 云端 |
| **知识门槛** | 中高（需要懂 CLI） | 低 | 低 | 低 |
| **生成速度** | 较慢（需 Agent 启动+推理） | 快（90s） | 快 | 快 |
| **输出抛光** | 参差不齐，依赖底层模型 | 较高 | 中等 | 中等 |

### 选择建议

**选 Open Design 当且仅当：**
- 你已经在使用（或愿意使用）某个 Coding Agent CLI
- 你需要严格的设计规范一致性（品牌规范、设计系统）
- 你必须本地运行（合规要求、无外网环境、数据隐私敏感）
- 你每周输出大量设计（10+），免费方案更具经济性
- 你希望设计产物进入 Git 工作流

**选 Claude Design 当且仅当：**
- 你只是偶尔设计（每周 < 5），受得了 $20/月
- 你没有也不想折腾本地 CLI 环境
- 你就在 Claude 生态里工作
- 你需要开箱即用的抛光效果

**选 v0.dev 当且仅当：**
- 你需要快速生成前端代码，对设计系统要求不高
- 你习惯直接复制代码而非使用工作流工具
- 你的主要产出是 React/Next.js 组件

**选 Lovable 当且仅当：**
- 你需要生成的是全栈可运行应用而非单页设计
- 用户登录、数据库、支付等后端需求优先级高于 UI 抛光

---

## 🎯 核心研判

### 项目优势（不可替代的价值点）

1. **"编排器"定位比"生成器"更具长期价值**：Open Design 不参与模型竞争，而是做所有模型的上层编排。随着底层模型能力趋同，编排层会成为设计品质的关键差异因素。
2. **极致的扩展性**：Skill（~30个）+ Design System（150+）+ Plugin（261+）+ Agent（25种），这个组合数是乘数效应。其他竞品无法快速复制此生态。
3. **Git 原生的工作流**：从生成到 PR 评审到部署，设计产物走完整 DevOps 流水线。这是其他所有 AI 设计工具无法做到的。
4. **社区飞轮效应显著**：74K Star + 300+ 贡献者 + 日更的 CI 流水线，项目正处在自加速增长的阶段。

### 项目风险（潜在隐患和局限性）

1. **⚠️ 重度风险：底层 Agent 兼容性问题**（Issue #5036）
   Claude-stream-json 协议对非 Anthropic 模型的兼容性存在结构性问题。GLM 和 MiMo 模型会丢 `tool_use`，而且这种失败以"成功"（Succeeded）状态报告给用户——这是最危险的一类 bug，因为用户会以为设计已经完成，实则产出了空结果。

2. **⚠️ 中度风险：中文地区用户体验不佳**
   中国境内 Docker 部署 + AMR 登录的问题在 Issue #5035 中已经确认。虽然可以通过 HTTPS_PROXY 或 VELA_RUNTIME_KEY 绕过，但增加了上手成本。

3. **⚠️ 中度风险：macOS CLI 命名冲突**（Issue #5120）
   `od` 命令与系统内置的 `od`（octal dump）冲突。这虽然不是核心功能缺陷，但会降低新手的第一印象。

4. **⚠️ 轻度风险：依赖链条过长**
   Node 24 + pnpm 10.33.x + 一个 Agent CLI + 可能有 Docker，对新手而言光是装环境就可能劝退。

5. **⚠️ 轻度风险：v1.0 尚未发布**
   当前版本为 0.12.1，仍在高频迭代期。项目中存在大量 TODO 和 Roadmap 未完成的特性（Comment-mode 部分完成、Tweaks Panel UX 未实现、Plugin SDK 规划中）。**做出生产环境决策前需要谨慎评估。**

### 适用场景 & 不适用场景

**✅ 适用场景：**
- 产品原型 / MVP / Landing Page
- 企业品牌规范下的批量设计输出
- SaaS Dashboard 和内部工具 UI
- 融资路演 PPT / 团队周报 / 产品 Deck
- 设计系统从零搭建到版本管理
- CI/CD 中的自动化设计生成

**❌ 不适用场景：**
- 需要像素级精确控制的 UI 设计
- 生产级核心产品界面（建议作为初稿而非终稿）
- 需要复杂 Figma 生态插件的团队
- 没有技术背景的设计师独立使用
- 低频使用场景（不如直接用 Claude Design）

### 趋势判断（上升期/稳定期/衰退期）

**当前阶段：爆发式上升期（2026年4月-至今）**

- Star 曲线：从 0 到 74K，2 个月增长曲线近乎指数级
- 版本节奏：0.8.0 → 0.9.0 → 0.10.0 → 0.12.1，每 2-3 周一个大版本
- 社区活跃度：Issues 响应快、PR 合并积极、300+ 贡献者
- 关键信号：已出现 Open Design Fellow 计划和 $1,000/MR 资助机制，说明项目正在从"个人项目"向"组织化运营"转型

**预期未来6个月：**
- 如果 1.0 版本顺利发布 + 插件 SDK 完成，将进入"平台生态"第二阶段
- 主要风险来自 Claude Design 未开源且 Anthropic 的改进速度（速度 + 定制化追赶）
- 中文市场受 AMR 和中网络限制影响，增长可能低于全球平均

**长期判断：** Open Design 已经定义了"AI 设计工作流"这个品类，即使未来 Claude Design 开源或推出免费版，Open Design 在"编排层 + 社区生态"上的先发优势也很难在半年内被追平。唯一的变量是框架级的范式转变（例如 Figma 直接集成 AI 生成能力）。

---

## 📂 关键文件路径速查

| 功能 | 文件路径 | 说明 |
|------|----------|------|
| Agent 注册表 | `apps/daemon/src/runtimes/registry.ts` | 25 种 Agent CLI 定义入口 |
| Claude 适配器 | `apps/daemon/src/runtimes/defs/claude.ts` | Claude Code 专用适配器 |
| Agent 检测 | `apps/daemon/src/runtimes/detection.ts` | PATH 扫描 + 能力探测 |
| 五维 Critique | `apps/daemon/src/critique/orchestrator.ts` | SSE 流式评分 + 修复循环 |
| Critique 评分板 | `apps/daemon/src/critique/scoreboard.ts` | 复合评分计算 + 轮次决策 |
| 插件引擎 | `apps/daemon/src/plugins/index.ts` | 插件安装/应用/发布核心 |
| 插件管道 | `apps/daemon/src/plugins/pipeline-runner.ts` | 插件执行流水线 |
| DESIGN.md 解析 | `apps/daemon/src/brands/engine/derive.ts` | 品牌令牌推导引擎 |
| 设计系统导入 | `apps/daemon/src