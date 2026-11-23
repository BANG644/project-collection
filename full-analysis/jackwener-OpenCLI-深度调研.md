# 🔬 jackwener/OpenCLI — 全方位深度调研

> 调研时间：2026-11-24（修旧账重写，原稿为 2026-06-19 抽样模板报告）
> 数据来源：`gh api` 实时抓取（元数据 / README 23KB / 文件树 600KB / 60 Issues / 20 Releases / `docs/developer/architecture.md` / `autoresearch/eval-skill.ts`）+ 第三方评测（Hlido / ReviewRamble / CSDN / dev.to）

## 📌 一句话定位

把「你已登录的浏览器」和 100+ 网站变成**确定性的命令行接口**：内置站点适配器让 Agent 用 `opencli hackernews top -f json` 这类稳定命令拿数据，其余网站用 `browser open/click/fill/extract` 原语 drive 你自己的 Chrome 登录态——核心卖点是「不写爬虫、不碰 API key、复用真实登录会话」。

> 核心判断：它的真正创新不是「网站转 CLI」，而是**让 Agent 在确定性命令（便宜、可脚本化）和 browser 原语（通用、能兜底）之间分层选择**。但这套能力建立在"借用你真实 Chrome 的全部登录态"之上——**便利与风险同源**，这是理解这个项目的钥匙。

**实时数据**：31,241⭐ / 3,057 forks / JavaScript / Apache-2.0 / 350 open issues / 最后推送 2026-11-07 / v2.0.3（2026-11-07）。

## ⭐ 项目亮点

1. **四层访问策略的智能降级**：`public`（直接 fetch）/ `cookie`（复用会话）/ `intercept`（拦截站点自己的网络响应）/ `ui`（DOM 驱动）——按站点特点选策略，`public` 不依赖浏览器，其余依赖 live browser。这是从架构文档里挖到的、README 未曾系统阐述的分层设计。
2. **sysexits 退出码 + 固定 JSON 信封**：`66` 空结果、`69` bridge 断、`75` 超时可重试、`77` 需登录、`78` 配置错——脚本/Agent 可靠判断状态。第三方 ReviewRamble 评价这是「比截图式浏览便宜得多、更好写脚本」的关键。
3. **adapter-authoring skill 让 Agent 自己写适配器**：一条 skill 引导 Agent 走「侦察站点 → 发现端点 → 选认证 → 字段解码 → verify」全流程；还有 `opencli-autofix` 应对站点改版导致的适配器失效——把"反爬维护"这个人力黑洞产品化。
4. **autoresearch 子系统：用 LLM Judge 自动评测 skill 质量**。`autoresearch/eval-skill.ts` 内置 27 个任务（extract/list/search/nav/scroll/form/complex/bench），spawn Claude Code 跑 adapter-author skill，再用 `judge_context` 多准则自评，统计 pass率/时长/成本。这是「用 Agent 评测 Agent skill」的实证工程。
5. **双连接模式**：Browser Bridge 扩展（本地 daemon + 扩展 + 已登录 Chrome，主路径）与直接 CDP（`OPENCLI_CDP_ENDPOINT`，远程/无头 Chrome）并存，覆盖桌面与服务器。

## 🏗️ 项目架构全景

### 四大子系统（架构文档权威表述）

OpenCLI 是架在四个子系统之上的命令面：①命令发现与注册 ②执行与格式化 ③浏览器/daemon/CDP 连接 ④适配器与插件集成。

```text
opencli CLI
  ├─ command discovery / registry   (discovery.ts / registry.ts / registry-api.ts)
  ├─ execution / output             (execution.ts / output.ts: table|json|yaml|md|csv)
  ├─ browser runtime
  │   ├─ Browser Bridge extension   (主路径: 已登录 Chrome)
  │   ├─ local daemon               (localhost:19825)
  │   └─ direct CDP path            (OPENCLI_CDP_ENDPOINT)
  └─ adapter & plugin loading
      ├─ built-in adapters (clis/, 100+)
      ├─ generated adapters (~/.opencli/clis/)
      └─ pipeline-backed adapters  (src/pipeline/steps/: fetch|download|browser|intercept|tap|transform)
```

### 命令来源合并

`opencli list` 看到的是一棵统一命令树，由三处合并：内置适配器（`clis/`）、用户自写（`~/.opencli/clis/`）、社区插件（`~/.opencli/plugins/`）。`src/commanderAdapter.ts` 把 registry 元数据桥接成 Commander 子命令——这是「一处注册、多处可用」的关键胶水。

### 技术栈与发布形态

TypeScript（Node ≥ 20.18.1）；npm 包 `@jackwener/opencli` + 桌面 App（macOS/Windows）+ Chrome 扩展。Agent 侧通过 `npx skills add jackwener/opencli` 装 skill。仓库顶层 25 个目录，含 `docs/`（VitePress 双语文档）、`autoresearch/`、`cases/`、`skills/`、`extension/`。

## 💡 应用场景与启发（重点章节）

### 典型使用场景（来自 Official + 第三方评测的真实案例）

- **社交媒体运营（尤其中文平台）**：定时跑 `opencli xiaohongshu creator-stats` / `opencli bilibili creator-stats -f csv` 进表格。ReviewRamble 点名这是它的"主场"——小红书 16 条命令、B 站 18 条，含 post/reply/follow/upvote 等写操作。
- **给研究型 Agent 读登录后的页面而不交密码**：装 `opencli-browser` skill，指向一个只登录必要站点的独立 Chrome profile，Agent 走 DOM 快照而非截图。
- **替换脆弱的一次性爬虫**：把 adapter 写进插件仓库版本管理，站点改版用 `opencli-autofix` 修。

### 可借鉴的解决方案模式

1. **「确定性命令 + 通用原语」双层接口**是给 Agent 设计工具时的黄金结构：能枚举的高频操作封装成稳定命令（token 便宜、可测试），长尾交给通用原语兜底。相似思路可用于任何"给 Agent 做工具层"的产品。
2. **退出码语义化（`sysexits.h` 约定）**：把「空/断连/超时/需登录/配置错」编码成不同 exit code，让上层脚本能精确分支重试。这是被低估的工程细节——多数 MCP/CLI 工具只返回成功/失败。
3. **adapter 自愈闭环**：站点改版是爬虫的天敌。它把"发现失效 → Agent 侦察新端点 → 重写 adapter → verify"做成 skill，值得任何依赖外部站点的数据产品设计。
4. **用 LLM Judge 做 skill 回归评测**：`eval-skill.ts` 的 27 任务 + `judge_context` 多准则，展示了"如何量化一个 prompt/skill 的质量"——可直接迁移到你自己的 Agent skill 评测体系。

### 同类需求的可参考思路

如果你的需求是「让 Agent 操作需要登录的 Web 系统」，本项目的取舍很值得对照 browser-use：browser-use 跑自己的浏览器（隔离好、适合无人值守），OpenCLI 借用你的登录态（复用强、但注入风险高）。**选择取决于账号敏感度**——第三方评测一致建议用"独立 profile"来降低风险。

## 🧠 核心源码解读

### 访问策略抽象（架构文档 + README）

四种 strategy 不是实现细节，而是贯穿 design 的一等概念：

| Strategy | 用途 | 依赖 live browser |
|---|---|---|
| `public` | 直接 fetch，无登录 | 否 |
| `cookie` | 复用浏览器会话 cookie | 是 |
| `intercept` | 捕获 App 自己的网络响应 | 是 |
| `ui` | DOM / accessibility 驱动交互 | 是 |

**为什么这么设计**：cookie/intercept 比纯 DOM 抓取更稳（拿到的是站点自己的结构化数据而非渲染文本），但代价是必须有一条活浏览器链路。这解释了为什么它需要 daemon + 扩展这一整套基础设施。

### autoresearch：Agent skill 的自评测循环（`autoresearch/eval-skill.ts`）

```ts
interface SkillTask { name; task; url?; judge_context: string[]; max_steps? }
const TASKS = [
  { name: "extract-github-stars", url: "...browser-use", judge_context: ["Output must contain a number (the star count)"] },
  { name: "form-login", url: "...the-internet.herokuapp.com/login",
    judge_context: ["must type 'testuser'...", "must NOT be submitted"] },
  ...
];
```

评测器 spawn Claude Code 带着 `opencli-adapter-author` skill 完成任务，再用 `judge_context` 做多准则判定，记录 `passed / duration / cost / explanation`。**独家发现**：任务集里特意放了 `form-login` / `form-fill` 且 judge 要求"必须不要提交"——说明作者在评测时刻意测"Agent 是否会越界执行写操作"，这是安全考量的体现。脚本头部注释自称 "Layer 2: Claude Code Skill E2E Testing (LLM Judge)"，暗示还有 Layer 1（baseline-skill.txt）做对照。

### 高风险改动区（架构文档主动标注）

`src/cli.ts`、`commanderAdapter.ts`、`discovery.ts`、`execution.ts`、`runtime.ts`、`daemon.ts`、`plugin.ts`、`pipeline/**` 被官方标为「改动影响面广」，需先针对性测试。这份自我标注是判断项目工程成熟度的好信号。

## 📐 架构决策与设计哲学

- **稳定性优先于覆盖广度**：宁可把 100+ 高频站点做成确定性适配器，也不承诺"任意网站都行"——第三方 Hlido 评测恰指出 "any website" 的广度宣称在长尾页面未经验证。
- **本地优先、数据不出机**：daemon 跑 localhost、复用本地 Chrome profile；官方 PRIVACY.md 说明数据本地处理。
- **v2.0  breaking change** 是重要哲学转变：2026-10-17 的 v2.0.0 重写了 CLI 语法与 JSON 输出契约，ReviewRamble 因此明确建议"pin 版本"——这是年轻项目快速迭代的典型代价。

## 🌐 全网口碑画像（5+ 真实来源）

- **ReviewRamble 3.8/5**："needs treating like a credential rather than a utility"（要像对待凭据一样对待它）——精准点出 prompt injection 可触及所有已登录账号的风险；同时肯定 sysexits + 固定 JSON 信封"便宜又好脚本化"。来源：reviewramble.com/github-repos/opencli
- **Hlido 独立实测 75/100（STEADY）**："a genuinely agent-shaped idea"，但 5 项公开面检查中 2 项 FAIL（无 CTA / 无明确 pricing），且无法手验 "any website" 在杂乱页面上的鲁棒性；Agentic-Commerce Readiness 仅 48/100（surface-only）。来源：hlido.eu/reviews/jackwener-opencli
- **CSDN 中文实测**（进击的雷神）：详细写了扩展加载 + npm 安装 + `opencli doctor` 自检五分钟上手流程，特别强调退出码语义（66/69/75/77/78）的价值。来源：thundergod-lyx.blog.csdn.net
- **dev.to 评测**（tenglongai2026）："The killer feature? It works through your already-logged-in browser"；把它与 Playwright/Puppeteer 对比，定位为"把网站变 CLI"的差异化路线。来源：dev.to/tenglongai2026
- **UseAI Station 编辑评测**：认可其"logged-in browser + deterministic command"双路径，但也列入 alternatives（Orca / qwen-code）供选型。来源：useaistation.com/githubai/projects/jackwener-opencli
- **GitHub Issue 一手信号**：350 open issues，高频痛点很具体——小红书 saved 只返 10 条（拦截器在导航时丢失）、Windows junction/symlink 适配器被静默忽略、browser get text 泄露 `<script>` JSON（session/auth state）、非英文 X UI 上 twitter 回复超时（成功 toast 只匹配英文）。还有一条「jackwener/OpenCLI was independently reviewed on Hlido — scored 75/100」说明社区在跟进第三方评测。

> 口碑结论：**好评集中在"确定性+免密登录态"的独特价值，差评集中在"站点改版易碎 + 安全边界 + 英文 UI 适配不全"**。被反复提醒的稳定做法是用独立 Chrome profile。

**可核验来源**：[ReviewRamble 3.8/5](https://www.reviewramble.com/github-repos/opencli) · [Hlido 独立实测 75/100](https://hlido.eu/reviews/jackwener-opencli) · [CSDN 中文实测](https://thundergod-lyx.blog.csdn.net/article/details/167388113) · [dev.to 评测](https://dev.to/tenglongai2026/i-turned-my-browser-into-a-terminal-and-now-i-can-control-any-website-from-the-command-line-124l) · [UseAI Station](https://useaistation.com/githubai/projects/jackwener-opencli)

## ⚔️ 竞品对比

| 方案 | 核心差异 | 登录态复用 | 隔离性 | 确定性 |
|---|---|---|---|---|
| **OpenCLI** | 网站→确定性 CLI + 已登录 Chrome | ✅ 强 | 弱（用真实 profile） | 强（适配器+exit code） |
| browser-use | 通用浏览器自动化 Agent | ❌ 自有浏览器 | 强 | 中（LLM 驱动） |
| Playwright/Puppeteer | 底层自动化库 | 需自己写 | 中 | 低（要写 200 行样板） |
| CLI-Anything | 把 CLI 工具变 AI 工具（反方向） | N/A | N/A | — |

**选择建议**：复用已有登录态、要稳定命令接口 → OpenCLI；无人值守、账号敏感、要强隔离 → browser-use 自有浏览器；从零写自动化 → Playwright，但别指望它有 adapter 生态。

## 🎯 核心研判

### 优势

1. **定位精准且差异化**：确定性命令 + 登录态复用这一组合，browser-use / Playwright 都没正面提供。
2. **生态与迭代活跃**：31k⭐、v2.0.3 当月发布、100+ 适配器、双语文档、agent skill 齐备。
3. **工程细节到位**：sysexits 退出码、autofix 自愈、LLM Judge 评测、高风险改动区标注——都超出"营销型项目"水准。

### 风险

1. **安全是头号问题**：Agent 在真实 profile 内操作，页面 prompt injection 可触达所有已登录账号（ReviewRamble 原话警示）。
2. **易碎性**：350 open issues，适配器随站点改版失效；非英文 UI / Windows 特有问题多。
3. **v2.0 breaking change**：JSON 契约重写，迁移需 pin 版本。
4. **ToS 灰色地带**：post/reply/upvote 等写操作及下载功能可能触碰平台条款，责任在账号持有者。

### 适用场景 & 不适用场景

- ✅ 社媒数据运营、读登录后页面、把内部 Web 工具包装成 Agent 接口、替换一次性爬虫。
- ❌ 需要保证任意站点成功率、非技术用户的无代码自动化、对账号隔离有强合规要求的场景。

### 趋势判断

**上升期但处于契约动荡期**。v2.0 刚重构完、issue 量大但迭代快（月度 release）。安全模型与适配器稳定性是能否从"极客玩具"走向"团队基础设施"的关键门槛。

## 📂 关键文件路径速查

| 路径 | 用途 |
|---|---|
| `docs/developer/architecture.md` | 四大子系统 + 四访问策略 + 高风险改动区（理解架构第一站） |
| `src/cli.ts` / `src/registry.ts` / `src/discovery.ts` | 命令树入口与注册发现核心 |
| `src/execution.ts` / `src/runtime.ts` | 参数校验、懒加载、目标解析 |
| `src/daemon.ts` / `src/browser/` / `src/interceptor.ts` | Browser Bridge 连接与拦截 |
| `src/pipeline/executor.ts` / `src/pipeline/steps/` | 声明式适配器管线引擎 |
| `clis/` | 100+ 内置站点适配器（按站点分目录） |
| `autoresearch/eval-skill.ts` | 27 任务 LLM Judge 评测器 |
| `skills/opencli-adapter-author/` | 让 Agent 自写适配器的 skill |
| `README.md` → Exit Codes / Output Formats | sysexits 退出码与 JSON 信封权威表 |
