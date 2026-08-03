# 🔍 anthropics/claude-plugins-official — 深度调研报告

> **一句话定位**：Anthropic 官方 Claude Code 插件目录 —— 但它真正的产品不是那 39 个自研插件，而是一套**「AI 当安全审核员 + SHA 钉版 + 自动回滚 + 外部 PR 自动关门」的软件供应链治理流水线**。

| 项目 | 值 |
|------|-----|
| 仓库 | [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official) |
| ⭐ Stars | **33,005** |
| 🍴 Forks | 3,727 |
| 👁 Watchers | 199 |
| 主语言 | Python |
| 许可证 | Apache-2.0（仓库级；各插件以自身 LICENSE 为准） |
| 创建 / 最后推送 | 2025-11-20 / **2026-08-03**（当日仍在合并） |
| Topics | `claude-code`、`mcp`、`skills` |
| Open Issues | 860 ｜ 已合/关 PR：**3,762** ｜ 最新 PR 编号 **#4822** |
| 仓库规模 | 662 个文件条目；`plugins/` 39 个、`external_plugins/` 15 个 |
| marketplace.json | **163KB，278 条插件条目** |

> ⚠️ **旧报告勘误**：此前记录「30,184⭐ / 3,266 forks / 创建于 2025-12」，实测为 33,005⭐ / 3,727 forks / 2025-11-20 创建。旧报告通篇为 README 转述，无架构、无口碑、无研判，本次完全重写。

---

## ✨ 项目亮点（README 完全没讲的部分）

1. **仓库里只有 8% 的插件。** marketplace.json 有 278 条目，但本地目录只有 54 个（39 内部 + 15 外部）。其余 **224 条是远程指针**：143 条 `source: url`、80 条 `source: git-subdir`、2 条 `github`。这是一个**索引仓库**，不是代码仓库。
2. **Anthropic 用 Claude 审 Claude 插件。** `.github/policy/prompt.md`（7,977 字节）是一份完整的 AI 安全审查员系统提示词，配 `schema.json` 强制结构化裁决输出。`scan-plugins.yml` 工作流 **27KB** —— 这是全仓库最大的一个文件。
3. **审查标准明确高于「无恶意」**：原文第一句就是 *"The bar here is 'handles user data responsibly,' not merely 'isn't malicious.'"* 插件可以完全无害，但只要 hook 观测范围超出其声明用途、或描述与实际行为不符，一样判不通过。
4. **策略文件里点名了一起真实事故**：反复出现的 **"the vercel-style misuse"** —— 读取 `ANTHROPIC_AUTH_TOKEN` 后发往非 Anthropic 端点。这是把一次真实供应链事件固化成了自动化检测规则。
5. **外部 PR 默认自动关闭。** `close-external-prs.yml` 用 `pull_request_target` 触发，非成员 PR 一律评论 + 关闭，只放行一种例外：给「源仓库已在市场中的插件」补 marketplace.json 条目。新插件必须走 `clau.de/plugin-directory-submission` 表单。

---

## 🏗️ 核心架构：治理流水线才是主体

### 目录结构（真实）

```
claude-plugins-official/
├── .claude-plugin/
│   └── marketplace.json        # ★ 163KB，278 条目，全站唯一真相源
├── plugins/                    # Anthropic 自研 39 个
│   ├── {clangd,csharp,gopls,jdtls,kotlin,lua,php,pyright,ruby,
│   │    rust-analyzer,swift,typescript}-lsp/      ← 12 个 LSP 插件
│   ├── code-review/ pr-review-toolkit/ code-simplifier/ code-modernization/
│   ├── claude-security/ security-guidance/ hookify/ mcp-tunnels/
│   ├── skill-creator/ plugin-dev/ mcp-server-dev/ agent-sdk-dev/
│   ├── ralph-loop/ receipts/ session-report/ project-artifact/ playground/
│   └── explanatory-output-style/ learning-output-style/ math-olympiad/ ...
├── external_plugins/           # 合作方 15 个
│   └── asana context7 discord fakechat firebase github gitlab greptile
│       imessage laravel-boost linear playwright serena telegram terraform
└── .github/
    ├── policy/
    │   ├── prompt.md           # ★ AI 安全审查员提示词（7.9KB）
    │   └── schema.json         # ★ 裁决结果强制 JSON Schema（9 个必填字段）
    ├── scripts/
    │   ├── discover_bumps.py           # 8.4KB  发现上游新 SHA
    │   ├── external-pr-scope.js        # 7.3KB  外部 PR 范围判定
    │   └── validate-frontmatter.ts     # 7.3KB  SKILL/agent frontmatter 校验
    └── workflows/
        ├── scan-plugins.yml            # 27KB ★ AI 安全扫描主流程
        ├── revert-failed-bumps.yml     # 14.3KB ★ 失败自动回滚
        ├── bump-plugin-shas.yml        # 4.8KB  自动升级 SHA
        ├── check-mcp-urls.yml          # 6.1KB  MCP 远端 URL 存活检查
        ├── close-external-prs.yml      # 2.8KB  外部 PR 自动关门
        ├── external-pr-scope-guard.yml / validate-{frontmatter,licenses,plugins}.yml
```

### 供应链闭环

```
上游第三方仓库更新
   ↓  discover_bumps.py（定时扫描）
bump-plugin-shas.yml  → 自动开 PR：bump(posthog): 257a7d59 → 13dd2e24
   ↓
scan-plugins.yml      → 克隆整仓 → Claude 按 policy/prompt.md 审查 → 输出 schema.json 结构化裁决
   ↓  通过                       ↓ 不通过 / 后续失败
合并，marketplace.json 钉新 SHA   revert-failed-bumps.yml 自动回滚到上一个已知良好 SHA
```

`2026-08-03` 当天的 commit 记录直接印证：`bump(ui5)`、`bump(chrome-devtools-mcp)`、`bump(astronomer-data-agents)`、`bump(modern-web-guidance)` 四连发 —— **这条流水线每天在跑。**

### 插件分类分布（解析 marketplace.json 得出）

| 分类 | 数量 | | 分类 | 数量 |
|------|-----|---|------|-----|
| development | 116 | | deployment | 8 |
| productivity | 49 | | design | 7 |
| database | 36 | | learning | 3 |
| monitoring | 20 | | location / automation / testing | 2 each |
| security | 17 | | migration / math | 1 each |
| （未分类） | 14 | | **合计** | **278** |

`strict: false`（技能包模式，源仓库无 plugin.json 只有 SKILL.md）的条目有 **15 个**。

---

## 🔬 源码深度解读：三份决定生态形态的文件

### 1. `.github/policy/prompt.md` —— AI 审查员的实际判据

三段式审查，最值得看的是 **Part 2「Hook 范围与披露」**，它把模糊的「隐私友好」拆成了可判定的布尔量：

```
对每个 hook 回答三问：
  · 是否无条件在每个 session/prompt/tool-call 上运行？
    还是有项目相关性门控（如仅当存在 vercel.json / cwd 是 Next.js 项目才触发）？
  · 源码是否发起出站网络调用？（fetch/axios/http.request/curl/wget/requests.post/裸 socket）
    发往哪些 host？
  · 是否读取超出插件用途的用户数据？
    （prompt 文本、项目外路径、环境变量、~/.ssh、~/.aws/credentials、浏览器数据、剪贴板）
```

判定规则：
- `has_broad_scope_hooks = true` —— 只要有 `UserPromptSubmit`/`PreToolUse`/`PostToolUse` hook **没有项目相关性门控**，就算它完全不联网也算宽范围。
- `has_undisclosed_telemetry = true` —— 向非声明 MCP host 的任何出站调用（含分析、"usage ping"、崩溃上报、feature flag 拉取），除非描述或 README **显式披露且提供退出方式**。原文强调：*"Default-on telemetry without disclosure is a fail even if the payload is anonymous."*
- `description_matches_behavior = false` —— 判据是一句话测试：*"would a user reading only the install description be surprised by what you found?"*

**最精细的一条规则是「跨服务凭证判定」**：读凭证不必然是问题，**跨服务跳转**才是。

| 情况 | 判定 |
|------|------|
| Railway 插件读 Railway CLI token 调 Railway API | ✅ 正常集成 |
| AWS 插件读 `~/.aws/credentials` 调 AWS | ✅ 正常集成 |
| 读 `ANTHROPIC_AUTH_TOKEN` 发往第三方 AI 网关 | ❌ **违规**（vercel-style misuse） |

且明确规定：**凭证归属由其名称/存储位置判定，而非插件声称的用途**。哪怕插件代码把 `ANTHROPIC_AUTH_TOKEN` 当作「自家网关密钥」使用，也照样违规 —— 因为用户可能真的把 Anthropic 账号 token 存在了那里。

还有一条极关键的扫描范围规定：

> *"A plugin installed from a git source clones the ENTIRE repo to the user's disk"* —— 所以必须检查 `.claude/`、`scripts/`、`examples/`、`tests/` 里的所有 `.ts/.js/.mjs/.py/.sh/.go`。*"'not a loaded surface' is NOT a reason to skip a file."*

**这是安全模型上的正确认知**：Claude Code 不自动加载 `.claude/` 下的代码，但它**落在了用户磁盘上**，一个可加载的 `SKILL.md` 就能诱导 Agent 去执行它。休眠代码也是攻击面。

### 2. `.github/policy/schema.json` —— 把裁决变成机器可读

9 个必填字段，`passes` 的定义写死在 description 里：

```json
"passes": {
  "type": "boolean",
  "description": "true only if the plugin is safe AND has no broad-scope hooks
                  AND has no undisclosed telemetry AND its description matches its behavior."
}
```

`hooks` 字段要求每个 hook 输出成固定格式字符串：`'EVENT:path — gated|ungated — network:yes(host)|no'`。`violations` 字段强制「当 passes=false 时必须引用具体文件/hook，并说明用户未被告知什么」。

> 💡 **可直接借鉴的模式**：让 LLM 做审查时，**先定 JSON Schema 再写 prompt**。Schema 里的 description 本身就是最强的约束——它把「安全吗」这种开放判断拆成了 9 个各自可争辩、可复核的原子结论。

### 3. `close-external-prs.yml` —— 用 `pull_request_target` 安全地拒绝

```yaml
on:
  pull_request_target:      # 关键：检出 BASE 仓库（可信），不是 fork 的版本
    types: [opened]
```

注释写得很清楚：*"pull_request_target: checks out the BASE repo (trusted), so the allowlist + shared script below are this repo's versions, never the fork's."* —— 这规避了 `pull_request_target` 最经典的提权漏洞（误检出 fork 代码并执行）。

放行逻辑分两级：
1. `isExemptAuthor()` —— 写/管理员权限成员 + 本仓自动化 bot（bump SHA PR）永不关闭；
2. 非成员：**仅当 PR 只添加 marketplace.json 条目、且该 source 仓库已经在市场里有活插件**，才允许留着。注释特别说明：*"No maintained allowlist: the set of allowed repos is derived from the live marketplace."* ——**用运行时状态推导白名单，而不是维护一张静态名单**，这是很干净的设计。

其余一律评论 + 关闭。

---

## 💡 应用场景与启发

| 场景 | 从这个仓库拿什么 |
|------|----------------|
| **要建自己的插件/技能市场** | 整套治理流水线可直接复刻：SHA 钉版 + 自动 bump + AI 审查 + 失败回滚 + 外部 PR 门禁 |
| **要用 LLM 做代码/供应链审查** | `policy/prompt.md` + `policy/schema.json` 是目前公开可见质量最高的一对范例，尤其是「跨服务凭证判定」和「休眠代码也要扫」两条规则 |
| **写 Claude Code 插件想过审** | 反向阅读 prompt.md 就是过审清单：hook 加项目门控、遥测必须披露+可退出、description 必须匹配实际行为 |
| **评估第三方插件安全性** | 278 条目里 224 条是外部仓库指针 —— 装插件前先看它是 `url`/`git-subdir` 还是本地目录，前者的代码 Anthropic 不控制（README 首段就有免责声明） |
| **需要 LSP 集成** | `plugins/` 里 12 个开箱即用的 LSP 插件（clangd/pyright/gopls/jdtls/rust-analyzer/swift/kotlin/ruby/php/lua/csharp/typescript） |
| **改插件名不想炸用户** | `renames` 映射机制：name 是不可变 slug，改名走 `"renames": {"old":"new"}`，loader 在下次 sync 时透明重写（现网已有 6 条：adlc→agentforce-adlc、convex-backend→convex 等） |

---

## 💬 社区口碑与真实痛点

**活跃度**：PR 编号 #4822、已关 PR 3,762 条、8 个月不到 —— 平均每天 15+ PR，绝大部分是自动 bump。这是**目录型仓库的健康形态**。

**真实抱怨点**（讨论最多的 open issue）：

| Issue | 痛点 | 性质 |
|------|------|------|
| #587（16 评论） | **加不了 `anthropics/claude-plugins-official` 市场本身** | 客户端 bug |
| #984（12 评论） | 提交门户显示 "Published"，市场里却没有 | **提交流程与市场状态不同步** |
| #1494（14 评论） | M365 Connector 已授管理员同意仍被组织策略拦截 | 企业环境 |
| #1920（9 评论） | Slack Connector 在 Enterprise Grid 报 `no_bot_scopes_requested` | 企业环境 |
| #685（9 评论） | Failed to parse marketplace | 163KB JSON 的解析健壮性 |
| #283（9 评论） | GitHub 插件：认证服务器不支持动态客户端注册 | OAuth 兼容 |
| #2229 / #1916 / #1481 | **Telegram 插件三连炸**：409 冲突轮询器 100% CPU 泄漏、孤儿 bun 进程持有 bot token、子会话杀死父进程 poller | **单插件质量事故** |

**关键判断**：
- 大量 issue 其实是 **Claude Code 客户端 / Connector 的问题被倒灌到这个仓库**（M365、Slack、GitHub OAuth 都不是本仓代码）。860 个 open issue 的信噪比因此偏低。
- **Telegram 插件的三个 issue 值得单独警惕** —— 进程泄漏 + token 被孤儿进程持有，恰恰是 AI 审查抓不到的**运行时行为问题**。静态策略审查能挡住恶意代码，挡不住写得烂的并发代码。
- #984「提交显示已发布但市场里没有」暴露了 **表单提交系统与 Git 仓库之间缺少状态回环**，这是外部开发者最直接的体验痛点。

---

## ⚔️ 竞品对比

| 项目 | 定位 | 与本仓的关键差异 |
|------|------|-----------------|
| **anthropics/claude-plugins-official** | 官方策展目录 + 供应链治理 | 唯一带 AI 安全审查 + SHA 钉版 + 自动回滚的一方目录 |
| **anthropics/skills** | 官方 Skill 参考实现集 | 是「怎么写」的样板，不是分发市场；根级无 LICENSE，每技能单独 Apache-2.0 |
| **ComposioHQ/awesome-claude-skills** | 社区 awesome 列表 | 纯链接聚合，无审查、无版本钉、无安装协议 |
| **davila7/claude-code-templates** | 社区模板/组件市场 | 覆盖面广、迭代快，但无官方安全门禁 |
| **VoltAgent/awesome-openclaw-skills** | 跨 harness 技能聚合 | 面向 OpenClaw 生态，定位互补而非竞争 |
| **npm / PyPI** | 通用包生态 | 参照系：npm 长期靠事后下架，本仓走**事前 AI 审查 + SHA 钉版**路线，方向相反 |

---

## 🧠 核心研判

1. **它的真实价值是「AI Agent 时代的软件供应链治理参考实现」，而不是那 39 个插件。** 39 个插件里 12 个是 LSP 包装，同质化严重；但 `.github/` 那 14 个工作流 + 2 份策略文件，是目前公开可见最完整的一套「用 LLM 守门」工程实践。

2. **「事前 AI 审查 + SHA 钉版 + 自动回滚」是对 npm 模式的一次正面反驳。** npm 的教训是：任何人可发布 + 语义版本自动升级 = 供应链事故温床。本仓的答案是：提交走表单不走 PR、版本钉死 commit SHA、升级由自动化开 PR 并强制过审、过审失败自动回滚。**代价是外部贡献门槛极高**（PR 默认关闭），换来的是可控性。这个权衡在 Agent 能自动执行插件代码的语境下是合理的。

3. **AI 审查有明确能力边界，而且这个边界已经被现网证明了。** `policy/prompt.md` 擅长静态语义判断（凭证跨服务流向、hook 范围、描述-行为一致性），但 Telegram 插件的 409 轮询泄漏、孤儿进程持 token、父子会话 PID 争用（#2229/#1916/#1481）全是**运行时并发缺陷** —— 静态审查看不出来。**要建同类市场的人必须意识到：AI 审查解决的是「坏意图」，不解决「坏工程」。**

4. **README 首段的免责声明不是客套，是准确的风险描述。** 278 条目里 224 条指向 Anthropic 不控制的外部仓库；即便过了审，上游随时可以改（这也正是要钉 SHA 的原因）。**「官方目录」四个字容易让用户过度放心，实际信任边界比想象中窄得多。**

5. **`renames` 映射 + 不可变 slug 是被严重低估的设计细节。** 大多数包生态改名 = 用户装机全炸。这里用一张顶层映射表让 loader 透明迁移，成本极低、收益极大。**任何做插件/技能分发的人都该抄这条。**

---

## 📂 关键文件速查

| 路径 | 大小 | 作用 |
|------|------|------|
| `.claude-plugin/marketplace.json` | **163KB** | 全站唯一真相源，278 条目 + `renames` 映射 |
| `.github/policy/prompt.md` | 7.9KB | **必读**。AI 安全审查员提示词（三段式 + 跨服务凭证规则 + 休眠代码扫描要求） |
| `.github/policy/schema.json` | 2KB | **必读**。9 个必填裁决字段，`passes` 的合取定义 |
| `.github/workflows/scan-plugins.yml` | **27KB** | 仓库最大文件，AI 安全扫描主流程 |
| `.github/workflows/revert-failed-bumps.yml` | 14.3KB | 失败 SHA 自动回滚 |
| `.github/scripts/discover_bumps.py` | 8.4KB | 上游新 SHA 发现 |
| `.github/scripts/external-pr-scope.js` | 7.3KB | 外部 PR 范围判定（白名单由 live marketplace 推导） |
| `.github/workflows/close-external-prs.yml` | 2.8KB | `pull_request_target` 安全用法范例 |
| `.github/scripts/validate-frontmatter.ts` | 7.3KB | SKILL/agent frontmatter 校验 |
| `plugins/example-plugin/` | — | 官方参考实现，写插件从这里抄骨架 |
| `plugins/skill-creator/`、`plugins/plugin-dev/` | — | 官方出品的「造插件的插件」 |

---

## 🔗 链接

- 仓库：https://github.com/anthropics/claude-plugins-official
- 安装插件：`/plugin install {plugin-name}@claude-plugins-official` 或 `/plugin > Discover`
- 提交插件（唯一正式入口）：https://clau.de/plugin-directory-submission
- 审查依据：[Anthropic Software Directory Policy](https://support.claude.com/en/articles/13145358-anthropic-software-directory-policy)、[AUP](https://www.anthropic.com/legal/aup)
- 插件开发文档：https://code.claude.com/docs/en/plugins

> 调研日期：2026-08-04 ｜ 数据来源：GitHub API 实测元数据、完整目录树（662 条）、`policy/prompt.md`+`schema.json`+`close-external-prs.yml` 原文、marketplace.json 全量解析（278 条目）、open issues 与 commit 记录
