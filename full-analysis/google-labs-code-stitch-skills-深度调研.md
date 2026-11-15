# 🔬 google-labs-code/stitch-skills - 全方位深度调研

> 调研日期：2026-11-16 ｜ 数据源：GitHub API（仓库/Issue/Release/源码）+ 全网口碑检索
> ⚠️ 本报告只写 README 之外的判断。基础安装命令、插件清单请直接看官方 README。

## 📌 一句话定位

Google Labs 出品的 **「设计→代码」Agent Skills 集合**：把 Google Stitch（谷歌的 AI UI 设计工具）的 MCP 工具能力，包装成一套有强制流程、有机器校验、可跨 6 种编码 Agent 复用的标准技能包——让 Agent 按固定顺序调用 Stitch，把设计稿稳定翻译成 React/React Native/Vite 工程，并把设计令牌（design token）同步回来防止设计漂移。

一句话点破本质：**MCP 给了 Agent「工具」，这套 skills 给了 Agent「工序 + 质检」**——这是它区别于「裸接一个 MCP」的核心价值，也是它的全部风险来源（强耦合 Stitch）。

## ⭐ 项目亮点

1. **GATE 关卡式强约束**：每个 SKILL.md 用 `MANDATORY` + `GATE` 把流程切成带门禁的阶段（如 Phase 1 必须下载并肉眼审查每张截图才准进 Phase 2），并用「Anti-patterns」列出禁止动作。这不是建议清单，是给 Agent 的行为契约——**把「提示词工程」升级成「可验收的SOP」**。
2. **AST 级机器校验，而非正则**：`validate.js` 用 `@swc/core` 真正解析 TSX 抽象语法树，检查每个组件是否有 `XxxProps` interface、`className` 里有没有硬编码 hex 色值。让「每个组件必须有 Props 类型」「禁止硬编码颜色」这类规范从纸面规则变成 `npm run validate` 可判定的硬约束。
3. **系统级高可靠下载脚本**：`fetch-stitch.sh` 用 `curl -L -f -sS --compressed` 处理 Google Cloud Storage 的重定向/TLS/SNI 握手——因为「内部 AI fetch 工具在 GCS 域名会失败」。这是一个非常实用的经验：**Agent 的内置网络工具不可靠时，把下载下沉到系统 curl 脚本**。
4. **DESIGN.md / style-guide.json 作为「设计—代码」中间契约**：强制从当前项目 HTML `<head>` 的 `tailwind.config` 抽取颜色/字体/间距，回写 `resources/style-guide.json`，并明确「上一个项目的 token 不可接受」——用中间产物把设计系统的漂移显性化。
5. **跨 6 种 Agent 的可移植性**：遵循 agentskills.io 开放标准（SKILL.md + scripts/ + resources/ + examples/），同一套文件夹可被 Codex / Antigravity / Gemini CLI / Claude Code / Cursor 加载，OpenCode 需手动改名。三个插件（design/build/utilities）可独立安装。

## 🏗️ 项目架构全景

### 目录即架构：三层插件 + marketplace 入口

```
.agents/plugins/marketplace.json     # Codex marketplace 注册入口，声明 3 个本地插件
plugins/
├── stitch-design/    # 创意层：generate-design / code-to-design / extract-design-md /
│                     #        extract-static-html / manage-design-system / upload-to-stitch
├── stitch-build/     # 编译层：react-components / react-native / react-vite-dashboard /
│                     #        remotion / shadcn-ui   （每个 skill 含 scripts + resources + examples）
└── stitch-utilities/ # 打磨层：enhance-prompt / stitch-loop / taste-design / design-md / site-md
```

**设计哲学：单向数据流 + 关注点分层**。`marketplace.json` 里每个插件带 `policy: {installation: AVAILABLE, authentication: ON_INSTALL}` 和 `category: Productivity`，即「安装时鉴权、按插件灰度」。设计层技能读本地输入（前端源码/运行中的 URL/图片）写入 Stitch；构建层技能读 Stitch 屏幕写回代码。MCP server 持有凭证与项目状态，skill 持有「工序」。

### 技术栈 & 依赖图谱

- **主体是 Markdown**：16 个 SKILL.md 是核心，TypeScript 只用于少量脚本（如 `extract-inline_html.ts`），shell/python 用于下载与上传（`fetch-stitch.sh` / `upload_to_stitch.py`）。
- **运行时依赖**：Stitch MCP server（前置必需）+ 各 skill 声明的 `allowed-tools`（`stitch*:*` / `Bash` / `Read` / `Write` / `web_fetch`）。
- **验证依赖**：`@swc/core`（AST 解析）、`tailwind.config`（token 来源）。注意第三方测评发现 **19 个脚本中有 2 个依赖未 pin 版本**（aigrowthrank 安全审查），这是供应链隐患。

## 💡 应用场景与启发（重点章节）

### 典型使用场景

- **团队用 Stitch 做 UI 探索**，需要把认可的屏幕稳定转成生产级 React 组件树——且希望二次同步时能对齐最新设计版本，而不是每次手工重做 token 映射。
- **设计系统治理**：把已有前端代码反向抽取成 `DESIGN.md` 并托管到 Stitch 的 design system，让「设计规范」变成Agent可读、可校验的中间产物。
- **多页面站点生成**：`stitch-loop` 用一个 prompt 驱动多页站点，配 `baton-schema` 在页面间传递上下文。

### 可借鉴的解决方案模式（最具迁移价值）

1. **「MCP 给工具，Skill 给工序」的分层**：任何接了 MCP/工具集的 Agent 系统，都可以照这个思路把「先调 A、再调 B、拿到结果必须肉眼/机器校验」写成 skill。工具能力 ≠ 正确使用工具的能力。这个模式可以直接迁移到你自己的 Agent 工具链设计。
2. **GATE + Anti-patterns 的提示词结构**：每个阶段写明「完成条件」+「禁止动作」，把模糊的自然语言指令变成可判定的状态机。写任何复杂 Agent 工作流 SOP 都可以套这个模板。
3. **把规范编译成校验器**：「组件要有 Props interface」「不许硬编码颜色」——与其在提示词里反复强调，不如写一个 AST 校验脚本让不合格代码直接 fail。这是「规范 → gate」的工程化思路。
4. **不可靠 I/O 下沉到系统脚本**：Agent 内置 fetch 处理不了 GCS 签名 URL 的重定向，就用 `curl -L --compressed` 脚本兜底。凡是 Agent 环境里网络/文件操作不稳，优先想到写一个确定性的 shell 脚本。

### 同类需求的可参考思路 / 可复用片段

- `fetch-stitch.sh`（20 行）可直接改造为任何「下载带签名的云存储 URL」的通用兜底脚本。
- `validate.js` 的 AST walk 模式（`TsInterfaceDeclaration` 判定 + `JSXAttribute` 判定）可作为「代码风格门禁」的模板，换成 eslint/oxlint 规则也成立。
- **反面教材**：技能间有依赖，选择性安装（`npx skills add` 单装）可能因为缺依赖而流程断裂——设计技能体系时要显式声明依赖图。

## 🧠 核心源码解读（克制代码量）

### 入口：marketplace.json 的插件声明

```json
{ "name": "stitch-design",
  "source": { "source": "local", "path": "./plugins/stitch-design" },
  "policy": { "installation": "AVAILABLE", "authentication": "ON_INSTALL" },
  "category": "Productivity" }
```
三个插件同一结构——把「鉴权时机」和「分类」下沉到 marketplace 元数据，Agent 安装时据此决策，无需读 SKILL.md 正文。

### 关键模块一：validate.js 的 AST 门禁（`plugins/stitch-build/skills/react-components/scripts/validate.js`）

```js
const ast = await swc.parse(code, { syntax: "typescript", tsx: true });
const walk = (node) => {
  if (node.type === 'TsInterfaceDeclaration' && node.id.value.endsWith('Props')) hasInterface = true;
  if (node.type === 'JSXAttribute' && (node.name?.value === 'className' || node.name?.name === 'className')) {
    if (node.value?.value && HEX_COLOR_REGEX.test(node.value.value)) tailwindIssues.push(node.value.value);
  }
  for (const key in node) { if (key === 'span') continue; if (node[key] && typeof node[key] === 'object') walk(node[key]); }
};
```
**设计解读**：用真正的 parser 而非正则，才能区分「注释里的 hex」和「className 里的 hex」，也才能确认 interface 声明而非字符串提及。`hasInterface && tailwindIssues.length === 0` 才 `exit(0)`——把风格规范变成二进制判定。这是全仓最值得抄的一段。

### 关键模块二：SKILL.md 的 GATE 结构（`plugins/stitch-build/skills/react-components/SKILL.md`）

```
> **CRITICAL: Every step in this skill is MANDATORY...**
> **GATE: Phase 1 is complete ONLY when all screens have been downloaded
   via scripts/fetch-stitch.sh AND visually audited.**
```
每阶段「完成条件 + 反模式清单」成对出现（Phase 1 下载、Phase 2 token 同步、Phase 3 架构规则共 3+ GATE）。这是把「agentskills.io 的 SKILL.md 格式」用到极致的结构化写法。

### 关键模块三：fetch-stitch.sh 的可靠性兜底

```bash
curl -L -f -sS --connect-timeout 10 --compressed "$URL" -o "$OUTPUT"
```
`-L` 跟重定向、`-f` HTTP 错误即失败、`--compressed` 处理编码、`--connect-timeout 10` 防挂死——针对 GCS 签名 URL 的标准硬化参数。截图 URL 还要手动追加 `=w{width}` 才能拿到高分辨率而非默认缩略图（这个坑写在 SKILL.md 里，README 不会告诉你）。

### 隐藏特性

- **DESIGN.md 多框架参考**：`extract-design-md/references/` 下有 angular / plain-css / react-tailwind / svelte / vue 五种框架的 DESIGN.md 抽取模板——说明该项目在有意做「框架无关的设计描述格式」。
- **Remotion 视频能力**：`stitch-build/skills/remotion` 能把设计屏幕转成产品演示视频（WalkthroughComposition），这是设计交付的延伸场景。

## 📐 架构决策与设计哲学

- **README 明确免责声明**："Not an officially supported Google product"——Google Labs 的实验性产出，非 GA 产品，依赖的 Stitch MCP 可能变动。
- **设计红线**：技能是「Stitch 操作的编排层」，不是独立 CLI/库；离开 Stitch MCP 无价值。这个边界在 README 和多方测评中被反复确认。
- **一个正在暴露的架构脆弱点**：Issue #94（open）报告「screen 的 downloadUrl 现在重定向到 Google 登录页，API-key MCP 客户端无法再下载屏幕」——即上游 MCP 的鉴权模型变更会让整个 skill 的 Phase 1 失效。这印证了「强耦合单一 MCP」的双刃剑本质。
- **版本节奏**：v0.1（2026-03）→ v1.0（2026-05），之后 8 月还在合入 site-md 功能（PR #91），最近一次提交 2026-08-17——**近 3 个月无提交**，需留意维护活跃度下滑。

## 🌐 全网口碑画像

### 好评共识

- ExplainX / hysenlabs / HotRepo 一致肯定「MCP + Skill 分层」的思路：MCP 只给工具，skills 补齐「调用顺序 + 校验」，把设计稿到 React 的机械翻译自动化（`explainx.ai` / `hysenlabs.com` 2026-10/11）。
- 开放标准带来的可移植性被反复提及：同一套 SKILL.md 能进 6 种 Agent，是「一次编写多宿主运行」的实际收益。
- 安全审查（aigrowthrank 2026-10-26）结论：16 个 SKILL.md / 86 文件 / 19 脚本，被动审查**未发现红旗（red flags: none found）**。

### 差评共识 & 踩坑高发区

- **OpenCode 支持是硬伤**：`stitch::` 前缀不符合 OpenCode 的 kebab-case 目录命名规则，需手动改名；MCP 也要在 `opencode.json` 里单独声明（多家测评一致指出）。
- **依赖地狱**：skill 间相互依赖，选择性安装容易断链（HotRepo / skillfoxx）。
- **上游不稳定**：Issue #94 的下载 URL 鉴权变更直接打断核心流程；#96 报 `manage-design-system` 上传路径只在仓库 checkout 下工作；#68 报 `generate-design` 编辑流程因上游 `edit_screens` 不持久化而成为 no-op。
- **供应链审查警告**：19 个脚本中有 2 个依赖未 pin 版本；测评方只审了 2026-08-17 的 commit，提醒「新版本可能改变一切」。

### 争议焦点 / 典型实战案例

- 最大争议是「**封闭生态绑定**」：不适用 Stitch 的场景（比如设计在 Figma）这整套技能价值归零。多家测评把它列为「poor fit」首要条件。
- 社区热度真实：约 9,188⭐，日榜曾单日 +250 星（explainx 数据），属于 Agent Skills 赛道的头部项目之一，但尚未被 Google 官方产品化。

### 维护者响应风格

- Issue #70/#66/#69 等安装与文档问题均被 closed，说明维护者在处理；但核心功能性问题（#94 下载失效、#68 编辑 no-op）仍 open，依赖上游 Stitch SDK 修复——**维护者能修的修，修不了的要等 Google 上游**。

## ⚔️ 竞品对比

| 维度 | stitch-skills | anthropics/skills（官方范例集） | Scenario skills（媒体生成） | Figma MCP / v0 |
|------|--------------|-------------------------------|---------------------------|----------------|
| 定位 | Stitch 设计↔代码工序层 | 通用 Agent Skills 官方示例/规范 | AI 媒体生成（图/视频/3D） | 设计工具直连代码 |
| 核心资产 | 3 插件 16 skill + AST 校验 + GATE | 规范与示例 skill | 一致性/质量门技能 | MCP 工具本身 |
| 强制流程 | **最强（GATE + 反模式 + 校验器）** | 弱（示例为主） | 中（dry_run 探价 + pass/warn/fail） | 弱 |
| 生态绑定 | 强绑 Stitch MCP | 无外部绑定 | 强绑 Scenario MCP | 绑 Figma/v0 |
| 跨 Agent | 6 种 | 广 | 依托 MCP | 视实现 |

**选择建议**：已经在用 Stitch 且要批量产出 React 工程 → stitch-skills；只想要 skill 规范范例 → anthropics/skills；做游戏美术/媒体资产 → Scenario；设计在 Figma → 走 Figma MCP 路线，别硬套本项目。

## 🎯 核心研判

### 项目优势（不可替代的价值点）

- **「可验收的 SOP」范式**：GATE + AST 校验 + 反模式，是当前 Agent Skills 里把「流程确定性」做得最系统的一套，工程价值远超「技能数量」。
- **设计 token 防漂移机制**：style-guide.json 的中间契约 + 「禁止硬编码 hex」的机器校验，直击设计到代码的最大痛点。
- **Google Labs 背书 + Apache-2.0**：可商用，社区信任度高。

### 项目风险（潜在隐患和局限性）

- **单一 MCP 强耦合**：#94/#68 已证明上游 Stitch MCP/SDK 一变，核心链路就断。这是架构级风险，不是 bug。
- **维护节奏放缓**：最近提交 2026-08-17，近 3 个月静默；非官方产品定位意味着随时可能被 Google 弃养。
- **供应链与安装体验**：未 pin 依赖 + 技能间依赖 + OpenCode 改名摩擦，抬高落地成本。

### 适用场景 & 不适用场景

- ✅ 适用：团队已用 Stitch 做设计、要稳定批量转 React、需要设计系统治理。
- ❌ 不适用：设计在 Figma、只想从截图生成组件、没有 Stitch MCP 环境、重度依赖 OpenCode。

### 趋势判断

**稳定期偏谨慎**：热度仍在（日榜常在），但从 v1.0 后无大版本、核心 issue 挂起、上游依赖不稳来看，处于「可用但未 GA」的平台期。**建议当作「Agent SOP 设计范本」学习其结构，是否生产采用则取决于团队是否已锁定 Stitch 生态。**

## 📂 关键文件路径速查

| 文件 | 作用 |
|------|------|
| `.agents/plugins/marketplace.json` | Codex marketplace 插件注册入口 |
| `plugins/stitch-build/skills/react-components/SKILL.md` | GATE 流程最完整的代表性技能 |
| `plugins/stitch-build/skills/react-components/scripts/validate.js` | AST 校验器（Props + hex 检测），最值得借鉴 |
| `plugins/stitch-build/skills/react-components/scripts/fetch-stitch.sh` | GCS 高可靠下载兜底脚本 |
| `plugins/stitch-build/skills/react-components/resources/style-guide.json` | 设计 token 中间契约 |
| `plugins/stitch-design/skills/extract-design-md/references/` | 5 种框架的 DESIGN.md 抽取模板 |
| `plugins/stitch-utilities/skills/stitch-loop/resources/baton-schema.md` | 多页站点上下文传递契约 |
