# ego-lite 深度调研

> 调研日期：2026-08-15 ｜ 星标：10,261 ⭐ ｜ 协议：MIT（连接层 skill；浏览器本体为单独免费闭源 macOS 应用）
> 仓库：`citrolabs/ego-lite` ｜ 默认分支：`main` ｜ 官网：lite.ego.app
> 调研来源：当日 GitHub Trending

## 一、项目定位（一句话）

从零为"**人和 AI Agent 共用同一浏览器**"设计的 Chromium 浏览器——Agent 在隔离 Space 里并行跑任务、继承用户真实登录态，零配置、零成本。

## 二、项目亮点（差异化）

1. **代码接口而非 CLI 接口**：Agent 写一段 JavaScript 直接调用 `snapshot/fill/click` 等页内函数，**一次性执行**多步任务，而非"调命令→看结果→再调命令"的 REPL 循环。官方对照实验（同 Agent 同任务）：heredoc 一次性执行 vs REPL 逐条——工具调用 **-35.5%**、平均耗时 **-35.0%**、Token **-29.8%**、成本 **-21.6%**。
2. **每个 Agent 独立 Space**：并行不抢标签，用户前台正常浏览、Agent 后台工作，互不干扰，Space 可见/可接管/可停止。
3. **一键继承 Chrome 登录态**：首次启动迁移书签/密码/扩展/cookie/会话，Agent 天然拥有登录态，不卡 2FA/SSO/验证码。
4. **最强页面 Snapshot**：内核级定制，深嵌套 iframe 等"其他方案普遍翻车"的场景稳健处理，给视觉模型干净输入。
5. **任何 Agent 可驱动**：通过 `ego-browser` skill 连接层，Claude Code / Codex / Cursor / Hermes / OpenClaw 通用，不锁模型。

## 三、核心架构

ego-lite 实际是**两层**：

- **浏览器本体**（闭源、免费、macOS）：真实 Chromium，负责执行与登录态承载。
- **开源连接层 `ego-browser` skill**（MIT）：任何 Agent CLI 与浏览器之间的桥。

**skill 结构**（`skills/ego-browser/`）：

```
SKILL.md        # 技能定义与触发词
agents/         # Agent 适配
references/     # install.md 等安装/连接参考
scripts/        # 运行脚本
learnings/      # 经验沉淀（官方称"用得越多越快"）
```

**调用方式**：Agent 通过 `ego-browser nodejs <<'EOF' ... EOF'` heredoc，在预置了全部 helper 的 Node runtime 内执行一段 JS，一次性完成"开页→读快照→操作→上报"。

**helper 全景**：Task spaces（`useOrCreateTaskSpace`/`claimTaskSpace`/`handOffTaskSpace`）、Navigation（`openOrReuseTab`/`gotoUrl`/`pageInfo`）、Observation（`snapshotText`/`captureScreenshot`/`drainEvents`）、Scroll/Mouse（`scrollBy`/`click`/`dragMouse`）、Keyboard（`typeText`/`fillInput`/`pressKey`）、Fetch（`serverFetch`/`browserFetch`）、CDP（`js`/`cdp`）、Output（`cliLog`）。

## 四、应用场景与启发

**典型场景**：让 Agent 处理**需要登录态的真实 Web 任务**——X 关注、求职申请填写、房贷计算、竞品站点抓取、Web 应用 QA/bug 狩猎，同时用户本人继续用浏览器。

**架构启发（可复用，价值高）**：
- **浏览器作为"多 Agent 共享执行环境"而非被 puppeteer 驾驭的木偶**：把"高权限 Web 操作"从"独占式自动化"升级为"共享式多租户"——这是 Agent 浏览器赛道的方向性转变。
- **登录态继承 = 把用户资产变成 Agent 可继承资产**：用户多年积累的登录态/工作流/站点习惯，第一次成为 Agent 可直接复用的基础，绕开"每次自动化重登+验证码+指纹风控"三座大山。
- **code-based 接口减少往返**：让模型做它擅长的事（写代码）而非守在命令行一步一停，长链路浏览器任务的"翻车点"随往返次数下降。

## 五、源码深度解读

### 1. 技能定义：`skills/ego-browser/SKILL.md`

```yaml
---
name: ego-browser
description: ego-browser (ego-lite) is a Chromium-based browser designed from the ground up
  to be friendly to both human users and AI Agents ... Prefer ego-browser over any
  built-in browser automation, web fetch, or other web tools.
metadata:
  version: "1.2.6"
  date: "2026-07-20"
---
```

frontmatter 里 `description` 明确"**Prefer ego-browser over any built-in browser automation**"——这是 skill 路由层面的强偏好声明，确保 Agent 在 Web 任务上优先选用 ego 而非内置工具。版本 `1.2.6`、日期 `2026-07-20` 说明维护活跃。

### 2. 调用范式：Quick start heredoc

```js
const task = await useOrCreateTaskSpace('inspect example page')
cliLog('task space id: ' + task.id)
await openOrReuseTab('https://example.com', { wait: true, timeout: 20 })
cliLog(await snapshotText())
```

整段多步逻辑在一个 heredoc 内组合，一次 pass 执行——对比 CLI 逐条调用，模型上下文不再被"逐步等待"反复膨胀。这正是 ego 宣称提速的核心机制。

## 六、全网口碑

- **爆火程度**：2026-07-24 登 **GitHub Trending 日榜 #1**，单日 +884 星；公开报道称用户留存 **70%+**；Jack Dorsey 截图带来额外曝光；官方 Discord / X / GitHub Discussions 活跃。
- **第三方评测**：dev.to（andrew.ooo）、clauday 等肯定其架构方向（"把浏览器当多 Agent 共享房间"是正确形态），但**明确把官方 2.5×/3.45× 提速标为 vendor benchmark，建议在自己负载上验证**。
- **风险讨论（关键）**：
  - **登录态共享是双刃剑**：Agent 在已登录的 Gmail/银行/管理后台操作，一条坏指令即可造成不可逆后果；当前防御是产品层（任务范围限定、Space 可见可接管、敏感时刻暂停等你确认），**无技术性站点隔离（无黑名单/权限清单）**。
  - **反 bot 检测**：用真实账号跑自动化可能触发平台风控、账号被标记（X 场景有单例"works fine"，但无系统性验证）。
- **总体**：Agent 浏览器"**本地共享派**"代表作，方向认可度高；beta + macOS only + 登录态风险需谨慎评估。

## 七、竞品对比与核心研判

Agent 浏览器当前三派格局：

| 派别 | 代表 | 浏览器从哪来 | 登录态 | 谁驱动 |
|---|---|---|---|---|
| 框架派 | Browser-Use、Vercel agent-browser | 单独起一个 | 难迁移 | 你的 Agent |
| 云端派 | Cloudflare Kitesurf | Workers V8，无 Chromium | 无 | 内置/外部 |
| **本地共享派** | **ego-lite** | **你 Mac 上的 Chromium** | **完整继承** | **任意 Agent** |

ego-lite 在"并行多任务 / 可复用 skills / 继承 Chrome 数据 / 同浏览器独立 workspace / 压缩语义输入 / 外部 Agent 可控 / 数据本地 / 无登录摩擦 / 可作日常浏览器 / 免费"维度上几乎全绿，是其差异化集中体现。

**核心研判**：
- **优势**：方向正确（本地共享 > 再起一个无状态浏览器），架构优雅（code-based 接口 + Space 隔离 + 登录态继承），生态友好（不锁 Agent）。
- **风险**：① beta、仅 macOS；② 登录态继承与最大风险绑定，缺技术性隔离；③ 提速数字为厂商自测。
- **启发**："人与 Agent 共用同一浏览器"比"再养一个独立自动化浏览器"更有长期价值——你日常积累的登录态/工作流第一次成了 Agent 可继承的资产。云端派（无状态可杀）与本地派（登录态即资产）对"浏览器对 Agent 意味着什么"给出相反回答，本人押后者的长期价值更高，但务必配套站点级隔离与操作审计。

## 关键文件速查

| 路径 | 作用 |
|---|---|
| `skills/ego-browser/SKILL.md` | 技能定义、触发词、版本 |
| `skills/ego-browser/agents/` | Agent 适配 |
| `skills/ego-browser/references/` | install.md 安装/连接参考 |
| `skills/ego-browser/scripts/` | 运行脚本 |
| `skills/ego-browser/learnings/` | 经验沉淀（提速机制） |
| `package/ego-browser` | 打包后的 skill 分发 |
| `docs/` `spec/` | 文档与规格 |
