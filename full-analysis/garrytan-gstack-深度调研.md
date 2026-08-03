# 🔍 garrytan/gstack — 深度调研报告

> **一句话定位**：YC 总裁 Garry Tan 开源的「AI 虚拟工程团队」工作流套件 —— 表面是 62 个 Claude Code 斜杠命令，内核是一个自带**常驻 Chromium 守护进程 + 六层提示注入防御**的浏览器运行时。

| 项目 | 值 |
|------|-----|
| 仓库 | [garrytan/gstack](https://github.com/garrytan/gstack) |
| ⭐ Stars | **126,088** |
| 🍴 Forks | 18,941 |
| 👁 Watchers | 774 |
| 主语言 | TypeScript（运行时 Bun） |
| 许可证 | MIT |
| 创建 / 最后推送 | 2026-03-11 / 2026-07-15 |
| Open Issues | 870 |
| 仓库规模 | 1,336 个文件条目，71 个顶层目录，62 份 `SKILL.md`，75 个 `bin/` 脚本 |
| 归档状态 | 否（活跃） |

> ⚠️ **旧报告勘误**：此前记录的「113K ⭐ / 23 个斜杠命令 / 目录含 docs、contrib」多处失真。实测星标 126,088；GitHub 描述里的「23 tools」是 2026-03 首发时的数字，当前仓库已有 **62 个 SKILL.md**；旧报告列出的目录结构为臆测，本次全部替换为真实目录树。

---

## ✨ 项目亮点（差异化，README 之外）

1. **它其实是个浏览器基础设施项目，Skill 只是外壳。** `ARCHITECTURE.md` 开门见山：「The browser is the hard part — everything else is Markdown.」`browse/src/` 单目录就有 145KB 的 `server.ts` + 75KB 的 `browser-manager.ts`，而 62 个 Skill 全是 Markdown。真正的技术护城河在浏览器守护进程，不在提示词。
2. **六层（L1–L6）提示注入防御，本地跑 22MB BERT 分类器。** 侧边栏 Agent 内置 TestSavantAI int8 量化 ONNX 模型离线扫描每条消息与工具输出，还有金丝雀 token 泄漏检测 + 双分类器投票才允许 BLOCK。这套东西在 Skill 类项目里几乎绝无仅有。
3. **「Boil the Ocean」反直觉方法论被写成可注入的 ETHOS.md。** 它把「不要把海煮沸」这条经典工程箴言直接推翻，并给出压缩比表格（样板代码 ~100x、测试 ~50x、架构 ~5x）作为决策依据。这份文件会**自动注入每个工作流 Skill 的前言**——方法论不是文档，是运行时约束。
4. **多 harness 宿主支持已是一等公民。** 顶层同时存在 `claude/`、`codex/`、`openclaw/` 目录，Issue 区还在推进 GitHub Copilot CLI(#393)、Hermes(#2148)、Google Antigravity(#2261)。它正从「Claude Code 插件」演化为「跨 Agent 宿主的工作流层」。
5. **iOS 全套工作流是隐藏彩蛋。** `ios-clean` / `ios-design-review` / `ios-fix` / `ios-qa` / `ios-sync` 五个 Skill 构成移动端闭环，包含真机隧道恢复逻辑（commit `fix(ios-qa): recover device tunnels safely after relaunch`）。README 几乎没提。

---

## 🏗️ 核心架构

### 三层守护进程模型（`ARCHITECTURE.md`）

```
Claude Code                       gstack
─────────                        ──────
  $B snapshot -i        →   CLI（bun build --compile 单文件 ~58MB）
                            · 读 state file 取 Bearer token
                            · POST /command → localhost:PORT
                                    │ HTTP
                            Server（Bun.serve）
                            · 派发命令 / 返回纯文本
                                    │ CDP
                            Chromium（headless，常驻）
                            · 持久 tab / cookie，30 分钟空闲超时
```

**首调用 ~3s，之后每次 ~100–200ms。** 设计动机写得很直白：Playwright 冷启动 2–3 秒，一次 20+ 命令的 QA 会话光启动开销就 40 秒以上，而且 cookie、localStorage、登录态全丢。

### 为什么选 Bun（原文给了 4 条，其中 2 条才是真理由）

| 理由 | 说明 | 是否关键 |
|------|------|---------|
| 编译单文件 | `bun build --compile` 产出 58MB 可执行文件，装进 `~/.claude/skills/` 后无需管理 node_modules | ✅ 关键 |
| 原生 SQLite | 直读 Chromium cookie 库，免 `better-sqlite3` / node-gyp 编译 | ✅ 关键 |
| 原生 TS / 内建 HTTP | 开发期免编译；`Bun.serve()` 免 Express | ➖ 次要 |

原文自陈：「瓶颈永远是 Chromium，不是 CLI 或 server。Bun 1ms 的启动速度很好，但不是我们选它的理由。」——**这种反向澄清是判断架构文档质量的好信号。**

### 顶层目录（71 个，节选真实结构）

```
gstack/
├── browse/          # ★ 核心：Chromium 守护进程 + CDP 客户端（TS，18 个 src 文件）
├── bin/             # 75 个 shell/TS 脚本（gstack-brain-*、gstack-config、gstack-security-dashboard…）
├── lib/             # 共享库：redact-engine.ts、gstack-memory-helpers.ts、diagram-render/
├── agents/          # 角色配置（openai.yaml）
├── claude/ codex/ openclaw/   # 多宿主适配层
├── autoplan/ spec/ review/ qa/ ship/ retro/ ...   # 每个工作流 = 一个含 SKILL.md 的目录
├── ios-{clean,design-review,fix,qa,sync}/         # iOS 专用工作流
├── supabase/        # community-pulse 社区遥测 Edge Function
└── ETHOS.md ARCHITECTURE.md CLAUDE.md SKILL.md TODOS.md CHANGELOG.md(912KB!)
```

`CHANGELOG.md` 高达 **912KB**、`TODOS.md` 144KB —— 侧面印证迭代密度极高。

---

## 🔬 源码深度解读（挑 3 处最有借鉴价值的）

### 1. Ref 系统：用 Playwright Locator 而非 DOM 注入

Agent 通过 `@e1`、`@e2` 这样的短引用点击元素，不写 CSS 选择器。实现路径：

```
$B snapshot -i
  → page.accessibility.snapshot()          # 走 Chromium 内建无障碍树
  → 遍历 ARIA 树，顺序分配 @e1/@e2/@e3
  → 每个 ref 建一个 Locator: getByRole(role,{name}).nth(index)
  → Map<string,RefEntry> 存在 BrowserManager 实例上
$B click @e3
  → resolveRef("e3") → locator.click()
```

**为什么不注入 `data-ref` 属性**（文档明确列了三条反例）：CSP 会拦截脚本改 DOM；React/Vue/Svelte 水合会抹掉注入属性；Shadow DOM 从外部够不着。Locator 存在于 DOM 之外，三个问题全绕过。

**陈旧检测**：SPA 路由切换不触发 `framenavigated`，refs 会静默失效。`resolveRef()` 因此在使用前先 `await locator.count()`：

```
resolveRef(@e3) → entry = refMap.get("e3")
                → count = await entry.locator.count()
                → count === 0 ? throw "Ref @e3 is stale — run 'snapshot'"
                              : return { locator }
```

约 5ms 开销，换掉 Playwright 默认 30 秒超时才失败的糟糕体验。**「快速失败优于长超时」在 Agent 场景下价值被放大**——Agent 不会等，它会重试并烧掉更多 token。

### 2. 孤儿代理对（lone surrogate）净化：一个页面能杀死整个会话

这是全仓库最值得抄的一个坑（`v1.38.0.0`）：网页 JS 字符串处理不当会产出孤立的 UTF-16 代理半对，`JSON.stringify` 把它编码成 `\uD800`，下游 `JSON.parse` 能接受，但 **Anthropic API 直接返回 400**——一个奇怪的页面就能终结整个会话。

修复是**单点净化 + 架构不变量**：

| 出口 | 净化点 |
|------|--------|
| `POST /command` / `/command/batch` | `handleCommandInternal` 包装器 |
| `GET /activity/stream`（SSE） | `JSON.stringify(payload, sanitizeReplacer)` |
| `GET /inspector/events`（SSE） | 同上 |
| `text/plain` 响应 | `sanitizeLoneSurrogates(body)` 纯字符串版 |

关键细节：**不能用 stringify 之后的正则**——那时 `\uD800` 已经变成字面量 `"\\ud800"`，正则匹配不到。必须用 replacer 在编码管线**内部**清洗。仓库还把这条写成不变量，用 `browse/test/server-sanitize-surrogates.test.ts` 钉死接线（测试会断言函数改名、中心净化行、replacer 存在、两个 SSE 生产者都带 replacer）。

> 💡 **启发**：任何「把网页/外部内容喂给 LLM API」的系统都会踩这个坑。修复模式值得直接复制：单点出口净化 + 用测试钉住架构不变量，而不是靠 code review 记得。

### 3. 双监听器权限面：tunnel 上 root token 直接 403

`browse` 服务同时开本地监听器和隧道监听器，同一路径在两个面上权限完全不同：

| 路由 | 本地面 | 隧道面 |
|------|--------|--------|
| `POST /command` | Bearer root 或 scoped | **仅 scoped + 命令白名单**；root token 上隧道 = 403 |
| `POST /pair`、`/tunnel/*`、`/token` | root-only | **404**（不是 403，直接装作不存在） |
| `GET /cookie-picker`、`/inspector`、`/welcome` | 本地可用 | **404** |
| SSE 流 | Bearer 或 HttpOnly `gstack_sse` cookie（30 分钟只读） | 404 |

隧道面每次拒绝都异步写 `~/.gstack/security/attempts.jsonl`（含时间戳、`x-forwarded-for` 源 IP、路径、方法），全局限速 60 次/分防日志洪水 DoS。**"隧道上返回 404 而非 403" 是刻意的信息隐藏**——不暴露端点存在性。

**已知未修缺口（仓库自己列为 #1136 非目标）**：cookie 导入路径用 `--remote-debugging-port=<random>` 启动 Chrome，在 Windows App-Bound Encryption v20 下，同用户本地进程可连该端口窃取已解密的 v20 cookie。修复方向是改用 `--remote-debugging-pipe`。**主动公开未修安全缺口，可信度加分。**

---

## 💡 应用场景与启发

| 场景 | 怎么用 gstack |
|------|--------------|
| **单人/双人创业团队做全流程** | 直接跑 `/office-hours → /autoplan → /spec → /review → /qa → /ship → /retro`，把 YC 式产品拷问固化进流程 |
| **需要给 Agent 装浏览器** | 只抄 `browse/` 也值——常驻守护进程 + Locator ref + 出口净化，是目前开源里最完整的 Agent 浏览器方案之一 |
| **构建对抗提示注入的 Agent** | `browse/src/security.ts` + `security-classifier.ts` 的 L1–L6 分层（数据标记→隐藏元素剥离→URL 黑名单→本地 ML→金丝雀 token→双分类器投票）是可直接迁移的模板 |
| **把方法论变成工程约束** | `ETHOS.md` 自动注入每个 Skill 前言的做法，适合任何想让团队规范真正生效（而非躺在 wiki 里）的组织 |
| **多 Agent 宿主兼容** | `claude/` `codex/` `openclaw/` 的适配层拆法，可参照做跨 harness 的 Skill 分发 |

**遇到这些问题可以回来翻这个仓库**：
- 「Agent 调浏览器太慢/丢登录态」→ 看守护进程模型
- 「页面内容喂给 LLM API 报 400」→ 看孤儿代理对净化
- 「怎么防提示注入」→ 看 L1–L6 分层与 `combineVerdict` 投票
- 「Skill 越写越多怎么组织」→ 看 62 个 `SKILL.md` + `SKILL.md.tmpl` 模板化方案

---

## 💬 社区口碑与真实痛点

**活跃度**：截至 2026-07-15 最后推送，PR 编号已到 **#2264**，Issue 编号 #2261，四个月烧掉 2000+ 编号。commit 大量来自 `time-attack/*` 分支（自动化 Agent 分支命名），说明仓库本身高度依赖 gstack 自举开发。

**真实抱怨点**（取自讨论最多的 open issue）：

| Issue | 痛点 |
|------|------|
| #1174（11 评论） | Conductor gstack 模板在新项目创建时 build exit code 128 失败 |
| #1269（7 评论） | **Cursor 的 setup 直接坏掉** |
| #1201（7 评论） | `setup --host hermes` 只打印 help banner 而非真的安装，"host install" 语义不明 |
| #1864 | Windows 上 browse 冷启动会闪出控制台窗口 |
| #2129 | Windows 符号链接需要 SeCreateSymbolicLinkPrivilege 才可用 |
| #1071 | 模型设计偏见：倾向少建表 + 滥用 JSONField，需要专门 Skill 去纠偏 |

**共性判断**：核心（macOS + Claude Code）体验成熟，**Windows 与非 Claude 宿主（Cursor/Hermes/Copilot CLI）是主要粗糙面**。870 个 open issue 也说明 issue 处理速度跟不上迭代速度。

**值得注意的信号**：`.github/workflows/` 里有 `evals.yml`（15.9KB）和 `evals-periodic.yml` —— 它为提示词/工作流建立了 CI 评测，这在 Skill 类项目里极罕见。另有 `windows-free-tests.yml`、`windows-setup-e2e.yml` 专门治 Windows 顽疾。

---

## ⚔️ 竞品对比

| 项目 | 定位 | 与 gstack 的关键差异 |
|------|------|---------------------|
| **gstack** | 角色化工作流 + 自带浏览器运行时 | 唯一自带编译版 Chromium 守护进程 + 本地 ML 注入防御；Skill 数量最多（62） |
| **ChromeDevTools/chrome-devtools-mcp** | 官方 CDP MCP 服务 | 只做浏览器，无工作流；协议层更标准，但无持久守护 + 无注入防御 |
| **vercel-labs/agent-browser** | Agent 浏览器控制 | 同赛道浏览器层，但不含产品/评审/发布工作流 |
| **anthropics/skills** | 官方 Skill 参考集 | 官方规范样板，无浏览器、无角色流程 |
| **open-gsd/gsd-core**（GSD 继任者） | 规格驱动多 Agent | 强在 phase/workstream 规格，弱在真实环境验证 |
| **BMAD** | 构建-测量-调整循环 | 循环驱动，非角色驱动，无浏览器 |

**赛道判断**：gstack 已经不在「Skill 集合」这个赛道了。同量级项目里，只有它把「Agent 的真实环境验证能力」做成了自带二进制。

---

## 🧠 核心研判

1. **真正的壁垒是 browse，不是 Skill。** 62 个 Markdown 谁都能 fork 改，58MB 编译版 Chromium 守护进程 + 六层注入防御 + 出口净化不变量则需要长期投入。评估 gstack 时把它当浏览器基础设施看，判断会准得多。

2. **`ETHOS.md` 是被低估的产物。** 「AI 让完整性的边际成本趋近于零，所以『别把海煮沸』这条建议已经过期」——这套压缩比表格（样板 100x / 测试 50x / 特性 30x / 架构 5x / 研究 3x）配合自动注入机制，本质是**把决策偏好写进运行时**。这个模式比任何具体 Skill 都更可迁移。

3. **它正在从插件变成平台，但适配层是软肋。** `claude/` `codex/` `openclaw/` 三个宿主目录 + 四个在推进的宿主（Copilot CLI / Hermes / Antigravity / Cursor），而 Cursor setup 已坏、Hermes 安装是空壳。**广度扩张跑在质量前面**，这是当前最大风险。

4. **870 个未关 Issue + 912KB CHANGELOG = 典型的高速单核项目。** 迭代由 Garry Tan 与自动化 Agent 分支驱动，社区 Issue 更像积压的反馈池而非协作入口。若要在生产依赖它，建议锁定版本并自行维护 fork。

5. **主动披露未修安全缺口（#1136 Windows ABE v20 cookie 提权路径）是罕见的成熟度信号。** 大多数同类项目连威胁模型都不写。这条反而提升了对整套安全设计的信任度——但也提醒使用者：**cookie 导入功能在 Windows 上目前有已知风险，谨慎使用。**

---

## 📂 关键文件速查

| 路径 | 大小 | 作用 |
|------|------|------|
| `ARCHITECTURE.md` | 32KB | **必读**。守护进程模型、Ref 系统、双监听器权限面、L1–L6 注入防御 |
| `ETHOS.md` | 7.9KB | 自动注入每个 Skill 的方法论（Boil the Ocean / Search Before Building / 三层知识） |
| `browse/src/server.ts` | 145KB | Bun.serve 主服务，命令派发 + SSE + 出口净化 |
| `browse/src/browser-manager.ts` | 76KB | Chromium 生命周期、refMap、`resolveRef()` 陈旧检测 |
| `browse/src/security-classifier.ts` | 27KB | TestSavantAI BERT-small ONNX 本地注入分类器（仅侧边栏进程） |
| `browse/src/security.ts` | 24KB | 金丝雀 token、`combineVerdict` 投票、攻击日志 |
| `browse/src/snapshot.ts` | 27KB | ARIA 树 → `@e1/@e2` ref 生成 |
| `browse/src/token-registry.ts` | 17KB | scoped token 铸造/吊销（与 SSE cookie 模块严格隔离） |
| `lib/redact-engine.ts` + `redact-patterns.ts` | 39KB | 敏感信息脱敏引擎 |
| `SKILL.md.tmpl` | 5.6KB | Skill 模板，62 个工作流的统一骨架 |
| `.github/workflows/evals.yml` | 16KB | 提示词/工作流 CI 评测 |
| `CHANGELOG.md` | **912KB** | 迭代密度的直接证据 |

---

## 🔗 链接

- 仓库：https://github.com/garrytan/gstack
- 许可证：MIT
- 安装：`git clone --depth 1 https://github.com/garrytan/gstack.git ~/.claude/skills/gstack && cd ~/.claude/skills/gstack && ./setup`
- 配套项目：[garrytan/gbrain](https://github.com/garrytan/gbrain)（记忆层，仓库内有 30KB 的 `USING_GBRAIN_WITH_GSTACK.md`）

> 调研日期：2026-08-04 ｜ 数据来源：GitHub API 实测元数据、完整目录树（1,336 条）、`ARCHITECTURE.md`/`ETHOS.md`/`DESIGN.md` 原文、open issues 与 commit 记录
