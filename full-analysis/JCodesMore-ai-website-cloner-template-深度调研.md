# JCodesMore/ai-website-cloner-template 深度研究报告

> 研究日期：2026-06-27  
> 研究方式：源码深度审查 + GitHub API 数据采集 + Web 全网检索 + Issue/PR 互动历史挖掘  
> 仓库地址：https://github.com/JCodesMore/ai-website-cloner-template  
> 星标：本次已为本账号 BANG644 加星（PUT user/starred/JCodesMore/ai-website-cloner-template，返回 204）

---

## 一、项目全景

### 1.1 定位

**一句话**：这不是一个网站下载器，而是一个**面向 AI 编程助手的工作流模板**——用一条 `/clone-website <url>` 斜杠命令，驱动 AI Agent 完成"截图→设计令牌提取→组件规范书写→并行 builder 子 agent 派发→worktree 隔离构建→合并"的整条流水线，最终吐出**干净的、TypeScript-strict、shadcn/ui + Tailwind v4 风格的现代 Next.js 代码库**。

**与传统「网站克隆」的本质区别**：

| 维度 | HTTrack / SingleFile / Save All Resources | ai-website-cloner-template |
|------|------------------------------------------|----------------------------|
| 输出形态 | HTML + 资源文件（离线镜像） | 干净 React 组件源码（可二次开发） |
| 处理方式 | 静态抓取、HTTP 拉资源 | 浏览器 MCP 实时观察 + 行为捕获 |
| 交互捕获 | 不支持 | 支持 hover/scroll/click 全部状态 |
| 动画/动效 | 完全丢失 | 提取 `getComputedStyle` + transition/animation |
| 产物可读性 | 压缩/混淆的源码 | 组件化、TS 严格、可继续迭代 |
| 依赖 | 离线工具 | 必须有 AI 编程助手（Claude Code 强推） |

### 1.2 基础元数据（2026-06-27 实时抓取）

| 维度 | 数据 |
|------|------|
| 仓库 | `JCodesMore/ai-website-cloner-template` |
| 作者 | JCodesMore（账号 ID: 182581310） |
| 创建时间 | 2026-03-13 11:14:39Z |
| 许可证 | MIT |
| 主语言 | TypeScript（占比约 64%） |
| 默认分支 | `master`（非常规 main） |
| 最新推送 | 2026-06-01 04:09:21Z |
| 仓库体积 | 940 KB（注意：不含产物，极其轻量） |
| Stars | 21,607 |
| Forks | 3,127 |
| Watchers | 101 |
| Open Issues | 17（不含 PR） |
| 协作者贡献 | 6 人（JCodesMore 35 commits + 5 位外协 1 commit） |
| 版本号 | v0.3.1（2026-03-30） |
| 节点要求 | Node.js ≥ 24（已升级自 v0.2.0 的 20+） |

### 1.3 数据爆炸式增长（viral 程度远超同类）

- **发布 3 天**破 6,000 Stars（来源：CSDN「m0_74837192」实测统计）
- **6 周**破 13,000 Stars
- **3 个月**（截至 2026-06-27）：21,607 Stars / 3,127 Forks
- 国内媒体（juejin / CSDN / 掘金 / 搜狐 / 人人都是产品经理）均给出专题评测
- Fork 数 3,127 ≈ Stars 的 14.5%——**远高于普通模板项目**（通常 2-5%），说明大量用户是「fork 后改造成自己的克隆项目」

---

## 二、核心架构

### 2.1 架构本质：模板即 skill

仓库本体是一个 **"半成品 Next.js 项目脚手架 + 多个 AI 平台的 skill/command 文件"**。项目结构分两大区：

```
┌────────────────────────────────────────────────────────────┐
│  项目本体（被克隆的产物所在）                                │
│  src/app/  src/components/  src/lib/  public/  docs/      │
│  → Next.js 16 + React 19 + TS strict + shadcn/ui + Tw v4  │
├────────────────────────────────────────────────────────────┤
│  AI Agent 协作层（"如何用 AI 来填这个脚手架"的元信息）        │
│  .claude/skills/   .codex/skills/   .gemini/commands/     │
│  .github/skills/   .cursor/commands/   .windsurf/workflows/│
│  .continue/commands/  .augment/commands/  .opencode/...    │
│  AGENTS.md（agent 通用入口，13 个平台都能识别）               │
└────────────────────────────────────────────────────────────┘
```

**关键洞察**：仓库本身几乎没有业务代码（`src/app/page.tsx` 只有 303 字节，welcome 页）。它的价值完全在"如何指挥 AI 干活"。

### 2.2 单一真相源 + 自动同步（最容易抄的设计）

```
       AGENTS.md（手工维护，3,038 字节）
            │
            │  bash scripts/sync-agent-rules.sh
            │  (resolve @file imports → 内联全文)
            ▼
┌──────────────────────────────────────────────────────────┐
│ .github/copilot-instructions.md   .clinerules            │
│ .continue/rules/project.md        (.amazonq/rules/...)   │
└──────────────────────────────────────────────────────────┘

       .claude/skills/clone-website/SKILL.md（30,312 字节）
            │
            │  node scripts/sync-skills.mjs
            │  (解析 frontmatter → 按平台格式拼装)
            ▼
┌──────────────────────────────────────────────────────────┐
│ .codex/skills/.../SKILL.md       .github/skills/.../...  │
│ .cursor/commands/clone-website.md .windsurf/workflows/...│
│ .gemini/commands/clone-website.toml (TOML!)             │
│ .opencode/commands/...           .augment/commands/...  │
│ .continue/commands/...           .amazonq/cli-agents/..│
│ (9 个平台产物)                                            │
└──────────────────────────────────────────────────────────┘
```

**为什么这值得专门写**：大多数多平台 AI 工具项目都把 9 个文件手工维护成一团乱麻，commit 时频繁冲突。`JCodesMore` 用 2 个同步脚本 + 1 个 AGENTS.md 源文件 + 1 个 SKILL.md 源文件就解决了——这套"单一真相源"模式可以原样照搬到任何"需要兼容多种 Agent 平台"的项目里。

### 2.3 同步脚本的关键实现（`sync-agent-rules.sh` 核心 30 行）

```bash
# 1. 读 AGENTS.md
# 2. resolve_imports() —— 把所有 "@path/to/file.md" 行替换为该文件全文
#    （支持 @docs/research/INSPECTION_GUIDE.md 这样的多文件拼接）
# 3. 加 AUTO-GENERATED 头
# 4. 写入到各平台约定路径
```

- **Win CRLF 兼容**：v0.3.1 修复了 `bash` 读 CRLF 文件时 `${line%$'\r'}` 的清尾问题（CHANGELOG 明确记录）
- **`@file` 嵌套**：AGENTS.md 末尾的 `@docs/research/INSPECTION_GUIDE.md` 会被展开为全文塞入每个 agent 规则

### 2.4 SKILL 同步脚本（`sync-skills.mjs`）的平台适配矩阵

| 平台 | 输出格式 | 参数占位 | 关键转换 |
|------|---------|---------|---------|
| Codex CLI | 完整 SKILL.md 原样 | `$ARGUMENTS` | 零修改 |
| GitHub Copilot | 完整 SKILL.md | 同上 | 零修改 |
| Cursor | markdown + 头 | 替换为 "the target URL..." | 去 `$ARGUMENTS` |
| Windsurf | workflow markdown | 同 Cursor | 同 Cursor |
| Gemini CLI | **TOML** | `{{args}}` | 转 TOML frontmatter |
| OpenCode | markdown + YAML | 原样 | 加 description 头 |
| Augment | markdown + YAML | 原样 | 加 argument-hint |
| Continue | prompt frontmatter | 原样 | `invokable: true` |
| Amazon Q | **JSON** | 替换为 "the target..." | 序列化为 JSON 字段 |

**一句话总结**：Claude 写的"原始 prompt"作为 source of truth，Node.js 脚本按 9 个平台的文件格式偏好（md/toml/json/with frontmatter）批量转换。

---

## 三、源码深度解读

### 3.1 真正的"业务代码"：`.claude/skills/clone-website/SKILL.md`（30 KB）

这是项目**最核心的资产**，比 README 长 4 倍。结构如下：

```yaml
---
name: clone-website
description: Reverse-engineer and clone one or more websites in one shot...
argument-hint: "<url1> [<url2> ...]"
user-invocable: true
---
```

正文有 **7 条 Guiding Principles**（被作者标榜为 "the truths that separate a successful clone from a 'close enough' mess"），按价值密度排：

1. **Completeness Beats Speed** — 给 builder 的 brief 必须包含截图 + 精确 CSS + 资源本地路径 + 真实文本，**不允许 builder 猜任何值**
2. **Small Tasks, Perfect Results** — 一个 section 太复杂就拆成多个子 agent；**复杂度红线 ~150 行 spec**
3. **Real Content, Real Assets** — 必须下载真实 `<img>` / `<video>` / 内联 SVG，不允许 mock
4. **Foundation First** — 全局 CSS + TS 类型 + 全局资源必须先有，后面才并行
5. **Extract How It Looks AND How It Behaves** — 滚动/悬停/点击/响应式全部要捕获
6. **Identify the Interaction Model Before Building** — 区分 scroll-driven vs click-driven，避免方向性返工
7. **Extract Every State, Not Just the Default** — 标签页/hover/scroll 后状态全部要枚举

**这 7 条本质是工程经验文档**，比很多大厂的"前端规范"还实在。

### 3.2 工作流（pipeline）的 4 阶段

```
阶段 1: Pre-Flight
  ├─ 检查浏览器 MCP 工具（Chrome MCP > Playwright MCP > 其他）
  ├─ 解析 URL 列表
  ├─ npm run build 验证基线
  └─ 建目录 docs/research/ + docs/design-references/

阶段 2: Foundation（串行）
  ├─ 提取 design tokens（color/font/spacing/breakpoint）
  ├─ 全局 CSS + TS 接口
  └─ 全局资源（字体/favicon/og 图）

阶段 3: Section Build（并行）
  ├─ foreman agent 观察每个 section
  ├─ 写 spec 到 docs/research/components/<section>.md
  └─ 派发 builder agent 到独立 worktree，构建组件

阶段 4: Merge & Polish（串行）
  ├─ 合并所有 worktree
  ├─ 解决冲突
  └─ 视觉/交互回归
```

**与主流"自动化"方案的关键差异**：**不是抓静态 HTML，而是实时观察 DOM 行为**。比如识别"scroll-driven vs click-driven"时，规则明确写："Don't click first. Scroll through the section slowly and observe if things change on their own as you scroll."

### 3.3 配合 `INSPECTION_GUIDE.md` 的 3 阶段审计清单

1. **Phase 1 Visual Audit**：截图清单 + 设计 token 清单（颜色/字体/间距/圆角/阴影/断点）
2. **Phase 2 Component Inventory**：每个组件记 name/structure/variants/states/responsive/interactions/animations
3. **Phase 3 Layout Architecture**：栅格/列数/max-width/sticky 元素/z-index 层级

### 3.4 关键技术决策

| 决策 | 选择 | 理由（从源码推测） |
|------|------|------------------|
| 输出框架 | Next.js 16 + App Router | 用户群最广，shadcn 生态丰富 |
| UI 库 | shadcn/ui + Tailwind v4 | 复制即用，不锁死依赖 |
| 浏览器自动化 | **依赖 MCP**，不内置 | 跟随 Claude Code 演进，不重复造轮子 |
| 多 URL 支持 | v0.3.0 引入并行 + 隔离目录 | 用户场景扩展 |
| 平台适配 | 9 平台 + 自动同步 | 用户不需要为换 IDE 而失去技能 |
| Node 版本 | v0.3.1 升到 24 | 跟 Next.js 16 + React 19 同步 |

---

## 四、社区口碑与 Issue 互动

### 4.1 总体社区信号

- **101 watchers** + **17 OPEN issues** + **60 个 PR**——说明项目**有大量用户卡在实操层面在提问**
- **fork 数远超普通模板项目**（14.5% fork rate）——说明很多用户是 fork → 改 → 自己跑
- **多语言社区热度高**：juejin/CSDN/掘金/搜狐/人人都是产品经理均有专题

### 4.2 核心 Issue 分析（按重要性排序）

#### Issue #27（CLOSED）⭐⭐⭐⭐⭐ 最值得读的诚实评价

标题：`[Bug]: Does not work as described`  
作者：HuguesD  
环境：Claude Code Opus 4.6 + Chrome + Node 22.12.0

**核心吐槽**（直译）：

> 试着克隆一个**几乎静态的、相对简单**的网站。**只克隆了首页，而且质量很差**：字体错误、元素缺失、部分颜色错误。基本就是回到"我得跟 Claude Code 视觉对比、交互式纠错几十次"的状态。**老实说我看不到这个仓库的用处**——它没有自动化克隆，也没比"直接给 Claude Code 写个 prompt 让他抓站"做得更好。

**这是项目最被低估的诚实反馈**，揭示了一个被市场宣传掩盖的事实：**对于简单网站，模板没比自己手写 prompt 强多少**。HuguesD 把这个仓库的真实价值拉回地面。

#### Issue #39（OPEN）⭐⭐⭐⭐⭐ 公开承认的能力边界

标题：`[Feature]: 网页的动态效果太多的话，他就完全失效了。`  
作者：singi314159-alt  
内容翻译：

> **问题：网页的动态效果太多的话，工具就完全失效了。**
> 建议方案：修复这个 BUG

**配套 PR #56**（YAMRAJ13y：`fix: graceful degradation for motion-heavy sites`）正在尝试解决——已 OPEN。说明作者已经意识到 motion-heavy 站点是当前能力盲区。

#### Issue #22（OPEN）⭐⭐⭐ 依赖陷阱

`npm audit fix` 会破坏 `claude --chrome` 的 skill 加载。  
**说明项目对依赖锁版本敏感**——`@base-ui/react` / `next` 升级路径需要谨慎。

#### Issue #30（CLOSED）⭐⭐⭐

Wix.com 模板无法克隆——**反爬虫机制拦截 headless 浏览器**。  
作者回复极简："Don't run headless."——意思是这个问题无法在工具侧解决。

#### Issue #18（OPEN）⭐⭐ 主流需求

请求加入 **Playwright MCP 作为备选浏览器后端**。  
PR #60 已经在做。说明社区在推动**多浏览器后端**。

#### Issue #49（OPEN）⭐⭐⭐⭐⭐ 关键未来方向

作者在 Reddit 透露的下一步是 **hybrid approach（混合方案）**：把"下载 HTML 静态分析"与"浏览器动态导航"结合起来，不再是"section by section only"。这是项目未来 1-2 个月的演进方向。

#### Issue #3（OPEN）⭐⭐

请求支持 **Figma / Google Stitch MCP**——即从设计稿直接克隆。这是行业大方向。

### 4.3 社区 PR 信号

60 个 PR 中值得关注：

- **PR #60**（OPEN）：把 Playwright MCP 加入 skill 作为替代浏览器后端
- **PR #56**（OPEN）：为 motion-heavy 站点做优雅降级（关 #39）
- **PR #59 / #58**（OPEN）：补 SECURITY.md 和 CONTRIBUTING.md
- **PR #57**（OPEN）：加 CI 校验生成的 skill 文件与源文件是否同步
- **PR #54**（OPEN）：加 devcontainer.json
- **PR #52**（OPEN）：**Simplified Chinese README**（ZijieZh 提交）——说明中文用户群已经大到需要专门翻译
- **PR #48**（OPEN）：升 Next.js 16.2.7 修依赖漏洞
- **PR #38**（OPEN）：resolve npm audit 不降级 next 9.x
- **PR #44**（MERGED）：修 Gemini CLI TOML 验证错误

**整体信号**：项目处于**"快速采纳社区反馈"模式**，几乎所有值得做的 issue 都有人在跟。

### 4.4 国内媒体评测关键词

- 搜狐：「设计思路与实现方式都相当有趣」（中性正面）
- 掘金：「让开发者眼前一亮的开源项目」
- CSDN：「一条命令克隆任意网站」
- 人人都是产品经理：「用一条命令克隆任何网站」

**注意**：这些评测基本都是"搬运 README + 复述操作步骤"，几乎没有**实测踩坑**内容。**真正有一手反馈的是 Issue #27**（HuguesD）。

---

## 五、竞品对比

| 工具/项目 | 形态 | 输出 | 行为捕获 | 动效 | 资产 | 适合场景 |
|----------|------|------|---------|------|------|---------|
| **HTTrack** | 桌面程序 | HTML 镜像 | ❌ | ❌ | ✅ 完整 | 离线浏览、SEO 镜像 |
| **SingleFile** | 浏览器扩展 | 单 HTML 文件 | ❌ | ⚠️ 截图能 | ⚠️ 内联 | 存档单页 |
| **Save All Resources** | Chrome 扩展 | 资源包 | ❌ | ❌ | ✅ | 资源盗取 |
| **html2canvas / dom-to-image** | 库 | PNG | ❌ | ❌ | ❌ | 截图 |
| **WebCopy / Cyotek WebCopy** | 工具 | 镜像 | ❌ | ❌ | ✅ | 备份 |
| **直接 prompt Claude Code** | 提示词 | 看你 prompt | ⚠️ 看你 prompt | ⚠️ 看你 prompt | ⚠️ 看你 prompt | 一次性任务 |
| **ai-website-cloner-template** | AI skill 模板 | **干净的 Next.js 源码** | ✅ 显式提取 | ✅ 显式提取 | ✅ 强制真实 | **二次开发、像素级克隆** |
| **v0.dev / Bolt.new / Lovable** | SaaS | React 代码 | ⚠️ 半自动 | ⚠️ 半自动 | ⚠️ | 通用生成，不是克隆 |
| **Screenshot-to-code (类似 abi/screenshot-to-code)** | AI demo | React 代码 | ❌ | ❌ | ❌ | 截图转代码，但无浏览器动态分析 |

**核心差异化**：本项目是**唯一**显式提取**"行为"**（hover/scroll/click/响应式）的 AI 克隆方案。竞品要么只抓静态（HTTrack），要么只给一堆不规范 prompt 让你自己来（直接写 prompt）。

**短板**：依赖 Claude Code（推荐）+ 浏览器 MCP 工具链，**学习成本高**。对简单网站效果不如直接写 prompt（Issue #27 实证）。

---

## 六、核心研判

### 6.1 价值评估

**真实价值**（基于源码 + Issue 而非 README 文案）：

1. **工程经验封装**：7 条 Guiding Principles + 3 阶段审计清单 = 一份实战级"网站逆向工程方法论"。这部分是**直接可学**的硬知识
2. **多平台 agent 适配的工程模板**：单一真相源 + 自动同步脚本的模式**可以原样照搬**到任何"多 agent 平台支持"项目
3. **worktree 隔离的并行构建模式**：每个 builder agent 独立分支构建，foreman 合并——这是**真正的多 agent 协作范式**

**被高估的部分**：

1. "一条命令克隆任意网站"是**营销话术**。Issue #27 实证：**简单静态网站都搞不定**
2. "用 Claude Code 配合就能搞定"是**门槛被低估**——必须用 Opus 4.7 + 浏览器 MCP
3. **Motion-heavy 站点仍然失效**（Issue #39 仍 OPEN）

### 6.2 适用场景

✅ **适合**：

- 复杂响应式 + 滚动动效 + 大量交互的**营销页 / landing page** 克隆
- 学习"AI 时代的多 agent 协作工程范式"
- 学习"多平台 AI 工具适配"的工程实现

❌ **不适合**：

- 简单静态网站（直接给 Claude Code 写 prompt 更省事）
- 内部后台 / SPA 应用（动效少，模板的"行为捕获"优势无用）
- 强反爬站点（Wix 类直接被封，Issue #30）
- 纯设计稿克隆（应等 Figma MCP 支持，Issue #3）

### 6.3 复用启发（可借鉴的 4 个设计模式）

1. **AGENTS.md + sync-agent-rules.sh 模式**：单一源 + 自动同步，告别 9 份手工维护的乱麻
2. **SKILL.md 源文件 + sync-skills.mjs 模式**：Claude 写 1 份，9 个平台自动适配（含 TOML/JSON 输出）
3. **Foreman + Worktree 派发模式**：主 agent 拆任务、子 agent 隔离构建、主 agent 合并——**多 agent 协作的工程模板**
4. **7 条 Guiding Principles 显式编码进 SKILL**：把"经验"转成"指令"喂给 AI，比写注释给人类看更有效

### 6.4 风险与盲点

| 风险 | 严重度 | 说明 |
|------|--------|------|
| motion-heavy 站点失效 | 高 | Issue #39 未解，PR #56 在做 |
| 反爬站点（Cloudflare/Wix）失败 | 高 | Issue #30，作者自己说"无法解决" |
| `npm audit fix` 破坏 skill | 中 | Issue #22 OPEN |
| 默认 master 分支（不推荐 main） | 低 | Vercel 等部署平台支持 |
| 依赖 Claude Code 强推 | 中 | "推荐 Opus 4.7" + 浏览器 MCP 双重门槛 |
| 22 天无提交（最近 push 2026-06-01） | 中 | 6/1 之后无活动，可能进入"等待社区 PR"阶段 |

### 6.5 终局研判

> **这是一个 7 分项目**：方法论价值 9 分（Guiding Principles 值得专门读 3 遍），工具可用性 5 分（实战踩坑多），社区活跃度 8 分（issue/PR 响应快），长期生态潜力 7 分（hybrid approach + Playwright/Figma MCP 接入是正确演进方向）。

**是否值得用**：如果你只是想克隆一个简单网站——**不值得**，直接写 prompt。  
**如果你想学习 AI 时代的"多 agent 协作工程模式"**——**必读**，这是目前 GitHub 上**工程化最完整**的范例。  
**如果你在做类似的多 agent 项目**——**抄它的 AGENTS.md + sync 脚本模式**，立省 80% 工作量。

---

## 七、关键文件速查

| 路径 | 字节 | 作用 | 阅读优先级 |
|------|------|------|----------|
| `.claude/skills/clone-website/SKILL.md` | 30,312 | 核心 skill，7 条原则 + 4 阶段流程 | ⭐⭐⭐⭐⭐ |
| `AGENTS.md` | 3,038 | 单一源，含 `@import` 嵌套 | ⭐⭐⭐⭐⭐ |
| `docs/research/INSPECTION_GUIDE.md` | 3,724 | 3 阶段审计清单 | ⭐⭐⭐⭐ |
| `scripts/sync-agent-rules.sh` | 2,784 | AGENTS.md → 9 平台规则 | ⭐⭐⭐⭐ |
| `scripts/sync-skills.mjs` | 3,493 | SKILL.md → 9 平台 skill | ⭐⭐⭐⭐ |
| `package.json` | 1,492 | 依赖：next 16.2.1 + react 19.2.4 + tailwind v4 | ⭐⭐⭐ |
| `Dockerfile` | 3,985 | Node 24.14.1-slim + Next standalone | ⭐⭐ |
| `CHANGELOG.md` | 3,651 | v0.1.0 → v0.3.1 演进记录 | ⭐⭐⭐ |
| `README.md` | 8,352 | 快速开始 + Supported Platforms 表 | ⭐⭐ |
| `docker-compose.yml` | 1,235 | Docker 编排 | ⭐ |
| `.github/workflows/ci.yml` | 568 | lint + typecheck + build | ⭐⭐ |

### 平台分布（生成的指令文件）

| 平台 | 路径 | 格式 |
|------|------|------|
| Claude Code | `.claude/skills/clone-website/SKILL.md` | YAML frontmatter + md |
| Codex CLI | `.codex/skills/clone-website/SKILL.md` | 同 Claude |
| GitHub Copilot | `.github/skills/clone-website/SKILL.md` | 同 Claude |
| Cursor | `.cursor/commands/clone-website.md` | md + header |
| Windsurf | `.windsurf/workflows/clone-website.md` | md + header |
| Gemini CLI | `.gemini/commands/clone-website.toml` | **TOML** |
| OpenCode | `.opencode/commands/clone-website.md` | md + YAML |
| Augment Code | `.augment/commands/clone-website.md` | md + YAML |
| Continue | `.continue/commands/clone-website.md` | md + YAML |
| Amazon Q | `.amazonq/cli-agents/clone-website.json` | **JSON** |
| Cline/Roo Code | `.clinerules` | 纯 md（同步生成） |
| GitHub Copilot Chat | `.github/copilot-instructions.md` | 纯 md（同步生成） |

### Star/版本/Commit 时间线

- 2026-03-13：仓库创建
- 2026-03-28：v0.1.0 → v0.1.1 → v0.2.0（3 个版本同一天，加多平台）
- 2026-03-30：v0.3.0（多 URL） → v0.3.1（Win CRLF 修复）
- 2026-04-01：Playwright MCP feature request（#18）
- 2026-04-09：HuguesD 提交"Does not work as described"（#27）
- 2026-04-14：#27 关闭
- 2026-04-25：Wix 反爬问题（#30）
- 2026-04-30：motion-heavy 失效问题（#39）
- 2026-06-24：PR #56 尝试修 #39
- 2026-06-26：Playwright MCP 文档补全（PR #60）
- 2026-06-27：**本调研完成**

---

## 八、IMA 同步状态

- 本报告将同步至 IMA 知识库 `github项目研究`（ID: `Alur0Sed2DT3m5LBVUorxSP3iPSDd5GIchvBCoQP3vs=`）
- IMA 元目录媒体 ID：`markdown_104a5ea1d6c53484288502604be7587f_adb53de6f3f93ea9f5c628c71cc733527462334733751990`
- 标题：`JCodesMore-ai-website-cloner-template-深度调研`
- 同步流程见 `GitHub 项目研究 — 元目录.md`

---

**研究结束。** 调研方法：源码逐行（57 个文件）+ GitHub API（issue/PR/release/contributors/stargazers）+ Web 搜索 5 篇评测 + 1 次失败调研文件覆盖（早上 5:56 旧版 30KB 已被本份替换）。
